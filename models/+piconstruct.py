mat=(
(2 , 2 , 7 , 2 , 7 , 9 , 8 , 3 , 5),
  (9 , 8 , 3 , 8 , 2 , 1 , 2 , 9 , 3),
   (1 , 8 , 5 , 7 , 3 , 6 , 8 , 6 , 1),
    (9 , 8 , 1 , 3 , 4 , 3 , 7 , 6 , 4),
     (1 , 5 , 5 , 8 , 4 , 9 , 5 , 5 , 3),
      (1 , 9 , 6 , 4 , 6 , 4 , 3 , 3 , 9),
       (8 , 2 , 4 , 1 , 9 , 5 , 5 , 4 , 7),
        (7 , 1 , 9 , 4 , 4 , 6 , 1 , 7 , 6),
	 (7 , 2 , 5 , 8 , 6 , 2 , 6 , 2 , 7))


# square order 
rt= 3 #square root of n
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

grp = [set() for i in range(1,10)]
for i in range(9):
	for j in range(9):
		grp[mat[i][j]-1].add((i+1,j+1))

#each integer must be assigned to a group once;
#note that each integer is assigned n times.
st([sum(x[i,j,k] for i,j in grp[p-1])>=1 
	for p in N for k in N])

#each cell must be assigned exactly one integer
st([sum(x[i,j,k] for k in N)<=1 for i,j in S])

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
