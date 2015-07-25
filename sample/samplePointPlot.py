import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
x_points = xrange(0,9)
y_points = xrange(0,9)
p = ax.plot(x_points, y_points, 'b')
ax.set_xlabel('x-points')
ax.set_ylabel('y-points')
ax.set_title('Simple XY point plot')
fig.show()


from pylab import *

# Generate random test data in your range
N = 200
epsilon = 10**(-9.0)
X = epsilon*(50*random(N) + 1)
Y = random(N)

# X2 now has the "units" of nanometers by scaling X
X2 = (1/epsilon) * X

subplot(121)
scatter(X,Y)
xlim(epsilon,50*epsilon)
xlabel("meters")

subplot(122)
scatter(X2,Y)
xlim(1, 50)
xlabel("nanometers")

show()
