import click 

@click.command(name = 'feature-selection')
def feature_selection():
    """
    execute feature selection (fisher by default).

    \b
    prompted information
        name      : output file name
        group_by  : group-by column
        values    : group-by values which are referred to as `keys` in the training stage
        method    : feature selection method
        aggregate : experimental (leave as False)
        sparse    : loads the data in sparse format to reduce RAM usage if set to True
    """
    from   genolearn.core.config import get_active
    from   genolearn.core import core_feature_selection
    from   genolearn.utils import prompt

    import pandas as pd
    import os

    active = get_active()
    if active is not None:
        if not os.path.exists(active["preprocess-dir"]):
            return print('need to preprocess data')

    if active['group'] == 'train_test':
        default_values = 'train'
        type_values    = click.Choice(['train', 'test'])
    else:
        default_values = None
        type_values    = click.Choice(sorted(set(pd.read_csv(os.path.join(active['data-dir'], active['meta']))[active['group']].apply(str))))
    info = dict(name = dict(prompt = 'output filename', default = 'fisher-scores.npz', type = click.STRING),
                group_by = dict(prompt = 'group-by column', default = active['group'], type = click.STRING),
                values = dict(prompt = 'values', default = default_values, type = type_values),
                method = dict(prompt = 'method', default = 'fisher', type = click.STRING),
                aggregate = dict(prompt = 'aggregate', default = False, type = click.BOOL),
                sparse = dict(prompt = 'sparse data', default = False, type = click.BOOL))
    
    if info['values']['default'] is None:
        info['values'].pop('default')

    params = prompt(info)

    # ensure .npz ending
    if not params['name'].endswith('.npz'):
        params['name'] = f'{params["name"]}.npz'

    if isinstance(params['values'], str):
        params['values'] = [params['values']]

    log = params['name'].replace('.npz', '.log')

    from   genolearn.logger import print_dict

    print_dict('executing "feature-selection" with parameters:', params)

    meta_path      = os.path.join(active['data-dir'], active['meta'])

    core_feature_selection(params['name'], active['preprocess-dir'], meta_path, active['identifier'], active['target'], 
                           params['group_by'], params['values'], params['method'], params['aggregate'], log, params['sparse'])
