from   genolearn.core.config import get_active
from   genolearn.utils import prompt

import resource
import click
import os

active = get_active()

@click.command()
def combine():
    """
    combines the preprocess of a gunzip (gz) compressed text file to an existing preprocessed directory.
    
    The text file should containing genome sequence data of the following sparse format

        \b
        sequence_1 | identifier_{1,1}:count_{1,1} identifier_{1,1}:count_{2,1} ...
        sequence_2 | identifier_{2,1}:count_{2,1} identifier_{2,1}:count_{2,2} ...
        ...

    and combines the preprocessed data with the `preprocess-dir` directory set in the \033[1mactive config\033[0m file.
    This relies on the user to have previously executed `genolearn preprocess`.

    See https://genolearn.readthedocs.io/tutorial/combine for more details.
    """
    choice = click.Choice([file for file in os.listdir(active['data-dir']) if file.endswith('.gz')])
    info = dict(data        = dict(prompt = 'data (gz) file', type = choice),
                batch_size  = dict(prompt = 'batch size', type = click.INT, default = None),
                n_processes = dict(prompt = 'n-processes', type = click.INT, default = None),
                verbose     = dict(prompt = 'verbose', type = click.INT, default = 250000),
                debug       = dict(prompt = 'n-features', type = click.INT, default = -1))
    params = prompt(info)
    
    params['data'] = os.path.join(active['data-dir'], params['data'])

    from pathos.multiprocessing import cpu_count

    if params['batch_size'] == None:
        params['batch_size'] = min(resource.getrlimit(resource.RLIMIT_NOFILE)[1], 2 ** 14) # safety
    if params['n_processes'] == None:
        params['n_processes'] = cpu_count()

    from   genolearn.logger      import print_dict

    print_dict('executing "combine" with parameters:', params)

    from   genolearn.core import core_combine

    core_combine(active['preprocess-dir'], **params)
