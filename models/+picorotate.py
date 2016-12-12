mat=(
(2 , 2 , 7 , 2 , 7 , 9 , 8 , 3 , 5),
  (9 , 8 , 3 , 8 , 2 , 1 , 2 , 9 , 3),
   (1 , 8 , 5 , 7 , 3 , 6 , 8 , 6 , 1),
    (9 , 8 , 1 , 3 , 4 , 3 , 7 , 6 , 4),
     (1 , 5 , 5 , 8 , 4 , 9 , 5 , 5 , 3),
      (1 , 9 , 6 , 4 , 6 , 4 , 3 , 3 , 9),
       (8 , 2 , 4 , 1 , 9 , 5 , 5 , 4 , 7),
        (7 , 1 , 9 , 4 , 4 , 6 , 1 , 7 , 6),
	 (7 , 2 , 5 , 8 , 6 , 2 , 6 , 2 , 7))

def test(n,m):
    "see if n and m are right"
    grp = [set() for i in n]
    for r1, r2 in zip(n,m):
	    for i,j in zip(r1,r2):
		    if j in grp[i-1]: return False
		    grp[i-1].add(j)

def flip(n): return zip(*n)

def rotate(n): return [reversed(r) for r in zip(*n)]

def rotout(n):
	if test(n,mat): return True
	for i in range(3):
		n=rotate(n)
		if test(n,mat): return True
	return False

def checkout(n):
	if rotout(n): return True
	n=flip(n)
	return rotout(n)


print(checkout(mat))
