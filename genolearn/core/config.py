"""
Some Test
"""

import json
import os
import re

HOME = os.path.expanduser('~')

root = f'{HOME}/.genolearn'
config_path = f'{root}/configs'

os.makedirs(config_path, exist_ok = True)

def get_active(**kwargs):
    if 'active' not in os.listdir(root):
        return 
    with open(f'{root}/active') as f:
        active = f.read()
    with open(f'{config_path}/{active}') as f:
        kwargs.update(json.loads(f.read()))
        return kwargs

def create(name, preprocess_dir, data_dir, meta):
    config = json.dumps(dict(data_dir = data_dir, preprocess_dir = preprocess_dir, meta = meta), indent = 4)
    with open(f'{config_path}/{name}', 'w') as file:
        print(config, file = file, end = '')
    print(f'"{name}" config created in {config_path}:\n{config}')

def get(file):
    if file in os.listdir():
        with open(file) as f:
            print(f.read())
    elif file in os.listdir(config_path):
        with open(f'{config_path}/{file}') as f:
            print(f.read())
    else:
        print(f'"{file}" not found!')

def list_(flag):
    files = os.listdir(config_path)
    if flag:
        for file in files[:-1]:
            print(f'{file}:')
            get(file)
            print('')
        print(f'{files[-1]}:')
        get(files[-1])
    else:
        if files:
            print('\n'.join(files))
        else:
            print('no config files found')


def activate(name):
    configs = os.listdir(config_path)
    if name in configs:
        with open(f'{root}/active', 'w') as file:
            print(name, file = file, end = '')
        print(f'"{name}" config activated')
    else:
        print(f'"{name}" not found!\n\nconfigs:' + '\n  - '.join([''] + configs))

def active():
    if 'active' not in os.listdir(root):
        return print('No active config! (Use genolearn config activate <name>)')
    with open(f'{root}/active') as f:
        active = f.read()
        print(f'{active}:')
    get(active)

def remove(name):
    if name in os.listdir(config_path):
        os.remove(f'{config_path}/{name}')
        print(f'removed "{name}" config')
    else:
        print('"{name}" not found!')


def model(name, string):

    # convert to dictionary like string
    string = '{' + re.sub(r'=| = | =|= ', ':', string) + '}'
    string = re.sub(' ', ', ', string)

    # convert key to "key"
    match  = re.search(r'[a-zA-Z0-9\_]+(?=:)', string)
    while match:
        start  = match.start()
        end    = match.end()
        string = '"'.join([string[:start], string[start:end], string[end:]])
        match  = re.search(r'[a-zA-Z0-9\_]+(?=:)', string)

    # explicitly expand range(a, b, c) to [a, a + c,...B] where B = a + nc and B < b
    while 'range' in string:
        nums   = re.findall('(?<=range\()[0-9, ]+', string)[0].replace(',', ' ').split()
        string = re.sub('range\([0-9, ]+\)', str(list(range(*map(int, nums)))), string, 1)

    # convert string like dictionary to python dictionary
    config = json.loads(string)

    path   = os.path.join(get_active()['preprocess_dir'], 'model')
    os.makedirs(path, exist_ok = True)

    # write to file
    with open(os.path.join(path, name), 'w') as file:
        print(json.dumps(config, indent = 4), file = file)