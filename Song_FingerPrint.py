import librosa
import numpy as np
from typing import Dict

class Song_FingerPrint:
    def __init__(self, song_spectrogram:np.ndarray, vocals_spectrogram:np.ndarray, music_spectrogram:np.ndarray, sampling_rate):
        """
        sr: Sampling rate of the original audio
        """
        self.song_sg = song_spectrogram
        self.vocals_sg = vocals_spectrogram
        self.music_sg = music_spectrogram
        
        self.general_features:Dict = {}
        self.vocals_features:Dict = {}
        self.music_features:Dict = {}
        
        self.sr = sampling_rate
        
        self.extract_general_features()
        self.extract_vocal_features()
        self.extract_instrument_features()
    
    def extract_general_features(self):
        """
        Extract general features from the song spectrogram.
        """
        # Compute power spectrogram
        power_spec = np.abs(self.song_sg) ** 2

        # Spectral Centroid
        self.general_features['spectral_centroid'] = librosa.feature.spectral_centroid(S=power_spec, sr=self.sr).mean()

        # Spectral Bandwidth
        self.general_features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(S=power_spec, sr=self.sr).mean()

        # Spectral Contrast
        self.general_features['spectral_contrast'] = librosa.feature.spectral_contrast(S=power_spec, sr=self.sr).mean(axis=1).tolist()

        # Spectral Flatness
        self.general_features['spectral_flatness'] = librosa.feature.spectral_flatness(S=power_spec).mean()

        # MFCCs (mean across time)
        mfccs = librosa.feature.mfcc(S=librosa.power_to_db(power_spec), sr=self.sr, n_mfcc=13)
        self.general_features['mfccs'] = mfccs.mean(axis=1).tolist()
 
    def extract_vocal_features(self):
        """
        Extract vocal-specific features from the vocals spectrogram.
        """
        # Pitch (Using librosa's piptrack for pitch estimation)
        pitches, magnitudes = librosa.piptrack(S=np.abs(self.vocals_sg), sr=self.sr)
        self.vocals_features['pitch'] = pitches[pitches > 0].mean() if pitches.any() else 0
        
        # Harmonic-to-Noise Ratio (HNR)
        hnr = librosa.feature.rms(S=np.abs(self.vocals_sg)) / np.std(self.vocals_sg, axis=0)
        self.vocals_features['harmonic_to_noise_ratio'] = hnr.mean()
        
        # Formants (Approximation: Use peaks in the spectrum)
        spectral_peaks = np.argmax(np.abs(self.vocals_sg), axis=0)
        self.vocals_features['formants'] = spectral_peaks[:5].tolist()  # First 5 peaks as formants

    def extract_instrument_features(self):
        """
        Extract instrument-specific features from the music spectrogram.
        """
        # Chroma Features
        chroma = librosa.feature.chroma_stft(S=np.abs(self.music_sg), sr=self.sr)
        self.music_features['chroma_features'] = chroma.mean(axis=1).tolist()

        # Spectral Peaks
        spectral_peaks = np.argmax(np.abs(self.music_sg), axis=0)
        self.music_features['spectral_peaks'] = spectral_peaks.tolist()

        # Rhythm (Estimate tempo)
        onset_env = librosa.onset.onset_strength(S=np.abs(self.music_sg), sr=self.sr)
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=self.sr)
        self.music_features['tempo'] = tempo


# Example usage
# Load audio
y, sr = librosa.load('song_file.wav', duration=30)
spectrogram = librosa.stft(y)

# Feature extraction
extractor = Song_FingerPrint(spectrogram, sr)
song_features = extractor.extract_song_features()

print(song_features)
