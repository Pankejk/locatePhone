import matplotlib.pyplot as plt
from numpy.random import normal
gaussian_numbers = [10,10,10]#normal(size=1000)
plt.hist(gaussian_numbers)
plt.title("Gaussian Histogram")
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.show()
