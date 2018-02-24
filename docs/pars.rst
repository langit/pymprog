
Working with parameters
=======================

Note that the sole purpose of parameters is to change its value
later and see how it would impact the model and its solution.
When the value of a parameter changes, the model will be updated
automatically.
If the value of a parameter never changes, it is better to
get rid of it for the sake of efficiency. However, you may still
want to use it for more meaningful representation of the model.

Creating parameters
-------------------

It is very simple to create parameters. 
Let's illustrate with an interactive Python session:

>>> from pymprog import *
>>> k = par('k', [2, 3, 4])
>>> type(k)
<type 'list'>
>>> k[1]
(k[1]:3)

There is one important property of parameter creation: the original indexing
of the raw values you passed in remains unchanged for the created parameters.
Let's continue with this live illustration:

>>> p = par('P', {'east':0, 'west':2, 'south':3, 'north':1})
>>> type(p)
<type 'dict'>
>>> p['east']
(P['east']:0)

From these examples we see that the function *par(...)* can
create parameters according to the index scheme of the value argument.
It is nice to use *help(par)* to find out the following information::

  Arguments:

  name(required): a str for the name of the parameter(s).

  val(default 0): may take the following types of values:

    1. a single value in (int, long, float) 
       -> a single parameter with the given name a value.
    2. a list/tuple of values -> a list of parameters,
       with names indicating the position index.
    3. a dict of values -> a dict of parameters,
       with names indicating the key index into the dict.
    4. an iterable of values -> same as type 2.

The cool thing about it is that it is recursive:

>>> r = [{(3,4):3, (1,2):4}, 5]
>>> R = par('R', r)
>>> R
[{(1, 2): (R[0][1,2]:4), (3, 4): (R[0][3,4]:3)}, (R[1]:5)]
>>> r[0][3,4]
3
>>> R[0][3,4]
(R[0][3,4]:3)
>>> r[1]
5
>>> R[1]
(R[1]:5)

Finally, you may define several parameters in one call:

>>> par('x, y', 3, 5)
[(x:3), (y:5)]
>>> a, b, c = par('a,b,c', 3, (5,2))
>>> a, b, c
((a:3), [(b[0]:5), (b[1]:2)], (c:0))

Folks, that's pretty much there is to it! 


Changing the value
------------------

From a user's point of view, changing the value of a parameter
is very, very simple, you just do something like this:

>>> p.value = new_value

Since now you are already an insider to PyMathProg, 
we'd like to share with you the things done 
on the backstage for this value change to take effect
throughout the entire model. When this value 
change happens, all related elements that depend
on this value are informed of this change. These
elements will then request the model for update.
The model would simply queque up the requests
until the last moment when the update is needed.
This is done for the sake of performance, 
for updating too eagerly would endup updating
one elements several times if several related 
parameters changes over time. Sometimes
updating could be quite expensive.
This approach is known as lazy update.

There are two distinct kinds of situations 
where updates are needed: 

   1. the time before solving the model: 
      all the elements in the model that
      needs update must be updated.

   2. the time when a the value/property
      of an element is requested, such
      as in an interactive session when
      an object is represented to the user.
      In this case only the requested 
      element is updated (if needed).
 
An example for value change
----------------------------

Here is a small example to show the effect of value changes. 
Sensitivity report is also provided for you to evaluate the result.


.. literalinclude:: ./sensana.py
      :linenos:

If you run this code, the output would be something like this:

.. code-block:: none

   GLPK Simplex Optimizer, v4.60
   2 rows, 3 columns, 6 non-zeros
   *     0: obj =  -0.000000000e+00 inf =   0.000e+00 (3)
   *     2: obj =   2.560000000e+04 inf =   0.000e+00 (0)
   OPTIMAL LP SOLUTION FOUND

   PyMathProg 1.0 Sensitivity Report Created: 2016/12/10 Sat 15:01PM
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
    R1                 93000   0.166667       -inf      93000      60600     121200
    R2                   101        100       -inf        101       77.5        155
   ================================================================================
   GLPK Simplex Optimizer, v4.60
   2 rows, 3 columns, 6 non-zeros
   *     2: obj =   2.570000000e+04 inf =   0.000e+00 (0)
   OPTIMAL LP SOLUTION FOUND

