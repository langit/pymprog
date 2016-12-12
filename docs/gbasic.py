from pymprog import * 
c = (10, 6, 4)
A = [ ( 1, 1, 1),     
      ( 9, 4, 5),   
      ( 2, 2, 6) ]   
b = (10, 60, 30)
begin('basic') # begin modelling
verbose(True)  # be verbose
x = var('x', 3) #create 3 variables
maximize(sum(c[i]*x[i] for i in range(3)))
for i in range(3):
  sum(A[i][j]*x[j] for j in range(3)) <= b[i] 
solve() # solve the model
sensitivity() # sensitivity report
end() #Good habit: do away with the model
