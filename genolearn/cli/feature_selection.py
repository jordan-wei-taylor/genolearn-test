import click 

@click.command(name = 'feature-selection')
def feature_selection():
    """
    execute feature selection (fisher by default).

    \b
    prompted information
        name      : output file name
        meta      : preprocessed metadata file
        method    : feature selection method
    """
    from   genolearn import get_active, wd
    from   genolearn.core.feature_selection import feature_selection
    from   genolearn.utils import prompt, append

    import os

    active = get_active()
    if active is not None:
        if not os.path.exists(wd):
            return print('execute "genolearn preprocess sequence" first')
        if 'meta' not in os.listdir(wd):
            return print('execute "genolearn preprocess meta" first')
    path = os.path.join(wd, 'meta')
    info = dict(name   = dict(default = 'fisher', type = click.STRING),
                meta   = dict(type = click.Choice(os.listdir(path))),
                method = dict(default = 'fisher', type = click.STRING))

    params = prompt(info)


    params['log'] = f"{params['name']}.log"

    from   genolearn.logger import print_dict

    print_dict('executing "feature-selection" with parameters:', params)

    params['working_dir'] = wd

    feature_selection(**params)
    append(f'feature-selection ({params["name"]})')
