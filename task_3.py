import lib.bn256 as bn256
import random as r
import time

def ms(func):
    def q(*args, **kwargs):
        t = time.process_time()
        out = func(*args, **kwargs)
        t = time.process_time() - t
        print(func.__name__,' : ',t)
        return out
    return q

def hamming_distance(v1,v2):
    return sum(v1[i] != v2[i] for i in range(len(v1))) / len(v1)

def invert(P): return P.scalar_mul(bn256.order - 1)

def gen_vect(n): return [r.randint(0,q) for _ in range(n)]

q = bn256.order

def points(v,G): return [G.scalar_mul(q + i) for i in v]

G1 = bn256.curve_G
G2 = bn256.twist_G

v1 = [r.choice([-1,1]) for _ in range(16)]
v2 = [r.choice([-1,1]) for _ in range(16)]

@ms
def KeyGen():
    s = gen_vect(16)
    t = gen_vect(16)
    u = gen_vect(18)
    v = gen_vect(18)
    h1 = r.randint(2,q)
    H1 = G1.scalar_mul(h1)
    h2 = r.randint(2,q)
    H2 = G2.scalar_mul(h2)
    gen1_h = [G1.scalar_mul(s[i]).add(H1.scalar_mul(t[i])) for i in range(16)]
    gen2_h = [G2.scalar_mul(u[i]).add(H2.scalar_mul(v[i])) for i in range(18)]
    return {'H1':H1,'H2':H2,'gen1_h':gen1_h,'gen2_h':gen2_h,'s':s,'t':t,'u':u,'v':v}

msk = KeyGen()

@ms
def Reg(msk,v1):
    v1points = points(v1,G2)
    r0 = r.randint(2,q)
    reg_t = [G2.scalar_mul(r0), msk['H2'].scalar_mul(r0)] + [msk['gen2_h'][i].scalar_mul(r0) for i in range(18)]
    f2 = v1points[0].scalar_mul(msk['s'][0])
    f3 = v1points[0].scalar_mul(msk['t'][0])
    for i in range(1,16):
        f2 = f2.add(v1points[i].scalar_mul(msk['s'][i]))
        f3 = f3.add(v1points[i].scalar_mul(msk['t'][i]))
        reg_t[i+4] = reg_t[i+4].add(v1points[i])
    reg_t[2] = reg_t[2].add(invert(f2))
    reg_t[3] = reg_t[3].add(invert(f3))
    reg_t[4] = reg_t[4].add(v1points[0])
    return reg_t

t1 = Reg(msk,v1)

@ms
def Auth(msk,v2):
    v2points = points(v2,G1)
    r0 = r.randint(2,q)
    auth_t = [G1.scalar_mul(0)]*2
    auth_t.append(G1.scalar_mul(r0))
    auth_t.append(msk['H1'].scalar_mul(r0))
    for i in range(4,20):
        auth_t.append(msk['gen1_h'][i-4].scalar_mul(r0))
        auth_t[i] = auth_t[i].add(v2points[i-4])
    f0 = auth_t[2].scalar_mul(msk['u'][0])
    f1 = auth_t[2].scalar_mul(msk['v'][0])
    for i in range(1,18):
        f0 = f0.add(auth_t[i+2].scalar_mul(msk['u'][i]))
        f1 = f1.add(auth_t[i+2].scalar_mul(msk['v'][i]))
    auth_t[0] = auth_t[0].add(invert( f0 ))
    auth_t[1] = auth_t[1].add(invert( f1 ))
    return auth_t

t2 = Auth(msk,v2)

log_table = [bn256.optimal_ate(G2,G1).exp(i) for i in range(16, -1, -2)]+[bn256.optimal_ate(G2, invert(G1)).exp(i) for i in range(2, 17, 2)]

@ms
def hamming_distance2(reg_t,auth_t):
    e = bn256.optimal_ate(reg_t[0],auth_t[0])
    for i in range(1,20):
        e = e.mul(bn256.optimal_ate(reg_t[i],auth_t[i]))
    return log_table.index(e)/16

print(hamming_distance(v1,v2) == hamming_distance2(t1,t2))
