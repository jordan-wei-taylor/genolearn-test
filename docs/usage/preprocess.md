GenoLearn Preprocess
####################

.. code-block:: bash

    genolearn preprocess COMMAND

preprocess your data into a more efficient format.

Commands
========

Sequence
--------

.. code-block:: bash

    genolearn preprocess sequence [OPTIONS]


preprocess a gunzip (gz) compressed text file.

The text file should containing genome sequence data of the following sparse format


    .. code-block:: bash

        sequence_1 | identifier_{1,1}:count_{1,1} identifier_{1,1}:count_{2,1} …
        sequence_2 | identifier_{2,1}:count_{2,1} identifier_{2,1}:count_{2,2} …
        …

into a directory of .npz files, a list of all the features, and some meta information containing number of identifiers, sequences, and non-zero counts.

It is expected that the parameter data is in the data_dir directory set in the active config file. See https://genolearn.readthedocs.io/usage/config for more details.

.. rubric:: Options
.. code-block:: text

    --max-features [None] : if defined, only preprocesses the first ``max-features`` rows of the input ``data``. 


.. rubric:: Prompted Information
.. code-block:: text

    data        : input genome sequence file (gunzipped)
    batch-size  : number of concurrent observations to preprocess at the same time
    n-processes : number of parallel processes
    sparse      : sparse output
    dense       : dense output
    verbose     : integer denoting number of features between each verbose update

Combine
--------

.. code-block:: bash

    genolearn preprocess combine


combines the preprocess of a gunzip (gz) compressed text file to an existing preprocessed directory.
    
The text file should containing genome sequence data of the following sparse format

    .. code-block:: text

        sequence_1 | identifier_{1,1}:count_{1,1} identifier_{1,1}:count_{2,1} ...
        sequence_2 | identifier_{2,1}:count_{2,1} identifier_{2,1}:count_{2,2} ...
        ...


and combines the preprocessed data with the `preprocess_dir` directory set in the \033[1mactive config\033[0m file.
This relies on the user to have previously executed `genolearn preprocess sequence`.

See https://genolearn.readthedocs.io/tutorial/ for example use case.

.. rubric:: Options
.. code-block:: text

    --max-features [None] : if defined, only preprocesses the first ``max-features`` rows of the input ``data``. 


.. rubric:: Prompted Information
.. code-block:: text

    data        : input genome sequence file (gunzipped)
    batch-size  : number of concurrent observations to preprocess at the same time
    n-processes : number of parallel processes
    verbose     : integer denoting number of features between each verbose update
    n-features  : number of features to preprocess (set to -1 to preprocess all)


Meta
----

.. code-block:: bash

    genolearn preprocess meta

Preprocesses the metadata and defines the train / test split for the later ``genolearn train`` execution.

.. rubric:: Prompted Information
.. code-block:: text

    output             : filename of preprocessed metadata
    identifier         : identifier column in input metadata
    target             : target column in input metadata
    group              : group column in input metadata
    train_group_values : group values to assign as training data [if group  = None]
    test_group_values  : group values to assign as testing data  [if group  = None]
    proportion train   : proportion of data to assign as train   [if group != None]

