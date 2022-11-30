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
@click.option('--group-by', default = '', help = 'perform analysis by <group_by> column')
@click.option('--min-count', default = 10, help = 'minimum count for suggested target subset')
@click.option('--test', default = '', help = 'identifiers to omit when computing statistics')
def analyse(group_by, test, min_count):
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
    from genolearn.core import core_analyse
    try:
        test = list(map(int, test.split()))
    except:
        test = test.split()
    active = get_active()
    meta   = os.path.join(active['data-dir'], active['meta'])
    core_analyse(meta, active['target'], group_by, test, min_count)

@data.command()
@click.argument('num', default = 10)
def head(num):
    """
    prints the first NUM rows of meta data.
    """
    from genolearn.core import core_head
    active = get_active()
    meta   = os.path.join(active['data-dir'], active['meta'])
    core_head(meta, num)

@data.command()
@click.argument('num', default = 10)
def tail(num):
    """
    prints the last NUM rows of meta data.
    """
    from genolearn.core import core_tail
    active = get_active()
    meta   = os.path.join(active['data-dir'], active['meta'])
    core_tail(meta, num)

@data.command()
@click.option('--ptrain', default = 0.75, help = 'proportion of data to be assigned "train"')
@click.option('--random-state', default = None, help = 'random seed for reproducibility')
def train_test_split(ptrain, random_state):
    """
    randomly assigns each row in meta data to be train or test.
    """
    if random_state is not None:
        random_state = int(random_state)
    from genolearn.core import core_train_test_split
    active = get_active()
    meta   = os.path.join(active['data-dir'], active['meta']) if active else None
    core_train_test_split(meta, ptrain, random_state)