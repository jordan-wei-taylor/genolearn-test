import numpy as np
import os
import re

clean_sample   = lambda sample : sample[sample.index('/') + 1:] if '/' in sample else sample
gather_feature = lambda line : line[:line.index(' ')]
gather_samples = lambda line : list(map(clean_sample, re.findall(r'(?<= )[^: ]+(?=:)', line)))
gather_counts  = lambda line : re.findall(r'(?<=:)[0-9]+', line)

def get_dtype(val):
    dtypes = [np.uint8, np.uint16, np.uint32, np.uint64]
    for dtype in dtypes:
        info = np.iinfo(dtype)
        if info.min <= val <= info.max:
            return dtype
    raise Exception()

def init(file, subpath = 'temp', ext = 'txt'):
    path = os.path.join(subpath, f'{file}.{ext}') if subpath else f'{file}.{ext}'
    if os.path.exists(path):
        os.remove(path)
    return open(path, 'a')

def add(object, i, count):
    object.write(f'{i} {count}\n')
    
def core_preprocess(preprocess_dir, data, batch_size, n_processes, sparse, dense, debug, verbose):
    """
    Preprocess a gunzip (gz) compressed text file containing genome sequence data of the following sparse format

        \b
        sequence_1 | identifier_{1,1}:count_{1,1} identifier_{1,1}:count_{2,1} ...
        sequence_2 | identifier_{2,1}:count_{2,1} identifier_{2,1}:count_{2,2} ...
        ...

    into a directory of .npz files, a list of all the features, and some meta information containing number of 
    identifiers, sequences, and non-zero counts.

    It is expected that the parameter `data` is in the `data-dir` directory set in the \033[1mactive config\033[0m file.
    See https://genolearn.readthedocs.io/tutorial/config for more details.

    \b\n
    Example Usage

    \b
    # reduce ram usage by setting a batch size (will increase preprocess time)
    >>> genolearn preprocess file.gz --batch-size 128
    """

    from   genolearn.logger       import msg, Waiting, print_dict
    from   genolearn              import utils

    from   pathos.multiprocessing import cpu_count, Pool
    from   shutil                 import rmtree

    import resource

    import json
    import gzip

    try:
        # remove number of files open restriction
        limit = min(resource.getrlimit(resource.RLIMIT_NOFILE)[1], batch_size)
        resource.setrlimit(resource.RLIMIT_NOFILE, (limit, limit))
    except:
        msg(f'Attempting to open to many files! Try reducing the number to 128 with\ngenolearn preprocess {data} --batch-size 128')
        return 

    n_processes    = cpu_count() if n_processes == 'auto' else int(n_processes)
    
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
        
        if os.path.exists(preprocess_dir):
            rmtree(preprocess_dir)

        os.mkdir(preprocess_dir)
        os.chdir(preprocess_dir)

        os.mkdir('temp')
        os.mkdir('feature-selection')

        files = {}

        while True:
           
            gz.seek(0)

            skip    = False
            skipped = False
            c       = 0
           
            for m, line in enumerate(gz, 1):

                line   = decode(line)

                srrs   = gather_samples(line)
                counts = gather_counts(line)

                if first_run:
                    features.append(gather_feature(line))
                    hi      = max(hi, *map(int, counts))
                    unique |= set(srrs)

                for SRR, count in zip(srrs, counts):
                    if SRR not in exceptions:
                        if SRR not in files and c < batch_size:
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

                d_dtype   = get_dtype(hi)
                c_dtype   = get_dtype(m)

                with Waiting('compressing', 'compressed', 'features.txt.gz'):
                    with gzip.open('features.txt.gz', 'wb') as g:
                        g.write(' '.join(features).encode())
                
                features.clear()

                f = init('meta', None, 'json')
                json.dump({'n' : len(unique), 'm' : m, 'max' : hi}, f)
                f.close()
               
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

                    for function in functions:
                        function(npz, c, d)

                    os.remove(txt)

                functions = []
                if sparse:
                    functions.append(to_sparse)
                    os.mkdir('sparse')

                if dense:
                    functions.append(to_dense)
                    os.mkdir('dense')
           
            with Pool(n_processes) as pool:
                pool.map(convert, list(files))

            if not skipped:
                break

            exceptions |= set(files)

            if len(files) < batch_size:
                break

            files.clear()

        os.rmdir('temp')

        utils.create_log('preprocess')
    

    msg(f'executed "genolearn preprocess"')