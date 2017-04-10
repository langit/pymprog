.. pymprog documentation master file, created by
   sphinx-quickstart on Thu May 21 09:19:35 2009.

##########################
Introduction to PyMathProg
##########################

.. _whetting:

Whetting your appetite
======================

If you'd like to have a powerful linear program(LP) solver 
wrapping around your little finger, then **PyMathProg** 
is the thing for you. 
PyMathProg provides an easy and flexible modelling syntax
using *Python* to create and optimize mathematical programming models. 
It is kind of a reincarnation of AMPL and GNU MathProg in Python. 
To illustrate, we will solve this tiny LP model here::

   maximize  15 x + 10 y         # profit
   S.T.
                x         <=  3  # mountain bike limit
                       y  <=  4  # racer limit
                x +    y  <=  5  # frame limit
                x >=0, y >=0     # non-negative

Believed it or not, we can almost literally transcribe it
into PyMathProg as follows::

  from pymprog import *
  begin('bike production')
  x, y = var('x, y') # variables
  maximize(15 * x + 10 * y, 'profit')
  x <= 3 # mountain bike limit
  y <= 4 # racer production limit
  x + y <= 5 # metal finishing limit
  solve()

For now, let's fire up an interactive python session, maybe in a 
terminal or a Python IDLE window, and try it all out like this:

>>> from pymprog import *
>>> begin('bike production')
model('bikes production') is the default model.
>>> x, y = var('x, y') # create variables
>>> x, y # take a look at them
(0 <= x continuous, 0 <= y continuous)
>>> maximize(15*x + 10*y, 'profit')
Max profit: 15 * x + 10 * y
>>> x <= 3
0 <= x <= 3 continuous
>>> y <= 4
0 <= y <= 4 continuous
>>> x + y <= 5
R1: x + y <= 5
>>> solve()
GLPK Simplex Optimizer, v4.60
1 row, 2 columns, 2 non-zeros
*     0: obj =  -0.000000000e+00 inf =   0.000e+00 (2)
*     2: obj =   6.500000000e+01 inf =   0.000e+00 (0)
OPTIMAL LP SOLUTION FOUND

That's just the beginning. A lot of more sophisticated 
examples are included in other parts of this documentation. 
We can also do many other interesing things to 
a model, even after solving it, for example:

- Conduct sensitivity analysis
- Change the value of a parameter 
- Fix a variable to an arbitrary value
- Manage the bounds of a variable or constraint
- Change the type of a variable
- Adding/deleting variables or constraints

When we solve it again, the solver usually takes
advantage of results from the latest solution.

.. _dream:

The Dream of PyMathProg
=======================

The dream of **PyMathProg** is to do math programming in *Python*
with ease and flexibility,  to create, optimize, report, 
change and re-optimize your model without breaking a sweat. 
To make that dream come true, a few things are essential:

- a good modelling language, and we've got Python
- a powerful and flexible solver, and there is GLPK
- an integrated toolset, with database, plotting, etc.
- an interactive modelling enviromment for easy learning

and for the last two, the answer is stiell "we've got Python".
Being embedded in Python, you can take advantage of all the good 
stuff available in Python: such as easy database access, 
graphical presentation of your solution, statistical analysis, 
or use pymprog for artificial intelligence in games, etc.
Interactive sessions enable us to get immediate feedback for 
each small step we take. We can also conveniently obtain help 
right within the session by using the 'help(.)' function. 
And we may quickly get an answer to our questions by conducting 
small experiments, or test out some ideas that arise at the occasion. 
Interactivity can make learning **PyMathProg** easy and fun.

.. _features:

Exciting new features
======================

Exciting new freatures offered by PyMathProg *v1.0* are as follows:

- New syntax to make modelling easy and intuitive
- Sensitivity analysis report
- Deletion of variables/constraints
- Improved solver options
- Friendly interactive session
- Arbitrary parameter changes update model automatically
- Parameters can be shared among many models

The underlying solver is still GLPK, but now it is
made available to PyMathProg by swiglpk, which has enabled:

- Super easy setup of PyMathProg with one single command
- Support of both Python 2 and 3
- Support of the newest version of GLPK (v4.60)

Therefore, this is indeed an exciting new version of **PyMathProg**!

.. _compatability:

A word on compatability
=========================

This new version (*v1.0*) of PyMathProg is *fully compatable*
with previous versions. However, some functions are deprecated and 
won't be fully supported in futre versions. Here is a list of them:

- var(.) now takes the name of variable(s) as the first argument
- par(.) now takes the name of parameter(s) as the first argument
- beginModel(.) is simplified into begin(.)
- endModel(.) is simplified into end(.)

