
from pymprog import *

r = group('r')
begin('groups')
x, y = var('x, y')

r['abc'] =  x+y <= 1
assert r['abc'].name == "r['abc']"
r[1,2] = 3*x+y >= 5
assert r[1,2].name == "r[1,2]"



