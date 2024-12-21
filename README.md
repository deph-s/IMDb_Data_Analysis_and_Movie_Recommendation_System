[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python for data science project : Some statistics on the IMDb database. 
This project was made as a class assignment at ENSAE by a group of 3 persons, myself, Guy and Sarakpy. It aims to provide some general statistics on movies, illustrate some trends relative to movie characteristics. We also built a movie recommendation algorithm that the user can interact with at the end. 

This project relies on several dependencies, including but not limited to Streamlit, all of those are listed in the requirements.txt file.

## Installation

To install and set up this project, follow these steps:

```bash
# Clone the repository
git clone https://github.com/deph-s/projet_python_ds2024

# Navigate into the directory
cd projet_python_ds2024/app/

# Install everything with the setup.py
python setup.py install

# Run the streamlit file
streamlit run Analysis_of_the_IMDb_dataset.py

# Check the data processing pipeline, make sure you have your own OMDB API key in your SSP Cloud vault. 
python data_gathering_and_processing.py
```

## Data processing pipeline 


Aside from the main streamlit script Analysis_of_the_IMDb_dataset.py python file, there is a second .py file in the app/ directory. This file is a standalone python file that contains all the functions that we wrote to gather and process the data that we used. **To run this script you need to inject your own OMDB API key under the name API_KEY in the environment variables when you start a new notebook, you can do this by clicking on Vault in the parameter menu that pops up when you start a new notebook and by adding 'api_key' in the 'Secret' section. Before that you need to create a new secret in the section "My secrets" on the datalab, name it 'api_key', then double click on that new secret and set its name to API_KEY and its value to your own key. The rest of the process is automated.** This script will run all the functions on a sample dataset made up of 50 popular entries of our dataset. Most of the functions in this file rely on previously written functions and worked well on our database. However they are not meant to be general database processing functions as a lot of the database parameters are hardcoded in the functions (for instance). 

Get you OMDB API key here : https://www.omdbapi.com/
