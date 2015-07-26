import matplotlib.pyplot as plt
import numpy as np

# Generate Data
data = np.random.rand(10,6)
print data
rows = list('ZYXWVUTSRQ')
columns = list('ABCDEF')

# Basic Syntax
plt.pcolor(data)
plt.show()
