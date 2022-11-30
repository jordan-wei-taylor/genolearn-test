import click

@click.command(name = 'feature-importance')
def feature_importance():
    """
    creates a npz file with the feature importance for a trained model.

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

    info   = dict(train_dir = dict(prompt = 'train-dir', type = click.Path()),
                  output    = dict(prompt = 'output', type = click.Path(), default = 'importance'))

    params = prompt(info)

    params['train_dir'] = os.path.abspath(params['train_dir'])
    params['model']     = os.path.join(params['train_dir'], 'model.pickle')
    selection_path      = os.path.join(params.pop('train_dir'), 'feature-selection.json')
    
    from   genolearn.logger import print_dict

    print_dict('executing "genolearn feature-importance" with parameters:', params)
    
    with open(selection_path) as f:
        selection = json.load(f)

    params['feature_selection'] = selection['feature_selection']
    params['key']               = selection['key']
    params['ascending']         = selection['ascending']

    from   genolearn.core import core_feature_importance

    core_feature_importance(active['preprocess-dir'], **params)
