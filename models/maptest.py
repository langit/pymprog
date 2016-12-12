from pymprog import model
imap = model._idxmap

def test_del1():
    m = imap()
    a = m.add(5)
    assert a == 1
    m.del1(1)
    assert m.nmap == 4
    for i in range (5):
        assert m.map(1+i) == i
    m.del1(5)
    m.del1(3)
    assert m.map(3) == 0
    assert m.map(4) == 2
    try: 
        m.map(5) #exception
        assert 1>2
    except: pass
    assert m.nmap == 2
    a = m.add(3)
    assert a == 5
    assert m.map(a) == 3
    
    
    

def test_delmany():
    m = imap()
    a = m.add(50)
    assert a == 1
    dl = [2, 9, 20, 21, 22, 48, 49, 50]
    m.delmany(dl)
    prev = 0
    for i, d in enumerate(dl):
        if d<48: 
            #print(i, d, m.map(d-1))
            assert m.map(d-1) == (d-1-i if prev+1 < d else 0)
        try:
            assert m.map(d) == 0
            if d<48: assert 1>2
        except: pass
        prev = d

test_del1()
test_delmany()
