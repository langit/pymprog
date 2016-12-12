import pymprog    # Import the module
# index and data
cid, rid = range(3), range(3)
c = (10.0, 6.0, 4.0)
mat = [ (1.0, 1.0, 1.0),     
        (10.0, 4.0, 5.0),   
        (2.0, 2.0, 6.0)]   
b = (100.0, 600.0, 300.0)
# Create empty problem instance
p = pymprog.model('basic example')  
#create variables: 
x = p.var('X', 3) # x: dict with keys in 'cid'
p.maximize(sum(c[i]*x[i] for i in cid), 'myobj')
p.verbose(True)
r=p.st( 
  0 <= sum(x[j]*mat[i][j] for j in cid) <= b[i] 
           for i in rid)
#solve and report
p.solve()
print('Z = %g;' % p.vobj()) # obj value
# Print struct variable names and primal values
print(';\n'.join('%s = %g {dual: %g}' % (
   x[i].name, x[i].primal, x[i].dual) 
                    for i in cid))
print(';\n'.join('%s = %g {dual: %g}' % (
   r[i].name, r[i].primal, r[i].dual) 
                    for i in rid))

p.sensitivity()
p.end()
