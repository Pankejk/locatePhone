import numpy as np
import matplotlib.pyplot as plt
import scipy.stats

'''fig, ax = plt.subplots(1, 1)
x = np.linspace(scipy.stats.norm.ppf(0.01), scipy.stats.norm.ppf(0.99), 100)
print x
y = scipy.stats.norm.pdf(x)
print y
ax.plot(x, scipy.stats.norm.pdf(x),'r-', lw=5, alpha=0.6, label='norm pdf')

plt.show()'''

fig, ax = plt.subplots(1, 1)
x = np.linspace(-74, -86, 100)
print x
y = scipy.stats.norm.cdf(x,-80,6)
print y
ax.plot(x, scipy.stats.norm.cdf(x,-80,6),'r-', lw=5, alpha=0.6, label='norm pdf')

plt.show()