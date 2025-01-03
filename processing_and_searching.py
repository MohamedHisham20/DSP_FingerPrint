from typing import List, Dict, Any, Union, Tuple, Set
import hashlib
import numpy as np
from scipy.spatial.distance import cosine, euclidean, cityblock, jensenshannon, hamming
import os
import librosa
from scipy.stats import pearsonr
import soundfile as sf
from scipy.interpolate import interp1d

def peak_normalize(data:np.ndarray):
    max_val = np.max(data)
    data = data / max_val
    return data

def min_max_normalize(data:np.ndarray):
    min_val = np.min(data)
    max_val = np.max(data)
    
    data = (data - min_val) / (max_val - min_val)
    return data

def trim_and_perform_monoticity(audio_data: np.ndarray, sample_rate):
    if len(audio_data.shape) > 1: audio_data = np.mean(audio_data, axis=1)
    audio_data = audio_data[:sample_rate * 18]
    
    return audio_data

def extract_audio_signal(file_path:str, sr = 48000):
    """
    return the normalized audio signal with its native sampling rate.\n
    Peak Normalization is applied if required.
    """
    file_path = os.path.normpath(file_path)
    audio_data, sample_rate = librosa.load(file_path, sr=sr)
    
    audio_data = trim_and_perform_monoticity(audio_data, sample_rate)
    
    audio_data = peak_normalize(audio_data)
    
    return audio_data, sample_rate

def mix_audio(path1:str, path2:str, w1:float, w2:float):
    """
    Return the normalizaed mixed signal, the common sampling rate, name and path\n
    w is the weight assigned to audio1. audio2 will have 1-w.\n
    0 < w < 1
    """
    path1 = os.path.normpath(path1)
    path2 = os.path.normpath(path2)
    
    audio1, sr = extract_audio_signal(path1)
    audio2, sr = extract_audio_signal(path2)
            
    
    audio1 = trim_and_perform_monoticity(audio1, sr)
    audio2 = trim_and_perform_monoticity(audio2, sr)       
    
    mix_audio = (w1*audio1) + (w2*audio2)
    
    mix_audio = peak_normalize(mix_audio)
    
    name, path =  save_mix(path1, path2, mix_audio, sr, w1, w2)
    
    return mix_audio, sr, name, path 
 
def save_mix(path1, path2, mix_audio, sr, w1, w2):
    """
    save mix audio in a .wav file.\n
    return mix_name and mix_file_path
    """
    name1 = os.path.basename(path1)
    name1, ext = os.path.splitext(name1)
        
    name2 = os.path.basename(path2)
    name2, ext = os.path.splitext(name2)
        
    audio_name = name1+'weight_'+str(w1)+' and '+name2 + 'weight_' + str(w2)+' mix'
    save_path = os.path.join('saved_mix/'+audio_name+'.wav') 
            
    sf.write(save_path, mix_audio, sr) 
            
    return audio_name, save_path 
    
def generate_spectrogram(audio_data:np.ndarray):
    """
    return normalized spectrogram in decibel scale.\n
    min-max normalization is applied if required.
    """
    sg = np.abs(librosa.stft(audio_data))
    sg = librosa.amplitude_to_db(sg, ref=1)
    sg = min_max_normalize(sg)
        
    return sg

def __generate_spectrograms(input_folder_path):
    sampling_rates = []
    audios = []
    paths = []
    names = []
    
    spectrograms:List[Dict] = []
    files = os.listdir(input_folder_path)
    
    for file in files:
        if file.endswith('.wav'):
            file_path = os.path.join(input_folder_path, file)
            file_path = os.path.normpath(file_path)
            audio_name, ext = os.path.splitext(file)
            audio_data, sample_rate = extract_audio_signal(file_path)
            
            audios.append(audio_data)
            sampling_rates.append(sample_rate)
            names.append(audio_name)
            paths.append(file_path)
            
    audios, max_sr = resample_audios_with_max_sr(audios, sampling_rates)
    
    for audio, path, name in zip(audios, paths, names):
        S_db = generate_spectrogram(audio)
        spectrograms.append({'file_path':path, 'audio_name': name, 'SG': S_db, 'SR':max_sr})
    
    return spectrograms        


def resample_audios_with_max_sr(audios, og_sampling_rates):
    max_sr = max(og_sampling_rates)
    new_audios = []
    
    for audio, og_sr in zip(audios, og_sampling_rates):
        audio = librosa.resample(y=audio, orig_sr=og_sr, target_sr=max_sr)
        new_audios.append(audio)
        
    return new_audios, max_sr    

def generate_dataset_spectrograms(paths:List):
    """
    return a list where each entry is a list of dictionaries.\n
    Each dict contains a wav file paramters as name, path, sampling_rate and spectrogram
    """
    full_songs_spectrograms = __generate_spectrograms(paths[0])
    vocals_spectrograms = __generate_spectrograms(paths[1])
    music_spectrograms = __generate_spectrograms(paths[2])

    return [full_songs_spectrograms, vocals_spectrograms, music_spectrograms]


def flatten_and_normalize(features: Dict):
    flattened_features = []
    
    for key, val in sorted(features.items()):
        if isinstance(val, float) or isinstance(val, int):
            flattened_features.append(val)
        elif isinstance(val, list):
            if isinstance(val[0], list):
                for item in val:
                    flattened_features.extend(item)
            else: flattened_features.extend(val)
            
    flattened_features = np.array(flattened_features)
    
    if np.linalg.norm(flattened_features) > 0:
        flattened_features = flattened_features / np.linalg.norm(flattened_features)
        
    return flattened_features.tolist()                

def p_hash(features: Dict) -> str:
    
    features = flatten_and_normalize(features)
    features = str(features).encode()
    features = hashlib.sha256(features)
    features = features.hexdigest()
        
    return features

def perceptual_hash(features: Dict[str, Any]) -> str:
    """
    Generate a perceptual hash for a dictionary of features.
    """
    flattened_features = []
    for key, value in features.items():
        if isinstance(value, np.ndarray):
            flattened_features.extend(value.flatten())
    flattened_features = np.array(flattened_features)

    if np.linalg.norm(flattened_features) > 0:
        flattened_features = flattened_features / np.linalg.norm(flattened_features)

    hash_object = hashlib.sha256(flattened_features.tobytes())
    return hash_object.hexdigest()

def generate_hashed_database(database: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate a hashed database of perceptual hashes for each song in the database.
    """
    hashed_database = []
    for song in database:
        song_name = song["song_name"]
        features = song["features"]
        song_hash = [perceptual_hash(feature) for feature in features]
        hashed_database.append({
            "song_name": song_name,
            "song_features_hash": song_hash
        })
    return hashed_database

def search_hashed_database(query_features: Dict[str, Any], hashed_database: List[Dict[str, Any]], distance_metric: str = 'cosine', top_n: int = 1) -> List[Dict[str, Any]]:
    """
    Search the hashed database for the most similar song to the query features.
    """
    query_hash = perceptual_hash(query_features)
    distances = []

    for song in hashed_database:
        db_hashes = song["song_features_hash"]
        song_distance = min(calculate_hash_distance(query_hash, db_hash, distance_metric) for db_hash in db_hashes)
        distances.append((song_distance, song))

    distances.sort(key=lambda x: x[0])
    return [song for _, song in distances[:top_n]]

def calculate_hash_distance(hash1: str, hash2: str, distance_metric: str = 'h') -> float:
    """ 
    Calculate the distance between two hashes based on the selected distance metric.\n
    distance_metric: cos --> cosine \n
    e -- > euclidean\n
    c --> cityblock\n
    j --> jensenshannon\n
    h --> hamming
    """
    hash1_array = np.frombuffer(bytes.fromhex(hash1), dtype=np.uint8)
    hash2_array = np.frombuffer(bytes.fromhex(hash2), dtype=np.uint8)

    # if np.linalg.norm(hash1_array) > 0:
    #     hash1_array = hash1_array / np.linalg.norm(hash1_array)
    # if np.linalg.norm(hash2_array) > 0:
    #     hash2_array = hash2_array / np.linalg.norm(hash2_array)

    if distance_metric == 'cos':
        return cosine(hash1_array, hash2_array)
    elif distance_metric == 'e':
        return euclidean(hash1_array, hash2_array)
    elif distance_metric == 'c':
        return cityblock(hash1_array, hash2_array)
    elif distance_metric == 'j':
        return jensenshannon(hash1_array, hash2_array)
    elif distance_metric == 'h':
        return hamming(hash1_array, hash2_array)
    else:
        raise ValueError(
            "Invalid distance metric. Supported metrics: 'cosine', 'euclidean', 'cityblock', 'jensenshannon'.")

def calc_shared_spectral_peaks_ratio(peaks1: Set, peaks2: Set):
    """
    return a similarity ratio incorporating how similar are the spectral peaks
    """
    shared_peaks = peaks1.intersection(peaks2)
    unique_peaks = peaks1.union(peaks2)
    
    similarity_ratio = len(shared_peaks) / len(unique_peaks)
    return similarity_ratio

def __sinc_interpolate(x_vals, y_vals, new_x_vals):
    if len(x_vals) != len(y_vals):
        raise ValueError("x_vals are not equal to y_vals")
    
    sinc_matrix = np.tile(new_x_vals, (len(x_vals), 1))
    sinc_matrix = np.sinc(sinc_matrix)
    
    interpolated = np.dot(y_vals, sinc_matrix)
    return interpolated.tolist()
    

def calc_energy_envelope_correlation(e1: List, e2: List, interpolation='sinc'):
    """
    return a metric that indicates how similar the energy distribution is
    """ 
    if len(e1) < len(e2):
        old = np.linspace(0, 1, len(e1))
        new = np.linspace(0, 1, len(e2))
        if interpolation=='sinc': e1 = __sinc_interpolate(old, e1, new)
        else:
            f = interp1d(old, e1, interpolation)
            e1 = f(new)
    
    elif len(e2) < len(e1):
        old = np.linspace(0, 1, len(e2))
        new = np.linspace(0, 1, len(e1))
        if interpolation=='sinc': e2 = __sinc_interpolate(old, e2, new)
        else:
            f = interp1d(old, e2, interpolation)
            e2 = f(new)
                     
    correlation, _ = pearsonr(e1, e2)
    return correlation


def main():
    a, sr = extract_audio_signal('Data/original_data/songs/FE!N.wav')

