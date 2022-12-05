.. _config-model-classification

GenoLearn Config Model Classification
#####################################

This section documents the usage of the classification sub-command of GenoLearn ...

Classification
==============

.. code-block:: bash

    genolearn config model classification MODEL


Creates a classification config.

Models
------

.. rubric:: logistic-regression
.. code-block:: bash

    genolearn config model classification logistic-regression

Creates a logistic regression config prompting for hyperparameters described by Sklearn's `LogisticRegression <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html>`_ model.

.. rubric:: random-forest
.. code-block:: bash

    genolearn config model classification random-forest

Creates a logistic regression config prompting for hyperparameters described by Sklearn's `RandomForestClassifier <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html>`_ model.

