import lib.bn256 as bn256
import random


def inverse(point):
    return point.scalar_mul(bn256.order - 1)


def hamming_distance(vector1, vector2):
    return (len(vector1) - sum([i*j for (i, j) in zip(vector2, vector1)])) / (2 * len(vector1))


def get_binary_random_vector(size):
    return [random.choice([-1, 1]) for _ in range(size)]


def get_order_random_vector(size):
    return [random.randint(0, bn256.order) for _ in range(size)]


def convert_to_points(vector, generator):
    result = []
    inversed_generator = inverse(generator)
    for element in vector:
        if element == -1:
            result.append(inversed_generator)
        elif element == 1:
            result.append(generator)
    return result
