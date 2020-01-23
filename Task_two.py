import numpy as np


def hamming_distance(v1, v2):
    if len(v1) == len(v2):
        return 0.5*(len(v1)-np.dot(v1, v2))


random_16_vector = (np.random.choice([1, -1], (2, 16)))
print(random_16_vector)


print(hamming_distance(random_16_vector[0], random_16_vector[1]))