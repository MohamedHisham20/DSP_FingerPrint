import json
import hashlib
import numpy as np
from typing import Dict

songs = [
    {
        "song_name": "song1",
        "song_features": {
            "spectral_centroid": 0.1,
            "mfccs": [ ],
        },
        "vocal_features": {
            "pitch": 0.1,
            "harmonic_to_noise_ratio": 0.2, 
            "formants": []
        },
        "music_features": {
            "chroma": [],
            "spectral_peaks": []
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


# # Add hashes to the structure
# for song in songs:
#     song["song_features_hash"] = perceptual_hash(song["song_features"])
#     song["vocal_features_hash"] = perceptual_hash(song["vocal_features"])
#     song["music_features_hash"] = perceptual_hash(song["music_features"])

# # # Print results
# # print(json.dumps(songs, indent=4))

# def create_hashed_database(songs: list) -> list:
#     """
#     Create a hashed database from a list of songs and their features.
#     """
#     hashed_database = []
#     for song in songs:
#         song["song_features_hash"] = perceptual_hash(song["song_features"])
#         song["vocal_features_hash"] = perceptual_hash(song["vocal_features"])
#         song["music_features_hash"] = perceptual_hash(song["music_features"])
#         hashed_database.append(song)
#     return hashed_database

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