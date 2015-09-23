import matplotlib.pyplot as plt
circle1=plt.Circle((0,0),1,fill=False)
#circle2=plt.Circle((.5,.5),.2,color='b')
#circle3=plt.Circle((1,1),.2,color='g',clip_on=False)
fig = plt.gcf()
fig.gca().add_artist(circle1)
#fig.gca().add_artist(circle2)
#fig.gca().add_artist(circle3)
plt.show()