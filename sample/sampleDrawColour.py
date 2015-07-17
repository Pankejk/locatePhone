import numpy as np
import matplotlib.pyplot as plt

x = np.random.rand(100)
y = np.random.rand(100)
t = [0] * 100#np.arange(100)
print x
print y
print t
#plt.scatter(x, y, c=t)
#plt.show()



coord_data = np.array([[0, 0, 0, 0, 0, 0], [10, 9, 8, 7, 6, 5]])# [1, 1, 1, 1, 3, 3], [3, 3, 3, 3, 4, 1]])
map = plt.imshow(coord_data)
plt.colorbar(map)
plt.show()
