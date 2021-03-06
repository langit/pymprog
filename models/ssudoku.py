from __future__ import print_function
"""Sudoku, also known as Number Place, is a logic-based placement
   puzzle. The aim of the canonical puzzle is to enter a numerical
   digit from 1 through 9 in each cell of a 9x9 grid made up of 3x3
   subgrids (called "regions"), starting with various digits given in
   some cells (the "givens"). Each row, column, and region must contain
   only one instance of each numeral.

   (From Wikipedia, the free encyclopedia.)

   This example will provide a sample Super Sudoku:
   in addition to satisfying all the requirements 
   of Sudoku, Super Sudoku also requires that the
   elements in each diagonal must be distinct."""

from pymprog import *        # Import the module
begin("ssudoku")
I = range(1,10)
J = range(1,10)
K = range(1,10)
T = iprod(I,J,K) #create Indice tuples
#x[i,j,k] = 1 means cell [i,j] is assigned number k 
x = var('x', T, bool) #binary vars
#each cell must be assigned exactly one number
[sum(x[i,j,k] for k in K)==1 for i in I for j in J]
#cells in the same row must be assigned distinct numbers
[sum(x[i,j,k] for j in J)==1 for i in I for k in K]
#cells in the same column must be assigned distinct numbers
[sum(x[i,j,k] for i in I)==1 for j in J for k in K]
#cells in the same region must be assigned distinct numbers
[sum(x[i,j,k] for i in range(r,r+3) for j in range(c, c+3))==1
 for r in range(1,10,3) for c in range(1,10,3) for k in K]

#cells in \-diagonal
[sum(x[i,i,k] for i in I)==1 for k in K]

#cells in /-diagonal
[sum(x[i,10-i,k] for i in I)==1 for k in K]

#there is no need for an objective function here

solve()

for i in I:
   if i in range(1,10,3):
      print(" +-------+-------+-------+")
   print('', end=' ')
   for j in J:
      if j in range(1,10,3): print("|", end=' ')
      print("%g"%sum(x[i,j,k].primal*k for k in K), end=' ')
      if j==9: print("|")
   if i == 9:
      print(" +-------+-------+-------+")

end()
