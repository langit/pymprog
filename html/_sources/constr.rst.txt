Working with Constraints
========================

Defining constraints in PyMathProg is very easy. 
After creating the model,
you can use two different styles to add constraints to it. 

  1. the implicit way(the more natural way): 
     simply use inequalities(comparisons using '<=', '==', '>=')
     to construct constraints.

  2. the explicit way: use the *st(.)* method to add constraints. 
     This way is a little more combersome, and it is the old way.

Which way to go entirely depends on your taste, the results are the same.

#. :ref:`single`
#. :ref:`double`
#. :ref:`group`

.. _single:

With a single comparison
----------------------------

Let's first use the more natural way to add constraints::

  begin('illustration')
  x = var('x', 3)
  y = var('y')
  c = [6,4,3]
  sum(p*q for p,q in zip(c,x)) <= y
  x[0] + x[2] >= x[1]
  x[0] + x[2] <= 1

Now the equivalence in the explicit way is as follows::

  begin('illustration')
  x = var('x', 3)
  y = var('y')
  c = [6,4,3]
  st( sum(p*q for p,q in zip(c,x)) <= y )
  st( x[0] + x[2] >= x[1] )
  st( x[0] + x[2] <= 1 )

Surely, we can use index sets to make the model 
more easy to read and write, as seen in this more 
interesting model for diet optimization::

  from pymprog import *
  fruits = ('apple', 'pear', 'orange')
  nutrit = ('fat', 'fibre', 'vitamin')
  ntrmin = ( 10, 50, 30 ) # min nutrition intake
  #nutrition ingredients of each fruit
  ingred = ('apple': (3,4,5), 'pear': (2,4,1),
            'orange': (2,3,4))
  diet = var('diet', fruits, int) 
  for n, ntr in enumerate(nutrit):
     sum( diet[frt] * ingred[frt][n] 
            for frt in fruits) >= ntrmin[n] 

Those constraints are perfectly fine: they just have 
one comparison. Now let's get a little more sophisticated.

.. _double:

With double comparisons
----------------------------

Things get more interesting when we use continuous comparisons in 
Python to specify both the lower and upper bounds in one expression::

>>> begin('model')
>>> x, y = var('x, y')
>>> 3 <= 4 * x + 5 * y <= 6

The new thing appears on the last line.
It bounds the linear expression in the middle 
by both a lower and upper bound using continuous comparison.

Before we move on, let's do a little side talk on
the similarity of variable bounds and constraints.
We already know how to bound a variable *x*::

>>>  x <= 100
>>>  1 <= x <= 5

From pure mathematical sense, bounds are just a special case of
constraints. And PyMathProg honors that sense, in that
the effect is the same as if it were a constraint. 
Yet, in terms of how things gets done inside, that
simply adds to the list of bounds for *x*, so that
all the bounds are simultaneous (adding a bound to a variable
does *not* cancle any of its previous bounds), 
just like constraints do.

More than two continuous comparisons are not encouraged in
PyMathProg. The major purpose of continuous comparisons
is to set both the lower and the upper bounds for a row,
in which case the two bounds must not contain variables.
However, it is entirely legal to use as many comparisons
as you like, the only caution is that in Python, if
any of the comparison evaluates to a False, all the
later comparisons will not be evaluated, and thus
won't take any effect (i.e. they would not produce 
constraints).


.. _group:


Grouping constraints
--------------------

Sometimes, it is necessary to use a Python variable to 
hold a constraint for later use, for example, to
obtain the dual value for a constraint. This is simple:

>>> begin('model')
model('model') is the default model.
>>> x, y = var('x, y')
>>> R = 3 * x + y >= 5
>>> R
R1: 3 * x + y >= 5
>>> R.name
'R1'
>>> R.name = 'Sugar Level'
>>> R
Sugar Level: 3 * x + y >= 5

Upon creation, a constraint is given a default name 
like this: *R#*, where *#* is the serial number.
Sometimes, it is desirable to change to a more meaningful
name, which can be done by assigning to the *name* property of
a constraint. Of course, it can also be done by employing
the *st(...)* function with the argument for *name* supplied.
Use *help(st)* in an interactive session for more information.
Another more elegant solution is to use a group object to
group desired constraints together. The cool thing about
group objects is that they can automatically name the
constraints by the group name with the index used as subscript.
Here is an illustration of using group objects::

  from pymprog import *
  minlev = group('minlev')
  fruits = ('apple', 'pear', 'orange')
  nutrit = ('fat', 'fibre', 'vitamin')
  ntrmin = ( 10, 50, 30 ) # min nutrition intake
  #nutrition ingredients of each fruit
  ingred = ('apple': (3,4,5), 'pear': (2,4,1),
            'orange': (2,3,4))
  diet = var('diet', fruits, int) 
  for n, ntr in enumerate(nutrit):
     minlev[ntr] = sum( diet[frt] * ingred[frt][n] 
            for frt in fruits) >= ntrmin[n] 

The new stuff here is that we use a group called 'minlev'
to hold the constraints, so *minlev['fat']* would hold
the constraint for minimal level of fat, and that
constraint is also given an informative name "minlev['fat']".
The resultant model would be much easier to understand.

