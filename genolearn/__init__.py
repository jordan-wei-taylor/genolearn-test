__version__ = '0.1.2'

import os

ls = os.listdir()
wd = True if '.genolearn' in ls else False

path = os.path.join(os.path.dirname(__file__), 'wd')
if wd:
    working_directory = os.path.abspath('.')
    with open(path, 'w') as f:
        f.write(working_directory)
elif os.path.exists(path):
    with open(path) as f:
        working_directory = f.read()
        if not (os.path.exists(working_directory) and '.genolearn' in os.listdir(working_directory)):
            working_directory = None
else:
    working_directory = None


ls = os.listdir(working_directory if working_directory and os.path.exists(working_directory) else '.')

class Path():

    def add(self, func):
        name = func.__name__
        if name.startswith('_'):
            name = name[1:]
        self.__dict__[name] = func

path = Path()

def add(func):
    path.add(func)
    return lambda *args, **kwargs : func(*args, **kwargs)
    
@add
def join(*args):
    return os.path.join(working_directory, *args)

@add
def join_from(path):
    return lambda *args : os.path.join(path, *args)

@add
def listdir(path = '.', *args):
    if working_directory and os.path.exists(working_directory):
        path = join(path, *args)
        return os.listdir(path) if os.path.exists(path) else []
    return []

@add
def expanduser(path, inverse = False):
    return path.replace('~', os.path.expanduser('~')) if inverse else path.replace(os.path.expanduser('~'), '~')   

@add
def _open(path, mode = 'r'):
    return open(join(path), mode)

@add
def exists(path):
    return os.path.exists(os.path.expanduser(path))

def get_active():
    try:
        if working_directory:
            path = join('.genolearn')
            if os.path.exists(path):
                import json
                with open(path) as f:
                    return json.load(f)
    except:
        ...
