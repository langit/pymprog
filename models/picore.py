"""
Put numbers 1..n, in a nXn square, with 
each number repeated exactly n times,
such that each row, each column, and
each wrapped diagonal have the same sum.
Also, n=rt*rt, so that the nXn square 
can be divided into exactly n rtXrt 
subsquares, each contains n numbers.
Those subsquares also have the same sum.
"""

# square order 
rt= 2 #square root of n
n = rt*rt 
# set of numbers
N = range(1,n+1)
# the magic sum
ms = sum(N)
from pymprog import *
begin('magic')
S = iprod(range(1,n+1), range(1,n+1))
rtS=iprod(range(1,rt+1), range(1,rt+1))
rtB=iprod(range(0,n,rt), range(0,n,rt))
T = iprod(range(1,n+1), range(1,n+1), N)
x = var('x', T, bool)
#x[i,j,k] = 1 means that cell (i,j) contains integer k

#each cell must be assigned exactly one integer
st([sum(x[i,j,k] for k in N)==1 for i,j in S])

#each integer must be assigned exactly to n cells
st([sum(x[i,j,k] for i,j in S)==n for k in N])

#the sum in each row must be the magic sum 
st([sum(k*x[i,j,k] for j in N for k in N)==ms
      for i in N], 'row')

#the sum in each column must be the magic sum 
st([sum(k*x[i,j,k] for i in N for k in N)==ms
      for j in N], 'col')

#the sum in the diagonal must be the magic sum
st([sum(k*x[i,(i+j-2)%n+1,k] for i in N for k in N)==ms
      for j in N], 'dia')

#the sum in the co-diagonal must be the magic sum
st([sum(k*x[i,(n-1-i+j)%n+1,k] for i in N for k in N)==ms
      for j in N], 'cod')

#the sum in each sub-square must be the magic sum
st([sum(k*x[i+bi, j+bj, k] for i,j in rtS for k in N)==ms
      for bi, bj in rtB], 'sub')

#the sum of the elements occupying the same location
#in the subsquares must also be the same. picomagic! 
st([sum(k*x[i+bi, j+bj, k] for i,j in rtB for k in N)==ms
      for bi, bj in rtS], 'sub')

solve()

print("solver status: %s"% status())
for i in range(1,n+1):
   print(' '.join("%2g"%sum(x[i,j,k].primal*k for k in N) 
             for j in range(1,n+1)))

end()
