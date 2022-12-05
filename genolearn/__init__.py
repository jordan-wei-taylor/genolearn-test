"""
genolearn doc

"""

import os

__version__ = '0.0.8dev'

path        = __file__.replace('__init__.py', '')
if 'wd' in os.listdir(path):
    with open(os.path.join(path, 'wd')) as f:
        wd = f.read()
else:
    wd = None

def get_active():
    if wd:
        import json
        path = os.path.join(wd, '.config')
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)