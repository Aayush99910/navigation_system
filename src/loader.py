import json 

def load_data(data_path):
    with open(data_path) as f:
        data = json.load(f)
    return data 