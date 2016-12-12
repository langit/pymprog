# SUDOKU, Number Placement Puzzle 
# Written in pymprog by Yingjie Lan <ylan@umd.edu>
from __future__ import print_function
"""Sudoku, also known as Number Place, is a logic-based placement
   puzzle. The aim of the canonical puzzle is to enter a numerical
   digit from 1 through 9 in each cell of a 9x9 grid made up of 3x3
   subgrids (called "regions"), starting with various digits given in
   some cells (the "givens"). Each row, column, and region must contain
   only one instance of each numeral.

   Example:

   +-------+-------+-------+
   | 5 3 . | . 7 . | . . . |
   | 6 . . | 1 9 5 | . . . |
   | . 9 8 | . . . | . 6 . |
   +-------+-------+-------+
   | 8 . . | . 6 . | . . 3 |
   | 4 . . | 8 . 3 | . . 1 |
   | 7 . . | . 2 . | . . 6 |
   +-------+-------+-------+
   | . 6 . | . . . | 2 8 . |
   | . . . | 4 1 9 | . . 5 |
   | . . . | . 8 . | . 7 9 |
   +-------+-------+-------+

   (From Wikipedia, the free encyclopedia.)"""

# the "givens" 
g =(
(5,3,0,0,7,0,0,0,0),
(6,0,0,1,9,5,0,0,0),
(0,9,8,0,0,0,0,6,0),
(8,0,0,0,6,0,0,0,3),
(4,0,0,8,0,3,0,0,1),
(7,0,0,0,2,0,0,0,6),
(0,6,0,0,0,0,2,8,0),
(0,0,0,4,1,9,0,0,5),
(0,0,0,0,8,0,0,7,9))

import pymprog
p = pymprog.model("sudoku")
I = range(1,10)
J = range(1,10)
K = range(1,10)
T = pymprog.iprod(I,J,K) #create Indice tuples
x = p.var('x', T, bool)
#x[i,j,k] = 1 means cell [i,j] is assigned number k 
#assign pre-defined numbers using the "givens"
p.st( [ +x[i,j,k] == (1 if g[i-1][j-1] == k else 0) 
       for (i,j,k) in T if g[i-1][j-1] > 0 ], 'given')

#each cell must be assigned exactly one number
p.st([sum(x[i,j,k] for k in K)==1 for i in I for j in J], 'cell')

#cells in the same row must be assigned distinct numbers
p.st([sum(x[i,j,k] for j in J)==1 for i in I for k in K], 'row') 

#cells in the same column must be assigned distinct numbers
p.st([sum(x[i,j,k] for i in I)==1 for j in J for k in K], 'col')

#cells in \-diagonal
#p.st([sum(x[i,i,k] for i in I)==1 for k in K])

#cells in /-diagonal
#p.st([sum(x[i,10-i,k] for i in I)==1 for k in K])

#cells in the same region must be assigned distinct numbers
p.st([sum(x[i,j,k] for i in range(r,r+3) for j in range(c, c+3))==1
    for r in range(1,10,3) for c in range(1,10,3) for k in K],'reg')
   
#there is no need for an objective function here

p.solve()

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
p.end()
