import random as rand

dim = 10
ord = 10

a = [rand.randint(0,ord) for _ in range(dim)]
b = [rand.randint(0,ord) for _ in range(dim)]

res1 = sum(a)*sum(b)
res2 = 0
for i in range(dim):
    for j in range(i+1):
        res2+=a[i]*b[i-j]

print(res1)
print(res2)
print(res1 == res2)
