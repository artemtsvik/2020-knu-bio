import random
import bn256 
r1=random.randrange(2, bn256.order)
r2=random.randrange(2, bn256.order)
r3=random.randrange(2, bn256.order)
print('r1 =',r1)
print('r2 =',r2)
print('r3 =',r3)

G1 = bn256.curve_G
G2 = bn256.twist_G
print('G1=',G1)
print('G2=',G2)

T1=G1.scalar_mul(r1)
T2=G1.scalar_mul(r2)
T3=G1.scalar_mul(r3)
print ('T1=',T1)
print('T2=',T2)
print('T3=',T3)

TP=T1.add(T2).add(T3.scalar_mul(bn256.order - 1))
print('TP=',TP)

T4=G2.scalar_mul(r1)
T5=G2.scalar_mul(r1)
T6=G2.scalar_mul(r1)
print('T4=',T4)
print('T5=',T5)
print('T6=',T6)

TQ = T4.add(T5).add(T6.scalar_mul(bn256.order - 1))
print('TQ=',TQ)

tf=r1+r2-r3
print('tf=',tf)