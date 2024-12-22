import pandas as pd
import json
import requests
import s3fs
from tabulate import tabulate
from imdb import Cinemagoer
import os
from bs4 import BeautifulSoup
import time
import re
import gender_guesser.detector as gender

""" 

File storing all of the intermediate functions that I used to gather, process the data, scrape stuff etc.... 

All the function are ordered in the order in which they were originally written, some functions may take a really long time to 
run, for instance the scraping stuff, to give a demonstration of the different functions and of the general data processing 
pipeline, I'm running the functions on the first 20 elements of the dataset at the end of the file. Feel free to experiment as 
you please.

"""

# Data gathering functions, Initial open data download, API calls, Cinemagoer python library and scraping in this order :

# Started to import the raw data in Pandas, all of those need to be cleaned etc...


def get_raw_data():  # Adapt this function with the new data links

    fs = s3fs.S3FileSystem(
        client_kwargs={
            "endpoint_url": "https://" + "minio.lab.sspcloud.fr"
        },  # If ran on SSP Cloud, keys are already filled in
    )

    MY_BUCKET = "keithmoon"  # My ID on SSP Cloud (Antoine)
    fs.get(
        f"{MY_BUCKET}/diffusion/title.basics.tsv.gz", "title.basics.tsv.gz"
    )  # Get the compressed files from S3
    fs.get(f"{MY_BUCKET}/diffusion/title.crew.tsv.gz", "title.crew.tsv.gz")
    fs.get(f"{MY_BUCKET}/diffusion/title.ratings.tsv.gz", "title_ratings.tsv.gz")
    fs.get(f"{MY_BUCKET}/diffusion/title.episode.tsv.gz", "title.episode.tsv.gz")

    titles_df = pd.read_csv(
        "title.basics.tsv.gz", sep="\t", compression="gzip"
    )  # Basic infos, title, release, runtime, genre
    crew_df = pd.read_csv(
        "title.crew.tsv.gz", sep="\t", compression="gzip"
    )  # Adds infos on director, writer etc...
    ratings_df = pd.read_csv(
        "title_ratings.tsv.gz", sep="\t", compression="gzip"
    )  # Gives us critics scores
    episodes_df = pd.read_csv(
        "title.episode.tsv.gz", sep="\t", compression="gzip"
    )  # Infos on tv shows episodes

    films_ = pd.merge(
        titles_df, crew_df, on="tconst"
    )  # Merge on unique film identifier
    films__ = pd.merge(films_, ratings_df, on="tconst")
    films = pd.merge(
        films__, episodes_df, on="tconst", how="left"
    )  # Left join because I want to add the episode id in case it exists, if it doesn't I just don't touch the row, this will allow me to remove from the dataframe any row that has a episode id filled in so that I can specifically exclude episodes of tv shows from the dataframe

    films = films.drop(
        columns=["titleType", "originalTitle", "isAdult", "endYear", "writers"]
    )  # Don't care

    films.rename(
        columns={
            "tconst": "film_id",  # Giving better names to columns
            "primaryTitle": "Title",
            "averageRating": "Rating",
            "startYear": "Released",
            "runtimeMinutes": "Runtime",
            "genres": "Genres",
            "directors": "Directors",
        },
        inplace=True,
    )

    films["Released"] = pd.to_numeric(
        films["Released"], errors="coerce"
    )  # For some reason unknown to man released and runtime weren't int
    films["Runtime"] = pd.to_numeric(films["Runtime"], errors="coerce")

    return films


# Quick functions to explore the different genres represented in our data :


def quick_database_overview(data):
    g = data["Genres"].unique()  # Get all the different possible genres
    genres = []
    for i in g:
        if isinstance(i, str):
            if "," in i:
                i = i.replace(",", " ")
                _ = i.split(" ")
                for j in _:
                    if j not in genres:
                        genres.append(j)
    print(f" There are : {len(genres)} genres represented.")
    print(f" Those are : {genres}.")
    print("Here are the first lines of the database : ")
    print(tabulate(data.head(), headers="keys", tablefmt="grid"))
    print("Here are some summary statistics about the numeric columns : ")
    print(tabulate(data.describe(), headers="keys", tablefmt="grid"))


def remove_tv_episodes(data):
    data = data[
        data["parentTconst"].isna()
    ]  # Remove row if a TV Show name is given as it is an episode
    return data


# Here's the script that I used to keep only the movies in the database, It takes a long while to run but if ran it will start
# outputting the name and the ids of the films in a .txt file, I ran it on the dataframe of the entries with more than 25k votes.


def keepfilmsonly(data, start_from=0):
    ia = Cinemagoer()
    to_process = data[data.index >= start_from]

    for index, row in to_process.iterrows():
        imdb_id = row["film_id"]
        movie = ia.get_movie(
            imdb_id[2:]
        )  # imdb_id starts with 'tt' and cinemagoer only uses the digits that come after
        with open(
            "output.txt", "a"
        ) as file:  # Initially I just dumped all of that in a simple txt file and filtered with the ids after
            if movie["kind"] == "movie":  # Check if it's a movie
                file.write(f"{index} : {movie['title']} : {row['film_id']}\n")

    id_list = []  # Get the list of film ids
    with open("output.txt", "r") as file:
        for line in file:
            id = line.strip().split(":")[
                -1
            ]  # Because the txt is composed of lines like : "The Godfather : tt62658513"
            id_list.append(id.strip())

    data = data[
        data["film_id"].isin(id_list)
    ]  # Only keep the rows that have their id present in the id list of films
    return data


def get_films_plots(
    data, omdb_api_key, start_from=0
):  # Used a ton of API keys because of daily request requirements, wanted to speed up the process
    request = f"http://www.omdbapi.com/?i=tt3896198&apikey={omdb_api_key}"  # To adapt
    to_process = data[data.index >= start_from]
    ids = to_process[
        "film_id"
    ].tolist()  # Simply convert the film_ids to a list to loop over it

    json_file_path = "movies_plots.json"
    if not os.path.exists(json_file_path):
        with open(json_file_path, "w") as json_file:
            json.dump([], json_file)

    # Make the calls to get the plots of the various movies and to dump it in a json:

    with open(
        "movies_plots.json", "r+"
    ) as json_file:  # r+ to append to the file and to not overwrite all the work so far
        current_data = json.load(json_file)

        for id in ids:
            response = requests.get(
                f"http://www.omdbapi.com/?i={id}&apikey={omdb_api_key}"
            )

            if response.status_code == 200:  # 200 is a positive answer for the server
                data = response.json()

                if (
                    data.get("Response") == "True"
                ):  # We get a dictionnary where Response is a key
                    plot = data.get(
                        "Plot", "No plot available"
                    )  # If there's no plot we default to writing "No plot available"

                    current_data.append(
                        {  # Json is not great for really large file as we are reading the entire file every time
                            "Plot": plot,  # then we append to it and then we overwrite the whole thing with the new file but here
                            "imdbID": id,  # it is not too slow so that's the strategy
                        }
                    )

                    json_file.seek(0)  # Just to get to the first line
                    json.dump(
                        current_data, json_file, indent=4
                    )  # We overwrite the previous file with the new data

                else:
                    print(f"Error: {data.get('Error')}")
            else:
                print(f"Failed to fetch data for {id}")


def scrape_film_reviews(
    imdb_id,
):  # It scrapes the 10 first reviews for the specific film whose id is inputted

    BASE_URL = "https://www.imdb.com/title/{}/reviews/"  # We can just fill in the id of a film to get to its review page
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }  #  Used to be able to request stuff to the server, simulates a real browser so we don't get instantly 403'd

    url = BASE_URL.format(imdb_id)
    response = requests.get(url, headers=headers)
    i = 0

    if (
        response.status_code != 200
    ):  # 200 is that everything went well, but if it didn't went well we signal it
        print(f"Failed to fetch data: {response.status_code}")
        return []

    soup = BeautifulSoup(
        response.text, "html.parser"
    )  # We use the native html parser and use bs to make the html easier to process
    reviews = []

    review_containers = soup.find_all(
        "div", class_="ipc-html-content-inner-div"
    )  # If you inspect the HTML code of the review page on IMDb, you see that the reviews are stored in div with the parameter that I entered

    for i, review in enumerate(review_containers):
        if i >= 10:  # Limit to the first 10 reviews
            break
        review_text = review.get_text(strip=True)
        if review_text:
            reviews.append(review_text)
        time.sleep(
            0.5
        )  # Avoid getting ip banned because of too many requests 0.5 seconds seems to be the shortest safe timeout

    return reviews


# Scraping the entirety of the reviews of the ~6600 popular films took around 10 hours (I ran this script on the already filtered dataset)


def get_json_reviews(
    data, starting_index=0
):  # Same as always, it takes a while so we can resume the process at a specific index
    to_process = data[data.index >= starting_index]
    ids = to_process["film_id"].tolist()

    json_file_path = (
        "movies_reviews.json"  # Convenient to create the file if it doesn't exist yet
    )
    if not os.path.exists(json_file_path):
        with open(json_file_path, "w") as json_file:
            json.dump([], json_file)  # We have to dump at least [] to make a valid json

    # Make the calls to get the reviews of the various movies and to dump it in a json:

    with open(
        "movies_reviews.json", "r+"
    ) as json_file:  # r+ to append to the file and to not overwrite all the work so far
        current_data = json.load(json_file)
        for id in ids:
            reviews = scrape_film_reviews(
                id
            )  # Takes a while because of the hidden time.sleep in this function
            current_data.append(
                {  # Json is not great for really large file as we are reading the entire file every time
                    "Reviews": reviews,  # then we append to it and then we overwrite the whole thing with the new file but here
                    "imdbID": id,  # it is not too slow so that's the strategy
                }
            )
            json_file.seek(0)  # Just to get to the first line
            json.dump(
                current_data, json_file, indent=4
            )  # We overwrite the previous file with the new data


def preprocess_text(
    text,
):  # Using regular expression, remove additional spaces, punctuation, lowercase the text and remove all special characters to get raw strings on which we can do text embeddings

    try:
        text = json.loads(
            '"' + text + '"'
        )  # Sometimes there are special characters that are escaped, apparently this is the way to handle them properly
    except json.JSONDecodeError:
        text = text

    text = text.lower()

    text = text.replace("\\", " ")

    text = re.sub(r"[^\w\s]", "", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text


def preprocess_plots():  # Obviously to run this function there should be a json file of plots to process

    with open("movies_plots.json", "r") as file:
        data = json.load(file)

    processed_data = []
    for entry in data:
        plot = entry.get(
            "Plot", ""
        )  # There is always a plot in our database anyways but I added a default behaviour
        processed_plot = preprocess_text(plot)

        processed_entry = {"imdbID": entry["imdbID"], "Plot": processed_plot}

        processed_data.append(processed_entry)

    with open(
        "processed_plots.json", "w"
    ) as outfile:  # We just dump all that we processed in the new file
        json.dump(processed_data, outfile, indent=4)

    print("Processed JSON saved to 'processed_plots.json'")


# The following functions processes all of the reviews as a big string and creates a json file like the previous one, at the end
# the string is the concatenation of the reviews without distinction between the reviews, it's not a problem because the text
# embedding process that we are gonna apply is oblivious to this fact, it only considers the information in the strings.


def preprocess_reviews():  # Obviously to run this function there should be a json file of reviews to process

    with open("movies_reviews.json", "r") as file:
        data = json.load(file)

    processed_data = []
    for entry in data:
        reviews = entry.get(
            "Reviews", ""
        )  # There is always a plot in our database anyways but I added a default behaviour
        if isinstance(
            reviews, list
        ):  # Handle the case where reviews might unexpectedly be a list
            reviews = " ".join(reviews)  # Convert the list of reviews into a string
        processed_reviews = preprocess_text(reviews)

        processed_entry = {"imdbID": entry["imdbID"], "Reviews": processed_reviews}

        processed_data.append(processed_entry)

    with open(
        "processed_reviews.json", "w"
    ) as outfile:  # We just dump all that we processed in the new file
        json.dump(processed_data, outfile, indent=4)

    print("Processed JSON saved to 'processed_reviews.json'")


def attach_text(
    data,
):  # Quick function to add a new column to the dataframe with the text of plots and reviews concatenated
    with open("processed_plots.json", "r") as file:
        processed_plots = json.load(file)
    with open("processed_reviews.json", "r") as file:
        processed_reviews = json.load(file)

    combined_dict = {}
    for plot, review in zip(processed_plots, processed_reviews):
        imdb_id = plot["imdbID"]
        plot_text = plot.get("Plot", "")
        reviews_text = str(
            review.get("Reviews", "")
        )  # Don't know why reviews was a list of characters, changed it to a string
        combined_text = f"{plot_text} {reviews_text}".strip()
        combined_dict[imdb_id] = combined_text

    data["text_data"] = data["film_id"].map(lambda x: combined_dict.get(x, ""))

    return data

def get_names(id_list, start_from=0):
    to_process = id_list[start_from:]
    ia = Cinemagoer()
    for index, id in enumerate(to_process):
        id = id[2:]
        with open('names.txt', 'a') as file:
            director_name = ia.get_person(id)
            file.write(f"{index+start_from} : {director_name}\n")


def get_gender_proportion(name_file):
    male = 0
    gender_unsure = []
    d = gender.Detector()
    line_count = 0
    with open(f'/home/onyxia/work/projet_python_ds2024/app/{name_file}', 'r') as file:
        for line in file:
            line_count += 1
    with open(f'/home/onyxia/work/projet_python_ds2024/app/{name_file}', 'r') as file:
        for line in file:
            first_name = line.split(' ')[2]
            gen = d.get_gender(first_name)
            if gen == 'unknown':
                gender_unsure.append(line)
            if gen == 'andy':
                male += 0.5 # Assume 50/50 distribution for gender neutral names.
            if gen in ['male', 'mostly_male']:
                male += 1 
    return male/(line_count - len(gender_unsure)), gender_unsure

""" 

For the sake of making the app lighter, I did not include sentence-transformers nor torch in the requirements.txt as the download 
is really long and it takes a while when running the setup.py. However for grading purposes, here is the code that I wrote to 
compute the text embeddings, I am commenting it out as it won't run because sentence-transformers and torch can't be imported.

Also I ran the code on a GPU machine with CUDA support to compute the embeddings in reasonable time. 


from sentence_transformers import SentenceTransformer
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu' 
model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

text_embeddings = model.encode(film_data['text_data'].tolist()) # Big calculation
np.save('embeddings.npy', text_embeddings)

"""

# Start by obtening the raw data from the zip files on S3 :
print("Downloading original compressed databases....")
raw_data = get_raw_data()  # We still drop some of the useless columns.
print("Done !")
quick_database_overview(raw_data)  # Here's how it looks at the beginning.
print("Filtering and sorting the database....")
data = raw_data[raw_data["numVotes"] >= 25000]  # Only keep the 'popular entries'
data = data.sort_values(by="Rating", ascending=False)  # Sort by descending rating
quick_database_overview(data)  # Here's how it looks so far
data = remove_tv_episodes(data)
data = data[
    :50
]  # To process the scraping faster, 50 because it happens that a vast majority of the top rated entries are tv shows
print("Making requests to exclude TV shows from the database....")
data = keepfilmsonly(data)
print("Done !")
quick_database_overview(data)
print("Obtaining plots and movie reviews.....")
api_key = os.getenv("API_KEY")
get_films_plots(
    data, api_key
)  # I'm putting my own API Key here, yes I know it's very bad practice but it's needed to make the function work from the get go.
get_json_reviews(data)
print("Done !")
preprocess_plots()
preprocess_reviews()
print("Final processing step, attaching text to the database.....")
data = attach_text(
    data
)  # After processing all of the text we can finally attach it, then after that as seen above, embeddings are computed on this column.tolist()
print("Done !")
print(
    "Not displaying the last step as the reviews and plots are too long to be properly displayed in the command line"
)
print("Feel free to run this on a notebook to take a look at the column !")
print("End of the data gathering and processing steps.")
print("Running functions used to analyse gender representation among directors...")
pop_films = pd.read_csv('/home/onyxia/work/projet_python_ds2024/app/data/pop_movies.csv')
pop_films['Directors'] = pop_films['Directors'].apply(lambda x: x.split(','))
pop_films = pop_films.explode(column='Directors', ignore_index=False)
ids = pop_films['Directors'].unique()
ids_sample = ids[:10]
print("Making requests to obtain the name of the directors...")
get_names(ids_sample)
print("Done !")
r, l = get_gender_proportion('names.txt')
print(f"In our very small sample dataset (n=10) the proportion of men is : {r}. However, I am unsure of the gender associated with {len(l)} name(s), thus I undershoot the real proportion of men...")
print("EOF...")