
import librosa
import hashlib
import json
import numpy as np
from typing import Dict
from scipy.spatial.distance import cosine
from scipy.spatial.distance import euclidean
from scipy.spatial.distance import cityblock
from scipy.spatial.distance import jensenshannon

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
            "spectral_centroid": 0.1,
            "spectral_bandwidth": 0.2,
            "spectral_contrast": [0.3, 0.4, 0.5],
            "spectral_flatness": 0.6,
            "mfccs": [0.7, 0.8, 0.9],
            "pitch": 0.1,
            "harmonic_to_noise_ratio": 0.2
        },
        "music_features": {
            "spectral_centroid": 0.1,
            "spectral_bandwidth": 0.2,
            "spectral_contrast": [0.3, 0.4, 0.5],
            "spectral_flatness": 0.6,
            "mfccs": [0.7, 0.8, 0.9],
            "pitch": 0.1,
            "harmonic_to_noise_ratio": 0.2
        }
    },
    {
        "song_name": "song2",
        "song_features": {
            "spectral_centroid": 0.2,
            "spectral_bandwidth": 0.3,
            "spectral_contrast": [0.4, 0.5, 0.6],
            "spectral_flatness": 0.7,
            "mfccs": [0.8, 0.9, 1.0],
            "pitch": 0.2,
            "harmonic_to_noise_ratio": 0.3
        },
        "vocal_features": {
            "spectral_centroid": 1.0,
            "spectral_bandwidth": 2.0,
            "spectral_contrast": [3.0, 4.0, 6.0],
            "spectral_flatness": 7.0,
            "mfccs": [8.0, 9.0, 1.0],
            "pitch": 0.2,
            "harmonic_to_noise_ratio": 0.3
        },
        "music_features": {
            "spectral_centroid": 0.2,
            "spectral_bandwidth": 0.3,
            "spectral_contrast": [0.4, 0.5, 0.6],
            "spectral_flatness": 0.7,
            "mfccs": [0.8, 0.9, 1.0],
            "pitch": 0.2,
            "harmonic_to_noise_ratio": 0.3
        }
    }
]


def perceptual_hash(features: Dict) -> str:
    """
    Generate a perceptual hash for a dictionary of features.
    """
    flattened_features = []
    for value in features.values():
        if isinstance(value, list):
            flattened_features.extend(value)
        else:
            flattened_features.append(value)
    flattened_features = np.array(flattened_features)

    if flattened_features.max() > 0:
        flattened_features = flattened_features / np.linalg.norm(flattened_features)

    hash_object = hashlib.sha256(flattened_features.tobytes())
    return hash_object.hexdigest()


# Add hashes to the structure
for song in songs:
    song["song_features_hash"] = perceptual_hash(song["song_features"])
    song["vocal_features_hash"] = perceptual_hash(song["vocal_features"])
    song["music_features_hash"] = perceptual_hash(song["music_features"])

# # Print results
# print(json.dumps(songs, indent=4))

def create_hashed_database(songs: list) -> list:
    """
    Create a hashed database from a list of songs and their features.
    """
    hashed_database = []
    for song in songs:
        song["song_features_hash"] = perceptual_hash(song["song_features"])
        song["vocal_features_hash"] = perceptual_hash(song["vocal_features"])
        song["music_features_hash"] = perceptual_hash(song["music_features"])
        hashed_database.append(song)
    return hashed_database

def create_hashed_database_json(input_json_path: str, output_json_path: str):
    """
    Create a hashed database from a JSON file of songs and their features, and save it to another JSON file.
    """
    with open(input_json_path, 'r') as infile:
        songs = json.load(infile)

    hashed_database = []
    for song in songs:
        song["song_features_hash"] = perceptual_hash(song["song_features"])
        song["vocal_features_hash"] = perceptual_hash(song["vocal_features"])
        song["music_features_hash"] = perceptual_hash(song["music_features"])
        hashed_database.append(song)

    with open(output_json_path, 'w') as outfile:
        json.dump(hashed_database, outfile, indent=4)


def search_hashed_database(input_features: Dict, hashed_database: list, distance_metric: str = 'cosine', top_n: int = 1) -> list:
    """
    Search the hashed database for the most similar song to the input features.
    """
    input_hash = perceptual_hash(input_features)
    distances = []

    for song in hashed_database:
        db_hash = song["song_features_hash"]
        distance = calculate_hash_distance(input_hash, db_hash, distance_metric)
        distances.append((distance, song))

    distances.sort(key=lambda x: x[0])
    return [song for _, song in distances[:top_n]]

def calculate_hash_distance(hash1: str, hash2: str, distance_metric: str) -> float:
    """
    Calculate the distance between two hashes based on the selected distance metric.
    """
    hash1_array = np.frombuffer(bytes.fromhex(hash1), dtype=np.uint8)
    hash2_array = np.frombuffer(bytes.fromhex(hash2), dtype=np.uint8)

    # Normalize the arrays to prevent overflow
    hash1_array = hash1_array / np.linalg.norm(hash1_array)
    hash2_array = hash2_array / np.linalg.norm(hash2_array)

    if distance_metric == 'cosine':
        return cosine(hash1_array, hash2_array)
    elif distance_metric == 'euclidean':
        return euclidean(hash1_array, hash2_array)
    elif distance_metric == 'cityblock':
        return cityblock(hash1_array, hash2_array)
    elif distance_metric == 'jensenshannon':
        return jensenshannon(hash1_array, hash2_array)
    else:
        raise ValueError("Invalid distance metric. Supported metrics: 'cosine', 'euclidean', 'cityblock', 'jensenshannon'.")


# Example usage
if __name__ == "__main__":

    # Example song database
    hashed_database = create_hashed_database(songs)

    # ##################### using json ##################
    # input_json_path = 'input_songs.json'
    # output_json_path = 'hashed_songs.json'
    # create_hashed_database_json(input_json_path, output_json_path)
    # ###################################################


    # test the search_database function
    input_features = {
        "spectral_centroid": 1.0,
            "spectral_bandwidth": 2.0,
            "spectral_contrast": [3.0, 4.0, 6.0],
            "spectral_flatness": 7.0,
            "mfccs": [8.0, 9.0, 1.0],
            "pitch": 0.2,
            "harmonic_to_noise_ratio": 0.3
    }

    similar_songs = search_hashed_database(input_features, hashed_database, distance_metric='cosine', top_n=1)
    print(json.dumps(similar_songs, indent=4))




