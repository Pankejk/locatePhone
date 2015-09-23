from matplotlib import pyplot as plt
y1 = [1,5,7,3]
x1 = [1,8,9,13]
#y2 = [3,5,10,3,6,8]
#x2 = range(4,len(y2)+4)
plt.plot(x1, y1, 'go-', label='line 1', linewidth=2)
#plt.plot(x2, y2, 'rs--',  label='line 2')
plt.legend()
plt.show()