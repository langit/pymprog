## TODD, a class of hard instances of zero-one knapsack problems

"""Chvatal describes a class of instances of zero-one knapsack problems
   due to Todd. He shows that a wide class of algorithms - including all
   based on branch and bound or dynamic programming - find it difficult
   to solve problems in the Todd class. More exactly, the time required
   by these algorithms to solve instances of problems that belong to the
   Todd class grows as an exponential function of the problem size.

   Reference:
   Chvatal V. (1980), Hard knapsack problems, Op. Res. 28, 1402-1411."""

## change this parameter to choose a particular instance
n = 19 # I found this is a particularly hard case.

from math import *
log2_n = log(n) / log(2)

k = floor(log2_n)

a = [2 ** (k + n + 1) + 2 ** (k + n + 1 - j) + 1
    for j in range(1,n+1)]

b = 0.5 * floor(sum(a));

import pymprog
todd = pymprog.model("todd")

x = todd.var('x', range(n), bool)

todd.maximize(sum(a[j]*x[j] for j in x))
todd.st(sum(a[j]*x[j] for j in x)<=b)

todd.solve()
print("solver status: ", todd.status())
print("obj: ", int(todd.vobj()), "b:", int(b))
V = 0
print("obj,      value,       accum")
for t in x:
   if x[t].primal > 0:
      V += int(a[t])
      print("%3i, %12i, %12i"%(t, int(a[t]), V))
todd.end()
