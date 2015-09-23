import numpy as np
import matplotlib.pyplot as plt

xs = np.arange(8)
series1 = np.array([1, 3, None, None, None, 5, 8, 9]).astype(np.double)
s1mask = np.isfinite(series1)
#series2 = np.array([2, None, 5, None, 4, None, 3, 2]).astype(np.double)
#s2mask = np.isfinite(series2)
print xs
print series1
print s1mask
print xs[s1mask]
print series1[s1mask]
plt.plot(xs[s1mask], series1[s1mask], linestyle='-', marker='o')
#plt.plot(xs[s2mask], series2[s2mask], linestyle='-', marker='o')

plt.show()