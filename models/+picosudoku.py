# SUDOKU, Number Placement Puzzle 
# Written in pymprog by Yingjie Lan <ylan@umd.edu>
from __future__ import print_function

"""Sudoku, also known as Number Place, is a logic-based placement
   puzzle. The aim of the canonical puzzle is to enter a numerical
   digit from 1 through 9 in each cell of a 9x9 grid made up of 3x3
   subgrids (called "regions"), starting with various digits given in
   some cells (the "givens"). Each row, column, and region must contain
   only one instance of each numeral.

   (From Wikipedia, the free encyclopedia.)

   This example will provide a sample PICO Sudoku:
   in addition to satisfying all the requirements 
   of Sudoku, PICO Sudoku also requires that the
   elements in all wrapped diagonals must be distinct."""

from pymprog import *        # Import the module
begin("picosudoku")
I = range(1,10)
J = range(1,10)
K = range(1,10)
T = iprod(I,J,K) #create Indice tuples
#x[i,j,k] = 1 means cell [i,j] is assigned number k 
x = var('x', T, bool) #binary vars
#each cell must be assigned exactly one number
st([sum(x[i,j,k] for k in K)==1 for i in I for j in J], 'cell')
#cells in the same row must be assigned distinct numbers
st([sum(x[i,j,k] for j in J)==1 for i in I for k in K], 'row') 
#cells in the same column must be assigned distinct numbers
st([sum(x[i,j,k] for i in I)==1 for j in J for k in K], 'col')
#cells in the same region must be assigned distinct numbers
st([sum(x[i,j,k] for i in range(r,r+3) for j in range(c, c+3))==1
 for r in range(1,10,3) for c in range(1,10,3) for k in K],'reg')

#cells in all wrapped \-diagonals sum up to const
st([sum(k*x[i,(i+h)%9+1,k] for i in I for k in K)==sum(K)
	for h in range(-1,8)], 'diag')

#cells in all wrapped /-diagonal sum up to const
st([sum(k*x[i,(h-i)%9+1,k] for i in I for k in K)==sum(K)
	for h in range(9,18)], 'codi')

"""Note: for any given arrangement, if there is a
   function on 1-9 that fully maps back to 1-9, then 
   the resultant arrangement after applying this function
   is still good in every aspect. Thus one can always
   fix the first row to 1, 2, 3, ..., 9."""
for j in J: 
   for k in K: 
       #protect assignment to this
       x[1, j, k] == (1 if j==k else 0)

#there is no need for an objective function here
solver('intopt', 
        #this branching option usually helps a lot
        br_tech=glpk.GLP_BR_PCH, #branching technique 
)

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
