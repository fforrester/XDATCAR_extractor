"""
Utilities for VASP AIMD analysis.
"""

from setuptools import setup, find_packages
from AIMD_extractor.version import __version__ as VERSION

readme = "README.md"
long_description = open(readme).read()

setup(
    name="figure-formatting",
    version=VERSION,
    description="Python utilities for VASP AIMD analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Benjamin J. Morgan",
    author_email="f.forrester2@ncl.ac.uk",
    url="https://github.com/fforrester/AIMD-extractor",
    download_url="https://github.com/fforrester/AIMD-extractor/archive/{}.tar.gz".format(
        VERSION
    ),
    license="MIT",
    install_requires=["pymatgen","numpy"],
    python_requires=">=3.7",
)
