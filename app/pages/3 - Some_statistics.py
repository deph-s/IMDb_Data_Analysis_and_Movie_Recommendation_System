import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import math

from plot_functions import plot_radial_chart, plot_line_chart
from stat_functions import avg_runtime_genre


def custom_metric_inline(label, value, delta=None, unit=None):
    delta_text = f" {delta:+} {unit}" if delta else ""
    st.markdown(
        f"""
        <div style="
            color: white;
            font-size: 16px;
            line-height: 1.2;
            height: 80px; /* Fixed height to ensure alignment */
        ">
            <div style="font-size: 16px; display: block; margin-bottom: 2px;">{label}</div>
            <div style="font-size: 32px; display: block; margin-bottom: 2px;">{value} {unit if unit else ''}</div>
            <div style="
                color: {'green' if delta and delta > 0 else 'red' if delta and delta < 0 else '#ffffff'};
                font-size: 14px;
                display: block;
            ">{delta_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


script_dir = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(script_dir, "..", "data", "popular_entries.csv")
data_path = os.path.abspath(data_path)
pop_entries = pd.read_csv(data_path)

data_path = os.path.join(script_dir, "..", "data", "pop_movies.csv")
data_path = os.path.abspath(data_path)
pop_films = pd.read_csv(data_path)

data_path = os.path.join(script_dir, "..", "data", "movie_data_clean.csv")
data_path = os.path.abspath(data_path)
imdb_data = pd.read_csv(data_path)

st.title("Some more specific statistics on our dataset")

st.header("Do genre impact length ? Average entry length depending on the genre : ")
st.write(
    """We focus here on the dataset of the popular entries, this means that, here, we also include TV Shows, 
hence 'entry' length"""
)

average_runtime_per_genre = avg_runtime_genre(pop_entries)

labels = average_runtime_per_genre[
    "Genres"
].tolist()  # The labels are simply the genres here
values = average_runtime_per_genre["Runtime"].tolist()

fig = plot_radial_chart(labels, values)
st.plotly_chart(fig)

st.header("What about film length ?")
st.write(
    """We're back to our original dataset of popular movies, does including TV Shows which typically have shorter episodes
change the average durations of some genres that much ?"""
)

average_runtime_per_genre_f = avg_runtime_genre(pop_films)

labels_f = average_runtime_per_genre_f[
    "Genres"
].tolist()  # The labels are simply the genres here
values_f = average_runtime_per_genre_f["Runtime"].tolist()

fig_f = plot_radial_chart(labels_f, values_f)
st.plotly_chart(fig_f)
st.write(
    """Not that much for many genres, however we can notice those facts : 
- Animation entries are longer on average now (+21 minutes than previously), this is not a surprise as there are many animation 
entries from animated series, and those usually have episodes with duration ranging from 10 to 30 minutes, thus, excluding them 
increases average duration for that genre quite a bit.

- The short category is still, well short on average but its average duration increased by 26 minutes when we excluded shows. 
Again, that makes sense as channels like adult swim that are really popular show a lot of short TV shows. When we exclude those, 
we are left with short films that are still longer on average.

- Reality TV, Game shows and Talk shows disappeared from the list, makes sense.

- Some genres almost didn't change in average duration : Thriller (4m), Music (4m), Biography (5m), War (5m), Musical (5m). 
This could potentially mean that those genres are mostly represented in films and not in TV Shows.
"""
)

st.header("Is there a link between film length and average rating ?")

pop_films_sorted = pop_films.sort_values(by="Rating", ascending=False)
top250 = pop_films_sorted[:250]

col1, col2 = st.columns(2)

with col1:
    custom_metric_inline(
        "Correlation between film length and average rating (entire dataset) : ",
        f"{imdb_data['Rating'].corr(imdb_data['Runtime']):.3f}",
    )
    custom_metric_inline(
        "Correlation between film length and average rating (popular films) : ",
        f"{pop_films['Rating'].corr(pop_films['Runtime']):.3f}",
    )
with col2:
    custom_metric_inline(
        'Average length of "Popular" films : ',
        f"{math.floor(pop_films['Runtime'].mean())}m{round((pop_films['Runtime'].mean() - math.floor(pop_films['Runtime'].mean()))*60)}s",
    )
    custom_metric_inline(
        'Average length of "Top 250" films : ',
        f"{math.floor(top250['Runtime'].mean())}m{round((top250['Runtime'].mean() - math.floor(top250['Runtime'].mean()))*60)}s <span style='font-size: 16px; color: #39FF14;'>(+ 1 σ)</span>",
    )

st.header("Do People Rate Older Films Higher?")
st.write("Let's start by looking at the trends for the popular films : ")

pop_films["Released"] = pd.to_numeric(pop_films["Released"], errors="coerce")
pop_films = pop_films.dropna(
    subset=["Released", "Rating"]
)  # Drop rows with no rating or no release date
average_ratings_by_year = pop_films.groupby("Released")["Rating"].mean().reset_index()
average_ratings_by_year.columns = ["Year", "Average Rating"]
average_ratings_by_year = average_ratings_by_year.sort_values(by="Year")

fig, pval, rsquared, beta = plot_line_chart(
    average_ratings_by_year,
    "Year",
    "Average Rating",
    "Average rating per year of popular films",
)
st.plotly_chart(fig)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("p-value : ", f"{pval:.2e}")
with col2:
    st.metric("R² :", f"{rsquared:.2f}")
with col3:
    st.metric("Slope of OLS :", "β = " + f"{beta:.2f}")

st.subheader("Why is that ?")
st.write("Taking biases into account : ")

release_year = imdb_data["Released"]
value_counts = release_year.value_counts()
value_counts = value_counts.reset_index(name="Count")
value_counts["Released"] = pd.to_numeric(value_counts["Released"], errors="coerce")
value_counts.sort_values(by="Released", ascending=True, inplace=True)
value_counts = value_counts[value_counts["Released"] >= 1888]

fig = px.histogram(
    value_counts,
    x="Released",
    y="Count",
    nbins=50,
    title="Histogram of Release Years",
)

tickvals = list(range(1880, 2023, 10))

fig.update_xaxes(
    tickmode="array", tickvals=tickvals, ticktext=[str(year) for year in tickvals]
)
fig.update_yaxes(title_text="Number of Movies Released")
st.plotly_chart(fig)
st.markdown(
    """<p style='text-align: center;'>⤷ There is a lot more content that is being released today than in the 
                past so probably more content of lower quality. </p>""",
    unsafe_allow_html=True,
)
st.markdown(
    """<p style='text-align: center;'>⤷ People that watch older movie probably watch movies that are known 
                to be good thus making them last in time.</p>""",
    unsafe_allow_html=True,
)

st.subheader("Does this trend generalizes to the entire dataset ?")

imdb_data["Released"] = pd.to_numeric(imdb_data["Released"], errors="coerce")
imdb_data = imdb_data.dropna(
    subset=["Released", "Rating"]
)  # Drop rows with no rating or no release date
average_ratings_by_year = imdb_data.groupby("Released")["Rating"].mean().reset_index()
average_ratings_by_year.columns = ["Year", "Average Rating"]
average_ratings_by_year = average_ratings_by_year.sort_values(by="Year")

fig, pval, rsquared, beta = plot_line_chart(
    average_ratings_by_year,
    "Year",
    "Average Rating",
    "Average rating per year of all the entries",
)
st.plotly_chart(fig)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("p-value : ", f"{pval:.2e}")
with col2:
    st.metric("R² :", f"{rsquared:.2f}")
with col3:
    st.metric("Slope of OLS :", "β = " + f"{beta:.2f}")

st.write("Not at all !")
st.write("⤷ Big selection bias in the popular movies.")
