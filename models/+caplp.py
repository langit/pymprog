import csv
dists = csv.reader(open('capdist.csv'), 'excel')
dm = [[int(k) for k in t[2:33]] 
     for t in dists if t[1]]

n = len(dm) #how many cities
V = range(n)
E = [(i,j) for i in V for j in V if i!=j]

print "there are %d cities"%n

from pymprog import *
beginModel('ChinaCapitalCitiesTSP')
x = var('x', E, bool)
minimize( sum(dm[i][j]*x[i,j] for i,j in E), 'TravelDist' )
st([sum( x[k,j] for j in V if j!=k ) == 1 for k in V], 'leave')
st([sum( x[i,k] for i in V if i!=k ) == 1 for k in V], 'enter')

y = var('y', E, bool) #the ordering variables
st([y[i,j] + y[j,i] == 1 for i in V for j in V if i>j], 
   'complete')
st([x[i,j] + y[j,i] <= y[j,k] + y[k,i] 
   for i in V for j in V for k in V if i!=j!=k!=i])

st([y[0,j] == 1 for j in V if j>0], 'insym')

from datetime import datetime
print datetime.now()
solve(float)
print datetime.now()
print "simplex done:", status()
print datetime.now()
solve(float)
print datetime.now()
print "simplex done:", status()

solvopt(integer='advanced')
solveMIP() #solve the IP problem

print "Optimal tour length:", vobj()
tour = [t for t in E if x[t].primal>.5]
cat = 0
print("This is the optimal tour:")
for k in V: 
   print cat+1, '->',
   for i,j in tour: 
      if i==cat: cat=j; break
print cat+1
