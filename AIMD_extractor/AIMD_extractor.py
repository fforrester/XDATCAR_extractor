import numpy as np
from pymatgen.analysis.diffusion.analyzer import DiffusionAnalyzer, fit_arrhenius, get_extrapolated_conductivity
from pymatgen.io.vasp.outputs import Xdatcar
import os
import argparse
import re
import json

class InvalidTemperatureFormatError(ValueError):
    pass

class TemperatureDirectoryNotFoundError(FileNotFoundError):
    pass

def write_to_output(outfile, string):
    with open(outfile, "a+") as f:
        f.write(string + "\n")

def read_temperature_variations():
    with open("temperature_variations.json", "r") as f:
        data = json.load(f)
    return data["variations"]

def read_run_variations():
    with open("run_variations.json", "r") as f:
        data = json.load(f)
    return data["variations"]

def get_temperature_directories():
    current_directory = os.getcwd()
    subdirectories = next(os.walk(current_directory))[1]

    temperatures = []
    for subdir in subdirectories:
        try:
            # Use regular expression to find three or four consecutive digits in the subdirectory names
            match = re.search(r'\b\d{3,4}\b', subdir)
            if match:
                temperature = int(match.group())
                temperatures.append(temperature)
        except ValueError:
            # If a ValueError occurs during int(match.group()), ignore this subdirectory
            pass

    return sorted(temperatures)  # Sort temperatures in ascending order

def get_run_range(temperature):
    run_variations = read_run_variations()
    current_directory = os.getcwd()

    # Use regular expression to find three or four consecutive digits in the temperature value
    match = re.search(r'\b\d{3,4}\b', str(temperature))
    if match:
        temperature = int(match.group())
    else:
        # If numeric temperature is not found, try variations from the configuration file
        for variation, format_string in run_variations.items():
            if variation in str(temperature):
                match = re.search(r'\b\d{3,4}\b', str(temperature).replace(variation, ""))
                if match:
                    temperature = int(match.group())
                    break
        else:
            raise InvalidTemperatureFormatError(f"Invalid temperature format for '{temperature}'.")

    temperature_directory = os.path.join(current_directory, str(temperature))

    if not os.path.exists(temperature_directory):
        # If the directory with the numeric temperature is not found, try variations from the configuration file
        for variation, format_string in run_variations.items():
            run_directory_variation = os.path.join(current_directory, format_string.format(run=temperature))
            if os.path.exists(run_directory_variation):
                temperature_directory = run_directory_variation
                break
        else:
            raise TemperatureDirectoryNotFoundError(f"Temperature directory '{temperature_directory}' does not exist.")

    run_directories = [dir_name for dir_name in os.listdir(temperature_directory) if os.path.isdir(os.path.join(temperature_directory, dir_name))]
    numeric_directories = []

    for dir_name in run_directories:
        # Use regular expression to find numeric run number from the directory name
        match = re.search(r'\d+', dir_name)
        if match:
            run_number = int(match.group())
            numeric_directories.append(run_number)

    if not numeric_directories:
        raise RuntimeError(f"No run directories found inside '{temperature_directory}'.")

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

        da = DiffusionAnalyzer.from_structures(structures, species, temperature, time_step, step_skip=step_skip, smoothed=smoothed
