from pymprog import *
# http://pymprog.sourceforge.net/

c = 0.05
N = 30
#p = [(1.0+i)/N for i in range(N)]

minp = (1-1./N)**N # D* = (M-m)(1-1/T)**T
#minp = 0.37
print(minp)
p = [minp**((N-1.0-i)/(N-1.0)) for i in range(N)]
p = par('p', p)

begin("monopath")
x = var("x", N)
y = var("y", N, bool)
z = var('z', N, bool)
D = var("D")

minimize(D)
for t in range(N):
    D + sum(p[i]*x[i] - c*y[i] for i in range(t+1)) - c*z[t] >= p[t] - c
    y[t] >= x[t]
    z[t] >= 1 - sum(x[:t+1])

sum(x[i] for i in range(N)) == 1

# for i in range(72): x[i] == 0
# x[72] == 0.3
#x[16]==0.3 #coerced!

solve()
print(D.primal)
tset = [t for t in range(N) if y[t].primal]
for t in tset:
    print("%i\t%r\t%.5f\t%r"%(t, p[t], x[t].primal,p[t-1]))
    print(t, evaluate(D + sum(p[i]*x[i] - c*y[i] for i in range(t+1)) - c*z[t] - p[t]+c))
    if not t: continue
    print(t-1, evaluate(D + sum(p[i]*x[i] - c*y[i] for i in range(t)) - c*z[t-1] - p[t-1]+c))

dd = D.primal
for i in range(N):
    p[i].value = dd**((N-1.0-i)/(N-1.0))

solve()
print(D.primal)
tset = [t for t in range(N) if y[t].primal]
for t in tset:
    print("%i\t%r\t%.5f\t%r"%(t, p[t], x[t].primal,p[t-1]))
    print(t, evaluate(D + sum(p[i]*x[i] - c*y[i] for i in range(t+1)) - c*z[t] - p[t]+c))
    if not t: continue
    print(t-1, evaluate(D + sum(p[i]*x[i] - c*y[i] for i in range(t)) - c*z[t-1] - p[t-1]+c))

end()
