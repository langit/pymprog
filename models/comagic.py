# MAGIC, Magic Square


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
rt= 2 #square root of n
n = rt*rt 
# set of numbers
N = range(1,n*n+1)
#the magic sum:
s = sum(N)//n
print("the magic sum must be: %r" % s)

import pymprog
p = pymprog.model('magic')
S = pymprog.iprod(range(1,n+1), range(1,n+1))
rtS=pymprog.iprod(range(1,rt+1), range(1,rt+1))
rtB=pymprog.iprod(range(0,n,rt), range(0,n,rt))
T = pymprog.iprod(range(1,n+1), range(1,n+1), N)
x = p.var('x', T, bool)
#x[i,j,k] = 1 means that cell (i,j) contains integer k

#each cell must be assigned exactly one integer
p.st([sum(x[i,j,k] for k in N)==1 for i,j in S])

#each integer must be assigned exactly to one cell
p.st([sum(x[i,j,k] for i,j in S)==1 for k in N])

#the sum in each row must be the magic sum 
p.st([sum(k*x[i,j,k] for j in range(1,n+1) for k in N)==s
      for i in range(1, n+1)], 'row')

#the sum in each column must be the magic sum 
p.st([sum(k*x[i,j,k] for i in range(1,n+1) for k in N)==s
      for j in range(1, n+1)], 'col')

#the sum in the diagonal must be the magic sum
p.st([sum(k*x[i,(i+j-2)%n+1,k] for i in range(1,n+1) for k in N)==s
      for j in range(1,n+1)], 'dia')

#the sum in the co-diagonal must be the magic sum
p.st([sum(k*x[i,(n-1-i+j)%n+1,k] for i in range(1,n+1) for k in N)==s
     for j in range(1,n+1)], 'cod')

#the sum in each sub-square must be the magic sum
p.st([sum(k*x[i+bi, j+bj, k] for i,j in rtS for k in N)==s
      for bi, bj in rtB], 'sub')

#in each sub-square, only one number btw [i*n+1,(i+1)*n]
#note: this additional constriant is to reduce complexity
p.st([sum(x[i+bi, j+bj, k] for i,j in rtS 
	for k in range(h*n+1, (h+1)*n+1))==1
	for h in range(n) for bi, bj in rtB], 'red') 

p.solve()
print("solver status: %s"% p.status())
for i in range(1,n+1):
   print(' '.join("%2g"%sum(x[i,j,k].primal*k for k in N) 
             for j in range(1,n+1)))

p.end()
