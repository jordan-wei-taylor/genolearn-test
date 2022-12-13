from   genolearn.logger import msg, Waiting

import numpy as np

def base_feature_selection(method, dataloader, init, loop, post, force_dense = False, force_sparse = False):
    """
    base feature selection function

    Parameters
    ----------
        dataloader : str
            genolearn.dataloader.DataLoader object.

        init : str
            Initialise function to generate and the associated ``args`` and ``kwargs`` for ``inner_loop`` and ``outer_loop`` functions.

        inner_loop : str
            Inner loop function to be executed on a given (x, y) pair.
        
        outer_loop : str
            Outer loop function to be executed for each value in ``values``.

        force_dense : bool, *default=False*
            Identify if computations should be forced to dense computations.

        force_dense : bool, *default=False*
            Identify if computations should be forced to sparse computations.
    """
    args, kwargs = init(dataloader)
    n            = sum(map(len, (dataloader.meta['group'][group] for group in dataloader.meta['Train'])))
    for i, (x, label) in enumerate(dataloader.generator('Train', force_dense = force_dense, force_sparse = force_sparse), 1):
        msg(f'{method} : {i:,d} of {n:,d}', inline = True)
        loop(i, x, label, 'Train', *args, **kwargs)
    
    with Waiting(f'{method} : {i:,d} (computing fisher)', f'{method} : {i:,d} (completed)'):
        ret = post(i, 'Train', *args, **kwargs)

    return ret

def feature_selection(name, meta, method, module, log):

    from   genolearn.logger  import msg, Writing
    from   genolearn.dataloader import DataLoader
    from   genolearn         import utils, working_directory

    import numpy  as np
    import os

    # parser = ArgumentParser(description = description, formatter_class = RawTextHelpFormatter)

    # parser.add_argument('output',     help = 'output file name')
    # parser.add_argument('path'  ,     help = 'path to preprocessed directory')
    # parser.add_argument('meta_path',  help = 'path to meta file')
    # parser.add_argument('identifier', help = 'column of meta data denoting the identifier')
    # parser.add_argument('target',     help = 'column of meta data denoting the target')
    # parser.add_argument('values', nargs = '*', help = 'incremental identifiers (or groups) to perform feature selection on')
    # parser.add_argument('-group', default = None, help = 'column of meta data denoting the grouping of labels')
    # parser.add_argument('-method', default = 'fisher', help = 'either "fisher" for built in Fisher Score or a module name (see example)')
    # parser.add_argument('-aggregate', default = False, action = 'store_true', help = 'removes incremental loop and performs a single outer loop')
    # parser.add_argument('-log', default = None, help = 'log file name')
    # parser.add_argument('--sparse', default = False, action = 'store_true', help = 'if sparse loading of data is preferred')

    dataloader = DataLoader(meta, working_directory)
    
    os.makedirs('feature-selection', exist_ok = True)

    variables  = {}
    with open(os.path.expanduser(module)) as f:
        exec(f.read(), {}, variables)

    save_path    = os.path.join('feature-selection', name)
    funcs        = ['init', 'loop', 'post']
    extra        = ['force_dense', 'force_sparse']

    for name in funcs:
        assert name in variables
        
    params       = {func : variables.get(func) for func in funcs + extra}

    scores       = base_feature_selection(method, dataloader, **params)

    with Writing(save_path, inline = True):
        np.savez_compressed(save_path, scores)
        os.rename(f'{save_path}.npz', save_path)

    utils.create_log(method if log is None else log, 'feature-selection')

    msg(f'executed "genolearn feature-selection"')
