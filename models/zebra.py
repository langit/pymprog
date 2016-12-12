# ZEBRA, Who Owns the Zebra? 
# Written in pymprog by Yingjie Lan <ylan@umd.edu>

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
from __future__ import print_function

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
zeb.st([sum(color[h,c] for c in COLOR)==1 for h in HOUSE])
zeb.st([sum(color[h,c] for h in HOUSE)==1 for c in COLOR])

nationality=zeb.var('nation', iprod(HOUSE, NATIONALITY), bool)
zeb.st([sum(nationality[h,n] for n in NATIONALITY)==1 for h in HOUSE])
zeb.st([sum(nationality[h,n] for h in HOUSE)==1 for n in NATIONALITY])

drink=zeb.var('drink', iprod(HOUSE, DRINK), bool)
zeb.st([sum(drink[h,d] for d in DRINK)==1 for h in HOUSE])
zeb.st([sum(drink[h,d] for h in HOUSE)==1 for d in DRINK])

smoke=zeb.var('smoke', iprod(HOUSE, SMOKE), bool)
zeb.st([sum(smoke[h,s] for s in SMOKE)==1 for h in HOUSE])
zeb.st([sum(smoke[h,s] for h in HOUSE)==1 for s in SMOKE])

pet=zeb.var('pet', iprod(HOUSE, PET), bool)
zeb.st([sum(pet[h,p] for p in PET)==1 for h in HOUSE])
zeb.st([sum(pet[h,p] for h in HOUSE)==1 for p in PET])

## the Englishman lives in the red house */
zeb.st([nationality[h,"Englishman"]==color[h,"red"] for h in HOUSE])

## the Spaniard owns the dog */
zeb.st([nationality[h,"Spaniard"]==pet[h,"dog"] for h in HOUSE])

## coffee is drunk in the green house */
zeb.st([drink[h,"coffee"]==color[h,"green"] for h in HOUSE])

## the Ukrainian drinks tea */
zeb.st([nationality[h,"Ukranian"]==drink[h,"tea"] for h in HOUSE])

## the green house is immediately to the right of the ivory house */
zeb.st([ + color[h,"green"] == (color[h-1, "ivory"] if h>1 else 0)
      for h in HOUSE])
## the Old Gold smoker owns snails */
zeb.st([smoke[h,"Old_Gold"]==pet[h,"snails"] for  h in HOUSE])

## Kools are smoked in the yellow house */
zeb.st([smoke[h,"Kools"]==color[h,"yellow"] for h in HOUSE])

## milk is drunk in the middle house */
zeb.st(drink[3,"milk"] == 1)

## the Norwegian lives in the first house */
zeb.st(nationality[1,"Norwegian"] == 1)

# the man who smokes Chesterfields lives in the house 
#   next to the man with the fox */
zeb.st([ 
   1 - smoke[h,"Chesterfield"] +
   (0 if h == 1 else pet[h-1,"fox"]) +
   (0 if h == 5 else pet[h+1,"fox"]) >= 1 
   for h in HOUSE])

# Kools are smoked in the house next to the house 
#   where the horse is kept */
zeb.st([
   1 - smoke[h,"Kools"] +
   (0 if h == 1 else pet[h-1,"horse"]) +
   (0 if h == 5 else pet[h+1,"horse"]) >= 1
   for h in HOUSE])

## the Lucky Strike smoker drinks orange juice */
zeb.st([smoke[h,"Lucky_Strike"] == drink[h,"orange_juice"]
   for h in HOUSE])


## the Japanese smokes Parliaments */
zeb.st([nationality[h,"Japanese"] == smoke[h,"Parliament"]
   for h in HOUSE])


#zeb.verb = True
## the Norwegian lives next to the blue house */
zeb.st([1 - nationality[h,"Norwegian"] +
   (0 if h == 1 else color[h-1,"blue"]) +
   (0 if h == 5 else color[h+1,"blue"]) >= 1
   for h in HOUSE])

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
