import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

embeddings = np.load("/home/onyxia/work/https://github.com/deph-s/IMDb_Data_Analysis_and_Movie_Recommendation_System/app/data/embeddings.npy")


def recommend_movies(data, liked_movies, nb_rec=5):  # Default to 5 recommendations
    numeric_features = ["Released", "Runtime", "numVotes", "Rating"]
    scaler = StandardScaler()
    data[numeric_features] = scaler.fit_transform(data[numeric_features])
    numeric_features = data[numeric_features].values
    combined_features = np.hstack([numeric_features, embeddings])
    user_preference_vector = np.mean(combined_features[liked_movies], axis=0)
    similarities = cosine_similarity(
        [user_preference_vector], combined_features
    ).flatten()
    recommended_indices = np.argsort(similarities)[::-1]
    recommended_indices = [i for i in recommended_indices if i not in liked_movies]
    return recommended_indices[:nb_rec]
