from resources import *
import lib.bn256 as bn256
import random
import time
import datetime


def split_output():
    print("---" * 113)


print("1. Included all needed libs.")

split_output()

print("2. Included function of hamming to verify yor final result.")

split_output()

v1 = get_binary_random_vector(16)
v2 = get_binary_random_vector(16)

print("3. Generated two vectors v1, v2 of [-1, 1] with length 16.")
print(f"v1 = {v1}.")
print(f"v2 = {v2}.")

split_output()

print("4. IPE: Key generation report:")

key_generation_time_before = datetime.datetime.now()
# инциализируем необходимые данные для дальнейшей работы
G1 = bn256.curve_G
G2 = bn256.twist_G


v1_converted = convert_to_points(v1, G2)
v2_converted = convert_to_points(v2, G1)
print(
    """
\ta. Transferred -1,1 to points. For v1 (registration template) you should use G2 generator,
\tfor v2 (authentication template) you should use G1 generator.
\tExample:
    \tv1 = -1, 1, -1, 1   v1points = invG2, G2, invG2, G2
    \tv2 =  1, 1, -1, 1   v2points = G1, G1, invG1, G1.
    """)

print(f"\tv1_converted = {v1_converted}.")
print(f"\tv2_converted = {v2_converted}.")


split_output()

s = get_order_random_vector(16)
print("\tb. Generated array 's' random keys with length equal to bio template length (16)")
print(f"\ts = {s}.")

split_output()

t = get_order_random_vector(16)
print("\tc. Generated array 't' random keys with length equal to bio template length (16)")
print(f"\tt = {t}.")

split_output()

u = get_order_random_vector(18)
print("\td. Generated array 'u' random keys with length equal to bio template length + 2 (18)")
print(f"\tu = {u}.")

split_output()

v = get_order_random_vector(18)
print("\te. Generated array 'v' random keys with length equal to bio template length + 2 (18)")
print(f"\tv = {v}.")

split_output()

h1 = random.randint(2, bn256.order)
H1 = G1.scalar_mul(h1)
print("\tf. Generated random h1 number and calculate point for G1 -> H1")
print(f"\th1 = {h1}.")
print(f"\tH1 = {H1}.")

split_output()

h2 = random.randint(2, bn256.order)
H2 = G2.scalar_mul(h2)
print("\tg. Generated random h2 number and calculate point for G2 -> H2")
print(f"\th2 = {h2}.")
print(f"\tH2 = {H2}.")

split_output()

gen1_h = [G1.scalar_mul(s[i]).add(H1.scalar_mul(t[i])) for i in range(16)]
print("\tj. Calculated gen1_h array keys: gen1_h[i] = s[i] * G1 + t[i] * H1")
print(f"\tgen1_h = {gen1_h}.")

split_output()

gen2_h = [G2.scalar_mul(u[i]).add(H2.scalar_mul(v[i])) for i in range(18)]
print(f"\ti. Calculated gen2_h array keys: gen2_h[i] = u[i] * G2 + v[i] * H2")
print(f"\tgen2_h = {gen2_h}.")

key_generation_time = datetime.datetime.now() - key_generation_time_before
split_output()
print(f"Key Generation time elapsed: {key_generation_time}.")
split_output()

print("5. IPE: Registration report:")

registration_time_before = datetime.datetime.now()

r0 = random.randint(2, bn256.order)
print(f"\t5.1. Generated random number r0")
print(f"\tr0 = {r0}.")

split_output()

reg_template = [G2.scalar_mul(r0), H2.scalar_mul(r0)] + [gen2_h[i].scalar_mul(r0) for i in range(18)]
print("\t5.2. Initialised array 'reg_template' of points with length 16 + 4.")

split_output()

print("\t5.3. Calculated reg_template[0] = r0 * G2")
print(f"\treg_template[0] = {reg_template[0]}.")

split_output()

print("\t5.4. Calculated reg_template[1] = r0 * H2")
print(f"\treg_template[1] = {reg_template[1]}.")

split_output()

temp_1 = v1_converted[0].scalar_mul(s[0])
temp_2 = v1_converted[0].scalar_mul(t[0])

for i in range(1, 16):
    temp_1 = temp_1.add(v1_converted[i].scalar_mul(s[i]))
    temp_2 = temp_2.add(v1_converted[i].scalar_mul(t[i]))

    reg_template[i + 4] = reg_template[i + 4].add(v1_converted[i])

reg_template[2] = reg_template[2].add(inverse(temp_1))
reg_template[3] = reg_template[3].add(inverse(temp_2))
reg_template[4] = reg_template[4].add(v1_converted[0])


print("\t5.5. Calculated for reg_template[2:18+2] = r0 * gen2_h[i], where i = 0 to 18")
print("\t5.6. Calculated for reg_template[2] = reg_template[2] - s[i] * v1points[i], where i = 0 to 16")
print("\t5.7. Calculated for reg_template[3] = reg_template[3] - t[i] * v1points[i], where i = 0 to 16")
print("\t5.8. Calculated for reg_template[4:16+4] = reg_template[4:16+4] + v1points[i], where i = 0 to 16")

print(f"\treg_template = {reg_template}.")

split_output()

print("\t5.9. reg_template is my encrypted bio template for registration.")

registration_time = datetime.datetime.now() - registration_time_before

split_output()
print(f"Registration time elapsed: {registration_time}.")
split_output()

print("6. IPE: Authentication report:")
authentication_time_before = datetime.datetime.now()

print("\t6.1. Generated random number r0 (it is another r0 then in previous step)")
another_r0 = random.randint(2, bn256.order)
print(f"\tanother_r0 = {another_r0}.")

split_output()

auth_template = [G1.scalar_mul(0), G1.scalar_mul(0), G1.scalar_mul(r0), H1.scalar_mul(r0)]

for i in range(4, 20):
    element = gen1_h[i - 4].scalar_mul(r0)
    auth_template.append(element.add(v2_converted[i - 4]))

temp_3 = auth_template[2].scalar_mul(u[0])
temp_4 = auth_template[2].scalar_mul(v[0])

for i in range(1, 18):
    temp_3 = temp_3.add(auth_template[i + 2].scalar_mul(u[i]))
    temp_4 = temp_4.add(auth_template[i + 2].scalar_mul(v[i]))

auth_template[0] = auth_template[0].add(inverse(temp_3))
auth_template[1] = auth_template[1].add(inverse(temp_4))

print("\t6.2. Initialised array 'auth_template' of points with length 16 + 4.")
print(f"\t6.3. Initialised auth_template[0,1] = 0 * G1 (we get 'infinitive points O, we will use in to add other points: O + P1 = P1')")
print("\t6.4. Calculated auth_template[2] = r0 * G1")
print("\t6.5. Calculated auth_template[3] = r0 * H1")
print("\t6.6. Calculated auth_template[4: 16+4] = (r0 * gen1_h[i]) + v2points[i], where i = 0 to 16")
print("\t6.7. Calculated for auth_template[0] = auth_template[0] - (u[i] * auth_template[i + 2]), where i = 0 to 16+2")
print("\t6.8. Calculated for auth_template[1] = auth_template[1] - (v[i] * auth_template[i + 2]), where i = 0 to 16+2")

split_output()

print("6.9. auth_template is my encrypted bio template for authentication")
print(f"\tauth_template NOW = {auth_template}.")
split_output()

print("\t6.10. Calculated Inner Product Encryption using reg_template and auth_template:")
print("\t\t6.10.1. e *= pairing(reg_template[i], auth_template[i]), where i = 0 to 16+4")

e = bn256.optimal_ate(reg_template[0], auth_template[0])
for i in range(1, 20):
    e = e.mul(bn256.optimal_ate(reg_template[i], auth_template[i]))

print(f"\t\te = {e}.")

split_output()

print("\t\t6.11.2. Next task is 8 after generate table of powers in taks 7.")

split_output()

print("7. IPE: Pre-computed table with powers of e(G2, G1), Exmaple of table t[0] = 1, t[1] = e(G2, G1)^1, t[1] = e(G2, G1)^2, t[1] = e(G2, G1)^3, ..., t[1] = e(G2, G1)^16.")
pairing_1 = bn256.optimal_ate(G2, G1)
pairing_2 = bn256.optimal_ate(G2, inverse(G1))

power_table = [pairing_1.exp(i) for i in range(16, -1, -2)] + [pairing_2.exp(i) for i in range(2, 17, 2)]
print(f"\tpower_table = {power_table}")

split_output()

print("8. Found result using pre-computed power table and use Hamming distance function to show result.")
result_hamming_distance = power_table.index(e) / 16

print(f"Result Hamming distance = {result_hamming_distance}.")
print(f"Initial Hamming distance: = {hamming_distance(v1, v2)}.")

authentication_time = datetime.datetime.now() - authentication_time_before

split_output()
print(f"Authentication time elapsed: {authentication_time}.")
split_output()
