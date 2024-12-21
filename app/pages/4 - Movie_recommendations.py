import streamlit as st
import pandas as pd
import os
from model import recommend_movies
import json


script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "..", "data", "pop_movies.csv")
data_path = os.path.abspath(data_path)
pop_films = pd.read_csv(data_path)

with open(
    "/home/onyxia/work/projet_python_ds2024/app/data/movies_plots.json", "r"
) as file:
    movie_plots = json.load(file)
movie_plots = {item["imdbID"]: item["Plot"] for item in movie_plots}

valid_input = True
movie_list = [movie.strip() for movie in pop_films["Title"].tolist()]

st.title("Recommend me a movie!")

user_input = st.multiselect(  # Multiselect looks nicer and solves annoying issues with parsing the input of the user like titles with a , inside like Monsters, Inc.
    "Select movies you like:", options=movie_list
)

with st.sidebar:  # Button on sidebar looks nicer I think
    if st.button("Recommend me movies"):
        valid_input = True
        final_input = user_input

        # Validate if the movies are part of the list
        for film_clean in final_input:
            if film_clean not in movie_list:
                st.write(f'"{film_clean}" is not in the movie database')
                valid_input = False

        if valid_input:
            liked_movies_indexes = [
                movie_list.index(movie) for movie in final_input if movie in movie_list
            ]
            st.session_state["recommendations"] = recommend_movies(
                pop_films, liked_movies_indexes
            )
        else:
            st.session_state["recommendations"] = []

# Dynamically show recommendations
if "recommendations" in st.session_state and st.session_state["recommendations"]:
    st.subheader("Recommended Movies:")
    for i in st.session_state["recommendations"][:5]:
        title = pop_films.iloc[i]["Title"]
        film_id = pop_films.iloc[i]["film_id"]
        plot = movie_plots.get(film_id, "Plot not available")
        st.markdown(
            f"<p><span style='text-decoration: underline; font-weight: bold;'>{title} :</span> {plot}</p>",
            unsafe_allow_html=True,
        )
