from pymprog import model, iprod, glpk

# The Queens Problem is to place as many queens as possible on the nxn
#   chess board in a way that they do not fight
#   each other. This problem is probably as old as the chess game itself,
#   and thus its origin is not known, but it is known that Gauss studied
#   this problem.

def queens(n): # n: size of the chess board
   p = model('queens')
   iboard = iprod(range(n), range(n)) #create indices
   x = p.var('x', iboard, bool) #create variables
   sum(x[t] for t in iboard) == n
   for i in range(n): # row-wise
       sum(x[i,j] for j in range(n)) <= 1
   for j in range(n): # column-wise
       sum(x[i,j] for i in range(n)) <= 1
   for k in range(2-n, n-1): # diagonal '\' wise
       sum(x[i,j] for i,j in iboard if i-j == k) <= 1 
   for k in range(1, n+n-2): # anti-diagonal '/' wise
       sum(x[i,j] for i,j in iboard if i+j == k) <= 1 
   return p,x

import random
n = random.randint(6, 11)
print("Board size: %i X %i"%(n,n))
def randpair():
    m = random.randint(0, n*n-1)
    return m%n, m//n
def randpos(k):
    while True:
       pos = [randpair() for i in range(k)]
       if len(set(i for i,j in pos))<k: continue
       if len(set(j for i,j in pos))<k: continue
       if len(set(i+j for i,j in pos))<k: continue
       if len(set(i-j for i,j in pos))<k: continue
       return pos

p, x = queens(n)

def try_out(pos):
   for r,c in pos:
     x[r,c] == 1
   p.solve()
   for r,c in pos:
     x[r,c].reset(0,1)
   return p.status(int) != glpk.GLP_OPT

p.solver(float, msg_lev=glpk.GLP_MSG_OFF)
p.solver(int, msg_lev=glpk.GLP_MSG_OFF)

bads = 0
k = 2
print("randomly put %i queens."%k)
for ii in range(100):
    pos = randpos(k)
    #print(pos)
    bads += try_out(pos)
print('found %i bad positions out of 100'%bads)
