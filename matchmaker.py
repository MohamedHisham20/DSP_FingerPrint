import librosa
import hashlib
import json
import numpy as np
from typing import Dict
from scipy.spatial.distance import cosine
from scipy.spatial.distance import euclidean
from scipy.spatial.distance import cityblock
from scipy.spatial.distance import jensenshannon
from DB_Generator import perceptual_hash, songs_DB
from Song_FingerPrint import Song_FingerPrint
# Sample structure

class Match_Maker:
    def __init__(self, spectrogram):
        self.DB = songs_DB
        self.sg = spectrogram
        
    def update_spectrogram(self, new_spectrogram):
        self.sg = new_spectrogram    
    
    def __extract_hashed_input_features(self, input_spectrogram):
        input_fingerprint = Song_FingerPrint(input_spectrogram, input_spectrogram, input_spectrogram)
        input_features = input_fingerprint.get_features()
        
        return perceptual_hash(input_features)
    
    def __calculate_hash_distance(self, hash1: str, hash2: str, distance_metric: str) -> float:
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
    
    def search_hashed_database(self, hashed_database: list, distance_metric: str = 'cosine', top_n: int = 1) -> list:
        """
        Search the hashed database for the most similar song to the input features.
        """
        input_hash = self.__extract_hashed_input_features(self.sg)
        song_distances = []
        vocal_distances = []
        music_distances = []

        for song in hashed_database:
            db_hash = song["song_features"]
            distance = self.calculate_hash_distance(input_hash, db_hash, distance_metric)
            song_distances.append((distance, song))

        song_distances.sort(key=lambda x: x[0])
        return [song for _, song in song_distances[:top_n]]








