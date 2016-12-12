from pymprog import *

#####Solve this 2-player zero-sum game:
##
##     Gain for player 1 
##    (Loss for player 2)
##   
##            ||  Player  2
##   Player 1 ||  B1     B2
##      A1    ||  5      9
##      A2    ||  8      6
##
##############################

begin('game')
# gain of player 1, a free variable
v = var('game_value', bounds=(None,None))
# mixed strategy of player 2
p = var('p', 2) 
# probability sums to 1
sum(p) == 1
# player 2 chooses p to minimize v
minimize(v) 
# player 1 chooses the better value 
r1 =  v >= 5*p[0] + 9*p[1] 
r2 =  v >= 8*p[0] + 6*p[1]
solve()
print('Game value: %g'% v.primal)
print("Mixed Strategy for player 1:")
print("A1: %g, A2: %g"%(r1.dual, r2.dual))
print("Mixed Strategy for player 2:")
print("B1: %g, B2: %g"%(p[0].primal, p[1].primal))
end()
