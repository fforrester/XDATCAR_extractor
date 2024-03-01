import numpy as np
from pymatgen.analysis.diffusion.analyzer import DiffusionAnalyzer, fit_arrhenius, get_extrapolated_conductivity
from pymatgen.io.vasp.outputs import Xdatcar
import os
import re
import argparse


class InvalidTemperatureFormatError(ValueError):
    pass

class DirectoryNotFoundError(FileNotFoundError):
    pass

def write_to_output(outfile, string):
    with open(outfile, "a") as f:  # Changed mode to "a" for writing
        f.write(string + "\n")
        
def find_numbers_in_directory_names(directory):
    # Regular expression to find 3 or 4-digit numbers without preceding 0 in the directory names
    regex = r"(?<!\d)([1-9]\d{2,3})(?!\d)"

    temperature_dict = {}  # Create an empty dictionary to store the results

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            matches = re.findall(regex, item)
            if len(matches) == 1:
                number = int(matches[0])
                if 99 < number < 2000:
                    print(f"Found temperature '{matches[0]}' in directory: {item}")
                    temperature_dict[item] = number  # Add the valid number to the dictionary
                else:
                    print(f"Found a number '{matches[0]}' but it does not meet the criteria in the directory: {item}")
            elif len(matches) > 1:
                print(f"Ignoring directory: {item} - can't confirm temperature.")
    
    # Sort the dictionary based on the number found in directory names
    sorted_temperature_dict = {k: v for k, v in sorted(temperature_dict.items(), key=lambda item: item[1])}
    return sorted_temperature_dict

def find_directory_for_temperature(directory, userinputted_temps):
    # Regular expression to find 3 or 4-digit numbers without preceding or succeeding digits in the directory names
    regex = r"(?<!\d)([1-9]\d{2,3})(?!\d)"
    
    matching_directory = None

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            matches = re.findall(regex, item)
            if len(matches) == 1:
                number = int(matches[0])
                if 99 < number < 2000 and number == userinputted_temps:
                    matching_directory = item_path
                    break
    return matching_directory

def get_run_range(temperature_directory):
    # Use regular expression to find numeric run numbers from the directory names (e.g., run_1, run_2, etc.) ignoring run_0.
    numeric_directories = [int(re.search(r'run_(\d+)', dir_name).group(1)) for dir_name in os.listdir(temperature_directory) if re.search(r'run_(\d+)', dir_name) and re.search(r'run_(\d+)', dir_name).group(1) != '0']

    if not numeric_directories:
        raise DirectoryNotFoundError(f"No run directories found inside '{temperature_directory}'.")

    return min(numeric_directories), max(numeric_directories)
    

def calculate_conductivity(species, temperature_range_dict, outfile, time_step=2, ballistic_skip=50, step_skip=1, smoothed="max"):
    write_to_output(outfile, "-----------------------------")
    write_to_output(outfile, f"Species: {species}")
    write_to_output(outfile, f"Temperatures: {list(temperature_range_dict.values())}")
    write_to_output(outfile, "-----------------------------")
    diffusivities = []
    diffusivities_x = []
    diffusivities_y = []
    diffusivities_z = []
    
    temperatures = list(temperature_range_dict.values())
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
        diffusivities_x.append(da.diffusivity_components[0])
        diffusivities_y.append(da.diffusivity_components[1])
        diffusivities_z.append(da.diffusivity_components[2])
        
    Ea, c, sEa = fit_arrhenius(temperatures, diffusivities)
    Ea_x, c_x, sEa_x = fit_arrhenius(temperatures, diffusivities_x)
    Ea_y, c_y, sEa_y = fit_arrhenius(temperatures, diffusivities_y)
    Ea_z, c_z, sEa_z = fit_arrhenius(temperatures, diffusivities_z)

    diff_p = [np.sqrt(diff_x**2 +diff_y**2) for diff_x, diff_y in zip(diffusivities_x, diffusivities_y)]
    Ea_p , c_p, sEa_p = fit_arrhenius(temperatures, diff_p)

    write_to_output(outfile, f"Ea = {Ea:.3f} +/- {sEa:.3f}")
    write_to_output(outfile, f"Ea_x = {Ea_x:.3f} +/- {sEa_x:.3f}")
    write_to_output(outfile, f"Ea_y = {Ea_y:.3f} +/- {sEa_y:.3f}")
    write_to_output(outfile, f"Ea_z = {Ea_z:.3f} +/- {sEa_z:.3f}")
    write_to_output(outfile, f"Ea_xy = {Ea_p:.3f} +/- {sEa_p:.3f}")

    
    conductivity = get_extrapolated_conductivity(temperatures, diffusivities, 300, structures[0], species)

    IT = np.divide(1, temperatures)
    lnD = np.log(diffusivities)

    zipped = np.column_stack((IT, lnD))
    np.savetxt("arrhenius.txt", zipped)

    write_to_output(outfile, f"conductivity = {conductivity}")
    write_to_output(outfile, "-----------------------------")

def main():
    parser = argparse.ArgumentParser(description="Tool for calculating MSD, diffusivity and conductivity from VASP AIMD runs.")
    parser.add_argument("species", type=str, help="The chemical species to analyze.")
    parser.add_argument("--outfile", type=str, default="XDATCAR_extractor.log", help="Output file name.")
    parser.add_argument("--time_step", type=float, default=2, help="Time step in femtoseconds (fs).")
    parser.add_argument("--ballistic_skip", type=int, default=50, help="Number of steps to skip to avoid ballistic region.")
    parser.add_argument("--step_skip", type=int, default=1, help="Number of steps to skip for efficiency.")
    parser.add_argument("--smoothed", type=str, default="max", help="Type of smoothing for MSD (max, constant or none).")
    parser.add_argument("--temperatures", nargs="+", type=int, help="List of temperatures in Kelvin.")
    args = parser.parse_args()
    
    # If args.temperatures ARE NOT provided, use the find_numbers_in_directory names to locate possible temperatures.
    if not args.temperatures:
        temperature_range_dict =  find_numbers_in_directory_names(os.getcwd())
        if not temperature_range_dict:
            print("No temperature directories found.")
            return
    else:
        # If args.temperatures ARE provided, use the specified temperatures to find corresponding directories
        temperature_range_dict = {}
        for temp in args.temperatures:
            directory = find_directory_for_temperature(os.getcwd(), temp)
            if directory:
                temperature_range_dict[directory] = temp
            else:
                print(f"Temperature directory for {temp}K not found.")
        if not temperature_range_dict:
            print("No valid temperature directories found for the provided temperatures.")
            return


    calculate_conductivity(args.species, temperature_range_dict, args.outfile,
                           time_step=args.time_step, ballistic_skip=args.ballistic_skip,
                           step_skip=args.step_skip, smoothed=args.smoothed)

if __name__ == "__main__":
    main()
