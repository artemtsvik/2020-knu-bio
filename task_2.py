import random as r

def random_vector(length): return [r.choice([-1,1]) for _ in range(length)]

def hamming_distance(v1,v2):
    return sum(v1[i] != v2[i] for i in range(len(v1))) / len(v1)

v1 = random_vector(16)
v2 = random_vector(16)

print('\nv1:',v1,'\nv2:',v2,'\nHamming distance:',hamming_distance(v1,v2))
