Working with variables
======================

Once the model is created, you need variables
to make the objective and the constraints. 
In this section we talk about
how to create and work with variables.

#. :ref:`create`
#. :ref:`bounds`

.. _create:

Creating variables
--------------------

The routine *var(...)* is the only tool to create variables.
Yet there are quite a few different ways to do so, depending
on the modelling situation. For the sake of communication,
a variable name must be provided when you create them.
You can create a single variable, or quite a few,
or even a huge group of variables at once. 
These scenarios are illustrated below:

>>> from pymprog import *
>>> begin('test')
model('test') is the default model.
>>> X = var('X')
>>> X # by default, it is non-negative and continuous
X >= 0 continuous
>>> x, y = var('x, y') # many names -> many vars
>>> x, y 
(x >= 0 continuous, y >= 0 continuous)
>>> z = var('z', 3) 
>>> z # an array of 3 variables
[z[0] >= 0 continuous, z[1] >= 0 continuous, z[2] >= 0 continuous]
>>> z[2] # access the third variable
z[2] >= 0 continuous
>>> v = var('v', kind=bool) # 0/1 variable
>>> v
0 <= v <= 1 binary
>>> w = var('w', bounds=(0,5)) # specify the bounds
>>> w
0 <= w <= 5 continuous
>>> colors = ('red', 'green', 'blue') # index set
>>> clr = var('color', colors, bool) # using an index set
>>> clr # a dictionary with keys from the index set
{'blue': 0 <= color['blue'] <= 1 binary, 'green': 0 <= color['green'] <= 1 binary, 
'red': 0 <= color['red'] <= 1 binary}
>>> clr['green']
0 <= color['green'] <= 1 binary

That interactive session demostrates different ways to use 
the function *var(...)* to create variables. Of course 
you may combine those ways to get things done efficiently.
Basically, there are three conventions for variable creation:

1. provide all the names literally, in a single string using
   commas to separate them, to manually create
   a few variables, usally for small models.
2. provide one single name, and a positive integer, to 
   create an array of variables indexed by integers.
3. provide one single name, and a set of indices, to
   create a dictionary with keys from the index set.

Once you decide to follow one convention, then you may 
further customize the variables by furnishing values
for the other arguments to the function call:

   - kind: specify what kind of variable to make.
     admissable values are:

          1. float (default): continuous
          2. int: integer
          3. bool: binary, side-effect: reset bounds to (0,1)

   - bounds: a pair of numbers, for the lower and upper bounds.
     If None is used, it means unbounded. The default value
     is (0, None), so the lower bound is 0, upper bound is none.

Note, you may also obtain help within the Python session by:

>>> help(var) # obtain help on this function

.. _bounds:

Change bounds and kind 
----------------------

Once you have created variables, you may further explicitly set
bounds on some variables, it is qutie straight forward:

>>> begin('test')
model('test') is the default model.
>>> x = var('x')
>>> x <= 5
0 <= x <= 5 continuous
>>> x >= 2
2 <= x <= 5 continuous
>>> x == 3
(x==3) continuous
>>> x == 4
4 <= x <= 3 continuous
>>> z = var('z', 3)
>>> b = [5, 8, 3]
>>> for i in range(3): z[i] <= b[i]
... 
0 <= z[0] <= 5 continuous
0 <= z[1] <= 8 continuous
0 <= z[2] <= 3 continuous

The most important thing to remember is this: bounds added 
by using '<=', '>=', and '==' are accumulative. Later bounds
won't invalidate former bounds. That is why when we set
*x == 4* after *x == 3* we got infeasibility: *4 <= x <= 3*.
It is possble to cancle all previous bounds and start anew.
Continue from where we have left off in the last Python session:

>>> x.reset(1, 5)
1 <= x <= 5 continuous
>>> x <= 10
1 <= x <= 5 continuous
>>> x.reset()
x >= 0 continuous
>>> x <= 10
0 <= x <= 10 continuous

This new interactive session below shows the interaction between 
kinds and bounds. The key concept behind all this is that a binary
variable is *defined* as an integer variable between 0 and 1.

>>> begin('test')
model('test') is the default model.
>>> x = var('x')
>>> x.kind = int
>>> x
x >= 0 integer
>>> x <= 1
0 <= x <= 1 binary
>>> x.reset(0, 5)
0 <= x <= 5 integer
>>> x.kind = bool
>>> x
0 <= x <= 1 binary
>>> x.kind = int
>>> x
0 <= x <= 1 binary
>>> x.kind = float
>>> x
0 <= x <= 1 continuous

We may also use parameters for bounds, in such case, when the
parameters change value, the bounds get updated automatically.

>>> p = par('p', 3)
>>> p
(p:3)
>>> begin('test')
model('test') is the default model.
>>> x = var('x')
>>> x <= p
0 <= x <= (p:3) continuous
>>> p.value = 4
>>> x
0 <= x <= (p:4) continuous
>>> x.bounds
(0, 4)

The last line of code obtains the numerical value of bounds. 
We will discuss parameters in more details in a later section.
