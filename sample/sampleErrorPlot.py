import pylab as plt
import random
x1, y1, z1 = [], [], []
x1 = [int(1000*random.random()) for i in xrange(10)]
y1 = [int(1000*random.random()) for i in xrange(10)]
z1 = [int(1000*random.random()) for i in xrange(10)]
# make a figure and an axes object
fig, ax = plt.subplots()
# ax.plot(x1, y1, 'o')
ax.errorbar(x1, y1, yerr=z1, xerr=z1, marker='o')

plt.show()
