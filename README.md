# XDATCAR_extractor

The XDATCAR Extractor is a Python module that analyses XDATCAR files to calculate the Mean Squared Displacement (MSD), diffusivity, and conductivity for a given chemical species. It makes use of the pymatgen library to handle the necessary computations.

Note: This code is not robust and is only intended for use within the author's directory architecture. A couple of examples of situations where this will work are given below:

temperature_1000 / run_{i} / XDATCAR  
800K / run_{j} / XDATCAR   

Variability in the number of runs per temperature is permitted, i.e. where i ≠ j. It should also be noted where i or j = 0 the directory will be ignored. 

Currently all runs must have the following form run_{i} --> This will likely be changed when I get chance. 

## Installation

Clone the repo and install:
```
git clone https://github.com/fforrester/XDATCAR_extractor.git
cd XDATCAR_extractor
pip install .
```
### Alternatively
```
pip install git+https://github.com/fforrester/XDATCAR_extractor.git
```

## Implementation 

Ensure that your runs have the required directory structure, including directories with numeric temperatures as a part of their names, e.g., 300K, 600, T900, 1000_K, Li3PS4_1200K, etc.

Run the XDATCAR_extractor with the following command:
```
XDATCAR_extractor <species> [--outfile <output_filename>] [--time_step <time_step>] [--ballistic_skip <ballistic_skip>] [--step_skip <step_skip>] [--smoothed <smoothing_type>] [--temperatures <temperature_list>]
```

* species : The chemical species you want to analyse, e.g., "Li", "Na", "O", etc.
* --outfile <output_filename>: (Optional) Specify the output filename. Default is "AIMD_extractor.log".
* --time_step <time_step>: (Optional) Time step in femtoseconds (fs). Default is 2 fs.
* --ballistic_skip <ballistic_skip>: (Optional) Number of steps to skip to avoid the ballistic region. Default is 50.
* --step_skip <step_skip>: (Optional) Number of steps to skip for efficiency. Default is 1.
* --smoothed <smoothing_type>: (Optional) Turning smoothing on or off with True opr False, respectively. Default True
* --temperatures <temperature_list>: (Optional) Specify a list of temperatures in Kelvin. If not provided, the script will attempt to locate temperature directories based on the regular expression in the directory names.

To view functionality, view the help message:
```
XDATCAR_extractor --help
```
## Example Usage

* Analysing AIMD runs for species "Li" at temperatures 300K and 600K:
```XDATCAR_extractor Li --temperatures 300 600```
* Analysing AIMD runs for species "Na" with a custom output filename:
```XDATCAR_extractor Na --outfile analysis_results.log```
* Analyzing XDATACR for species "O" with a 1 fs time step:
```XDATCAR_extractor O --time_step 1```

## Disclaimer

This code is not affiliated with VASP. This programme is made available under the MIT License; use and modify it at your own risk.

## Acknowledgements
The AIMD_extractor uses the pymatgen library for diffusivity and conductivity calculations. For more information about pymatgen, visit [https://pymatgen.org/].
