
import os
import yaml
import json
import pickle


def load(file, mode='r', encoding=None, load_func=None):
    if not os.path.isfile(file): return None
    with open(file, mode, encoding=encoding) as f:
        if load_func is not None: return load_func(f)
        else: return f.read()



def save(file, data, mode='w', encoding=None ,save_func=None):
    # create directory
    file_dir = os.path.dirname(file)
    os.makedirs(file_dir, exist_ok=True)

    # remove old file
    if os.path.isfile(file): os.remove(file)

    # flush
    with open(file, mode, encoding=encoding) as f:
        if save_func is not None: return save_func(f, data)
        else: return f.write(data)



def isfile(file): return os.path.isfile(file)


def mkdirs4file(file):
    dir = os.path.dirname(file)
    os.makedirs(dir, exist_ok=True)


def load_yaml(file, encoding='utf-8'): return load(file, encoding=encoding, load_func=lambda f: yaml.load(f, Loader=yaml.FullLoader))

def save_yaml(file, data, encoding='utf-8'): return save(file, data, encoding=encoding, save_func=lambda f, d: yaml.dump(d, f, allow_unicode=True))

def load_json(file, encoding='utf-8'): return load(file, encoding=encoding, load_func=lambda f: json.load(f))

def save_json(file, data, encoding='utf-8'): return save(file, data, save_func=lambda f, d: json.dump(d, f, ensure_ascii=False, encoding=encoding))

def load_pickle(file, encoding='utf-8'): return load(file, mode='rb', load_func=lambda f: pickle.load(f, encoding=encoding))

def save_pickle(file, data): return save(file, data, mode='wb', save_func=lambda f, d: pickle.dump(d, f))
