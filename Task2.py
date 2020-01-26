from random import randint

def gen_rand_vect(n):
    symb = [-1,1]
    v = []
    for i in range(n):
        v.append(symb[randint(0,1)])
    return v

def HD(x,y):
    assert len(x) == len(y)
    return (len(x) - sum([i*j for (i, j) in zip(y, x)]))/2

v1 = gen_rand_vect(16)
v2 = gen_rand_vect(16)

print(v2)
print(v1)
print(HD(v1,v2))
