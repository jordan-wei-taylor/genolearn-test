def core_combine(preprocess_dir, data, batch_size, n_processes, debug, verbose):
    """
    Preprocess a gunzip (gz) compressed text file containing genome sequence data of the following sparse format

        \b
        sequence_1 | identifier_{1,1}:count_{1,1} identifier_{1,1}:count_{2,1} ...
        sequence_2 | identifier_{2,1}:count_{2,1} identifier_{2,1}:count_{2,2} ...
        ...

    and combines the preprocessed data with the `preprocess-dir` directory set in the \033[1mactive config\033[0m file.
    This relies on the user to have previously executed `genolearn preprocess`.

    See https://genolearn.readthedocs.io/tutorial/combine for more details.
    """

    from   genolearn.logger       import msg, print_dict
    from   genolearn.core.preprocess import gather_counts, gather_feature, gather_samples, init, add, get_dtype
    from   genolearn              import utils
    from   pathos.multiprocessing import cpu_count, Pool

    import numpy  as np

    import resource

    import json
    import gzip
    import re
    import os

    assert os.path.exists(preprocess_dir)

    limit = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    resource.setrlimit(resource.RLIMIT_NOFILE, (limit, limit))

    with gzip.open(os.path.join(preprocess_dir, 'features.txt.gz')) as gz:
        feature_set = gz.read().decode().split()
        
    n_processes    = cpu_count() if n_processes == 'auto' else int(n_processes)

    gather_feature = lambda line : line[:line.index(' ')]
    gather_samples = lambda line : re.findall(r'[\w]+(?=:)', line)
    gather_counts  = lambda line : re.findall(r'(?<=:)[\w]+', line)

    first_run  = True
    features   = []
    exceptions = set()
    C          = 0
    hi         = 0
    unique     = set()

    if data.endswith('.gz'):
        _open  = gzip.GzipFile
        decode = lambda line : line.decode()
    else:
        _open  = open
        decode = lambda line : line

    with _open(data) as gz:
       
        os.chdir(preprocess_dir)
        os.mkdir('temp')
        
        files = {}

        while True:
           
            gz.seek(0)

            skip    = False
            skipped = False
            c       = 0
           
            for m, line in enumerate(gz, 1):

                line    = decode(line)

                srrs    = gather_samples(line)
                counts  = gather_counts(line)

                if first_run:
                    features.append(gather_feature(line))
                    hi      = max(hi, *map(int, counts))
                    unique |= set(srrs)

                for SRR, count in zip(srrs, counts):
                    if SRR not in exceptions:
                        if SRR not in files:
                            if skip:
                                skipped = True
                                continue
                            files[SRR] = init(SRR)
                            c         += 1
                            C         += 1
                            skip = c == batch_size
                        add(files[SRR], m - 1, count)

                if m % verbose == 0:
                    msg(f'{C:10,d} {m:10,d}')
               
                if m == debug:
                    break
           
            if m % verbose:
                msg(f'{C:10,d} {m:10,d}')

            for f in files.values():
                f.close()

            if first_run:
                first_run = False

                n         = len(unique)
                d_dtype   = get_dtype(hi)
                c_dtype   = get_dtype(m)
                
                with open('meta.json') as f:
                    meta = json.load(f)
                    n    = meta['n'] + n
                    m    = meta['m']
                    hi   = max(meta['max'], hi)

                f = init('meta', None, 'json')
                json.dump({'n' : n, 'm' : m, 'max' : hi}, f)
                f.close()
                
                feature_overlap = np.nonzero(np.isin(features, feature_set, assume_unique = True))[0]

                def to_sparse(npz, c, d):
                    np.savez_compressed(os.path.join('sparse', npz), col = c.astype(c_dtype), data = d.astype(d_dtype))

                def to_dense(npz, c, d):
                    arr = np.zeros(m, dtype = d.dtype)
                    arr[c] = d
                    np.savez_compressed(os.path.join('dense', npz), arr = arr)
               
                def convert(file):
                    txt  = os.path.join('temp', f'{file}.txt')
                    npz  = f'{file}.npz'
                    c, d = np.loadtxt(txt, dtype = c_dtype).T
                    mask = np.nonzero(np.isin(c, feature_overlap, assume_unique = True))[0]
                    for function in functions:
                        function(npz, c[mask], d[mask])

                    os.remove(txt)

                functions = []
                if 'sparse' in os.listdir():
                    functions.append(to_sparse)

                if 'dense' in os.listdir():
                    functions.append(to_dense)
           
            with Pool(n_processes) as pool:
                pool.map(convert, list(files))

            if not skipped:
                break

            exceptions |= set(files)

            if len(files) < batch_size:
                break

            files.clear()

        os.rmdir('temp')

        utils.create_log('combine')

    msg(f'executed "genolearn combine"')
