from typing import List, Dict, Union
import os, librosa
import numpy as np
from Song_FingerPrint import Song_FingerPrint
import hashlib
from copy import copy
import json
from pprint import pprint
import json_ctrl
import processing_and_searching as ps

database_json_file = 'db.json'
hashed_db_json_file = 'hashed_db.json'

real_number = Union[int, float]

#number of songs in database
number_of_songs = 11

# normalized_database: List[Dict] = [{} for _ in range(number_of_songs)]

# total_spectral_centroids: List[List[real_number]] = [[] for _ in range(3)]
# total_pitches: List[List[real_number]] = [[] for _ in range(3)]
# total_HNRs: List[List[real_number]] = [[] for _ in range(3)]

# total_mfccs: List[List[List]] = [[] for _ in range(3)]
# total_chroma_peaks: List[List[List]] = [[] for _ in range(3)]

def generate_spectrograms(input_folder_path, get_song_name: bool = False):
    """
return a list of spectrgorams of the .wav files in the input folder.\n
if get_song_name_is true, the song name and the audio file sampling rate are also returned.\n
    """
    spectrograms:List[Dict] = []
    files = os.listdir(input_folder_path)
    
    for file in files:
        if file.endswith('.wav'):
            file_path = os.path.join(input_folder_path, file)

            audio_data, sample_rate = ps.extract_audio_signal(file_path)

            S_db = ps.generate_spectrogram(audio_data)

            if get_song_name:
                spectrograms.append({'song_name': file, 'SG': S_db, 'SR':sample_rate})
            else:
                spectrograms.append({'SG': S_db, 'SR':sample_rate})  
    
    return spectrograms

def create_database():
    """
    return a tuple of the raw and the hashed database
    """
    global number_of_songs
    
    database:List[Dict] = [{} for _ in range(number_of_songs)]
    hashed_database: List[Dict] = [{} for _ in range(number_of_songs)]
        
    songs_spectrograms: List[Dict] = generate_spectrograms('Data/original_data/songs', True)
    vocals_spectrograms: List[Dict] = generate_spectrograms('Data/original_data/vocals')
    music_spectrograms:List[Dict] = generate_spectrograms('Data/original_data/music')
    
    for i in range(len(songs_spectrograms)):
        sr = []
        
        song_name = songs_spectrograms[i]["song_name"]
        
        sr.append(songs_spectrograms[i]["SR"])
        sr.append(vocals_spectrograms[i]["SR"])
        sr.append(music_spectrograms[i]["SR"])
        
        
        ssg = songs_spectrograms[i]["SG"]
        vsg = vocals_spectrograms[i]["SG"]
        msg = music_spectrograms[i]["SG"]
        
        # Features Extraction and hashing processed in the Song_FingerPrint Class
        song_fingerprint = Song_FingerPrint(sampling_rate=sr, song_spectrogram=ssg, vocals_spectrogram=vsg, music_spectrogram=msg, song_name=song_name)
        
        raw_features = song_fingerprint.get_raw_features()
        hashed_features = song_fingerprint.get_hashed_features()
            
        database[i] = {"song_name":song_name, "features":raw_features}
        hashed_database[i] = {'song_name':song_name,
                              'hashed_features':hashed_features
                              }
            
    return database, hashed_database    

def write_data():
    db, h_db = create_database()
    
    json_ctrl.write_in_json_file('db.json', db)
    json_ctrl.write_in_json_file('hashed_db.json', h_db)

def main():
    json_ctrl.clear_json_file(database_json_file)
    json_ctrl.clear_json_file(hashed_db_json_file)
    write_data()
    
main()    