def normalize_database():
    normalize(total_spectral_centroids)
    normalize(total_mfccs, True, "mfccs")
    normalize(total_pitches, "pitch")
    normalize(total_HNRs)
    normalize(total_chroma_peaks, True, "chroma")

def create_normalized_database():
    database = create_database()
    normalize_database()
    
    #create normalized database
    for k in range(len(normalized_database)):
        
        normalized_database[k]["song_name"] = database[k]["song_name"]
        normalized_database[k]["features"] = [{} for _ in range(3)]
        features_list = normalized_database[k]["features"]
        
        for j in range(len(features_list)):
            dictionary = features_list[j]
            
            dictionary["spectral_centroid"] = total_spectral_centroids[k][j]
            dictionary["mfccs"] = total_mfccs[k][j]
            dictionary["pitch"] = total_pitches[k][j]
            dictionary["HNR"] = total_HNRs[k][j]
            dictionary["chroma"] = total_chroma_peaks[k][j]
                    
def normalize(feature_3d: List):
    for list in feature_3d:
        if complex: #list is a list of lists (Complex Feature like MFCCs)
           min_max_complex_normalize(list) 
        else:
            min_val = min(list)
            max_val = max(list)
            min_max_normalize(min_val, max_val, list)



def min_max_complex_normalize(list_of_lists: List[List[real_number]]):
    # if any(len(inner_list) == 0 for inner_list in list_of_lists):
    #     raise ValueError("One or more inner lists are empty")
    
    list_of_arrays = [np.array(inner_list) for inner_list in list_of_lists]
        
    try: matrix = np.stack(list_of_arrays)
    except ValueError as e: raise ValueError(f"Error stacking arrays: {e}")
    
    print(f"Matrix Shape: {matrix.shape}")  
    
    min_vals = matrix.min(axis=0)
    max_vals = matrix.max(axis=0)
    
    for i in range(matrix.shape[1]):
            if max_vals[i] != min_vals[i]:
                matrix[:, i] = (matrix[:, i] - min_vals[i]) / (max_vals[i] - min_vals[i])
            else:
                matrix[:, i] = 0
    # Update the original sublists with normalized values
    for j in range(len(list_of_lists)):
        list_of_lists[j][:] = matrix[j].tolist()

def min_max_normalize(min, max, list):
    """
x_norm = (x-x_min) / (x_max-x_min)    
    """
    for i in range(len(list)):
        list[i] = (list[i] - min) / (max-min)   
