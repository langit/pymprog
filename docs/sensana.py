from pymprog import *
begin('trader')
x = var('x', 3)
c = par('c', [100, 300, 50])
b = par('b', [93000, 101, 201])
maximize(sum(c[i]*x[i] for i in range(3)), 'Profit')

300*x[0] + 1200*x[1] + 120*x[2] <= b[0]
0.5*x[0] +      x[1] + 0.5*x[2] <= b[1]

solve()
sensitivity()

b[1].value += 1
solve()

end()
