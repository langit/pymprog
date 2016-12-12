# Assignment Problem
# Written in pymprog by Yingjie Lan <ylan@umd.edu>

# The assignment problem is one of the fundamental combinatorial
#   optimization problems.

#   In its most general form, the problem is as follows:

#   There are a number of agents and a number of tasks. Any agent can be
#   assigned to perform any task, incurring some cost that may vary
#   depending on the agent-task assignment. It is required to perform all
#   tasks by assigning exactly one agent to each task in such a way that
#   the total cost of the assignment is minimized.
#   (From Wikipedia, the free encyclopedia.)

#problem data
m = 8 # agents
M = range(m) #set of agents
n = 8 # tasks
N = range(n) #set of tasks
c = [ #cost
(13,21,20,12,8,26,22,11),
(12,36,25,41,40,11,4,8),
(35,32,13,36,26,21,13,37),
(34,54,7,8,12,22,11,40),
(21,6,45,18,24,34,12,48),
(42,19,39,15,14,16,28,46),
(16,34,38,3,34,40,22,24),
(26,20,5,17,45,31,37,43)]

from pymprog import *

beginModel("assign")
#verbose(True) #Turn on this for model output
A = iprod(M, N) #combine index
#declare variables
x = var('x', A) #assignment decision vars
#declare parameters: 
#for automatic model update if parameters change
tc = par('cost', c) 
minimize(sum(tc[i][j]*x[i,j] for i,j in A), 'totalcost')
st(#subject to: each agent works on at most one task
[sum(x[k,j] for j in N)<=1 for k in M], #one for each agent
'agent') #a name for this group of constraints, optional
st(#subject to: each task must be assigned to somebody
[sum(x[i,k] for i in M)==1 for k in N], 'task')

solve()
print("Total Cost = %g"%vobj())
assign = [(i,j) for i in M for j in N 
                if x[i,j].primal>0.5]
for i,j in assign:
   print("Agent %d gets Task %d with Cost %g"%(i, j, tc[i][j].value))

i,j = assign[0]
tc[i][j].value += 10
print("set cost c%s to higher value %s"%(str([i,j]),str(tc[i][j].value)))

solve() #this takes care of model update
print("Total Cost = %g"%vobj())
assign = [(i,j) for i in M for j in N 
                if x[i,j].primal>0.5]
for i,j in assign:
   print("Agent %d gets Task %d with Cost %g"%(i, j, tc[i][j].value))

end()
