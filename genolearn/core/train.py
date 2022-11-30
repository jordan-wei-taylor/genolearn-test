
def core_train(path, model, data_config, model_config, train, test, K, order, order_key, ascending, min_count, target_subset, metric, mean_func, overwrite, flag = True):
    
    params = locals().copy()

    import os
    
    params.pop('flag')
    path   = params['path'] = os.path.abspath(path)
    
    from   genolearn.logger import print_dict

    command = (' ' if flag else '.').join(('genolearn', 'train'))

    from genolearn.utils                 import create_log
    from genolearn.models.classification import get_model
    from genolearn.models                import grid_predictions
    from genolearn.dataloader            import DataLoader
    from genolearn.logger                import msg, Writing
    
    import warnings
    import shutil
    import numpy as np
    import os
    import json
    import pickle
    
    if os.path.exists(path):
        if overwrite:
            shutil.rmtree(path)
        else:
            return print(f'"{path}" already exists! Add the "--overwrite" flag to overwrite.')

    os.makedirs(path)

    warnings.simplefilter("ignore")
    os.environ["PYTHONWARNINGS"] = "ignore"


    # data_config, model_config = map(check_config, (data_config, model_config))

    # with open(model_config) as f:
    #     model_config = json.load(model_config)


    # print_dict('executing "train.py" with parameters', params)

    kwargs     = {key : val for key, val in model_config.items() if isinstance(val, list)}
    common     = {key : val for key, val in model_config.items() if key not in kwargs}

    if train[0] == 'train':
        data_config['group'] = 'train_test'

    dataloader = DataLoader(**data_config)
    
    if order and order_key:
        selection = dataloader.load_feature_selection(order).rank(ascending = ascending)[order_key]

    Model   = get_model(model)
    
    outputs, params = grid_predictions(dataloader, train, test, Model, K, selection, common, min_count, target_subset, metric, mean_func, **kwargs)
    
    params['model'] = model
    
    model, predict, *probs = outputs.pop('best')

    target  = outputs['target']

    npz     = os.path.join(path, 'results.npz')
    pkl     = os.path.join(path, 'model.pickle')
    csv     = os.path.join(path, 'predictions.csv')
    js      = os.path.join(path, 'params.json')
    fs      = os.path.join(path, 'feature-selection.json')

    dump    = np.c_[outputs['identifiers'], np.array([target, predict]).T]
    headers = ['identifier', 'target', 'predict']

    if probs:
        for i, label in enumerate(dataloader.encoder):
            dump = np.c_[dump, probs[0][:,i].astype(str)]
            headers.append(label)

    dump = ','.join(headers) + '\n' + '\n'.join(','.join(row) for row in dump)

    with open(csv, 'w') as f:
        f.write(dump)

    with Writing(npz, inline = True):
        np.savez_compressed(npz, **outputs)

    with Writing(pkl, inline = True):
        with open(pkl, 'wb') as f:
            pickle.dump(model, f)

    with Writing(js, inline = True):
        with open(js, 'w') as f:
            f.write(json.dumps(params, indent = 4))
        
    with Writing(fs, inline = True):
        with open(fs, 'w') as f:
            print(json.dumps(dict(feature_selection = order, key = order_key, ascending = ascending), indent = 4), file = f)

    create_log('train', path)

    msg(f'executed "{command}"')
