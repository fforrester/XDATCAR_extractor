import numpy as np
from pymatgen.analysis.diffusion.analyzer import DiffusionAnalyzer, fit_arrhenius, get_extrapolated_conductivity
from pymatgen.io.vasp.outputs import Xdatcar
import os
import argparse
import re

def write_to_output(outfile, string):
    with open(outfile, "a+") as f:
        f.write(string + "\n")

def get_temperature_directories():
    current_directory = os.getcwd()
    subdirectories = next(os.walk(current_directory))[1]

    temperatures = []
    for subdir in subdirectories:
        try:
            # Use regular expression to find three or four consecutive digits in the subdirectory names
            match = re.search(r'\b\d{3,4}\b',subdir)
            if match:
                temperature = int(match.group())
                temperatures.append(temperature)
        except ValueError:
            # If a ValueError occurs during int(match.group()), ignore this subdirectory
            pass

    return sorted(temperatures)  # Sort temperatures in ascending order

def get_run_range(temperature):
    # Use regular expression to find three or four consecutive digits in the temperature value
    match = re.search(r'\b\d{3,4}\b', str(temperature))
    if match:
        temperature = int(match.group())
    else:
        print(f"Invalid temperature format for '{temperature}'.")
        return None, None

    current_directory = os.getcwd()
    temperature_directory = os.path.join(current_directory, str(temperature))

    if not os.path.exists(temperature_directory):
        print(f"Temperature directory '{temperature_directory}' does not exist.")
        return None, None

    run_directories = [dir_name for dir_name in os.listdir(temperature_directory) if os.path.isdir(os.path.join(temperature_directory, dir_name))]
    numeric_directories = []

    for dir_name in run_directories:
        # Use regular expression to find numeric run number from the directory name
        match = re.search(r'\d+', dir_name)
        if match:
            run_number = int(match.group())
            numeric_directories.append(run_number)

    if not numeric_directories:
        print(f"No run directories found inside '{temperature_directory}'.")
        return None, None

    return min(numeric_directories), max(numeric_directories)

def calculate_conductivity(species, temperatures, outfile, time_step=2, ballistic_skip=50, step_skip=1, smoothed="max"):
    all_trajectories = []
    diffusivities = []

    write_to_output(outfile, "-----------------------------")
    write_to_output(outfile, f"Species: {species}")
    write_to_output(outfile, f"Temperatures: {temperatures}")
    write_to_output(outfile, "-----------------------------")

    for temperature in temperatures:
        run_start, run_end = get_run_range(temperature)
        if run_start is None or run_end is None:
            write_to_output(outfile, f"No run directories found for {temperature} K. Skipping...")
            continue

        structures = []
        for run in range(run_start, run_end + 1):
            filepath = f"{temperature}/run_{run}/XDATCAR"
            write_to_output(outfile, f"Reading from {filepath}...")
            structures += Xdatcar(filepath).structures

        structures = structures[ballistic_skip:]

        da = DiffusionAnalyzer.from_structures(structures, species, temperature, time_step, step_skip=step_skip, smoothed=smoothed)

        write_to_output(outfile, f"Printing msd.{temperature}.dat...")
        da.export_msdt(f"msd.{temperature}.dat")

        diffusivities.append(da.diffusivity)
        all_trajectories.append(structures)

    Ea, c, sEa = fit_arrhenius(temperatures, diffusivities)
    write_to_output(outfile, f"Ea = {Ea:.3f} +/- {sEa:.3f}")
    conductivity = get_extrapolated_conductivity(temperatures, diffusivities, 300, structures[0], species)

    IT = np.divide(1, temperatures)
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
        temperatures = get_temperature_directories()
        if not temperatures:
            print("No temperature directories found.")
            return
    else:
        temperatures = sorted(args.temperatures)

    calculate_conductivity(args.species, temperatures, args.outfile,
                           time_step=args.time_step, ballistic_skip=args.ballistic_skip,
                           step_skip=args.step_skip, smoothed=args.smoothed)

if __name__ == "__main__":
    main()
