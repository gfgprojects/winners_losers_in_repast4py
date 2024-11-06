#Pietro Terna's Code from
#https://github.com/terna/winners-losers/blob/main/par2.1Chakraborti.ipynb

#exec(open('par2.1Chakraborti.py').read())

import random
import matplotlib.pyplot as plt
import time

#timer T()
startTime=-1
def T():
    global startTime
    if startTime < 0:
        startTime=time.time()
    return time.time() - startTime

elapsedTime=T();
print(elapsedTime)

random.seed(123)

N=2400

v=[1]*N

for i in range (480000):
    a=random.randrange(N)
    b=random.randrange(N)

    tot=v[a]+v[b]

    q=random.random()

    v[a]=q*tot

    v[b]=(1-q)*tot

elapsedTime=T();
print(elapsedTime)

#plt.hist(v,200);
#plt.show()





