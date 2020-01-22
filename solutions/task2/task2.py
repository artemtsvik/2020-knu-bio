import numpy as np

POOL = [-1, 1]


def slit_output():
    print("---" * 20)


def generate_random_vector(size: int = 16):
    vector = np.array([np.random.choice(POOL) for _ in range(size)])
    return vector


def hamming_distance(vector1: np.array, vector2: np.array):
    if vector1.shape == vector2.shape and len(vector1.shape) == 1:
        vector_product = vector1 * vector2
        return np.count_nonzero(vector_product == -1) / vector_product.shape[0]
    else:
        raise ValueError("arrays have different length or not 1-dim")


v1 = generate_random_vector()
v2 = generate_random_vector()

print("2. Generated two random vectors v1 and v2 with length 16:")
print(v1)
print(v2)

slit_output()

print("3. Created \"hamming_distance\" function:")
print("""
    def hamming_distance(vector1: np.array, vector2: np.array):
        if vector1.shape == vector2.shape and len(vector1.shape) == 1:
            vector_product = vector1 * vector2
            return np.count_nonzero(vector_product == -1) / vector_product.shape[0]
        else:
            raise ValueError("arrays have different length or not 1-dim")
""")

slit_output()

hmd = hamming_distance(v1, v2)
print("4. Use \"hamming_distance\" function to calculate distance between v1 and v2")
print("\tit is equals to ", end="")
print(hmd)


