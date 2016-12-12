import unittest

def mymodels():
    import glob, os.path
    ff ='''
def test_{name}(me):
    print(' >>> Testing model: {name}')
    import models.{name}
'''
    for f in glob.glob('models/[a-z]*[.]py'):
        with open(f) as h:
            for l in h: 
                if 'pymprog' in l:
                    f = os.path.split(f)[1][:-3]
                    print(f)
                    yield ff.format(name=f)
                    break

class TestExamples(unittest.TestCase):
    for code in mymodels():
        exec(code)

if __name__ == '__main__':
     unittest.main()
