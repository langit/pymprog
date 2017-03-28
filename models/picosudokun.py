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
   elements in the same position of all sub-matrix must be distinct."""

from pymprog import *        # Import the module
begin("picosudoku")
n = 4
nn = n*n
I = range(1,1+nn)
J = range(1,1+nn)
K = range(1,1+nn)
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
st([sum(x[i,j,k] for i in range(r,r+n) for j in range(c, c+n))==1
 for r in range(1,1+nn,n) for c in range(1,1+nn,n) for k in K],'reg')

#elements in the same position of all regions are distinct
st([sum(x[i+ti*n,j+tj*n,k] for ti in range(n) for tj in range(n))==1 
    for k in K for i in range(1,1+n) for j in range(1,1+n)], 'pico')

"""Note: for any good arrangement, a permutation of the numbers
in the arrangement would give another good arrangement.
Thus one can always fix the first row to 1, 2, 3, ..., 9."""
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
   if i in range(1,1+nn,n):
      print(" +"+("---"*(n-1)+"--+")*n)
   print('', end=' ')
   for j in J:
      if j == 1: print("|", end='')
      print("%2g"%sum(x[i,j,k].primal*k for k in K), 
            end='|' if j in range(n,1+nn,n) else ' ')
      if j==nn: print()
   if i == nn:
      print(" +"+("---"*(n-1)+"--+")*n)

end()
