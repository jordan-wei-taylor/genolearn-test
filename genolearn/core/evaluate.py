def core_evaluate(model, data_config, feature_selection, ascending, key, values, output):

    from   genolearn.logger import msg

    from   genolearn.dataloader import DataLoader

    import joblib
    import pandas as pd

    model       = joblib.load(model)
    dataloader  = DataLoader(**data_config)

    if feature_selection and key:
        features = dataloader.load_feature_selection(feature_selection).rank(ascending = ascending)[key]
    else:
        features = None

    X   = dataloader.load_X(*values, features = features)

    df  = pd.DataFrame(index = dataloader.identifiers)
    df['hat'] = dataloader.decode(model.predict(X))
    
    if hasattr(model, 'predict_proba'):
        prob = model.predict_proba(X)
        for i, name in enumerate(dataloader.encoder):
            df[f'P({name})'] = prob[:,i]
    
    df.to_csv(output)

    msg('executed "genolearn evaluate"')
