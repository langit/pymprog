import csv
#dm = (
#( 0,86,49,57,31,69,50),
#(86, 0,68,79,93,24, 5),
#(49,68, 0,16, 7,72,67),
#(57,79,16, 0,90,69, 1),
#(31,93, 7,90, 0,86,59),
#(69,24,72,69,86, 0,81),
#(50, 5,67, 1,59,81, 0))

dists = csv.reader(open('capdist.csv'), 'excel')
dm = [[int(k) for k in t[2:33]] 
     for t in dists if t[1]]

n = len(dm) #how many cities

max_dist = max(max(t) for t in dm) + 1

dm = [[max_dist-x for x in row]
      for row in dm]

n = len(dm) #how many cities
V = range(n)
E = [(i,j) for i in V for j in V if i!=j]

print "there are %d cities"%n

from pymprog import *
beginModel('ChinaCapitalCitiesTSP')
x = var('x', E, bool)
v = var('v', E, bool)

maximize( sum(dm[i][j]*x[i,j] for i,j in E), 'AntiDist' )
st([sum( x[k,j] for j in V if j!=k ) == 1 for k in V], 'leave')
st([sum( x[i,k] for i in V if i!=k ) == 1 for k in V], 'enter')
st(v[i,j] + v[j,i] == 1 for i,j in E if i<j)
st(v[i,j] + x[j,i] <= v[i,k] + v[k,j] for i,j in E 
		for k in V if i!=k!=j)

for j in range(1,n): v[0,j] == 1

solve(float)
print "simplex done:", status()
solvopt(integer='advanced')
solveMIP() #solve the IP problem

print "Optimal tour length:", max_dist*n - vobj()
tour = [t for t in E if x[t].primal>.5]
cat = 0
print("This is the optimal tour:")
for k in V: 
   print cat+1, '->',
   for i,j in tour: 
      if i==cat: cat=j; break
print cat+1
