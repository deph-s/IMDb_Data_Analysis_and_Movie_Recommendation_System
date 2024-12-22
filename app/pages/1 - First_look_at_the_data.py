import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import math

from plot_functions import plot_bar_chart, plt_hist

###### Calculate variable #####
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "..", "data", "movie_data_clean.csv")
data_path = os.path.abspath(data_path)
imdb_data = pd.read_csv(data_path)

num_movies = len(imdb_data)
avg_runtime = imdb_data["Runtime"].mean()
max_runtime = imdb_data["Runtime"].max()
min_runtime = imdb_data["Runtime"].min()
nb_genres = 28  # Calculated in the data_cleaning notebook
imdb_data["Released"] = pd.to_numeric(imdb_data["Released"], errors="coerce")
imdb_data.loc[imdb_data["Released"] <= 1887, "Released"] = (
    3000  # Aucun film jamais fait avant 1888 donc si entrée elle est fausse
)
oldest_film = int(imdb_data["Released"].min())

st.title("A first look at our dataset :")

##### Top section #####
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Number of entries", f"{num_movies:,}")
    st.metric("Number of genres", f"{nb_genres:,}")

with col2:
    st.metric(
        "Average entry length",
        f"{math.floor(avg_runtime)}m{round((avg_runtime - math.floor(avg_runtime))*60)}s",
    )
    st.metric("Longest entry : ", f"{max_runtime/60:.0f}" + "h")

with col3:
    st.metric("Oldest entry", f"{oldest_film:,}".replace(",", ""))
    st.metric("Shortest entry", value="≤ 1 min")

##### PLOTLY SECTION BAR CHART #####
st.header("Number of movies per genre in full database :")

# Add buttons to filter genres
filter_option = st.radio(
    "Filter genres",
    ["All Genres", "Exclude Drama"],
    index=0,  # Default selection
)

if filter_option == "All Genres":
    filtered_genre_list = imdb_data["Genres"].str.split(",").explode().str.strip()
elif filter_option == "Exclude Drama":
    filtered_genre_list = (
        imdb_data["Genres"].str.split(",").explode().str.strip()
    )
    filtered_genre_list = filtered_genre_list[
        ~filtered_genre_list.isin(["Drama", "\\N"])
    ]  # Exclude drama

# Count genres
genre_counts = filtered_genre_list.value_counts()

# Plot bar chart
labels = genre_counts.index.tolist()
values = genre_counts.values.tolist()

fig = plot_bar_chart(labels, values)

st.plotly_chart(fig)


##### Histogram of entry lengths #####
st.header("Histogram of entry lengths : ")

fig_f = plt_hist(imdb_data, "Runtime", "Histogram of entry lengths :")
st.plotly_chart(fig_f)

st.markdown(
    """⤷ We can note several peaks in the graph: a first one at 30 minutes and anonther one at 60 minutes, which both correspond to the average length of dramas.
Numerous values are concentrated around 90 minutes, and corespond to the films in the data.""",
    unsafe_allow_html=True,
)

##### Describe de fin #####
st.header("Some general statistics : ")
summary_stats = imdb_data.describe()
summary_stats = summary_stats.rename(
    index={
        "count": "Nb Observ",
        "mean": "Mean",
        "std": "Std.",
        "min": "Min",
        "max": "Max",
    }
)
st.write(summary_stats.T)

st.header("First few rows of the dataset : ")
st.dataframe(imdb_data.head())
