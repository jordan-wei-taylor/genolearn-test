"""
classification doc

"""

from   genolearn.utils import prompt
import click
import json

@click.group()
def classification():
    """
    creates a classification config.
    """
    ...
    
INFO = dict(logistic_regression = \
                dict(model = 'LogisticRegression',
                     config_name = dict(type = click.STRING, default = 'logistic-regression.config'),
                     penalty = dict(type = click.Choice(['l1', 'l2', 'elasticnet', 'none']), default = 'l2'),
                     dual = dict(type = click.BOOL, default = False),
                     tol = dict(type = click.FloatRange(1e-8), default = 1e-4),
                     C = dict(type = click.FloatRange(1e-8), default = 1.),
                     fit_intercept = dict(type = click.BOOL, default = True),
                     class_weight = dict(type = click.Choice(['balanced', 'None']), default = 'None'),
                     random_state = dict(type = click.INT, default = None),
                     solver = dict(type = click.Choice(['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga']), default = 'lbfgs'),
                     max_iter = dict(type = click.IntRange(1), default = 100),
                     multi_class = dict(type = click.Choice(['auto', 'ovr', 'multinomial']), default = 'auto'),
                     n_jobs = dict(type = click.IntRange(-1), default = -1),
                     l1_ratio = dict(type = click.FloatRange(0), default = 1.)),
            random_forest = \
                dict(model = 'RandomForestClassifier',
                     config_name = dict(type = click.STRING, default = 'random-forest.config'),
                     n_estimators = dict(type = click.IntRange(1), default = 100),
                     criterion = dict(type = click.Choice(['gini', 'entropy', 'log_loss']), default = 'gini'),
                     max_depth = dict(type = click.IntRange(1), default = None),
                     min_samples_split = dict(type = click.IntRange(1), default = 2),
                     min_samples_leaf = dict(type = click.IntRange(1), default = 1),
                     min_weight_fraction_leaf = dict(type = click.FloatRange(0., 0.5), default = 0.),
                     max_features = dict(type = click.Choice(['sqrt', 'log2', 'None']), default = 'sqrt'),
                     max_leaf_nodes = dict(type = click.IntRange(1), default = None),
                     min_impurity_decrease = dict(type = click.FloatRange(0), default = 0.),
                     bootstrap = dict(type = click.BOOL, default = True),
                     oob_score = dict(type = click.BOOL, default = False),
                     n_jobs = dict(type = click.IntRange(-1), default = -1),
                     random_state = dict(type = click.INT, default = 0),
                     class_weight = dict(type = click.Choice(['balanced', 'balanced_subsample', 'None']), default = None))
        )

def base(name):
    from   genolearn.core.config import get_active
    import os

    info        = INFO[name]
    params      = {'model' : info.pop('model')}
    params.update(prompt(info))
    config_name = params.pop('config_name')
    active      = get_active()
    path        = os.path.join(active['preprocess_dir'], 'model')
    os.makedirs(path, exist_ok = True)
    with open(os.path.join(path, config_name), 'w') as file:
        print(json.dumps(params, indent = 4), file = file)
    print(f'generated "{config_name}" in {path}')

@classification.command(name = 'logistic-regression')
def logistic_regression():
    base('logistic_regression')

@classification.command(name = 'random-forest')
def random_forest():
    base('random_forest')