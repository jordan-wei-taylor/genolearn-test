import click

@click.command(name = 'feature-importance')
def feature_importance():
    """
    given a trained model, inspect which features were important.

    \b
    prompted information
        train_dir : directory of a subdirectory within <working-dir>/train
    """
    from   genolearn import get_active, wd
    from   genolearn.utils       import prompt, append

    import json
    import os

    active = get_active()
    valid  = os.path.join(wd, 'train')

    if not os.path.exists(valid):
        return print('execute "genolearn train" first')

    info   = dict(train_dir = dict(type = click.Choice(os.listdir(valid))))

    params = prompt(info)

    train_dir = params['train_dir']

    from   genolearn.logger import print_dict

    print_dict('executing "genolearn feature-importance" with parameters:', params)
    
    params['train_dir'] = os.path.join(wd, 'train', params['train_dir'])
    params['model']     = os.path.join(params['train_dir'], 'model.pickle')
    params['output']    = os.path.join(wd, 'train', params['train_dir'], 'importance')
    
    with open(os.path.join(params.pop('train_dir'), 'train.log')) as f:
        log = f.read()
        log = json.loads('\n'.join(log.split('\n')[4:]))
        params['feature_selection'] = log['feature_selection']
        params['meta'] = log['meta']
    

    from   genolearn.core.feature_importance import feature_importance

    feature_importance(**params)
    append(f'feature-importance ({train_dir})')