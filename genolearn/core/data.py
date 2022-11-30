def core_analyse(meta, target, group_by, test, min_count):
    import pandas as pd
    import numpy  as np

    df = pd.read_csv(meta)

    if group_by:
        unique        = sorted(set(df[target]))
        counts        = {}
        groups        = sorted(set(df[group_by]))
        maxu          = max(map(len, unique))
        maxuc         = 0
        for group in groups:
            counts[group] = {}
            for u in unique:
                counts[group][u] = len(df.loc[(df[group_by] == group) & (df[target] == u)])
                maxuc            = max(maxuc, len(f'{counts[group][u]:,d}'))
        
        maxg   = max(map(len, map(str, groups)))
        sumg   = max(map(sum, [counts[group].values() for group in groups]))
        sumgc  = len(f'{sumg:,d}')
        string = []
        for group in groups:
            string.append(f'{str(group):{maxg}s} ({sum(counts[group].values()):{sumgc},d})')
            for u, c in counts[group].items():
                string.append(f'  {u:{maxu}s} : {c:{maxuc},d}')
            string.append('')
        print('\n'.join(string[:-1]))
        if test == []:
            test = ['test']
        if test and df[group_by].isin(test).any():
            targets      = []
            test_mask    = df[group_by].isin(test)
            train_mask   = ~test_mask
            train_counts = {}
            for t in unique:
                train_counts[t] = len(df.loc[train_mask & (df[target] == t)])           
                if train_counts[t] >= min_count:
                    targets.append(t)
            if len(targets) < len(unique):
                print(f'\nsuggested target subset list for training (count >= {min_count})')
                print(','.join(targets))
        return counts
    else:

        unique, count = np.unique(df[target], return_counts = True)

        maxu = max(map(len, unique))
        maxc = max(map(len, [f'{c:,d}' for c in count]))
        for u, c in zip(unique, count):
            print(f'{u:{maxu}s} : {c:{maxc},d}')

        return dict(zip(unique, count))

def core_head(meta, num):
    import pandas as pd
    
    df      = pd.read_csv(meta)
    array   = df.iloc[:num].T.reset_index().T.values.astype(str)
    maxlen  = [max(map(len, a)) for a in array.T]
    print(' | '.join(f'\033[1m{val:{m}s}\033[0m' for val, m in zip(array[0], maxlen)))
    print(' + '.join('-' * m for m in maxlen))
    print('\n'.join(' | '.join([f'{val:{m}s}' for val, m in zip(row, maxlen)]) for row in array[1:]))

def core_tail(meta, num):
    import pandas as pd
    
    df      = pd.read_csv(meta)
    array   = df.iloc[-num:].T.reset_index().T.values.astype(str)
    maxlen  = [max(map(len, a)) for a in array.T]
    print(' | '.join(f'\033[1m{val:{m}s}\033[0m' for val, m in zip(array[0], maxlen)))
    print(' + '.join('-' * m for m in maxlen))
    print('\n'.join(' | '.join([f'{val:{m}s}' for val, m in zip(row, maxlen)]) for row in array[1:]))

def core_train_test_split(meta, ptrain, random_state):

    import numpy  as np
    import pandas as pd

    df = pd.read_csv(meta)

    if random_state:
        np.random.seed(int(random_state))

    n  = len(df)
    ix = np.random.permutation(n)

    nr = int(ptrain * n + 0.5)

    df.loc[:      , 'train_test'] = 'test'
    df.loc[ix[:nr], 'train_test'] = 'train'

    df.to_csv(meta, index = False, header = True)
