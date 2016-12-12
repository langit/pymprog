from __future__ import print_function

#The subset sum problem: given a multiset of integers, find
#subset of it such that the sum of the subset equals a given 
#value.
from random import *
n = 40
m = 90000000
a=[randint(1, m) for i in range(n)]
for i in range(1, n+1): print(i, a[i-1], ",", end=' ')
print()
print( a)
s = sum(a)/2
print("(n,m):", (n,m), "sum:", sum(a), " s:", s)
from pymprog import *
beginModel("subsetsum")
x = var('x', range(n), bool)
st( sum(a[i]*x[i] for i in range(n)) == s )

from datetime import datetime
print(datetime.now())
solve()
print(datetime.now())
print("solver status: %r" % status())
for i in range(n):
   if x[i].primal > 0.5: print(a[i], end=' ')
print()
end()
