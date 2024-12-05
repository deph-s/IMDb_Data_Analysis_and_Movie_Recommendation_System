import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'dev__ds/app/src'))   # To use the src files here.

from stat_functions import avg_runtime_genre
from plot_functions import plot_radial_chart

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'data', 'imdb_data.csv')
data_path = os.path.abspath(data_path)
imdb_data = pd.read_csv(data_path)
st.header("Do genre impact film length ? Average film length depending on the genre : ")

average_runtime_per_genre = avg_runtime_genre(imdb_data)

labels = average_runtime_per_genre['Genres'].tolist() # The labels are simply the genres here
values = average_runtime_per_genre['Runtime'].tolist()

fig = plot_radial_chart(labels, values)
st.plotly_chart(fig)