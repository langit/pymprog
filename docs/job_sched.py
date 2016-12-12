n = 3
N = range(n)
M = [(i,j) for i in N for j in N if i<j]

D = (3,4,2) #duration of each job
L = (0,2,0) #earliest start
U = (9,7,8) #latest finish

from pymprog import *

begin("job-scheduling")
x = var('x',  N) #start time
#MD[i,j] = (D[i]+D[j])/2.0
#T[i] = x[i] + D[i]
#y[i,j]<= |T[i]-x[j]-MD[i,j]|
#y[i,j] < MD[i,j] <==> overlap betw jobs i,j
y = var('y',  M ) 
#w[i,j]: the 'OR' for |T[i]-x[j]-MD[i,j]|
w = var('w', M, kind=bool)
# z[i,j] >= MD[i,j] - y[i,j]
z = var('z',  M )

minimize( sum(z[i,j] for i,j in M) )

for i,j in M:
   ((D[i]+D[j])/2.0 - (x[i]+D[i] - x[j]) + 
       (U[i]-L[j]) * w[i,j] >= y[i,j])

   ((x[i]+D[i] - x[j]) - (D[i]+D[j])/2.0 +
       (U[j]-L[i])*(1-w[i,j]) >= y[i,j])

   (D[i]+D[j])/2.0 - y[i,j] <= z[i,j] 

#set bounds on x
for i in N:
   L[i] <= x[i] <= U[i] - D[i] 

#another way to enforce no overlapping:
#
# x[i] >= T[j] or x[j] >= T[i]
#
# Which can be formulated as:
#
# x[i] + (U[j]-L[i])*w[i,j]>= x[j]+D[j]
# x[j] + (U[i]-L[j])*(1-w[i,j]) >= x[i]+D[i]

solve()

print("status: %r"% status())
print( "overlap: %r"% vobj())
print( "schedule:")

for i in N:
   start = x[i].primal
   print("job %i: %r, %r"%(i, start, start+D[i]))

