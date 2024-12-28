from typing import List, Dict, Union
import os, librosa
import numpy as np
from Song_FingerPrint import Song_FingerPrint
import hashlib
from copy import copy
import json
from pprint import pprint
from json_ctrl import write_in_json_file
from perceptual_hashing import perceptual_hash

real_number = Union[int, float]

number_of_songs = 11

database:List[Dict] = [{} for _ in range(number_of_songs)]
normalized_database: List[Dict] = [{} for _ in range(number_of_songs)]
hashed_database: List[Dict]= {}

total_spectral_centroids: List[List[real_number]] = [[] for _ in range(3)]
total_pitches: List[List[real_number]] = [[] for _ in range(3)]
total_HNRs: List[List[real_number]] = [[] for _ in range(3)]

total_mfccs: List[List[List]] = [[] for _ in range(3)]
total_chroma_peaks: List[List[List]] = [[] for _ in range(3)]


def generate_spectrograms(input_folder_path, get_song_name: bool = False):
    # Generate spectrogram using librosa from audio files in input_folder
    spectrograms = []
    files = os.listdir(input_folder_path)
    
    for file in files:
        if file.endswith('.wav'):
            file_path = os.path.join(input_folder_path, file)
            audio_data, sample_rate = librosa.load(file_path, sr=None)
            

            # Ensure data is mono for simplicity
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)

            # Trim to first 20 seconds
            audio_data = audio_data[:sample_rate * 20]

            S = np.abs(librosa.stft(audio_data))
            S_db = librosa.amplitude_to_db(S, ref=np.max)

            if get_song_name:
                spectrograms.append({'song_name': file, 'SG': S_db, 'SR':sample_rate})
            else:
                spectrograms.append(S_db)
    
    return spectrograms

def create_raw_database():    
    songs_spectrograms: List[Dict] = generate_spectrograms('Data/original_data/songs', True)
    vocals_spectrograms = generate_spectrograms('Data/original_data/vocals')
    music_spectrograms = generate_spectrograms('Data/original_data/music')
    
    for i in range(len(songs_spectrograms)):
        song_name = songs_spectrograms[i]["song_name"]
        sampling_rate = songs_spectrograms[i]["SR"]
        
        ssg = songs_spectrograms[i]["SG"]
        vsg = vocals_spectrograms[i]
        msg = music_spectrograms[i]
        
        # Features Extraction Processed in the Song_FingerPrint Class
        song_fingerprint = Song_FingerPrint(ssg, vsg, msg, sampling_rate, song_name)
        
        features = song_fingerprint.get_raw_features()
        
        for i in range(3):
            total_spectral_centroids[i].append(features[i]["spectral_centroid"])
            total_pitches[i].append(features[i]["pitch"])
            total_HNRs[i].append(features[i]["HNR"])
            total_chroma_peaks[i].append(features[i]["chroma"])
            total_mfccs[i].append(features[i]["mfccs"])
            
        temp:Dict = {
            "song_name": song_name,
            "features": features
        }
        
        database.append(temp)

def create_hashed_database():
    create_raw_database()
    
    for song_fp in database:
        hashed_database['song_name'] = song_fp['song_name']
        features_3d = song_fp["features"]
        
        dimensions_strings = [" " for _ in range(3)]
        
        for dimension in features_3d:
            dimension_str = perceptual_hash(dimension)
            dimensions_strings.append(dimension_str)
            
        hashed_database['song_features'] = dimensions_strings[0]
        hashed_database['vocals_features'] = dimensions_strings[1]
        hashed_database['music_features'] = dimensions_strings[2]    

def normalize_database():
    normalize(total_spectral_centroids)
    normalize(total_mfccs, True, "mfccs")
    normalize(total_pitches, "pitch")
    normalize(total_HNRs)
    normalize(total_chroma_peaks, True, "chroma")

def create_normalized_database():
    create_raw_database()
    normalize_database()
    
    #create normalized database
    for k in range(len(normalized_database)):
        
        normalized_database[k]["song_name"] = database[k]["song_name"]
        normalized_database[k]["features"] = [{} for _ in range(3)]
        features_list = normalized_database[k]["features"]
        
        for j in range(len(features_list)):
            dictionary = features_list[j]
            
            dictionary["spectral_centroid"] = total_spectral_centroids[k][j]
            dictionary["mfccs"] = total_mfccs[k][j]
            dictionary["pitch"] = total_pitches[k][j]
            dictionary["HNR"] = total_HNRs[k][j]
            dictionary["chroma"] = total_chroma_peaks[k][j]
                    
def normalize(feature_3d: List):
    for list in feature_3d:
        if complex: #list is a list of lists (Complex Feature like MFCCs)
           min_max_complex_normalize(list) 
        else:
            min_val = min(list)
            max_val = max(list)
            min_max_normalize(min_val, max_val, list)

def write_raw_data():
    write_in_json_file('db.json', database)
        
def write_normalized_data():
    write_in_json_file('norm_data.json', normalize_database)        
    
def write_hashed_data():
    write_in_json_file('hashed_db.json', hashed_database)

def min_max_complex_normalize(list_of_lists: List[List[real_number]]):
    # if any(len(inner_list) == 0 for inner_list in list_of_lists):
    #     raise ValueError("One or more inner lists are empty")
    
    list_of_arrays = [np.array(inner_list) for inner_list in list_of_lists]
        
    try: matrix = np.stack(list_of_arrays)
    except ValueError as e: raise ValueError(f"Error stacking arrays: {e}")
    
    print(f"Matrix Shape: {matrix.shape}")  
    
    min_vals = matrix.min(axis=0)
    max_vals = matrix.max(axis=0)
    
    for i in range(matrix.shape[1]):
            if max_vals[i] != min_vals[i]:
                matrix[:, i] = (matrix[:, i] - min_vals[i]) / (max_vals[i] - min_vals[i])
            else:
                matrix[:, i] = 0
    # Update the original sublists with normalized values
    for j in range(len(list_of_lists)):
        list_of_lists[j][:] = matrix[j].tolist()

def min_max_normalize(min, max, list):
    """
x_norm = (x-x_min) / (x_max-x_min)    
    """
    for i in range(len(list)):
        list[i] = (list[i] - min) / (max-min)   

def create_database():
    create_raw_database()
    create_normalized_database()
    create_hashed_database()

def write_data():
    write_raw_data()
    write_normalized_data()
    write_hashed_data()

def main():
    create_hashed_database()
    write_hashed_data()
    
main()