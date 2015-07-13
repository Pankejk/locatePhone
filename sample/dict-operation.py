import operator

d = [{'x' : 5, 'y' : 6, 'd' : 4353}, {'x' : 5, 'y' : 6, 'd' : 435},{'x' : 5, 'y' : 6, 'd' : 43}]
t = sorted(d, key=lambda x:x['d'])

print d
print t
