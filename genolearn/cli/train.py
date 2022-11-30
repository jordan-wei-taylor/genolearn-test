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
    path   = os.path.join(active['preprocess-dir'], 'feature-selection')
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
    from genolearn.utils import prompt, IntRange
    
    info = dict(output_dir = dict(prompt = 'output directory', default = 'training-output', type = click.Path()),
                model_config = dict(prompt = 'model config', type = click.Path()),
                num_features = dict(prompt = 'number of features', default = 1000, type = IntRange(1)),
                training_data = dict(prompt = 'training data', default = 'train', type = click.STRING),
                testing_data = dict(prompt = 'testing data', default = 'test', type = click.STRING),
                feature_selection = dict(prompt = 'feature selection', type = order),
                feature_selection_key = dict(prompt = 'feature selection key', default = 'train', type = click.STRING),
                ascending = dict(prompt = 'ascending', default = False, type = click.BOOL),
                min_count = dict(prompt = 'min count', default = 0, type = IntRange(0)),
                target_subset = dict(prompt = 'target subset', default = 'None', type = click.STRING),
                metric = dict(prompt = 'metric', default = 'f1_score', type = click.STRING),
                aggregate_func = dict(prompt = 'aggregation function', default = 'weighted_mean', type = click.Choice(['mean', 'weighted_mean'])))

    params = prompt(info)

    for key in ['num_features', 'training_data', 'testing_data']:
        if not isinstance(params[key], list):
            params[key] = [params[key]]

    model_config = params.pop('model_config')
    with open(model_config) as file:
        model_config = json.load(file)

    model = model_config.pop('model')

    data_config = dict(path = active['preprocess-dir'], meta_path = os.path.join(active['data-dir'], active['meta']),
                        identifier = active['identifier'], target = active['target'], group = active['group'])
            
    print_dict('executing "genolearn train" with parameters:', params)

    from genolearn.core import core_train
    core_train(params['output_dir'], model, data_config, model_config, params['training_data'], params['testing_data'], params['num_features'], params['feature_selection'], 
               params['feature_selection_key'], params['ascending'], params['min_count'], params['target_subset'], params['metric'],
               params['aggregate_func'], overwrite)
