"""
.. autosummary::

    create
    list
    get
    activate
    active
    remove

"""

from   genolearn.cli.config.model import model

from   genolearn.core.data        import core_train_test_split
import genolearn.core.config

import click
import os


@click.group()
def config():
    """
    configure static data used by GenoLearn.
    """
    pass

@config.command()
@click.argument('name')
def get(name):
    """ prints configuration file. """
    genolearn.core.config.get(name)

@config.command()
def create():
    """
    creates a config file in ~/.genolearn/configs.
    
    \b
    prompted information
        config name              : name of output configuration file
        preprocess dir           : output preprocess directory
        data dir                 : data directory containing metadata and genome sequence data
        metadata file            : metadata file expected to be in a standard csv format
        identifier               : column within metadata denoting the unique identifiers
        target                   : column within metadata denoting the metadata target of interest
        group                    : column within metadata denoting how to later split the data into train / test
        feature selection method : method to use to reduce the dimensionality of the dataset
    """
    name = click.prompt(f"{'config name':33s}")
    preprocess_dir = click.prompt(f"{'preprocess-dir':33}", type = click.Path())
    data_dir = click.prompt(f"{'data-dir':33s}", type = click.Path())
    meta = click.prompt(f"{'metadata file ':33s}", type = click.Choice(os.listdir(data_dir)), show_choices = False)
    with open(os.path.join(data_dir, meta)) as f:
        columns = f.readline().strip().split(',')
    identifier = click.prompt(f"{'identifier column in metadata':33s}", type = click.Choice(columns), show_choices = False)
    columns.pop(columns.index(identifier))
    target = click.prompt(f"{'target column in metadata':33s}", type = click.Choice(columns), show_choices = False)
    columns.pop(columns.index(target))
    columns.append('auto')
    group = click.prompt(f"{'group column in meta data':26s}", default = 'auto', type = click.Choice(columns), show_choices = False)
    feature_selection = click.prompt(f"{'feature-selection method':24s}", default = 'fisher')
    if group == 'auto':
        group = 'train_test'
        genolearn.core.config.create(name, preprocess_dir, data_dir, meta, identifier, target, group, feature_selection)
        core_train_test_split(os.path.join(data_dir, meta), 0.75, None)
    else:
        genolearn.core.config.create(name, preprocess_dir, data_dir, meta, identifier, target, group, feature_selection)
    genolearn.core.config.activate(name)

@config.command()
@click.option('-f', '--full', default = False, is_flag = True, help = 'prints the contents of each config file')
def list(full):
    """ lists all config files in ~/.genolearn/configs. 
    
    if the --full flag is provided, prints the contents of each config file."""
    genolearn.core.config.list_(full)

@config.command()
@click.argument('name', type = click.Choice(os.listdir(os.path.expanduser('~/.genolearn/configs'))))
def activate(name):
    """ sets active config file. 
    
    note that the only valid NAME values are the filenames detected in ~/.genolearn/configs/ which are
    generated from executing genolearn config create."""
    genolearn.core.config.activate(name)

@config.command()
def active():
    """ prints active config file """
    genolearn.core.config.active()

@config.command()
@click.argument('name')
def remove(name):
    """
    removes a config file. 
    
    if NAME = 'all', removes all config files
    """
    if name == 'all':
        for name in os.listdir(genolearn.core.config.config_path):
            genolearn.core.config.remove(name)
        if os.path.exists(os.path.expanduser('~/.genolearn/active')):
            os.remove(os.path.expanduser('~/.genolearn/active'))
    else:
        genolearn.core.config.remove(name)

config.add_command(model)