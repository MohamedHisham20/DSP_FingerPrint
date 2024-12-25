# apply perceptual hashing to find similar songs
# and search for a song in the database
# using the extracted features
#
import librosa
import hashlib
import json
import numpy as np
from typing import Dict
from scipy.spatial.distance import cosine
from scipy.spatial.distance import euclidean
from scipy.spatial.distance import cityblock
from scipy.spatial.distance import jensenshannon

# function to perceptual hash a song from a np array of songs which are in the format of

# [
#     {
#         "song_name": "song1",
#         "song_features": {
#             "spectral_centroid": 0.1,
#             "spectral_bandwidth": 0.2,
#             "spectral_contrast": [0.3, 0.4, 0.5],
#             "spectral_flatness": 0.6,
#             "mfccs": [0.7, 0.8, 0.9],
#             "pitch": 0.1,
#             "harmonic_to_noise_ratio": 0.2
#         },
#         "vocal_features": {
#             "pitch": 0.3,
#             "harmonic_to_noise_ratio": 0.4,
#             "formants": [0.5, 0.6, 0.7]
#         },
#         "instrumental_features": {
#             "pitch": 0.8,
#             "harmonic_to_noise_ratio": 0.9
#         }
#     },
#
# ]


# Sample structure
songs = [
    {
        "song_name": "song1",
        "song_features": {
            "spectral_centroid": 0.1,
            "spectral_bandwidth": 0.2,
            "spectral_contrast": [0.3, 0.4, 0.5],
            "spectral_flatness": 0.6,
            "mfccs": [0.7, 0.8, 0.9],
            "pitch": 0.1,
            "harmonic_to_noise_ratio": 0.2
        },
        "vocal_features": {
            "pitch": 0.3,
            "harmonic_to_noise_ratio": 0.4,
            "formants": [0.5, 0.6, 0.7]
        },
        "instrumental_features": {
            "pitch": 0.8,
            "harmonic_to_noise_ratio": 0.9
        }
    },
]


# Helper function to create a perceptual hash
def perceptual_hash(features):
    """
    Generate a perceptual hash for a dictionary of features.
    """
    # Flatten and normalize the feature values
    flattened_features = []
    for key, value in features.items():
        if isinstance(value, list):
            flattened_features.extend(value)
        else:
            flattened_features.append(value)
    flattened_features = np.array(flattened_features)

    # Normalize to range [0, 1]
    if flattened_features.max() > 0:
        flattened_features = flattened_features / np.linalg.norm(flattened_features)

    # Create a hash using SHA-256
    hash_object = hashlib.sha256(flattened_features.tobytes())
    return hash_object.hexdigest()


# Add hashes to the structure
for song in songs:
    song["song_features_hash"] = perceptual_hash(song["song_features"])
    song["vocal_features_hash"] = perceptual_hash(song["vocal_features"])
    song["instrumental_features_hash"] = perceptual_hash(song["instrumental_features"])

# Print results
print(json.dumps(songs, indent=4))


# def perceptual_hash_song(song_features: Dict) -> Dict:
#     """
#     Perceptual hashing of a song based on its features.
#
#     :param song_features: Dictionary containing the features of the song.
#     :return: Dictionary containing the perceptual hash of the song.
#     """
#     # Extract features of the song
#     general_features = song_features['general_features']
#     vocal_features = song_features['vocal_features']
#     instrumental_features = song_features['instrumental_features']
#
#     # Hash the general features
#     general_hash = hash_features(general_features)
#
#     # Hash the vocal features
#     vocal_hash = hash_features(vocal_features)
#
#     # Hash the instrumental features
#     instrumental_hash = hash_features(instrumental_features)
#
#     # Combine the hashes
#     perceptual_hash = general_hash + vocal_hash + instrumental_hash
#
#     return perceptual_hash
#
# def hash_features(features: Dict) -> str:
#     """
#     Hash a set of features.
#
#     :param features: Dictionary of features to be hashed.
#     :return: Hash of the features.
#     """
#     # Convert the features to a string
#     features_str = str(features)
#
#     # Hash the string
#     return str(hash(features_str))

def search_database(song_features: Dict, song_database: np.ndarray, distance_metric: str = 'cosine', top_n: int = 5) -> np.ndarray:
    """
    Perceptual hashing of a song based on its features and comparing it with the song database.

    :param song_features: Dictionary containing the features of the song to be hashed.
    :param song_database: Numpy array containing dictionaries of songs and their features.
    :param distance_metric: Distance metric to be used for comparison. Default is 'cosine'.
    :param top_n: Number of similar songs to return. Default is 5.
    :return: Numpy array of top N similar songs based on the distance metric.
    """
    # Extract features of the song to be hashed
    song_general_features = song_features['general_features']
    song_vocals_features = song_features['vocals_features']
    song_instrumental_features = song_features['instrumental_features']

    # Initialize an array to store the distances
    distances = []

    # Iterate over the song database to calculate distances
    for song in song_database:
        # Extract features of the song in the database
        db_general_features = song['general_features']
        db_vocals_features = song['vocals_features']
        db_instrumental_features = song['instrumental_features']

        # Calculate distances based on the selected metric
        general_distance = calculate_distance(song_general_features, db_general_features, distance_metric)
        vocals_distance = calculate_distance(song_vocals_features, db_vocals_features, distance_metric)
        instrumental_distance = calculate_distance(song_instrumental_features, db_instrumental_features, distance_metric)

        # Combine the distances using a weighted sum
        total_distance = 0.5 * general_distance + 0.3 * vocals_distance + 0.2 * instrumental_distance

        # Append the total distance to the distances array
        distances.append(total_distance)

    # Convert the distances array to a numpy array
    distances = np.array(distances)

    # Get the indices of the top N smallest distances
    top_n_indices = np.argsort(distances)[:top_n]

    # Return the top N similar songs
    return song_database[top_n_indices]

def calculate_distance(features1: Dict, features2: Dict, distance_metric: str) -> float:
    """
    Calculate the distance between two sets of features based on the selected distance metric.

    :param features1: Dictionary of features of the first song.
    :param features2: Dictionary of features of the second song.
    :param distance_metric: Distance metric to be used for comparison.
    :return: Distance between the two sets of features.
    """
    if distance_metric == 'cosine':
        return cosine_distance(features1, features2)
    elif distance_metric == 'euclidean':
        return euclidean_distance(features1, features2)
    elif distance_metric == 'cityblock':
        return cityblock_distance(features1, features2)
    elif distance_metric == 'jensenshannon':
        return jensenshannon_distance(features1, features2)
    else:
        raise ValueError("Invalid distance metric. Supported metrics: 'cosine', 'euclidean', 'cityblock', 'jensenshannon'.")

def cosine_distance(features1: Dict, features2: Dict) -> float:
    """
    Calculate the cosine distance between two sets of features.

    :param features1: Dictionary of features of the first song.
    :param features2: Dictionary of features of the second song.
    :return: Cosine distance between the two sets of features.
    """
    # Flatten the features
    def flatten_features(features):
        flattened = []
        for value in features.values():
            if isinstance(value, list):
                flattened.extend(value)
            else:
                flattened.append(value)
        return np.array(flattened)

    features1_array = flatten_features(features1)
    features2_array = flatten_features(features2)

    # Calculate the cosine distance
    return cosine(features1_array, features2_array)

def euclidean_distance(features1: Dict, features2: Dict) -> float:
    """
    Calculate the Euclidean distance between two sets of features.

    :param features1: Dictionary of features of the first song.
    :param features2: Dictionary of features of the second song.
    :return: Euclidean distance between the two sets of features.
    """
    # Flatten the features
    def flatten_features(features):
        flattened = []
        for value in features.values():
            if isinstance(value, list):
                flattened.extend(value)
            else:
                flattened.append(value)
        return np.array(flattened)

    features1_array = flatten_features(features1)
    features2_array = flatten_features(features2)

    # Calculate the Euclidean distance
    return euclidean(features1_array, features2_array)

def cityblock_distance(features1: Dict, features2: Dict) -> float:
    """
    Calculate the cityblock (Manhattan) distance between two sets of features.

    :param features1: Dictionary of features of the first song.
    :param features2: Dictionary of features of the second song.
    :return: Cityblock distance between the two sets of features.
    """
    # Convert the features to numpy arrays
    features1_array = np.array(list(features1.values()))
    features2_array = np.array(list(features2.values()))

    # Calculate the cityblock distance
    return cityblock(features1_array, features2_array)

def jensenshannon_distance(features1: Dict, features2: Dict) -> float:
    """
    Calculate the Jensen-Shannon distance between two sets of features.

    :param features1: Dictionary of features of the first song.
    :param features2: Dictionary of features of the second song.
    :return: Jensen-Shannon distance between the two sets of features.
    """
    # Convert the features to numpy arrays
    features1_array = np.array(list(features1.values()))
    features2_array = np.array(list(features2.values()))

    # Calculate the Jensen-Shannon distance
    return jensenshannon(features1_array, features2_array)

# Example usage
if __name__ == "__main__":
    # Example song database
    song_database = np.array([
        {
            "song_name": "song1",
            "general_features": {
                "spectral_centroid": 0.1,
                "spectral_bandwidth": 0.2,
                "spectral_contrast": [0.3, 0.4, 0.5],
                "spectral_flatness": 0.6,
                "mfccs": [0.7, 0.8, 0.9]
            },
            "vocals_features": {
                "pitch": 0.1,
                "harmonic_to_noise_ratio": 0.2
            },
            "instrumental_features": {
                "pitch": 0.8,
                "harmonic_to_noise_ratio": 0.9
            }
        },
        {
            "song_name": "song2",
            "general_features": {
                "spectral_centroid": 0.2,
                "spectral_bandwidth": 0.3,
                "spectral_contrast": [0.4, 0.5, 0.6],
                "spectral_flatness": 0.7,
                "mfccs": [0.8, 0.9, 1.0]
            },
            "vocals_features": {
                "pitch": 0.2,
                "harmonic_to_noise_ratio": 0.3
            },
            "instrumental_features": {
                "pitch": 0.9,
                "harmonic_to_noise_ratio": 1.0
            }
        }
    ])

    # Example song features like song1 in the database to be hashed
    song_features = {
            "general_features": {
                "spectral_centroid": 0.1,
                "spectral_bandwidth": 0.2,
                "spectral_contrast": [0.3, 0.4, 0.5],
                "spectral_flatness": 0.6,
                "mfccs": [0.7, 0.8, 0.9]
            },
            "vocals_features": {
                "pitch": 0.1,
                "harmonic_to_noise_ratio": 0.2
            },
            "instrumental_features": {
                "pitch": 0.8,
                "harmonic_to_noise_ratio": 0.9
            }
        }

    # test the search_database function
    # create a song with the same features
    song1 = song_features

    # search for the song in the database
    similar_songs = search_database(song1, song_database, distance_metric='cosine', top_n=1)
    print(similar_songs)




