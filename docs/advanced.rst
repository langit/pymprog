.. Advanced examples by Yingjie Lan, May 2009.

More Advanced Examples
=======================

Here some more advanced examples are presented 
with brief explanations. There are dozens more
examples in the *models* folder of the project 
if you downloaded the zipped source files from 
its `sourceforge project page
<https://sourceforge.net/projects/pymprog/>`__.
The source code of all the examples here are placed
in the *docs* folder of this project.
Some of these examples were originally written in 
GNU MathProg by Andrew Makhorin (thanks to Andrew),
and were adopted into PyMathProg. 

#. :ref:`assign`
#. :ref:`dynaqueens`
#. :ref:`tsp`
#. :ref:`zebra`
#. :ref:`magic`
#. :ref:`sudoku`
#. :ref:`sudoku2`
#. :ref:`jobsched`
#. :ref:`revman`

.. _assign:

Re-optimize the assignment
--------------------------

In this example, we first solve the assignment problem,
then we change one of the cost parameter, and
re-optimize. See how easily this is done in PyMathProg.

.. literalinclude:: ./gassign.py
      :linenos:

Below is the output, note how the optimal assignment
changed after increasing the cost, and how the second
time of solving the problem seems much easier.

.. code-block:: none

   GLPK Simplex Optimizer, v4.60
   16 rows, 64 columns, 128 non-zeros
         0: obj =   0.000000000e+00 inf =   8.000e+00 (8)
         8: obj =   1.750000000e+02 inf =   0.000e+00 (0)
   *    24: obj =   7.600000000e+01 inf =   0.000e+00 (0)
   OPTIMAL LP SOLUTION FOUND
   Total Cost = 76
   Agent 0 gets Task 0
   Agent 1 gets Task 7
   Agent 2 gets Task 6
   Agent 3 gets Task 4
   Agent 4 gets Task 1
   Agent 5 gets Task 5
   Agent 6 gets Task 3
   Agent 7 gets Task 2
   Set cost c[0, 0] to higher value 23
   GLPK Simplex Optimizer, v4.60
   16 rows, 64 columns, 128 non-zeros
   *    25: obj =   7.800000000e+01 inf =   0.000e+00 (0)
   OPTIMAL LP SOLUTION FOUND
   Total Cost = 78
   Agent 0 gets Task 7
   Agent 1 gets Task 0
   Agent 2 gets Task 6
   Agent 3 gets Task 4
   Agent 4 gets Task 1
   Agent 5 gets Task 5
   Agent 6 gets Task 3
   Agent 7 gets Task 2


.. _dynaqueens:

Interaction with queens
-----------------------

This example will randomly pick a board size and then
randomly place some queens on the board. 
The rest of the queens are then placed
by the LP program to see if all queens   
can be placed without attaching each other.
If that's impossible, then the random positions
are said to be bad. Note that in that LP,
no objective function is needed.

.. literalinclude:: ./dynaqueens.py
      :linenos:

.. _tsp:

The traveling sales man(TSP) 
------------------------------

Really, the too well known problem.

.. literalinclude:: ./tsp.py
      :linenos:

.. _zebra:

Zebra: using string as index
----------------------------

A logic puzzle, see how strings are
used as indices here to enhance the
readability of the model.

.. literalinclude:: ./zebra.py
      :linenos:


.. _magic:

Magic numbers
--------------

Magic numbers, a very interesting problem.

.. literalinclude:: ./magic.py
      :linenos:

.. _sudoku:

Sudoku: want some AI?
---------------------

Do you play Sudoku? 
This program might help you crack a Sudoku in seconds ;).

.. literalinclude:: ./sudoku.py
      :linenos:

.. _sudoku2:

Super Sudoku
------------

This example will provide a sample Super Sudoku:
in addition to satisfying all the requirements 
of Sudoku, Super Sudoku also requires that the
elements in each diagonal must be distinct,
below is a sample Super Sudoku obtained by the
code provided afterwards::

 +-------+-------+-------+
 | 2 1 3 | 4 6 5 | 8 7 9 |
 | 4 5 6 | 7 8 9 | 2 1 3 |
 | 7 8 9 | 2 1 3 | 4 5 6 |
 +-------+-------+-------+
 | 1 2 4 | 3 5 6 | 7 9 8 |
 | 3 6 8 | 9 7 2 | 5 4 1 |
 | 9 7 5 | 8 4 1 | 3 6 2 |
 +-------+-------+-------+
 | 8 4 2 | 1 9 7 | 6 3 5 |
 | 6 3 1 | 5 2 4 | 9 8 7 |
 | 5 9 7 | 6 3 8 | 1 2 4 |
 +-------+-------+-------+


.. literalinclude:: ./ssudoku.py
      :linenos:



.. _jobsched:


Machine Scheduling
------------------

Schedule jobs on a single machine, given the duration, 
earliest start time, and the latest finish time
of each job. Jobs can not be interrupted, and
the machine can only handle one job at one time. 

.. literalinclude:: ./job_sched.py
      :linenos:

The output schedule is as follows (your run
may not be the same, as the data is randomly
generated -- you might even get infeasible
problem instances)::

  Duration [7, 4, 1, 7]
  Earliest [13, 17, 19, 12]
  Latest [22, 41, 28, 38]
  status: opt
  schedule:
  job 0: 13.0 20.0
  job 1: 20.0 24.0
  job 2: 27.0 28.0
  job 3: 31.0 38.0


.. _revman:

Scheduling for Revenue
-----------------------

The same scheduling problem as above, but add a new
spin to the problem: when it is not feasible to 
accept all jobs, try accept those that will maximize
the total revenue.

.. literalinclude:: ./revman_jobs.py
      :linenos:

