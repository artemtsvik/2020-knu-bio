'''
TODO:
    1) rand_matrix function
        a function that generates an invertable matrix over finite field
    2) inverse_matrix function
        a function that invert matrix over finite field
'''
def rand_matrix(dim,q):
    M = []
    for i in range(0,dim):
        M.append([])
        for j in range(0,dim):
            if i+1==j: M[i].append(1)
            elif i==dim-1 and j==0: M[i].append(1)
            else: M[i].append(0)
    print_matrix(M)
    return M

def inverse_matrix(A):
    dim = len(A)
    M = []
    for i in range(0,dim):
        M.append([])
        for j in range(0,dim):
            if i-1==j: M[i].append(1)
            elif i==0 and j==dim-1: M[i].append(1)
            else: M[i].append(0)
    print_matrix(M)
    return M

def print_matrix(M):
    string = '\n'
    for i in range(len(M)):
        stri = ''
        for j in range(len(M)):
            stri += str(M[i][j])+' '
        string += stri+'\n'
    print(string)
