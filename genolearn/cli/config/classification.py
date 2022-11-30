"""
classification doc

"""

from   genolearn.utils import prompt, IntRange, FloatRange
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
                     config_name = dict(prompt = 'config-name', type = click.STRING, default = 'logistic-regression.config'),
                     penalty = dict(prompt = 'penalty', type = click.Choice(['l1', 'l2', 'elasticnet', 'none']), default = 'l2'),
                     dual = dict(prompt = 'dual', type = click.BOOL, default = False),
                     tol = dict(prompt = 'tol', type = click.FloatRange(1e-8), default = 1e-4),
                     C = dict(prompt = 'C', type = click.FloatRange(1e-8), default = 1.),
                     fit_intercept = dict(prompt = 'fit-intercept', type = click.BOOL, default = True),
                     class_weight = dict(prompt = 'class-weight', type = click.Choice(['balanced', 'None']), default = 'None'),
                     random_state = dict(prompt = 'random-state', type = click.INT, default = None),
                     solver = dict(prompt = 'solver', type = click.Choice(['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga']), default = 'lbfgs'),
                     max_iter = dict(prompt = 'max-iter', type = click.IntRange(1), default = 100),
                     multi_class = dict(prompt = 'multi-class', type = click.Choice(['auto', 'ovr', 'multinomial']), default = 'auto'),
                     n_jobs = dict(prompt = 'n-jobs', type = click.IntRange(-1), default = 1),
                     l1_ratio = dict(prompt = 'l1-ratio', type = click.FloatRange(0), default = 1.)),
            random_forest = \
                dict(model = 'RandomForestClassifier',
                     config_name = dict(prompt = 'config-name', type = click.STRING, default = 'random-forest.config'),
                     n_estimators = dict(prompt = 'n-estimators', type = IntRange(1), default = 100),
                     criterion = dict(prompt = 'criterion', type = click.Choice(['gini', 'entropy', 'log_loss']), default = 'gini'),
                     max_depth = dict(prompt = 'max-depth', type = IntRange(1), default = None),
                     min_samples_split = dict(prompt = 'min-samples-split', type = IntRange(1), default = 2),
                     min_samples_leaf = dict(prompt =  'min-samples-leaf', type = IntRange(1), default = 1),
                     min_weight_fraction_leaf = dict(prompt = 'min-weight-fraction-leaf', type = FloatRange(0., 0.5), default = 0.),
                     max_features = dict(prompt = 'max-features', type = click.Choice(['sqrt', 'log2', 'None']), default = 'sqrt'),
                     max_leaf_nodes = dict(prompt = 'max-leaf-nodes', type = IntRange(1), default = None),
                     min_impurity_decrease = dict(prompt = 'min-impurity-decrease', type = FloatRange(0), default = 0.),
                     bootstrap = dict(prompt = 'bootstrap', type = click.BOOL, default = True),
                     oob_score = dict(prompt = 'oob-score', type = click.BOOL, default = False),
                     n_jobs = dict(prompt = 'n-jobs', type = IntRange(-1), default = 1),
                     random_state = dict(prompt = 'random-state', type = click.INT, default = 0),
                     class_weight = dict(prompt = 'class-weight', type = click.Choice(['balanced', 'balanced_subsample', 'None']), default = None))
        )

def base(name):
    info        = INFO[name]
    params      = {'model' : info.pop('model')}
    params.update(prompt(info))
    config_name = params.pop('config_name')
    with open(config_name, 'w') as file:
        print(json.dumps(params, indent = 4), file = file)

@classification.command(name = 'logistic-regression')
def logistic_regression():
    base('logistic_regression')

@classification.command(name = 'random-forest')
def random_forest():
    base('random_forest')