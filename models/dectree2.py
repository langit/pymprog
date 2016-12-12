#data section:
S = 30
D = 100

decisions=['a','c','d','e']
events = ['b','f','g','h']
tree = {
'a':('b','e'),
'b':(('c',0.7),('d',0.3)),
'c':('f',90-S),
'd':('g',90-S),
'e':('h',90),
'f':((800-D-S,.143),(-D-S,.857)),
'g':((800-D-S,.5),(-D-S,.5)),
'h':((800-D,.25),(-D,.75))}
tree_root='a'

from pymprog import *

beginModel("dectree")
verbose(True)

#####
# approach one
#####
#suppose at any decision node, you can 
#randomize among the alternatives,
#so for each decision node, attach
#a probability to each of its choises (arcs).
#  
#  x = var('x', arcs)
#
#for each node, we must balance the
#probabilities of in-arcs and out-arcs.
# for j in nodes:
#   x[i,j] == sum( x[j,k] 
#        for k in children of j)
#
# And a value can be assigned to each arc as well,
# as this is a standard feature of decision trees.
#
# maximize( sum(x[i]*v[i] for i in arcs ) )

#####
# approach two
#####
#each arc has a binary var (indicating if it is chosen).
#if it is not chosen, then all the children of the node
# that is directly reached by this arc can not be chosen.
#if it is chosen, there are two cases:
# 1) if it leads to a decision node, only one of its children
#     may be chosen;
# sum(x[i] for i in arcs from dec_node) == x[arc]
# 2) if it leads to an event node, all of its children are chosen.
# x[i] == x[arc] for i in arcs from event_node

# Also note that, for any single arc,
# a probability can be assigned to it this way:
# a unique path exists from the root to this arc,
# and each event arc on the path has a probability,
# simply find the product of those probabilities,
# and assign the product to the arc in question.

# And a value can be assigned to each arc as well,
# as this is a standard feature of decision trees.

# Then maximize( x[i] * v[i] * p[i] for i in arcs )


x = var('x', decisions, bounds = (None, None))
y = var('y', events, bounds = (None, None))


def vnode(node):
   if node not in tree:
      return node #assume a number
   return (y[node] if node in events else x[node])

minimize(sum(x[i] for i in decisions),'forced')
decst = {}
for i in decisions:
   decst[i] = st([ 0 <= x[i] - vnode(j) 
     for j in tree[i]], 'dec_node[%s]'%i)

st([y[i] == sum(j[1]*vnode(j[0]) for j in tree[i])
    for i in events], 'evt_nodes')

solve()

print(status())

for t in x: print(x[t])
for t in y: print(y[t])

print(x[tree_root].primal)

print("EVSI = %r"% evaluate(y['b'] - x['e']+S))


def trace_dec(cnode):
   if cnode in decisions:
      k = 0
      for j in tree[cnode]:
         if decst[cnode][k].dual:
            print("%s -> %s"%(cnode,str(j)))
         trace_dec(j)
         k += 1
   elif cnode in events:
      for j in tree[cnode]:
         trace_dec(j[0])

trace_dec(tree_root)
end()
