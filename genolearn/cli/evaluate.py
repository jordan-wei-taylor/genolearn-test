import click

@click.command()
def evaluate():
    """
    configure static data used by GenoLearn.

    \b
    prompted information
        model             : path to trained model generated from executing ``genolearn train``
        output            : output feature importance file
    """
    from   genolearn.core.config import get_active
    from   genolearn.utils       import prompt

    import json
    import os

    active = get_active()
    path   = os.path.join(active['data_dir'], active['meta'])

    info   = dict(train_dir = dict(type = click.Path()),
                  values    = dict(type = click.STRING))

    params = prompt(info)
    
    from   genolearn.logger import print_dict

    print_dict('executing "evaluate" with parameters:', params)

    from   genolearn.core          import core_evaluate

    data_config = dict(path = active['preprocess_dir'], meta_path = os.path.join(active['data'], active['meta']),
                        identifier = active['identifier'], target = active['target'], group = active['group'])

    params['data_config'] = data_config

    model = os.path.join(params['train_dir'], 'model.pickle')

    with open(os.path.join(params['train_dir'], 'feature-selection.json')) as f:
        selection = json.load(f)

    params['feature_selection'] = selection['feature-selection']
    params['key'] = selection['key']
    params['ascending'] = selection['ascending']

    core_evaluate(**params)
