#based on Pietro Terna's Code from
#https://github.com/terna/winners-losers/blob/main/par2.1Chakraborti.ipynb

#type
#exec(open('par2.1Chakraborti.py').read())
#to run the script from the python prompt

import random
import matplotlib.pyplot as plt
import time

#verboseFlag=True
verboseFlag=False
if verboseFlag:
    N=3
    iterations=10
else:
    N=2400
    iterations=480000

print()
print(f'Going to run the winners-losers model with {iterations} exchanges')

#timer T()
startTime=-1
def T():
    global startTime
    if startTime < 0:
        startTime=time.time()
    return time.time() - startTime

elapsedTime=T();

random.seed(123)

v=[1]*N
if verboseFlag: print('wealth at beginning',str(sum(v)))

for i in range (iterations):
    a=random.randrange(N)
    b=random.randrange(N)
    if a!=b:
        tot=v[a]+v[b]
        q=random.random()
        v[a]=q*tot
        v[b]=(1-q)*tot
        if verboseFlag: print(f'tick {i} total {tot}. To position {a}:{v[a]}, to position {b}: {v[b]}')
    else:
        if verboseFlag: print(f"tick {i} same position selected")

elapsedTime=T();
print()
if verboseFlag: print('seconds elapsed since beginning: ',str(round(elapsedTime,2)))
print()

if verboseFlag: print('wealth at end',str(sum(v)))

if not verboseFlag:
    plt.hist(v,200);
    plt.show()


