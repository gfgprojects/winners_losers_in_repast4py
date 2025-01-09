#based on Pietro Terna's Code from
#https://github.com/terna/winners-losers/blob/main/par2.1Chakraborti.ipynb

#type
#exec(open('par2.1Chakraborti.py').read())
#to run the script from the python prompt

import random
import matplotlib.pyplot as plt
import time


print()
print('Going to run the winners-losers model with 480000 exchanges')

#timer T()
startTime=-1
def T():
    global startTime
    if startTime < 0:
        startTime=time.time()
    return time.time() - startTime

elapsedTime=T();

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
print()
print('seconds elapsed since beginning: ',str(round(elapsedTime,2)))
print()

#plt.hist(v,200);
#plt.show()


