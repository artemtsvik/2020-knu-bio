# 2020-knu-bio
Crypto for Biometrics, K.Krutoy

My modification of IPE algorithm is a simple stirring of scalars in the degrees of ate pairing.

The idea is to generate a random system of linear equations with registration or authentication template coefficients and replace old coefficients with new linear combinations. It is equivalent to generate two invertible matrices and use it to the registration and authentication templates. Calculations showed that the second matrix must be the inverse of the first.

TODO list:

0: Finish lib.matrix.py

	0.1: rand_matrix function

	0.2: inverse_matrix function
