n = 40
N = range(n)
M = [(i,j) for i in N for j in N if i<j]

from random import Random

rand = Random()

D = [rand.randint(1,10) for i in N]
R = [rand.randint(1,10) for i in N]
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


from pymprog import *

beginModel("job-scheduling")
x = var("x", N ) #start time
#MD[i,j] = (D[i]+D[j])/2.0
#T[i] = x[i] + D[i]
#y[i,j]<= |T[i]-x[j]-MD[i,j]|
#y[i,j] < MD[i,j] <==> overlap betw jobs i,j
y = var("y", M ) 
#w[i,j]: the 'OR' for |T[i]-x[j]-MD[i,j]|
w = var("w", M, bool)
# z[i,j] >= MD[i,j] - y[i,j]
z = var("z", M)
#u[i] = 1 iff job i is scheduled.
u = var("u", N, bool)

maximize(sum(R[i]*u[i] for i in N), 'revenue')

st( 0 == sum(z[i,j] for i,j in M), "single" )
#w[i,j]=0  ==> 
#x[j] + D[j]/2 >= x[i]+D[i]/2 + y[i,j]
#That is: i preceed j when w[i,j]=0.
st([(D[i]+D[j])/2.0 - (x[i]+D[i]- x[j]) + 
   (U[i]-L[j]) * w[i,j] >= y[i,j]
   for i,j in M], 'small') #T[i]-x[j]<MD[i,j]
st([(x[i]+D[i]- x[j]) - (D[i]+D[j])/2.0 +
   (U[j]-L[i])*(1-w[i,j]) >= y[i,j]
   for i,j in M], 'large') #T[i]-x[j]>MD[i,j]
st([(D[i]+D[j])/2.0 - y[i,j] <= z[i,j] + 
       (2-u[i]-u[j])*(D[i]+D[j])/2.0
   for i,j in M], 'overlap') 

st(w[i,j] == (0 if (i,j) in P else 1)
  for (i,j) in M if ((i,j) in P or (j,i) in P))


#set bounds on x
for i in N:
   L[i] <= x[i] <= U[i] - D[i] 

solver(int, 
    #this branching option often helps 
    br_tech=glpk.GLP_BR_PCH, 
)
solve()

print "status:", status()
print "revenue:", vobj(), '//', sum(R)
print "schedule:"
for i in N:
   start = x[i].primal
   used = u[i].primal
   print "job %i:"%i, start, start+D[i],
   print "Accept" if used else "Reject",
   print R[i]/float(D[i])
