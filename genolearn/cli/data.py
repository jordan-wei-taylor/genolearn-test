from   genolearn.core.config import get_active

import click
import os


@click.group()
def data():
    """
    data analysis and assignment of train-test split.
    """
    ...

@data.command()
def analyse():
    """
    analyses the meta data.

    Example
    =======

    \b
    # summary global statistics
    >>> genolearn data analyse
    
    \b
    # summary statistics by group (group should be a column in meta data)
    >>> genolearn data analyse --group-by <group_by>

    \b
    # additional suggestion for which target values should be taken forward for modelling
    >>> genolearn data analyse --group-by <group_by> --test <test>
    """
    from   genolearn.utils import prompt

    active = get_active()
    metas = os.listdir(os.path.join(active['preprocess_dir'], 'meta'))
    info  = dict(meta       = dict(type = click.Choice(metas)),
                 min_count  = dict(type = click.IntRange(0), default = 10),
                 proportion = dict(type = click.BOOL, default = False))

    params = prompt(info)
    params['meta'] = os.path.join(active['preprocess_dir'], 'meta', params['meta'])
    from   genolearn.core.data import analyse
    
    if os.path.exists(params['meta']):
        analyse(**params)
    else:
        print('execute genolearn preprocess first')

@data.command()
@click.option('--num', default = 10)
def head(num):
    """
    prints the first NUM rows of meta data.
    """
    from genolearn.core.data import head
    active = get_active()
    metas  = os.listdir(os.path.join(active['preprocess_dir'], 'meta'))
    if len(metas) == 1:
        meta = metas[0]
    else:
        meta = click.prompt('meta', type = click.Choice(metas))
    meta   = os.path.join(active['preprocess_dir'], 'meta', meta)
    head(meta, num)

@data.command()
@click.option('--num', default = 10)
def tail(num):
    """
    prints the last NUM rows of meta data.
    """
    from genolearn.core.data import tail
    active = get_active()
    metas  = os.listdir(os.path.join(active['preprocess_dir'], 'meta'))
    if len(metas) == 1:
        meta = metas[0]
    else:
        meta = click.prompt('meta', type = click.Choice(metas))
    meta   = os.path.join(active['preprocess_dir'], 'meta', meta)
    tail(meta, num)

@data.command()
@click.option('--num', default = 10)
def sample(num):
    """
    prints the last NUM rows of meta data.
    """
    from genolearn.core.data import sample
    active = get_active()
    metas  = os.listdir(os.path.join(active['preprocess_dir'], 'meta'))
    if len(metas) == 1:
        meta = metas[0]
    else:
        meta = click.prompt('meta', type = click.Choice(metas))
    meta   = os.path.join(active['preprocess_dir'], 'meta', meta)
    sample(meta, num)

@data.command()
def train_test_split():
    """
    randomly assigns each row in meta data to be train or test.
    """
    
    from genolearn.utils import prompt
    import json

    info = dict(output = dict(prompt = 'output', type = click.STRING, default = 'default.meta'),
                ptrain = dict(prompt = 'ptrain', type = click.FloatRange(0., 1.), default = 0.75),
                random_state = dict(prompt = 'random-state', type = click.INT, default = None))

    params = prompt(info)
    
    from genolearn.core import train_test_split
    active = get_active()

    with open(os.path.join(active['preprocess_dir'], 'default.meta')) as f:
        params['meta'] = json.load(f)

    params['output'] = os.path.join(active['preprocess_dir'], params['output'])

    train_test_split(**params)