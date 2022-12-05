from   genolearn.cli.model.classification import classification
from   genolearn.cli.model.regression     import regression

import click

@click.group()
def model():
    """
    creates a model config to later use for training.
    """
    ...

model.add_command(classification)
model.add_command(regression)