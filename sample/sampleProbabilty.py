import scipy.stats

while(True):
    anws = raw_input('value,loc, scale')
    anws = anws.split(' ')
    value = int(anws[0])
    loc = int(anws[1])
    scale = int(anws[2])
    t = scipy.stats.norm.pdf(1,3,4)
    print t
    anws = raw_input('quit(q)')
    if anws == 'q':
        break
