n = 80
N = range(n)
M = [(i,j) for i in N for j in N if i<j]

from random import Random

rand = Random()

D = [rand.randint(1,10) for i in N]
R = [rand.randint(1,10) for i in N]
tt = sum(D)
L = [rand.randint(1,tt) for i in N]
U = [L[i]+D[i]+rand.randint(0,10) for i in N]

M = [(i,j) for i,j in M 
      if L[i]<U[j] and L[j]<U[i]] 

from pymprog import *

beginModel("job-scheduling")
x = var("x", N ) #start time
u = var("u", N, bool) #if accept
w = var("w", M, bool)

#one way to enforce no overlapping:
#
# x[i] >= T[j] or x[j] >= T[i]
#

st(x[i] + (U[j]-L[i])*(w[i,j]+2-u[i]-u[j])
    >= x[j]+D[j] for i,j in M)
st(x[j] + (U[i]-L[j])*(3-w[i,j]-u[i]-u[j]) 
    >= x[i]+D[i] for i,j in M)

maximize( sum(u[i]*R[i] for i in N), 'revenue')

#set bounds on x
for i in N:
   L[i] <= x[i] <= U[i] - D[i] 

solve()

print("status: %s"% status())
print("revenue:", vobj(), '//', sum(R))
print("schedule:")
for i in N:
   start = x[i].primal
   used = u[i].primal
   print("job %i:"%i, start, start+D[i],
   "Accept" if used else "Reject", R[i]/float(D[i]))
