import pymprog 

# The Queens Problem is to place as many queens as possible on the nxn
#   chess board in a way that they do not fight
#   each other. This problem is probably as old as the chess game itself,
#   and thus its origin is not known, but it is known that Gauss studied
#   this problem.

def queens(n): # n: size of the chess board
   p = pymprog.model('queens')
   iboard = pymprog.iprod(range(n), range(n)) #create indices
   x = p.var('X', iboard, bool) #create variables
   #row wise:
   p.st([sum(x[i,j] for j in range(n)) <= 1 for i in range(n)])
   #column wise:
   p.st([sum(x[i,j] for i in range(n)) <= 1 for j in range(n)])
   #diagion '\' wise
   p.st([sum(x[i,j] for i,j in iboard if i-j == k) <= 1 
                    for k in range(2-n, n-1)])
   #diagion '/' wise
   p.st([sum(x[i,j] for i,j in iboard if i+j == k) <= 1 
                    for k in range(1, n+n-2)])
   p.max(sum(x[t] for t in iboard), 'queens')
   return p,x

n = raw_input("board size = ")
n = int(n)
p,x = queens(n)
ys = raw_input("Would you like to place a queen? [y]/n")
while ys!='n':
   r = raw_input("row [0, %i): "%n)
   c = raw_input("col [0, %i): "%n)
   p.st(x[int(r), int(c)] == 1)
   ys = raw_input("Would you like to place another queen? [y]/n")
 
p.solve()
#print "solver status: ", p.p.status
for i in range(n):
   for j in range(n):
       if x[i,j].primal > 0.5: print 'Q',
       else: print '.',
   print
