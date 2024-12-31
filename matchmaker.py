import numpy as np
from typing import Dict, List
from Song_FingerPrint import Song_FingerPrint
import processing_and_searching as ps
import database
import librosa
import os
import json_ctrl
import soundfile as sf

path = "Data/original_data/songs/FE!N.wav"

class Match_Maker:
    """
Accepts the spectrogram of the audio under investigation
    """
    def __init__(self, path1:str, path2:str = None,  mix:bool = False, w1:float = None):        
        
        self.__audio = None
        self.__sg = None
                
        self.__hashed_fingerprint = self.__create_hashed_form(path1=path1, path2=path2, mix=mix, w1=w1)
        self.__raw_database, self.__hashed_database = database.create_database()
        
        self.__matches = self.__search_hashed_database()
    
    def new_audio_path(self, path1:str, path2:str = None, mix=False, w1=0):
        self.__create_hashed_form(path1, path2, mix, w1)
        
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
                
    def __create_hashed_form(self, path1:str, path2:str=None, mix:bool = False, w1:float = None):        
        
        audio, sampling_rate = ps.get_audio_and_sampling_rate(path1, path2, mix, w1)
        sg = ps.generate_spectrogram(audio)
        song_name = self.__get_song_name(path1=path1, path2=path2, mix=mix, save_sr=sampling_rate, mix_audio=audio)
        
        finger_print = Song_FingerPrint(input_sampling_rate=sampling_rate, input_sg=sg,song_name=song_name, mode='in')
        
        hashed_features = finger_print.get_hashed_features()
        
        hashed_fingerprint = {'song_name':song_name}
        hashed_fingerprint.update(hashed_features)
        
        return hashed_fingerprint


    def __get_song_name(self, path1, path2 = None, mix = False, save_sr=None, mix_audio = None):
        """
        get song name or compose name in case of mix.\n
        the mixed audio will be saved in a .wav file
        """
        name1:str = os.path.basename(path1)
        song_name = name1
        
        if mix:
            name2:str = os.path.basename(path2)
            song_name = name1+'and'+name2+'mix.wav'
            save_path = 'saved_mix/'+song_name
            sf.write(save_path, mix_audio, save_sr)
            print(f"mix of {name1} and {name2} has been saved")
            
        return song_name    

    def __search_hashed_database(self):
        distances:List[Dict[str, float]] = []        

        for fingerprint in self.__hashed_database:
            song_name = fingerprint['song_name']
            input_hash = self.get_hash_str()
            for key, val in fingerprint['hashed_features'].items():
                component = key[:-9]
                d = self.__get_hashing_distance_dict(input_hash, val, component,song_name)
                distances.append(d)
                
        sorted_distances = sorted(distances, key=lambda x: x["distance"])
        return sorted_distances         

    def __get_hashing_distance_dict(self, hash1, hash2, component:str, song_name:str):
        d = ps.calculate_hash_distance(hash1, hash2, "h")
        
        temp = {
            "song_name": song_name + "//" +  component,
            "distance": d
        }
        
        return temp

def main():
    mk = Match_Maker()
    json_ctrl.clear_json_file('matches.json')
    json_ctrl.clear_json_file('input_hash.json')
    json_ctrl.write_in_json_file('input_hash.json', mk.get_hash_str())
    json_ctrl.write_in_json_file('matches.json', mk.get_all_matches()) 
    
main()           