import numpy as np
from typing import Dict, List
from Song_FingerPrint import Song_FingerPrint
import hash_and_search
import database
import librosa
import os
import json_ctrl


path = "Data/Test/songs/wen_elkhael.wav"

class Match_Maker:
    """
Accepts the spectrogram of the audio under investigation
    """
    def __init__(self, audio_file_path: str = path):
        if not audio_file_path.endswith('wav'):
            print("audio files must have .wav extension")
            return
        
        audio_file_path = os.path.normpath(audio_file_path)
        self._audio_path = audio_file_path
        self.__hashed_fingerprint = self.__create_hashed_form()
        self.__hashed_database = database.create_hashed_database()
        self.__top_matches = self.__search_hashed_database()
        
    
    def get_all_matches(self):
        return self.__top_matches
    
    def get_top_matches(self, display_n=1):        
        return self.__top_matches[:display_n]
            
    def get_hashed_fingerprint(self, get_song_name = True):
        if get_song_name: return self.__hashed_fingerprint

        return {key: value for key, value in self.__hashed_fingerprint.items() if key != 'song_name'}
            
    
    def get_audio_file_path(self):
        return self._audio_path    
    
    def __create_hashed_form(self):
        audio_data, sample_rate = librosa.load(self._audio_path, sr=None)
        
        if len(audio_data.shape) > 1: audio_data = np.mean(audio_data, axis=1)
        
        audio_data = audio_data[:sample_rate * 30]
        
        sg = np.abs(librosa.stft(audio_data))
        sg = librosa.amplitude_to_db(sg, ref=1)
        sg = np.abs(sg)
        
        file_name:str = os.path.basename(self._audio_path)
        
        finger_print = Song_FingerPrint(input_sg=sg, sampling_rate=sample_rate)
        
        raw_features = finger_print.get_raw_features()
        
        hashed_features = hash_and_search.p_hash(raw_features)
        
        hashed_fingerprint = {
            "song_name": file_name,
            'features':hashed_features 
        }
        
        return hashed_fingerprint

    def __search_hashed_database(self):
        distances:List[Dict[str, float]] = []        

        for dimension in self.get_hashed_fingerprint(get_song_name=False):
        
        distances = sorted(distances, key=lambda x: x["distance"], reverse=True)
        return distances
        
        
    def append_hashing_distance_dict(self, hash1, hash2, component:str, song_name:str):
        d = hash_and_search.calculate_hash_distance(hash1, hash2, "h")
        
        temp = {
            "song_name": song_name + "//" +  component,
            "distance": d
        }
        
        return temp
    
def main():
    mk = Match_Maker()
    json_ctrl.clear_json_file('matches.json')
    json_ctrl.write_in_json_file('matches.json', mk.get_top_matches(20)) 
    
main()           