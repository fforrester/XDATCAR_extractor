"""
Utilities for VASP AIMD analysis.
"""

from setuptools import setup, find_packages
from AIMD_extractor.version import __version__ as VERSION

readme = "README.md"
long_description = open(readme).read()

setup(
    name="AIMD_extractor",
    version=VERSION,
    description="Python utilities for VASP AIMD analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Frazer N. Forrester",
    author_email="f.forrester2@ncl.ac.uk",
    url="https://github.com/fforrester/AIMD_extractor",
    download_url="https://github.com/fforrester/AIMD_extractor/archive/{}.tar.gz".format(
        VERSION
    ),
    license="MIT",
    install_requires=["pymatgen","numpy"],
    python_requires=">=3.7",
)
