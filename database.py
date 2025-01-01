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
number_of_songs = 11

def create_database():
    """
Database is a list of fingerprints.    
    """
    global number_of_songs
    database = []
    
    full_songs_path = 'Data/original_data/songs'
    vocals_files_path = 'Data/original_data/vocals'
    music_files_path = 'Data/original_data/music'
    
    paths = [full_songs_path, vocals_files_path, music_files_path]
    
    spectrograms = ps.generate_dataset_spectrograms(paths)
    
    i = 0
    dim = ['full_song', 'vocals', 'music']
    
    for dimension in spectrograms:    
        for sg in dimension:
            file_path = sg['file_path']
            name = sg['audio_name']
            sg = sg['SG']
            sr = sg['sr']
            
            fp = Audio_Fingerprint(name,dim[i],file_path,sr,sg)
            database.append(fp.get_fingerprint())
        
        i+=1    
            
    print("Database Created successfully")
    return database    

def main():
    json_ctrl.clear_json_file(database_json_file)
    db = create_database()
    json_ctrl.write_in_json_file(database_json_file, db)    