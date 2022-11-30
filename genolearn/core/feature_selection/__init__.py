from   genolearn.logger import msg

import numpy as np

def base_feature_selection(dataloader, init, inner_loop, outer_loop, values, force_dense = False, force_sparse = False, aggregate = False):
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
        
        values : list, *default=[]*
            Set of values to use when looping over the generator method of the ``DataLoader`` object.

        force_dense : bool, *default=False*
            Identify if computations should be forced to dense computations.

        force_dense : bool, *default=False*
            Identify if computations should be forced to sparse computations.

        aggregate : bool, *default=False*
            Performs a single outer loop instead of incremental loop using the values list.
        
    Notes
    -----

    If it is intended to execute the ``inner_loop`` function on all examplars and the ``outer_loop`` function once at the end, ``values`` should be set such that it evaluates to ``False``.
    """
    ret          = {}
    args, kwargs = init(dataloader)
    if values:
        if aggregate:
            values = dataloader.meta[dataloader.identifier][np.isin(dataloader.meta[dataloader.group], values)]
            for i, (x, label) in enumerate(dataloader.generator(*values, force_dense = force_dense, force_sparse = force_sparse), 1):
                inner_loop(ret, i, x, label, 'all', *args, **kwargs)
            outer_loop(ret, i, 'all', *args, **kwargs)
        else:
            for value in values:
                for i, (x, label) in enumerate(dataloader.generator(value, force_dense = force_dense, force_sparse = force_sparse), 1):
                    inner_loop(ret, i, x, label, value, *args, **kwargs)
                outer_loop(ret, i, value, *args, **kwargs)
    else:
        values = dataloader.meta[dataloader.identifier]
        for i, (x, label) in enumerate(dataloader.generator(*values, force_dense = force_dense, force_sparse = force_sparse), 1):
            inner_loop(ret, i, x, label, 'all', *args, **kwargs)
        outer_loop(ret, i, 'all', *args, **kwargs)
    return ret

def core_feature_selection(name, preprocess_dir, meta_path, identifier, target, group, values, method, aggregate, log, sparse):

    from   genolearn.logger  import msg, Writing
    from   genolearn.dataloader import DataLoader
    from   genolearn         import utils

    import importlib

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

    dataloader = DataLoader(preprocess_dir, meta_path, identifier, target, group, sparse)
    
    os.makedirs(os.path.join(preprocess_dir, 'feature-selection'), exist_ok = True)

    if f'{method}' == 'fisher':

        module       = importlib.import_module(f'genolearn.core.feature_selection.fisher')

    elif f'{method}.py' in os.listdir():

        module       = importlib.import_module(method)

    else:
        raise Exception(f'"{method}.py" not in current directory!')

    variables    = dir(module)
    save_path    = f'{preprocess_dir}/feature-selection/{name}'
    
    for name in ['init', 'inner_loop', 'outer_loop']:
        assert name in variables
        
    force_sparse = module.force_sparse if 'force_sparse' in variables else False
    force_dense  = module.force_dense  if 'force_dense'  in variables else False

    scores       = base_feature_selection(dataloader, module.init, module.inner_loop, module.outer_loop, values, force_dense, force_sparse, aggregate)

    with Writing(save_path, inline = True):
        np.savez_compressed(save_path, **scores)

    utils.create_log(method if log is None else log, f'{preprocess_dir}/feature-selection')

    msg(f'executed "genolearn feature-selection"')
