n = 25
N = range(n)
M = [(i,j) for i in N for j in N if i<j]

from random import Random

rand = Random()

D = [rand.randint(1,10) for i in N]
tt = sum(D)
L = [rand.randint(1,tt) for i in N]
U = [L[i]+D[i]+rand.randint(10,40) for i in N]

M = [(i,j) for i,j in M 
      if L[i]<U[j] and L[j]<U[i]] 

#i must preceed j and they could bump into each other
P = [(i,j) for i in N for j in N if i!=j
   and L[i]<U[j] and L[j]<U[i]
   #lastest start < earliest finish
   and U[i]-D[i]<L[j]+D[j]] 

print( "Duration:"); print( D)
print("Earliest:"); print( L )
print("Latest:"); print( U)
print("Preceeds:"); print( P)

from pymprog import *

beginModel("job-scheduling")
x = var("x", N ) #start time
w = var("w", M, kind=bool)

#one way to enforce no overlapping:
#
# x[i] >= T[j] or x[j] >= T[i]
#
# Which can be formulated as:
#
st(x[i] + (U[j]-L[i])*w[i,j]>= x[j]+D[j]
    for i,j in M)
st(x[j] + (U[i]-L[j])*(1-w[i,j]) >= x[i]+D[i]
    for i,j in M)
st(w[i,j] == (1 if (i,j) in P else 0)
  for (i,j) in M if ((i,j) in P or (j,i) in P))

#set bounds on x
for i in N:
   L[i] <= x[i] <= U[i] - D[i] 

solve()

print("status:", status())
print("schedule:")
for i in N:
   start = x[i].primal
   endat = evaluate(x[i]+D[i])
   print("job %i: %r, %r"%(i, start, endat))
end()
