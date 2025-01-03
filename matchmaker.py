import numpy as np
from typing import Dict, List
from Audio_Fingerprint import Audio_Fingerprint
import processing_and_searching as ps
import database
import librosa
import os
import json_ctrl
import soundfile as sf

path = "Data/original_data/songs/FE!N.wav"

class SingletonMeta(type):
    """
    A metaclass for creating singleton classes.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Match_Maker():
    """
A singelton class responsible for processing all inputs and performing the search process\n
Also once instantiated, entire database will be loaded.\n
A slightly expensive process that will take a minute at most. 
    """
    def __init__(self):
        self.mix_path = ""         
        self.__full_db = database.create_database()
        
    def new_search(self, path1:str, path2:str = None, mix=False, w1=0.5):        
        
        self.__fingerprint = self.__create_fingerprint(path1, path2, mix, w1)
        self.__matches = self.__search_database()
        
    def get_all_matches(self):
        return self.__matches
    
    def get_top_matches(self, display_n=10):        
        return self.__matches[:display_n]
                
    def __create_fingerprint(self, path1:str, path2:str=None, mix:bool = False, w1:float = None):        
        if mix:
            audio, sr, audio_name, path = ps.mix_audio(path1, path2, w1, 1-w1)
            self.mix_path = path
        else:
            audio, sr = ps.extract_audio_signal(path1)
            audio_name = os.path.basename(path1)
            audio_name, ext = os.path.splitext(audio_name)
            path = path1
        
        sg = ps.generate_spectrogram(audio)
            
        finger_print = Audio_Fingerprint(audio_name=audio_name, dimension='none', file_path=path, sampling_rate=sr, spectrogram=sg)
        
        return finger_print
        
    

    def __search_database(self):
        indices = []
        
        for fp in self.__full_db:
            index = self.__calc_similarity_index(fp)
            indices.append(index)
                
        indices = sorted(indices, key=lambda x: x["score"], reverse=True)
        
        return indices         


    def __calc_similarity_index(self, db_fingerprint):
        name = db_fingerprint['audio_name']
        path = db_fingerprint['file_path']
        dim = db_fingerprint['dimension']
        hash_str = db_fingerprint['hash_str']
        raw_features = db_fingerprint['raw_features']
        peaks = raw_features['spectral_peaks']
        e = raw_features['energy_envelope']
        
        peaks = {tuple(inner_list) for inner_list in peaks}
        
        hash_dist = ps.calculate_hash_distance(hash_str, self.__fingerprint.get_hash_str())
        score = 1 - float(hash_dist)
        
        score += ps.calc_shared_spectral_peaks_ratio(peaks, self.__fingerprint.get_spectral_peaks_set())
        
        score += ps.calc_energy_envelope_correlation(e, self.__fingerprint.get_energy_envelope())
        
        score = (score / 3) * 100
        
        return {
            'score': score, 
            'audio_name': name, 
            'file_path':path,
            'dimension':dim
        }
        

def main():
    file_path = 'Data/original_data/songs/Rolling_in_the_deep(Original).mp3.wav'
    
    mk = Match_Maker()
    mk.new_search(path1=file_path)
    
    print(mk.get_top_matches(1)) 
    
           