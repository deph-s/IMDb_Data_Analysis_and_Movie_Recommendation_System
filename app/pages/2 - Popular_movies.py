import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'dev__ds/app/src'))

from plot_functions import plot_bar_chart

# Load the popular movies data : 

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path1 = os.path.join(script_dir, '..', 'data', 'imdb_data.csv')
data_path1 = os.path.abspath(data_path1)
film_data = pd.read_csv(data_path1)

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path2 = os.path.join(script_dir, '..', 'data', 'pop_entries.csv')
data_path2 = os.path.abspath(data_path2) 
pop_entries = pd.read_csv(data_path2)

num_movies = len(pop_entries)
avg_runtime = pop_entries['Runtime'].mean()
max_runtime = pop_entries['Runtime'].max()
min_runtime = pop_entries['Runtime'].min()
nb_genres = 27 # computed in plots notebook
pop_entries['Released'] = pd.to_numeric(pop_entries['Released'], errors='coerce')
pop_entries.loc[pop_entries['Released'] <= 1887, 'Released'] = 3000 # Aucun film jamais fait avant 1888 donc si entrée elle est fausse
oldest_film = pop_entries['Released'].min()
shortest = pop_entries['Runtime'].min()

# This allow HTML at the end allows us to use HTML commands in Markdown so that we can underline, bold etc... the text.

st.header("The top 250 IMDb :")
st.markdown("""The IMDb top 250 Movies is the list of the **250 highest rated films of all time**. To appear on the list, the movie 
                must be a **feature film** (long enough) and at least <u>**25,000**</u> 
                users must have rated it.""", unsafe_allow_html=True)
            
st.markdown("""⤷ In consequence we decided to restrict our dataset to the \"popular\" movies, i.e, movies that have more
                than <u>**25,000**</u> reviews on IMDb so that they are susceptible to appear on the top 250""", unsafe_allow_html=True)

st.header("Some statistics on the popular movies :")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Number of entries", f"{num_movies:,}", delta=' 1,491,359')
    st.metric("Number of genres", f"{nb_genres:,}", delta='28')

with col2:
    st.metric("Average entry length", f"{avg_runtime:.2f}" +"m", delta='55.47m')
    st.metric("Longest entry : ", f"{max_runtime/60:.0f}" + "h", delta="991h")

with col3:
    st.metric("Oldest entry", f"{oldest_film:,}", delta="1888")
    st.metric("Shortest entry", f"{shortest:,}" + "m", delta="≤ 1 min")


# PLOTLY SECTION ##########################################################################################

# We have to create a function to create the bar chart depending on the input of the button : 

st.header("Genre representation in the popular movies dataset (No drama) : ")

if 'show_old_version' not in st.session_state:
    st.session_state.show_old_version = False  

if st.session_state.show_old_version:
    glob_genre_list = film_data['Genres'].str.split(',').explode().str.strip() # Consider the whole database
    glob_genre_list = glob_genre_list[~glob_genre_list.isin(['Drama', '\\N'])] # Remove drama and things with no genre indicated
    genre_counts = glob_genre_list.value_counts()

    labels = genre_counts.index.tolist()
    values = genre_counts.values.tolist()

    fig = plot_bar_chart(labels, values)
else:
    glob_genre_list = pop_entries['Genres'].str.split(',').explode().str.strip() # Consider the whole database
    glob_genre_list = glob_genre_list[~glob_genre_list.isin(['Drama', '\\N'])] # Remove drama and things with no genre indicated
    genre_counts = glob_genre_list.value_counts()

    labels = genre_counts.index.tolist()
    values = genre_counts.values.tolist()

    fig = plot_bar_chart(labels, values)

# Display the selected bar chart
st.plotly_chart(fig)

if st.button("Compare with old chart" if not st.session_state.show_old_version else "Compare with new chart"):
    st.session_state.show_old_version = not st.session_state.show_old_version