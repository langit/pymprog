dm = ( # distance matrix
( 0,86,49,57,31,69,50),
(86, 0,68,79,93,24, 5),
(49,68, 0,16, 7,72,67),
(57,79,16, 0,90,69, 1),
(31,93, 7,90, 0,86,59),
(69,24,72,69,86, 0,81),
(50, 5,67, 1,59,81, 0))

n = len(dm) #how many cities
V = range(n) # set of cities
E = [(i,j) for i in V for j in V if i!=j]

print("there are %d cities"%n)

from pymprog import *
begin('subtour elimination')
x = var('x', E, bool)
minimize(sum(dm[i][j]*x[i,j] for i,j in E), 'dist')
for k in V:
    sum( x[k,j] for j in V if j!=k ) == 1
    sum( x[i,k] for i in V if i!=k ) == 1

solver(float, msg_lev=glpk.GLP_MSG_OFF)
solver(int, msg_lev=glpk.GLP_MSG_OFF)

solve() #solve the IP problem

def subtour(x):
   "find a subtour in current solution"
   succ = 0
   subt = [succ] #start from node 0
   while True:
      succ=sum(x[succ,j].primal*j 
               for j in V if j!=succ)
      if succ == 0: break #tour found
      subt.append(int(succ+0.5))
   return subt

while True:
   subt = subtour(x)
   if len(subt) == n:
      print("Optimal tour length: %g"%vobj())
      print("Optimal tour:"); print(subt)
      break
   print("New subtour: %r"% subt)
   if len(subt) == 1: break #something wrong
   #now add a subtour elimination constraint:
   nots = [j for j in V if j not in subt]
   sum(x[i,j] for i in subt for j in nots) >= 1
   solve() #solve the IP problem again
end()
