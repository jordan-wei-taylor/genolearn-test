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

    genolearn data analyse


.. rubric:: Prompted Information
.. code-block:: text

    meta               : preprocessed metadata filename
    min count     [10] : minimum count for suggested target subset
    proportion [False] : print the proportions instead of counts


Head
----

.. code-block:: bash

    genolearn data head [NUM]


.. rubric:: Prompted Information
.. code-block:: text

    meta : preprocessed metadata filename (autofilled if only one file to choose from)


Prints the first ``NUM`` rows of metadata.

.. rubric:: Arguments

.. code-block:: text

    NUM : number of rows to print of metadata

Tail
----

.. code-block:: tail

    genolearn data tail [NUM]


.. rubric:: Prompted Information
.. code-block:: text

    meta : preprocessed metadata filename (autofilled if only one file to choose from)

Prints the last ``NUM`` rows of metadata.

.. rubric:: Arguments
.. code-block:: text

    NUM : number of rows to print of metadata


Sample
----

.. code-block:: tail

    genolearn data sample [NUM]


.. rubric:: Prompted Information
.. code-block:: text

    meta : preprocessed metadata filename (autofilled if only one file to choose from)


Prints the ``NUM`` randomly sampled rows of metadata.

.. rubric:: Arguments
.. code-block:: text

    NUM : number of rows to print of metadata