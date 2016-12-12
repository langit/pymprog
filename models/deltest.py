from pymprog import *
p = begin('trader')
verbose(True)
x = var('x', 3)
c = par('c', [100, 300, 50])
b = par('b', [93000, 101, 201])
maximize(sum(c[i]*x[i] for i in range(3)), 'Profit')

300*x[0] + 1200*x[1] + 120*x[2] <= b[0]
0.5*x[0] +      x[1] + 0.5*x[2] <= b[1]
r = x[0] +          x[1] +     x[2] <= b[2]

solve()
sensitivity()

r.delete()
# deleting a basic varriable destroys the basis
x[1].delete()
# restore the standard basis
p.std_basis() 
solve()
sensitivity()

end()
