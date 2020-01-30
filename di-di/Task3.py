import bn256
import numpy as np
import random
import copy

v1=np.random.choice([1,-1],16 )
print('v1 =',v1)
v2=np.random.choice([1,-1],16)
print('v2 =',v2)

G1 = bn256.curve_G     #generator  of group 1
G2 = bn256.twist_G     #generator  of group 2
print('G1=',G1)
print('G2=',G2)

for i in v1:
    v1p = [G2.scalar_mul(bn256.order +i)]
for i in v2:
    v2p = [G1.scalar_mul(bn256.order +i)]

print('v1p =',v1p)
print('v2p =',v2p)

