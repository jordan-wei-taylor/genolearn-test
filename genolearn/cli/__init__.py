"""
genolearn cli
"""

from   genolearn import wd

from   genolearn.cli.data               import data
from   genolearn.cli.evaluate           import evaluate
from   genolearn.cli.feature_importance import feature_importance
from   genolearn.cli.feature_selection  import feature_selection
from   genolearn.cli.preprocess         import preprocess
from   genolearn.cli.train              import train
from   genolearn.cli.model              import model
from   genolearn.cli.dir                import dir

# from   genolearn.cli._print              import _print

from   genolearn import get_active
import os
import json


from   genolearn import __version__

from   shutil import get_terminal_size
import click

click.formatting.FORCED_WIDTH = min(get_terminal_size().columns - 10, 110)

@click.group()
@click.version_option(__version__, message = 'GenoLearn %(version)s')
def cli():
    """ 
    GenoLearn Command Line Interface

    \b\n

    GenoLearn is designed to enable researchers to perform Machine Learning on their genome sequence data such 
    as fsm-lite or unitig files.
    
    See https://genolearn.readthedocs.io for the most up-to-date documentation.
    """
    ...

cli.add_command(model)
cli.add_command(data)
cli.add_command(evaluate)
cli.add_command(feature_importance)
cli.add_command(feature_selection)
cli.add_command(preprocess)
cli.add_command(train)
cli.add_command(dir)

@cli.command(name = 'next')
def _next():
    """
    provides a hint at the next command the user should execute.
    """
    active = get_active()
    if active is None or not os.path.exists(os.path.join(wd, '.config')):
        return print('genolearn dir set')
    with open(os.path.join(wd, '.history')) as f:
        history = f.readlines()
    for command in ['preprocess sequence', 'preprocess meta', 'feature-selection', 'model', 'train', 'feature-importance']:
        flag = True
        for line in history:
            if line.startswith(command):
                flag = False
                break
        if flag:
            return print(f'genolearn {command}')

def _reduce(d, limit):
    if isinstance(d, dict):
        if len(d) > limit:
            for i, (k, v) in enumerate(d.copy().items(), 1):
                if i < limit:
                    d[k] = _reduce(v, limit)
                else:
                    del d[k]
                    d['...'] = '...'
        else:
            for k, v in d.items():
                d[k] = _reduce(v, limit)
    elif isinstance(d, list):
        if len(d) > limit:
            d = d[:limit - 1] + ['...']
    return d

def reduce(d, limit):
    for k, v in d.items():
        d[k] = _reduce(v, limit)
    return d

@cli.command(name = 'print')
@click.argument('name', default = 'None', type = click.STRING)
@click.argument('limit', default = 5, type = click.IntRange(1))
def _print(name, limit):
    """
    prints various files GenoLearn relies on.
    """
    active    = get_active()
    if active is None:
        return print('execute "genolearn config create" first')
    metas     = os.path.join(wd, 'meta')
    models    = os.path.join(wd, 'model')
    locations = [metas, models]
    if name == 'None':
        for i, location in enumerate(locations):
            loc = location.replace(wd, '<working_dir>').replace(os.path.expanduser('~'), '~')
            if os.path.exists(location):
                print(f'{loc}\n  - ' + '\n  - '.join(os.listdir(location)))
            else:
                command = 'config model' if i else 'preprocess meta'
                print(f'{loc} (does not exist - execute "genolearn {command}" first)')
            if i < 1:
                print()
    elif name == 'history':
        with open(os.path.join(wd, '.history')) as f:
            print(f.read(), end = '')
    else:
        flag      = True
        for i, location in enumerate(locations):
            if os.path.exists(location):
                if name in os.listdir(location):
                    file = os.path.join(location, name)
                    with open(file) as f:
                        config = reduce(json.load(f), limit)
                        print(file.replace(os.path.expanduser('~'), '~'))
                        print(json.dumps(config, indent = 4).replace('"', '').replace('...: ...', '...'))
                        flag = False
                        break
            else:
                command = 'config model' if i else 'preprocess meta'
                print(f'{location} (does not exist - execute "genolearn {command}")\n')
        if flag:
            print(f'could not find "{name}" in' + '\n  - '.join([''] + locations))


