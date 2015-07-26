from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.gca(projection='3d')
X = np.arange(-5, 5, .25)
print 'X: ' + str(X)
print len(X)
Y = np.arange(-5, 5, .25)
print 'Y: ' + str(Y)
print len(Y)
X, Y = np.meshgrid(X, Y)
print 'AFTER MESHGRID: '
print 'X: ' + str(X)
print len(X)
print 'Y: ' + str(Y)
print len(Y)
R = np.sqrt(X**2 + Y**2)
print 'R'
print R
print len(R)
Z = np.sin(R)
print 'Z'
print Z
print len(Z)
Gx, Gy = np.gradient(Z) # gradients with respect to x and y
print 'Gx'
print Gx
print len(Gx)
print 'Gy'
print Gy
print len(Gy)
G = (Gx**2+Gy**2)**.5  # gradient magnitude
print 'G'
print G
print len(G)
N = G/G.max()  # normalize 0..1
print 'N'
print N
print len(N)
surf = ax.plot_surface(
    X, Y, Z, rstride=1, cstride=1,
    facecolors=cm.jet(N),
    linewidth=0, antialiased=False, shade=False)
plt.show()



#import random

#def fun(x, y):
#    return x**2 + y

#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#x = y = np.arange(-3.0, 3.0, 0.05)
#X, Y = np.meshgrid(x, y)
#zs = np.array([fun(x,y) for x,y in zip(np.ravel(X), np.ravel(Y))])
#Z = zs.reshape(X.shape)

#ax.plot_surface(X, Y, Z)

#ax.set_xlabel('X Label')
#ax.set_ylabel('Y Label')
#ax.set_zlabel('Z Label')

#plt.show()
