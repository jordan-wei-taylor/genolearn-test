from setuptools import setup
from genolearn  import __version__

url = "https://github.com/jordan-wei-taylor/genolearn"

def read(path):
    with open(path, encoding = 'utf-8') as f:
        return f.read()

setup(
    name             = "genolearn",
    version          = __version__,
    author           = "Jordan Taylor",
    author_email     = "jt2006@bath.ac.uk",
    description      = "A machine learning toolkit for genome sequence data",
    long_description = read('README.md'),
    license          = read('LICENSE'),
    package          = ['genolearn'],
    url              = url,
    project_urls     = {"Bug Tracker": f"{url}/issues"},
    classifiers      = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires  = ">=3.10",
    install_requires = [
        'click>=8.1.3',        # cli
        'numpy>=1.22.3',       # core
        'pandas>=1.4.2'        # core
        'pathos>=0.3.0',       # parallelisation
        'psutil>=5.9.0',       # logging RAM
        'scikit-learn>=1.1.2', # core
        'scipy>=1.8.0',        # sparse arrays
    ],
    entry_points     = '''
        [console_scripts]
        genolearn=genolearn.cli:cli
    ''',
    
)