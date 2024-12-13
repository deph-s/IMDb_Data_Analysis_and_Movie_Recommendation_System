import pandas as pd

def avg_runtime_genre(data):
    data['Genres'] = data['Genres'].fillna('').astype(str) # Replace entries with no genre with the empty string 
    data['Genres'] = data['Genres'].str.split(',').apply(lambda x: [genre.strip() for genre in x]) #Splits str on , remove spaces
    data_exploded = data.explode('Genres') # If multiple genres, each one counts for 1 so we explode the dataset 
    data_exploded = data_exploded[data_exploded['Genres'] != '\\N'] # We remove some of the entries with \\N value
    average_runtime_per_genre = data_exploded.groupby('Genres')['Runtime'].mean().reset_index() # reset index because groupby
    average_runtime_per_genre = average_runtime_per_genre[average_runtime_per_genre['Runtime'].notna()]

    return average_runtime_per_genre # We get out a panda dataframe with 2 columns, 1 for the genres and 1 for the avg length