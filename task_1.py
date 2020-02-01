import lib.bn256 as bn256
import random as r

def invert(P): return P.scalar_mul(bn256.order - 1)

R = [r.randrange(2, bn256.order) for _ in range(3)]

TG1 = [bn256.curve_G.scalar_mul(R[i]) for i in range(3)]
TP = TG1[0].add(TG1[1]).add(invert(TG1[2]))

TG2 = [bn256.twist_G.scalar_mul(R[i]) for i in range(3)]
TQ = TG2[0].add(TG2[1]).add(invert(TG2[2]))

tf = R[0] + R[1] - R[2]

oa_exp = bn256.optimal_ate(bn256.twist_G,bn256.curve_G).exp(tf ** 2)
oa_str = bn256.optimal_ate(TQ,TP)

print(oa_exp == oa_exp)
