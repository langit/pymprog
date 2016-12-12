
Working with Indices
======================

Without indices, it is really hard to work with big models:
one has to give each variable a different name. In modern
modeling languages such as AMPL and GMPL, index sets 
are an essential building instrument, which is really not
surprising, as we see indices almost everywhere in advanced
mathematics. PyMathProg also provides a solution
to indexing into variables and constraints.

#. :ref:`natural`
#. :ref:`combined`
#. :ref:`varidx`


.. _natural:

Natural indices
----------------

Python already provides some natural indices: 
tuples, lists, sets(such as the keys in a dict), 
or anything iterable(e.g. a generator, a sequence, etc.).
For an object to become an legitimate index, it has
to be immutable, which means that its value should
not change (in the sense defined by the magic method of
*__eq__*) during its entire life cycle. By the tacit
contract between objects in Python, objects of equal
value should also produce the same hash code, thus 
immutable objects have a constant hash code,
which is used for indexing purposes to quickly locate
an object in a set or dict.

PyMathProg trusts you to provide a list, a tuple, a set, 
a dict (in such case only the keys are used for indices),
or any iterable as a set of indices without repeated elements.
They can be utilized in PyMathProg as indices
for variables, constraints, and parameters.
If your put duplicate indices there, things could get lost.

.. _combined:

Combined indices
----------------

PyMathProg also provides a way to combine smaller index sets
into bigger ones by the concept of set product. Given two sets
A and B, the product of A * B is defined as::

   A * B = { (a,b) : a in A, b in B }

In the pymprog module, there is a class to achieve this::

  >>> from pymprog import *
  >>> A = (1, 2, 3)
  >>> B = (6, 7, 8)
  >>> C = iprod(A,B)
  >>> for c in C: print(c)
  ... 
  (1, 6) (1, 7) (1, 8) (2, 6) (2, 7) (2, 8) (3, 6) (3, 7) (3, 8)

Well, that's about it. By the way, the constructor *iprod(...)* 
can take as many iterables (sets, lists, tuples, or sequences) 
as you want -- that's the cool part of it.


.. _varidx:

Use index with variables
-------------------------

It is simple to create many variables over some indices in PyMathProg.
Let's continue the Python session above::

  >>> begin('test')
  >>> x = var('x', C)
  >>> type(x)
  <type 'dict'>
  >>> x[2,7].name
  'x[2,7]'

So we use the combined set C as the index set to create variables, 
the major variable name is 'X'. 
Out of curiosity, we want to know the type of the python object 
referenced by 'x': it turns out to be a dict type -- probably that 
is not that important anyway, what is more important is how easily 
and intuitively it is indexed, as shown in the next line.

