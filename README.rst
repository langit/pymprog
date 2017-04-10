PyMathProg
==========

*An easy and flexible mathematical programming environment for Python.*

Description
~~~~~~~~~~~

PyMathProg is a pythonic reincarnation of AMPL and GNU MathProg 
modeling language, implemented in pure Python, connecting to GLPK via 
swiglpk. Create, optimize, report, change and re-optimize your model 
with Python, easily integrate database, plotting, etc.

PyMathProg provides an easy and flexible modelling syntax
using *Python* to create and optimize mathematical programming models. 
Optimization is done by open source optimization packages such as
the *GNU Linear Programming Kit (GLPK)* that is made available
to PyMathProg by swiglpk.

Great features offered by PyMathProg include:

    - Ergonomic syntax for modelling 
    - Friendly interactive session
    - Sensitivity report
    - Advanced solver options
    - Automatic model update on parameter changes
    - Parameters sharable between models
    - Deleting variables/constraints
    - Supporting both Python 2 and 3
    - Supporting all major platforms


Installation
~~~~~~~~~~~~

Assuming you already have Python 2 or Python 3 installed, now open a
terminal window (also known as a command window), and type in this 
line of command and hit return::

    pip install pymprog

That's it. Since it is a pure Python project that only depends on swiglpk,
it can be installed this way wherever swiglpk can be installed.
Currently, swiglpk comes with binary wheels for Windows, Mac, and Linux.
If you'd like to have PyMathProg installed on other platforms, 
the only hurdle to overcome is to get swiglpk installed there first.

Example
~~~~~~~

Below is a small example taken from the dive-in turorial
in the `PyMathProg Documentation 
<http://pymprog.sourceforge.net/index.html>`__:

::

  from pymprog import *
  begin('bike production')
  x, y = var('x, y') # variables
  maximize(15 * x + 10 * y, 'profit')
  x <= 3 # mountain bike limit
  y <= 4 # racer production limit
  x + y <= 5 # metal finishing limit
  solve()

Help in the following ways are more than welcome: 
 
1. tutorials and samples. 
2. bug reports 
3. feature requests
4. code contribution 

I hope you will find it useful.
