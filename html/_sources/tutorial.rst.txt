

A Dive-in Tutorial 
==================

.. _divin:

A dive-in example
-----------------

Suppose you have an easy linear program. 
A *3x3* matrix is given as the matrix for
constraints, along with *2* vectors of 
length *3*, one for the objective function 
and the other for the right-hand-sides.
You need to solve the problem and give
a sensitivity report. 
This is very easy with PyMathProg:

.. literalinclude:: ./gbasic.py
      :linenos:

The code is quite straight-forward.
Note there are three basic building blocks:
it starts with a data block, followed by a model
block, and finished with a report block.

#. **Data block (lines 2-6):** 

   The matrix and the vectors are defined. 
   Of course, you can also read data from
   some external database, as Python can do that easily.

#. **Model block (lines 7-12):**

   It all starts by a function ``begin(name)`` on line 7.
   It creates a new model instance  with the given name
   for later modelling steps to build upon.
   It is also possible to handle the 
   model directly, we will come to that later.

   Line 8 turns on the verbosity option, which enables
   PyMathProg to provide feedbacks on each building step.

   Line 9 defines the three variables and organize them in a list: 
   you simply provide the name for the group, and the number of
   variables to create, which is 3 in this case. By default,
   these variables are continuous and non-negative.

   Line 10 defines the objective: maximize the summation
   of the terms b[i]*x[i], where i goes from 0 to 3.

   Lines 11-12 define the constraints with a for loop.

   That's it for modelling. Now the code moves on to 

#. **Report block (lines 13-15):**

   Line 13 issues a call *solve()* to solve the model. 

   Line 14 produces the sensitivity report.

   Finally, line 15 calls the function *end()* to do away 
   with the model.

And here is the output (with the verbosity turned on):

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

   PyMathProg 1.0 Sensitivity Report Created: 2016/12/08 Thu 12:55PM
   ================================================================================
   Variable            Activity   Dual.Value     Obj.Coef   Range.From   Range.Till
   --------------------------------------------------------------------------------
   *x[0]                      4            0           10            6         13.5
   *x[1]                      6            0            6      4.44444           10
    x[2]                      0         -2.8            4         -inf          6.8
   ================================================================================
   Note: rows marked with a * list a basic variable.

   ================================================================================
   Constraint       Activity Dual.Value  Lower.Bnd  Upper.Bnd RangeLower RangeUpper
   --------------------------------------------------------------------------------
    R1                    10        2.8       -inf         10    6.66667         15
    R2                    60        0.8       -inf         60         40         90
   *R3                    20          0       -inf         30         20         20
   ================================================================================
   Note: normally, RangeLower is the min for the binding bound, and RangeUpper
   gives the max value. However, when neither bounds are binding, the row is 
   marked with a *, and RangeLower is the max for Lower.Bnd(whose min is -inf), 
   and RangeUpper is the min for Upper.Bnd(whose max value is inf). Then the 
   columns of RangeLower, RangeUpper and Activity all have identical values.

   __del__ is deleting problem: basic


.. _parallel:

A parallel example
------------------

In the previous example, we use global functions to create and manipulate
a default model -- we did not directly handle it. PyMathProg also provides
a way of direct handling of the model, as demonstrated by the code below
that does exactly the same thing as before:

.. literalinclude:: ./basic.py
         :linenos:

Clearly, there is a line to line correspondence to the previous code.
In the first line, this code only imports *model* from pymprog. Then
on line 7, instead of call ``begin(.)``, this code uses ``p=model(.)``
to create a new model instance. From then on, each function call is 
converted into a method invocation on the created model instance.

.. _game2p:

Zero-sum Two-player Game
------------------------

This example is employed to show the use
of the 'primal' and 'dual' values.
A zero-sum two-player game is a game
between two players, where the gain
of one player is the loss of the other,
hence their pay-offs always sums up to zero.
The value *a[i,j]* is the pay-off for player one
when player one plays strategy *i* and 
player two plays strategy *j*.
Here is an LP formulation to find the 
equilibrium mixed strategies and the value 
of the game.

.. literalinclude:: ./game2p.py
         :linenos:

In this block of code, two variables *r1*
and *r2* are employed to save the constraints
for the sake of reporting. Note that in this
model, the *primal* value of the variables gives
the probability for player 2's mixed strategy,
and the *dual* value of the constraints *r1* and *r2*
gives the mixed strategy of player 1.
And the output is as follows:

.. code-block:: none

  GLPK Simplex Optimizer, v4.60
  3 rows, 3 columns, 8 non-zeros
      0: obj =   0.000000000e+00 inf =   1.000e+00 (1)
      3: obj =   7.000000000e+00 inf =   0.000e+00 (0)
  OPTIMAL LP SOLUTION FOUND
  Game value: 7
  Mixed Strategy for player 1:
  A1: 0.333333, A2: 0.666667
  Mixed Strategy for player 2:
  B1: 0.5, B2: 0.5

Hope this dive-in tutorial has served to give you the
basic idea of how PyMathProg works. Before working on 
more advanced examples, please read on!
