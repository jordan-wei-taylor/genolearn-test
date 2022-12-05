##############
GenoLearn
##############

GenoLearn is a machine learning pipeline designed for biologists working with genome sequence data looking to build a predictive model or identify important patterns.

Installation
############

Ensure you have a minimum Python3 version of 3.10.

Pip
====================

Stable Install

Ubuntu / Mac OS
---------------

.. code-block:: sh

    # set a virtual environment if not already done so
    python3 -m venv env

    # activate virtual environment
    source env/bin/activate

    # install GenoLearn
    pip install genolearn


Windows
-------

.. code-block:: sh

    # set a virtual environment if not already done so
    python3 -m venv env

    # activate virtual environment
    ./env/Scripts/activate

    # install GenoLearn
    pip install genolearn


Conda
======================

Stable Install

.. code-block:: sh

    # make sure my channel and conda-forge are your first channels for installation
    conda config --prepend channels conda-forge --prepend channels jordan-wei-taylor

    # create a new conda environment env with genolearn installed
    conda create --name env genolearn

    # activate environment to use genolearn
    conda activate env


.. code-block:: sh

    pip install git+https://github.com/jordan-wei-taylor/genolearn.git

.. toctree::
    :hidden:
    :titlesonly:
    
    Installation <self>
    tutorial
    glossary

.. .. toctree::
..     :hidden:
..     :titlesonly:
..     :caption: Usage

..     usage/preprocess
..     usage/feature-selection
..     usage/train
..     usage/evaluate

.. .. toctree::
..     :hidden:
..     :titlesonly:
..     :caption: Background

..     background/overview
..     background/preprocessing

.. .. toctree::
..     :hidden:

..     background/feature-selection/index

.. .. toctree::
..     :hidden:

..     background/data-loader
..     background/metrics
..     background/models
    
.. .. toctree::
..     :hidden:

..     implementation/feature-importance/index
    
.. toctree::
    :hidden:
    :titlesonly:
    :caption: Usage

    data <usage/data>
    dir <usage/dir>
    evaluate <usage/evaluate>
    feature-importance <usage/feature-importance>
    feature-selection <usage/feature-selection>
    model <usage/model/index>
    next <usage/next>
    preprocess <usage/preprocess>
    print <usage/print>
    train <usage/train>
    
    

.. .. toctree::
..     :hidden:
..     :caption: Python Documentation

..     genolearn/index

.. toctree::
    :hidden:
    :maxdepth: 4
    :caption: Case Studies
    :titlesonly:

    case-study/predicting-strain-origin-from-k-mer-counts/index
