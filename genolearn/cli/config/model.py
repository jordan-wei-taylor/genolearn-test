from   genolearn.cli.config.classification import classification
from   genolearn.cli.config.regression     import regression

import click

@click.group()
def model():
    ...

model.add_command(classification)
model.add_command(regression)