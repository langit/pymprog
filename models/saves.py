from pymprog import *
p = begin('save')
x = var('x', 3)
x[2].kind = int
c = par('c', [100, 300, 50])
b = par('b', [93000, 101, 201])
maximize(sum(c[i]*x[i] for i in range(3)), 'Profit')

300*x[0] + 1200*x[1] + 120*x[2] <= b[0]
0.5*x[0] +      x[1] + 0.5*x[2] <= b[1]
r = x[0] +          x[1] +     x[2] <= b[2]

solve()

save(mps='_save.mps', sol='_save.sol',
     clp='_save.clp', glp='_save.glp', 
     sen='_save.sen', ipt='_save.ipt',
     mip='_save.mip')

end()
