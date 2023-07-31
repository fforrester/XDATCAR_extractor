# AIMD_extractor

The AIMD Extractor is a Python module that analyses VASP (Vienna Ab initio Simulation Package) AIMD (Ab initio Molecular Dynamics) runs to calculate the Mean Squared Displacement (MSD), diffusivity, and conductivity for a given chemical species. It makes use of the pymatgen library to handle the necessary computations.

Note: This code is not robust and is only intended for use within the author's directory architecture. A couple of examples of situations where this will work are given below:

temperature_1000 / run_{i} / XDATCAR  
800K / run{j} / XDATCAR   

Variability in the number of runs per temperature is permitted, i.e. where i ≠ j

However, currently all runs must have the following form run_{i} --> This will likely be changed in due course. 

## Installation

Clone the repo and install:
```
git clone https://github.com/fforrester/AIMD_extractor
cd AIMD_extractor
pip install .
```
### Alternatively
```
pip install git+https://github.com/fforrester/AIMD_extractor.git
```

## Implementation 

Ensure that your VASP AIMD runs have the required directory structure, including directories with numeric temperatures as a part of their names, e.g., 300K, 600, T900,1000_K etc.

Run the AIMD_Extractor with the following command:
```
python aimd_extractor.py <species> [--outfile <output_filename>] [--time_step <time_step>] [--ballistic_skip <ballistic_skip>] [--step_skip <step_skip>] [--smoothed <smoothing_type>] [--temperatures <temperature_list>]
```

* species : The chemical species you want to analyze, e.g., "Li", "Na", "O", etc.
* --outfile <output_filename>: (Optional) Specify the output filename. Default is "AIMD_extractor.log".
* --time_step <time_step>: (Optional) Time step in femtoseconds (fs). Default is 2 fs.
* --ballistic_skip <ballistic_skip>: (Optional) Number of steps to skip to avoid the ballistic region. Default is 50.
* --step_skip <step_skip>: (Optional) Number of steps to skip for efficiency. Default is 1.
* --smoothed <smoothing_type>: (Optional) Type of smoothing for MSD. Choose from "max", "constant", or "none". Default is "max".
* --temperatures <temperature_list>: (Optional) Specify a list of temperatures in Kelvin. If not provided, the script will attempt to locate temperature directories based on the regular expression in the directory names.

To view functionality, view the help message:
```
AIMD_extractor --help
```
## Example Usage

Analysing AIMD runs for species "Li" at temperatures 300K and 600K:
```AIMD_extractor Li --temperatures 300 600```
Analysing AIMD runs for species "Na" with a custom output filename:
```AIMD_extractor Na --outfile analysis_results.log```
Analyzing AIMD runs for species "O" with a 1 fs time step:
```AIMD_extractor O --time_step 1```

## Disclaimer

This code is not affiliated with VASP. This programme is made available under the MIT License; use and modify it at your own risk.

## Acknowledgements
The AIMD_extractor uses the pymatgen library for diffusivity and conductivity calculations. For more information about pymatgen, visit [https://pymatgen.org/].
