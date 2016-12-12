from pymprog import model 
c = (10, 6, 4)
A = [ ( 1, 1, 1),     
      ( 9, 4, 5),   
      ( 2, 2, 6) ]   
b = (10, 60, 30)
p = model('basic')  
p.verbose(True)
x = p.var('x', 3) 
p.maximize(sum(c[i]*x[i] for i in range(3)))
for i in range(3):
  sum(A[i][j]*x[j] for j in range(3)) <= b[i] 
p.solve() # solve the model
p.sensitivity() # sensitivity report
p.end()
