"""
Some Test
"""

import json
import os


def create_config(working_dir, data_dir, meta):
    config = json.dumps(dict(data_dir = data_dir, meta = meta), indent = 4)
    with open(os.path.join(working_dir, '.config'), 'w') as file:
        print(config, file = file, end = '')
    print(f'".config" created in {working_dir}')