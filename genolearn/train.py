def __check(config):
    import json
    import re

    if config:
        if '{' in config:
            raw    = config
            while 'range' in raw:
                nums = re.findall('(?<=range\()[0-9, ]+', raw)[0].replace(',', ' ').split()
                raw  = re.sub('range\([0-9, ]+\)', str(list(range(*map(int, nums)))), raw, 1)
            config = json.loads(raw)
        else:
            with open(config) as f:
                config = json.load(f)
                if isinstance(config, str):
                    config = json.loads(config)
    else:
        config = {}

    return config

def main(path, model, data_config, model_config, train, test, K, order, order_key, ascending, min_count, overwrite):
    
    params = {k : v for k, v in locals().items() if not k.startswith('_')}

    from genolearn.utils                 import create_log, get_basename
    from genolearn.models.classification import get_model
    from genolearn.models                import grid_predictions
    from genolearn.dataloader            import DataLoader
    from genolearn.logger                import msg, print_dict
    
    import warnings
    import shutil
    import numpy as np
    import os
    
    if overwrite:
        if os.path.exists(path):
            shutil.rmtree(path)

    os.makedirs(path)

    warnings.simplefilter("ignore")
    os.environ["PYTHONWARNINGS"] = "ignore"

    print_dict('executing "train.py" with parameters', params)

    data_config, model_config = map(__check, (data_config, model_config))

    kwargs     = {key : val for key, val in model_config.items() if isinstance(val, list)}
    common     = {key : val for key, val in model_config.items() if key not in kwargs}

    dataloader = DataLoader(**data_config)
    
    if order and order_key:
        name  = order
        order = dataloader.load_feature_selection(order).rank(ascending = ascending)[order_key]

    Model = get_model(model)
    
    hats, times = grid_predictions(dataloader, train, test, Model, K, order, common, min_count, **kwargs)

    np.savez_compressed(os.path.join(path, 'results.npz'), hats = hats, times = times, K = K)

    create_log(path)

    msg('executed "train.py"')

    
if __name__ == '__main__':

    from   genolearn.models import classification

    import argparse
    
    parser = argparse.ArgumentParser('genolearn.train')

    parser.add_argument('path')
    parser.add_argument('model', choices = classification.valid_models)
    parser.add_argument('data_config')
    parser.add_argument('model_config')
    parser.add_argument('-train', nargs = '+')
    parser.add_argument('-test', nargs = '*')
    parser.add_argument('-K', nargs = '+', type = int)
    parser.add_argument('-order', default = None)
    parser.add_argument('-order_key', default = None)
    parser.add_argument('-ascending', default = False, type = bool)
    parser.add_argument('-min_count', default = 0, type = int)
    parser.add_argument('--overwrite', action = 'store_true')

    args = parser.parse_args()

    main(**dict(args._get_kwargs()))

    


