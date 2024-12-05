import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'dev__ds/app/src'))

from plot_functions import plot_bar_chart

import os
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'data', 'imdb_data.csv')
data_path = os.path.abspath(data_path)
imdb_data = pd.read_csv(data_path)

num_movies = len(imdb_data)
avg_runtime = imdb_data['Runtime'].mean()
max_runtime = imdb_data['Runtime'].max()
min_runtime = imdb_data['Runtime'].min()
nb_genres = 28  # Calculated in the data_cleaning notebook
imdb_data['Released'] = pd.to_numeric(imdb_data['Released'], errors='coerce')
imdb_data.loc[imdb_data['Released'] <= 1887, 'Released'] = 3000 # Aucun film jamais fait avant 1888 donc si entrée elle est fausse
oldest_film = imdb_data['Released'].min()

st.title("A first look at our dataset :")

# Top section

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Number of entries", f"{num_movies:,}")
    st.metric("Number of genres", f"{nb_genres:,}")

with col2:
    st.metric("Average entry length", f"{avg_runtime:.2f} minutes")
    st.metric("Longest entry : ", f"{max_runtime/60:.0f}" + "h")

with col3:
    st.metric("Oldest entry", f"{oldest_film:,}")
    st.metric("Shortest entry", value="≤ 1 min")

# PLOTLY SECTION BAR CHART : 

st.header("Number of movies per genre in full database (excluding Drama) : ")

glob_genre_list = imdb_data['Genres'].str.split(',').explode().str.strip() # Consider the whole database
glob_genre_list = glob_genre_list[~glob_genre_list.isin(['Drama', '\\N'])] # Remove drama and things with no genre indicated
genre_counts = glob_genre_list.value_counts()

labels = genre_counts.index.tolist()
values = genre_counts.values.tolist()

fig = plot_bar_chart(labels, values)

st.plotly_chart(fig)

# Describe de fin

st.header("Some general statistics : ")
summary_stats = imdb_data.describe()
summary_stats = summary_stats.rename(index={'count' : 'Nb Observ', 'mean' : 'Mean', 'std' : 'Std.', 'min' : 'Min', 'max' : 'Max'})
st.write(summary_stats.T)

st.header("First few rows of the dataset : ")
st.dataframe(imdb_data.head())