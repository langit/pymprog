import csv
dists = csv.reader(open('capdist.csv'), 'excel')
dm = [[int(k) for k in t[2:33]] 
     for t in dists if t[1]]

n = len(dm) #how many cities

max_dist = max(max(t) for t in dm)

print(n)
for row in dm:
   print(' '.join("%r"%(max_dist - x) 
             for x in row))
