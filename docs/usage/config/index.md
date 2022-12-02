GenoLearn Config
################

This section documents the usage of the ``config`` command of GenoLearn. For configuration of models, refer to `genolearn config model <model/index.html>`_.

.. code-block:: bash

    genolearn config SUBCOMMAND


Configure static data used by GenoLearn.

Create
======

.. code-block:: bash

    genolearn config create


Creates a config file in ~/.genolearn/configs

.. code-block:: text

    prompted information
        config name              : name of output configuration file
        preprocess dir           : output preprocess directory
        data dir                 : data directory containing metadata and genome sequence data
        metadata file            : metadata file expected to be in a standard csv format
        identifier               : column within metadata denoting the unique identifiers
        target                   : column within metadata denoting the metadata target of interest
        group                    : column within metadata denoting how to later split the data into train / test
        feature selection method : method to use to reduce the dimensionality of the dataset


List
====

.. code-block:: bash

    genolearn config list [OPTIONS]

Lists all config files in ~/.genolearn/configs.

If the ``-f`` of ``–full`` flag is provided, prints the contents of each config file.

.. rubric:: OPTIONS
.. code-block:: bash

    -f, --full : Prints the contents of each config file


Get
===

.. code-block:: bash

    genolearn config get NAME

Prints a configuration file.

.. rubric:: ARGUMENTS
.. code-block:: bash

    NAME : Name of config file located in ~/.genolearn/configs.


Remove
======

.. code-block:: bash

    genolearn config remove NAME


Removes a config file.

If ``NAME`` = 'all', removes all config files.


.. rubric:: ARGUMENTS
.. code-block:: bash

    NAME : Name of config file located in ~/.genolearn/configs.


Activate
========

.. code-block:: bash

    genolearn config activate NAME


Sets the active config file.

Note that the only valid ``NAME`` values are the filenames detected in ~/.genolearn/configs which are generated from executing ``genolearn config create``.

.. rubric:: ARGUMENTS
.. code-block:: bash

    NAME : Name of config file located in ~/.genolearn/configs.


Active
======

.. code-block:: bash

    genolearn config active

Prints the active config file.

.. toctree::
    :hidden:
    :titlesonly:

     model <model/index>