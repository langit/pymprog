
Using Solver Options
====================

Currently, there are four solvers available for use,
and each solver comes with a set of options for 
the parameters that control its behavior.
Use the global function *solver(...)*
to select the solver for your model,
and to set the desired options for the 
chosen solver.

.. _setgetopt:

Setting/getting options
----------------------------

The four solvers available for use are
each given a name: 'simplex', 'exact', 'interior', 
and 'intopt'. Note that the first three 
are good for solving linear programs, whereas the
last ('intopt') is good for solving integer programs.
That means we only have choices (at least for now)
when we have a linear program to solve. 
To select a particular solver, just do:

>>> solver('interior')

That would set 'interior' solver as the solver for linear programming.
You may also provide options at the same time:

>>> solver('interior', msg_lev=glpk.GLP_MSG_OFF)
{'msg_lev': 0}

which would turn off message output from the solver,
and return the current values for options explicitly set. 
For options whose value is not set, they would take the default value.
For information on what options and values are available for a 
particular solver, try something like this:

>>> solver(help = 'interior')

To find out which solver will be used for linear programming:

>>> solver(float)
'simplex'

To find out which solver will be used for integer programming:

>>> solver(int)
'intopt'

To set options on one of the default solvers, for example, use

>>> solver(int, br_tech=glpk.GLP_BR_PCH)

to select the hybrid pseudo-cost heuristic(PCH) 
branching technique for the integer optimizer.



.. _delopts:

Deleting an option
-------------------

To delete an option, simply set it to *None*. 

>>> solver(int, msg_lev=None)

This would delete the explicit value for the 'msg_lev' option, 
and leave it at its default value.

Note: if you need to warm start your simplex method 
(that is, start the simplex method with the optimal 
basis from your last invocation, which is often used 
when employing row generation and/or column generation), 
please don't turn on the 'presolve' option. 

