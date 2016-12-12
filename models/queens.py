from __future__ import print_function
import pymprog

# The Queens Problem is to place as many queens as possible on the nxn
#   chess board in a way that they do not fight
#   each other. This problem is probably as old as the chess game itself,
#   and thus its origin is not known, but it is known that Gauss studied
#   this problem.

n = 16 #size of chess board
p = pymprog.model('queens')
iboard = pymprog.iprod(range(n), range(n)) #create indices
x = p.var('X', iboard, bool) #create variables
#row wise:
p.st([sum(x[i,j] for j in range(n)) <= 1 for i in range(n)])
#column wise:
p.st([sum(x[i,j] for i in range(n)) <= 1 for j in range(n)])
#diagion '/' wise
p.st([sum(x[i,j] for i,j in iboard if i-j == k) <= 1 
                    for k in range(2-n, n-1)])
#diagion '\' wise
p.st([sum(x[i,j] for i,j in iboard if i+j == k) <= 1 
                    for k in range(1, n+n-2)])
p.maximize(sum(x[t] for t in iboard), 'queens')

p.solve()
for i in range(n):
   for j in range(n):
       if x[i,j].primal > 0: print('Q', end=' ')
       else: print('.', end=' ')
   print()
p.end()
