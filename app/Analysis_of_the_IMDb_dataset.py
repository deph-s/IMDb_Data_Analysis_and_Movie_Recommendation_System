import streamlit as st

# Streamlit automatically recognizes all files in the 'pages/' folder as pages
st.set_page_config(page_title="Movies Dashboard", layout="wide")

st.title("Python for data science - IMDb database exploration")

st.write(
    """
    This app shows descriptive statistics and visualizations about movies and their characteristics extracted from the IMDb 
    dataset. The fourth page presents our movie recommendation algorithm. 
"""
)
