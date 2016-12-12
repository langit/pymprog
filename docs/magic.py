"""In recreational mathematics, a magic square of order n is an
   arrangement of n^2 numbers, usually distinct integers, in a square,
   such that n numbers in all rows, all columns, and both diagonals sum
   to the same constant. A normal magic square contains the integers
   from 1 to n^2.

   (From Wikipedia, the free encyclopedia.)

When n=5, we have:

the magic sum must be:  65
solver status: opt
10  2  4 24 25
 9 11 20  6 19
22 14 16  8  5
23 17  7 15  3
 1 21 18 12 13"""

# square order 
n = 4
# set of numbers
N = range(1,n*n+1)
#the magic sum:
s = sum(t for t in N)//n
print("the magic sum must be: %r "% s)

from pymprog import  model, iprod
S = iprod(range(1,n+1), range(1,n+1))
T = iprod(range(1,n+1), range(1,n+1), N)
p = model('magic')
x = p.var('x', T, bool)
#x[i,j,k] = 1 means that cell (i,j) contains integer k

#each cell must be assigned exactly one integer
for i,j in S: sum(x[i,j,k] for k in N)==1 

#each integer must be assigned exactly to one cell
for k in N: sum(x[i,j,k] for i,j in S)==1 

#the sum in each row must be the magic sum 
for i in range(1, n+1):
  sum(k*x[i,j,k] for j in range(1,n+1) for k in N)==s

#the sum in each column must be the magic sum 
for j in range(1, n+1):
  sum(k*x[i,j,k] for i in range(1,n+1) for k in N)==s

#the sum in the diagonal must be the magic sum
sum(k*x[i,i,k] for i in range(1,n+1) for k in N)==s

#the sum in the co-diagonal must be the magic sum
sum(k*x[i,n+1-i,k] for i in range(1,n+1) for k in N)==s

p.solve()
print("solver status: %s"% p.status())
for i in range(1,n+1):
   print(' '.join("%2g"%sum(x[i,j,k].primal*k for k in N) 
             for j in range(1,n+1)))
p.end()
