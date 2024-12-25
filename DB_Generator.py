import os
import librosa
import numpy as np
from spectrogram_generator import generate_spectrogram_using_librosa
from Song_FingerPrint import Song_FingerPrint

SR = 100

finger_prints = []

songs_spectrograms = generate_spectrogram_using_librosa('Task 5 Data/original data/songs', True)
vocals_spectrograms = generate_spectrogram_using_librosa('Task 5 Data/original data/vocals')
music_spectrograms = generate_spectrogram_using_librosa('Task 5 Data/original data/music')

for i in range(songs_spectrograms):
    song_name = songs_spectrograms[i]["song_name"]
    ssg = songs_spectrograms[i]["spectrogram"]
    vsg = vocals_spectrograms[i]
    msg = music_spectrograms[i]
    
    song_fingerprint = Song_FingerPrint(ssg, vsg, msg, SR, song_name)
    finger_prints.append(song_fingerprint)