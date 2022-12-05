from   genolearn import wd
from   genolearn.utils import prompt

import click
import os

if wd and os.path.exists(os.path.join(wd, 'meta')):
    metas = click.Choice(os.listdir(os.path.join(wd, 'meta')))
else:
    metas = None

@click.group()
def data():
    """
    data viewing and analysis.
    """
    ...

@data.command()
def analyse():
    """
    analyses a preprocessed metadata file.

    prompted information
        meta       : metadata filename
        min_count  : minimum count to consider when suggesting which targets to take forward for modelling
        proportion : flag indicating to print proportions or countsW
    """
    from   genolearn.utils import prompt

    info  = dict(meta       = dict(type = metas),
                 min_count  = dict(type = click.IntRange(0), default = 10),
                 proportion = dict(type = click.BOOL, default = False))

    params = prompt(info)

    params['meta'] = os.path.join(wd, 'meta', params['meta'])
    
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
    info   = dict(meta = dict(type = metas))
    params = prompt(info)
    meta   = os.path.join(wd, 'meta', params['meta'])
    head(meta, num)

@data.command()
@click.option('--num', default = 10)
def tail(num):
    """
    prints the last NUM rows of meta data.
    """
    from genolearn.core.data import tail
    info   = dict(meta = dict(type = metas))
    params = prompt(info)
    meta   = os.path.join(wd, 'meta', params['meta'])
    tail(meta, num)

@data.command()
@click.option('--num', default = 10)
def sample(num):
    """
    prints the last NUM rows of meta data.
    """
    from genolearn.core.data import sample
    info   = dict(meta = dict(type = metas))
    params = prompt(info)
    meta   = os.path.join(wd, 'meta', params['meta'])
    sample(meta, num)