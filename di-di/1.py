import random
import bn256 

r1=random.randrange(2, bn256.order) #three random numbers
r2=random.randrange(2, bn256.order)
r3=random.randrange(2, bn256.order)
print('r1 =',r1)
print('r2 =',r2)
print('r3 =',r3)

G1 = bn256.curve_G     #generator  of group 1
G2 = bn256.twist_G     #generator  of group 2
print('G1=',G1)
print('G2=',G2)

T1=G1.scalar_mul(r1)   #T1 = r1 * G1
T2=G1.scalar_mul(r2)   #T2 = r2 * G1
T3=G1.scalar_mul(r3)   #T3 = r3 * G1
print ('T1=',T1)
print('T2=',T2)
print('T3=',T3)

TP=T1.add(T2).add(T3.scalar_mul(bn256.order - 1))     #TP = T1 + T2 - T3
print('TP=',TP)

T4=G2.scalar_mul(r1)   #T4 = r1 * G2
T5=G2.scalar_mul(r2)   #T5 = r2 * G3
T6=G2.scalar_mul(r3)   #T6 = r3 * G4
print('T4=',T4)
print('T5=',T5)
print('T6=',T6)

TQ = T4.add(T5).add(T6.scalar_mul(bn256.order - 1))   #TQ = T4 + T5 - T6
print('TQ=',TQ)

tf=r1+r2-r3            #tf = r1 + r2 - r3
print('tf=',tf)

E1=bn256.optimal_ate(G2,G1).exp(tf**2)
E2 = bn256.optimal_ate(TQ,TP)
print(E1==E2)