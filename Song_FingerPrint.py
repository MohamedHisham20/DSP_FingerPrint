import librosa
import numpy as np
from typing import Dict, List

class Song_FingerPrint:
    def __init__(self, song_spectrogram:np.ndarray = None, vocals_spectrogram:np.ndarray = None, music_spectrogram:np.ndarray=None, sampling_rate = 200, song_name:str="UNKNOWN"):
        """
        sr: Sampling rate of the original audio
        index zero for song_sg, 1 for vocals, 2 for ,music
        
        """
        self._SR = sampling_rate
        self.__song_sg = song_spectrogram
        self.__vocals_sg = vocals_spectrogram
        self.__music_sg  = music_spectrogram
        self.__song_name = song_name
        self.__features:list[Dict]= []
        
    
    def get_song_name(self):
        return self.__song_name
    
    def get_song_features(self):
        return self.__features[0]
    
    def get_vocals_features(self):
        return self.__features[1]
    
    def get_music_features(self):
        return self.__features[2]
    
    def get_features(self):
        return self.__features
    
    def extract_general_features(self, spectrogram:np.ndarray):
        """
        Extract general features from the song spectrogram.
        """
        features = {}
        
        power_spec = np.abs(spectrogram) ** 2
        
        mfccs = librosa.feature.mfcc(S=librosa.power_to_db(power_spec), sr=self._SR, n_mfcc=13)
        
        features['mfccs'] = mfccs.mean(axis=1).tolist()
        
        features['spectral_centroid'] = librosa.feature.spectral_centroid(S=power_spec, sr=self._SR).mean()

        # # Spectral Bandwidth
        # features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(S=power_spec, sr=self._SR).mean()

        # # Spectral Contrast
        # features['spectral_contrast'] = librosa.feature.spectral_contrast(S=power_spec, sr=self._SR).mean(axis=1).tolist()

        # # Spectral Flatness
        # features['spectral_flatness'] = librosa.feature.spectral_flatness(S=power_spec).mean()

        # MFCCs (mean across time)

        
        return features
 
    def extract_vocal_features(self, spectrogram:np.ndarray):
        """
        Extract vocal-specific features from the vocals spectrogram.
        """
        features = {}
        
        # Pitch (Using librosa's piptrack for pitch estimation)
        pitches, magnitudes = librosa.piptrack(S=np.abs(spectrogram), sr=self._SR)
        features['pitch'] = pitches[pitches > 0].mean() if pitches.any() else 0
        
        # Harmonic-to-Noise Ratio (HNR)
        hnr = librosa.feature.rms(S=np.abs(spectrogram)) / np.std(spectrogram, axis=0)
        features['harmonic_to_noise_ratio'] = hnr.mean()
        
        # Formants (Approximation: Use peaks in the spectrum)
        spectral_peaks = np.argmax(np.abs(spectrogram), axis=0)
        features['formants'] = spectral_peaks[:5].tolist()  # First 5 peaks as formants

        return features

    def extract_instrument_features(self, spectrogram:np.ndarray):
        """
        Extract instrument-specific features from the music spectrogram.
        """
        features = {}
        
        # Chroma Features
        chroma = librosa.feature.chroma_stft(S=np.abs(spectrogram), sr=self._SR)
        features['chroma_features'] = chroma.mean(axis=1).tolist()

        # Spectral Peaks
        spectral_peaks = np.argmax(np.abs(spectrogram), axis=0)
        features['spectral_peaks'] = spectral_peaks.tolist()

        # Rhythm (Estimate tempo)
        # onset_env = librosa.onset.onset_strength(S=np.abs(spectrogram), sr=self._SR)
        # tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=self._SR)
        # features['tempo'] = tempo
        
        return features

    def extract_features(self):
        if self.__song_sg is not None:
            features = self.extract_general_features(self.__song_sg)
            features.update(self.extract_vocal_features(self.__song_sg))
            features.update(self.extract_instrument_features(self.__song_sg))
            self.__features.append(features)
        
        if self.__vocals_sg is not None:
            features = self.extract_general_features(self.__vocals_sg)
            features.update(self.extract_vocal_features(self.__vocals_sg))
            features.update(self.extract_instrument_features(self.__vocals_sg))
            self.__features.append(features)
        
        if self.__music_sg is not None:
            features = self.extract_general_features(self.__music_sg)
            features.update(self.extract_vocal_features(self.__music_sg))
            features.update(self.extract_instrument_features(self.__music_sg))
            self.__features.append(features)
               