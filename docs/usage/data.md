GenoLearn Data
##############

.. code-block:: bash

    genolearn data COMMAND


Data analysis and assignment of train / test split.


Commands
========


Analyse
-------

.. code-block:: bash

    genolearn data analyse [OPTIONS]


.. rubric:: Options
.. code-block:: bash

    --group-by GROUP  : perform analysis by group-by GROUP column values
    --min-count VALUE : minimum count for suggested target subset
    --test TEST       : identifiers to omit when computing statistics


.. rubric:: Example Usage
.. code-block:: bash

    # summary global statistics
    genolearn data analyse

    # summary statistics by group (group should be a colmn in metadata)
    genolearn data analyse --group-by GROUP

    # additional suggestion for which target values should be taken forward for modelling
    # (no list is generated if all target values are valid for modelling purposes)
    genolearn data analyse --group-by GROUP --test TEST


.. rubric:: Default Example Usage
.. code-block:: bash

    genolearn data analyse -group-by train_test --test test


Head
----

.. code-block:: bash

    genolearn data head [NUM]


Prints the first ``NUM`` rows of metadata.

.. rubric:: Arguments

.. code-block:: text

    NUM : number of rows to print of metadata

Tail
----

.. code-block:: tail

    genolearn data tail [NUM]


Prints the last ``NUM`` rows of metadata.

.. rubric:: Arguments
.. code-block:: text

    NUM : number of rows to print of metadata


Train Test Split
----------------

.. code-block:: bash

    genolearn data train-test-split [OPTIONS]


.. rubric:: Options
.. code-block:: text

    --ptrain PTRAIN      : propoertion of data to be assigned "train"
    --random-state STATE : random seed for reproducibility
