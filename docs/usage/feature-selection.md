GenoLearn Feature Selection
###########################

.. code-block:: bash

    genolearn feature-selection


Computes which features to take forward for modelling purposes (fisher score for feature selection by default).

.. rubric:: Prompted Information
.. code-block:: text

    name        : output file name
    group_by    : group-by column
    values      : group-by values which are referred to as keys in the training stage
    method      : feature selection method
    aggregate   : experimental (leave as False)
    sparse      : loads the data in sparse format to reduce RAM usage if set to True


