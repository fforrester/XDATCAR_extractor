from setuptools import setup, find_packages
from XDATCAR_extractor.version import __version__ as VERSION

with open("README.md","r") as f:
    long_description = f.read()

setup(
    name="XDATCAR_extractor",
    version=VERSION,
    description="Python utilities for XDATCAR analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Frazer N. Forrester",
    author_email="frazer.forrester@ncl.ac.uk",
    url="https://github.com/fforrester/XDATCAR_extractor",
    download_url="https://github.com/fforrester/XDATCAR_extractor/archive/{}.tar.gz".format(VERSION),
    license="MIT",
    packages=find_packages(),
    package_data={
        'XDATCAR_extractor': ['temperature_variations.json', 'run_variations.json']
    },
    install_requires=["pymatgen", "pymatgen-analysis-diffusion", "numpy"],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'XDATCAR_extractor = XDATCAR_extractor.XDATCAR_extractor:main',
        ],
    },
)

