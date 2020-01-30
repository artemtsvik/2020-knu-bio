import bls from lib
import bn256 from lib
import tripartite from lib

import numpy as np

v1=np.random.choice([1,-1],16 )
print('v1 =',v1)
v2=np.random.choice([1,-1],16)
print('v2 =',v2)


def hamming_distance(string1, string2):
    distance = 0
    L = len(string1)
    for i in range(L):
        if string1[i] != string2[i]:
            distance += 1
    return distance
print(hamming_distance(v1,v2))