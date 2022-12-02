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
    from   genolearn.core.feature_selection import feature_selection
    from   genolearn.utils import prompt

    import os

    active = get_active()
    if active is not None:
        if not os.path.exists(active["preprocess_dir"]):
            return print('execute "genolearn preprocess sequence" first')
        if 'meta' not in os.listdir(active['preprocess_dir']):
            return print('execute "genolearn preprocess meta" first')
    path = os.path.join(active['preprocess_dir'], 'meta')
    info = dict(name   = dict(default = 'fisher-scores.npz', type = click.STRING),
                meta   = dict(type = click.Choice(os.listdir(path))),
                method = dict(default = 'fisher', type = click.STRING))

    params = prompt(info)

    # ensure .npz ending
    if not params['name'].endswith('.npz'):
        params['name'] = f'{params["name"]}.npz'

    params['log'] = params['name'].replace('.npz', '.log')

    from   genolearn.logger import print_dict

    print_dict('executing "feature-selection" with parameters:', params)

    params['preprocess_dir'] = active['preprocess_dir']

    feature_selection(**params)
