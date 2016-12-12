from pymprog import *  # Import the module
# max { c'x: Ax <= b, x >= 0 }
c = (10.0, 6.0, 4.0)
A = [ (1.0, 1.0, 1.0),     
       (10.0, 4.0, 5.0),   
       (2.0, 2.0, 6.0)]   
b = (100.0, 600.0, 300.0)
# index for row and variable
ir, ix = range(3), range(3)

begin('basic') # start problem 
verbose(True) # show model

x = var('X', 3) # create 3 variables
maximize(sum(c[i]*x[i] for i in ix))

for i in ir: 
    sum(x[j]*A[i][j] for j in ix) <= b[i] 

solve() #solve the problem

print("Solver status:", status())
print('Z = ', vobj()) # obj value

#Print variable names and related values
for i in ix: print("%s = %g; dual = %g"%(
         x[i].name, x[i].primal, x[i].dual))

print(KKT())
print(evaluate(sum(x[i]*(i+x[i])**2 for i in ix)))
print(sum(x[i].primal*(i+x[i].primal)**2 for i in ix))
end() #Good habit: do away with the problem
