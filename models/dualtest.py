from pymprog import *

beginModel('dual')

x = var('x')
minimize(x)
r=st(+x>=5)

solve()
print(status())

print(r.dual)

end()
