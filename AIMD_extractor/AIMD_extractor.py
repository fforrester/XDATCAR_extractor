import numpy as np
from pymatgen.analysis.diffusion.analyzer import DiffusionAnalyzer, fit_arrhenius, get_extrapolated_conductivity
from pymatgen.io.vasp.outputs import Xdatcar
import os
import re
import argparse


class InvalidTemperatureFormatError(ValueError):
    pass

class TemperatureDirectoryNotFoundError(FileNotFoundError):
    pass

def write_to_output(outfile, string):
    with open(outfile, "a") as f:  # Changed mode to "a" for writing
        f.write(string + "\n")

#funtion to determine whether or not the directory name has a temperature in it
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

def find_directories_with_temperature(path):
    temperature_dict = {}

    subdirectories = [entry for entry in os.listdir(path) if os.path.isdir(os.path.join(path, entry))]
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


def get_run_range(temperature_directory):
    # Use regular expression to find numeric run numbers from the directory names (e.g., run_1, run_2, etc.)
    numeric_directories = [int(re.search(r'run_(\d+)', dir_name).group(1)) for dir_name in os.listdir(temperature_directory) if re.search(r'run_(\d+)', dir_name)]

    if not numeric_directories:
        raise TemperatureDirectoryNotFoundError(f"No run directories found inside '{temperature_directory}'.")

    return min(numeric_directories), max(numeric_directories)
    

def calculate_conductivity(species, temperature_range_dict, outfile, time_step=2, ballistic_skip=50, step_skip=1, smoothed="max"):
    write_to_output(outfile, "-----------------------------")
    write_to_output(outfile, f"Species: {species}")
    write_to_output(outfile, f"Temperatures: {list(temperature_range_dict.values())}")
    write_to_output(outfile, "-----------------------------")
    diffusivities = []

    for temperature_dir, temperature in temperature_range_dict.items():
        run_start, run_end = get_run_range(temperature_dir)

        structures = []
        for run in range(run_start, run_end):
            filepath = os.path.join(temperature_dir, f"run_{run}", "XDATCAR")
            write_to_output(outfile, f"Reading from {filepath}...")
            structures += Xdatcar(filepath).structures

        structures = structures[ballistic_skip:]

        da = DiffusionAnalyzer.from_structures(structures, species, temperature, time_step, step_skip=step_skip, smoothed=smoothed)

        write_to_output(outfile, f"Printing msd.{temperature}.dat...")
        da.export_msdt(f"msd.{temperature}.dat")

        diffusivities.append(da.diffusivity)
    Ea, c, sEa = fit_arrhenius(list(temperature_range_dict.values()), diffusivities)

    write_to_output(outfile, f"Ea = {Ea:.3f} +/- {sEa:.3f}")
    conductivity = get_extrapolated_conductivity(list(temperature_range_dict), diffusivities, 300, structures[0], species)

    IT = np.divide(1, list(temperature_range_dict.values()))
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
        temperature_range_dict = {f"temp_{temp}": temp for temp in temperatures}


    calculate_conductivity(args.species, temperature_range_dict, args.outfile,
                           time_step=args.time_step, ballistic_skip=args.ballistic_skip,
                           step_skip=args.step_skip, smoothed=args.smoothed)

if __name__ == "__main__":
    main()
