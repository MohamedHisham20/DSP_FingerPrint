import numpy as np
from typing import Dict, List
from Song_FingerPrint import Song_FingerPrint
from hash_and_search import calculate_hash_distance
import database
import librosa
import os
import json_ctrl


path = "Data/original_data/songs/FE!N.wav"

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
        self.__raw_database, self.__hashed_database = database.create_database()
        
        self.__matches = self.__search_hashed_database()
     
    def get_raw_database(self):
        return self.__raw_database
    
    def get_hashed_database(self):
        return self.__hashed_database    
    
    def get_all_matches(self):
        return self.__matches
    
    def get_top_matches(self, display_n=5):        
        return self.__matches[:display_n]
            
    def get_hash_str(self)->str:
        return self.__hashed_fingerprint['hash_str']
            
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
        
        finger_print = Song_FingerPrint(input_sampling_rate=sample_rate, input_sg=sg,song_name=file_name, mode='in')
        
        hashed_features = finger_print.get_hashed_features()
        
        hashed_fingerprint = {'song_name':file_name}
        hashed_fingerprint.update(hashed_features)
        
        return hashed_fingerprint

    def __search_hashed_database(self):
        distances:List[Dict[str, float]] = []        

        for fingerprint in self.__hashed_database:
            song_name = fingerprint['song_name']
            input_hash = self.get_hash_str()
            for key, val in fingerprint['hashed_features'].items():
                component = key[:-9]
                d = self.get_hashing_distance_dict(input_hash, val, component,song_name)
                distances.append(d)
                
        sorted_distances = sorted(distances, key=lambda x: x["distance"])
        return sorted_distances         

    def get_hashing_distance_dict(self, hash1, hash2, component:str, song_name:str):
        d = calculate_hash_distance(hash1, hash2, "h")
        
        temp = {
            "song_name": song_name + "//" +  component,
            "distance": d
        }
        
        return temp
    
    def mix_audio_signals(self, path1:str, path2:str):
        pass

def main():
    mk = Match_Maker()
    json_ctrl.clear_json_file('matches.json')
    json_ctrl.clear_json_file('input_hash.json')
    json_ctrl.write_in_json_file('input_hash.json', mk.get_hash_str())
    json_ctrl.write_in_json_file('matches.json', mk.get_all_matches()) 
    
main()           