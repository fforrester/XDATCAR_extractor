from setuptools import setup, find_packages

setup(
    name='conductivity-calculator',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pymatgen',
    ],
    entry_points={
        'console_scripts': [
            'conductivity_calculator = conductivity_calculator:main',
        ],
    },
)
