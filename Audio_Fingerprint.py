import librosa
import numpy as np
from typing import Dict, List, Union
from scipy.signal import find_peaks
from typing import Union, Tuple
import processing_and_searching as ps
import json_ctrl

real_num = Union[int, float]

class Audio_Fingerprint:
    """
Create a finger print for an audio file. The finger print contains parameters as:\n
path, audio_name, dimension(song, vocals, music), raw_features, hash_str.
    """
    def __init__(self, audio_name:str, dimension, file_path, sampling_rate:real_num , spectrogram:np.ndarray):
            self.__audio_name = audio_name
            self.__path = file_path
            self.__dimension = dimension
            self.__sampling_rate = sampling_rate
            self.__sg = spectrogram
            
            self.__fingerprint = self.__create_fingerprint()
   
    def get_fingerprint(self):
        return self.__fingerprint
    
    def get_raw_features(self):
        return self.__fingerprint['raw_features']
    
    def get_file_path(self):
        return self.__fingerprint['file_path']
    
    def get_audio_name(self):
        return self.__fingerprint['audio_name']
    
    def get_dimension(self):
        return self.__fingerprint['dimension']
    
    def get_hash_str(self):
        return self.__fingerprint['hash_str']
        
    def get_spectral_peaks(self):
        return self.__spectral_peaks
    
    def get_spectral_peaks_set(self):
        return self.__peaks_set
    
    def get_energy_envelope(self):
        return self.__energy_envelope          
      
    def __extract_general_features(self, spectrogram:np.ndarray, sampling_rate):
        """
        Extract general features that can  apply to all spectrograms.
        """
        features = {}
        power_spec = spectrogram ** 2
        
        # Extract Spectral Bandwidth, scalar, works on audio or spectrogram
        # spectral_bandwidth = librosa.feature.spectral_bandwidth(S=spectrogram, sr=sampling_rate)
        # features['spectral_bandwidth'] = float(spectral_bandwidth.mean())
        
        # # Extract Spectral Rolloff, scalar, works on audio or spectrogram
        # spectral_rolloff = librosa.feature.spectral_rolloff(S=spectrogram, sr=sampling_rate)
        # features['spectral_rolloff'] = float(spectral_rolloff.mean())
        
        # # Mean Centroid, Scalar, works on audio or spectrogram
        spectral_centroid = librosa.feature.spectral_centroid(S=power_spec, sr=sampling_rate).mean()
        spectral_centroid = float(spectral_centroid)
        features['spectral_centroid'] = spectral_centroid

        # # Spectral Contrast, List, works on audio or spectrogram
        spectral_contrast = librosa.feature.spectral_contrast(S=spectrogram, sr=sampling_rate)
        features['spectral_contrast'] = spectral_contrast.mean(axis=1).tolist()
        
        # Extract Zero Crossing Rate, float, works on the audio singal
        # zero_crossing_rate = librosa.feature.zero_crossing_rate(y=librosa.istft(spectrogram))
        # features['zero_crossing_rate'] = float(zero_crossing_rate.mean())
         
        #list, works on audio or spectrogram
        mfccs = librosa.feature.mfcc(S=librosa.power_to_db(power_spec), sr=sampling_rate, n_mfcc=13)
        mfccs = mfccs.mean(axis=1).tolist()
        for i in range(len(mfccs)): mfccs[i] = float(mfccs[i])
        features['mfccs'] = mfccs
        
        # Min-Max Normalized Energy Distribution, List
        energy = np.sum(spectrogram, axis=0)
        energy = ps.min_max_normalize(energy)
        energy = energy.tolist()
        self.__energy_envelope = features['energy_envelope'] = energy
        
        #Shazam Spectral Peaks
        self.__spectral_peaks, self.__peaks_set = self.__calculate_spectral_peaks(spectrogram)
        features['spectral_peaks'] = self.__spectral_peaks

        return features
    
    def __extract_chroma(self, spectrogram, sampling_rate):
        """
        return chroma list, works on audio or spectrogram
        """
        chroma = librosa.feature.chroma_stft(S=spectrogram, sr=sampling_rate)
        chroma = chroma.mean(axis=1).tolist()
        
        for i in range(len(chroma)): chroma[i] = float(chroma[i])
        
        return chroma
    
    def __extract_onset_strength(self, spectrogram, sampling_rate):
        onset_env = librosa.onset.onset_strength(S=spectrogram, sr=sampling_rate).tolist()
        return onset_env
    
    #applied on the audio signal
    # def __extract_tempo(self, spectrogram, sampling_rate, onset_strength):
    #     tempo, _ = librosa.beat.beat_track(onset_envelope=onset_strength, sr=sampling_rate)
    #     return tempo
     
    #applied on audio signal
    # def __extract_tonnetz(self, sg, sr):
    #     tonnetz = librosa.feature.tonnetz(chroma=librosa.feature.chroma_cqt(S=sg, sr=sr))
    #     return tonnetz.mean(axis=1).tolist() 
   
    def __extract_energy_entropy(self, sg):
        energy_entropy = -np.sum((sg / np.sum(sg, axis=0)) * np.log2(sg / (np.sum(sg, axis=0) + 0.000001)), axis=0)
        return energy_entropy.tolist()

    def __extract_spectral_flateness(self, sg):
        """
    return spectral flateness mean value, works on audio and spectrogram   
        """
        spectral_flatness = librosa.feature.spectral_flatness(S=sg)
        return float(spectral_flatness.mean())
         
    def __extract_full_song_features(self, spectrogram:np.ndarray, sampling_rate):
        """
    Features that best apply to the full song spectrogram.\n
        """
        features = {}
        
        #chroma, List
        features["full_chroma"] = self.__extract_chroma(spectrogram, sampling_rate)
        
        #onset strength
        features["full_onset_strength"] = self.__extract_onset_strength(spectrogram, sampling_rate)
        
        #tempo
        # features["full_tempo"] = self.__extract_tempo(spectrogram, sampling_rate, features['full_onset_strength'])
        
        # #full tonnetz
        # features['full_tonnetz'] = self.__extract_tonnetz(spectrogram, sampling_rate)
        
        #entropy
        features['full_energy_entropy'] = self.__extract_energy_entropy(spectrogram)
        
        #spectral_flateness
        features['spectral_flateness'] =self.__extract_spectral_flateness(spectrogram)
        
        return features
        
    def __extract_vocal_features(self, spectrogram:np.ndarray, sampling_rate):
        """
        Extract vocal-specific features from the vocals spectrogram.\n
        pitch, formants, HNR, 
        """
        features = {}
        
        #spectral flateness 
        features['vocals_spectral_flateness'] = self.__extract_spectral_flateness(spectrogram)
        
        #Extract Pitch --  Scalar, work on audio and spectrogram
        pitches, magnitudes = librosa.piptrack(S=spectrogram, sr=sampling_rate)
        features['vocals_pitch'] = float(pitches[pitches > 0].mean() if pitches.any() else 0)
        
        #Extract harmonics to noise ratio, Scalar,works on spectrogram or audio
        hnr = librosa.feature.rms(S=spectrogram) / (np.std(spectrogram, axis=0) + 1e-10)
        features['HNR'] = float(hnr.mean())
        
        #jitter
        #shimmer
        #spectral envelope
        #voice activity detection
        #Cepstral Peak Prominence
        
        return features

    def __extract_instrument_features(self, spectrogram:np.ndarray, sampling_rate):
        """
        Extract instrument-specific features from the music spectrogram.\n
        beat, strength
        """
        features = {}
        
        #tonnetz
        # features['music_tonnetz'] = self.__extract_tonnetz(spectrogram, sampling_rate)
        
        #energy entropy
        features['music_energy_entropy'] = self.__extract_energy_entropy(spectrogram)
        
        #List
        features['music_chroma'] = self.__extract_chroma(spectrogram, sampling_rate)
        
        #Extract Pitch --  Scalar
        pitches, magnitudes = librosa.piptrack(S=np.abs(spectrogram), sr=sampling_rate)
        features['music_pitch'] = float(pitches[pitches > 0].mean() if pitches.any() else 0)

        #onset strength, list
        features['music_onset_strength'] = self.__extract_onset_strength(spectrogram, sampling_rate)
        
        return features
        
        #tempo, audio feature
        # features['music_tempo'] = self.__extract_tempo(spectrogram, sampling_rate, features['music_onset_strength'])
         
        #inharmonicity
        #energy envelope 
    
    def __calculate_spectral_peaks(self, spectrogram):
        """
        Calculate spectral peaks similar to Shazam's approach.

        Args:
            spectrogram (2D array): Magnitude spectrogram (frequency x time).
            min_peak_height (float): Minimum magnitude for a peak to be considered.
            neighborhood_size (int): Size of the local neighborhood to identify peaks.

        Returns:
            List of spectral peaks  + set of [(freq_bin, time_bin), ...].
        """
        min_peak_height, neighborhood_size = self.__obtain_min_peaks_and_neighborhood_size(spectrogram)
        
        peaks: List[List] = []
        peaks_set = set()
        # Iterate over time frames (columns in the spectrogram)
        for time_idx in range(spectrogram.shape[1]):
            # Extract the frequency magnitudes for the current time frame
            freq_magnitudes = spectrogram[:, time_idx]

            # Find peaks (local maxima) in the frequency spectrum
            peak_indices, _ = find_peaks(freq_magnitudes, height=min_peak_height, distance=neighborhood_size)

            # Append (frequency bin, time bin) for each peak
            for freq_idx in peak_indices:
                peaks.append([int(freq_idx), time_idx])
                peaks_set.add((int(freq_idx), time_idx))
        
        return peaks, peaks_set
    
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

    def __create_fingerprint(self):
        raw_features = self.__extract_general_features(self.__sg, self.__sampling_rate)
        hash_str = ps.p_hash(raw_features)
        
        fingerprint = {
            'file_path': self.__path,
            'audio_name': self.__audio_name,
            'dimension' : self.__dimension,
            'raw_features' : raw_features,
            'hash_str': hash_str
        }
        return fingerprint
    
               