import lib.bn256 as bn256
import lib.matrix as matrix
import lib.biometrics as biometrics
import random as rand
import time
from PIL import Image
from copy import copy

q = bn256.order

def time_spent(func): #Decorator for estimating perfomence of certain function.
    def _func(*args, **kwargs):
        t = time.process_time() # the same as time.clock(), time.clock() is not avalible in Python 3.8+
        res = func(*args, **kwargs)
        t = time.process_time() - t
        print('{0}: time elapsed {1:.8f} s.' .format(func.__name__, t))
        return res
    return _func

def HD(x,y): # Hamming distance
    assert len(x) == len(y)
    return (len(x) - sum([i*j for (i, j) in zip(y, x)]))/(2*len(x)) # (|x| - (x,y))/(2|x|) where (,) is an inner product

def inv(P): return P.scalar_mul(q - 1) # inverse element for the elliptic curve group.

def invG1(P):
    P = copy(P)
    P.y = P.y.additive_inverse()
    return P
def invG2(P):
    P.negate()
    return P

def gen_rand_vect(n,q=bn256.order,TH=False):
    # random vector with elements in Zq of length n if TH=False or vector of -1,1 of length n if TH=True
    if TH: return [rand.choice([-1,1]) for _ in range(n)]
    return [rand.randint(0,q) for _ in range(n)]

def points(v,G): # vector of -1,1 will be returned as vector of -G,G respectivly
    out = []
    _G = inv(G)
    for i in v:
        if i == -1: out.append(_G)
        else: out.append(G)
    return out

class MSK: # class for master key
    def __init__(self,h1,h2,gen1_h,gen2_h,s,t,u,v,A):
        self.h1 = h1
        self.h2 = h2
        self.gen1_h = gen1_h
        self.gen2_h = gen2_h
        self.s = s
        self.t = t
        self.u = u
        self.v = v
        self.A = A

class IPE: # inner product encryption realization
    @time_spent
    def __init__(self,G1,G2,dim): # init parametrs
        self.dim = dim # the length of input vectors, in our case 16, must be even number
        self.G1 = G1 # the generator of curve group (Authentication space group)
        self.G2 = G2 # the generator of twist group (Registration space group)
    @time_spent
    def KeyGen(self): # generation of msk
        s = gen_rand_vect(self.dim)
        t = gen_rand_vect(self.dim)
        u = gen_rand_vect(self.dim+2)
        v = gen_rand_vect(self.dim+2)
        A = matrix.rand_matrix(self.dim+4,1)
        print('\nRandom unimodular matrix:')
        matrix.print_matrix(A)
        h1 = rand.randint(2,q)
        h2 = rand.randint(2,q)
        gen1_h = [s[i]+h1*t[i] for i in range(self.dim)]
        gen2_h = [u[i]+h2*v[i] for i in range(self.dim+2)]
        return MSK(h1,h2,gen1_h,gen2_h,s,t,u,v,A)
    @time_spent
    def Registration(self,msk,v1): # generation of registration template
        r0 = rand.randint(2,q)
        reg_template = [r0, msk.h2*r0] + [msk.gen2_h[i]*r0 for i in range(self.dim+2)]
        f2 = v1[0]*msk.s[0]
        f3 = v1[0]*msk.t[0]
        for i in range(1,self.dim):
            f2 = f2+v1[i]*msk.s[i]
            f3 = f3+v1[i]*msk.t[i]
            reg_template[i+4] = reg_template[i+4]+v1[i]
        reg_template[2] = reg_template[2]-f2
        reg_template[3] = reg_template[3]-f3
        reg_template[4] = reg_template[4]+v1[0]
        for i in range(self.dim+4):
            reg_template[i] = self.G2.scalar_mul(matrix.format_number(reg_template[i],q))
        reg_template = self.sort(reg_template,matrix.inverse_matrix(msk.A))
        return reg_template
    @time_spent
    def Authentication(self,msk,v2):  # generation of authentication template
        r0 = rand.randint(2,q)
        auth_template = [0]*2
        auth_template.append(r0)
        auth_template.append(msk.h1*r0)
        for i in range(4,self.dim+4):
            auth_template.append(msk.gen1_h[i-4]*r0)
            auth_template[i] = auth_template[i]+v2[i-4]
        f0 = auth_template[2]*msk.u[0]
        f1 = auth_template[2]*msk.v[0]
        for i in range(1,self.dim+2):
            f0 = f0+auth_template[i+2]*msk.u[i]
            f1 = f1+auth_template[i+2]*msk.v[i]
        auth_template[0] = auth_template[0]- f0
        auth_template[1] = auth_template[1]- f1
        for i in range(self.dim+4):
            auth_template[i] = self.G1.scalar_mul(matrix.format_number(auth_template[i],q))
        auth_template = self.sort(auth_template,matrix.transpose_matrix(msk.A))
        return auth_template
    @time_spent
    def LogarithmTable(self): # generation of logarithm table of powers of e(G2,G1)
        A = bn256.optimal_ate(self.G2,self.G1)
        out1 = [A.exp(i) for i in range(self.dim, -1, -2)]
        B = bn256.optimal_ate(self.G2, inv(self.G1))
        out2 = [B.exp(i) for i in range(2, self.dim+1, 2)]
        out = out1+out2
        return out
    @time_spent
    def HammingDistance(self,reg_template,auth_template): # calculating Hamming distance
        e = bn256.optimal_ate(reg_template[0],auth_template[0])
        for i in range(1,self.dim+4):
            e = e.mul(bn256.optimal_ate(reg_template[i],auth_template[i]))
        return self.LogarithmTable().index(e)/self.dim
    def sort(self,template,operator):
        _template = []
        for i in range(self.dim+4):
            T = template[0].scalar_mul(0)
            for j in range(self.dim+4):
                if operator[i][j] < 0:
                    G = inv(template[j].scalar_mul(-int(operator[i][j])))
                else: G = template[j].scalar_mul(int(operator[i][j]))
                T = T.add(G)
            _template.append(T)
        return _template

@time_spent
def main():

    dim = 16

    G1 = bn256.curve_G
    G2 = bn256.twist_G

    #reg_vect = biometrics.procces(Image.open('./biometrics/reg.png'))
    #auth_vect = biometrics.procces(Image.open('./biometrics/auth.png'))

    reg_vect = gen_rand_vect(dim,1,True)
    auth_vect = gen_rand_vect(dim,1,True)

    assert len(reg_vect) == len(auth_vect)

    print('Registration vector:',reg_vect)
    print('Authentication vector:',auth_vect)

    myIPE = IPE(G1,G2,dim)

    msk = myIPE.KeyGen()
    reg_template = myIPE.Registration(msk,reg_vect)
    auth_template = myIPE.Authentication(msk,auth_vect)

    dist = myIPE.HammingDistance(reg_template,auth_template)

    print('Hamming distance:',HD(reg_vect,auth_vect))
    print('Hamming distance via homomorphic encryption:',dist)

if __name__ == '__main__': main()
