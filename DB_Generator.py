import os
import librosa
import hashlib
import json
import numpy as np
from spectrogram_generator import generate_spectrogram_using_librosa
from Song_FingerPrint import Song_FingerPrint
from typing import List, Dict

SR = 100
Songs_Database:List[Dict] = []

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

songs_spectrograms = generate_spectrogram_using_librosa('Task 5 Data/original data/songs', True)
vocals_spectrograms = generate_spectrogram_using_librosa('Task 5 Data/original data/vocals')
music_spectrograms = generate_spectrogram_using_librosa('Task 5 Data/original data/music')

for i in range(songs_spectrograms):
    song_name = songs_spectrograms[i]["song_name"]
    ssg = songs_spectrograms[i]["spectrogram"]
    vsg = vocals_spectrograms[i]
    msg = music_spectrograms[i]
    
    song_fingerprint = Song_FingerPrint(ssg, vsg, msg, SR, song_name)
    
    Songs_Database[i]["song_name"] = song_name
    
    song_features = perceptual_hash(song_fingerprint.get_song_features())
    Songs_Database[i]["song_features"] = song_features
    
    vocals_features = perceptual_hash(song_fingerprint.get_vocals_features())
    Songs_Database[i]["vocals_features"] = vocals_features
    
    music_features = perceptual_hash(song_fingerprint.get_music_features())
    Songs_Database[i]["music_features"] = music_features
    
    