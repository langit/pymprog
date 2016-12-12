from pymprog import *

def testBinder():
   binder = iprod(('a','b'),range(3))
   print(len(binder))
   vd = {}
   for t in binder: 
     vd[t] = t
   for t in binder: print(vd[t])


testBinder()

def testProblem():
  p = model('test')
  x = p.var('x', 3)
  for i in range(3): print(x[i] <= 5)
  inds = iprod(range(3), range(2))
  y = p.var('y', inds)
  for t in inds: print(1 <= y[t] <= 3)
  print()
  #ex = (-x[0] + 2* x[1] - 5*y[2,1])*3 + 23
  #print(ex)
  #print(10 <= ex <= 30)
  #p.st(20 <= ex <= 60)
  for i in range(3): print(x[i].name, x[i].bounds)
  print("End")
  #del ex
  #del p.p
  #del p

testProblem()

import gc
gc.collect()
print(gc.garbage)
