Miscellaneous functions
========================

There are some msscellaneous functions provided in PyMathProg
for less common tasks. Here we will talk about:

  #. :ref:`delete`
  #. :ref:`save`
  #. :ref:`kkt`

.. _delete:

Deleting model elements
-----------------------

Deleting variables and/or constraints from a model 
is done by invoking the *delete()* method on a 
variable or constraint.

.. literalinclude:: ./deltest.py
   :linenos:

The output is as follows:

.. code-block:: none

  GLPK Simplex Optimizer, v4.60
  3 rows, 3 columns, 9 non-zeros
  *     0: obj =  -0.000000000e+00 inf =   0.000e+00 (3)
  *     2: obj =   2.560000000e+04 inf =   0.000e+00 (0)
  OPTIMAL LP SOLUTION FOUND

  PyMathProg 1.0 Sensitivity Report Created: 2016/12/11 Sun 09:05AM
  ================================================================================
  Variable            Activity   Dual.Value     Obj.Coef   Range.From   Range.Till
  --------------------------------------------------------------------------------
  *x[0]                     94            0          100         87.5          150
  *x[1]                     54            0          300          200      366.667
   x[2]                      0          -20           50         -inf           70
  ================================================================================
  ================================================================================
  Constraint       Activity Dual.Value  Lower.Bnd  Upper.Bnd RangeLower RangeUpper
  --------------------------------------------------------------------------------
   R1                 93000   0.166667       -inf      93000      61200     121200
   R2                   101        100       -inf        101       77.5    118.667
  *R3                   148          0       -inf        201        148        148
  ================================================================================
  GLPK Simplex Optimizer, v4.60
  2 rows, 2 columns, 4 non-zeros
  *     3: obj =   2.020000000e+04 inf =   0.000e+00 (0)
  OPTIMAL LP SOLUTION FOUND

  PyMathProg 1.0 Sensitivity Report Created: 2016/12/11 Sun 09:05AM
  ================================================================================
  Variable            Activity   Dual.Value     Obj.Coef   Range.From   Range.Till
  --------------------------------------------------------------------------------
  *x[0]                    202            0          100           50 1.79769e+308
   x[2]                      0          -50           50         -inf          100
  ================================================================================
  ================================================================================
  Constraint       Activity Dual.Value  Lower.Bnd  Upper.Bnd RangeLower RangeUpper
  --------------------------------------------------------------------------------
  *R1                 60600          0       -inf      93000      60600      60600
   R2                   101        200       -inf        101          0        155
  ================================================================================


.. _save:

Saving model and solution
-------------------------

It is possible to save the model and/or the solution to a text file. The example
below shows how to do that through the global function *save(...)*.

.. literalinclude:: ./saves.py
   :linenos:

Note that the sensitivity report just saved is produced by GLPK. 
The format is not the same as the report produced by the global
function *sensitivity()* in PyMathProg.

.. _kkt:

Karush-Kuhn-Tucker conditions
-----------------------------

The KKT condition tells how much error are there
in terms of satisfying the constraints. Errors
may be measured both absolutely or relatively.
To produce KKT conditions, just call the routine KKT()
after solving a model.

.. literalinclude:: ./gkkt.py
   :linenos:

The produced output is as follows:

.. code-block:: none

   Max : 10 * x[0] + 6 * x[1] + 4 * x[2]
   R1: x[0] + x[1] + x[2] <= 10
   R2: 9 * x[0] + 4 * x[1] + 5 * x[2] <= 60
   R3: 2 * x[0] + 2 * x[1] + 6 * x[2] <= 30
   GLPK Simplex Optimizer, v4.60
   3 rows, 3 columns, 9 non-zeros
   *     0: obj =  -0.000000000e+00 inf =   0.000e+00 (3)
   *     2: obj =   7.600000000e+01 inf =   0.000e+00 (0)
   OPTIMAL LP SOLUTION FOUND 
   Karush-Kuhn-Tucker optimality conditions:
   =========================================
   Solver used for this solution: simplex

   1) Error for Primal Equality Constraints:
   ----------------------------------------
   Largest absolute error: 0.000000 (row id: 0)
   Largest relative error: 0.000000 (row id: 0)

   2) Error for Primal Inequality Constraints:
   -------------------------------------------
   Largest absolute error: 0.000000 (row id: 0)
   Largest relative error: 0.000000 (row id: 0)

   1) Error for Dual Equality Constraints:
   ----------------------------------------
   Largest absolute error: 0.000000 (var id: 0)
   Largest relative error: 0.000000 (var id: 0)

   2) Error for Dual Inequality Constraints:
   -------------------------------------------
   Largest absolute error: 0.000000 (var id: 0)
   Largest relative error: 0.000000 (var id: 0)

   __del__ is deleting problem: basic

