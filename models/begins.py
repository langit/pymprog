from pymprog import *

m = begin('a')
assert model._prob_ is m
x = var('x')
end()
assert model._prob_ is None

m = model('b')
# can't use global functions
try: 
    x = var('x')
except: pass
else:
    raise Exception("Can't reach here!")

try: end()
except: pass
else:
    raise Exception("Can't reach here!")
