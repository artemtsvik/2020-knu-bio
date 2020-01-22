import random
import lib.bn256 as bn256
print("2. Included bn256 module from lib directory.")


def slit_output():
    print("---" * 318)


slit_output()

r1 = random.randrange(2, bn256.order)
r2 = random.randrange(2, bn256.order)
r3 = random.randrange(2, bn256.order)

print("3. Generated three random numbers r1, r2, r3 in field Fp1 with order 2^256:")
print(r1, r2, r3, sep="\n")

slit_output()

G1 = bn256.curve_G
G2 = bn256.twist_G

T1 = G1.scalar_mul(r1)
print("4. Calculated: T1 = r1 * G1")
print(T1)

slit_output()

T2 = G1.scalar_mul(r2)
print("5. Calculated: T2 = r2 * G1")
print(T2)

slit_output()

T3 = G1.scalar_mul(r3)
print("6. Calculated: T3 = r3 * G1")
print(T3)

slit_output()

# использовал дальше идею с домножением на p^n - 1, так как с additive_inverse() и negate(),
# почему-то, последние спаривания E1 и E2 не получались равными.
TP = T1.add(T2).add(T3.scalar_mul(bn256.order - 1))
print("7. Calculated: TP = T1 + T2 - T3")
print(TP)

slit_output()

T4 = G2.scalar_mul(r1)
print("8. Calculated: T4 = r1 * G2")
print(T4)

slit_output()

T5 = G2.scalar_mul(r2)
print("9. Calculated: T5 = r2 * G3")
print(T5)

slit_output()

T6 = G2.scalar_mul(r3)
print("10. Calculated: T6 = r3 * G4")
print(T6)

slit_output()

TQ = T4.add(T5).add(T6.scalar_mul(bn256.order - 1))
print("11. Calculated: TQ = T4 + T5 - T6")
print(TQ)

slit_output()

tf = r1 + r2 - r3
print("12. Calculated: tf = r1 + r2 - r3")
print(tf)

slit_output()

E1 = bn256.optimal_ate(G2, G1).exp(tf * tf)
print("13. Calculated: E1 = pairing(G1, G2) ^ (tf * tf)")
print(E1)

slit_output()

E2 = bn256.optimal_ate(TQ, TP)
print("14. Calculated: E2 = pairing(TQ, TP)")
print(E2)

slit_output()

print("Проверяем равны ли E1 и E2: ")
print(E1 == E2)

slit_output()
