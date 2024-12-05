import streamlit as st

# Streamlit automatically recognizes all files in the 'pages/' folder as pages
st.set_page_config(page_title="Movies Dashboard", layout="wide")

st.title("Welcome to the Movies Dashboard")

st.write("""
    This app shows descriptive statistics and visualizations about movies and their characteristics.
    
    - Navigate to the other pages in the sidebar to see more details.
""")