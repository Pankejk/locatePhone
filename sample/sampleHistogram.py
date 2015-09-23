import matplotlib.pyplot as plt
from numpy.random import normal
gaussian_numbers = normal(size=1000)
print type(gaussian_numbers)
plt.hist(gaussian_numbers)
plt.title("Gaussian Histogram")
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.show()
