import librosa
import numpy as np
from typing import Dict, List, Union
from scipy.signal import find_peaks
from typing import Union
from pprint import pprint
from json_ctrl import write_in_json_file

real_num = Union[int, float]

class Song_FingerPrint:
    def __init__(self, song_spectrogram:np.ndarray = None, vocals_spectrogram:np.ndarray = None, music_spectrogram:np.ndarray=None, sampling_rate=200, song_name:str="UNKNOWN"):
        """
        sr: Sampling rate of the original audio
        index zero for song_sg, 1 for vocals, 2 for ,music
        
        """
        self._SR = sampling_rate
        self.__song_sg = song_spectrogram
        self.__vocals_sg = vocals_spectrogram
        self.__music_sg  = music_spectrogram
        
        self.__song_name = song_name
        
        self.__features:list[Dict]= [{} for _ in range(3)]
        self.__hashed_features: list[Dict] = [{} for _ in range(3)]
        
        self.__extract_features()
        write_in_json_file('test.json', self.__features)
        
    def get_song_name(self):
        return self.__song_name
    
    def get_spectral_centroid_3d(self):
        features = self.get_raw_features()
        spectral_centroid_3d: List[real_num] = []
        
        for dict in features:
            spectral_centroid_3d.append(dict["spectral_centroid"])
            
        return spectral_centroid_3d    
    
    def get_hashed_features(self):
        return self.__hashed_features 
    
    def get_raw_features(self):
        return self.__features
    
    def __extract_general_features(self, spectrogram:np.ndarray):
        """
        Extract general features from the song spectrogram.
        """
        features = {}
        power_spec = spectrogram ** 2
        
        # Mean Centroid, Scalar
        specral_centroid = librosa.feature.spectral_centroid(S=power_spec, sr=self._SR).mean()
        specral_centroid = float(specral_centroid)
        features['spectral_centroid'] = specral_centroid
        
        #list
        mfccs = librosa.feature.mfcc(S=librosa.power_to_db(power_spec), sr=self._SR, n_mfcc=13)
        mfccs = mfccs.mean(axis=1).tolist()
        
        for i in range(len(mfccs)):
            mfccs[i] = float(mfccs[i])
        
        features['mfccs'] = mfccs
        
        #features['song_peaks'] = self.__calculate_spectral_peaks(spectrogram)
        
        return features
        
        # # Spectral Bandwidth
        # features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(S=power_spec, sr=self._SR).mean()
        # # Spectral Contrast
        # features['spectral_contrast'] = librosa.feature.spectral_contrast(S=power_spec, sr=self._SR).mean(axis=1).tolist()
        # # Spectral Flatness
        # features['spectral_flatness'] = librosa.feature.spectral_flatness(S=power_spec).mean()

    def __extract_vocal_features(self, spectrogram:np.ndarray):
        """
        Extract vocal-specific features from the vocals spectrogram.
        """
        features = {}
        
        #Extract Pitch --  Scalar
        pitches, magnitudes = librosa.piptrack(S=np.abs(spectrogram), sr=self._SR)
        features['pitch'] = float(pitches[pitches > 0].mean() if pitches.any() else 0)
        
        #Extract harmonics to noise ratio
        hnr = librosa.feature.rms(S=np.abs(spectrogram)) / (np.std(spectrogram, axis=0) + 1e-10)
        features['HNR'] = float(hnr.mean())
        
        # features['vocals_peaks'] = self.__calculate_spectral_peaks(spectrogram)
        
        return features

    def __extract_instrument_features(self, spectrogram:np.ndarray):
        """
        Extract instrument-specific features from the music spectrogram.
        """
        features = {}
        
        chroma = librosa.feature.chroma_stft(S=np.abs(spectrogram), sr=self._SR)
        chroma = chroma.mean(axis=1).tolist()
        
        for i in range(len(chroma)):
            chroma[i] = float(chroma[i])
        
        features['chroma'] = chroma

        # features['music_peaks'] = self.__calculate_spectral_peaks(spectrogram)
        return features
        
        # Spectral Peaks
        # spectral_peaks = np.argmax(np.abs(spectrogram), axis=0)
        # features['spectral_peaks'] = spectral_peaks.tolist()
        # Rhythm (Estimate tempo)
        # onset_env = librosa.onset.onset_strength(S=np.abs(spectrogram), sr=self._SR)
        # tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=self._SR)
        # features['tempo'] = tempo
               
    def __extract_features(self):
        if self.__song_sg is not None:
            features = self.__extract_general_features(self.__song_sg)
            features.update(self.__extract_vocal_features(self.__song_sg))
            features.update(self.__extract_instrument_features(self.__song_sg))
            
            self.__features[0] = features
        
        if self.__vocals_sg is not None:
            features = self.__extract_general_features(self.__vocals_sg)
            features.update(self.__extract_vocal_features(self.__vocals_sg))
            features.update(self.__extract_instrument_features(self.__vocals_sg))
            
            self.__features[1] = features
        
        if self.__music_sg is not None:
            features = self.__extract_general_features(self.__music_sg)
            features.update(self.__extract_vocal_features(self.__music_sg))
            features.update(self.__extract_instrument_features(self.__music_sg))
            
            self.__features[2] = features
    
    def __calculate_spectral_peaks(self, spectrogram):
        """
        Calculate spectral peaks similar to Shazam's approach.

        Args:
            spectrogram (2D array): Magnitude spectrogram (frequency x time).
            min_peak_height (float): Minimum magnitude for a peak to be considered.
            neighborhood_size (int): Size of the local neighborhood to identify peaks.

        Returns:
            List of spectral peaks [(freq_bin, time_bin), ...].
        """
        min_peak_height, neighborhood_size = self.__obtain_min_peaks_and_neighborhood_size(spectrogram)
        
        peaks = []
        # Iterate over time frames (columns in the spectrogram)
        for time_idx in range(spectrogram.shape[1]):
            # Extract the frequency magnitudes for the current time frame
            freq_magnitudes = spectrogram[:, time_idx]
            
            # Find peaks (local maxima) in the frequency spectrum
            peak_indices, _ = find_peaks(freq_magnitudes, height=min_peak_height, distance=neighborhood_size)
            
            # Append (frequency bin, time bin) for each peak
            for freq_idx in peak_indices:
                peaks.append((freq_idx, time_idx))
        
        return peaks
    
    def __obtain_min_peaks_and_neighborhood_size(self, spectrogram, fft_size:int = 2048):
        """
        Analyze the spectrogram to determine suitable min_peak_height and neighborhood_size.

        Args:
            spectrogram (2D array): Magnitude spectrogram (frequency x time).
            fft_size (int): The FFT size used for generating the spectrogram.

        Returns:
            `min_peak_height` and `neighborhood_size`.
        """
        # Spectrogram statistics
        mean_value = np.mean(spectrogram)
        std_dev = np.std(spectrogram)
        max_value = np.max(spectrogram)
        
        # 1. Determine min_peak_height
        # Option 1: Based on mean and standard deviation (adaptive threshold)
        min_peak_height = mean_value + 1.5 * std_dev
        
        # Option 2: Based on a percentage of the maximum amplitude
        min_peak_height_alt = max_value * 0.1  # 10% of the maximum
        
        # Choose the smaller of the two to capture both strong and moderate peaks
        min_peak_height = min(min_peak_height, min_peak_height_alt)

        # 2. Determine neighborhood_size
        # Frequency resolution = Sampling rate / FFT size (assume Nyquist limit applies)
        # Here, we approximate neighborhood size based on the frequency bin spacing
        neighborhood_size = max(5, int(fft_size / spectrogram.shape[0] * 2))  # At least 5 bins
        
        return min_peak_height, neighborhood_size

 
# A list of dicts Each dict is song finger print
# each dict has two keys
Database_Sample = [
    # entry example
    {
        "song_name": " ",
        "features": [
            {
               #key-value pairs for first dict
            },
            {
            
            },
            {
                
            }
        ]
    },
] 
  