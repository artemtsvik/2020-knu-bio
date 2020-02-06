# 2020-knu-bio
Crypto for Biometrics, K.Krutoy

My modification of IPE algorithm is a simple stirring of scalars in the degrees of ate pairing.

# the Algorithm

The idea is to generate a random system of linear equations with registration or authentication template coefficients and replace old coefficients with new linear combinations. It is equivalent to generate two invertible matrices and use it to the registration and authentication templates. Calculations showed that the second matrix must be the inverse of the first.

So after the ate pairings we'll see:

    e(reg_i*G2,auth_i*G1) ==> e(G2,G1) ^ (reg_i*auth_i)

Where reg_i and auth_i are the coefficients of registration and authentication templates respectively. Where:

    reg_0*auth_0 + reg_1*auth_1 + ... + reg_(dim+4)*auth_(dim+4) = Hamming distance (v1,v2)

The problem is that we can check what positions of v1,v2 are the same by calculating e(reg_i*G2,auth_i*G1) for the i's position.
We can replace coefitions reg_i, auth_i with their linear combinations in the next way:

    reg_i --> sum from j = 1 to dim+4 of alpha[j][i]*reg_j

    auth_i --> sum from j = 1 to dim+4 of beta[i][j]*auth_j

After direct calculations we'll see that the only thing that we must require is the following:

    matrix of alpha[j][i] = inverse of matrix of beta[i][j]

This procedure will mix our coefitions to avoid the problem.

TODO list:

0: Finish lib.matrix.py

0.1: rand_matrix function

0.2: inverse_matrix function

# some notes

The random matrix can be replaced with a certain invertible matrix.
