from pymprog import *

#####Solve this 2-player 0-sum game:
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
# the gain of player 1
v = var('game_value', 
      bounds=(None,None)) #free
# mixed strategy of player 2
p = var('prob', [1,2]) 
# player 2 wants to minimize v
minimize(v) 
# probability sums to 1
st(p[1]+p[2] == 1)
# player 1 plays the best strat.
r1=st(v >= 5*p[1] + 9*p[2])
r2=st(v >= 8*p[1] + 6*p[2])
solve()
print(v)
print("Player 1's mixed Strategy:" )
print("A1: %r; A2: %r"%(r1.dual, r2.dual))
print("Player 2's mixed strategy:" )
print("B1: %r; B2: %r"%(p[1].primal, p[2].primal))
end()
