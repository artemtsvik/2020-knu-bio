import numpy as np
import random as rand

def rand_matrix(dim,q):
    L = [[0 for j in range(dim)] for i in range(dim)]
    U = [[0 for j in range(dim)] for i in range(dim)]
    for i in range(dim):
        L_row,U_col = two_vect_with_dot1(dim,q,i)
        for j in range(dim):
            L[i][j] = L_row[j]
            U[j][i] = U_col[j]
    out = mul_matrix(L,U)
    return out

def format_matrix(a,q):
    A = copy_matrix(a)
    dim = len(A)
    for i in range(dim):
        for j in range(dim):
            A[i][j] = int(format_number(A[i][j],q))
    return A

def format_number(number,q):
    if 0 <= number < q: return number
    elif number < 0: number = -number*(q-1)
    return int(number)

def two_vect_with_dot1(dim,q,iter):
    z = [0]*(dim-iter-1)
    v1 = [1]+[rand.randint(0,q) for _ in range(iter)]+z
    v2 = [1]+[rand.randint(0,q) for _ in range(iter)]+z
    v1[iter] = 1
    v2[iter] = 1
    for i in range(1,dim):
        v2[0] -= v1[i]*v2[i]
    return v1,v2

def det(A): return np.linalg.det(np.array(A))
def mul_matrix(A, B): return list(np.dot(np.array(A),np.array(B)))
def inverse_matrix(A): return list(np.linalg.inv(np.array(A)))
def transpose_matrix(A): return list(np.array(A).transpose())
def invT(A): return inverse_matrix(transpose_matrix(A))
def copy_matrix(M): return [[M[i][j] for j in range(len(M))] for i in range(len(M))]

def print_matrix(M):
    string = '\n'
    for i in range(len(M)):
        stri = '    '
        for j in range(len(M)):
            if M[i][j] >= 0: stri+=' '
            stri += str(int(M[i][j]))+' '
        string += stri+'\n\n'
    print(string)
