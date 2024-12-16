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
```

## Data processing pipeline 

Aside from the main streamlit script Analysis_of_the_IMDb_dataset.py python file, there is a second .py file in the app/ directory. This file is a standalone python file that contains all the functions that we wrote to gather and process the data that we used. It can be executed immediately after you run setup.py and it will run all the functions on a sample_dataset made up of 50 popular entries of our dataset. Most of the functions in this file rely on previously written functions and worked well on our database. However they are not meant to be general database processing functions as a lot of the database parameters are hardcoded in the functions (for instance). 
