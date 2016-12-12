from __future__ import print_function
from pymprog import *
begin('test')
verbose(True)

x = var('x', 3)
r = group('R',
   '{name} is the bound for the sum of x[{0}]' 
   ' and its rotating next.') 

for j in range(3): print(r.desc(j))

for i in range(3):
    r[i] = x[i] + x[ (i+1) % 3] <= 1

x[0]+0.2 <= x[1] + 0.1 <= x[2]

maximize(sum(x[i] for i in range(3)))

#print(ncon())

solve()

for j in range(3): 
    print(x[j], r[j])

end('test')
