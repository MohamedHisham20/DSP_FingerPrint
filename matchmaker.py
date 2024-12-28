import numpy as np
from typing import Dict, List
from Song_FingerPrint import Song_FingerPrint
import hash_and_search
import database
import librosa
import os
import json_ctrl

path_song_full = r"C:\\Users\\moham\\OneDrive\\Desktop\\Boda\\CUFE\\SBE_3\\Projects\\DSP\\DSP_FingerPrint\\Data\\Test\\songs\\wen_elkhael.wav"
path_song_vocals = r"C:\\Users\\moham\\OneDrive\\Desktop\\Boda\\CUFE\\SBE_3\\Projects\\DSP\\DSP_FingerPrint\\Data\\Test\\vocals\\wen_elkhael [vocals].wav"
path_song_music = r"C:\\Users\\moham\\OneDrive\\Desktop\\Boda\\CUFE\\SBE_3\\Projects\\DSP\\DSP_FingerPrint\\Data\\Test\\music\\wen_elkhael [music].wav"

class Match_Maker:
    """
Accepts the spectrogram of the audio under investigation
    """
    def __init__(self, audio_file_path: str = path_song_full):
        if not audio_file_path.endswith('wav'):
            print("audio files must have .wav extension")
            return
        
        self._audio_path = audio_file_path
        self.__hashed_fingerprint = self.__create_hashed_form()
        self.__hashed_database = database.create_hashed_database()
        self.__top_matches = self.__search_hashed_database()
        
    
    def get_all_matches(self):
        return self.__top_matches
    
    def get_top_matches(self, display_n=1):        
        return self.__top_matches[:display_n]
            
    def get_hashed_fingerprint(self):
        return self.__hashed_fingerprint
    
    def get_audio_file_path(self):
        return self._audio_path    
    
    def __create_hashed_form(self):  
        audio_data, sample_rate = librosa.load(self._audio_path)
        
        if len(audio_data.shape) > 1: audio_data = np.mean(audio_data, axis=1)
        
        audio_data = audio_data[:sample_rate * 30]
        
        sg = np.abs(librosa.stft(audio_data))
        sg = librosa.amplitude_to_db(sg, ref=np.max)
        
        file_name:str = os.path.basename(self._audio_path)
        
        finger_print = Song_FingerPrint(sg,sg,sg,sample_rate,file_name)
        
        raw_features_3d = finger_print.get_raw_features()
        
        hashed_features_3d = hash_and_search.p_hash(raw_features_3d)
        
        hashed_fingerprint = {
            "song_name": file_name,
            "song_features": hashed_features_3d[0],
            "vocals_features": hashed_features_3d[1],
            "music_features": hashed_features_3d[2]
        }
        
        return hashed_fingerprint

    def __search_hashed_database(self):
        distances:List[Dict[str, float]] = []
        three_hashed_components = []
        
        for key, val in self.__hashed_fingerprint.items():
            if not (key=="song_name"): three_hashed_components.append(val)
        
        for component in three_hashed_components:
            for hashed_fp in self.__hashed_database:
                temp = self.append_hashing_distance_dict(component, hashed_fp["song_features"], "full", hashed_fp["song_name"])
                distances.append(temp)
                
                temp = self.append_hashing_distance_dict(component, hashed_fp["vocals_features"], "vocals", hashed_fp["song_name"])
                distances.append(temp) 
                
                temp = self.append_hashing_distance_dict(component, hashed_fp["music_features"], "instruments", hashed_fp["song_name"])
                distances.append(temp)                 

        
        distances = sorted(distances, key=lambda x: x["distance"], reverse=True)
        return distances
        
        
    def append_hashing_distance_dict(self, hash1, hash2, component:str, song_name:str):
        d = hash_and_search.calculate_hash_distance(hash1, hash2, "cos")
        
        temp = {
            "song_name": song_name + "//" +  component,
            "distance": d
        }
        
        return temp
    
def main():
    mk = Match_Maker()
    json_ctrl.write_in_json_file('test.json', mk.get_top_matches(20)) 
    
main()           