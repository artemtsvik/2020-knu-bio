import lib.bn256 as bn256
import random as rand

def additive_inverse(P): return P.scalar_mul(bn256.order -1)

r1 = rand.randrange(2, bn256.order)
r2 = rand.randrange(2, bn256.order)
r3 = rand.randrange(2, bn256.order)

G1 = bn256.curve_G
G2 = bn256.twist_G

T1 = G1.scalar_mul(r1)
T2 = G1.scalar_mul(r2)
T3 = G1.scalar_mul(r3)

TP = T1.add(T2).add(additive_inverse(T3))

T4 = G2.scalar_mul(r1)
T5 = G2.scalar_mul(r2)
T6 = G2.scalar_mul(r3)

TQ = T4.add(T5).add(additive_inverse(T6))

tf = r1 + r2 - r3

E1 = bn256.optimal_ate(G2,G1).exp(tf ** 2)
E2 = bn256.optimal_ate(TQ,TP)

print(E1 == E2)
