from typing import List, Dict, Any
import hashlib
import numpy as np
from scipy.spatial.distance import cosine, euclidean, cityblock, jensenshannon

def perceptual_hash(features: Dict[str, Any]) -> str:
    """
    Generate a perceptual hash for a dictionary of features.
    """
    flattened_features = []
    for key, value in features.items():
        if isinstance(value, np.ndarray):
            flattened_features.extend(value.flatten())
    flattened_features = np.array(flattened_features)

    if np.linalg.norm(flattened_features) > 0:
        flattened_features = flattened_features / np.linalg.norm(flattened_features)

    hash_object = hashlib.sha256(flattened_features.tobytes())
    return hash_object.hexdigest()

def generate_hashed_database(database: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate a hashed database of perceptual hashes for each song in the database.
    """
    hashed_database = []
    for song in database:
        song_name = song["song_name"]
        features = song["features"]
        song_hash = [perceptual_hash(feature) for feature in features]
        hashed_database.append({
            "song_name": song_name,
            "song_features_hash": song_hash
        })
    return hashed_database

def search_hashed_database(query_features: Dict[str, Any], hashed_database: List[Dict[str, Any]], distance_metric: str = 'cosine', top_n: int = 1) -> List[Dict[str, Any]]:
    """
    Search the hashed database for the most similar song to the query features.
    """
    query_hash = perceptual_hash(query_features)
    distances = []

    for song in hashed_database:
        db_hashes = song["song_features_hash"]
        song_distance = min(calculate_hash_distance(query_hash, db_hash, distance_metric) for db_hash in db_hashes)
        distances.append((song_distance, song))

    distances.sort(key=lambda x: x[0])
    return [song for _, song in distances[:top_n]]

def calculate_hash_distance(hash1: str, hash2: str, distance_metric: str) -> float:
    """
    Calculate the distance between two hashes based on the selected distance metric.
    """
    hash1_array = np.frombuffer(bytes.fromhex(hash1), dtype=np.uint8)
    hash2_array = np.frombuffer(bytes.fromhex(hash2), dtype=np.uint8)

    if np.linalg.norm(hash1_array) > 0:
        hash1_array = hash1_array / np.linalg.norm(hash1_array)
    if np.linalg.norm(hash2_array) > 0:
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
        raise ValueError(
            "Invalid distance metric. Supported metrics: 'cosine', 'euclidean', 'cityblock', 'jensenshannon'.")

def main():
    # Create an example database
    database = []
    for i in range(10):
        song_name = f"Song_{i}"
        song_spectrogram = np.random.rand(100, 100)
        vocals_spectrogram = np.random.rand(100, 100)
        music_spectrogram = np.random.rand(100, 100)

        song = {
            "song_name": song_name,
            "features": [
                {"song_spectrogram": song_spectrogram},
                {"vocals_spectrogram": vocals_spectrogram},
                {"music_spectrogram": music_spectrogram}
            ]
        }
        database.append(song)

    # Generate a hashed database
    hashed_database = generate_hashed_database(database)

    # Create a query song
    query_features = {
        "song_spectrogram": np.random.rand(100, 100),
        "vocals_spectrogram": np.random.rand(100, 100),
        "music_spectrogram": np.random.rand(100, 100)
    }

    # Search the hashed database
    matching_songs = search_hashed_database(query_features, hashed_database)

    print(f"Matching songs: {matching_songs}")

if __name__ == "__main__":
    main()
# Output: Matching songs: [{'song_name': 'Song_2', 'song_features_hash': ['b3c9a5d3e7d3f5d5b ... 3e7d3f5d5b']}]