.. A simple tutorial by Yingjie Lan, May 2009.

Case: Subtour Elimination
=========================

This example is adapted from the presentation
titled *Mathematical Programming: Modeling and 
Applications* by Giacomo Nannicini. Thanks are
hereby extended to him.

#. :ref:`intro_tsp`
#. :ref:`subtelim`
#. :ref:`implement`

.. _intro_tsp:

Brief Introduction
-------------------

The Traveling Salesman Problem (TSP) is
a very well known problem in the literature.
Applications of TSP include: logistics, 
crane control, placing circuits on a board 
minimizing the required time, and many more.
Unfortunately, it is a very difficult problem.
For not too large instances, it can be done 
on a desktop machine. 


Here is a definition of a TSP problem:
A salesman must visit all cities to see his customers, 
and return to the starting point.
He wants to minimize the total travel distance.
Here are are going to play with a small example
of TSP, assuming that the distance between any 
two cities is symmetric.

.. _subtelim:

Subtour Elimination
-------------------

A subtour is also a round tour that returns back
to where you start, but does not visit all the cities.
A formulation of TSP is this:

#. enter each city exactly once.

#. leave each city excatly once.

#. make sure there is no subtour.

To make sure there is no subtour, we must consider
*all* subset of cities, and make sure that there
is an arc leaving a city in the subset and entering
a city NOT in the subset. So there are exponential
number of subtour elimination constraints. 
Obviously, only a small number of them will be
actually needed to eliminate subtours. 
The idea is to start out without them and then
add those violated ones gradually,
until the solution contains no subtour. 
For a more detailed discussion on TSP, please see 
http://www.tsp.gatech.edu/methods/opt/subtour.htm

.. _implement:

Implementation 
--------------

This is how I have it implemented using PyMathProg:

.. literalinclude:: ./elimsubt.py
      :linenos:

And here is the output::

  there are 7 cities
  New subtour:  [0, 4, 2]
  New subtour:  [0, 6, 3, 2, 4]
  Optimal tour length: 153.0
  Optimal tour:
  [0, 5, 1, 6, 3, 2, 4]

