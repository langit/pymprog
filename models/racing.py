king_horse_speed = (2,4,6)
tian_horse_speed = (1,3,5)

#the order to race the horses
strats = (
 (0,1,2),
 (0,2,1),
 (1,0,2),
 (1,2,0),
 (2,0,1),
 (2,1,0)
)

bonus = (3,2,1) # traditional: (1,1,1)

def gain(king_strat, tian_strat):
   g = 0
   for i,j,k in zip(king_strat, tian_strat, range(3)):
      if king_horse_speed[i] > tian_horse_speed[j]:
         g += bonus[k]
      else: 
         g -= bonus[k]
   return g


A = [ [gain(a,b) for a in strats] for b in strats ]


from pymprog import *

beginModel('racing')
v = var('game_value', bounds=(None, None))
x = var('prob', strats)
minimize(v)
st( sum( x[s] for s in strats ) == 1 )
rr = st( 
   v >= sum( A[i][j]*x[strats[j]] for j in range(6) ) 
                                  for i in range(6) 
)

solve()
print(v)
for s in x: 
   if x[s].primal > 0: print(x[s])
for r in range(6):
   if rr[r].dual > 0:
      print(strats[r], rr[r].dual)
end()
