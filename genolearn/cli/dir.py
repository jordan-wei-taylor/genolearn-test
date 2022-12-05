import click
import os

@click.group()
def dir():
    """
    sets or gets the working directory.
    """
    ...

@dir.command()
@click.argument('path', type = click.Path())
def set(path):
    """
    sets the current working directory.
    """
    path = os.path.abspath(path)
    if not os.path.exists(path):
        os.mkdir(path)
    if '.history' not in os.listdir(path):
        with open(os.path.join(path, '.history'), 'w') as f:
            print('', end = '', file = f)
    if '.config' not in os.listdir(path):
        from genolearn.core.dir import create_config
        data_dir = os.path.abspath(click.prompt(f"{'data_dir':14s}", type = click.Path()))

        if not os.path.exists(data_dir):
            return print(f'"{data_dir}" not a valid path!')

        meta     = click.prompt(f"{'metadata file':14s}", type = click.Choice(os.listdir(data_dir)), show_choices = False)
        meta     = os.path.join(data_dir, meta)

        create_config(path, data_dir, meta)

    with open(__file__.replace('cli/dir.py', 'wd'), 'w') as f:
        f.write(path)

@dir.command()
def get():
    """
    prints the current working directory.
    """
    from genolearn import wd
    print(wd)