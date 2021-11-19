# Always prefer setuptools over distutils
from setuptools import setup

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="aprofiles",
    version="0.1.1",
    description="aerosol profiles processing and visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://aprofiles.readthedocs.io/",
    author="Augustin Mortier",
    author_email="augustinm@met.no",
    license="GPL-3.0",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    packages=["aprofiles"],
    python_requires=">=3.8,<4",
    include_package_data=True,
    install_requires=[
        "matplotlib",
        "miepython",
        "netcdf4",
        "numpy",
        "seaborn",
        "scipy",
        "tqdm",
        "xarray",
    ],
)
