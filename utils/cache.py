import json
import os

from models.motherboard_support import MotherboardSupport

def set_json_cache(key, value):
    if isinstance(value, list):
        value = [item.to_dict() if isinstance(item, MotherboardSupport) else item for item in value]
    elif isinstance(value, MotherboardSupport):
        value = value.to_dict()
    set_cache(key, json.dumps(value))

def get_json_cache(key):
    cache = get_cache(key)
    if cache is None:
        return None
    return json.loads(cache)

def set_cache(key, value):
    path = make_path_from_key(key)
    make_dirs_with_key(key)
    with open(path, 'w') as file:
        file.write(value)

def get_cache(key):
    path = make_path_from_key(key)
    if os.path.exists(path):
        with open(path, 'r') as file:
            return file.read()
    return None

def delete_cache(key):
    path = make_path_from_key(key)
    try:
        os.remove(path)
    except Exception as e:
        print(e)

def make_path_from_key(key):
    sub_dir = generate_sub_dir_from_key(key)
    return f'./cache/{sub_dir}/{key}'



# make cache directory with key for cache directory structure
def make_dirs_with_key(key):
    sub_dir = generate_sub_dir_from_key(key)
    is_ok = create_dir()
    if not is_ok:
        return False
    is_ok = create_dirs_by_key(key)
    if not is_ok:
        return False
    
    return True

# create cache directory
def create_dir():
    try:
        if not os.path.exists('./cache'):
            os.makedirs('./cache')
    except Exception as e:
        print(e)
    
    if not os.path.exists('./cache'):
        return False
    return True

# create cache sub directory by key for cache directory structure
def create_dirs_by_key(key):
    sub_dir = generate_sub_dir_from_key(key)
    try:
        if not os.path.exists(f'./cache/{sub_dir}'):
            os.makedirs(f'./cache/{sub_dir}')
    except Exception as e:
        print(e)

    if not os.path.exists(f'./cache/{key}'):
        return False
    return True

# generate sub directory from key for cache directory structure example: key = '1234567890' -> '123'
def generate_sub_dir_from_key(key):
    return key[:3]