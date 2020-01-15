#!/usr/bin/python

import random
import bn256
import numpy as np



def getHemmingDist(product, m_TemplateSize):
    HammingDistance = (float)(m_TemplateSize - product) / 2
    HammingDistance /= m_TemplateSize
    print("HammingDistance: ", HammingDistance)

x = [1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1]
y = [-1, -1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1]


a = 0
for i in range(16):
    a += x[i] * y[i]

print("Product", a)
getHemmingDist(a, 16)

def getG1template(point):
    if point < 0: 
        tmp = bn256.curve_point(bn256.curve_G.x, bn256.curve_G.y.additive_inverse(), bn256.curve_G.z)
    else:
        tmp = bn256.curve_point(bn256.curve_G.x, bn256.curve_G.y, bn256.curve_G.z)
    return tmp

def getG2template(point): 
    tmp = bn256.curve_twist(bn256.twist_G.x, bn256.twist_G.y, bn256.twist_G.z)
    if point < 0:
        tmp.negate()
    return tmp

m_TemplateLength = 16

m_DataPtrSecret = [int] * (m_TemplateLength + 4)
m_DataPtrChipher = [int] * (m_TemplateLength + 4)

m_h = 0
m_barh = 0
m_gT = 0

m_hi = [int] * m_TemplateLength
m_s = [int] * m_TemplateLength
m_t = [int] * m_TemplateLength
m_barhi = [int] * (m_TemplateLength + 2)
m_u = [int] * (m_TemplateLength + 2)
m_v = [int] * (m_TemplateLength + 2)

# Gen master key
gh = random.randrange(2, bn256.order)
bargh = random.randrange(2, bn256.order)

m_h = bn256.g1_scalar_base_mult(gh)
m_barh = bn256.g2_scalar_base_mult(bargh)


for j in range(m_TemplateLength):
    tmp = 0
    m_s[j] = random.randrange(2, bn256.order)
    m_t[j] = random.randrange(2, bn256.order)

    m_hi[j] = bn256.g1_scalar_base_mult(m_s[j])
    tmp = m_h.scalar_mul(m_t[j])
    m_hi[j] = m_hi[j].add(tmp)

for j in range(m_TemplateLength + 2):
    tmp = 0
    m_u[j] = random.randrange(2, bn256.order)
    m_v[j] = random.randrange(2, bn256.order)

    m_barhi[j] = bn256.g2_scalar_base_mult(m_u[j])
    tmp = m_barh.scalar_mul(m_v[j])
    m_barhi[j] = m_barhi[j].add(tmp)


# Gen chiper text

r0 = random.randrange(2, bn256.order)

template_g = [int] * m_TemplateLength

m_DataPtrChipher[0] = bn256.g1_scalar_base_mult(0)
m_DataPtrChipher[1] = bn256.g1_scalar_base_mult(0)
m_DataPtrChipher[2] = bn256.g1_scalar_base_mult(r0)
m_DataPtrChipher[3] = m_h.scalar_mul(r0)

for j in range(m_TemplateLength):
    tmp_2 = getG1template(y[j])
    tmp_1 = m_hi[j].scalar_mul(r0)
    m_DataPtrChipher[j + 4] = tmp_1.add(tmp_2)

for j in range(m_TemplateLength + 2):
    tmp_1 = m_DataPtrChipher[j + 2].scalar_mul(m_u[j])
    tmp_2 = m_DataPtrChipher[j + 2].scalar_mul(m_v[j])

    inv_point_1 = bn256.curve_point(tmp_1.x, tmp_1.y.additive_inverse(), tmp_1.z)
    inv_point_2 = bn256.curve_point(tmp_2.x, tmp_2.y.additive_inverse(), tmp_2.z)

    m_DataPtrChipher[0] = m_DataPtrChipher[0].add(inv_point_1)
    m_DataPtrChipher[1] = m_DataPtrChipher[1].add(inv_point_2)

# Gen secret key

barr0 = random.randrange(2, bn256.order)

template_barg = [int] * m_TemplateLength
acc_sy0 = [int] * m_TemplateLength
acc_ty0 = [int] * m_TemplateLength

m_DataPtrSecret[0] = bn256.g2_scalar_base_mult(barr0)
m_DataPtrSecret[1] = m_barh.scalar_mul(barr0)

for j in range(m_TemplateLength + 2):
    m_DataPtrSecret[j + 2] = m_barhi[j].scalar_mul(barr0)


for j in range(m_TemplateLength):
    template_barg[j] = getG2template(x[j])
    acc_sy0[j] = template_barg[j].scalar_mul(m_s[j])
    acc_ty0[j] = template_barg[j].scalar_mul(m_t[j])

    acc_sy0[j].negate()
    acc_ty0[j].negate()

    m_DataPtrSecret[2] = m_DataPtrSecret[2].add(acc_sy0[j])
    m_DataPtrSecret[3] = m_DataPtrSecret[3].add(acc_ty0[j])

    m_DataPtrSecret[j + 4] = m_DataPtrSecret[j + 4].add(template_barg[j])


# Gen DLog table

m_DlogLength = m_TemplateLength + 2
m_DlogTable = [int] * m_DlogLength

ep = bn256.gfp_12(bn256.gfp_6_zero, bn256.gfp_6_one)

m_gT = bn256.optimal_ate(bn256.twist_G, bn256.curve_G)

for j in range(m_DlogLength):
    m_DlogTable[j] = ep
    ep = ep.mul(m_gT)

	
# Final step

e = bn256.gfp_12(bn256.gfp_6_zero, bn256.gfp_6_one)
e_acc = 0

for j in range(m_TemplateLength + 4):
    e_acc = bn256.optimal_ate(m_DataPtrSecret[j], m_DataPtrChipher[j])
    e = e.mul(e_acc)

e2 = bn256.gfp_12(bn256.gfp_6_zero, bn256.gfp_6_one)

for j in range(m_DlogLength):
    if m_DlogTable[j] == e:
        print(j)
        getHemmingDist(j, m_TemplateLength)
        exit(0)


print("Something wrong")

exit(1)
