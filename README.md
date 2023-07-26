# AIMD_extractor
Tool for extracting MSD, calculating activation energy, conductivities and diffusivities from VASP AIMD runs.

Note: This code is not robust and is only intended for use within the author's directory architecture. An example of this is given below:

├── temperature_800/
│   ├── run_0/
│   │   └── XDATCAR  # Output trajectory file for run 0 at 800 K
│   ├── run_1/
│   │   └── XDATCAR  # Output trajectory file for run 1 at 800 K
│   ├── ...
│   └── run_10/
│       └── XDATCAR  # Output trajectory file for run 39 at 800 K
│
├── temperature_1000/
│   ├── run_0/
│   │   └── XDATCAR  # Output trajectory file for run 0 at 1000 K
│   ├── run_1/
│   │   └── XDATCAR  # Output trajectory file for run 1 at 1000 K
│   ├── ...
│   └── run_39/
│       └── XDATCAR  # Output trajectory file for run 39 at 1000 K
...

Variability in the number of runs per temperature is permitted.

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

To view functionality, view the help message:

```
AIMD_extractor --help
```

## Disclaimer

This code is not affiliated with VASP. This programme is made available under the MIT License; use and modify it at your own risk.


