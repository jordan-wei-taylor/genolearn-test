GenoLearn Commmands
###################

Users initially will only be able to execute the Setup command. GenoLearn makes available new commands as the user executes the currently available commands.


Setup
=====

Prepares the ``current directory`` to be used by GenoLearn. Ensure that you have your ``genome sequence data`` (\*.gz) and ``metadata`` (\*.csv) in a ``data directory``.

.. code-block:: text
    
    <current directory>
    └── <data directory>
        ├── <genome sequence data>
        └── <metadata>

During the setup, you will be prompted to first select which subdirectory within your current directory is your data directory and then which file within your data directory is your metadata. Upon a successful execution, the Setup command is no longer available in the current directory unless the user executes the Clean command.

Clean
=====

Deletes all GenoLearn generated directories and files. Users may wish to start their project again. This process cannot be undone and the user will be asked to confirm first before the command is executed. This command is only available if the user is in the root directory where they have previously executed the Setup command. 


Print
=====

Prints various GenoLearn generated files. Initially the user can only choose from history and config which corresponds to the history of GenoLearn commands executed in the current directory and the configuration used by GenoLearn defining the data directory and the metadata file within it. As the user executes later commands, they will be able to additionally select to print or analyse their preprocessed metadata and to print

- preprocessed metadata stored in the meta subdirectory
- model configurations stored in the model subdirectory

This command is only available if the user is in the root directory where they have previously executed the Setup command. 

Preprocess
==========

Preprocesses the user's data into a more friendly format which is faster to read. This command is only available if the user is in the root directory where they have previously executed the Setup command.


Preprocess Sequence
-------------------

Preprocesses sequence data and generates the subdirectory ``preprocess``. The user has to first select which ``*.gz`` file within the data directory to preprocess. If there is only a single ``*.gz`` file within the ``data directory``, it will be automatically selected. Upon selecting a sequence file, the user is prompted for more information:

.. code-block:: text

    batch-size   : number of concurrent observations to preprocess at the same time
    n-processes  : number of parallel processes
    sparse       : flag to generate sparse data representation
    dense        : flag to generate dense  data representation
    verbose      : integer denoting the number of features between each verbose update
    max_features : integer denoting the first number of features to preprocess (set to -1 to preprocess all)


Preprocess Combine
------------------

Similar to the previous subcommand, preprocesses another ``*.gz`` file and combines the outputs with the previous execution of Preprocess Sequence. 

.. code-block:: text

    batch-size   : number of concurrent observations to preprocess at the same time
    n-processes  : number of parallel processes
    verbose      : integer denoting the number of features between each verbose update


This command is only available if the user is in the root directory where they have previously executed the Preprocess Sequence command.

Preprocess Meta
---------------

Preprocesses the metadata defining the identifier column, target column, and splitting which datapoints can be used to train and test our later Machine Learning models on. The user is prompted on

.. code-block:: text

    output              : filename of preprocessed metadata
    identifier          : identifier column in input metadata
    target              : target column in input metadata
    group               : group column in input metadata
    train group values* : group values to assign as training data [if group  = None]
    test group values * : group values to assign as testing data  [if group  = None]
    proportion train    : proportion of data to assign as train   [if group != None]

The user should leave the ``group`` value as ``None`` if they want to randomly assign their data as train and test (this is standard practice). If the user has defined their own groupings of the data points, they should specify the group column and state which (non-overlapping) group values belong to the train and test datasets. This command is only available if the user is in the root directory where they have previously executed the Preprocess Sequence command.


Feature Selection
=================

Compute a score for each feature quantifying some measure to later select which features to use for modelling purposes. By default, the Fisher Score for Feature Selection as described by Aggarwal 2014 [#fisher]_ is used. The user if prompted for

.. code-block:: text

    name      : output file name
    method    : feature selection method

The user can select their own ``custom`` method so long as they have a \<custom\>.py file with certain functions defined. See here for more details. This command is only available if the user is in the root directory where they have previously executed the Preprocess Meta command.

Model Config
============

Creates a Machine Learning model configuration file used by the later ``Train`` command. The user is prompted on which classifier they would like to design a config file for before prompted for further information on each of the chosen model's hyperparameters. The user can choose to perform a gridsearch by entering multiple values seperated by a comma. This command is only available if the user is in the root directory where they have previously executed the Feature Selection command.

Train
=====

Trains a Machine Learning model based on previous generated configuration files. Model is tuned based on the hyperparameter gridsearch defined in the ``Model Config`` execution and generates the following directory

.. code-block:: text

   output
    ├── encoding.json      # translation between the prediction integers and the class labels
    ├── model.pickle       # trained scikit-learn model which performed the best during the gridsearch
    ├── params.json        # parameters of the saved model
    ├── predictions.csv    # predictions on the test dataset with probabilities if applicable
    ├── results.npz        # numpy file with more information on the training such as predictions for all models in the gridsearch, train / test time etc
    └── train.log          # text file logging information such as time of execution, RAM usage, parameters for command execution

The user is prompted for

.. code-block:: text

    output directory      : output directory
    num features*         : comma seperated integers for varying number of features to consider
    min count             : min count of training class observations to be considered
    target subset         : subset of target values to train on if provided
    metric                : statistical metric to measure goodness of fit
    aggregation function  : aggregation function to compute overall goodness of fit

This command is only available if the user is in the root directory where they have previously executed the Model Config command.


Feature Importance
==================

Given a ``train`` subdirectory generated by the ``Train`` command, generates an ``importance`` subdirectory describing the important features as inferred by the trained model.


Evaluate
========

Given a ``train`` subdiirectory generated by the ``Train`` command, evaluates the saved model on a subset of the user's preprocessed data.


.. [#fisher] Charu C. Aggarwal. 2014. Data Classification: Algorithms and Applications (1st. ed.). Chapman & Hall/CRC. page 44