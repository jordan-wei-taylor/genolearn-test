"""
genolearn cli
"""


from   genolearn.cli.data               import data
from   genolearn.cli.evaluate           import evaluate
from   genolearn.cli.feature_importance import feature_importance
from   genolearn.cli.feature_selection  import feature_selection
from   genolearn.cli.preprocess         import preprocess
from   genolearn.cli.train              import train
from   genolearn.cli.config             import config

from   genolearn import __version__

from   shutil import get_terminal_size
import click

click.formatting.FORCED_WIDTH = min(get_terminal_size().columns - 10, 110)

@click.group()
@click.version_option(__version__, message = 'GenoLearn %(version)s')
def cli():
    """ 
    GenoLearn Command Line Interface

    \b\n

    GenoLearn is designed to enable researchers to perform Machine Learning on their genome sequence data such 
    as fsm-lite or unitig files.
    
    See https://genolearn.readthedocs.io for the most up-to-date documentation.
    """
    ...

cli.add_command(config)
cli.add_command(data)
cli.add_command(evaluate)
cli.add_command(feature_importance)
cli.add_command(feature_selection)
cli.add_command(preprocess)
cli.add_command(train)