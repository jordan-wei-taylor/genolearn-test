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
    meta   = os.listdir(os.path.join(active['preprocess_dir'], 'meta'))
    info   = dict(train_dir = dict(type = click.Path()),
                  output    = dict(type = click.Path(), default = 'importance'))

    params = prompt(info)

    params['train_dir'] = os.path.abspath(params['train_dir'])
    params['model']     = os.path.join(params['train_dir'], 'model.pickle')
    
    from   genolearn.logger import print_dict

    print_dict('executing "genolearn feature-importance" with parameters:', params)
    
    with open(os.path.join(params.pop('train_dir'), 'train.log')) as f:
        log = f.read()
        log = json.loads('\n'.join(log.split('\n')[4:]))
        selection = dict(feature_selection = log['feature_selection'], ascending = log['ascending'])
        params['meta'] = log['meta']
        
    params['feature_selection'] = selection['feature_selection']
    params['ascending']         = selection['ascending']

    from   genolearn.core.feature_importance import feature_importance

    feature_importance(**params)
