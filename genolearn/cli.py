from   genolearn.logger import up, clear, print_dict
from   genolearn.utils  import prompt, append, _prompt
from   genolearn        import __version__, ls, working_directory, get_active, listdir

from   shutil           import rmtree

import resource
import inspect
import pandas as pd
import click
import json
import os

# set preprocessed metadata list
metas  = listdir('meta')

# get active working directory and input metadata
active = get_active()

def user_input(text, n):
    """
    Obtains user input and is bounded between [0, n]
    """
    j = input(text)
    if j.isdigit():
        if 0 <= int(j) < n:
            return int(j), False
    return None, True

def enum(options, pre = 'commands', post = 'user input', k = None, back = None):
    """
    Prints enumerated options to for user input, records the user input, then executes an associated function or returns the option key.

    Parameters
    ----------
        options, (list, dict)
            Available options from the user to choose from. If type dict, the values should be a dictionary with optional entries:
                prompt : prompt to display to the user
                info   : information explaining what the prompt is for
                func   : function to execute should the user choose the option
        
        pre, str ['commands']
            Text to print prior to the enumerated options.

        post, str ['user input']
            Text to print post enumerated options.

        k, int [None]
            Truncate enumerated options.

        back, function [None]
            Function to execute if the user selects to go back (None results in main menu).
    """

    # set back to menu if not provided
    if back is None:
        back = menu

    # set options to only contain back initially (to ensure back is the option 0)
    if back == exit:
        _options = dict(exit = dict(info = 'exits GenoLearn', func = back))
    else:
        _options = dict(back = dict(info = 'goes to the previous command', func = back))

    # add in entries provided
    if isinstance(options, list):
        _options.update({option : {} for i, option in enumerate(options) if k is None or i < k})
    else:
        _options.update({key : value for i, (key, value) in enumerate(options.items()) if k is None or i < k})
        
    options = _options

    # number of options (ignoring back)
    n = len(options)

    # spacing for option number
    m = len(f'{n}')

    # spacing for prompt
    c = max(max(len(option.get('prompt', name)) for name, option in options.items()) + 15, 30)

    # print the pre-text
    print(pre, '\n')

    # print enumerated options
    for i, (name, option) in enumerate(options.items()):
        print(f'{i:{m}d}.  {option.get("prompt", name):{c}s}  {option.get("info", "")}')

        # print extra space to seperate back option from the rest of the option
        if i == 0: print()

    # line space between last option and post-text
    print()

    # obtain user input
    j, flag = user_input(f'{post} : ', n)

    # if incorrect, retry
    while flag:
        print(f'{up}{clear}', end = '')
        j, flag = user_input(f'\r{post} : ', n)

    # clear screen
    pre_n = pre.count('\n') + 1
    print(up * (n + pre_n + 4) + clear, end = '')

    # option key
    key = list(options)[j]

    # if func was provided, execute it
    if 'func' in options[key]:
        func = options[key]['func']
        return func(key) if inspect.signature(func).parameters else func() # if takes in an argument, pass the option key

    # if func not provided, return the option key
    return key

def select_meta(pre, func, back, meta_func = None):
    """ Wrapper for first selecting metadata """
    def _select_meta():
        if len(metas) == 1:
            return func(metas[0])
        common  = lambda meta : {'func' : func, 'info' : meta_func(meta)} if meta_func else {'func' : func}
        options = {meta : common(meta) for meta in metas}
        enum(options, pre, back = back)
    return _select_meta

def _train():
    """ Wrapper for first selecting metadata and then feature-selection """
    def _select_meta():
        def _select_feature_selection(meta):
            selections = []
            for file in listdir('feature-selection'):
                if file.endswith('.log'):
                    log = read_log(os.path.join('feature-selection', file))
                    if log['meta'] == meta:
                        selections.append(file.replace('.log', ''))
            if len(selections) == 0:
                return print(f'feature-selection for {meta} not executed')
            elif len(selections) == 1:
                train(meta, selections[0])
            else:
                options = {selection : {'func' : lambda selection : train(meta, selection)} for selection in selections}
                enum(options, f'select feature selection using "{meta}" metadata', back = _select_meta)
        if len(metas) == 1:
            return _select_feature_selection(metas[0])
        _options = {}
        for meta in metas:
            for file in listdir('feature-selection'):
                if file.endswith('.log'):
                    log = read_log(os.path.join('feature-selection', file))
                    if log['meta'] == meta:
                        _options[meta] = {'func' : _select_feature_selection, 'info' : detect_train(meta)}
                        break
        enum(_options, 'select metadata file for train command')
    return _select_meta()

def select_train_dir(pre, func, back, train_dir_func = None):
    """ Wrapper for first selecting training directory """
    def _select_train_dir():
        train_dirs = os.listdir(os.path.join(working_directory, 'train'))
        if len(train_dirs) == 1:
            return func(train_dirs[0])
        common  = lambda train_dir : {'func' : func, 'info' : train_dir_func(train_dir)} if train_dir_func else {'func' : func}
        options = {train_dir : common(train_dir) for train_dir in train_dirs}
        enum(options, pre, back = back)
    return _select_train_dir    

def exit():
    """ Exits the Python shell execution """
    quit()

def _reduce(d, limit):
    """ Truncates dictionary values for printing purposes """
    if isinstance(d, dict):
        if len(d) > limit:
            for i, (k, v) in enumerate(d.copy().items(), 1):
                if i < limit:
                    d[k] = _reduce(v, limit)
                else:
                    del d[k]
                    d['...'] = '...'
        else:
            for k, v in d.items():
                d[k] = _reduce(v, limit)
    elif isinstance(d, list):
        if len(d) > limit:
            d = d[:limit - 1] + ['...']
    return d

def reduce(d, limit):
    """ Truncates dictionary values for printing purposes """
    for k, v in d.items():
        d[k] = _reduce(v, limit)
    return d

def read_log(file):
    """ Reads only the dictionary component of a text file """
    with open(os.path.join(working_directory, file)) as f:
        string = f.read()
        log    = json.loads(string[string.index('{'):])
        return log

def check_history(string):
    """ Checks if any previously executed commands starts with {string}"""
    with open(os.path.join(working_directory, '.genolearn')) as f:
        history = json.load(f)['history']
        for line in history:
            if line.startswith(string):
                return True
        return False

def detect_feature_selection(meta):
    """ Adds the "info" entry when selecting a metadata file for the feature-selection command"""
    if 'feature-selection' in ls:
        ret = []
        for log in listdir('feature-selection'):
            if log.endswith('.log'):
                log = read_log(os.path.join('feature-selection', log))
                if log['meta'] == meta:
                    ret.append(log['method'])
        if ret:
            return f'({", ".join(ret)})'
    return ''

def detect_train(meta):
    """ Adds the "info" entry when selecting a metadata file for the train command """
    if 'train' in ls:
        ret = []
        for train_dir in listdir('train'):
            if read_log(os.path.join('train', train_dir, 'train.log'))['meta'] == meta:
                ret.append(train_dir)
        if ret:
            return f'({", ".join(ret)})'
    return ''
    
def detect_feature_importance(train_dir):
    """ Adds the "info" entry when selecting a train_dir for the feature-importance command """
    if 'importance' in listdir(os.path.join('train', train_dir)):
        return '(already exists)'
    return ''

def detect_evaluate(train_dir):
    """ Adds the "info" entry when selecting a train_dir for the evaluate command """
    if 'evaluate' in ls and train_dir in listdir('evaluate'):
        print(train_dir)
        ret = []
        for file in listdir(os.path.join('evaluate', train_dir)):
            ret.append(file.replace('.csv', ''))
        return f'({", ".join(ret)})'
    return ''

def setup():
    """ Sets the data directory and proceeds to set the metadata file path """
    def _setup_meta(dir):
        csvs    = [csv for csv in os.listdir(dir) if csv.endswith('.csv')]
        if len(csvs) == 0:
            return print(f'no csv files found in {os.path.abspath(dir)}!')
        options = {csv : {'func' : lambda csv : _setup(dir, csv)} for csv in csvs}
        enum(options, 'select metadata csv for setup', back = setup)
    dirs = [dir for dir in ls if os.path.isdir(dir) and not dir.startswith('_')]
    options = {'.' : {'func' : _setup_meta, 'info' : '(current directory)'}}
    for dir in dirs:
        options[dir] = {'func' : _setup_meta}
    enum(options, 'select data directory for setup')

def _setup(data_dir, meta):
    """ Sets the current working directory and metadata file within it """

    config = dict(data_dir = os.path.abspath(data_dir), meta = meta, history = [f'setup ({__version__})'])
    with open('.genolearn', 'w') as file:
        print(json.dumps(config, indent = 4), file = file, end = '')
    print('setup complete in current directory')

def clean():
    """ Deletes all GenoLearn generated files upon user confirmation """
    option = dict(confirm = dict(func = _clean, info = 'this cannot be undone'))
    enum(option, f'confirm deletion of all GenoLearn generated files in {working_directory}?')

def _clean():
    """ Deletes all GenoLearn generated files """
    os.chdir(working_directory)
    for dir in ['evaluate', 'feature-selection', 'meta', 'model', 'preprocess', 'train']:
        if dir in ls:
            rmtree(dir)
    hidden = '.genolearn'
    if hidden in ls:
        os.remove(hidden)
    print(f'cleaned {working_directory}')

def preprocess_sequence_data():
    """ Select sequential data to preprocess """
    gzs     = [gz for gz in os.listdir(active['data_dir']) if gz.endswith('.gz')]
    if len(gzs) == 0:
        return print('no sequence data (*.gz) files found!')
    elif len(gzs) == 1:
        return preprocess_sequence(gzs[0])
    options = {gz : {'func' : preprocess_sequence} for gz in gzs}
    enum(options, 'select sequence data to preprocess', back = preprocess)

def preprocess_sequence(data):
    """ Preprocesses sequential data """
    print(f'preprocess {data}')
    info   = dict(batch_size = dict(type = click.INT, default = None),
                  n_processes = dict(type = click.INT, default = None),
                  sparse = dict(type = click.BOOL, default = True),
                  dense = dict(type = click.BOOL, default = True),
                  verbose = dict(type = click.IntRange(1), default = 250000),
                  max_features = dict(type = click.IntRange(-1), default = -1))

    params = dict(data = data)
    params.update(prompt(info))

    assert params['dense'] or params['sparse'], 'set either / both dense and sparse to True'

    params['data']         = os.path.join(active['data_dir'], data)

    if params['max_features'] != -1:
        params['verbose'] = params['max_features'] // 10

    from multiprocessing import cpu_count

    if params['batch_size'] == None:
        params['batch_size'] = min(resource.getrlimit(resource.RLIMIT_NOFILE)[1], 2 ** 14) # safety
    if params['n_processes'] == None:
        params['n_processes'] = cpu_count()

    print_dict('executing "preprocess" with parameters:', params)

    from   genolearn.core.preprocess import preprocess as core_preprocess

    os.chdir(working_directory)
    core_preprocess('preprocess', **params)
    append(f'preprocess sequence ({data})')

def preprocess_combine_data():
    """ Select sequential data to preprocess and combine with already preprocessed data """
    with open(os.path.join(working_directory, '.genolearn')) as f:
        log = json.load(f)
        preprocessed = []
        for line in log['history']:
            if line.startswith('preprocess sequence'):
                preprocessed.append(line[21:-1])
    options = {}
    for data in os.listdir(active['data_dir']):
        if data.endswith('.gz') and data not in preprocessed:
            options[data] = {'func' : preprocess_combine}
    enum(options, 'sequence data', back = preprocess)

def preprocess_combine(data):
    """ Preprocess sequential data and combine with already preprocessed data """
    print(f'preprocess {data}')
    info = dict(batch_size   = dict(type = click.INT, default = None),
                n_processes  = dict(type = click.INT, default = None),
                verbose      = dict(type = click.INT, default = 250000))

    params = dict(data = data)
    params.update(prompt(info))

    meta   = read_log(os.path.join('preprocess', 'preprocess.log'))
    params['max_features'] = meta['max_features']

    params['data'] = os.path.join(active['data_dir'], data)

    if params['max_features'] != -1:
        params['verbose'] = params['max_features'] // 10
        
    from multiprocessing import cpu_count

    if params['batch_size'] == None:
        params['batch_size'] = min(resource.getrlimit(resource.RLIMIT_NOFILE)[1], 2 ** 14) # safety
    if params['n_processes'] == None:
        params['n_processes'] = cpu_count()

    print_dict('executing "combine" with parameters:', params)

    from   genolearn.core.preprocess import combine

    os.chdir(working_directory)
    combine('preprocess', **params)
    append(f'preprocess combine ({data})')

def preprocess_meta():
    """ Preprocesses metadata """
    meta_path      = os.path.join(active['data_dir'], active['meta'])
    print(f'preprocess {os.path.basename(active["meta"])}')

    meta_df        = pd.read_csv(meta_path).applymap(str)
    valid_columns  = set(meta_df.columns)
    
    output         = click.prompt('output       ', type = click.STRING, default = 'default')
    identifier     = click.prompt('identifier             ', type = click.Choice(valid_columns), show_choices = False)

    valid_columns -= set([identifier])

    target         = click.prompt('target                 ', type = click.Choice(valid_columns), show_choices = False)

    valid_columns -= set([target])
    valid_columns |= set(['None'])

    group          = click.prompt('group           ', type = click.Choice(valid_columns), show_choices = False, default = 'None')

    if group != 'None':
        groups       = set(sorted(set(meta_df[group])))
        train_values = _prompt('train group values*    ', type = click.Choice(groups), default = None, default_option = False, multiple = True)
        groups      -= set(train_values)
        test_values  = _prompt('test  group values*    ', type = click.Choice(groups), default = None, default_option = False, multiple = True)
        ptrain       = None
    else:
        train_values = ['Train']
        test_values  = ['Test']
        ptrain       = click.prompt('proportion train', type = click.FloatRange(0., 1.), default = 0.75)

    from genolearn.core.preprocess import preprocess_meta

    os.chdir(working_directory)
    preprocess_meta(output, meta_path, identifier, target, group, train_values, test_values, ptrain)
    append(f'preprocess meta ({output})')

def preprocess():
    """ Preprocess command """
    options = {'sequence' : {'info' : 'preprocesses sequence data',
                             'func' : preprocess_sequence_data},
               'combine'  : {'info' : 'preprocesses sequence data and combines to previous preprocessing',
                             'func' : preprocess_combine_data},
               'meta'     : {'info' : 'preprocesses meta data',
                             'func' : preprocess_meta}}
    enum(options, 'preprocess commands', k = None if check_history('preprocess sequence') else 1)

def analyse(meta):
    """ Analyse preprocessed metadata for class label distribution and suggested target subset list """
    info  = dict(min_count  = dict(type = click.IntRange(0), default = 10),
                 proportion = dict(type = click.BOOL, default = False))

    print(f'analysing "{meta}"')
    params = dict(meta = meta)
    params.update(prompt(info))

    params['meta'] = os.path.join('meta', params['meta'])
    
    from   genolearn.core.data import analyse
    
    os.chdir(working_directory)
    if os.path.exists(params['meta']):
        analyse(**params)
    else:
        print('execute genolearn preprocess first')


def head(meta, num = 10):
    """ Prints the first NUM rows of meta data """
    meta   = os.path.join(working_directory, 'meta', meta)
    from genolearn.core.data import head
    head(meta, num)


def tail(meta, num = 10):
    """ Prints the last NUM rows of meta data """
    meta   = os.path.join(working_directory, 'meta', meta)
    from genolearn.core.data import tail
    tail(meta, num)


def sample(meta, num = 10):
    """ Prints random NUM rows of meta data """
    meta   = os.path.join(working_directory, 'meta', meta)
    from genolearn.core.data import sample
    sample(meta, num)

def data():
    """ Data command """
    pre     = lambda command : f'select metadata for data {command} command'
    options = {'analyse' : {'info' : 'analyses the metadata'                , 'func' : select_meta(pre('analyse'), analyse, data)},
               'head'    : {'info' : 'prints the head of the metadata'      , 'func' : select_meta(pre('head')   , head   , data)},
               'tail'    : {'info' : 'prints the tail of the metadata'      , 'func' : select_meta(pre('tail')   , tail   , data)},
               'sample'  : {'info' : 'prints random entries of the metadata', 'func' : select_meta(pre('sample') , sample , data)}}
    enum(options, 'print data commands')


def _feature_selection():
    """ Wrapper for first selecting metadata and then feature-selection method """

    path = 'feature-selection'

    def detect_outer(meta):
        ret = []
        if os.path.exists(os.path.join(working_directory, path)):
            for file in listdir(path):
                if file.endswith('.log'):
                    log = read_log(os.path.join(path, file))
                    if log['meta'] == meta:
                        ret.append(log['method'])
            if ret:
                return f'({", ".join(ret)})'
        return ''

    def detect_inner(meta, method):
        if os.path.exists(os.path.join(working_directory, path)):
            for file in listdir(path):
                if file.endswith('.log'):
                    log = read_log(os.path.join(path, file))
                    if log['meta'] == meta and log['method'] == method:
                        return '(already exists)'
        return ''
        
    def _select_meta():
        def _select_feature_selection(meta):
            key     = os.path.join(os.path.dirname(__file__), 'core', 'feature_selection', 'fisher.py')
            func    = lambda method : feature_selection(meta, method)
            exists  = detect_inner(meta, 'fisher')
            options = {key : {'prompt' : 'fisher', 'info' : exists if exists else 'Fisher Score for Feature Selection', 'func' : func}}
            for dir in set([working_directory, os.path.abspath('.')]):
                for file in os.listdir(dir):
                    if file.endswith('.py'):
                        py  = file.replace('.py', '')
                        key = os.path.join(dir, file)
                        options[key] = {'prompt' : py, 'func' : func, 'info' : detect_inner(meta, py)}
            if len(options) == 1:
                return feature_selection(meta, key)
            
            enum(options, f'select feature selection method to use for "{meta}" metadata', back = _select_meta)
        if len(metas) == 1:
            return _select_feature_selection(metas[0])
        options = {meta : {'func' : _select_feature_selection, 'info' : detect_outer(meta)} for meta in metas}
        enum(options, 'select metadata file for feature selection command')
    return _select_meta()
            
def feature_selection(meta, module):
    """ Computes Feature Selection (Fisher by default) """
    print(f'set parameter for feature selection using "{meta}" meta with "{os.path.basename(module)[:-3]}" method')
    py     = os.path.basename(module).replace('.py', '')
    params = dict(meta = meta, method = py, module = module.replace(os.path.expanduser('~'), '~'))
    info   = dict(name = dict(default = f'{py}-{params["meta"]}', type = click.STRING))
    
    params.update(prompt(info))

    params['log'] = f"{params['name']}.log"

    print_dict('executing "feature-selection" with parameters:', params)

    from   genolearn.core.feature_selection import feature_selection
    os.chdir(working_directory)
    feature_selection(**params)
    append(f'feature-selection ({params["name"]})')

classifiers = dict(
                  logistic_regression = \
                  dict(model = 'LogisticRegression',
                          config_name = dict(type = click.STRING, default = 'logistic-regression'),
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
                          config_name = dict(type = click.STRING, default = 'random-forest'),
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
                          random_state = dict(type = click.INT, default = None),
                          class_weight = dict(type = click.Choice(['balanced', 'balanced_subsample', 'None']), default = None))
                  )

def _model(name):
    """ Given a model name, prompts user for hyperparameter settings """
    classifier  = classifiers[name]
    params      = {'model' : classifier.pop('model')}
    print(f'parameters for {params["model"]}')
    params.update(prompt(classifier))
    config_name = params.pop('config_name')
    path        = os.path.join(working_directory, 'model')
    os.makedirs(path, exist_ok = True)
    with open(os.path.join(path, config_name), 'w') as file:
        print(json.dumps(params, indent = 4), file = file)
    print(f'generated "{config_name}" in {path}')
    append(f'model ({config_name})')

def model_config():
    """ Prompts user for model to use before prompting for hyperparameter settings """
    models  = ['logistic_regression', 'random_forest']
    options = {model : {'func' : _model} for model in models}
    enum(options, 'choose a model')

def train(meta, feature_selection):
    """ Given a preprocessed metadata file, trains model(s) and save outputs to the train subdirectory within the working directory """
    print(f'train parameters for metadata file "{meta}" with feature-selection "{feature_selection}"')
    model = listdir('model')
    info  = dict(output_dir = dict(type = click.Path(), default = feature_selection if feature_selection.endswith(meta) else f'{meta}-{feature_selection}'),
                 model_config = dict(type = click.Choice(model)),
                 num_features = dict(default = 1000, type = click.IntRange(1), multiple = True),
                 min_count = dict(default = 0, type = click.IntRange(0)),
                 target_subset = dict(default = 'None', type = click.STRING),
                 metric = dict(default = 'f1_score', type = click.STRING),
                 aggregate_func = dict(default = 'weighted_mean', type = click.Choice(['mean', 'weighted_mean'])))

    params = dict(meta = meta, feature_selection = feature_selection)
    params.update(prompt(info))

    os.chdir(working_directory)
    os.makedirs('train', exist_ok = True)
    
    params['output_dir'] = os.path.join('train', params['output_dir'])
    
    if os.path.exists(params['output_dir']):
        rmtree(params['output_dir'])

    if isinstance(params['num_features'], int):
        params['num_features'] = [params['num_features']]

    print_dict('executing "genolearn train" with parameters:', params)

    from genolearn.core.train import train
    train(**params)
    append(f'train ({os.path.basename(params["output_dir"])})')

def feature_importance(train_dir):
    """ Given a training directory, computes the Feature Importance and outputs an Importance subdirectory """
    params = dict(train_dir = train_dir)

    print_dict('executing "genolearn feature-importance" with parameters:', params)
    
    params['train_dir'] = os.path.join('train', params['train_dir'])
    params['model']     = os.path.join(params['train_dir'], 'model.pickle')
    params['output']    = os.path.join(params['train_dir'], 'importance')
    
    os.chdir(working_directory)

    log = read_log(os.path.join(params.pop('train_dir'), 'train.log'))
    params['feature_selection'] = log['feature_selection']
    params['meta'] = log['meta']

    from   genolearn.core.feature_importance import feature_importance

    feature_importance(**params)
    append(f'feature-importance ({train_dir})')

def evaluate(train_dir):
    """  Given a training directory, evaluates a model on user prompted inputs and outputs to the evaluate subdirectory within the working directory """
    print(f'evaluate parameters for "{train_dir}"')
    log  = read_log(os.path.join(working_directory, 'train', train_dir, 'train.log'))
    meta = log['meta']

    with open(os.path.join(working_directory, 'meta', meta)) as f:
        meta   = json.load(f)
        groups = list(meta['group']) + ['unlabelled']

    info   = dict(output    = dict(prompt = 'output filename', type = click.Path()),
                  values    = dict(prompt = 'group values', type = click.Choice(groups), multiple = True))

    params = dict(train_dir = train_dir)
    params.update(prompt(info))

    log = read_log(os.path.join(working_directory, 'train', params['train_dir'], 'train.log'))
    for key in ['meta', 'feature_selection']:
        params[key] = log[key]

    log = read_log(os.path.join(working_directory, 'train', params['train_dir'], 'params.json'))
    params['num_features'] = log['num_features']

    print_dict('executing "evaluate" with parameters:', params)

    log = read_log(os.path.join(working_directory, 'train', params['train_dir'], 'encoding.json'))
    params['encoder'] = log

    path   = os.path.join(working_directory, 'evaluate', params['train_dir'])
    os.makedirs(path, exist_ok = True)

    params['output'] = os.path.join(path, params['output'])

    if not params['output'].endswith('.csv'):
        params['output'] = params['output'] + '.csv'

    from   genolearn.core.evaluate import evaluate

    data_config = dict(working_dir = working_directory, meta_file = params.pop('meta'))

    params['data_config'] = data_config

    params['model'] = os.path.join(os.path.join('train', params.pop('train_dir')), 'model.pickle')
    os.chdir(working_directory)
    evaluate(**params)
    append(f'evaluate ({params["output"][9:]})') # ignore evaluate in evaluate/*


def __print(name, limit = 5):
    """ Prints various files GenoLearn relies on """

    os.chdir(working_directory)

    if ' ' in name:
        name = name[:name.index(' ')]

    if active is None:
        return print('execute "genolearn config create" first')
    locations = ['meta', 'model']
    if name == 'None':
        for i, location in enumerate(locations):
            loc = location.replace(os.path.expanduser('~'), '~')
            if os.path.exists(location):
                print(f'{loc}\n  - ' + '\n  - '.join(os.listdir(location)))
            else:
                command = 'config model' if i else 'preprocess meta'
                print(f'{loc} (does not exist - execute "genolearn {command}" first)')
            if i < 1:
                print()
    if name == 'config':
        print('config')
        with open('.genolearn') as f:
            log = json.load(f)
            log.pop('history')
            print(json.dumps(log, indent = 4))
    elif name == 'history':
        print('history')
        with open('.genolearn') as f:
            log = json.load(f)
            print('\n'.join(log['history']))
    else:
        flag      = True
        for i, location in enumerate(locations):
            if os.path.exists(location):
                if name in os.listdir(location):
                    file = os.path.join(location, name)
                    with open(file) as f:
                        config = reduce(json.load(f), limit)
                        print(file.replace(os.path.expanduser('~'), '~'))
                        print(json.dumps(config, indent = 4).replace('"', '').replace('...: ...', '...'))
                        flag = False
                        break
            else:
                command = 'config model' if i else 'preprocess meta'
                print(f'{location} (does not exist - execute "genolearn {command}")\n')
        if flag:
            print(f'could not find "{name}" in' + '\n  - '.join([''] + locations))

def _print():
    """ Prints various files GenoLearn relies on """
    func     = lambda command : __print(command)
    commands = dict(history = dict(info = 'history of significant GenoLearn commands', func = func),
                    config  = dict(info = 'current config', func = func))
    if 'meta' in ls:
        commands['meta'] = dict(info = 'metadata information', func = data)

    for subdir in ['meta', 'model']:
        if subdir in ls:
            for file in listdir( subdir):
                commands[file] = dict(info = f'({subdir})', func = func)
    enum(commands, 'print commands', back = menu)

def check_working_directory():
    if working_directory:
        if os.path.exists(working_directory):
            if '.genolearn' in listdir():
                return True
    return False

pre_menu = \
f"""
Genolearn ({__version__}) Command Line Interface

GenoLearn is designed to enable researchers to perform Machine Learning on their genome
sequence data such as fsm-lite or unitig files.

See https://genolearn.readthedocs.io for documentation.
""".strip()

if check_working_directory():
    pre_menu = f'{pre_menu}\n\nWorking directory: {working_directory}'

    
def menu():
    """ Main menu for GenoLearn """

    _feature_importance = select_train_dir('select train_dir for feature-importance command', feature_importance, menu, detect_feature_importance)
    _evaluate           = select_train_dir('select train_dir for evaluate command', evaluate, menu, detect_evaluate)

    options             = {'setup'              : {'info' : 'setup the current directory as the working directory',
                                                   'func' : setup},
                           'clean'              : {'info' : 'deletes all GenoLearn generated files and directories from the current directory',
                                                   'func' : clean},
                           'print'              : {'info' : 'prints various GenoLearn generated files',
                                                   'func' : _print},
                           'preprocess'         : {'info' : 'preprocess data into an easier format for file reading',
                                                   'func' : preprocess},
                           'feature-selection'  : {'info' : 'computes a feature selection method for later training',
                                                   'func' : _feature_selection},
                           'model-config'       : {'info' : 'creates a machine learning model config',
                                                   'func' : model_config},
                           'train'              : {'info' : 'trains a machine learning model',
                                                   'func' : _train},
                           'feature-importance' : {'info' : 'computes the model feature importances',
                                                   'func' : _feature_importance},
                           'evaluate'           : {'info' : 'evaluates a trained model on an input dataset',
                                                   'func' : _evaluate}}

    # set k to not truncate options initially
    k = None

    # set k = 1 if not in working directory or has not executed setup
    if not check_working_directory():
        k = 1
        del options['clean']

    # if a command has not been previously executed truncate options to not include other commands that rely on it.
    else:
        del options['setup']
        for i, command in enumerate(['preprocess meta', 'feature-selection', 'model', 'train'], 3):
            if not check_history(command):
                k = i
                break
        
    enum(options, pre_menu, k = k, back = exit)

def _menu():
    while True:
        menu()
        print('\033c', end = '')