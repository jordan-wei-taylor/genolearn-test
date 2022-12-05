import click

@click.command()
def evaluate():
    """
    configure static data used by GenoLearn.

    \b
    prompted information
        train_dir : a subdirectory within <working-dir>/train containing the model of interest to evaluate
        output    : output subdirectory name within <working-dir>/evaluate/<train_dir>
        values    : group value(s) to identify which observations should be part of the dataset for evaluation
    """
    from   genolearn       import get_active, wd
    from   genolearn.utils import prompt, append

    import json
    import os

    active = get_active()

    info   = dict(train_dir = dict(type = click.Choice(os.listdir(os.path.join(wd, 'train')))),
                  output    = dict(type = click.Path()),
                  values    = dict(type = click.STRING, multiple = True))

    params = prompt(info)

    with open(os.path.join(wd, 'train', params['train_dir'], 'train.log')) as f:
        log  = json.loads('\n'.join(f.readlines()[4:]))
        for key in ['meta', 'feature_selection']:
            params[key] = log[key]

    with open(os.path.join(wd, 'train', params['train_dir'], 'params.json')) as f:
        params['num_features'] = json.load(f)['num_features']

    from   genolearn.logger import print_dict

    print_dict('executing "evaluate" with parameters:', params)

    with open(os.path.join(wd, 'train', params['train_dir'], 'encoding.json')) as f:
        params['encoder'] = json.load(f)

    path   = os.path.join(wd, 'evaluate', params['train_dir'])
    os.makedirs(path, exist_ok = True)

    params['output'] = os.path.join(path, params['output'])

    if not params['output'].endswith('.csv'):
        params['output'] = params['output'] + '.csv'

    from   genolearn.core.evaluate import evaluate

    data_config = dict(working_dir = wd, meta_file = params.pop('meta'))

    params['data_config'] = data_config

    params['model'] = os.path.join(os.path.join(wd, 'train', params.pop('train_dir')), 'model.pickle')
    evaluate(**params)
    append(f'evaluate ({params["output"]})')