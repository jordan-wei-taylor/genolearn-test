"""
train doc
"""

from   genolearn.logger import print_dict
# from   genolearn.models.classification import valid_models
from   genolearn.core.config import get_active

import click
import json
import os

active = get_active()

models = click.Choice(['RandomForestClassifier', 'LogisticRegression'])

if active:
    path   = os.path.join(active['preprocess_dir'], 'feature-selection')
    order  = click.Choice([file for file in os.listdir(path) if file.endswith('.npz')] if os.path.exists(path) else [])
else:
    path   = None
    order  = None

@click.command()
@click.option('--overwrite', default = False, is_flag = True, show_default = True)
def train(overwrite):
    """
    trains machine learning models using a grid search for hyperparameter tuning.

    \b
    prompted information
        output directory      : output directory
        model config          : path to model configuration file generated by genolean config model
        number of features    : comma seperated integers for varying number of features to consider
        training data         : group value(s) to identify which observations should be part of the training data
        testing data          : group value(s) to identify which observations should be part of the testing data
        feature selection     : feature selection file to use generated by genolearn feature-selection
        feature selection key : feature selection key to use within the feature selection file
        ascending             : feature order to use
        min count             : min count of training class observations to be considered
        target subset         : subset of target values to train on if provided
        metric                : statistical metric to measure goodness of fit
        aggregation function  : aggregation function to compute overall goodness of fit
    """
    from genolearn.utils import prompt
    
    if 'model' not in os.listdir(active['preprocess_dir']):
        return print('execute "genolearn config model" first')
    
    if 'feature-selection' not in os.listdir(active['preprocess_dir']):
        return print('execute "genolearn feature-selection" first')
        
    meta  = os.listdir(os.path.join(active['preprocess_dir'], 'meta'))
    model = os.listdir(os.path.join(active['preprocess_dir'], 'model'))
    fs    = [file for file in os.listdir(os.path.join(active['preprocess_dir'], 'feature-selection')) if file.endswith('.npz')]
    info  = dict(output_dir = dict(default = 'training-output', type = click.Path()),
                 meta = dict(type = click.Choice(meta)),
                 model_config = dict(type = click.Choice(model)),
                 feature_selection = dict(type = click.Choice(fs)),
                 num_features = dict(default = 1000, type = click.IntRange(1)),
                 ascending = dict(default = False, type = click.BOOL),
                 min_count = dict(default = 0, type = click.IntRange(0)),
                 target_subset = dict(default = 'None', type = click.STRING),
                 metric = dict(default = 'f1_score', type = click.STRING),
                 aggregate_func = dict(default = 'weighted_mean', type = click.Choice(['mean', 'weighted_mean'])))

    params = prompt(info)

    if isinstance(params['num_features'], int):
        params['num_features'] = [params['num_features']]

    print_dict('executing "genolearn train" with parameters:', params)

    with open(os.path.join(active['preprocess_dir'], 'model', params['model_config'])) as file:
        params['model_config'] = json.load(file)

    params['model'] = params['model_config'].pop('model')

    from genolearn.core.train import train
    train(**params, overwrite = overwrite)