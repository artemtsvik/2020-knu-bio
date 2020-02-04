import bn256
import numpy as np
import random


random_two_vector = (np.random.choice([1, -1], (2, 16)))
v1 = random_two_vector[0]
v2 = random_two_vector[1]
print('v1 =',v1)
print('v2 =',v2)

def hamming_distance(string1, string2):
    distance = 0
    L = len(string1)
    for i in range(L):
        if string1[i] != string2[i]:
            distance += 1
    return distance
hm=hamming_distance(v1,v2)
print(hamming_distance(v1,v2))

G1 = bn256.curve_G     
G2 = bn256.twist_G     
print('G1=',G1)
print('G2=',G2)

v1points = [G2.scalar_mul(bn256.order + i) for i in v1]
v2points  = [G1.scalar_mul(bn256.order + i) for i in v2]
print('v1points = ', v1points)
print('v2points =', v2points)

s = [random.randrange(2, bn256.order) for _ in range(16)]
t = [random.randrange(2, bn256.order) for _ in range(16)]
print('s =',s)
print('t =',t)


u = [random.randrange(2, bn256.order) for _ in range(18)]
v = [random.randrange(2, bn256.order) for _ in range(18)]
print('u =',u)
print('v =',v)

h1 = random.randrange (2, bn256.order)
h2 = random.randrange (2, bn256.order)
print('h1 =',h1)
print('h2 =',h2)

H1 = G1.scalar_mul(h1)
H2 = G2.scalar_mul(h2)
print('H1 =',H1)
print('H2 =',H2)

gen1_h = [G1.scalar_mul(int(s[i])).add(H1.scalar_mul(int(t[i]))) for i in range(len(s))]
gen2_h = [G2.scalar_mul(int(u[i])).add(H2.scalar_mul(int(v[i]))) for i in range(len(u))]
print('gen1_h =',gen1_h)
print('gen2_h =',gen2_h)

def IPE_reg(G2, s, t, v1points):
    r0 = random.randrange(2, bn256.order)
    reg_template = []
    reg_template.append(G2.scalar_mul(r0))
    reg_template.append(H2.scalar_mul(r0))
    for i in range(18):
        reg_template.append(gen2_h[i].scalar_mul(r0))

    for i in range(16):
        reg_template[2] = reg_template[2].add(v1points[i].scalar_mul(s[i]).scalar_mul(bn256.order - 1))
        reg_template[3] = reg_template[3].add(v1points[i].scalar_mul(t[i]).scalar_mul(bn256.order - 1))
        reg_template[i + 4] = reg_template[i + 4].add(v1points[i])

    return reg_template
result1=IPE_reg(G2, s, t, v1points)
print('result1 =',result1)

def IPE_aut(G1, u, v, v2points ):
    r0 = random.randrange(2, bn256.order)
    auth_template = []
    for i in range(2):
        auth_template.append(G1.scalar_mul(0))
    auth_template.append(G1.scalar_mul(r0))
    auth_template.append(H1.scalar_mul(r0))
    for i in range(16):
        auth_template.append(gen1_h[i].scalar_mul(r0).add(v2points[i]))
    for i in range(18):
        auth_template[0] = auth_template[0].add((auth_template[i+2].scalar_mul(u[i])).scalar_mul(bn256.order - 1))
        auth_template[1] = auth_template[1].add(auth_template[i+2].scalar_mul(v[i]).scalar_mul(bn256.order - 1))
    return auth_template
result2=IPE_aut(G1, u, v, v2points)
print('result2 =',result2)

e = bn256.optimal_ate(result1[0], result2[0])
for i in range(1, 20):
    e = e.mul(bn256.optimal_ate(result1[i], result2[i]))
print('e =',e)

spar_one = bn256.optimal_ate(G2, G1)
log_table = [spar_one.exp(i) for i in range(16, -1, -2)]
spar_two = bn256.optimal_ate(G2, G1.scalar_mul(bn256.order - 1))
log_table = log_table + [spar_two.exp(i) for i in range(2, 17, 2)]

index_e_log = log_table.index(e)
print('log_table.index(e) =',log_table.index(e))

if hm == index_e_log:
    print('True')