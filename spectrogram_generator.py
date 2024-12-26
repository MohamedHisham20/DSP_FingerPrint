import os
import matplotlib.pyplot as plt
import numpy as np
import librosa.display
import librosa

class SG_Generator:
    """
An abstract class that provides functions for generating spectrograms
"""

    def generate_spectrogram_from_folder(input_folder, get_song_name:bool=False):
        # Generate spectrogram using librosa from audio files in input_folder
        directories_names = os.listdir(input_folder)
        spectrograms = []    

        for directory in directories_names:
            selected_folder = os.path.join(input_folder, directory)
            for file in os.listdir(selected_folder):
                if file.endswith('.wav'):
                    file_path = os.path.join(selected_folder, file)
                    audio_data, sample_rate = librosa.load(file_path, sr=None)

                    # Ensure data is mono for simplicity
                    if len(audio_data.shape) > 1:
                        audio_data = np.mean(audio_data, axis=1)

                    # Trim to first 20 seconds
                    audio_data = audio_data[:sample_rate * 20]

                    S = np.abs(librosa.stft(audio_data))
                    S_db = librosa.amplitude_to_db(S, ref=np.max)

                    if get_song_name:
                        spectrograms.append({'song_name':file, 'SG':S_db})
                    else: spectrograms.append(S_db)    
                        
        return spectrograms
    
    def generate_input_spectrogram(file_path:str):
        audio_data, SR= librosa.load(file_path, sr=None)
        
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
            
        audio_data = audio_data[:SR * 20]
        
        decibel_SG = librosa.amplitude_to_db(np.abs(librosa.stft(audio_data)))
        
        return decibel_SG