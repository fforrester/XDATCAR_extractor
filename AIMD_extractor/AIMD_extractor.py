import numpy as np
from pymatgen.analysis.diffusion.analyzer import DiffusionAnalyzer, fit_arrhenius, get_extrapolated_conductivity
from pymatgen.io.vasp.outputs import Xdatcar
import os
import re
import argparse
import json

class InvalidTemperatureFormatError(ValueError):
    pass

class TemperatureDirectoryNotFoundError(FileNotFoundError):
    pass

def write_to_output(outfile, string, print_to_console=True):
    with open(outfile, "a+") as f:
        f.write(string + "\n")

    if print_to_console:
        print(string)

def has_temperature(name):
    consecutive_digits = 0
    for char in name:
        if char.isdigit():
            consecutive_digits += 1
        else:
            consecutive_digits = 0

        if consecutive_digits >= 3 and consecutive_digits <= 4:
            return True

    return False

def find_directories_with_temperature(root_path):
    temperature_dict = {}

    subdirectories = [entry for entry in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, entry))]
    for dirname in subdirectories:
        if has_temperature(dirname):
            try:
                match = re.search(r"\d{3,4}", dirname)
                if match:
                    temperature = int(match.group())
                    temperature_dict[dirname] = temperature
            except ValueError:
                # If a ValueError occurs during int(match.group()), ignore this subdirectory
                pass

    # Sort the dictionary by temperature values in ascending order and return it
    return {k: v for k, v in sorted(temperature_dict.items(), key=lambda item: item[1])}

def get_run_range(temperature_directories):
    current_directory = os.getcwd()
    temperature_range_dict = {}
    for temperature_dir in temperature_directories:
        temperature_directory = os.path.join(current_directory, temperature_dir)

        numeric_directories = []

        for dir_name in os.listdir(temperature_directory):
            # Use regular expression to find numeric run number from the directory name
            match = re.search(r'\d+', dir_name)
            if match:
                run_number = int(match.group())
                numeric_directories.append(run_number)

        if not numeric_directories:
            write_to_output(outfile, f"No run directories found inside '{temperature_directory}'.")
            continue
        temperature_range_dict[temperature_dir] = (min(numeric_directories), max(numeric_directories))

    return temperature_range_dict
    
def calculate_conductivity(species, temperature_range_dict, outfile, time_step=2, ballistic_skip=50, step_skip=1, smoothed="max"):
    all_trajectories = []
    diffusivities = []

    write_to_output(outfile, "-----------------------------")
    write_to_output(outfile, f"Species: {species}")
    write_to_output(outfile, "-----------------------------")

    for temperature_dir, run_range in temperature_range_dict.items():
        temperature_val = run_range[0]
        run_start, run_end = get_run_range(temperature_dir)

        structures = []
        for run in range(run_range[0], run_range[1] + 1):
            filepath = f"{temperature_dir}/run_{run}/XDATCAR"
            write_to_output(outfile, f"Reading from {filepath}...")
            structures += Xdatcar(filepath).structures

        structures = structures[ballistic_skip:]

        da = DiffusionAnalyzer.from_structures(structures, species, temperature_val, time_step, step_skip=step_skip, smoothed=smoothed)

        write_to_output(outfile, f"Printing msd.{temperature_val}.dat...")
        da.export_msdt(f"msd.{temperature_val}.dat")

        diffusivities.append(da.diffusivity)
        all_trajectories.append(structures)

    Ea, c, sEa = fit_arrhenius([run_range[0] for _, run_range in temperature_range_dict.items()], diffusivities)

    write_to_output(outfile, f"Ea = {Ea:.3f} +/- {sEa:.3f}")
    conductivity = get_extrapolated_conductivity([run_range[0] for _, run_range in temperature_range_dict.items()], diffusivities, 300, structures[0], species)

    IT = np.divide(1, [run_range[0] for _, run_range in temperature_range_dict.items()])
    lnD = np.log(diffusivities)

    zipped = np.column_stack((IT, lnD))
    np.savetxt("arrhenius.txt", zipped)

    write_to_output(outfile, f"conductivity = {conductivity}")

    write_to_output(outfile, "-----------------------------")



def main():
    parser = argparse.ArgumentParser(description="Calculate conductivity from DiffusionAnalyzer.")
    parser.add_argument("species", type=str, help="The chemical species to analyze.")
    parser.add_argument("--outfile", type=str, default="conductivity.txt", help="Output file name.")
    parser.add_argument("--time_step", type=float, default=2, help="Time step in femtoseconds (fs).")
    parser.add_argument("--ballistic_skip", type=int, default=50, help="Number of steps to skip to avoid ballistic region.")
    parser.add_argument("--step_skip", type=int, default=1, help="Number of steps to skip for efficiency.")
    parser.add_argument("--smoothed", type=str, default="max", help="Type of smoothing for MSD.")
    parser.add_argument("--temperatures", nargs="+", type=int, help="List of temperatures in Kelvin.")
    args = parser.parse_args()

    if not args.temperatures:
        temperature_range_dict = find_directories_with_temperature(os.getcwd())
        if not temperature_range_dict:
            print("No temperature directories found.")
            return
    else:
        temperatures = sorted(args.temperatures)

    # Print the temperatures to the outfile and suppress printing to console
    write_to_output(args.outfile, "Temperatures: " + ", ".join(map(str, temperature_range_dict.values())), print_to_console=False)

    calculate_conductivity(args.species, temperature_range_dict, args.outfile,
                           time_step=args.time_step, ballistic_skip=args.ballistic_skip,
                           step_skip=args.step_skip, smoothed=args.smoothed)

if __name__ == "__main__":
    main()
