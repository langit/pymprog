#**************************************************************************

#PyMathProg is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 3 of the License, or
#(at your option) any later version.

#PyMathProg is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with PyMathProg. If not, see <http://www.gnu.org/licenses/>.

#**************************************************************************

#This file is part of PyMathProg.
#Author: Yingjie Lan, Email: ylan@pku.edu.cn

#### { for both python 2 and 3 
#Cheat Sheet: Writing Python 2-3 compatible code
#http://python-future.org/compatible_idioms.html
#>>>Minimum versions
#     * Python 2: 2.6+
#     * Python 3: 3.3+
#from __future__ import division #since 2.2
from __future__ import print_function 

#from past.builtins import long
import sys
if sys.version_info > (3,):
     long = int

def _with_metaclass(mcls):
    def decorator(cls):
        body = vars(cls).copy()
        # clean out class body
        body.pop('__dict__', None)
        body.pop('__weakref__', None)
        return mcls(cls.__name__, cls.__bases__, body)
    return decorator
   
#### for both python 2 and 3 }

try: import swiglpk as glpk
#pymprog only depends on swiglpk
except:
    print('''
The module swiglpk is missing in python.
Try this command to have it installed:

pip install swiglpk>=1.3.3

Note: assume you have already installed pip,
a package installation tool for python.
''')
    import sys
    sys.exit(1)

##### Utility functions ####
 
def evaluate(expr):
   """return the value of an expression
when all its variables take their primal values."""
   return expr.evaluate() if isinstance(expr, _parex)\
      else expr.primal if isinstance(expr, _var)\
      else expr.value if isinstance(expr, _proxy)\
      else expr #unchanged

def subscript(t, top=True):
    '''convert t into a compact subscription.'''
    if type(t) in (list, tuple, dict, set):
        ret = ','.join(subscript(tt,False) for tt in t)
        return ret if top else '(%s)'%ret
    if type(t) is str:
        return '_'.join(repr(t).split())
    return str(t)

####### Class Definitions ####
class group(object):
    '''a holder to hold a group of constraints. 
it uses __setitem__ to accomplish two things at one time:
1. hold an object by the index
2. use the index to set a name for the constraint
'''
    def __init__(me, group, desc=None):
        me.group = group #the group name
        me.templ = desc #template for description
        me.dict = {}

    def description(me, *index):
        return me.templ.format(*index, 
            name=me.name(*index)) if me.templ else None
    desc = description #alternative method name

    def name(me, *index):
        return '%s[%s]'%(me.group, subscript(index))

    def __setitem__(me, index, e):
        assert isinstance(e, _cons) 
        e.name = me.name(*index) if isinstance(index, 
            tuple) else me.name(index)
        me.dict[index] = e

    def __getitem__(me, index):
        return me.dict[index]

#below is how to do mixed indexing with dictionary
# x = {(3,'h'):6, (5,'k'):5}
# x[3,'h']

#this can be replaced by something in itertools
class iprod(object): 
   """index product: given a list/tuple of sets, 
   enumerate all combinations as tuples."""
   def __init__(self, *args): 
      self._llist =  args
      self._sofar = []

   def __iter__(self): 
      return self.next() 

   def next(self): 
      for idx in self._llist[len(self._sofar)]:
         self._sofar.append(idx)
         if len(self._sofar)==len(self._llist):
            yield tuple(self._sofar)
         else:
            for v in self.next(): yield v
         self._sofar.pop()

   def __len__(self):
       ret = 1
       for i in self._llist: ret *= len(i)
       return ret

class _guard(object):
   def __init__(me, model, updater):
       me.m = model
       me.up = updater

   @property
   def bounds(me): 
       return me.up.vbounds(True)

   def used(me):
       me.m.replace_last(id(me))
       return me

   def __nonzero__(me):
       'this is called with something like 3 <= me <= 20.'
       if me.m.replace_last(None) != id(me):
           me.m.replace_last(me)
       return True

   def value_changed(me, p):
       me.update(False)

   def update(me, now):
       if now: # immediately
           me.m.update1(me.up)
       # lazy update: model decides when
       else: me.m.add_lazy(me.up)

   def listen(me, real=True):
      """register for possible changes."""
      for d in me.up.data(): #bounds list
          me.listen2(d, real)

   def listen2(me, expr, real=True):
      """register for possible changes."""
      def check(x): return isinstance(x,_proxy)
      if check(expr): 
          expr.register(me, real) 
          return
      if not isinstance(expr, _exup):
          return
      for p in expr.preorder(check):
          p.register(me, real)

   def free(me, n=None): # free from bounds
       '''set it all free if n is None. 
otherwise delete only the n-th bound.'''
       assert me.up.id
       me.listen(False)
       if n is None:
            me.up.blist = []
       else: del me.up.blist[n]
       me.update(False) 
       me.listen(True)
       return me

   def reset(me, lo=0, hi=None):
       '''reset the bounds to lo and hi, 
all previous bounds are lost.'''
       assert me.up.id
       assert isConst(lo) and isConst(hi)
       me.listen(False)
       me.up.blist = [(lo, hi)]
       me.update(False) 
       me.listen(True)
       return me

class _bnds(object): # as updater
   'class for bound management.'
   def addbounds(me, lo, hi, merge):
      for i in lo, hi: 
          assert isConst(i)
      if not merge or not me.blist:
          me.blist.append((lo, hi))
          return # the simple way

      # try to merge...
      a,b = me.blist[-1]
      if lo is None and b is None:
           lo = a #b also discarded
           me.blist.pop()
      if hi is None and a is None:
           hi = b #a also discarded
           me.blist.pop()
      me.blist.append((lo, hi))

   pinf = float('+inf')
   ninf = float('-inf')
   def vbounds(me, nobt=False):
       """value of bounds"""
       lo = max(v.value if type(v) in (_proxy, _parex) else 
               me.ninf if v is None else v
               for v, _ in me.blist) if me.blist else me.ninf
       hi = min(v.value if type(v) in (_proxy, _parex) else
               me.pinf if v is None else v
               for _, v in me.blist) if me.blist else me.pinf
       #if lo > hi: raise Exception("Bound error: %s"% str(me))
       if nobt: return lo, hi
       if lo == hi: bt = glpk.GLP_FX
       elif hi == me.pinf and lo != me.ninf: 
           bt = glpk.GLP_LO
       elif lo == me.ninf and hi != me.pinf: 
           bt = glpk.GLP_UP
       elif lo == me.ninf and hi == me.pinf: 
           bt = glpk.GLP_FR
       else: bt = glpk.GLP_DB
       return bt, lo, hi 

   def collect(me):
       'collect bounds into lo and hi sets'
       llist, hlist, beq = [], [], []
       ml, mh = me.ninf, me.pinf
       for lo, hi in me.blist:
            if type(lo) in (int, float, long):
               ml, lo = max(ml, lo), None
            if type(hi) in (int, float, long):
               mh, hi = min(mh, hi), None
            if lo is not None:
                if lo is not hi: 
                    llist.append(lo) 
                else: beq.append(lo)
            if hi is not None: 
                if hi is not lo: 
                    hlist.append(hi) 
       if ml == mh: beq.append(ml)
       else:
          if me.ninf < ml: llist.append(ml)
          if mh < me.pinf: hlist.append(mh)
       return llist, beq, hlist

   def repr(me, expr):
       'represent expr with bounding conditions.'
       llist, beq, hlist = me.collect()
       eq, lo, hi = len(beq), len(llist), len(hlist)
       if not (eq+lo+hi): return expr+" free"
       if eq: expr = '(%s==%s)'%(expr, subscript(beq))
       if lo and not hi: # throw lb to the right
          return "%s >= %s"%(expr, subscript(llist))
       lo = '' if not lo else subscript(llist)+' <= '
       hi = '' if not hi else ' <= '+subscript(hlist)
       return '%s%s%s'%(lo, expr, hi)

class _vbup(_bnds):
   'variable updater'
   def __init__(me, id, lo, hi):
       assert id
       me.id = id
       me.blist = [(lo, hi)]

   def data(me):
        for l, h in me.blist:
            yield l
            yield h

   def primal(me, m):
       return (None if not m._solved else 
               m.mip_col_val(me.id)
                if m._solved == 'intopt' else
               m.get_col_prim(me.id) )

   def dual(me, m):
       return (None  if not m._solved else 
               m.get_col_dual(me.id)
            if m._solved != 'intopt' else None)

   def update(me, m): #bounds
       '''update the bounds of a variable.
as of glpk v4.60, it is known that when a
binary variable is set to a fixed value,
its kind will become integer.'''
       if me.id: m.set_col_bnds(me.id, *me.vbounds())
        
class _bexp(_bnds):
    'bounded expression.'
    def __init__(me, id, lo, expr, hi):
        assert id > 0
        me.id = id
        gut=lambda x: x.up if isinstance(x, _math) else x
        me.blist = [(gut(lo), gut(hi))]
        me.expr = gut(expr)

    def data(me):
        for l, h in me.blist:
            yield l
            yield h
        yield me.expr

    def primal(me, m):
        return (None if not m._solved else
                m.mip_row_val(me.id)
                  if m._solved == 'intopt' else
                m.get_row_prim(me.id))

    def dual(me, m):
        return (None if not m._solved else
                m.get_row_dual(me.id) 
              #not sure about interior point method
                if m._solved != 'intopt' else None)

    def update(me, m): #update row (usually before solve)
       if not me.id: return #deleted
       rex = me.expr.linearize()
       assert type(rex) is _linexp,\
              "Error: constraint has no variables."
       exprconst = rex.const
       bt, lo, hi = me.vbounds()
       lo -= exprconst #_linexp
       hi -= exprconst #_linexp
       mat = rex.matrix()
       n = len(mat)
       cidx = glpk.intArray(1+n) 
       cval = glpk.doubleArray(1+n) 
       for i in range(n):
           cidx[1+i], cval[1+i] = mat[i]
       m.set_mat_row(me.id, n, cidx, cval)
       m.set_row_bnds(me.id, bt, lo, hi)

    #def update_bounds(me, m): #bounds
    #   bt, lo, hi = me.vbounds()
    #   lo -= me.exprconst #_linexp
    #   hi -= me.exprconst #_linexp
    #   m.set_row_bnds(me.id, bt, lo, hi)

    def __repr__(me):
       return me.repr(repr(me.expr))


class _cons(_guard):
    def __init__(me, id, lo, expr, hi): 
        me.m = expr.m
        me.up = _bexp(id, lo, expr, hi)
        me.update(False) 
        me.name  = "R%i"%id
        me.listen()

    def delete(me):
       assert me.m and me.up
       m = me.m
       me.listen(False)
       me.m.lazy.discard(me.up)
       me.m.del1row(me.up.id)
       me.up.id = 0
       me.m, me.up = None, None

    def boundby(me, lo, hi): #constrain
        '''assume this is always called when adding 
another bound in continuous comparisons.'''
        me.up.addbounds(lo, hi, True) #merge to prev
        #me.up.update_bounds(me.m)
        me.update(False) 
        me.listen2(lo)
        me.listen2(hi)
        return me
    
    @property
    def status (me): 
        return me.m.get_row_stat(me.up.id)

    #@property
    #def bounds(me): 
    #    return me.up.vbounds()[1:]
              #(me.m.get_row_lb(me.up.id),
              #me.m.get_row_ub(me.up.id))

    @property
    def primal(me): return me.up.primal(me.m)

    @property
    def dual (me): return me.up.dual(me.m)
 
    @property
    def name(me): 
        return me.m.get_row_name(me.up.id)

    @name.setter
    def name(me, name): 
        me.m.set_row_name(me.up.id, name)

    def __repr__(me): 
        return '%s: %s'%(me.name, 
            me.up.repr(repr(me.up.expr)))


class _math(object):
   """The base class for _var, _param, _parex.
The main functionality is to provide numerical type support,
so that the subclasses can be operated by operators like
'+', '-', '*', '/', '**'."""

   _good_types =  (int, long, float, type(None))
   def _bad_type(me, b):
       return type(b) not in me._good_types\
           and not isinstance(b, _math)

   def __add__(me, b):
       if me._bad_type(b): return NotImplemented
       if type(b) in (int, float, long) and b==0:
          return me
       return _parex(me, '+', b)

   def __radd__(me, b):
       if me._bad_type(b): return NotImplemented
       if type(b) in (int, float, long) and b==0:
          return me
       return _parex(b, '+', me)

   def __mul__(me, b):
       if me._bad_type(b): return NotImplemented
       if type(b) in (int, float, long) and (b==1 or b==-1):
          return me if b>0 else -me
       return _parex(me, '*', b)

   def __rmul__(me, b):
       if me._bad_type(b): return NotImplemented
       if type(b) in (int, float, long) and (b==1 or b==-1):
          return me if b>0 else -me
       return _parex(b, '*', me)

   def __sub__(me, b):
       if me._bad_type(b): return NotImplemented
       if type(b) in (int, float, long) and b==0:
          return me
       return _parex(me, '-', b)

   def __rsub__(me, b): # b - me
       if me._bad_type(b): return NotImplemented
       if type(b) in (int, float, long) and b==0:
          return - me
       return _parex(b, '-', me)

   def __div__(me, b):
       if me._bad_type(b): return NotImplemented
       if type(b) in (int, float, long) and (b==1 or b==-1):
          return me if b>0 else -me
       return _parex(me, '/', b)

   def __truediv__(me, b):
       if me._bad_type(b): return NotImplemented
       if type(b) in (int, float, long) and (b==1 or b==-1):
          return me if b>0 else -me
       return _parex(me, '/', b)

   def __rdiv__(me, b): #since me could be a const
       if me._bad_type(b): return NotImplemented
       if type(b) in (int, float, long) and (b==1 or b==-1):
          return me if b>0 else -me
       return _parex(b, '/', me)

   def __pos__(me): 
       return _parex(0, 'ps', me)

   def __neg__(me):
       return _parex(0, 'ng', me)

   def __pow__(me, b):
       return _parex(me, '**', b)

def isConst(b):
       if b is None: return True
       if type(b) in (int, float, long, _param): 
          return True
       if isinstance(b, _parex): 
          return b.isConst()
       if isinstance(b, _var):
          return False
       assert True == False

class _proxy(object): # value proxy
        def __init__(me, n, v, par):
            me.name = n
            me.value = v
            import weakref
            me.par = weakref.ref(par)

        def __repr__(me):
            return '(%s:%g)'%(me.name, me.value)

        def register(me, client, real):
            """register as clients/listeners."""
            par = me.par()
            if not par: return
            #print(par, type(client), client) #, hash(client))
            clid = id(client)
            if real: par.clients[clid] = client
            else: del par.clients[clid]
            # unregister as clients/listeners.
            # what if registered multiple times? solution:
            # after unregister, the client must re-register to all!

class _param(_math):
   """A parameter, whose value may be changed,
When a parameter changed in value, it will 
add it self to the class owned dirty list.
Each param also maintains its own list of listeners. 
The listeners can be _parex or variable objects.
A class method is also provided to fire off the
updating process.

To avoid loop reference, a param holds a value proxy,
and hands it out during operations. 
The proxy holds the param value, so the value is 
updated directly.
"""
   #def __iadd__(me, b): 
   #    raise Exception("Bad opperation!")

   #def __isub__(me, b): 
   #    raise Exception("Bad opperation!")

   #def __imul__(me, b): 
   #    raise Exception("Bad opperation!")

   #def __idiv__(me, b): 
   #    raise Exception("Bad opperation!")

   #def __ipow__(me, b):
   #    raise Exception("Bad opperation!")

   def __init__(me, name, val=None):
      '''When a param changes, clients using it might wish to 
be informed of the chanage and update itself. 
typical clients are instances of the class _var and _parex.
as both variable and _parex redefine the __eq__ method,
which always returns a true value(for we abused it
to express constraints and bounds, and if false value is returned,
later continuous comparisons will be ignored by reason of the 
short circuiting of logic and operation), we can't define
__hash__ in a way that makes sense. for example,
when two different instances collide by reason of 
the hash value in a set, usually the hash values 
of them are compared first, if the have the same
hash value, then the __eq__ method is used to 
decide whether they are of the same value (maybe 
their ids are compared right before __eq__ method). 
If that's how set is implemented in Python, 
then we can simply use id(self) for the hash value 
and the abused __eq__ method will never be called.
the experiment below shows that this is indeed the case:

>>> s = set()
>>> class hashtest:
    ...   def __init__(me, hv): me.hv = hv
    ...   def __hash__(me): return me.hv
    ...   def __eq__(me, ot): return True
    ... 
s = set(hashtest(i) for i in range(1000000))
>>> len(s)
1000000
>>> class ht2:
    ...   def __eq__(me, ot): return True
    ...   def __hash__(me): return id(me)
    ... 
>>> s = set(ht2() for i in range(500000))
>>> len(s)
500000
>>> 

To be absolutely safe, one might suggest to register a proxy
of a variable or constrained _parex for param changes.
but loop ref will be formed as the proxy holds a ref to 
a variable or _parex, which also holds a ref to its proxy.

The final solution is to have a dict using the client's id as keys 
for that client.
'''
      if type(val) not in (int, float, long):
        raise Exception("Bad parameter value!")
      me.clients = dict() #loop refs? value proxy
      # value proxy, weakref to me, no loop refs!
      me.up = _proxy(name, val, me)

   def __str__(me):
       return 'param(%s)'%me.name if me.name else 'param(v=%g)'%me.value

   @property
   def name(me): return me.up.name

   @name.setter
   def name(me, val): me.up.name = val

   @property
   def value(me): return me.up.value

   @value.setter
   def value(me, val): 
       if val == me.up.value: return
       me.up.value = val
       for i, c in me.clients.items():
           c.value_changed(me)

   def __repr__(me): 
      return repr(me.up)

   spid = 0
   @classmethod
   def par(me, name, val=0):
      '''Creating parameters according to the
index scheme of the value argument.

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
'''
      if not isinstance(name, str):
         # backward compatability
         print("Deprecated call to par(.):"
             " name should be the first argument.")
         name, val = val, name
         if name is None:
            _param.spid += 1
            name = "P%d"% _param.spid
      assert name # non-empty
      if type(val) in (int, long, float):
         return _param( name, val )
      if type(val) in (list, tuple):
         return [me.par("%s[%d]"%(name, i), v) for 
           i,v in enumerate(val)]
      if type(val) == dict: 
         pp = val.copy(); name += "[%s]"
         for t in val: 
            pp[t] = me.par(name%subscript(t), val[t])
         return pp
      #assume to be something iterable (generator, set, ...):
      #however, if v is a string, umlimited recursion results
      return me.par(name, [v for v in val]) 

par = _param.par #global version

class _var(_math, _guard):
   """Represents a variable. 
Set bounds using A <= x <= B.
If A or B is an expression containing parameters, 
the bounds will be updated if the parameters changes.
To fix a variable at constant C, simply use x == C.
It is possible to set bounds several times:
    A1 <= x <= B1
          x <= B2
the result is: A1 <= x <= B2
"""

   def __init__(me, model, cid, name=None, kind=float, bounds=(0,None)):
       'to make a free variable, let bounds = (None, None)' 
       me.m = model
       me.up = _vbup(cid, *bounds)
       me.update(False)
       me.listen()
       #note: if kind=bool, then bounds<-(0,1)
       me.kind = kind #must follow set_bounds
       me.name = str(name) if name else "X%d"%cid
       #me.flag = 0 #if compared to constants, if been tested


   def boundby(me, lo, hi, merge): # add bounds to _var
        if merge: me.used() # don't register as last comparison
        me.up.addbounds(lo, hi, merge)
        me.update(False)
        me.listen2(lo)
        me.listen2(hi)
        return me

   #@property
   #def bounds(me): 
   #    return (me.m.get_col_lb(me.up.id),
   #            me.m.get_col_ub(me.up.id))

   kindmap2py = {glpk.GLP_CV:float, 
      glpk.GLP_IV:int, glpk.GLP_BV:bool}
   @property
   def kind(me): 
      me.update(True)
      kind = me.m.get_col_kind(me.up.id)
      return me.kindmap2py[kind]

   kindmap2glpk = {float:glpk.GLP_CV,
               int:glpk.GLP_IV, bool:glpk.GLP_BV}
   @kind.setter
   def kind(me, kind): 
       if kind is bool: me.reset(0,1)
       kind = me.kindmap2glpk[kind]
       me.m.set_col_kind(me.up.id, kind)

   @property
   def status(me): 
       return me.m.get_col_stat(me.up.id)

   @property
   def primal(me): return me.up.primal(me.m)

   @property
   def dual(me):  return me.up.dual(me.m)

   @property
   def name(me): return me.up.name

   @name.setter
   def name(me, name): 
      me.m.set_col_name(me.up.id, name)
      me.up.name = name

   _var_kinds = {float:'continuous', 
        int:'integer', bool:'binary'}

   def __repr__(me):
       kind = me._var_kinds[me.kind] #me.update(True)
       return '%s %s'%(me.up.repr(me.name), kind)

   #def __str__(me):
   #    return "%s=%r"%(me.name, me.primal)

   def __le__(me, b):
       c = me.m.replace_last(None)
       if me._bad_type(b): return NotImplemented
       if isConst(b):
          return me.boundby(None, b, c is me)
       return me.m.newcon(None, me-b, 0).used()

   def __ge__(me, b): 
       c = me.m.replace_last(None)
       if me._bad_type(b): return NotImplemented
       if isConst(b):
          return me.boundby(b, None, c is me)
       return me.m.newcon(0, me-b, None).used()

   def __eq__(me, b):
       c = me.m.replace_last(None)
       if me._bad_type(b): return NotImplemented
       if isConst(b):
          return me.boundby(b, b, c is me)
       return me.m.newcon(0, me - b, 0).used()

   def delete(me):
       assert me.m and me.up
       m = me.m
       if not m: return
       me.listen(False)
       me.m.lazy.discard(me.up)
       m.del1col(me.up.id) # different
       me.up.id = 0
       me.m, me.up = None, None

class _obj(_guard):
    
   def __init__(me, model, max, expr, name):
       me.m = model
       me.up = _obup(expr)
       me.update(False)
       me.name = name
       me.max = max
       me.listen()

   @property
   def name(me): return me.m.get_obj_name()
   @name.setter
   def name(me, name):
       me.m.set_obj_name(name)

   @property
   def max(me): return me.m.get_obj_dir()==glpk.GLP_MAX
   @max.setter
   def max(me, max):
       me.m.set_obj_dir(glpk.GLP_MAX if max else glpk.GLP_MIN)

   @property
   def min(me): return me.m.get_obj_dir()==glpk.GLP_MIN
   @min.setter
   def min(me, min):
       me.m.set_obj_dir(glpk.GLP_MIN if min else glpk.GLP_MAX)

   def __repr__(me):
       name = me.name or ''
       max = "Max" if me.max else "Min"
       return "%s %s: %r"%(max, name, me.up.expr)

class _obup(object):
   """An objective, which takes care of automatic update."""
   id = 0 #for all instances, see _guard.free
   def __init__(me, expr):
       me.expr = expr.up

   def data(me): yield me.expr
       
   def update(me, m):
       expr = me.expr.linearize()
       assert type(expr) is _linexp,\
          "Error: objective degenerated to a constant."
       #if not isinstance(expr, _linexp):
       #   return m.set_obj_coef(0, expr) #_linexp
       for i, c in expr.mat:
           m.set_obj_coef(i, c) 
       m.set_obj_coef(0, expr.const) #_linexp

class _exup(object):
   def __init__(me, left, op, rite):
      gut=lambda x: x.up if isinstance(x, _math) else x
      me.left = gut(left)
      me.op = op #must be str 
      me.rite = gut(rite)

   @staticmethod
   def pretty_push(expr, op, nodes):
      def priority(op):
         if op in ('<=', '>=', '=='):
            return -1
         return ['+','-','*','/','ps','ng','**'].index(op)//2

      if isinstance(expr, _exup):
         if priority(expr.op) < priority(op):
            nodes.append(')')
            nodes.append(expr)
            nodes.append('(')
         else: nodes.append(expr)
      else: nodes.append(expr)

   def pinorder(me):
      """pretty inorder traversal for print."""
      nodes = [me] #for tree traversion
      while nodes:
         cur = nodes.pop() #explore
         if not isinstance(cur, _exup):
            yield cur; continue
         me.pretty_push(cur.rite, cur.op, nodes)
         nodes.append(cur.op)
         if cur.op in ('ps','ng'): continue
         me.pretty_push(cur.left, cur.op, nodes)

   def __repr__(me):
      ret = []
      for i in me.pinorder():
         assert type(i) in (str, int, long, float, 
                _proxy, _vbup, _exup)
         if type(i) is _vbup:
            ret.append( i.name )
         elif i in ('ps', 'ng'): 
            ret.append({'ps':'+','ng':'-'}[i])
         elif type(i) is str:
            ret.append( i )
         else: ret.append(repr(i))
      return ' '.join(ret)

   def __str__(me):
      cols = {}
      def check(x): return isinstance(x, _vbup)
      for v in me.preorder(check): 
         cols[v.up.id] = v
      lexp = me.linearize()
      return lexp.tostr(cols)

   def preorder(me, check=lambda x:True):
      """reversed preorder traversal."""
      nodes = [me] #for tree traversion
      while len(nodes)>0:
         cur = nodes.pop() #explore
         if not isinstance(cur, _exup):
            if check(cur): yield cur
            continue
         nodes.append(cur.op)
         nodes.append(cur.left)
         nodes.append(cur.rite)

   import operator
   operations_map = { #switch(t) 
            '+': operator.add, #lambda a,b: a+b,
            '-': operator.sub, #lambda a,b: a-b,
            '*': operator.mul, #lambda a,b: a*b,
            # to avoid integer division
            '/': operator.truediv, #lambda a,b: (a+0.0)/b, 
            '**': operator.pow, #lambda a,b: a**b,
            '<=': operator.le, #lambda a,b: a<=b,
            '>=': operator.ge, #lambda a,b: a>=b,
            '==': operator.eq, #lambda a,b: a==b,
            'ps': lambda a,b: +b,
            'ng': lambda a,b: -b
          } 

   def linearize(me, m=None): 
       """
convert this expression to a _linexp.

Args:
   m (model): 
       when None, a _linexp is constructed.
       when a model instance, a variable takes its primal value.
  returns: a _linexp or a number.
"""
       stack = []
       for t in me.preorder():
          #assert not isinstance(t, _param)
          if type(t) in (int, float, long):
             stack.append(t)
          elif isinstance(t, _proxy):
             stack.append(t.value)
          elif isinstance(t, _vbup):
             if not t.id: stack.append(0.0) #deleted
             else: stack.append(_linexp(t)
               if m is None else t.primal(m))
          else: stack.append( 
                    me.operations_map[t](
                        stack.pop(), stack.pop()
                    )
                )
       assert len(stack)==1
       return stack[0]

class _parex(_math):
   """expression that can take parameter objects.
When parameters change, _parex sits in the middle
to have the model updated.
"""

   def __init__(me, left, op, rite):
      ml = None if isConst(left) else left.m
      mr = None if isConst(rite) else rite.m
      assert ml is None or mr is None or ml is mr
      me.m = ml or mr

      me.up = _exup(left, op, rite) 

   def __repr__(me): return me.up.__repr__()

   def isConst(me): return me.m is None

   #def within(me, p=None):
   #    check = lambda x: isinstance(x, _var)
   #    for v in me.preorder( check ):
   #        if not p: p = v.m
   #        assert p is v.m
   #    return p


   #the value when the _parex is a constant 
   @property
   def value(me): 
       assert me.m is None
       return me.up.linearize()

   def evaluate(me): 
       """
evaluate this expression to a number with
variables taking their primal values.
"""
       return me.up.linearize(me.m)

   def __le__(me, b): #me <= b
       """
   when you have something like this:
     rex = (expr1 <= expr2 <= expr3)
   the rex gets 'expr2 <= expre3',
   and the constraint 'expr1 <= expr2' is lost
   (when expr1 or expr3 contains variables, 
    the constraint is not well defined).
   However, if expr1 and expr3 are CONSTANTS,
   such as: 0 <= expr <= 3, then nothing is lost.
   'expr' must be an _parex that is not a constant."""
       if me._bad_type(b): return NotImplemented
       if isConst(me):
          return me.value <= b if isConst(b) else b >= me
       c = me.m.replace_last(None)
       if not isinstance(c, _cons): c = None
       if isConst(b):
           if c and c.up.expr is me.up:
               return c.boundby(None, b).used()
           return me.m.newcon(None, me, b)
       expr = me-b
       return expr.m.newcon(None, expr, 0).used()

   def __ge__(me, b): # me >= b
       if me._bad_type(b): return NotImplemented
       if isConst(me): 
          return me.value >= b if isConst(b) else b <= me
       c = me.m.replace_last(None)
       if not isinstance(c, _cons): c = None
       if isConst(b):
           if c and c.up.expr is me.up:
                return c.boundby(b, None).used()
           return me.m.newcon(b, me, None)
       expr = me-b
       return expr.m.newcon(0, expr, None).used()

   def __eq__(me, b):
       if me._bad_type(b): return NotImplemented
       if isConst(me): 
          return me.value == b if isConst(b) else b == me
       c = me.m.replace_last(None)
       if not isinstance(c, _cons): c = None
       if isConst(b):
           if c and c.up.expr is me.up:
                return c.boundby(b, b).used()
           return me.m.newcon(b, me, b)
       expr = me-b
       return expr.m.newcon(0, expr, 0).used()

class _linexp(object): #linear expressions
   """class _linexp for pymprog.
   this class facilitates constraints evaluation.
   """

   def __init__(me, var=None, coef=1.0):
       me.const = 0
       me.mat = []
       if var is not None: 
          me.mat.append((var.id, coef))

   def matrix(me): #get the corresponding matrix row
       return me.mat # all nonzero entries

   def copy2(me, u):
      u.const= me.const
      u.mat = me.mat[:]

   def tostr(me, cols):
       ret, s = '', ''
       for i,cf in me.mat:
           cf = s if cf==1 else '- ' if cf==-1 else\
              "%s%g "%(s,cf) if cf>=0 else "%g "%cf
           ret += "%s%s"%(cf, cols[i].name)
           s = '+ ' # after first item, use '+'
       if me.const < 0: ret += str(me.const)
       if me.const > 0: ret += '+' + str(me.const)
       return ret

   def _bad_type(me, b):
       return type(b) not in (int, float, long, _linexp)

   #If one of those methods does not support the operation with 
   #the supplied arguments, it should return NotImplemented.
   def __add__(me, be):
       if me._bad_type(be): return NotImplemented
       rex = _linexp()
       if type(be) in (int, long, float):
          me.copy2(rex)
          rex.const += be
          return rex
       #assert type(b) == _linexp:
       ma, mb, mc = me.mat, be.mat, rex.mat
       na, nb  = len(ma), len(mb)
       a, b = 0, 0
       while a<na or b<nb:
           if b==nb or a<na and ma[a][0] < mb[b][0]:
               mc.append(ma[a]); a += 1; continue
           if a==na or b<nb and mb[b][0] < ma[a][0]:
               mc.append(mb[b]); b += 1; continue
           if a<na and b<nb and ma[a][0] == mb[b][0]:
               v = ma[a][1]+mb[b][1]
               #if v: mc.append((ma[a][0], v)) 
               mc.append((ma[a][0], v)) #don't eliminate!
               a += 1; b += 1
       rex.const = me.const + be.const
       return rex

   def __radd__(me, b):
       if me._bad_type(b): return NotImplemented
       return me + b

   def __mul__(me, b):
       if type(b) not in (int, float):
          return NotImplemented
       #if not b: return b #don't eliminate!
       rex = _linexp()
       rex.const = me.const*b
       rex.mat = [(i,c*b) for i,c in me.mat]
       return rex

   def __rmul__(me, b):
       if type(b) not in (int, float):
          return NotImplemented
       return me * b

   def __sub__(me, b):
       if me._bad_type(b): return NotImplemented
       return me + b*(-1.0)

   def __rsub__(me, b): # b - me
       if me._bad_type(b): return NotImplemented
       return me*(-1.0) + b

   def __div__(me, b):
       if type(b) not in (int, long, float):
          return NotImplemented
       return me * (1.0/b)

   def __truediv__(me, b):
       if type(b) not in (int, long, float):
          return NotImplemented
       return me * (1.0/b)

   def __pos__(me): 
       return me 

   def __neg__(me):
       return me*(-1.0)

##    def _related(glpk_h):
##        '''This metaclass will add a list of related functions
##from a glpk header file when creating the target class.'''
##        related = []
##        import re #regular expression
##        pat = re.compile(r'(glp_\w+)\s*\(\s*glp_prob\s*\*')
##        with open(glpk_h) as header:
##            for line in header:
##                mat = pat.search(line)
##                if not mat: continue
##                related.append(mat.group(1))
##        return related
##    _related = _related('./glpk.h') #extract from glpk header file v4.60
##    _related.sort()
##    n = len(_related)
##    for i in range(0, n, 3):
##        print(str(_related[i:i+3])[1:-1], ',')
##    print(i, "out of total:", n)
    

class _Extractor(object):
    '''given the glpk.h file and the doc directory 
with the glpk*.tex files, this will find all
funsctions in glpk.h that matches a rex,
and find the corresponding documentation in 
the tex file.'''
    import re, glob
    
    debug = False
    
    def __init__(me, glpk_h, doc_dir):
        me.glpk_h = glpk_h
        me.doc_dir = doc_dir

    def grep_funs(me, rex, i):
        rex = me.re.compile(rex)
        funs = []
        with open(me.glpk_h) as header:
            for line in header:
                if "#ifdef GLP_UNDOC" in line:
                    next(header) #skip next line
                    continue
                mat = rex.search(line)
                if not mat: continue
                funs.append(mat.group(i))
        return funs

    def grep_doc(me, funs=None):
        dod = {}
        #now find the docs
        for name in me.glob.iglob(me.doc_dir+'/glpk*.tex'):
            with open(name) as docf: 
                 print(name)
                 #print(me.rex_com.findall(docf.read()))
                 me.grep_file(docf, dod, funs) 
        return dod

    known_coms = ('\\vspace', '\\hspace', '\\begin', '\\end')
    rex_start = re.compile(
        r'^\\subsection\{(glp(\\_\w+)+)\s*---\s*([^}]+\}?)')
    rex_synop = re.compile(r'\s*(\w+\b\s*)+(\*?)\s*(glp_\w+)\s*\(')
    rex_altsyn= re.compile(
        r'(\s*\{?\s*\\tt)(\s+\w+(\\_\w+)*)+\s*(\*?)\s*(glp(\\_\w+)+)\s*\([^}]+\}?')
    rex_altsyn_end= re.compile(r'[^)]+\)\s*;\s*\}')
    rex_com = re.compile(r'\s*(\\[a-zA-Z]\w*)(\s*\*?\s*\{-?\w+\}|=-?\w+\b)?')

    replaces = ( ('\\ x\\ ', ' x '), 
            ('\\verb|GLP_', '|glpk.GLP_'), ('\\verb|', '|'), 
            ('\\leq','<='), ('\\lt','<'), 
            ('\\geq',">="), ('\\gt','>'), 
            ('\\infty','inf'), ('\\dots','...'))

    def grep_file(me, docf, dod, funs=None):
        '''grep one tex document.''' #TODO: simplify it.
        maxseek, maxlines = 20, 100    
        state, lines, no_return = 0, None, None
        for ln in docf:
            if state and len(lines)>maxlines: 
                print(state, name, ''.join(lines))
                raise Exception(
                    "doc problem: lines exceeding %i."%maxlines)

            if '\\newpage' in ln or ln.lstrip().startswith('%'): 
                continue


            if state: 
                for kk,rr in me.replaces:
                    if kk not in ln: continue
                    ln = ln.replace(kk, rr)

            if state == 0:
                m = me.rex_start.match(ln)
                if not m: continue
                name = ''.join(m.group(1).split('\\'))
                if funs and name not in funs: continue
                shortdesc = m.group(3)
                if shortdesc.endswith('\n'):
                    shortdesc += next(docf)
                if me.debug: print(name, shortdesc)
                if "}" not in shortdesc:
                    print( state, name, shortdesc)
                    print("Badly formatted text.\n"+ln) 
                    state, lines, no_return = 0, None, None
                    continue #abort this attempt
                shortdesc = shortdesc[:shortdesc.rindex("}")]
                lines = [name+" --- " + shortdesc+"\n"]
                state += 1
                
            elif state == 1:
                if ln.startswith('\\synopsis'):
                   lines.append('synopsis:\n')
                elif ln.startswith('\\begin{verbatim}'):
                    state += 2; 
                elif m.group(1) in ln: 
                    m = me.rex_altsyn.match(ln)
                    if not m: 
                        print( state, ''.join(lines))
                        print("Badly formatted text.\n"+ln) 
                        state, lines, no_return = 0, None, None
                        continue #abort this attempt
                    no_return = m.group(2).strip() == 'void'\
                                and not m.group(4)
                    ln  = ln[len(m.group(1)):] #get rid of {\tt
                    #clean up the line
                    ln = '_'.join(ln.split('\\_'))
                    lines.append(me.rex_com.sub('', ln))
                    if  me.rex_altsyn_end.match(ln):
                        state += 3 #jump
                    else: state += 1 
                else: 
                    rm = me.rex_com.match(ln)
                    if rm and rm.group(1) not in me.known_coms:
                        print( state, ''.join(lines))
                        print("unexpected command:\n"+ln)
                        state, lines, no_return = 0, None, None
                        continue #abort this attempt
                    lines.append(me.rex_com.sub('', ln))

            elif state == 2: # alternative synopsis
                #clean up the line
                ln = '_'.join(ln.split('\\_'))
                if not ln.strip(): continue
                lines.append(me.rex_com.sub('', ln))
                if me.rex_altsyn_end.match(ln):
                    state += 2
                
            elif state == 3: #watch out for void return type
                if ln.startswith('\\end{verbatim}'): 
                    if no_return is None:
                        print( state, ''.join(lines))
                        print("no_return is None!\n"+ln)
                        state, lines, no_return = 0, None, None
                        continue #abort this attempt
                    else: state += 1; continue
                if name in ln: 
                    m = me.rex_synop.match(ln)
                    if m: 
                        if m.group(3) != name:
                            print( state, ''.join(lines))
                            print("bad function name:\n"+ln)
                            state, lines, no_return = 0, None, None
                            continue #abort this attempt
                        no_return = m.group(1).strip() == 'void'\
                                and not m.group(2)
                if me.rex_com.match(ln):
                    com = me.rex_com.match(ln).group(1)
                    if com in me.known_coms: continue
                    print( state, ''.join(lines))
                    print("unexpected latex command:\n"+ln)
                    state, lines, no_return = 0, None, None
                    continue #abort this attempt
                lines.append(me.rex_com.sub('',ln))

            elif state == 4: #description or returns
                if ln.startswith('\\returns'):
                    lines.append('returns:\n')
                    state += 2 #jump
                    if no_return: 
                        print( state, ''.join(lines))
                        print("no_return is true, but got returns")
                        state, lines, no_return = 0, None, None
                        continue #abort this attempt
                elif ln.lstrip().startswith('\\description'):
                    lines.append('description:\n')
                    state += 2 if no_return else 1
                elif me.rex_com.match(ln.lstrip()):
                    com = me.rex_com.match(ln.lstrip()).group()
                    if com in me.known_coms: continue
                    print( state, ''.join(lines))
                    print("unexpected latex command:\n"+ln)
                    state, lines, no_return = 0, None, None
                    continue #abort this attempt
                else:
                    lines.append(me.rex_com.sub('', ln))
                    if len(lines) < maxseek: continue
                    
                    print( state, ''.join(lines))
                    print("neither description nor returns?")
                    state, lines, no_return = 0, None, None
                    continue #abort this attempt    
                        
            elif state == 5: #has return
                if ln.startswith('\\returns'):
                    lines.append('returns:\n')
                    state += 1
                else: lines.append(me.rex_com.sub('',ln))

            elif state == 6: #end if new paragraph header
                m = me.rex_com.match(ln)
                if m and m.group(1) not in me.known_coms\
                  and not lines[-1].strip():
                    while not lines[-1].strip(): del lines[-1]
                    dod[name] = ''.join(lines)
                    state, lines, no_return = 0, None, None
                else: lines.append(me.rex_com.sub('',ln))
                
                if state: continue
                # copy & paste from "if state == 0:"
                m = me.rex_start.match(ln)
                if not m: continue
                name = ''.join(m.group(1).split('\\'))
                if funs and name not in funs: continue
                shortdesc = m.group(3)
                if shortdesc.endswith('\n'):
                    shortdesc += next(docf)
                if me.debug: print(name, shortdesc)
                if "}" not in shortdesc:
                    print( state, name, shortdesc)
                    print("Badly formatted text.\n"+ln) 
                    state, lines, no_return = 0, None, None
                    continue #abort this attempt
                shortdesc = shortdesc[:shortdesc.rindex("}")]
                lines = [name+" --- " + shortdesc+"\n"]
                state += 1

            else: raise Exception("Impossible state!")


    def undocumented(me):
        funs = me.grep_funs(
            r'^\s*\w+(\s+\w+)*\s*\**\s*(glp_\w+)\s*\(', 2)
        
        dod = me.grep_doc(funs)

        print('\n\nHere are the undocumented:\n')
        n = 0
        for k in funs:
            if k not in dod:
                n += 1
                print (n, k)
                
    def interactive(dod):        
        badname = "No such function name."    
        while True:
            k = raw_input("Function name: ")
            if not k: break
            d = dod.get(k, badname)
            print(d)

    def lp_related(me, silent=False):
        funs = me.grep_funs(r'(glp_\w+)\s*\(\s*glp_prob\s*\*', 1)
        dod = me.grep_doc(funs)
    
        nodoc = "No original doc found in glpk."
        for k in funs:
            if k not in dod:
                dod[k] = nodoc
                print ('#', k, ':', nodoc)
        if silent: return dod
        
        for k,d in dod.items():
            print(repr(k), ':', sep='')
            print("'''", d, "''',\n", sep='')

class _LinkGLPK(type):
    '''this metaclass will add glpk functions related to a problem instance
to a class that wraps such an instance. the instance will be stored in
the field _glp_.'''

    glpk_h = 'glpk-4.60/src/glpk.h'
    doc_dir = 'glpk-4.60/doc'
    #_related = _Extractor(glpk_h, doc_dir).lp_related()

    _related ={
# glp_get_it_cnt : No original doc found in glpk.
# glp_set_it_cnt : No original doc found in glpk.
# glp_analyze_coef : No original doc found in glpk.
# glp_read_cnfsat : No original doc found in glpk.
# glp_check_cnfsat : No original doc found in glpk.
# glp_write_cnfsat : No original doc found in glpk.
# glp_minisat1 : No original doc found in glpk.
# glp_intfeas1 : No original doc found in glpk.
# glp_mincost_lp : No original doc found in glpk.
# glp_maxflow_lp : No original doc found in glpk.
# glp_asnprob_lp : No original doc found in glpk.
'glp_sort_matrix':
'''glp_sort_matrix --- sort elements of the constraint
matrix

synopsis:

   void glp_sort_matrix(glp_prob *P);

description:

The routine |glp_sort_matrix| sorts elements of the constraint
matrix by rebuilding its row and column linked lists.

On exit from the routine the constraint matrix is not changed, however,
elements in the row linked lists become ordered by ascending column
indices, and the elements in the column linked lists become ordered by
ascending row indices.
''',

'glp_get_row_lb':
'''glp_get_row_lb --- retrieve row lower bound

synopsis:

   double glp_get_row_lb(glp_prob *P, int i);

returns:

The routine |glp_get_row_lb| returns the lower bound of
|i|-th row, i.e. the lower bound of corresponding auxiliary
variable. However, if the row has no lower bound, the routine returns
|-DBL_MAX|.
''',

'glp_transform_col':
'''glp_transform_col --- transform explicitly specified
column

synopsis:

   int glp_transform_col(glp_prob *P, int len, int ind[], double val[]);

description:

The routine |glp_transform_col| performs the same operation as the
routine |glp_eval_tab_col| with exception that the column to be
transformed is specified explicitly as a sparse vector.

The explicitly specified column may be thought as it were added to
the original system of equality constraints:
$$
{l@{\ }c@{\ }r@{\ }c@{\ }r@{\ }c@{\ }r}
x_1&=&a_{11}x_{m+1}&+...+&a_{1n}x_{m+n}&+&a_1x \\
x_2&=&a_{21}x_{m+1}&+...+&a_{2n}x_{m+n}&+&a_2x \\
{c}
{.\ \ .\ \ .\ \ .\ \ .\ \ .\ \ .\ \ .\ \ .\ \ .\ \ .\ \ .\ \ .\ \ .}\\
x_m&=&a_{m1}x_{m+1}&+...+&a_{mn}x_{m+n}&+&a_mx \\

$$
where $x_i$ are auxiliary variables, $x_{m+j}$ are structural variables
(presented in the problem object), $x$ is a structural variable for the
explicitly specified column, $a_i$ are constraint coefficients at $x$.

On entry row indices and numerical values of non-zero coefficients
$a_i$ of the specified column should be placed in locations
|ind[1]|, ..., |ind[len]| and |val[1]|, ...,
|val[len]|, where |len| is number of non-zero coefficients.

This routine uses the system of equality constraints and the current
basis in order to express the current basic variables through the
structural variable $x$ (as if the transformed column were added to the
problem object and the variable $x$ were non-basic):
$$
{l@{\ }c@{\ }r}
(x_B)_1&=...+&x\\
(x_B)_2&=...+&x\\
{c}{.\ \ .\ \ .\ \ .\ \ .\ \ .}\\
(x_B)_m&=...+&x\\

$$
where $$ are influence coefficients, $x_B$ are basic (auxiliary
and structural) variables, $m$ is the number of rows in the problem
object.

On exit the routine stores indices and numerical values of non-zero
coefficients $$ of the resultant column in locations |ind[1]|,
..., |ind[len']| and |val[1]|, ..., |val[len']|,
where $0<={ len'}<= m$ is the number of non-zero coefficients in
the resultant column returned by the routine. Note that indices of basic
variables stored in the array |ind| correspond to original ordinal
numbers of variables, i.e. indices 1 to $m$ mean auxiliary variables,
indices $m+1$ to $m+n$ mean structural ones.

returns:

The routine |glp_transform_col| returns |len'|, the number of
non-zero coefficients in the resultant column stored in the arrays
|ind| and |val|.
''',

'glp_set_prob_name':
'''glp_set_prob_name --- assign (change) problem name

synopsis:

   void glp_set_prob_name(glp_prob *P, const char *name);

description:

The routine |glp_set_prob_name| assigns a given symbolic
|name| (1 up to 255 characters) to the specified problem object.

If the parameter |name| is |NULL| or empty string, the
routine erases an existing symbolic name of the problem object.
''',

'glp_set_obj_coef':
'''glp_set_obj_coef --- set (change) objective coefficient
or constant term

synopsis:

   void glp_set_obj_coef(glp_prob *P, int j, double coef);

description:

The routine |glp_set_obj_coef| sets (changes) the objective
coefficient at |j|-th column (structural variable). A new value of
the objective coefficient is specified by the parameter |coef|.

If the parameter |j| is 0, the routine sets (changes) the constant
term (``shift'') of the objective function.
''',

'glp_set_obj_name':
'''glp_set_obj_name --- assign (change) objective function
name

synopsis:

   void glp_set_obj_name(glp_prob *P, const char *name);

description:

The routine |glp_set_obj_name| assigns a given symbolic
|name| (1 up to 255 characters) to the objective function of the
specified problem object.

If the parameter |name| is |NULL| or empty string, the
routine erases an existing symbolic name of the objective function.
''',

'glp_warm_up':
'''glp_warm_up --- ``warm up'' LP basis

synopsis:

   int glp_warm_up(glp_prob *P);

description:

The routine |glp_warm_up| ``warms up'' the LP basis for the
specified problem object using current statuses assigned to rows and
columns (that is, to auxiliary and structural variables).

This operation includes computing factorization of the basis matrix
(if it does not exist), computing primal and dual components of basic
solution, and determining the solution status.

returns:


0 & The operation has been successfully performed.\\

|glpk.GLP_EBADB| & The basis matrix is invalid, because the number of
basic (auxiliary and structural) variables is not the same as the
number of rows in the problem object.\\

|glpk.GLP_ESING| & The basis matrix is singular within the working
precision.\\

|glpk.GLP_ECOND| & The basis matrix is ill-conditioned, i.e. its
condition number is too large.\\
''',

'glp_adv_basis':
'''glp_adv_basis --- construct advanced initial LP basis

synopsis:

   void glp_adv_basis(glp_prob *P, int flags);

description:

The routine |glp_adv_basis| constructs an advanced initial LP
basis for the specified problem object.

The parameter |flags| is reserved for use in the future and must
be specified as zero.

In order to construct the advanced initial LP basis the routine does
the following:

1) includes in the basis all non-fixed auxiliary variables;

2) includes in the basis as many non-fixed structural variables as
possible keeping the triangular form of the basis matrix;

3) includes in the basis appropriate (fixed) auxiliary variables to
complete the basis.

As a result the initial LP basis has as few fixed variables as possible
and the corresponding basis matrix is triangular.
''',

'glp_ipt_obj_val':
'''glp_ipt_obj_val --- retrieve objective value

synopsis:

   double glp_ipt_obj_val(glp_prob *P);

returns:

The routine |glp_ipt_obj_val| returns value of the objective
function for interior-point solution.
''',

'glp_get_sjj':
'''glp_get_sjj --- retrieve column scale factor



synopsis:

   double glp_get_sjj(glp_prob *P, int j);

returns:

The routine |glp_get_sjj| returns current scale factor $s_{jj}$
for $j$-th column of the specified problem object.
''',

'glp_maxflow_lp':
'''No original doc found in glpk.''',

'glp_get_row_stat':
'''glp_get_row_stat --- retrieve row status

synopsis:

   int glp_get_row_stat(glp_prob *P, int i);

returns:

The routine |glp_get_row_stat| returns current status assigned to
the auxiliary variable associated with |i|-th row as follows:

|glpk.GLP_BS| --- basic variable;

|glpk.GLP_NL| --- non-basic variable on its lower bound;

|glpk.GLP_NU| --- non-basic variable on its upper bound;

|glpk.GLP_NF| --- non-basic free (unbounded) variable;

|glpk.GLP_NS| --- non-basic fixed variable.
''',

'glp_mip_row_val':
'''glp_mip_row_val --- retrieve row value

synopsis:

   double glp_mip_row_val(glp_prob *P, int i);

returns:

The routine |glp_mip_row_val| returns value of the auxiliary
variable associated with |i|-th row for MIP solution.
''',

'glp_del_cols':
'''glp_del_cols --- delete columns from problem object

synopsis:

   void glp_del_cols(glp_prob *P, int ncs, const int num[]);

description:

The routine |glp_del_cols| deletes columns from the specified
problem object. Ordinal numbers of columns to be deleted should be
placed in locations |num[1]|, ..., |num[ncs]|, where
${ ncs}>0$.

Note that deleting columns involves changing ordinal numbers of other
columns remaining in the problem object. New ordinal numbers
of the remaining columns are assigned under the assumption that the
original order of columns is not changed. Let, for example, before
deletion  there be six columns $p$, $q$, $r$, $s$, $t$, $u$ with
ordinal numbers 1, 2, 3, 4, 5, 6, and let columns $p$, $q$, $s$ have
been deleted. Then after deletion the remaining columns $r$, $t$, $u$
are assigned new ordinal numbers 1, 2, 3.

If the basis factorization exists, deleting basic columns invalidates
it.
''',

'glp_get_col_kind':
'''glp_get_col_kind --- retrieve column kind

synopsis:

   int glp_get_col_kind(glp_prob *P, int j);

returns:

The routine |glp_get_col_kind| returns the kind of |j|-th
column (structural variable) as follows:

|glpk.GLP_CV| --- continuous variable;

|glpk.GLP_IV| --- integer variable;

|glpk.GLP_BV| --- binary variable.
''',

'glp_eval_tab_col':
'''glp_eval_tab_col --- compute column of the tableau

synopsis:

   int glp_eval_tab_col(glp_prob *P, int k, int ind[], double val[]);

description:

The routine |glp_eval_tab_col| computes a column of the current
simplex tableau (see Subsection 3.1.1, formula (3.12)), which (column)
corresponds to some non-basic variable specified by the parameter $k$:
if $1<= k<= m$, the non-basic variable is $k$-th auxiliary
variable, and if $m+1<= k<= m+n$, the non-basic variable is
$(k-m)$-th structural variable, where $m$ is the number of rows and $n$
is the number of columns in the specified problem object. The basis
factorization must exist.

The computed column shows how basic variables depends on the specified
non-basic variable $x_k=(x_N)_j$:
$$
{r@{\ }c@{\ }l@{\ }l}
(x_B)_1&=&...+(x_N)_j&+...\\
(x_B)_2&=&...+(x_N)_j&+...\\
.\ \ .&.&.\ \ .\ \ .\ \ .\ \ .\ \ .\ \ .\\
(x_B)_m&=&...+(x_N)_j&+...\\

$$
where $$, $$, ..., $$ are elements of the
simplex table column, $(x_B)_1$, $(x_B)_2$, ..., $(x_B)_m$ are basic
(auxiliary and structural) variables.

The routine stores row indices and corresponding numeric values of
non-zero elements of the computed column in unordered sparse format in
locations |ind[1]|, ..., |ind[len]| and |val[1]|,
..., |val[len]|, respectively, where $0<={ len}<= m$ is
the number of non-zero elements in the column returned on exit.

Element indices stored in the array |ind| have the same sense as
index $k$, i.e. indices 1 to $m$ denote auxiliary variables while
indices $m+1$ to $m+n$ denote structural variables (all these variables
are obviously basic by definition).

returns:

The routine |glp_eval_tab_col| returns |len|, which is the
number of non-zero elements in the simplex table column stored in the
arrays |ind| and |val|.
''',

'glp_print_sol':
'''glp_print_sol --- write basic solution in printable
format

synopsis:

   int glp_print_sol(glp_prob *P, const char *fname);

description:

The routine |glp_print_sol writes| the current basic solution to
an LP problem, which is specified by the pointer |P|, to a text
file, whose name is the character string |fname|, in printable
format.

Information reported by the routine |glp_print_sol| is intended
mainly for visual analysis.

returns:

If no errors occurred, the routine returns zero. Otherwise the routine
prints an error message and returns non-zero.
''',

'glp_check_kkt':
'''glp_check_kkt --- check feasibility/optimality
conditions

synopsis:

{
 void glp_check_kkt(glp_prob *P, int sol, int cond,
double *ae_max, int *ae_ind,
double *re_max, int *re_ind);}

description:

The routine |glp_check_kkt| allows to check
feasibility/optimality conditions for the current solution stored in
the specified problem object. (For basic and interior-point solutions
these conditions are known as { Karush--Kuhn--Tucker optimality
conditions}.)

The parameter |sol| specifies which solution should be checked:

|glpk.GLP_SOL| --- basic solution;

|glpk.GLP_IPT| --- interior-point solution;

|glpk.GLP_MIP| --- mixed integer solution.

The parameter |cond| specifies which condition should be checked:

|glpk.GLP_KKT_PE| --- check primal equality constraints (KKT.PE);

|glpk.GLP_KKT_PB| --- check primal bound constraints (KKT.PB);

|glpk.GLP_KKT_DE| --- check dual equality constraints (KKT.DE). This
conditions can be checked only for basic or interior-point solution;

|glpk.GLP_KKT_DB| --- check dual bound constraints (KKT.DB). This
conditions can be checked only for basic or interior-point solution.

Detailed explanations of these conditions are given below in paragraph
``Background''.

On exit the routine stores the following information to locations
specified by parameters |ae_max|, |ae_ind|, |re_max|,
and |re_ind| (if some parameter is a null pointer, corresponding
information is not stored):

|ae_max| --- largest absolute error;

|ae_ind| --- number of row (KKT.PE), column (KKT.DE), or variable
(KKT.PB, KKT.DB) with the largest absolute error;

|re_max| --- largest relative error;

|re_ind| --- number of row (KKT.PE), column (KKT.DE), or variable
(KKT.PB, KKT.DB) with the largest relative error.

Row (auxiliary variable) numbers are in the range 1 to $m$, where $m$
is the number of rows in the problem object. Column (structural
variable) numbers are in the range 1 to $n$, where $n$ is the number
of columns in the problem object. Variable numbers are in the range
1 to $m+n$, where variables with numbers 1 to $m$ correspond to rows,
and variables with numbers $m+1$ to $m+n$ correspond to columns. If
the error reported is exact zero, corresponding row, column or variable
number is set to zero.
''',

'glp_dual_rtest':
'''glp_dual_rtest --- perform dual ratio test

synopsis:

   int glp_dual_rtest(glp_prob *P, int len, const int ind[], const double val[],
                      int dir, double eps);

description:

The routine |glp_dual_rtest| performs the dual ratio test using
an explicitly specified row of the simplex table.

The current basic solution associated with the LP problem object must
be dual feasible.

The explicitly specified row of the simplex table is a linear form
that shows how some basic variable $x$ (which is not necessarily
presented in the problem object) depends on non-basic variables $x_N$:
$$x=(x_N)_1+(x_N)_2+...+(x_N)_n.$$

The row is specified on entry to the routine in sparse format. Ordinal
numbers of non-basic variables $(x_N)_j$ should be placed in locations
|ind[1]|, ..., |ind[len]|, where ordinal numbers 1 to $m$
denote auxiliary variables, and ordinal numbers $m+1$ to $m+n$ denote
structural variables. The corresponding non-zero coefficients $$
should be placed in locations |val[1]|, ..., |val[len]|.
The arrays |ind| and |val| are not changed by the routine.

The parameter |dir| specifies direction in which the variable $x$
changes on leaving the basis: $+1$ means that $x$ goes on its lower
bound, so its reduced cost (dual variable) is increasing (minimization)
or decreasing (maximization); $-1$ means that $x$ goes on its upper
bound, so its reduced cost is decreasing (minimization) or increasing
(maximization).

The parameter |eps| is an absolute tolerance (small positive
number, say, $10^{-9}$) used by the routine to skip $$'s whose
magnitude is less than |eps|.

The routine determines which non-basic variable (among those specified
in |ind[1]|, ..., |ind[len]|) should enter the
basis in order to keep dual feasibility, because its reduced cost
reaches the (zero) bound first before this occurs for any other
non-basic variables.

returns:

The routine |glp_dual_rtest| returns the index, |piv|, in the
arrays |ind| and |val| corresponding to the pivot element
chosen, $1<=$ |piv| $<=$ |len|. If the adjacent basic
solution is dual unbounded, and therefore the choice cannot be made,
the routine returns zero.
''',

'glp_set_obj_dir':
'''glp_set_obj_dir --- set (change) optimization direction
flag

synopsis:

   void glp_set_obj_dir(glp_prob *P, int dir);

description:

The routine |glp_set_obj_dir| sets (changes) the optimization
direction flag (i.e. ``sense'' of the objective function) as specified
by the parameter |dir|:

|glpk.GLP_MIN| means minimization;

|glpk.GLP_MAX| means maximization.

Note that by default the problem is minimization.
''',

'glp_analyze_coef':
'''No original doc found in glpk.''',

'glp_get_num_cols':
'''glp_get_num_cols --- retrieve number of columns

synopsis:

   int glp_get_num_cols(glp_prob *P);

returns:

The routine |glp_get_num_cols| returns the current number of
columns in the specified problem object.
''',

'glp_set_bfcp':
'''glp_set_bfcp --- change basis factorization control
parameters

synopsis:

   void glp_set_bfcp(glp_prob *P, const glp_bfcp *parm);

description:

The routine |glp_set_bfcp| changes control parameters, which are
used by internal GLPK routines on computing and updating the basis
factorization associated with the specified problem object.

New values of the control parameters should be passed in a structure
|glp_bfcp|, which the parameter |parm| points to. For a
detailed description of the structure |glp_bfcp| see paragraph
``Control parameters'' below.

The parameter |parm| can be specified as |NULL|, in which
case all control parameters are reset to their default values.
''',

'glp_del_rows':
'''glp_del_rows --- delete rows from problem object

synopsis:

   void glp_del_rows(glp_prob *P, int nrs, const int num[]);

description:

The routine |glp_del_rows| deletes rows from the specified problem
object. Ordinal numbers of rows to be deleted should be placed in
locations |num[1]|, ..., |num[nrs]|, where ${ nrs}>0$.

Note that deleting rows involves changing ordinal numbers of other
rows remaining in the problem object. New ordinal numbers of the
remaining rows are assigned under the assumption that the original
order of rows is not changed. Let, for example, before deletion there
be five rows $a$, $b$, $c$, $d$, $e$ with ordinal numbers 1, 2, 3, 4,
5, and let rows $b$ and $d$ have been deleted. Then after deletion the
remaining rows $a$, $c$, $e$ are assigned new oridinal numbers 1, 2, 3.

If the basis factorization exists, deleting active (binding) rows,
i.e. whose auxiliary variables are marked as non-basic, invalidates it.
''',

'glp_write_sol':
'''glp_write_sol --- write basic solution in GLPK format

synopsis:

   int glp_write_sol(glp_prob *P, const char *fname);

description:

The routine |glp_write_sol| writes the current basic solution to
a text file in the GLPK format. (For description of the GLPK basic
solution format see Subsection ``Read basic solution in GLPK format.'')

The character string |fname| specifies the name of the text file
to be written. (If the file name ends with suffix `|.gz|', the
routine |glp_write_sol| compresses it "on the fly".)

returns:

If the operation was successful, the routine |glp_write_sol|
returns zero. Otherwise, it prints an error message and returns
non-zero.
''',

'glp_set_mat_row':
'''glp_set_mat_row --- set (replace) row of the constraint
matrix

synopsis:

   void glp_set_mat_row(glp_prob *P, int i, int len, const int ind[],
                        const double val[]);

description:

The routine |glp_set_mat_row| stores (replaces) the contents of
|i|-th row of the constraint matrix of the specified problem
object.

Column indices and numerical values of new row elements should be
placed in locations |ind[1]|, ..., |ind[len]| and
|val[1]|, ..., |val[len]|, respectively, where
$0 <=$ |len| $<= n$ is the new length of $i$-th row, $n$ is
the current number of columns in the problem object. Elements with
identical column indices are not allowed. Zero elements are allowed,
but they are not stored in the constraint matrix.

If the parameter |len| is 0, the parameters |ind| and/or
|val| can be specified as |NULL|.
''',

'glp_get_status':
'''glp_get_status --- determine generic status of basic
solution

synopsis:

   int glp_get_status(glp_prob *P);

returns:

The routine |glp_get_status| reports the generic status of the
current basic solution for the specified problem object as follows:

|glpk.GLP_OPT   | --- solution is optimal;

|glpk.GLP_FEAS  | --- solution is feasible;

|glpk.GLP_INFEAS| --- solution is infeasible;

|glpk.GLP_NOFEAS| --- problem has no feasible solution;

|glpk.GLP_UNBND | --- problem has unbounded solution;

|glpk.GLP_UNDEF | --- solution is undefined.

More detailed information about the status of basic solution can be
retrieved with the routines |glp_get_prim_stat| and
|glp_get_dual_stat|.
''',

'glp_print_ipt':
'''glp_print_ipt --- write interior-point solution in
printable format

synopsis:

   int glp_print_ipt(glp_prob *P, const char *fname);

description:

The routine |glp_print_ipt| writes the current interior point
solution to an LP problem, which the parameter |P| points to, to
a text file, whose name is the character string |fname|, in
printable format.

Information reported by the routine |glp_print_ipt| is intended
mainly for visual analysis.

returns:

If no errors occurred, the routine returns zero. Otherwise the routine
prints an error message and returns non-zero.
''',

'glp_get_row_prim':
'''glp_get_row_prim --- retrieve row primal value

synopsis:

   double glp_get_row_prim(glp_prob *P, int i);

returns:

The routine |glp_get_row_prim| returns primal value of the
auxiliary variable associated with |i|-th row.
''',

'glp_write_mip':
'''glp_write_mip --- write MIP solution in GLPK format

synopsis:

   int glp_write_mip(glp_prob *P, const char *fname);

description:

The routine |glp_write_mip| writes the current MIP solution to
a text file in the GLPK format. (For description of the GLPK MIP
solution format see Subsection ``Read MIP solution in GLPK format.'')

The character string |fname| specifies the name of the text file
to be written. (If the file name ends with suffix `|.gz|', the
routine |glp_write_mip| compresses it "on the fly".)

returns:

If the operation was successful, the routine |glp_write_mip|
returns zero. Otherwise, it prints an error message and returns
non-zero.
''',

'glp_get_prim_stat':
'''glp_get_prim_stat --- retrieve status of primal basic
solution

synopsis:

   int glp_get_prim_stat(glp_prob *P);

returns:

The routine |glp_get_prim_stat| reports the status of the primal
basic solution for the specified problem object as follows:

|glpk.GLP_UNDEF | --- primal solution is undefined;

|glpk.GLP_FEAS  | --- primal solution is feasible;

|glpk.GLP_INFEAS| --- primal solution is infeasible;

|glpk.GLP_NOFEAS| --- no primal feasible solution exists.
''',

'glp_read_prob':
'''glp_read_prob --- read problem data in GLPK format

synopsis:

   int glp_read_prob(glp_prob *P, int flags, const char *fname);

description:

The routine |glp_read_prob| reads problem data in the GLPK LP/MIP
format from a text file. (For description of the GLPK LP/MIP format see
below.)

The parameter |flags| is reserved for use in the future and should
be specified as zero.

The character string |fname| specifies a name of the text file to
be read in. (If the file name ends with suffix `|.gz|', the file
is assumed to be compressed, in which case the routine
|glp_read_prob| decompresses it ``on the fly''.)

Note that before reading data the current content of the problem object
is completely erased with the routine |glp_erase_prob|.

returns:

If the operation was successful, the routine |glp_read_prob|
returns zero. Otherwise, it prints an error message and returns
non-zero.
''',

'glp_prim_rtest':
'''glp_prim_rtest --- perform primal ratio test

synopsis:

   int glp_prim_rtest(glp_prob *P, int len, const int ind[], const double val[],
                      int dir, double eps);

description:

The routine |glp_prim_rtest| performs the primal ratio test using
an explicitly specified column of the simplex table.

The current basic solution associated with the LP problem object must
be primal feasible.

The explicitly specified column of the simplex table shows how the
basic variables $x_B$ depend on some non-basic variable $x$ (which is
not necessarily presented in the problem object):
$$
{l@{\ }c@{\ }r}
(x_B)_1&=...+&x\\
(x_B)_2&=...+&x\\
{c}{.\ \ .\ \ .\ \ .\ \ .\ \ .}\\
(x_B)_m&=...+&x\\

$$

The column is specifed on entry to the routine in sparse format.
Ordinal numbers of basic variables $(x_B)_i$ should be placed in
locations |ind[1]|, ..., |ind[len]|, where ordinal number
1 to $m$ denote auxiliary variables, and ordinal numbers $m+1$ to $m+n$
denote structural variables. The corresponding non-zero coefficients
$$ should be placed in locations
|val[1]|, ..., |val[len]|. The arrays |ind| and
|val| are not changed by the routine.

The parameter |dir| specifies direction in which the variable $x$
changes on entering the basis: $+1$ means increasing, $-1$ means
decreasing.

The parameter |eps| is an absolute tolerance (small positive
number, say, $10^{-9}$) used by the routine to skip $$'s whose
magnitude is less than |eps|.

The routine determines which basic variable (among those specified in
|ind[1]|, ..., |ind[len]|) reaches its (lower or upper)
bound first before any other basic variables do, and which, therefore,
should leave the basis in order to keep primal feasibility.

returns:

The routine |glp_prim_rtest| returns the index, |piv|, in the
arrays |ind| and |val| corresponding to the pivot element
chosen, $1<=$ |piv| $<=$ |len|. If the adjacent basic
solution is primal unbounded, and therefore the choice cannot be made,
the routine returns zero.
''',

'glp_set_row_stat':
'''glp_set_row_stat --- set (change) row status

synopsis:

   void glp_set_row_stat(glp_prob *P, int i, int stat);

description:

The routine |glp_set_row_stat| sets (changes) the current status
of |i|-th row (auxiliary variable) as specified by the parameter
|stat|:

|glpk.GLP_BS| --- make the row basic (make the constraint inactive);

|glpk.GLP_NL| --- make the row non-basic (make the constraint active);

|glpk.GLP_NU| --- make the row non-basic and set it to the upper bound;
if the row is not double-bounded, this status is equivalent to
|glpk.GLP_NL| (only in case of this routine);

|glpk.GLP_NF| --- the same as |glpk.GLP_NL| (only in case of this
routine);

|glpk.GLP_NS| --- the same as |glpk.GLP_NL| (only in case of this
routine).
''',

'glp_mip_col_val':
'''glp_mip_col_val --- retrieve column value

synopsis:

   double glp_mip_col_val(glp_prob *P, int j);

returns:

The routine |glp_mip_col_val| returns value of the structural
variable associated with |j|-th column for MIP solution.
''',

'glp_get_col_lb':
'''glp_get_col_lb --- retrieve column lower bound

synopsis:

   double glp_get_col_lb(glp_prob *P, int j);

returns:

The routine |glp_get_col_lb| returns the lower bound of
|j|-th column, i.e. the lower bound of corresponding structural
variable. However, if the column has no lower bound, the routine
returns |-DBL_MAX|.
''',

'glp_cpx_basis':
'''glp_cpx_basis --- construct Bixby's initial LP basis

synopsis:

   void glp_cpx_basis(glp_prob *P);

description:

The routine |glp_cpx_basis| constructs an initial basis for the
specified problem object with the algorithm proposed by
R.~Bixby.{Robert E. Bixby, ``Implementing the Simplex Method:
The Initial Basis.'' ORSA Journal on Computing, Vol. 4, No. 3, 1992,
pp. 267-84.}
''',

'glp_mip_obj_val':
'''glp_mip_obj_val --- retrieve objective value

synopsis:

   double glp_mip_obj_val(glp_prob *P);

returns:

The routine |glp_mip_obj_val| returns value of the objective
function for MIP solution.
''',

'glp_get_row_name':
'''glp_get_row_name --- retrieve row name

synopsis:

   const char *glp_get_row_name(glp_prob *P, int i);

returns:

The routine |glp_get_row_name| returns a pointer to an internal
buffer, which contains a symbolic name assigned to |i|-th row.
However, if the row has no assigned name, the routine returns
|NULL|.
''',

'glp_get_col_prim':
'''glp_get_col_prim --- retrieve column primal value

synopsis:

   double glp_get_col_prim(glp_prob *P, int j);

returns:

The routine |glp_get_col_prim| returns primal value of the
structural variable associated with |j|-th column.
''',

'glp_add_cols':
'''glp_add_cols --- add new columns to problem object

synopsis:

   int glp_add_cols(glp_prob *P, int ncs);

description:

The routine |glp_add_cols| adds |ncs| columns (structural
variables) to the specified problem object. New columns are always
added to the end of the column list, so the ordinal numbers of existing
columns are not changed.

Being added each new column is initially fixed at zero and has empty
list of the constraint coefficients.

Each new column is marked as non-basic, i.e. zero value of the
corresponding structural variable becomes an active (binding) bound.

If the basis factorization exists, it remains valid.

returns:

The routine |glp_add_cols| returns the ordinal number of the first
new column added to the problem object.
''',

'glp_get_obj_coef':
'''glp_get_obj_coef --- retrieve objective coefficient or
constant term

synopsis:

   double glp_get_obj_coef(glp_prob *P, int j);

returns:

The routine |glp_get_obj_coef| returns the objective coefficient
at |j|-th structural variable (column).

If the parameter |j| is 0, the routine returns the constant term
(``shift'') of the objective function.
''',

'glp_get_obj_val':
'''glp_get_obj_val --- retrieve objective value

synopsis:

   double glp_get_obj_val(glp_prob *P);

returns:

The routine |glp_get_obj_val| returns current value of the
objective function.
''',

'glp_transform_row':
'''glp_transform_row --- transform explicitly specified row

synopsis:

   int glp_transform_row(glp_prob *P, int len, int ind[], double val[]);

description:

The routine |glp_transform_row| performs the same operation as the
routine |glp_eval_tab_row| with exception that the row to be
transformed is specified explicitly as a sparse vector.

The explicitly specified row may be thought as a linear form:
$$x=a_1x_{m+1}+a_2x_{m+2}+...+a_nx_{m+n},$$
where $x$ is an auxiliary variable for this row, $a_j$ are coefficients
of the linear form, $x_{m+j}$ are structural variables.

On entry column indices and numerical values of non-zero coefficients
$a_j$ of the specified row should be placed in locations |ind[1]|,
..., |ind[len]| and |val[1]|, ..., |val[len]|, where
|len| is number of non-zero coefficients.

This routine uses the system of equality constraints and the current
basis in order to express the auxiliary variable $x$ through the current
non-basic variables (as if the transformed row were added to the problem
object and the auxiliary variable $x$ were basic), i.e. the resultant
row has the form:
$$x=(x_N)_1+(x_N)_2+...+(x_N)_n,$$
where $$ are influence coefficients, $(x_N)_j$ are non-basic
(auxiliary and structural) variables, $n$ is the number of columns in
the problem object.

On exit the routine stores indices and numerical values of non-zero
coefficients $$ of the resultant row in locations |ind[1]|,
..., |ind[len']| and |val[1]|, ..., |val[len']|,
where $0<={ len'}<= n$ is the number of non-zero coefficients in
the resultant row returned by the routine. Note that indices of
non-basic variables stored in the array |ind| correspond to
original ordinal numbers of variables: indices 1 to $m$ mean auxiliary
variables and indices $m+1$ to $m+n$ mean structural ones.

returns:

The routine |glp_transform_row| returns |len'|, the number of
non-zero coefficients in the resultant row stored in the arrays
|ind| and |val|.
''',

'glp_eval_tab_row':
'''glp_eval_tab_row --- compute row of the tableau

synopsis:

   int glp_eval_tab_row(glp_prob *P, int k, int ind[], double val[]);

description:

The routine |glp_eval_tab_row| computes a row of the current
simplex tableau (see Subsection 3.1.1, formula (3.12)), which (row)
corresponds to some basic variable specified by the parameter $k$ as
follows: if $1<= k<= m$, the basic variable is $k$-th auxiliary
variable, and if $m+1<= k<= m+n$, the basic variable is $(k-m)$-th
structural variable, where $m$ is the number of rows and $n$ is the
number of columns in the specified problem object. The basis
factorization must exist.

The computed row shows how the specified basic variable depends on
non-basic variables:
$$x_k=(x_B)_i=(x_N)_1+(x_N)_2+...+(x_N)_n,$$
where $$, $$, ..., $$ are elements of the
simplex table row, $(x_N)_1$, $(x_N)_2$, ..., $(x_N)_n$ are non-basic
(auxiliary and structural) variables.

The routine stores column indices and corresponding numeric values of
non-zero elements of the computed row in unordered sparse format in
locations |ind[1]|, ..., |ind[len]| and |val[1]|,
..., |val[len]|, respectively, where $0<={ len}<= n$ is
the number of non-zero elements in the row returned on exit.

Element indices stored in the array |ind| have the same sense as
index $k$, i.e. indices 1 to $m$ denote auxiliary variables while
indices $m+1$ to $m+n$ denote structural variables (all these variables
are obviously non-basic by definition).

returns:

The routine |glp_eval_tab_row| returns |len|, which is the
number of non-zero elements in the simplex table row stored in the
arrays |ind| and |val|.
''',

'glp_set_it_cnt':
'''No original doc found in glpk.''',

'glp_print_ranges':
'''glp_print_ranges --- print sensitivity analysis report

synopsis:

 int glp_print_ranges(glp_prob *P, int len, const int list[],
int flags,\\
const char *fname);}

description:

The routine |glp_print_ranges| performs sensitivity analysis of
current optimal basic solution and writes the analysis report in
human-readable format to a text file, whose name is the character
string { fname}. (Detailed description of the report structure is
given below.)

The parameter { len} specifies the length of the row/column list.

The array { list} specifies ordinal number of rows and columns to be
analyzed. The ordinal numbers should be passed in locations
{ list}[1], { list}[2], ..., { list}[{ len}]. Ordinal
numbers from 1 to $m$ refer to rows, and ordinal numbers from $m+1$ to
$m+n$ refer to columns, where $m$ and $n$ are, resp., the total number
of rows and columns in the problem object. Rows and columns appear in
the analysis report in the same order as they follow in the array list.

It is allowed to specify $len=0$, in which case the array { list} is
not used (so it can be specified as |NULL|), and the routine
performs analysis for all rows and columns of the problem object.

The parameter { flags} is reserved for use in the future and must be
specified as zero.

On entry to the routine |glp_print_ranges| the current basic
solution must be optimal and the basis factorization must exist.
The application program can check that with the routine
|glp_bf_exists|, and if the factorization does
not exist, compute it with the routine |glp_factorize|. Note that
if the LP preprocessor is not used, on normal exit from the simplex
solver routine |glp_simplex| the basis factorization always exists.

returns:

If the operation was successful, the routine |glp_print_ranges|
returns zero. Otherwise, it prints an error message and returns
non-zero.
''',

'glp_get_row_ub':
'''glp_get_row_ub --- retrieve row upper bound

synopsis:

   double glp_get_row_ub(glp_prob *P, int i);

returns:

The routine |glp_get_row_ub| returns the upper bound of
|i|-th row, i.e. the upper bound of corresponding auxiliary
variable. However, if the row has no upper bound, the routine returns
|+DBL_MAX|.
''',

'glp_find_row':
'''glp_find_row --- find row by its name

synopsis:

   int glp_find_row(glp_prob *P, const char *name);

returns:

The routine |glp_find_row| returns the ordinal number of a row,
which is assigned the specified symbolic |name|. If no such row
exists, the routine returns 0.
''',

'glp_print_mip':
'''glp_print_mip --- write MIP solution in printable format

synopsis:

   int glp_print_mip(glp_prob *P, const char *fname);

description:

The routine |glp_print_mip| writes the current solution to a MIP
problem, which is specified by the pointer |P|, to a text file,
whose name is the character string |fname|, in printable format.

Information reported by the routine |glp_print_mip| is intended
mainly for visual analysis.

returns:

If no errors occurred, the routine returns zero. Otherwise the routine
prints an error message and returns non-zero.
''',

'glp_get_bhead':
'''glp_get_bhead --- retrieve the basis header information

synopsis:

   int glp_get_bhead(glp_prob *P, int k);

description:

The routine |glp_get_bhead| returns the basis header information
for the current basis associated with the specified problem object.

returns:

If basic variable $(x_B)_k$, $1<= k<= m$, is $i$-th auxiliary
variable ($1<= i<= m$), the routine returns $i$. Otherwise, if
$(x_B)_k$ is $j$-th structural variable ($1<= j<= n$), the routine
returns $m+j$. Here $m$ is the number of rows and $n$ is the number of
columns in the problem object.
''',

'glp_bf_exists':
'''glp_bf_exists --- check if the basis factorization
exists

synopsis:

   int glp_bf_exists(glp_prob *P);

returns:

If the basis factorization for the current basis associated with the
specified problem object exists and therefore is available for
computations, the routine |glp_bf_exists| returns non-zero.
Otherwise the routine returns zero.
''',

'glp_write_prob':
'''glp_write_prob --- write problem data in GLPK format

synopsis:

int glp_write_prob(glp_prob *P, int flags, const char *fname);

description:

The routine |glp_write_prob| writes problem data in the GLPK
LP/MIP format to a text file. (For description of the GLPK LP/MIP
format see Subsection ``Read problem data in GLPK format''.)

The parameter |flags| is reserved for use in the future and should
be specified as zero.

The character string |fname| specifies a name of the text file to
be written out. (If the file name ends with suffix `|.gz|', the
file is assumed to be compressed, in which case the routine
|glp_write_prob| performs automatic compression on writing it.)

returns:

If the operation was successful, the routine |glp_read_prob|
returns zero. Otherwise, it prints an error message and returns
non-zero.
''',

'glp_factorize':
'''glp_factorize --- compute the basis factorization

synopsis:

   int glp_factorize(glp_prob *P);

description:

The routine |glp_factorize| computes the basis factorization for
the current basis associated with the specified problem
object.{The current basis is defined by the current statuses
of rows (auxiliary variables) and columns (structural variables).}

The basis factorization is computed from ``scratch'' even if it exists,
so the application program may use the routine |glp_bf_exists|,
and, if the basis factorization already exists, not to call the routine
|glp_factorize| to prevent an extra work.

The routine |glp_factorize| { does not} compute components of
the basic solution (i.e. primal and dual values).

returns:


0 & The basis factorization has been successfully computed.\\
|glpk.GLP_EBADB| & The basis matrix is invalid, because the number of
basic (auxiliary and structural) variables is not the same as the number
of rows in the problem object.\\

|glpk.GLP_ESING| & The basis matrix is singular within the working
precision.\\

|glpk.GLP_ECOND| & The basis matrix is ill-conditioned, i.e. its
condition number is too large.\\
''',

'glp_get_dual_stat':
'''glp_get_dual_stat --- retrieve status of dual basic
solution

synopsis:

   int glp_get_dual_stat(glp_prob *P);

returns:

The routine |glp_get_dual_stat| reports the status of the dual
basic solution for the specified problem object as follows:

|glpk.GLP_UNDEF | --- dual solution is undefined;

|glpk.GLP_FEAS  | --- dual solution is feasible;

|glpk.GLP_INFEAS| --- dual solution is infeasible;

|glpk.GLP_NOFEAS| --- no dual feasible solution exists.
''',

'glp_asnprob_lp':
'''No original doc found in glpk.''',

'glp_get_col_ub':
'''glp_get_col_ub --- retrieve column upper bound

synopsis:

   double glp_get_col_ub(glp_prob *P, int j);

returns:

The routine |glp_get_col_ub| returns the upper bound of
|j|-th column, i.e. the upper bound of corresponding structural
variable. However, if the column has no upper bound, the routine
returns |+DBL_MAX|.
''',

'glp_get_mat_col':
'''glp_get_mat_col --- retrieve column of the constraint
matrix

synopsis:

   int glp_get_mat_col(glp_prob *P, int j, int ind[], double val[]);

description:

The routine |glp_get_mat_col| scans (non-zero) elements of
|j|-th column of the constraint matrix of the specified problem
object and stores their row indices and numeric values to locations
 |ind[1]|, ..., |ind[len]| and |val[1]|,
..., |val[len]|, respectively, where $0<={ len}<= m$ is
the number of elements in $j$-th column, $m$ is the number of rows.

The parameter |ind| and/or |val| can be specified as
|NULL|, in which case corresponding information is not stored.

returns:

The routine |glp_get_mat_col| returns the length |len|, i.e.
the number of (non-zero) elements in |j|-th column.
''',

'glp_simplex':
'''glp_simplex --- solve LP problem with the primal or dual
simplex method

synopsis:

   int glp_simplex(glp_prob *P, const glp_smcp *parm);

description:

The routine |glp_simplex| is a driver to the LP solver based on
the simplex method. This routine retrieves problem data from the
specified problem object, calls the solver to solve the problem
instance, and stores results of computations back into the problem
object.

The simplex solver has a set of control parameters. Values of the
control parameters can be passed in the structure |glp_smcp|,
which the parameter |parm| points to. For detailed description of
this structure see paragraph ``Control parameters'' below.
Before specifying some control parameters the application program
should initialize the structure |glp_smcp| by default values of
all control parameters using the routine |glp_init_smcp| (see the
next subsection). This is needed for backward compatibility, because in
the future there may appear new members in the structure
|glp_smcp|.

The parameter |parm| can be specified as |NULL|, in which
case the solver uses default settings.

returns:


0 & The LP problem instance has been successfully solved. (This code
does { not} necessarily mean that the solver has found optimal
solution. It only means that the solution process was successful.) \\

|glpk.GLP_EBADB| & Unable to start the search, because the initial
basis specified in the problem object is invalid---the number of basic
(auxiliary and structural) variables is not the same as the number of
rows in the problem object.\\

|glpk.GLP_ESING| & Unable to start the search, because the basis matrix
corresponding to the initial basis is singular within the working
precision.\\

|glpk.GLP_ECOND| & Unable to start the search, because the basis matrix
corresponding to the initial basis is ill-conditioned, i.e. its
condition number is too large.\\

|glpk.GLP_EBOUND| & Unable to start the search, because some
double-bounded (auxiliary or structural) variables have incorrect
bounds.\\

|glpk.GLP_EFAIL| & The search was prematurely terminated due to the
solver failure.\\

|glpk.GLP_EOBJLL| & The search was prematurely terminated, because the
objective function being maximized has reached its lower limit and
continues decreasing (the dual simplex only).\\

|glpk.GLP_EOBJUL| & The search was prematurely terminated, because the
objective function being minimized has reached its upper limit and
continues increasing (the dual simplex only).\\

|glpk.GLP_EITLIM| & The search was prematurely terminated, because the
simplex iteration limit has been exceeded.\\

|glpk.GLP_ETMLIM| & The search was prematurely terminated, because the
time limit has been exceeded.\\



|glpk.GLP_ENOPFS| & The LP problem instance has no primal feasible
solution (only if the LP presolver is used).\\

|glpk.GLP_ENODFS| & The LP problem instance has no dual feasible
solution (only if the LP presolver is used).\\
''',

'glp_get_col_dual':
'''glp_get_col_dual --- retrieve column dual value

synopsis:

   double glp_get_col_dual(glp_prob *P, int j);

returns:

The routine |glp_get_col_dual| returns dual value (i.e. reduced
cost) of the structural variable associated with |j|-th column.
''',

'glp_intopt':
'''glp_intopt --- solve MIP problem with the branch-and-cut
method

synopsis:

   int glp_intopt(glp_prob *P, const glp_iocp *parm);

description:

The routine |glp_intopt| is a driver to the MIP solver based on
the branch-and-cut method, which is a hybrid of branch-and-bound and
cutting plane methods.

If the presolver is disabled (see paragraph ``Control parameters''
below), on entry to the routine |glp_intopt| the problem object,
which the parameter |mip| points to, should contain optimal
solution to LP relaxation (it can be obtained, for example, with the
routine |glp_simplex|). Otherwise, if the presolver is enabled, it
is not necessary.

The MIP solver has a set of control parameters. Values of the control
parameters can be passed in the structure |glp_iocp|, which the
parameter |parm| points to. For detailed description of this
structure see paragraph ``Control parameters'' below. Before specifying
some control parameters the application program should initialize the
structure |glp_iocp| by default values of all control parameters
using the routine |glp_init_iocp| (see the next subsection). This
is needed for backward compatibility, because in the future there may
appear new members in the structure |glp_iocp|.

The parameter |parm| can be specified as |NULL|, in which case
the solver uses default settings.

Note that the GLPK branch-and-cut solver is not perfect, so it is
unable to solve hard or very large scale MIP instances for a reasonable
time.

returns:


0 & The MIP problem instance has been successfully solved. (This code
does { not} necessarily mean that the solver has found optimal
solution. It only means that the solution process was successful.) \\

|glpk.GLP_EBOUND| & Unable to start the search, because some
double-bounded variables have incorrect bounds or some integer
variables have non-integer (fractional) bounds.\\

|glpk.GLP_EROOT| & Unable to start the search, because optimal basis
for initial LP relaxation is not provided. (This code may appear only
if the presolver is disabled.)\\

|glpk.GLP_ENOPFS| & Unable to start the search, because LP relaxation
of the MIP problem instance has no primal feasible solution. (This code
may appear only if the presolver is enabled.)\\




|glpk.GLP_ENODFS| & Unable to start the search, because LP relaxation
of the MIP problem instance has no dual feasible solution. In other
word, this code means that if the LP relaxation has at least one primal
feasible solution, its optimal solution is unbounded, so if the MIP
problem has at least one integer feasible solution, its (integer)
optimal solution is also unbounded. (This code may appear only if the
presolver is enabled.)\\

|glpk.GLP_EFAIL| & The search was prematurely terminated due to the
solver failure.\\

|glpk.GLP_EMIPGAP| & The search was prematurely terminated, because the
relative mip gap tolerance has been reached.\\

|glpk.GLP_ETMLIM| & The search was prematurely terminated, because the
time limit has been exceeded.\\

|glpk.GLP_ESTOP| & The search was prematurely terminated by application.
(This code may appear only if the advanced solver interface is used.)\\
''',

'glp_read_cnfsat':
'''No original doc found in glpk.''',

'glp_read_mps':
'''glp_read_mps --- read problem data in MPS format

synopsis:

   int glp_read_mps(glp_prob *P, int fmt, const glp_mpscp *parm,
                    const char *fname);

description:

The routine |glp_read_mps| reads problem data in MPS format from a
text file. (The MPS format is described in Appendix, page
.)

The parameter |fmt| specifies the MPS format version as follows:

|glpk.GLP_MPS_DECK| --- fixed (ancient) MPS format;

|glpk.GLP_MPS_FILE| --- free (modern) MPS format.

The parameter |parm| is reserved for use in the future and should
be specified as |NULL|.

The character string |fname| specifies a name of the text file to
be read in. (If the file name ends with suffix `|.gz|', the file
is assumed to be compressed, in which case the routine
|glp_read_mps| decompresses it ``on the fly''.)

Note that before reading data the current content of the problem object
is completely erased with the routine |glp_erase_prob|.

returns:

If the operation was successful, the routine |glp_read_mps|
returns zero. Otherwise, it prints an error message and returns
non-zero.
''',

'glp_ipt_col_dual':
'''glp_ipt_col_dual --- retrieve column dual value

synopsis:

   double glp_ipt_col_dual(glp_prob *P, int j);

returns:

The routine |glp_ipt_col_dual| returns dual value (i.e. reduced
cost) of the structural variable associated with |j|-th column.
''',

'glp_read_mip':
'''glp_read_mip --- read MIP solution in GLPK format

synopsis:

   int glp_read_mip(glp_prob *P, const char *fname);

description:

The routine |glp_read_mip| reads MIP solution from a text file in
the GLPK format. (For description of the format see below.)

The character string |fname| specifies the name of the text file
to be read in. (If the file name ends with suffix `|.gz|', the
file is assumed to be compressed, in which case the routine
|glp_read_mip| decompresses it "on the fly".)

returns:

If the operation was successful, the routine |glp_read_mip|
returns zero. Otherwise, it prints an error message and returns
non-zero.
''',

'glp_get_obj_name':
'''glp_get_obj_name --- retrieve objective function name

synopsis:

   const char *glp_get_obj_name(glp_prob *P);

returns:

The routine |glp_get_obj_name| returns a pointer to an internal
buffer, which contains symbolic name assigned to the objective
function. However, if the objective function has no assigned name, the
routine returns |NULL|.
''',

'glp_erase_prob':
'''glp_erase_prob --- erase problem object content

synopsis:

   void glp_erase_prob(glp_prob *P);

description:

The routine |glp_erase_prob| erases the content of the specified
problem object. The effect of this operation is the same as if the
problem object would be deleted with the routine |glp_delete_prob|
and then created anew with the routine |glp_create_prob|, with the
only exception that the pointer to the problem object remains valid.
''',

'glp_btran':
'''glp_btran --- perform backward transformation

synopsis:

   void glp_btran(glp_prob *P, double x[]);

description:

The routine |glp_btran| performs backward transformation (BTRAN),
i.e. it solves the system $B^Tx=b$, where $B^T$ is a matrix transposed
to the basis matrix $B$ associated with the specified problem object,
$x$ is the vector of unknowns to be computed, $b$ is the vector of
right-hand sides.

On entry to the routine elements of the vector $b$ should be stored in
locations |x[1]|, ..., |x[m]|, where $m$ is the number of
rows. On exit the routine stores elements of the vector $x$ in the same
locations.
''',

'glp_get_unbnd_ray':
'''glp_get_unbnd_ray --- determine variable causing
unboundedness

synopsis:

   int glp_get_unbnd_ray(glp_prob *P);

returns:

The routine |glp_get_unbnd_ray| returns the number $k$ of
a variable, which causes primal or dual unboundedness.
If $1<= k<= m$, it is $k$-th auxiliary variable, and if
$m+1<= k<= m+n$, it is $(k-m)$-th structural variable, where $m$ is
the number of rows, $n$ is the number of columns in the problem object.
If such variable is not defined, the routine returns 0.
''',

'glp_write_mps':
'''glp_write_mps --- write problem data in MPS format

synopsis:

   int glp_write_mps(glp_prob *P, int fmt, const glp_mpscp *parm,
                     const char *fname);

description:

The routine |glp_write_mps| writes problem data in MPS format to
a text file. (The MPS format is described in Appendix,
page.)

The parameter |fmt| specifies the MPS format version as follows:

|glpk.GLP_MPS_DECK| --- fixed (ancient) MPS format;

|glpk.GLP_MPS_FILE| --- free (modern) MPS format.

The parameter |parm| is reserved for use in the future and should
be specified as |NULL|.

The character string |fname| specifies a name of the text file to
be written out. (If the file name ends with suffix `|.gz|', the
file is assumed to be compressed, in which case the routine
|glp_write_mps| performs automatic compression on writing it.)

returns:

If the operation was successful, the routine |glp_write_mps|
returns zero. Otherwise, it prints an error message and returns
non-zero.
''',

'glp_set_mat_col':
'''glp_set_mat_col --- set (replace) column of the
constr\-aint matrix

synopsis:

   void glp_set_mat_col(glp_prob *P, int j, int len, const int ind[],
                        const double val[]);

description:

The routine |glp_set_mat_col| stores (replaces) the contents of
|j|-th column of the constraint matrix of the specified problem
object.

Row indices and numerical values of new column elements should be
placed in locations |ind[1]|, ..., |ind[len]| and
|val[1]|, ..., |val[len]|, respectively, where
$0 <=$ |len| $<= m$ is the new length of $j$-th column, $m$ is
the current number of rows in the problem object. Elements with
identical row indices are not allowed. Zero elements are allowed, but
they are not stored in the constraint matrix.

If the parameter |len| is 0, the parameters |ind| and/or
|val| can be specified as |NULL|.
''',

'glp_set_col_bnds':
'''glp_set_col_bnds --- set (change) column bounds

synopsis:

 void glp_set_col_bnds(glp_prob *P, int j, int type,
double lb, double ub);}

description:

The routine |glp_set_col_bnds| sets (changes) the type and bounds
of |j|-th column (structural variable) of the specified problem
object.

The parameters |type|, |lb|, and |ub| specify the type,
lower bound, and upper bound, respectively, as follows:


{cr@{}c@{}ll}
Type &{c}{Bounds} & Comment \\

|glpk.GLP_FR| & $-inf <$ &$ x $& $< +inf$
   & Free (unbounded) variable \\
|glpk.GLP_LO| & $lb <=$ &$ x $& $< +inf$
   & Variable with lower bound \\
|glpk.GLP_UP| & $-inf <$ &$ x $& $<= ub$
   & Variable with upper bound \\
|glpk.GLP_DB| & $lb <=$ &$ x $& $<= ub$
   & Double-bounded variable \\
|glpk.GLP_FX| & $lb =$ &$ x $& $= ub$
   & Fixed variable \\
''',

'glp_find_col':
'''glp_find_col --- find column by its name

synopsis:

   int glp_find_col(glp_prob *P, const char *name);

returns:

The routine |glp_find_col| returns the ordinal number of a column,
which is assigned the specified symbolic |name|. If no such column
exists, the routine returns 0.
''',

'glp_interior':
'''glp_interior --- solve LP problem with the interior-point
method

synopsis:

   int glp_interior(glp_prob *P, const glp_iptcp *parm);

description:

The routine |glp_interior| is a driver to the LP solver based on
the primal-dual interior-point method. This routine retrieves problem
data from the specified problem object, calls the solver to solve the
problem instance, and stores results of computations back into the
problem object.

The interior-point solver has a set of control parameters. Values of
the control parameters can be passed in the structure |glp_iptcp|,
which the parameter |parm| points to. For detailed description of
this structure see paragraph ``Control parameters'' below. Before
specifying some control parameters the application program should
initialize the structure |glp_iptcp| by default values of all
control parameters using the routine |glp_init_iptcp| (see the
next subsection). This is needed for backward compatibility, because in
the future there may appear new members in the structure
|glp_iptcp|.

The parameter |parm| can be specified as |NULL|, in which
case the solver uses default settings.

returns:


0 & The LP problem instance has been successfully solved. (This code
does { not} necessarily mean that the solver has found optimal
solution. It only means that the solution process was successful.) \\

|glpk.GLP_EFAIL| & The problem has no rows/columns.\\

|glpk.GLP_ENOCVG| & Very slow convergence or divergence.\\

|glpk.GLP_EITLIM| & Iteration limit exceeded.\\

|glpk.GLP_EINSTAB| & Numerical instability on solving Newtonian
system.\\
''',

'glp_get_num_rows':
'''glp_get_num_rows --- retrieve number of rows

synopsis:

   int glp_get_num_rows(glp_prob *P);

returns:

The routine |glp_get_num_rows| returns the current number of rows
in the specified problem object.
''',

'glp_get_row_bind':
'''glp_get_row_bind --- retrieve row index in the basis
header

synopsis:

   int glp_get_row_bind(glp_prob *P, int i);

returns:

The routine |glp_get_row_bind| returns the index $k$ of basic
variable $(x_B)_k$, $1<= k<= m$, which is $i$-th auxiliary variable
(that is, the auxiliary variable corresponding to $i$-th row),
$1<= i<= m$, in the current basis associated with the specified
problem object, where $m$ is the number of rows. However, if $i$-th
auxiliary variable is non-basic, the routine returns zero.
''',

'glp_set_sjj':
'''glp_set_sjj --- set (change) column scale factor

synopsis:

   void glp_set_sjj(glp_prob *P, int j, double sjj);

description:

The routine |glp_set_sjj| sets (changes) the scale factor $s_{jj}$
for $j$-th column of the specified problem object.
''',

'glp_delete_index':
'''glp_delete_index --- delete the name index

synopsis:

   void glp_delete_index(glp_prob *P);

description:

The routine |glp_delete_index| deletes the name index previously
created by the routine |glp_create_index| and frees the
memory allocated to this auxiliary data structure.

This routine can be called at any time. If the name index does not
exist, the routine does nothing.
''',

'glp_set_col_name':
'''glp_set_col_name --- assign (change) column name

synopsis:

   void glp_set_col_name(glp_prob *P, int j, const char *name);

description:

The routine |glp_set_col_name| assigns a given symbolic
|name| (1 up to 255 characters) to |j|-th column (structural
variable) of the specified problem object.

If the parameter |name| is |NULL| or empty string, the
routine erases an existing name of $j$-th column.
''',

'glp_get_num_bin':
'''glp_get_num_bin --- retrieve number of binary columns

synopsis:

   int glp_get_num_bin(glp_prob *P);

returns:

The routine |glp_get_num_bin| returns the number of columns
(structural variables), which are marked as integer and whose lower
bound is zero and upper bound is one.
''',

'glp_get_col_type':
'''glp_get_col_type --- retrieve column type

synopsis:

   int glp_get_col_type(glp_prob *P, int j);

returns:

The routine |glp_get_col_type| returns the type of |j|-th
column, i.e. the type of corresponding structural variable, as follows:

|glpk.GLP_FR| --- free (unbounded) variable;

|glpk.GLP_LO| --- variable with lower bound;

|glpk.GLP_UP| --- variable with upper bound;

|glpk.GLP_DB| --- double-bounded variable;

|glpk.GLP_FX| --- fixed variable.
''',

'glp_get_col_bind':
'''glp_get_col_bind --- retrieve column index in the basis
header

synopsis:

   int glp_get_col_bind(glp_prob *P, int j);

returns:

The routine |glp_get_col_bind| returns the index $k$ of basic
variable $(x_B)_k$, $1<= k<= m$, which is $j$-th structural
variable (that is, the structural variable corresponding to $j$-th
column), $1<= j<= n$, in the current basis associated with the
specified problem object, where $m$ is the number of rows, $n$ is the
number of columns. However, if $j$-th structural variable is non-basic,
the routine returns zero.
''',

'glp_write_ipt':
'''glp_write_ipt --- write interior-point solution in GLPK
format

synopsis:

   int glp_write_ipt(glp_prob *P, const char *fname);

description:

The routine |glp_write_ipt| writes the current interior-point
solution to a text file in the GLPK format. (For description of the
GLPK interior-point solution format see Subsection ``Read
interior-point solution in GLPK format.'')

The character string |fname| specifies the name of the text file
to be written. (If the file name ends with suffix `|.gz|', the
routine |glp_write_ipt| compresses it "on the fly".)

returns:

If the operation was successful, the routine |glp_write_ipt|
returns zero. Otherwise, it prints an error message and returns
non-zero.
''',

'glp_minisat1':
'''No original doc found in glpk.''',

'glp_get_prob_name':
'''glp_get_prob_name --- retrieve problem name

synopsis:

   const char *glp_get_prob_name(glp_prob *P);

returns:

The routine |glp_get_prob_name| returns a pointer to an internal
buffer, which contains symbolic name of the problem. However, if the
problem has no assigned name, the routine returns |NULL|.
''',

'glp_write_cnfsat':
'''No original doc found in glpk.''',

'glp_set_row_bnds':
'''glp_set_row_bnds --- set (change) row bounds

synopsis:

 void glp_set_row_bnds(glp_prob *P, int i, int type,
double lb, double ub);}

description:

The routine |glp_set_row_bnds| sets (changes) the type and bounds
of |i|-th row (auxiliary variable) of the specified problem
object.

The parameters |type|, |lb|, and |ub| specify the type,
lower bound, and upper bound, respectively, as follows:


{cr@{}c@{}ll}
Type &{c}{Bounds} & Comment \\

|glpk.GLP_FR| & $-inf <$ &$ x $& $< +inf$
   & Free (unbounded) variable \\
|glpk.GLP_LO| & $lb <=$ &$ x $& $< +inf$
   & Variable with lower bound \\
|glpk.GLP_UP| & $-inf <$ &$ x $& $<= ub$
   & Variable with upper bound \\
|glpk.GLP_DB| & $lb <=$ &$ x $& $<= ub$
   & Double-bounded variable \\
|glpk.GLP_FX| & $lb =$ &$ x $& $= ub$
   & Fixed variable \\
''',

'glp_get_num_int':
'''glp_get_num_int --- retrieve number of integer columns

synopsis:

   int glp_get_num_int(glp_prob *P);

returns:

The routine |glp_get_num_int| returns the number of columns
(structural variables), which are marked as integer. Note that this
number { does} include binary columns.
''',

'glp_set_row_name':
'''glp_set_row_name --- assign (change) row name

synopsis:

   void glp_set_row_name(glp_prob *P, int i, const char *name);

description:

The routine |glp_set_row_name| assigns a given symbolic
|name| (1 up to 255 characters) to |i|-th row (auxiliary
variable) of the specified problem object.

If the parameter |name| is |NULL| or empty string, the
routine erases an existing name of $i$-th row.
''',

'glp_set_col_stat':
'''glp_set_col_stat --- set (change) column status

synopsis:

   void glp_set_col_stat(glp_prob *P, int j, int stat);

description:

The routine |glp_set_col_stat sets| (changes) the current status
of |j|-th column (structural variable) as specified by the
parameter |stat|:

|glpk.GLP_BS| --- make the column basic;

|glpk.GLP_NL| --- make the column non-basic;

|glpk.GLP_NU| --- make the column non-basic and set it to the upper
bound; if the column is not double-bounded, this status is equivalent
to |glpk.GLP_NL| (only in case of this routine);

|glpk.GLP_NF| --- the same as |glpk.GLP_NL| (only in case of this
routine);

|glpk.GLP_NS| --- the same as |glpk.GLP_NL| (only in case of this
routine).
''',

'glp_ipt_col_prim':
'''glp_ipt_col_prim --- retrieve column primal value

synopsis:

   double glp_ipt_col_prim(glp_prob *P, int j);

returns:

The routine |glp_ipt_col_prim| returns primal value of the
structural variable associated with |j|-th column.
''',

'glp_bf_updated':
'''glp_bf_updated --- check if the basis factorization has
been updated

synopsis:

   int glp_bf_updated(glp_prob *P);

returns:

If the basis factorization has been just computed from ``scratch'', the
routine |glp_bf_updated| returns zero. Otherwise, if the
factorization has been updated at least once, the routine returns
non-zero.
''',

'glp_get_it_cnt':
'''No original doc found in glpk.''',

'glp_mincost_lp':
'''No original doc found in glpk.''',

'glp_ipt_row_dual':
'''glp_ipt_row_dual --- retrieve row dual value

synopsis:

   double glp_ipt_row_dual(glp_prob *P, int i);

returns:

The routine |glp_ipt_row_dual| returns dual value (i.e. reduced
cost) of the auxiliary variable associated with |i|-th row.
''',

'glp_analyze_bound':
'''glp_analyze_bound --- analyze active bound of non-basic
variable

synopsis:

   void glp_analyze_bound(glp_prob *P, int k, double *limit1, int *var1,
                          double *limit2, int *var2);

description:

The routine |glp_analyze_bound| analyzes the effect of varying the
active bound of specified non-basic variable.

The non-basic variable is specified by the parameter $k$, where
$1<= k<= m$ means auxiliary variable of corresponding row, and
$m+1<= k<= m+n$ means structural variable (column).

Note that the current basic solution must be optimal, and the basis
factorization must exist.

Results of the analysis have the following meaning.

|value1| is the minimal value of the active bound, at which the
basis still remains primal feasible and thus optimal. |-DBL_MAX|
means that the active bound has no lower limit.

|var1| is the ordinal number of an auxiliary (1 to $m$) or
structural ($m+1$ to $m+n$) basic variable, which reaches its bound
first and thereby limits further decreasing the active bound being
analyzed. if |value1| = |-DBL_MAX|, |var1| is set to 0.

|value2| is the maximal value of the active bound, at which the
basis still remains primal feasible and thus optimal. |+DBL_MAX|
means that the active bound has no upper limit.

|var2| is the ordinal number of an auxiliary (1 to $m$) or
structural ($m+1$ to $m+n$) basic variable, which reaches its bound
first and thereby limits further increasing the active bound being
analyzed. if |value2| = |+DBL_MAX|, |var2| is set to 0.

The parameters |value1|, |var1|, |value2|, |var2|
can be specified as |NULL|, in which case corresponding information
is not stored.
''',

'glp_load_matrix':
'''glp_load_matrix --- load (replace) the whole constraint
matrix

synopsis:

   void glp_load_matrix(glp_prob *P, int ne, const int ia[],
                        const int ja[], const double ar[]);

description:

The routine |glp_load_matrix| loads the constraint matrix passed
in  the arrays |ia|, |ja|, and |ar| into the specified
problem object. Before loading the current contents of the constraint
matrix is destroyed.

Constraint coefficients (elements of the constraint matrix) should be
specified as triplets (|ia[k]|, |ja[k]|, |ar[k]|) for
$k=1,...,ne$, where |ia[k]| is the row index, |ja[k]| is
the column index, and |ar[k]| is a numeric value of corresponding
constraint coefficient. The parameter |ne| specifies the total
number of (non-zero) elements in the matrix to be loaded. Coefficients
with identical indices are not allowed. Zero coefficients are allowed,
however, they are not stored in the constraint matrix.

If the parameter |ne| is 0, the parameters |ia|, |ja|,
and/or |ar| can be specified as |NULL|.
''',

'glp_delete_prob':
'''glp_delete_prob --- delete problem object

synopsis:

   void glp_delete_prob(glp_prob *P);

description:

The routine |glp_delete_prob| deletes a problem object, which the
parameter |lp| points to, freeing all the memory allocated to this
object.
''',

'glp_add_rows':
'''glp_add_rows --- add new rows to problem object

synopsis:

   int glp_add_rows(glp_prob *P, int nrs);

description:

The routine |glp_add_rows| adds |nrs| rows (constraints) to
the specified problem object. New rows are always added to the end of
the row list, so the ordinal numbers of existing rows are not changed.

Being added each new row is initially free (unbounded) and has empty
list of the constraint coefficients.

Each new row becomes a non-active (non-binding) constraint, i.e. the
corresponding auxiliary variable is marked as basic.

If the basis factorization exists, adding row(s) invalidates it.

returns:

The routine |glp_add_rows| returns the ordinal number of the first
new row added to the problem object.
''',

'glp_std_basis':
'''glp_std_basis --- construct standard initial LP basis

synopsis:

   void glp_std_basis(glp_prob *P);

description:

The routine |glp_std_basis| constructs the ``standard'' (trivial)
initial LP basis for the specified problem object.

In the ``standard'' LP basis all auxiliary variables (rows) are basic,
and all structural variables (columns) are non-basic (so the
corresponding basis matrix is unity).
''',

'glp_get_col_stat':
'''glp_get_col_stat --- retrieve column status

synopsis:

   int glp_get_col_stat(glp_prob *P, int j);

returns:

The routine |glp_get_col_stat| returns current status assigned to
the structural variable associated with |j|-th column as follows:

|glpk.GLP_BS| --- basic variable;

|glpk.GLP_NL| --- non-basic variable on its lower bound;

|glpk.GLP_NU| --- non-basic variable on its upper bound;

|glpk.GLP_NF| --- non-basic free (unbounded) variable;

|glpk.GLP_NS| --- non-basic fixed variable.
''',

'glp_unscale_prob':
'''glp_unscale_prob --- unscale problem data



synopsis:

   void glp_unscale_prob(glp_prob *P);

description:

The routine |glp_unscale_prob| performs unscaling of problem data
for the specified problem object.

``Unscaling'' means replacing the current scaling matrices $R$ and $S$
by unity matrices that cancels the scaling effect.
''',

'glp_create_index':
'''glp_create_index --- create the name index

synopsis:

   void glp_create_index(glp_prob *P);

description:

The routine |glp_create_index| creates the name index for the
specified problem object. The name index is an auxiliary data
structure, which is intended to quickly (i.e. for logarithmic time)
find rows and columns by their names.

This routine can be called at any time. If the name index already
exists, the routine does nothing.
''',

'glp_check_cnfsat':
'''No original doc found in glpk.''',

'glp_read_ipt':
'''glp_read_ipt --- read interior-point solution in GLPK
format

synopsis:

   int glp_read_ipt(glp_prob *P, const char *fname);

description:

The routine |glp_read_ipt| reads interior-point solution from
a text file in the GLPK format. (For description of the format see
below.)

The character string |fname| specifies the name of the text file
to be read in. (If the file name ends with suffix `|.gz|', the
file is assumed to be compressed, in which case the routine
|glp_read_ipt| decompresses it "on the fly".)


returns:

If the operation was successful, the routine |glp_read_ipt|
returns zero. Otherwise, it prints an error message and returns
non-zero.
''',

'glp_read_lp':
'''glp_read_lp --- read problem data in CPLEX LP format

synopsis:

 int glp_read_lp(glp_prob *P, const glp_cpxcp *parm,
const char *fname);}

description:

The routine |glp_read_lp| reads problem data in CPLEX LP format
from a text file. (The CPLEX LP format is described in Appendix
, page.)

The parameter |parm| is reserved for use in the future and should
be specified as |NULL|.

The character string |fname| specifies a name of the text file to
be read in. (If the file name ends with suffix `|.gz|', the file
is assumed to be compressed, in which case the routine
|glp_read_lp| decompresses it ``on the fly''.)

Note that before reading data the current content of the problem object
is completely erased with the routine |glp_erase_prob|.

returns:

If the operation was successful, the routine |glp_read_lp| returns
zero. Otherwise, it prints an error message and returns non-zero.
''',

'glp_intfeas1':
'''No original doc found in glpk.''',

'glp_ftran':
'''glp_ftran --- perform forward transformation

synopsis:

   void glp_ftran(glp_prob *P, double x[]);

description:

The routine |glp_ftran| performs forward transformation (FTRAN),
i.e. it solves the system $Bx=b$, where $B$ is the basis matrix
associated with the specified problem object, $x$ is the vector of
unknowns to be computed, $b$ is the vector of right-hand sides.

On entry to the routine elements of the vector $b$ should be stored in
locations |x[1]|, ..., |x[m]|, where $m$ is the number of
rows. On exit the routine stores elements of the vector $x$ in the same
locations.
''',

'glp_exact':
'''glp_exact --- solve LP problem in exact arithmetic

synopsis:

   int glp_exact(glp_prob *P, const glp_smcp *parm);

description:

The routine |glp_exact| is a tentative implementation of the
primal two-phase simplex method based on exact (rational) arithmetic.
It is similar to the routine |glp_simplex|, however, for all
internal computations it uses arithmetic of rational numbers, which is
exact in mathematical sense, i.e. free of round-off errors unlike
floating-point arithmetic.

Note that the routine |glp_exact| uses only two control parameters
passed in the structure |glp_smcp|, namely, |it_lim| and
|tm_lim|.

returns:


0 & The LP problem instance has been successfully solved. (This code
does { not} necessarily mean that the solver has found optimal
solution. It only means that the solution process was successful.) \\

|glpk.GLP_EBADB| & Unable to start the search, because the initial basis
specified in the problem object is invalid---the number of basic
(auxiliary and structural) variables is not the same as the number of
rows in the problem object.\\

|glpk.GLP_ESING| & Unable to start the search, because the basis matrix
corresponding to the initial basis is exactly singular.\\

|glpk.GLP_EBOUND| & Unable to start the search, because some
double-bounded (auxiliary or structural) variables have incorrect
bounds.\\

|glpk.GLP_EFAIL| & The problem instance has no rows/columns.\\

|glpk.GLP_EITLIM| & The search was prematurely terminated, because the
simplex iteration limit has been exceeded.\\

|glpk.GLP_ETMLIM| & The search was prematurely terminated, because the
time limit has been exceeded.\\
''',

'glp_copy_prob':
'''glp_copy_prob --- copy problem object content

synopsis:

   void glp_copy_prob(glp_prob *dest, glp_prob *prob, int names);

description:

The routine |glp_copy_prob| copies the content of the problem
object |prob| to the problem object |dest|.

The parameter |names| is a flag. If it is |glpk.GLP_ON|,
the routine also copies all symbolic names; otherwise, if it is
|glpk.GLP_OFF|, no symbolic names are copied.
''',

'glp_get_num_nz':
'''glp_get_num_nz --- retrieve number of constraint
coefficients

synopsis:

   int glp_get_num_nz(glp_prob *P);

returns:

The routine |glp_get_num_nz| returns the number of non-zero
elements in the constraint matrix of the specified problem object.
''',

'glp_ipt_row_prim':
'''glp_ipt_row_prim --- retrieve row primal value

synopsis:

   double glp_ipt_row_prim(glp_prob *P, int i);

returns:

The routine |glp_ipt_row_prim| returns primal value of the
auxiliary variable associated with |i|-th row.
''',

'glp_ipt_status':
'''glp_ipt_status --- determine solution status

synopsis:

   int glp_ipt_status(glp_prob *P);

returns:

The routine |glp_ipt_status| reports the status of a solution
found by the interior-point solver as follows:

|glpk.GLP_UNDEF | --- interior-point solution is undefined;

|glpk.GLP_OPT   | --- interior-point solution is optimal;

|glpk.GLP_INFEAS| --- interior-point solution is infeasible;

|glpk.GLP_NOFEAS| --- no feasible primal-dual solution exists.
''',

'glp_read_sol':
'''glp_read_sol --- read basic solution in GLPK format

synopsis:

   int glp_read_sol(glp_prob *P, const char *fname);

description:

The routine |glp_read_sol| reads basic solution from a text file
in the GLPK format. (For description of the format see below.)

The character string |fname| specifies the name of the text file
to be read in. (If the file name ends with suffix `|.gz|', the
file is assumed to be compressed, in which case the routine
|glp_read_sol| decompresses it "on the fly".)

returns:

If the operation was successful, the routine |glp_read_sol|
returns zero. Otherwise, it prints an error message and returns
non-zero.
''',

'glp_get_mat_row':
'''glp_get_mat_row --- retrieve row of the constraint
matrix

synopsis:

   int glp_get_mat_row(glp_prob *P, int i, int ind[], double val[]);

description:

The routine |glp_get_mat_row| scans (non-zero) elements of
|i|-th row of the constraint matrix of the specified problem
object and stores their column indices and numeric values to locations
|ind[1]|, ..., |ind[len]| and |val[1]|, ...,
|val[len]|, respectively, where $0<={ len}<= n$ is the
number of elements in $i$-th row, $n$ is the number of columns.

The parameter |ind| and/or |val| can be specified as
|NULL|, in which case corresponding information is not stored.


returns:

The routine |glp_get_mat_row| returns the length |len|, i.e.
the number of (non-zero) elements in |i|-th row.
''',

'glp_get_col_name':
'''glp_get_col_name --- retrieve column name

synopsis:

   const char *glp_get_col_name(glp_prob *P, int j);

returns:

The routine |glp_get_col_name| returns a pointer to an internal
buffer, which contains a symbolic name assigned to |j|-th column.
However, if the column has no assigned name, the routine returns
|NULL|.
''',

'glp_get_row_type':
'''glp_get_row_type --- retrieve row type

synopsis:

   int glp_get_row_type(glp_prob *P, int i);

returns:

The routine |glp_get_row_type| returns the type of |i|-th
row, i.e. the type of corresponding auxiliary variable, as follows:

|glpk.GLP_FR| --- free (unbounded) variable;

|glpk.GLP_LO| --- variable with lower bound;

|glpk.GLP_UP| --- variable with upper bound;

|glpk.GLP_DB| --- double-bounded variable;

|glpk.GLP_FX| --- fixed variable.
''',

'glp_get_bfcp':
'''glp_get_bfcp --- retrieve basis factorization control
parameters

synopsis:

   void glp_get_bfcp(glp_prob *P, glp_bfcp *parm);

description:

The routine |glp_get_bfcp| retrieves control parameters, which are
used on computing and updating the basis factorization associated with
the specified problem object.

Current values of the control parameters are stored in
a |glp_bfcp| structure, which the parameter |parm| points to.
For a detailed description of the structure |glp_bfcp| see
comments to the routine |glp_set_bfcp| in the next subsection.
''',

'glp_get_row_dual':
'''glp_get_row_dual --- retrieve row dual value

synopsis:

   double glp_get_row_dual(glp_prob *P, int i);

returns:

The routine |glp_get_row_dual| returns dual value (i.e. reduced
cost) of the auxiliary variable associated with |i|-th row.
''',

'glp_get_obj_dir':
'''glp_get_obj_dir --- retrieve optimization direction
flag

synopsis:

   int glp_get_obj_dir(glp_prob *P);

returns:

The routine |glp_get_obj_dir| returns the optimization direction
flag (i.e. ``sense'' of the objective function):

|glpk.GLP_MIN| means minimization;

|glpk.GLP_MAX| means maximization.
''',

'glp_scale_prob':
'''glp_scale_prob --- scale problem data



synopsis:

   void glp_scale_prob(glp_prob *P, int flags);

description:

The routine |glp_scale_prob| performs automatic scaling of problem
data for the specified problem object.

The parameter |flags| specifies scaling options used by the
routine. The options can be combined with the bitwise OR operator and
may be the following:

|glpk.GLP_SF_GM  | --- perform geometric mean scaling;

|glpk.GLP_SF_EQ  | --- perform equilibration scaling;

|glpk.GLP_SF_2N  | --- round scale factors to nearest power of two;

|glpk.GLP_SF_SKIP| --- skip scaling, if the problem is well scaled.

The parameter |flags| may be also specified as |glpk.GLP_SF_AUTO|,
in which case the routine chooses the scaling options automatically.
''',

'glp_get_rii':
'''glp_get_rii --- retrieve row scale factor

synopsis:

   double glp_get_rii(glp_prob *P, int i);

returns:

The routine |glp_get_rii| returns current scale factor $r_{ii}$
for $i$-th row of the specified problem object.
''',

'glp_mip_status':
'''glp_mip_status --- determine status of MIP solution

synopsis:

   int glp_mip_status(glp_prob *P);

returns:

The routine |glp_mip_status| reports the status of a MIP solution
found by the MIP solver as follows:

|glpk.GLP_UNDEF | --- MIP solution is undefined;

|glpk.GLP_OPT   | --- MIP solution is integer optimal;

|glpk.GLP_FEAS  | --- MIP solution is integer feasible, however, its
optimality (or non-optimality) has not been proven, perhaps due to
premature termination of the search;

|glpk.GLP_NOFEAS| --- problem has no integer feasible solution (proven
by the solver).
''',

'glp_set_rii':
'''glp_set_rii --- set (change) row scale factor

synopsis:

   void glp_set_rii(glp_prob *P, int i, double rii);

description:

The routine |glp_set_rii| sets (changes) the scale factor $r_{ii}$
for $i$-th row of the specified problem object.
''',

'glp_write_lp':
'''glp_write_lp --- write problem data in CPLEX LP format

synopsis:

 int glp_write_lp(glp_prob *P, const glp_cpxcp *parm,
const char *fname);}

description:

The routine |glp_write_lp| writes problem data in CPLEX LP format
to a text file. (The CPLEX LP format is described in Appendix
, page.)

The parameter |parm| is reserved for use in the future and should
be specified as |NULL|.

The character string |fname| specifies a name of the text file to
be written out. (If the file name ends with suffix `|.gz|', the
file is assumed to be compressed, in which case the routine
|glp_write_lp| performs automatic compression on writing it.)

returns:

If the operation was successful, the routine |glp_write_lp|
returns zero. Otherwise, it prints an error message and returns
non-zero.
''',

'glp_set_col_kind':
'''glp_set_col_kind --- set (change) column kind

synopsis:

   void glp_set_col_kind(glp_prob *P, int j, int kind);

description:

The routine |glp_set_col_kind| sets (changes) the kind of
|j|-th column (structural variable) as specified by the parameter
|kind|:

|glpk.GLP_CV| --- continuous variable;

|glpk.GLP_IV| --- integer variable;

|glpk.GLP_BV| --- binary variable.

Setting a column to |glpk.GLP_BV| has the same effect as if it were
set to |glpk.GLP_IV|, its lower bound were set 0, and its upper bound
were set to 1.
'''
}#_related
    
    if 'glp_delete_prob' not in _related:
        print("Warning: glp_delete_prob is abscent!")

    # decorator + exec
    @staticmethod
    def _init(__init__):
        def init(me, *args, **kwds):
            me._glp_ = glpk.glp_create_prob()
            if __init__: __init__(me, *args, **kwds)
        return init
    
    @staticmethod
    def _del(__del__):
        def delete(me):
            if me.verb:
                print("__del__ is deleting problem:", me.name)
            if __del__: __del__(me)
            glpk.glp_delete_prob(me._glp_)
            del me._glp_
        return delete

    @staticmethod
    def defs(names, decorated=False): #do exec right after __init__ and __del__ defs
        '''param decorated: if already decorated __init__ and __del__.'''
        
        for name, doc in _LinkGLPK._related.items():
            m = name[4:]
            if m in names: 
                mm = names[m]
                m = name[3:]
                assert m not in names
                mm.__doc__ = """
{oldoc}

Note: this is a manual wrapper for the glpk routine glp{name}. 
the automatic wrapper is model.{name}, for the glpk documentation, 
try this at a python interactive session:
>>> from pymprog import model
>>> help(model.{name})

""".format(name = m, doc = doc, oldoc = 
        mm.__doc__ or "Note: No manual docstr found.")

            yield '''
def {name}(me, *args):
    """Automatic wrapper for glpk routine, documented as follows:

{doc}
"""
    return glpk.{gname}(me._glp_, *args)
'''.format(name=m, gname=name, doc = doc)

        _ft_ = """__{n}__ = _LinkGLPK._{n}(
            __{n}__ if '__{n}__' in locals() else None)"""
        if not decorated: yield _ft_.format(n = 'init')
        if not decorated: yield _ft_.format(n='del')

    ## Code below implements the metaclass way
    def __new__(cls, name, bases, dct):
        
        def add_fun(f, name, gname):
            def meth(me, *args): return f(me._glp_, *args)
            meth.__name__ = gname
            meth.__doc__ = \
            "Automatic wrapper for glpk routine, documented as follows:\n\n"\
                           + _LinkGLPK._related[gname]
            dct[name] = meth

        for fadd, doc in _LinkGLPK._related.items():
            f = getattr(glpk, fadd, None)
            if f is None:
                print("Meta: %s seems missing in swiglpk."%fadd)
                continue 
            m = fadd[4:]
            if m in dct: 
                mm = dct[m]
                m = fadd[3:] # starts with _
                mm.__doc__ = """
{oldoc}

Note: this is a manual wrapper for the glpk routine glp{name}. 
the automatic wrapper is model.{name}, for the glpk documentation, 
try this at a python interactive session:
>>> from pymprog import model
>>> help(model.{name})

""".format(name = m, doc = doc, oldoc = 
        mm.__doc__ or "Note: No manual docstr found.")

            add_fun(f, m, fadd)

        #deal with __init__ and __del__
        init = dct.get('__init__', None)
        def _init_(me, *args, **kwds):
            me._glp_ = glpk.glp_create_prob()
            if init: init(me, *args, **kwds)
        dct['__init__'] = _init_

        delf = dct.get('__del__', None)
        def _del_(me):
           if me.verb:
                print("__del__ is deleting problem:", me.name)
           if delf: delf(me)
           glpk.glp_delete_prob(me._glp_)
           me._glp_ = None
        dct['__del__'] = _del_

        return super(_LinkGLPK, cls).__new__(cls, name, bases, dct)

_globalized = ['std_basis']
def _globalize(meth):
    name = meth.__name__
    _globalized.append(name)
    return meth
def _global_defs():
        gft = """
def {name}(*args, **kwds):
    '''Calls the method {name} on the current model.
Here is the documentation on the original method:

{doc}
'''
    if model._prob_ is None: raise Exception(
       'No global model instance in place yet, create one first!')
    return model._prob_.{name}(*args, **kwds)
"""
        for name in _globalized:
            f = getattr(model, name)
            assert callable(f)
            yield gft.format(name=name, 
                doc=getattr(model, name).__doc__)

#@_with_metaclass(_LinkGLPK) #the metaclass way
class model(object):
   """this object holds an glpk.LPX() object.
    you can retrieve it by the "solver()" method.
    for how to use that object to solve models,
    you can refer to PyGLPK documentation.
    Once the model is solved, you can access
    the results via that object. You can also 
    access the solution by the variables created
    via the "var()" method, or find out the 
    status of the constraints by the constraints
    created by the "st()" method."""
   #only for implementation of the global interface.
   _prob_ = None #current model


   opt_kinds=('simplex', 'exact', 'interior', 'intopt')
   num_lp_solvers = 3 #now many lp solvers in opt_kinds

   def update_lazy(me):
      #print('update params', cls.dirtyset)
      if not me.lazy: return
      for e in me.lazy:
        e.update(me) 
      me.lazy = set()

   def update1(me, up):
       if up in me.lazy:
          me.lazy.discard(up)
          up.update(me)
          return True
       return False

   def add_lazy(me, e):
       me.lazy.add(e)

   def replace_last(me, last): # msg mechanism
       last, me._last = me._last, last
       return last
       
   def __init__(me, name, as_global=False):
      assert name
      me.name = str(name)
      me.lazy = set()
      me.verb = False
      # new ways of doing option
      me.options = { kind: {} 
        for kind in me.opt_kinds
      } # solver options

      me._solved = me._last = None

      # or use lists of weakrefs
      me._colmap = model._idxmap() 
      me._rowmap = model._idxmap() 

      if as_global:
          prob = model._prob_
          if prob: prob.end(prob.name)
          model._prob_ = me

   def __repr__(me):
       return 'model(%r) %s the default model.'%(me.name,
               'is' if me is model._prob_ else 'is not')

   def add_rows(me, n):
       "add_rows with transparent index mapping." 
       return me._rowmap.add(n, me._add_rows)
   def del1row(me, rid):
       "delete one row with transparent index mapping." 
       me._rowmap.del1(rid, me._del_rows)
   def del_rows(me, ids):
       "delete many rows with transparent index mapping." 
       me._rowmap.delmany(ids, me._del_rows)
   def set_mat_row(me, rid, n, cidx, cval):
       "set_mat_row with transparent index mapping." 
       rid = me._rowmap.map(rid)
       if rid: return me._set_mat_row(rid, n, cidx, cval)
   def set_row_bnds(me, rid, bt, lo, hi):
       "set_row_bnds with transparent index mapping." 
       rid = me._rowmap.map(rid)
       if rid: return me._set_row_bnds(rid, bt, lo, hi)
   def get_row_lb(me, rid):
       "get_row_lb with transparent index mapping." 
       rid = me._rowmap.map(rid)
       if rid: return me._get_row_lb(rid)
   def get_row_ub(me, rid):
       "get_row_ub with transparent index mapping." 
       rid = me._rowmap.map(rid)
       if rid: return me._get_row_ub(rid)
   def get_row_type(me, rid):
       "get_row_type with transparent index mapping." 
       rid = me._rowmap.map(rid)
       if rid: return me._get_row_type(xid)
   def get_row_stat(me, rid):
       "get_row_stat with transparent index mapping." 
       rid = me._rowmap.map(rid)
       if rid: return me._get_row_stat(rid)
   def mip_row_val(me, rid):
       "mip_row_val with transparent index mapping." 
       rid = me._rowmap.map(rid)
       if rid: return me._mip_row_val(rid)
   def get_row_dual(me, rid):
       "get_row_dual with transparent index mapping." 
       rid = me._rowmap.map(rid)
       if rid: return me._get_row_dual(rid)
   def get_row_prim(me, rid):
       "get_row_prim with transparent index mapping." 
       rid = me._rowmap.map(rid)
       if rid: return me._get_row_prim(rid)
   def get_row_name(me, rid):
       "get_row_name with transparent index mapping." 
       rid = me._rowmap.map(rid)
       if rid: return me._get_row_name(rid)

   def add_cols(me, n):
       "add_cols with transparent index mapping." 
       return me._colmap.add(n, me._add_cols)
   def del1col(me, xid):
       "delete one col with transparent index mapping." 
       me._colmap.del1(xid, me._del_cols)
   def del_cols(me, ids):
       "delete many cols with transparent index mapping." 
       me._colmap.delmany(ids, me._del_cols)
   def set_col_bnds(me, xid, bt, lo, hi):
       "set_col_bnds with transparent index mapping." 
       xid = me._colmap.map(xid) if xid else xid
       if xid > 0: return me._set_col_bnds(xid, bt, lo, hi)
   def get_col_lb(me, xid):
       "get_col_lb with transparent index mapping." 
       xid = me._colmap.map(xid) if xid else xid
       if xid> 0: return me._get_col_lb(xid)
   def get_col_ub(me, xid):
       "get_col_ub with transparent index mapping." 
       xid = me._colmap.map(xid) if xid else xid
       if xid > 0: return me._get_col_ub(xid)
   def set_col_kind(me, xid, kind):
       "set_col_kind with transparent index mapping." 
       xid = me._colmap.map(xid) if xid else xid
       if xid > 0: return me._set_col_kind(xid, kind)
   def get_col_kind(me, xid):
       "get_col_kind with transparent index mapping." 
       xid = me._colmap.map(xid) if xid else xid
       if xid > 0: return me._get_col_kind(xid)
   def get_col_type(me, xid):
       "get_col_type with transparent index mapping." 
       xid = me._colmap.map(xid) if xid else xid
       if xid > 0: return me._get_col_type(xid)
   def get_col_stat(me, xid):
       "get_col_stat with transparent index mapping." 
       xid = me._colmap.map(xid) if xid else xid
       if xid > 0: return me._get_col_stat(xid)
   def mip_col_val(me, xid):
       "mip_col_val with transparent index mapping." 
       xid = me._colmap.map(xid) if xid else xid
       if xid > 0: return me._mip_col_val(xid)
   def get_col_dual(me, xid):
       "get_col_dual with transparent index mapping." 
       xid = me._colmap.map(xid) if xid else xid
       if xid > 0: return me._get_col_dual(xid)
   def get_col_prim(me, xid):
       "get_col_prim with transparent index mapping." 
       xid = me._colmap.map(xid) if xid else xid
       if xid > 0: return me._get_col_prim(xid)
   def get_col_name(me, xid):
       "get_col_name with transparent index mapping." 
       xid = me._colmap.map(xid) if xid else xid
       if xid>0: return me._get_col_name(xid)
 
   def set_obj_coef(me, xid, v):
       "set_obj_coef with transparent index mapping." 
       if xid == 0: return me._set_obj_coef(xid, v)
       xid = me._colmap.map(xid) if xid else xid
       if xid > 0: return me._set_obj_coef(xid, v)
   def get_obj_coef(me, xid ):
       "get_obj_coef with transparent index mapping." 
       if xid == 0: return me._get_obj_coef(xid)
       xid = me._colmap.map(xid) if xid else xid
       if xid>0: return me._get_obj_coef(xid)

   class _idxmap(object):
        def __init__(me):
            me.lmap = None
            me.nmap = 0
        def newmap(me):
            me.lmap = [i for i in range(me.nmap+1)] 
            me.lmap[0] = -1 #head
        def map(me, xid): 
            if me.lmap and 0< xid < len(me.lmap): 
               return me.lmap[xid] 
            return xid if not me.lmap and xid <=me.nmap else 0 
        def add(me, n, call=None):
            if call: call(n)
            idx = me.nmap + 1
            me.nmap += n 
            if not me.lmap: return idx
            me.lmap.extend(range(idx, idx+n))
            return len(me.lmap) - n
        def del1(me, xid, call = None):
            mid = me.map(xid)
            assert mid > 0 
            if call: 
                xa = glpk.intArray(2)
                xa[1] = mid
                call(1, xa)
            if not me.lmap:
                if mid == me.nmap: #last col
                    me.nmap -= 1
                    return
                me.newmap() 
            me.lmap[xid] = 0
            while me.lmap[-1] == 0:
                del me.lmap[-1]
            for k in range(xid+1, len(me.lmap)):
                v = me.lmap[k]
                if v: me.lmap[k] = v-1
            if len(me.lmap)==1: 
                me.lmap == None
            me.nmap -= 1

        def delmany(me, idx, call=None):
            idx.sort()
            idx = [d for i,d in enumerate(idx) 
                    if i==0 or idx[i-1]!=d]
            cc = len(idx)
            if call:
                xa = glpk.intArray(cc+1)
                for i, xid in enumerate(idx):
                    xa[1+i] = me.map(xid)
                    assert xa[1+i] > 0
                call(cc, xa)
            if not me.lmap:
                if me.map(idx[0]) + cc - 1 == me.nmap: #last cols
                    me.nmap -= cc
                    return
                me.newmap() 
            for xid in idx: me.lmap[xid] = 0
            while me.lmap[-1] == 0:
                del me.lmap[-1]
            for j, xx in enumerate(idx):
                if not j: xid=xx; continue
                if xx >= len(me.lmap): 
                    xx = len(me.lmap) 
                for k in range(xid+1, xx):
                    v = me.lmap[k]
                    if v: me.lmap[k] = v-j
                    #print(k, v, j, v-j)
                if xx == len(me.lmap): break
                xid = xx
            else:
                for k in range(xid + 1, len(me.lmap)):
                    v = me.lmap[k]
                    if v: me.lmap[k] = v-j-1
                    #print(k, v, j, v-j-1)
            if len(me.lmap) ==1: 
                me.lmap == None
            me.nmap -= cc

   def newcon(me, lo, expr, hi):
       assert not isConst(expr) # _parex
       assert isConst(lo) and isConst(hi)
       rid = me.add_rows(1)
       c = _cons(rid, lo, expr, hi)
       if me.verb: print(c)
       return c

   _opt_help = {

           "simplex":

'''This paragraph describes all control parameters currently used in the
simplex and exact solver. Symbolic names of control parameters are names of
corresponding members in the structure |glp_smcp|.

{int msg_lev} (default: {GLP_MSG_ALL})

Message level for terminal output:

|glpk.GLP_MSG_OFF| --- no output;

|glpk.GLP_MSG_ERR| --- error and warning messages only;

|glpk.GLP_MSG_ON | --- normal output;

|glpk.GLP_MSG_ALL| --- full output (including informational messages).

{int meth} (default: {GLP_PRIMAL})

Simplex method option:

|glpk.GLP_PRIMAL| --- use two-phase primal simplex;

|glpk.GLP_DUAL  | --- use two-phase dual simplex;

|glpk.GLP_DUALP | --- use two-phase dual simplex, and if it fails,
switch to the primal simplex.

{int pricing} (default: {GLP_PT_PSE})

Pricing technique:

|glpk.GLP_PT_STD| --- standard (``textbook'');

|glpk.GLP_PT_PSE| --- projected steepest edge.

{int r_test} (default: {GLP_RT_HAR})

Ratio test technique:

|glpk.GLP_RT_STD| --- standard (``textbook'');

|glpk.GLP_RT_HAR| --- Harris' two-pass ratio test.

{double tol_bnd} (default: {1e-7})

Tolerance used to check if the basic solution is primal feasible.
(Do not change this parameter without detailed understanding its
purpose.)

{double tol_dj} (default: {1e-7})

Tolerance used to check if the basic solution is dual feasible.
(Do not change this parameter without detailed understanding its
purpose.)

{double tol_piv} (default: {1e-9})

Tolerance used to choose eligble pivotal elements of the simplex table.
(Do not change this parameter without detailed understanding its
purpose.)

{double obj_ll} (default: {-DBL_MAX})

Lower limit of the objective function. If the objective function
reaches this limit and continues decreasing, the solver terminates the
search. (Used in the dual simplex only.)

{double obj_ul} (default: {+DBL_MAX})

Upper limit of the objective function. If the objective function
reaches this limit and continues increasing, the solver terminates the
search. (Used in the dual simplex only.)

{int it_lim} (default: {INT_MAX})

Simplex iteration limit.

{int tm_lim} (default: {INT_MAX})

Searching time limit, in milliseconds.

{int out_frq} (default: {500})

Output frequency, in iterations. This parameter specifies how
frequently the solver sends information about the solution process to
the terminal.

{int out_dly} (default: {0})

Output delay, in milliseconds. This parameter specifies how long the
solver should delay sending information about the solution process to
the terminal.

{int presolve} (default: {GLP_OFF})

LP presolver option:

|glpk.GLP_ON | --- enable using the LP presolver;

|glpk.GLP_OFF| --- disable using the LP presolver.
''',

     'interior':

'''This paragraph describes all control parameters currently used in the
interior-point solver. Symbolic names of control parameters are names of
corresponding members in the structure |glp_iptcp|.

{int msg_lev} (default: {GLP_MSG_ALL})

Message level for terminal output:

|glpk.GLP_MSG_OFF|---no output;

|glpk.GLP_MSG_ERR|---error and warning messages only;

|glpk.GLP_MSG_ON |---normal output;

|glpk.GLP_MSG_ALL|---full output (including informational messages).

{int ord_alg} (default: {GLP_ORD_AMD})

Ordering algorithm used prior to Cholesky factorization:

|glpk.GLP_ORD_NONE  |---use natural (original) ordering;

|glpk.GLP_ORD_QMD   |---quotient minimum degree (QMD);

|glpk.GLP_ORD_AMD   |---approximate minimum degree (AMD);

|glpk.GLP_ORD_SYMAMD|---approximate minimum degree (SYMAMD).''',

    'intopt':

'''This paragraph describes all control parameters currently used in the
MIP solver. Symbolic names of control parameters are names of
corresponding members in the structure |glp_iocp|.

{int msg_lev} (default: {GLP_MSG_ALL})

Message level for terminal output:

|glpk.GLP_MSG_OFF| --- no output;

|glpk.GLP_MSG_ERR| --- error and warning messages only;

|glpk.GLP_MSG_ON | --- normal output;

|glpk.GLP_MSG_ALL| --- full output (including informational messages).


{int br_tech} (default: {GLP_BR_DTH})

Branching technique option:

|glpk.GLP_BR_FFV| --- first fractional variable;

|glpk.GLP_BR_LFV| --- last fractional variable;

|glpk.GLP_BR_MFV| --- most fractional variable;

|glpk.GLP_BR_DTH| --- heuristic by Driebeck and Tomlin;

|glpk.GLP_BR_PCH| --- hybrid pseudo-cost heuristic.


{int bt_tech} (default: {GLP_BT_BLB})

Backtracking technique option:

|glpk.GLP_BT_DFS| --- depth first search;

|glpk.GLP_BT_BFS| --- breadth first search;

|glpk.GLP_BT_BLB| --- best local bound;

|glpk.GLP_BT_BPH| --- best projection heuristic.


{int pp_tech} (default: {GLP_PP_ALL})

Preprocessing technique option:

|glpk.GLP_PP_NONE| --- disable preprocessing;

|glpk.GLP_PP_ROOT| --- perform preprocessing only on the root level;

|glpk.GLP_PP_ALL | --- perform preprocessing on all levels.


{int sr_heur} (default: {GLP_ON})

Simple rounding heuristic option:

|glpk.GLP_ON | --- enable applying the simple rounding heuristic;

|glpk.GLP_OFF| --- disable applying the simple rounding heuristic.


{int fp_heur} (default: {GLP_OFF})

Feasibility pump heuristic option:

|glpk.GLP_ON | --- enable applying the feasibility pump heuristic;

|glpk.GLP_OFF| --- disable applying the feasibility pump heuristic.


{int ps_heur} (default: {GLP_OFF})

Proximity search heuristic footnote{The Fischetti--Monaci Proximity
Search (a.k.a. Proxy) heuristic. This algorithm is often capable of
rapidly improving a feasible solution of a MIP problem with binary
variables. It allows to quickly obtain suboptimal solutions in some
problems which take too long time to be solved to optimality.} option:

|glpk.GLP_ON | --- enable applying the proximity search heuristic;

|glpk.GLP_OFF| --- disable applying the proximity search pump heuristic.


{int ps_tm_lim} (default: {60000})

Time limit, in milliseconds, for the proximity search heuristic (see
above).


{int gmi_cuts} (default: {GLP_OFF})

Gomory's mixed integer cut option:

|glpk.GLP_ON | --- enable generating Gomory's cuts;

|glpk.GLP_OFF| --- disable generating Gomory's cuts.


{int mir_cuts} (default: {GLP_OFF})

Mixed integer rounding (MIR) cut option:

|glpk.GLP_ON | --- enable generating MIR cuts;

|glpk.GLP_OFF| --- disable generating MIR cuts.


{int cov_cuts} (default: {GLP_OFF})

Mixed cover cut option:

|glpk.GLP_ON | --- enable generating mixed cover cuts;

|glpk.GLP_OFF| --- disable generating mixed cover cuts.


{int clq_cuts} (default: {GLP_OFF})

Clique cut option:

|glpk.GLP_ON | --- enable generating clique cuts;

|glpk.GLP_OFF| --- disable generating clique cuts.


{double tol_int} (default: {1e-5})

Absolute tolerance used to check if optimal solution to the current LP
relaxation is integer feasible. (Do not change this parameter without
detailed understanding its purpose.)


{double tol_obj} (default: {1e-7})

Relative tolerance used to check if the objective value in optimal
solution to the current LP relaxation is not better than in the best
known integer feasible solution. (Do not change this parameter without
detailed understanding its purpose.)


{double mip_gap} (default: {0.0})

The relative mip gap tolerance. If the relative mip gap for currently
known best integer feasible solution falls below this tolerance, the
solver terminates the search. This allows obtainig suboptimal integer
feasible solutions if solving the problem to optimality takes too long
time.


{int tm_lim} (default: {INT_MAX})

Searching time limit, in milliseconds.


{int out_frq} (default: {5000})

Output frequency, in milliseconds. This parameter specifies how
frequently the solver sends information about the solution process to
the terminal.


{int out_dly} (default: {10000})

Output delay, in milliseconds. This parameter specifies how long the
solver should delay sending information about solution of the current
LP relaxation with the simplex method to the terminal.


{void (*cb_func)(glp_tree *tree, void *info)}
(default: {NULL})

Entry point to the user-defined callback routine. |NULL| means
the advanced solver interface is not used. For more details see Chapter
``Branch-and-Cut API Routines''.


{void *cb_info} (default: {NULL})

Transit pointer passed to the routine |cb_func| (see above).

{int cb_size} (default: {0})

The number of extra (up to 256) bytes allocated for each node of the
branch-and-bound tree to store application-specific data. On creating
a node these bytes are initialized by binary zeros.

{int presolve} (default: {GLP_OFF})

MIP presolver option:

|glpk.GLP_ON | --- enable using the MIP presolver;

|glpk.GLP_OFF| --- disable using the MIP presolver.

{int binarize} (default: {GLP_OFF})

Binarization option (used only if the presolver is enabled):

|glpk.GLP_ON | --- replace general integer variables by binary ones;

|glpk.GLP_OFF| --- do not use binarization.

'''
           }

   _opt_help['exact'] = _opt_help['simplex']

   @_globalize
   def solver(me, solver=None, **kwds):
      '''
It helps to set solver options before calling solve(), e.g.
    >>> solver('interior', msg_lev=glpk.GLP_MSG_OFF)

sets 'interior' solver as the solver for linear programming,
along with corresponding control parameters supplied as keyword
arguments. Currently supported solver names are:

    'simplex', 'exact', 'interior', 'intopt'

For help on the control parameters of a particular solver, use
    >>> solver(help = 'interior')

To find out which solver will be used for linear programming:
    >>> solver(float)

To find out which solver will be used for integer programming:
    >>> solver(int)

To set options on one of the default solvers, use
    >>> solver(int, ...)
''' 
      if solver is None: #here comes help 
          if 'help' in kwds: #e.g. solver(help='simplex')
              print(me._opt_help.get(
                  kwds['help'], 'Invalid solver.'))
          else: return 'Invalid call. Use help(solver) for help.'

      if solver is float:
          solver = me.options.get('lp solver', 'simplex')
          if len(kwds) == 0: return solver
          if me.verb: print("default solver:", solver)
      elif solver is int:
          solver = me.options.get('mip solver', 'intopt')
          if len(kwds) == 0: return solver
          if me.verb: print("default solver:", solver)

      if solver not in me.opt_kinds:
          print('Bad solver. Supported solvers are:', 
                  ', '.join(me.opt_kinds))
          return

      if me.opt_kinds.index(solver) < me.num_lp_solvers:
          me.options['lp solver'] = solver
          if me.verb: print('LP solver is set to', solver)
      else: 
          me.options['mip solver'] = solver
          if me.verb: print('MIP solver is set to', solver)

      options = me.options[solver]
      if len(kwds)==0: return options
      for opt, val in kwds.items():
          if val is not None:
             options[opt] = val
          elif opt in options:
             del options[opt]
      return options

   def _solver_ctrl(me, solver):
       opts = me.options[solver]
       if not opts: return

       if solver == 'simplex':
           cp = glpk.glp_smcp()
           glpk.glp_init_smcp(cp)
       elif solver == 'exact':
           cp = glpk.glp_smcp()
           glpk.glp_init_iocp(cp)
       elif solver == 'interior':
           cp = glpk.glp_iptcp()
           glpk.glp_init_iptcp(cp)
       elif solver == 'intopt':
           cp = glpk.glp_iocp()
           glpk.glp_init_iocp(cp)
       else: return #

       for n in opts:
           p = getattr(cp, n, None)
           if p is None: 
               print("Ignored a bad option", n)
               continue

           pv = opts[n]
           if type(p) != type(pv):
               pv = type(p)(opts[p]) #convertion
           setattr(cp, n, pv)

       return cp

   #return values and meanings
   _ret_str = {
           'simplex':{

0 : '''The LP problem instance has been successfully solved. (This code
does {\it not} necessarily mean that the solver has found optimal
solution. It only means that the solution process was successful.) ''',

glpk.GLP_EBADB:'''Unable to start the search, because the initial
basis specified in the problem object is invalid---the number of basic
(auxiliary and structural) variables is not the same as the number of
rows in the problem object.''',

glpk.GLP_ESING:'''Unable to start the search, because the basis matrix
corresponding to the initial basis is singular within the working
precision.''',

glpk.GLP_ECOND:'''Unable to start the search, because the basis matrix
corresponding to the initial basis is ill-conditioned, i.e. its
condition number is too large.''',

glpk.GLP_EBOUND:'''Unable to start the search, because some
double-bounded (auxiliary or structural) variables have incorrect
bounds.''',

glpk.GLP_EFAIL:'''The search was prematurely terminated due to the
solver failure.''',

glpk.GLP_EOBJLL:'''The search was prematurely terminated, because the
objective function being maximized has reached its lower limit and
continues decreasing (the dual simplex only).''',

glpk.GLP_EOBJUL:'''The search was prematurely terminated, because the
objective function being minimized has reached its upper limit and
continues increasing (the dual simplex only).''',

glpk.GLP_EITLIM:'''The search was prematurely terminated, because the
simplex iteration limit has been exceeded.''',

glpk.GLP_ETMLIM:'''The search was prematurely terminated, because the
time limit has been exceeded.''',

glpk.GLP_ENOPFS:'''The LP problem instance has no primal feasible
solution (only if the LP presolver is used).''',

glpk.GLP_ENODFS:'''The LP problem instance has no dual feasible
solution (only if the LP presolver is used).''',
               },
           'exact':{
0 : '''The LP problem instance has been successfully solved. (This code
does { not} necessarily mean that the solver has found optimal
solution. It only means that the solution process was successful.)''',

glpk.GLP_EBADB:'''Unable to start the search, because the initial basis
specified in the problem object is invalid---the number of basic
(auxiliary and structural) variables is not the same as the number of
rows in the problem object.''',

glpk.GLP_ESING:'''Unable to start the search, because the basis matrix
corresponding to the initial basis is exactly singular.''',

glpk.GLP_EBOUND:'''Unable to start the search, because some
double-bounded (auxiliary or structural) variables have incorrect
bounds.''',

glpk.GLP_EFAIL:'''The problem instance has no rows/columns.''',

glpk.GLP_EITLIM:'''The search was prematurely terminated, because the
simplex iteration limit has been exceeded.''',

glpk.GLP_ETMLIM:'''The search was prematurely terminated, because the
time limit has been exceeded.''',
               },

           'interior':{

0 : '''The LP problem instance has been successfully solved. (This code
does {\it not} necessarily mean that the solver has found optimal
solution. It only means that the solution process was successful.)''',

glpk.GLP_EFAIL:'''The problem has no rows/columns.''',

glpk.GLP_ENOCVG:'''Very slow convergence or divergence.''',

glpk.GLP_EITLIM:'''Iteration limit exceeded.''',

glpk.GLP_EINSTAB:'''Numerical instability on solving Newtonian system.''',
               },
           'intopt':{
0 : '''The MIP problem instance has been successfully solved. (This code
does {\it not} necessarily mean that the solver has found optimal
solution. It only means that the solution process was successful.)''',

glpk.GLP_EBOUND:'''Unable to start the search, because some
double-bounded variables have incorrect bounds or some integer
variables have non-integer (fractional) bounds.''',

glpk.GLP_EROOT:'''Unable to start the search, because optimal basis
for initial LP relaxation is not provided. (This code may appear only
if the presolver is disabled.)''',

glpk.GLP_ENOPFS:'''Unable to start the search, because LP relaxation
of the MIP problem instance has no primal feasible solution. (This code
may appear only if the presolver is enabled.)''',

glpk.GLP_ENODFS:'''Unable to start the search, because LP relaxation
of the MIP problem instance has no dual feasible solution. In other
word, this code means that if the LP relaxation has at least one primal
feasible solution, its optimal solution is unbounded, so if the MIP
problem has at least one integer feasible solution, its (integer)
optimal solution is also unbounded. (This code may appear only if the
presolver is enabled.)''',

glpk.GLP_EFAIL:'''The search was prematurely terminated due to the
solver failure.''',

glpk.GLP_EMIPGAP:'''The search was prematurely terminated, because the
relative mip gap tolerance has been reached.''',

glpk.GLP_ETMLIM:'''The search was prematurely terminated, because the
time limit has been exceeded.''',

glpk.GLP_ESTOP:'''The search was prematurely terminated by application.
(This code may appear only if the advanced solver interface is used.)''',
               }
           }
   @_globalize
   def solve(me, kind = None):
       """you can change parameters, then the model will
rebuild itself before actually solve."""
       ## a point between consecutive comparisons
       me._last = None 

       me.update_lazy() #this takes care of rebuilding

       if kind is float or kind is None:
           meth = me.solver(float) #lp method
           cp = me._solver_ctrl(meth)
           method = getattr(me, meth)
           rv = method(cp)
           rv = me._ret_str[meth][rv]
           me._solved = meth
           if kind is float: return rv

       if kind is int or kind is None:
           if not me.nint(): return
           meth = me.solver(int) #mip method
           cp = me._solver_ctrl(meth)
           method = getattr(me, meth)
           ri = method(cp) 
           ri = me._ret_str[meth][ri]
           me._solved = 'intopt'
           return rv+'\n'+ri if kind is None else ri

       print('Error: kind is not one of float, int, None.')

   @_globalize
   def end(me, name=None): 
       me._last = None 
       if name is None: 
           # might not be a serious end
           me.update_lazy()
       elif name==me.name: 
           # an emphetic end
           me.lazy = None
       else:
           raise Exception('Bad argument!')

       if me is model._prob_:
           model._prob_ = None

       return me
       
   @_globalize
   def verbose(me, v): me.verb = v

   status_map = {
glpk.GLP_OPT : 'solution is optimal',
glpk.GLP_FEAS : 'solution is feasible',
glpk.GLP_INFEAS : 'solution is infeasible',
glpk.GLP_NOFEAS : 'problem has no feasible solution',
glpk.GLP_UNBND : 'problem has unbounded solution',
glpk.GLP_UNDEF : 'solution is undefined'
   }
   @_globalize
   def status(me, format=None):
       """The routine glp_get_status reports the generic status of the
current basic solution for the specified problem object as follows:

GLP_OPT | solution is optimal;
GLP_FEAS | solution is feasible;
GLP_INFEAS | solution is infeasible;
GLP_NOFEAS | problem has no feasible solution;
GLP_UNBND | problem has unbounded solution;
GLP_UNDEF | solution is undefined."""
       ret = (me.get_status() #simplex and exact
                    if me._solved in ('simplex', 'exact') else
              me.ipt_status() if me._solved == 'interior' else
              me.mip_status())
       return ret if format is int else me.status_map[ret] 

   @_globalize
   def vobj(me): 
       """value of the objective."""
       return (me.get_obj_val() #simplex and exact
                  if me._solved in ('simplex', 'exact') else
               me.ipt_obj_val() if me._solved == 'interior' else
               me.mip_obj_val())

   @property
   def name(me): return me.get_prob_name()
   @name.setter
   def name(me, name): me.set_prob_name(name)

   @_globalize #TODO: think about using readonly group
   def var(me, name, inds=None, kind=float, bounds=(0,None)):
      '''Create new variables by the given name(s).

Arguments:

  name(required): a str for the name(s) of the variable(s)

  inds(default to None): index set or an integer

  kind(default to float): what kind of variable to create

  bounds(default to 0,None): a pair of numbers for bounds

Detailed explanation:

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
'''
      if not isinstance(name, str):
         # backwards compatability.
         print("Deprecated call to var(.):"
          " name should be the first argument.")
         name, inds = inds, name
         if name is None: name = '_'

      if inds==None:
         names = name.split(',')
         idx = me.add_cols(len(names))
         if len(names) == 1:
             return _var(me, idx, name, kind, bounds) 
         return [_var(me, idx+i, name.strip(), kind, bounds) 
                   for i, name in enumerate(names)]
 
      #create many variables as a dict.
      if type(inds) is int: 
          inds = range(inds)
          vars = [None for i in inds]
      else:
          vars = {}
          for t in inds: vars[t] = None

      idx = me.add_cols(len(vars))
      name = name + "[%s]" if name else "X%d[%%s]"%idx
      for t in inds:
         vars[t] = _var(me, idx, 
            name%subscript(t), kind, bounds)
         idx += 1
      return vars

   @_globalize
   def st(me, cons, name=None, inds=None):
      """subject to: add one or many constraints.

    Arguments:

    cons(required): one or a list/tuple/sequence of constraints.

    name(default to None): a single name for the constraints.
        if the argument name is not provided, will leave name unchanged.

    inds(default to None): the index for the constraints, will be
        used as subscripts to name each individual constraints. 
        If the index set is not provided, index counts from 0.
 """
      me._last = None 

      if type(cons) is _var:
          if me.verb: print(cons.name, "bounds:", cons.bounds)
          return None #treat as bound
      if type(cons) is _cons: 
          if name: cons.name = name 
          if me.verb: print(str(cons))
          return cons

      idx, iit = 0, inds and iter(inds) 
      rets = {} if iit else []
      name = name and name + "[%s]"
      for c in cons:
          idx = next(iit) if iit else 1+idx
          one = me.st(c, name and name%subscript(idx))
          if iit: rets[idx] = one
          else: rets.append(one)
      return rets

   @_globalize
   def maximize(me, expr, name=None):
       return me.fobj(True, expr, name)
   max = maximize
   @_globalize
   def minimize(me, expr, name=None):
       return me.fobj(False, expr, name)
   min = minimize
   def fobj(me, max, expr, name):
      if type(expr) is _var:
         expr = +expr #convert to expression
      if type(expr) is not _parex:
         raise Exception("Bad expression.")
      obj = _obj(me, max, expr, name) 
      if me.verb: print(obj)
      return obj

   @_globalize
   def nvar(me):
       "Get number of variables."
       return me.get_num_cols()

   @_globalize
   def nint(me): 
      """Get number of integer variables."""
      return me.get_num_int()

   @_globalize
   def nbin(me): 
      """Get number of binary variables."""
      return me.get_num_bin()

   @property
   def kind (me): 
      return (bool if me.nbin() == me.nvar() else
                int if me.nint() else #mixed integer problem
                float) #assert nint >= nbin


   class _KKT(object): 
       def __init__(me, method ): 
           me.method = method

       def convert(me, p): 
           'convert row, col index to names'
           pass

       def __repr__(res): return """
Karush-Kuhn-Tucker optimality conditions:
=========================================
Solver used for this solution: %s

1) Error for Primal Equality Constraints:
----------------------------------------
Largest absolute error: %f (row id: %s)
Largest relative error: %f (row id: %s)

2) Error for Primal Inequality Constraints:
-------------------------------------------
Largest absolute error: %f (row id: %s)
Largest relative error: %f (row id: %s)
"""%( res.method,
      res.pe_aem, res.pe_aei, 
      res.pe_rem, res.pe_rei,
      res.pb_aem, res.pb_aei, 
      res.pb_rem, res.pb_rei,
) + ("""
1) Error for Dual Equality Constraints:
----------------------------------------
Largest absolute error: %f (var id: %s)
Largest relative error: %f (var id: %s)

2) Error for Dual Inequality Constraints:
-------------------------------------------
Largest absolute error: %f (var id: %s)
Largest relative error: %f (var id: %s)
"""%( 
      res.de_aem, res.de_aei, 
      res.de_rem, res.de_rei,
      res.db_aem, res.db_aei, 
      res.db_rem, res.db_rei,
    ) if res.dual else '')

   @_globalize
   def KKT(me):
      """Karush-Kuhn-Tucker optimality conditions for the latest solution.
for more information, try: >>> help(model.check_kkt)"""
      res = model._KKT(me._solved)
      isol = me.opt_kinds.index(me._solved)
      solt = glpk.GLP_SOL if isol <2 else\
            glpk.GLP_IPT if isol ==2 else glpk.GLP_MIP
      def ptr(t=float, n=1): 
        return glpk.intArray(n) if t is int else glpk.doubleArray(n)
      aem, aei, rem, rei = ptr(), ptr(int), ptr(), ptr(int) 
      def kkt_vals(prefix):
          cond = getattr(glpk, 'GLP_KKT_'+prefix.upper()) 
          me.check_kkt(solt, cond, aem, aei, rem, rei)
          for attr in ('aem', 'aei', 'rem', 'rei'):
              setattr(res, prefix+'_'+attr, vars()[attr][0])
      kkt_vals('pe')
      kkt_vals('pb')
      res.dual = isol <= 2 #me.opt_kinds.index('interior')
      if res.dual:
        kkt_vals('de')
        kkt_vals('db')
      return res

   def scale(me, flags=None): 
      """scale or unscale (without arguments) the problem. 
flags: options can be combined
with the bitwise OR operator and may be the following:
GLP_SF_GM | perform geometric mean scaling;
GLP_SF_EQ | perform equilibration scaling;
GLP_SF_2N | round scale factors to nearest power of two;
GLP_SF_SKIP | skip scaling, if the problem is well scaled.
GLP_SF_AUTO | chooses the scaling options automatically.
     """
      if type(flags) is int: 
         me.scale_prob(flags)
      else: me.unscale_prob()

   @_globalize
   def sensit(me):
       '''print the sensitivity report.'''
       from datetime import datetime
       print()
       print("PyMathProg 1.0 Sensitivity Report Created:", 
            datetime.now().strftime('%Y/%m/%d %a %H:%M%p'))
       me.coef_ranges()
       me.bound_ranges()

   @_globalize
   def sensitivity(me): 
       '''print the sensitivity report.'''
       me.sensit()
   
   @_globalize
   def coef_ranges(me, cols = None):
      """sensitivity report on objective coeficients.
         Args:
             cols(None, iterable or dict): a number of variables.
                  if it is None, report on all variables.
                  if an iterable, report on variables in the iterable.
                  if a dict, report on variables in the dict by 
                      ignorig the keys.
"""
      map = me._colmap.map
      if cols is None: 
          n = me.get_num_cols()
          cols = range(1, n+1)
      elif isinstance (cols, _var): 
          cols = [map(cols.up.id)]
      elif isinstance (cols, dict): 
          cols = [map(c.up.id) for k,c in cols.items()]
      elif isinstance (cols, list): 
          cols = [map(c.up.id) for c in cols]
      print('===='*20)
      fmt = "%-15s %12s %12s %12s %12s %12s"
      print(fmt%("Variable", "Activity", "Dual.Value", 
           "Obj.Coef", "Range.From", "Range.Till"))
      print('----'*20)
      fmt = "%s%-14s %12g %12g %12g %12g %12g"
      for vals in me._viter(cols): print(fmt%vals)
      print('===='*20)
      if me.verb: print(
'''Note: rows marked with a * list a basic variable.
''')

   @_globalize
   def bound_ranges(me, rows = None):
      """sensitivity report on the bounds of constraints.
         Args:
             rows(None, iterable or dict): a number of variables.
                  if it is None, report on all variables.
                  if an iterable, report on variables in the iterable.
                  if a dict, report on variables in the dict by 
                      ignorig the keys.
"""
      map = me._rowmap.map
      if rows is None: 
          m = me.get_num_rows() 
          rows = range(1, m+1)
      elif isinstance (rows, _cons): 
          rows = [map(rows.up.id)]
      elif isinstance (rows, dict): 
          rows = [map(c.up.id) for k,c in rows.items()]
      elif isinstance (rows, list): 
          rows = [map(c.up.id) for c in rows]
      print('===='*20)
      #(name, prim, dual, lb, ub, slack, coef1[0], coef2[0])
      fmt = "%-14s %10s %10s %10s %10s %10s %10s"
      print(fmt%("Constraint", "Activity", "Dual.Value", 
           "Lower.Bnd", "Upper.Bnd", "RangeLower", "RangeUpper"))
      print('----'*20)
      fmt = "%s%-13s %10g %10g %10g %10g %10g %10g"
      for vals in me._citer(rows): print(fmt%vals)
      print('===='*20)
      if me.verb: print(
'''Note: normally, RangeLower is the min for the binding bound, and RangeUpper
gives the max value. However, when neither bounds are binding, the row is 
marked with a *, and RangeLower is the max for Lower.Bnd(whose min is -inf), 
and RangeUpper is the min for Upper.Bnd(whose max value is inf). Then the 
columns of RangeLower, RangeUpper and Activity all have identical values.
''')

   def _viter(me, idx): #varialbes
      '''iterate over a set of raw index for variables.'''
      m = me.get_num_rows() 
      coef1 = glpk.doubleArray(1) #min
      var1 = glpk.intArray(1)
      val1 = glpk.doubleArray(1)
      coef2 = glpk.doubleArray(1) #max
      var2 = glpk.intArray(1)
      val2 = glpk.doubleArray(1)
      objdir = me.get_obj_dir()
      from sys import float_info
      fmax = float_info.max
      ninf, pinf = float('-inf'), float('inf')
      for k in idx:
        name = me._get_col_name(k)
        stat = me._get_col_stat(k)
        prim = me._get_col_prim(k)
        dual = me._get_col_dual(k)
        coef = me._get_obj_coef(k)
        if stat == glpk.GLP_BS:
            me.analyze_coef(m+k, coef1, var1, val1, 
                           coef2, var2, val2)
        elif stat == glpk.GLP_NF:
            coef1[0] = coef2[0] = coef
        elif stat == glpk.GLP_NS:
            coef1[0], coef2[0] = ninf, pinf
        elif stat == glpk.GLP_NL and objdir == glpk.GLP_MIN\
             or stat == glpk.GLP_NU and objdir == glpk.GLP_MAX:
            coef1[0], coef2[0] = coef - dual, pinf
        else:
            coef1[0], coef2[0] = ninf, coef - dual
        bs = '*' if stat == glpk.GLP_BS else ' '
        yield tuple(v if type(v) is not float or abs(v)>1e-9 else 0.0
            for v in (bs, name, prim, dual, coef, coef1[0], coef2[0]))

   def _citer(me, idx): #constraints
      '''iterate over a set of raw index for constraints.'''
      var1 = glpk.intArray(1)
      val1 = glpk.doubleArray(1)
      var2 = glpk.intArray(1)
      val2 = glpk.doubleArray(1)
      from sys import float_info
      fmax = float_info.max
      ninf, pinf = float('-inf'), float('inf')
      for k in idx:
        name = me._get_row_name(k)
        stat = me._get_row_stat(k)
        prim = me._get_row_prim(k)
        dual = me._get_row_dual(k)
        coef = 0.
        lb = me.get_row_lb(k)
        lb = lb if lb > -fmax else ninf 
        ub = me.get_row_ub(k)
        ub = ub if ub <  fmax else pinf 
        if stat == glpk.GLP_BS:
            # trivial case for row bounds 
            val1[0] = prim #upper bound for lower.bnd
            val2[0] = prim #lower bound for upper.bnd
            #val1[0] = ninf if ub is pinf else prim
            #val2[0] = prim if ub is pinf else pinf
        else:
            me.analyze_bound(k, val1, var1, val2, var2)
        bs = '*' if stat == glpk.GLP_BS else ' '
        yield tuple(v if type(v) is not float or abs(v)>1e-9 else 0.0
        for v in (bs, name, prim, dual, lb, ub, val1[0], val2[0]))


   @_globalize
   def save(me, **kwds):
      """Output data about the linear program into a file with a given
    format.  What data is written, and how it is written, depends
    on which of the format keywords are used.  Note that one may
    specify multiple format and filename pairs to write multiple
    types and formats of data in one call to this function.
    
    mps       -- For problem data in the fixed MPS format.
    clp       -- Problem data in the CPLEX LP format.
    glp       -- Problem data in the GNU LP format.
    sol*      -- Basic solution in printable format.
    sen*      -- Bounds sensitivity information.
    ipt*      -- Interior-point solution in printable format.
    mip*      -- MIP solution in printable format.
"""
      if 'mps' in kwds:
          filename = kwds['mps']
          me.write_mps(glpk.GLP_MPS_FILE, None, filename)
          if me.verb: print("Problem written to file '%s'"%filename)

      if 'glp' in kwds:
          filename = kwds['glp']
          me.write_prob(0, filename)
          if me.verb: print("Problem written to file '%s'"%filename)

      if 'clp' in kwds: #cplex lp
          filename = kwds['clp']
          me.write_lp(None, filename)
          if me.verb: print("Problem written to file '%s'"%filename)

      if 'sol' in kwds: #lp solution
          filename = kwds['sol']
          me.print_sol(filename)
          if me.verb: print("Solution written to file '%s'"%filename)

      if 'ipt' in kwds: #ipt solution
          filename = kwds['ipt']
          me.print_ipt(filename)
          if me.verb: print("Solution written to file '%s'"%filename)

      if 'mip' in kwds: #mip solution
          filename = kwds['mip']
          me.print_mip(filename)
          if me.verb: print("Solution written to file '%s'"%filename)

      if 'sen' in kwds: #lp sensivitity
          filename = kwds['sen']
          me.print_ranges(0, None, 0, filename)
          if me.verb: print("Sensitivity written to file '%s'"%filename)

   #the exec way to add related glpk routines:
   for adef in _LinkGLPK.defs(locals()): exec(adef)

####### some global wrapping functions #######
#Global interface:
#This allows one to create, manipulate, solve
#A model without explicitly deal with a model instance.
#Rather, the package manages a global model instance.

#model = custom_model

def begin(name):
    return model(name, as_global=True)

def beginModel(name): 
    print("beginModel(.) is deprecated. Use model(.) instead.")
    return model(name, as_global=True)

def endModel(name=None):
    print("endModel(.) is deprecated. Use end(.) instead.")
    p = end(name)

### exposed methods on the current model ###
### these functions are generated dynamically

for code in _global_defs(): exec(code)
del code, sys

#print("before importing self") #you'll see it twice!
#import pymprog as _self_ #importing itself!
#print("after importing self") #you'll see it twice!

#_self_ = sys.modules[__name__]

##def make_gfun(name, f):
##   def wrapper(*args, **kwds):
##        return f(_prob_, *args, **kwds)
##   wrapper.__doc__ = (
##   "Calls the method '%s' on the current model.\n"%name +
##   "Use help(model.%s) for details of that method."%name)
##   wrapper.__name__ = name
##
##   if name in globals():
##      print("Warning: overriding global attr", name)
##      print(getattr(_self_, name))
##      print(wrapper)
##   globals()[name] = wrapper

