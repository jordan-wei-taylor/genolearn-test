from   genolearn.logger import print_dict
from   genolearn.core.config import get_active
from   genolearn.utils import prompt

import resource
import click
import os

@click.command()
def preprocess():
    """
    preprocess a gunzip (gz) compressed text file.
    
    The text file should containing genome sequence data of the following sparse format

    \b
    sequence_1 | identifier_{1,1}:count_{1,1} identifier_{1,1}:count_{2,1} ...
    sequence_2 | identifier_{2,1}:count_{2,1} identifier_{2,1}:count_{2,2} ...
    ...

    into a directory of .npz files, a list of all the features, and some meta information containing number of 
    identifiers, sequences, and non-zero counts.

    It is expected that the parameter ``data`` is in the ``data-dir`` directory set in the \033[1mactive config\033[0m file.
    See https://genolearn.readthedocs.io/usage/config for more details.

    .. code-block:: bash 

        \b
        Prompted information
        data        : input genome sequence file (gunzipped)
        batch-size  : number of concurrent observations to preprocess at the same time
        n-processes : number of parallel processes
        sparse      : sparse output
        dense       : dense output
        verbose     : integer denoting number of features between each verbose update
        n-features  : number of features to preprocess (set to -1 to preprocess all)
    """
    active = get_active()
    choice = click.Choice([file for file in os.listdir(active['data-dir']) if file.endswith('.gz')])

    info   = dict(data = dict(prompt = 'data (gz) file', type = choice),
                  batch_size = dict(prompt = 'batch-size', type = click.INT, default = None),
                  n_processes = dict(prompt = 'n-processes', type = click.INT, default = None),
                  sparse = dict(prompt = 'sparse', type = click.BOOL, default = True),
                  dense = dict(prompt = 'dense', type = click.BOOL, default = True),
                  verbose = dict(prompt = 'verbose', type = click.INT, default = 250000),
                  debug = dict(prompt = 'n-features', type = click.INT, default = -1))
    params = prompt(info)

    assert params['dense'] or params['sparse'], 'set either / both dense and sparse to True'

    params['data'] = os.path.join(active['data-dir'], params['data'])

    from pathos.multiprocessing import cpu_count

    if params['batch_size'] == None:
        params['batch_size'] = min(resource.getrlimit(resource.RLIMIT_NOFILE)[1], 2 ** 14) # safety
    if params['n_processes'] == None:
        params['n_processes'] = cpu_count()

    print_dict('executing "preprocess" with parameters:', params)

    from   genolearn.core import core_preprocess

    core_preprocess(active['preprocess-dir'], **params)
