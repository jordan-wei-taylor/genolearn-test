from   genolearn.logger import print_dict
from   genolearn.core.config import get_active
from   genolearn.utils import prompt

import resource
import click
import os


@click.group()
def preprocess():
    """
    preprocess your data into a more efficient format.
    """
    ...

@preprocess.command()
@click.option('--max-features', default = None, type = click.IntRange(-1))
def sequence(max_features):
    """
    preprocess a gunzip (gz) compressed text file.
    
    The text file should containing genome sequence data of the following sparse format

    \b
    sequence_1 | identifier_{1,1}:count_{1,1} identifier_{1,1}:count_{2,1} ...
    sequence_2 | identifier_{2,1}:count_{2,1} identifier_{2,1}:count_{2,2} ...
    ...

    into a directory of .npz files, a list of all the features, and some meta information containing number of 
    identifiers, sequences, and non-zero counts.

    It is expected that the parameter ``data`` is in the ``data_dir`` directory set in the \033[1mactive config\033[0m file.
    See https://genolearn.readthedocs.io/usage/config for more details.

    \b
    Prompted information
        data        : input genome sequence file (gunzipped)
        batch-size  : number of concurrent observations to preprocess at the same time
        n-processes : number of parallel processes
        sparse      : sparse output
        dense       : dense output
        verbose     : integer denoting number of features between each verbose update
    """
    active = get_active()
    choice = click.Choice([file for file in os.listdir(active['data_dir']) if file.endswith('.gz')])

    info   = dict(data = dict(prompt = 'data (gz) file', type = choice),
                  batch_size = dict(prompt = 'batch-size', type = click.INT, default = None),
                  n_processes = dict(prompt = 'n-processes', type = click.INT, default = None),
                  sparse = dict(prompt = 'sparse', type = click.BOOL, default = True),
                  dense = dict(prompt = 'dense', type = click.BOOL, default = True),
                  verbose = dict(prompt = 'verbose', type = click.INT, default = 250000))
    params = prompt(info)

    assert params['dense'] or params['sparse'], 'set either / both dense and sparse to True'

    params['data']         = os.path.join(active['data_dir'], params['data'])
    params['max_features'] = -1 if max_features is None else max_features

    from multiprocessing import cpu_count

    if params['batch_size'] == None:
        params['batch_size'] = min(resource.getrlimit(resource.RLIMIT_NOFILE)[1], 2 ** 14) # safety
    if params['n_processes'] == None:
        params['n_processes'] = cpu_count()

    print_dict('executing "preprocess" with parameters:', params)

    from   genolearn.core.preprocess import preprocess

    preprocess(active['preprocess_dir'], **params)

@preprocess.command()
@click.option('--max-features', default = None, type = click.IntRange(-1))
def combine(max_features):
    """
    combines the preprocess of a gunzip (gz) compressed text file to an existing preprocessed directory.
    
    The text file should containing genome sequence data of the following sparse format

        \b
        sequence_1 | identifier_{1,1}:count_{1,1} identifier_{1,1}:count_{2,1} ...
        sequence_2 | identifier_{2,1}:count_{2,1} identifier_{2,1}:count_{2,2} ...
        ...

    and combines the preprocessed data with the `preprocess_dir` directory set in the \033[1mactive config\033[0m file.
    This relies on the user to have previously executed `genolearn preprocess`.

    See https://genolearn.readthedocs.io/tutorial/combine for more details.

    \b
    Prompted information
        data        : input genome sequence file (gunzipped)
        batch-size  : number of concurrent observations to preprocess at the same time
        n-processes : number of parallel processes
        verbose     : integer denoting number of features between each verbose update

    """
    active = get_active()
    choice = click.Choice([file for file in os.listdir(active['data_dir']) if file.endswith('.gz')])
    info = dict(data        = dict(prompt = 'data (gz) file', type = choice),
                batch_size  = dict(type = click.INT, default = None),
                n_processes = dict(type = click.INT, default = None),
                verbose     = dict(type = click.INT, default = 250000))
    params = prompt(info)
    
    params['data'] = os.path.join(active['data_dir'], params['data'])
    params['max_features'] = -1 if max_features is None else max_features

    from multiprocessing import cpu_count

    if params['batch_size'] == None:
        params['batch_size'] = min(resource.getrlimit(resource.RLIMIT_NOFILE)[1], 2 ** 14) # safety
    if params['n_processes'] == None:
        params['n_processes'] = cpu_count()

    from   genolearn.logger      import print_dict

    print_dict('executing "combine" with parameters:', params)

    from   genolearn.core.preprocess import combine

    combine(active['preprocess_dir'], **params)

@preprocess.command()
def meta():
    """
    preprocesses the metadata and defines the train / test split for the later ``genolearn train`` execution.

    \b
    prompted information
        output             : filename of preprocessed metadata
        identifier         : identifier column in input metadata
        target             : target column in input metadata
        group              : group column in input metadata
        train_group_values : group values to assign as training data [if group  = None]
        test_group_values  : group values to assign as testing data  [if group  = None]
        proportion train   : proportion of data to assign as train   [if group != None]
    """
    from genolearn.core.config import get_active
    from genolearn.utils       import _prompt

    import pandas as pd

    active         = get_active()
    meta_path      = os.path.join(active['data_dir'], active['meta'])
    meta_df        = pd.read_csv(meta_path).applymap(str)
    valid_columns  = set(meta_df.columns)
    
    output         = click.prompt('output       ', type = click.STRING, default = 'default')
    identifier     = click.prompt('identifier             ', type = click.Choice(valid_columns), show_choices = False)

    valid_columns -= set([identifier])

    target         = click.prompt('target                 ', type = click.Choice(valid_columns), show_choices = False)

    valid_columns -= set([target])
    valid_columns |= set(['None'])

    group          = click.prompt('group           ', type = click.Choice(valid_columns), show_choices = False, default = 'None')

    if group != 'None':
        groups       = set(meta_df[group])
        train_values = _prompt('train group values     ', type = click.Choice(groups), default = None, default_option = False, multiple = True)
        groups      -= set(train_values)
        test_values  = _prompt('test  group values     ', type = click.Choice(groups), default = None, default_option = False, multiple = True)
        ptrain       = None
    else:
        train_values = ['Train']
        test_values  = ['Test']
        ptrain       = click.prompt('proportion train', type = click.FloatRange(0., 1.), default = 0.75)

    from genolearn.core.preprocess import preprocess_meta

    preprocess_meta(output, meta_path, identifier, target, group, train_values, test_values, ptrain)

