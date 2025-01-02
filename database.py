from typing import List, Dict, Union
import os, librosa
import numpy as np
from Audio_Fingerprint import Audio_Fingerprint
import hashlib
from copy import copy
import json
from pprint import pprint
import json_ctrl
import processing_and_searching as ps

database_json_file = 'json_files/db.json'

real_number = Union[int, float]

#number of songs in database
number_of_songs = 17

full_songs_path = 'Data/original_data/songs'
vocals_files_path = 'Data/original_data/vocals'
music_files_path = 'Data/original_data/music'
    
paths = [full_songs_path, vocals_files_path, music_files_path]
dim = ['full_song', 'vocals', 'music']

def create_database():
    """
Database is a list of fingerprints.    
    """
    global number_of_songs, paths, dim
    
    spectrograms: List[List[Dict]] = ps.generate_dataset_spectrograms(paths)
    full_database = []
    
    i = 0
    for dimension in spectrograms:    
        for sg in dimension:
            file_path = sg['file_path']
            name = sg['audio_name']
            spectrogram = sg['SG']
            sr = sg['SR']
            
            fp = Audio_Fingerprint(audio_name=name, dimension=dim[i], file_path=file_path, sampling_rate=sr, spectrogram=spectrogram)
            full_database.append(fp.get_fingerprint())
            print(sr)
            
        i+=1    
            
    print("Database Created successfully")
    return full_database    

def main():
    json_ctrl.clear_json_file(database_json_file)
    db = create_database()
    json_ctrl.write_in_json_file(database_json_file, db[0])

            