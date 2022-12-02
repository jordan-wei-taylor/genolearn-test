Tutorial
################

In this Tutorial, we imagine ourselves having collected data from years 2014-2018 and find ourselves in 2019. We want to preprocess the 2014-2018 dataset, perform feature selection, and train machine learning models on this data. We then collect data in 2019 and wish to see how accurate our machine learning models are for the new data.

We start by cloning an E. Coli O157 dataset which consists kmer count files (split into parts) and location region as the meta data. We have split the data into parts as per the maximum file size guidelines listed by GitHub (100 MB).

.. code-block:: bash

    git clone https://github.com/jordan-wei-taylor/e-coli-o157-data.git

Upon cloning the repository, ``cd`` into the repository and execute the ``merge.sh`` script to merge all part files.

.. code-block:: bash

    cd e-coli-o157-data
    ./merge.sh

Once the above has been executed there should be three files within the directory ``raw-data``.

.. code-block:: text

    e-coli-o157-data
    ├── merge.sh
    └── raw-data
        ├── meta-data.csv
        ├── STEC_14-18_fsm_kmers.txt.gz
        └── STEC_19_fsm_kmers.txt.gz

Lets install ``GenoLearn`` on a virtual python environment.

.. code-block:: bash

    python3 -m venv env
    source env/bin/activate
    pip install git+https://github.com/jordan-wei-taylor/genolearn.git

Now that we have the most recent installation of ``GenoLearn``, lets configure ``GenoLearn``.

.. code-block:: bash

    genolearn config create


.. rubric:: Prompted Information
.. code-block:: text

    config name                      : e-coli
    preprocess_dir                   : preprocess
    data_dir                         : data
    metadata file                    : meta-data.csv


Lets preprocess the 2014-2018 dataset

.. code-block:: bash

    genolearn preprocess sequence


.. rubric:: Prompted Information
.. code-block:: text

    data (gz) file {STEC_14-18_fsm_kmers.txt.gz, STEC_19_fsm_kmers.txt.gz}: STEC_14-18_fsm_kmers.txt.gz
    batch-size                                                      [None]:
    n-processes                                                     [None]:
    sparse                                                          [True]:
    dense                                                           [True]:
    verbose                                                       [250000]:


Imagine, at a later point in time, we had access to the 2019 dataset. We can combine the preprocessing if this data with our previous data with

.. code-block:: bash

    genolearn preprocess combine


.. rubric:: Prompted Information
.. code-block:: text

    data (gz) file {STEC_14-18_fsm_kmers.txt.gz, STEC_19_fsm_kmers.txt.gz}: STEC_19_fsm_kmers.txt.gz
    batch-size                                                      [None]:
    n-processes                                                     [None]:
    verbose                                                       [250000]:


The dataset contains data relating to E. Coli O157 with 2,875 different strains, each with a count vector of over 12 million :math:`k`-mers, and an associated region of origin in the meta data file for years 2014 to 2019. We can note this is a large dataset so in order to run any machine learning models on this dataset we will need a means of selecting which genome sequences are of interest. We can assign a *train / test* split and then use a feature selection method to reduce the number of genome sequences we model.

.. code-block:: bash

    genolearn preprocess meta

.. rubric:: Prompted Information
.. code-block:: text

    output        [default]: 
    identifier             : Accession
    target                 : Region
    group            [None]: Year
    train group values     : 2014, 2015, 2016, 2017, 2018
    test  group values     : 2019


If you do not have a dataset that can be grouped into a similar way to our example use case of *Year*, leave the ``group`` prompt blank. We can analyse the distribution of our metadata with

.. code-block:: bash

    genolearn data analyse


.. rubric:: Prompted Information
.. code-block:: text

    meta {default} [default]: 
    min_count           [10]: 
    proportion       [False]:


which prints

.. code-block:: text

                      |   2014 |   2015 |   2016 |   2017 |   2018 |   2019 |  Train |   Test | Global
    ------------------+--------+--------+--------+--------+--------+--------+--------+--------+--------
    Asia              |      0 |      4 |     16 |      9 |     18 |     10 |     47 |     10 |     57
    Australasia       |      0 |      0 |      1 |      0 |      3 |      2 |      4 |      2 |      6
    C. America        |      0 |      2 |      6 |      6 |     10 |      5 |     24 |      5 |     29
    C. Europe         |      0 |      0 |     26 |     15 |      8 |     13 |     49 |     13 |     62
    M. East           |      3 |     11 |     33 |     23 |     42 |     45 |    112 |     45 |    157
    N. Africa         |      0 |     15 |      7 |     26 |     24 |     19 |     72 |     19 |     91
    N. America        |      1 |      1 |      3 |      3 |      3 |      1 |     11 |      1 |     12
    N. Europe         |      0 |      1 |      2 |      7 |      2 |      6 |     12 |      6 |     18
    S. America        |      0 |      0 |      1 |      2 |      0 |      0 |      3 |      0 |      3
    S. Europe         |      5 |     13 |     62 |     59 |     54 |     44 |    193 |     44 |    237
    Subsaharan Africa |      3 |      2 |      7 |      7 |      6 |      3 |     25 |      3 |     28
    UK                |    133 |    135 |    765 |    406 |    468 |    267 |  1,907 |    267 |  2,174
    Total             |    145 |    184 |    929 |    563 |    638 |    415 |  2,459 |    415 |  2,874

    suggested target subset: Asia, C. America, C. Europe, M. East, N. Africa, N. America, N. Europe, S. Europe, Subsaharan Africa, UK


We can see that we have a big target class imbalanced heavily skewed towards the UK. Additionally, not all of the Train class label counts exceed a minimum count of 10 (the choice 10 is arbitrary) so it is recommended to perform the later machine learning task on a subset of class labels as we may not have enough examples to learn from.


At this point, we can now use Fisher Scores to compute which genome sequences to take forward for modelling purposes (see :ref:`FeatureSelection` for more details). Lets compute the Fisher Scores for each genome sequence with the below command

.. code-block:: bash

    genolearn feature-selection


.. rubric:: Prompted Information
.. code-block:: text

    name [fisher-scores.npz]: 
    meta {default} [default]: 
    method          [fisher]:


Upon execution of the above command, the path ``data/feature-selection/fisher-scores.npz`` should exist.  The above command computes the fisher scores for all genome sequence counts that have been assigned as *Train*. 

Now that we have preprocessed all of our data and computed the Fisher Scores, we can look to see how our machine learning models perform on our dataset. Before training a machine learning model, we will need define a ``model config``. Here is an example of generating one:

.. code-block:: bash

    genolearn config model classification random-forest


.. rubric:: Prompted Information
.. code-block:: text

    config-name                       [random-forest.config]: 
    n-estimators                                       [100]: 
    criterion               {gini, entropy, log_loss} [gini]: 
    max-depth                                         [None]: range(10, 51, 10)
    min-samples-split                                    [2]: 
    min-samples-leaf                                     [1]: 
    min-weight-fraction-leaf                           [0.0]: 
    max-features                   {sqrt, log2, None} [sqrt]: 
    max-leaf-nodes                                    [None]: 
    min-impurity-decrease                              [0.0]: 
    bootstrap                                         [True]: 
    oob-score                                        [False]: 
    n-jobs                                              [-1]:
    random-state                                         [0]: range(5)
    class-weight {balanced, balanced_subsample, None} [None]: balanced


The above should generate a random-forest.config file in the directory ``preprocess/model``

.. rubric:: random-forest.config
.. code-block:: text

    {
        "model": "RandomForestClassifier",
        "n_estimators": 100,
        "criterion": "gini",
        "max_depth": [
            10,
            20,
            30,
            40,
            50
        ],
        "min_samples_split": 2,
        "min_samples_leaf": 1,
        "min_weight_fraction_leaf": 0.0,
        "max_features": "sqrt",
        "max_leaf_nodes": null,
        "min_impurity_decrease": 0.0,
        "bootstrap": true,
        "oob_score": false,
        "n_jobs": -1,
        "random_state": [
            0,
            1,
            2,
            3,
            4
        ],
        "class_weight": "balanced"
    }


If we would like to try a range of values we can do so by specifying a list of values. In the above example we are training models with ``max_depth`` values of 10, 30, and 50 as well as 10 different ``random_state`` values.

Now lets run a training script where we train on all strains collected in 2018 and compute predictions on strains collected in 2019 using the most important 10000 genome sequences.

.. code-block:: bash

    genolearn train


.. rubric:: Prompted Information
.. code-block:: text
    output_dir                               [training-output]: 
    meta                                   {default} [default]: 
    model_config {random-forest.config} [random-forest.config]: 
    feature_selection  {fisher-scores.npz} [fisher-scores.npz]: 
    num_features                                        [1000]: 
    ascending                                          [False]: 
    min_count                                              [0]: 
    target_subset                                       [None]: Asia, C. America, C. Europe, M. East, N. Africa, N. America, N. Europe, S. Europe, Subsaharan Africa, UK
    metric                                          [f1_score]: 
    aggregate_func       {mean, weighted_mean} [weighted_mean]: 

The above generates the following tree

.. code-block:: text
    
    training-output
    ├── model.pickle           # a saved model which achieved the highest metric and can be re-evaluated with the ``genolearn evaluate``
    ├── params.json            # json file storing the model parameters used when instantiating the model class
    ├── predictions.csv        # predictions and the associated probability distributions over class labels csv
    ├── results.npz            # predictions from all model configurations and can be opened within Python as shown below
    └── train.log              # information used when running ``genolearn train``


For a deeper insight on the results, you will need to run in Python

.. code-block:: python

    import numpy as np

    npz = np.load('training-output/results.npz')

    identifiers = npz['identifiers'] # shape (n,)
    predictions = npz['predict']     # shape (1, 20, 10, n) (1 K, 20 max_depth, and 10 random_state parameters for n predictions)
    times       = npz['times']       # shape (1, 20, 10, 2) (last dimension measures training and predicting times)

where :math:`n` is the number of valid testing strains present in 2019 i.e. only the strains in 2019 where the associated target region was present in 2018. This ignores strains in 2019 where the associated target region does not appear in 2018 as there are no training examples to learn from.

Feature importances can be obtained by

.. code-block:: bash

    genolearn feature-importance


.. rubric:: Prompted Information
.. code-block:: text

    train_dir               : training-output
    output      [importance]:

which outputs in the current directory

.. code-block:: text

    importance
    ├── importance.npz         # numpy arrays of further details of the feature importances
    └── importance-rank.csv    # a csv ranking the important features from most to least important

See `Feature Importance <https://genolearn.readthedocs.io/en/latest/usage/feature-importance.html>`_ for further details on interpretation of the ``importance.npz`` file.




