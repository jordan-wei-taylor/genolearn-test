def _load_df(meta):
    import pandas as pd
    import json

    with open(meta) as f:
        meta = json.load(f)

    g  = []
    t  = []
    s  = []
    for identifier in meta['identifiers']:
        t.append(meta['search'][identifier])

        for group, identifiers in meta['group'].items():
            if identifier in identifiers:
                g.append(group)
                continue

        s.append('train' if any(identifier in meta['group'][group] for group in meta['Train']) else 'val')

    df = pd.DataFrame()
    df['identifier'] = meta['identifiers']
    df['group']      = g
    df['target']     = t
    df['train/val']  = s
    df.index         += 1

    return df
    
def _count(meta):
    import pandas as pd
    df    = _load_df(meta)
    count = pd.DataFrame(dtype = int)
    for target in sorted(set(df['target'])):
        for group in sorted(set(df['group'])):
            count.loc[target, group] = ((df['target'] == target) & (df['group'] == group)).sum()

    if 'train' in count.columns:
        count.columns  = [column.title() for column in count.columns]
    else:
        count['Train'] = count[list(meta['Train'])].sum(axis = 1)
        count['Val'  ] = count[list(meta['Val'  ])].sum(axis = 1)

    count['Total'] = count['Train'] + count['Val']
    count.loc['Total'] = count.sum(axis = 0)

    return count

def _print(func):
    def inner(meta):
        print(f'genolearn command : print metadata {func.__name__}')
        print(f'metadata          : {meta.split("/")[-1]}', '\n')
        print(func(meta))
    return inner
    
@_print    
def count(meta):
    df = _count(meta).applymap(int)
    return df

@_print   
def proportion(meta):
    df = _count(meta)
    df.iloc[:-1] /= df.iloc[:-1].sum(axis = 0)
    df.iloc[-1]   = df.iloc[-1] / df.iloc[-1,-1]
    df *= 100
    return df.round(0).applymap(int)

@_print   
def head(meta, num = 10):
    df = _load_df(meta)
    if (df['group'] == df['train/val']).all():
        df.drop('group', axis = 1, inplace = True)
    return df.head(num)
    
@_print   
def tail(meta, num = 10):
    df = _load_df(meta)
    if (df['group'] == df['train/val']).all():
        df.drop('group', axis = 1, inplace = True)
    return df.tail(num)

@_print   
def sample(meta, num = 10):
    df = _load_df(meta)
    if (df['group'] == df['train/val']).all():
        df.drop('group', axis = 1, inplace = True)
    return df.sample(num)
