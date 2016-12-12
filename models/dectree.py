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

begin("dectree")
verbose(True)

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

st([ y[i] == sum(j[1]*vnode(j[0]) for j in tree[i])
    for i in events], 'evt_nodes')

solve()

print(status())

for t in x: print(x[t])
for t in y: print(y[t])

print(x[tree_root].primal)

print("EVSI = %r"% evaluate(y['b'] - x['e']+S))

def trace_dec(cnode):
   #print "tracing node", cnode
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
