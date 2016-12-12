# ZEBRA, Who Owns the Zebra? 
# Adapted from GLPK to pymprog by Yingjie Lan <ylan@pku.edu.cn>

########################################################################
#  The Zebra Puzzle is a well-known logic puzzle.
#
#  It is often called "Einstein's Puzzle" or "Einstein's Riddle"
#  because it is said to have been invented by Albert Einstein as a boy,
#  with the common claim that Einstein said "only 2 percent of the
#  world's population can solve". It is also sometimes attributed to
#  Lewis Carroll. However, there is no known evidence for Einstein's or
#  Carroll's authorship.
#
#  There are several versions of this puzzle. The version below is
#  quoted from the first known publication in Life International
#  magazine on December 17, 1962.
#
#   1. There are five houses.
#   2. The Englishman lives in the red house.
#   3. The Spaniard owns the dog.
#   4. Coffee is drunk in the green house.
#   5. The Ukrainian drinks tea.
#   6. The green house is immediately to the right of the ivory house.
#   7. The Old Gold smoker owns snails.
#   8. Kools are smoked in the yellow house.
#   9. Milk is drunk in the middle house.
#  10. The Norwegian lives in the first house.
#  11. The man who smokes Chesterfields lives in the house next to the
#      man with the fox.
#  12. Kools are smoked in the house next to the house where the horse
#      is kept.
#  13. The Lucky Strike smoker drinks orange juice.
#  14. The Japanese smokes Parliaments.
#  15. The Norwegian lives next to the blue house.
#
#  Now, who drinks water? Who owns the zebra?
#
#  In the interest of clarity, it must be added that each of the five
#  houses is painted a different color, and their inhabitants are of
#  different national extractions, own different pets, drink different
#  beverages and smoke different brands of American cigarettes. One
#  other thing: In statement 6, right means your right.
#
#  (From Wikipedia, the free encyclopedia.)
########################################################################

HOUSE=range(1,6)

COLOR = ("blue", "green", "ivory", "red", "yellow")

NATIONALITY = ("Englishman", "Japanese", "Norwegian",
               "Spaniard", "Ukranian")

DRINK = ("coffee", "milk", "orange_juice", "tea", "water")

SMOKE = ("Chesterfield", "Kools", "Lucky_Strike", 
          "Old_Gold", "Parliament")

PET = ("dog", "fox", "horse", "snails", "zebra")

from pymprog import *
#Uncomment to forbid comparison with a variable as an expression.
#pymprog.variable.comparable=False
zeb = model("zebra")

color=zeb.var('color', iprod(HOUSE, COLOR), bool)
for h in HOUSE: sum(color[h,c] for c in COLOR)==1
for c in COLOR: sum(color[h,c] for h in HOUSE)==1

nationality=zeb.var('nation', iprod(HOUSE, NATIONALITY), bool)
for h in HOUSE: sum(nationality[h,n] for n in NATIONALITY)==1
for n in NATIONALITY: sum(nationality[h,n] for h in HOUSE)==1 

drink=zeb.var('drink', iprod(HOUSE, DRINK), bool)
for h in HOUSE: sum(drink[h,d] for d in DRINK)==1 
for d in DRINK: sum(drink[h,d] for h in HOUSE)==1 

smoke=zeb.var('smoke',iprod(HOUSE, SMOKE),bool)
for h in HOUSE: sum(smoke[h,s] for s in SMOKE)==1 
for s in SMOKE: sum(smoke[h,s] for h in HOUSE)==1 

pet=zeb.var('pet', iprod(HOUSE, PET),bool)
for h in HOUSE: sum(pet[h,p] for p in PET)==1 
for p in PET: sum(pet[h,p] for h in HOUSE)==1 

## the Englishman lives in the red house */
for h in HOUSE: nationality[h,"Englishman"]==color[h,"red"] 

## the Spaniard owns the dog */
for h in HOUSE: nationality[h,"Spaniard"]==pet[h,"dog"] 

## coffee is drunk in the green house */
for h in HOUSE: drink[h,"coffee"]==color[h,"green"] 

## the Ukrainian drinks tea */
for h in HOUSE: nationality[h,"Ukranian"]==drink[h,"tea"] 

## the green house is immediately to the right of the ivory house */
for h in HOUSE:
   color[h,"green"] == (color[h-1, "ivory"] if h>1 else 0)
## the Old Gold smoker owns snails */
for  h in HOUSE: smoke[h,"Old_Gold"]==pet[h,"snails"] 

## Kools are smoked in the yellow house */
for h in HOUSE: smoke[h,"Kools"]==color[h,"yellow"] 

## milk is drunk in the middle house */
drink[3,"milk"] == 1

## the Norwegian lives in the first house */
nationality[1,"Norwegian"] == 1

# the man who smokes Chesterfields lives in the house 
#   next to the man with the fox */
for h in HOUSE:(
   1 - smoke[h,"Chesterfield"] +
   (0 if h == 1 else pet[h-1,"fox"]) +
   (0 if h == 5 else pet[h+1,"fox"]) >= 1 )

# Kools are smoked in the house next to the house 
#   where the horse is kept */
for h in HOUSE:(
   1 - smoke[h,"Kools"] +
   (0 if h == 1 else pet[h-1,"horse"]) +
   (0 if h == 5 else pet[h+1,"horse"]) >= 1)

## the Lucky Strike smoker drinks orange juice */
for h in HOUSE:
   smoke[h,"Lucky_Strike"] == drink[h,"orange_juice"]


## the Japanese smokes Parliaments */
for h in HOUSE:
   nationality[h,"Japanese"] == smoke[h,"Parliament"]


#zeb.verb = True
## the Norwegian lives next to the blue house */
for h in HOUSE:(
   1 - nationality[h,"Norwegian"] +
   (0 if h == 1 else color[h-1,"blue"]) +
   (0 if h == 5 else color[h+1,"blue"]) >= 1)

zeb.solve()

def answ(h):
   for c in COLOR: 
      if color[h,c].primal>0: break
   for n in NATIONALITY:
      if nationality[h,n].primal>0: break
   for d in DRINK:
      if drink[h,d].primal>0: break
   for s in SMOKE:
      if smoke[h,s].primal>0: break
   for p in PET:
      if pet[h,p].primal>0: break
   return (h,c,n,d,s,p)

print("HOUSE  COLOR   NATIONALITY  DRINK         SMOKE         PET")
for h in HOUSE:
   print("%5d  %-6s  %-11s  %-12s  %-12s  %-6s"%answ(h))
zeb.end()
