import json

raw_data_path = 'db.json'
hashed_db_path = 'hashed_db.json'
matches_json = 'matches.json'
input_hash_json = 'input_hash.json'

def clear_json_file(file_path: str):
    # Overwrite the file with an empty list
    with open(file_path, 'w') as file:
        file.write('')
        
def write_in_json_file(file_path:str, data, indent=4):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=indent)
        
clear_json_file(matches_json)
clear_json_file(input_hash_json)