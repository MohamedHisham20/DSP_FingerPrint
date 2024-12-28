import json

def delete_data_in_json(file_path: str):
    # Overwrite the file with an empty list
    with open(file_path, 'w') as file:
        json.dump([], file)
        
def write_in_json_file(file_path:str, data, indent=4):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=indent)
        
delete_data_in_json('db.json')        
            