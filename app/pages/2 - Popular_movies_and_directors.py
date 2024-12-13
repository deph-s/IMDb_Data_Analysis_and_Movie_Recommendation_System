import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

from plot_functions import plot_bar_chart, plt_hist

def custom_metric_inline(label, value, delta=None): # I did not write this as I don't know CSS and HTML that much, Chatgpt did
    # Safely convert delta to string and handle the formatting properly
    delta_text = f" {str(delta)}" if delta else ""
    
    arrow = ""
    clean_delta = str(delta)
    if delta:
        if delta.startswith('+'):
            arrow = "▲"  # Up arrow for increase
            clean_delta = delta.lstrip('+')  # Remove the `+`
        elif delta.startswith('-'):
            arrow = "▼"  # Down arrow for decrease
            clean_delta = delta.lstrip('-')  # Remove the `-`

    st.markdown(
        f"""
        <div style="
            color: white;
            font-size: 16px;
            line-height: 1.2;
            height: 100px; /* Fixed height for alignment */
        ">
            <div style="font-size: 14px; display: block; margin-bottom: 2px;">{label}</div>
            <div style="font-size: 36px; display: block; margin-bottom: 2px;">{value}</div>
            <div style="
                color: {'#1dbf22' if delta and delta.startswith('+') else 'red' if delta and delta.startswith('-') else '#ffffff'};
                font-size: 18px;
                display: block;
            ">
                {arrow} {clean_delta}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



# Load the movie data : 

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path1 = os.path.join(script_dir, '..', 'data', 'movie_data_clean.csv')
data_path1 = os.path.abspath(data_path1)
film_data = pd.read_csv(data_path1)

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path2 = os.path.join(script_dir, '..', 'data', 'pop_movies.csv')
data_path2 = os.path.abspath(data_path2) 
pop_films = pd.read_csv(data_path2)

num_movies = len(pop_films)
avg_runtime = pop_films['Runtime'].mean()
max_runtime = pop_films['Runtime'].max()
min_runtime = pop_films['Runtime'].min()
nb_genres = 27 # computed in plots notebook
pop_films['Released'] = pd.to_numeric(pop_films['Released'], errors='coerce')
pop_films.loc[pop_films['Released'] <= 1887, 'Released'] = 3000 # Aucun film jamais fait avant 1888 donc si entrée elle est fausse
oldest_film = pop_films['Released'].min()
shortest = pop_films['Runtime'].min()

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
    custom_metric_inline("Number of entries", f"{num_movies:,}", delta='-1,491,359')
    custom_metric_inline("Number of genres", f"{nb_genres:,}", delta='-28')

with col2:
    custom_metric_inline("Average entry length", f"{avg_runtime:.2f}" +"m", delta='+55.47m')
    custom_metric_inline("Longest entry : ", f"{max_runtime/60:.0f}" + "h", delta="-991h")

with col3:
    custom_metric_inline("Oldest entry", f"{oldest_film:,}", delta="+1888")
    custom_metric_inline("Shortest entry", f"{shortest:,}" + "m", delta="-≤ 1 min")


# PLOTLY SECTION ##########################################################################################

st.header("Genre representation in the popular movies dataset (excluding drama) : ")

if 'show_old_version' not in st.session_state: # Code to do the fancy thing with the button changing to the old plot
    st.session_state.show_old_version = False  

if st.session_state.show_old_version:
    glob_genre_list = film_data['Genres'].str.split(',').explode().str.strip() # Consider the whole database
    glob_genre_list = glob_genre_list[~glob_genre_list.isin(['Drama', '\\N'])] # Remove drama and things with no genre indicated
    genre_counts = glob_genre_list.value_counts()

    labels = genre_counts.index.tolist()
    values = genre_counts.values.tolist()

    fig = plot_bar_chart(labels, values)
else:
    glob_genre_list = pop_films['Genres'].str.split(',').explode().str.strip() # Consider the whole database
    glob_genre_list = glob_genre_list[~glob_genre_list.isin(['Drama', '\\N'])] # Remove drama and things with no genre indicated
    genre_counts = glob_genre_list.value_counts()

    labels = genre_counts.index.tolist()
    values = genre_counts.values.tolist()

    fig = plot_bar_chart(labels, values)

# Display the selected bar chart
st.plotly_chart(fig)

if st.button("Compare with old chart" if not st.session_state.show_old_version else "Compare with new chart"): # The button 
    st.session_state.show_old_version = not st.session_state.show_old_version

fig_pop_f = plt_hist(pop_films, 'Runtime', 'Histogram of entry lengths :')
st.plotly_chart(fig_pop_f)
st.write("⤷ Looks like a Beta/Weibull distribution ?")

# Visualisation for the top 250 films : 

top_250 = pop_films.sort_values(by='Rating', ascending=False)[:250]

st.header("What about the top 250 ?")

glob_genre_list = top_250['Genres'].str.split(',').explode().str.strip() # Consider the whole database
glob_genre_list = glob_genre_list[~glob_genre_list.isin(['Drama', '\\N'])] # Remove drama and things with no genre indicated
genre_counts = glob_genre_list.value_counts()
labels = genre_counts.index.tolist()
values = genre_counts.values.tolist()

fig = plot_bar_chart(labels, values)
st.plotly_chart(fig)
st.write("⤷ Comedy is now in fourth place but other than that genres are still mostly in the same order...")

fig_top_250 = plt_hist(top_250, 'Runtime', 'Histogram of entry lengths :')
st.plotly_chart(fig_top_250)
st.write("⤷ We can see the shift of the mean (of the runtime) to the left...")

# Actors and director section : 

st.header("What can we say about directors in our dataset ?")

st.subheader("Some prolific directors : ")

film_data['Directors'] = film_data['Directors'].apply(lambda x: x.split(","))
film_data_e = film_data.explode('Directors', ignore_index=True)
counts = film_data_e['Directors'].value_counts()
counts = counts.reset_index('Directors')
counts = counts[counts['Directors'] != r'\N']
most_prolific = counts[:5]

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Chuck O'Neil", f"{counts['count'][1]}")
with col2:
    st.metric("Doug Walker", f"{counts['count'][2]}")
with col3:
    st.metric("William Hanna", f"{counts['count'][3]}")
with col4:
    st.metric("Joseph Barbera", f"{counts['count'][4]}")
with col5:
    st.metric("James Burrows", f"{counts['count'][5]}")

st.write("⤷ They all produced really long shows with hundreds of episodes")

st.subheader("Which are the most critically acclaimed directors ?")
st.write("Directors with the most films in the top 250 : ")

top_250['Directors'] = top_250['Directors'].apply(lambda x: x.split(",") if isinstance(x, str) else x)
top_250_e = top_250.explode('Directors', ignore_index=True)
counts_a = top_250_e['Directors'].value_counts()
counts_a = counts_a.reset_index('Directors')
counts_a = counts_a[counts_a['Directors'] != r'\N']
most_acclaimed = counts_a[:5]

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Christopher Nolan", f"{counts_a['count'][1]}")
with col2:
    st.metric("Akira Kurosawa", f"{counts_a['count'][2]}")
with col3:
    st.metric("Martin Scorsese", f"{counts_a['count'][3]}")
with col4:
    st.metric("Stanley Kubrick", f"{counts_a['count'][4]}")
with col5:
    st.metric("Alfred Hitchcock", f"{counts_a['count'][5]}")