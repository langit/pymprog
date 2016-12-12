'''minimal spanning tree.'''
Vname = 'ABCDEFG'
V = range(7)
Ename = 'AB,AC,AD,BC,BE,CE,CF,CD,DF,EF,EG,FG'.split(',')
W = (2,5,4,2,7,4,3,1,4,1,5,7)

from pymprog import *

E = [(Vname.index(e[0]),Vname.index(e[1])) for e in Ename]
A = E + [(j,i) for i,j in E]
We = dict(zip(E,W))
VA = iprod(V,A)

beginModel('MST')
x = var('x', E)
y = var('y', VA)
minimize( sum(We[e]*x[e] for e in E), 'TotalWeight' )
st([ y[v,(i,j)] <= x[min(i,j), max(i,j)] for v,(i,j) in VA ], 'edge')
st( sum(y[k,(s,j)] for i,j in A if i==s) 
	- sum(y[k,(i,s)] for i,j in A if j==s) == 
	(1 if s==0 else -1 if s==k else 0) 
	for s in V for k in V if k>0 )

solve(float)
print("simplex done:", status())
print(sum(We[e]*x[e].primal for e in E))
for e in E: print(e, x[e].primal)
