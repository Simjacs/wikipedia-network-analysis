# Data location
Data can be found at https://dumps.wikimedia.org/other/clickstream/2023-06/

Documentation for it is at https://meta.wikimedia.org/wiki/Research:Wikipedia_clickstream

# Setup
This project was built in a virtual environment, the package management was done with poetry. 

Poetry installation guide: https://python-poetry.org/docs/#installation

If you are familiar with it, please use the `poetry.lock` and `pyproject.toml` files to install the necessary packages
However, the packages are all listed in `requirements.txt` 

# Structure
The code expects a directory called `data/` which contains all of the input and output data
- The code, except for the exploration notebook is all in `src/`
