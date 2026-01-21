import numpy as np
from Pyfhel import Pyfhel, PyCtxt, PyPtxt
import concurrent.futures
import base64
import hickle
import time

def initialize_HE():
    n_mults = 7
    ckks_params = {
    'scheme': 'CKKS',
    'n': 2**14,  # Polynomial modulus degree 4096
    'scale': 2**31,  # Scale factor
    'qi_sizes': [60] + [31]*n_mults + [60]  # Adjusted coefficient modulus bit sizes
}
    HE = Pyfhel()
    status = HE.contextGen(**ckks_params)
    print(status)
    HE.keyGen()
    HE.relinKeyGen()
    return HE

HE = initialize_HE()


def encodeMatrix(matrix, HE):
    matrix = np.array(matrix)
    PT = PyPtxt(pyfhel=HE)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        encoded_matrix = list(executor.map(PT.encode, matrix.flat))
    return np.array(encoded_matrix).reshape(matrix.shape)

def encodeMatrixToBytes(matrix, HE):
    matrix = np.array(matrix)
    PT = PyPtxt(pyfhel=HE)
    
    def encodeToBytes(value):
        encoded = PT.encode(value)
        # Convert to bytes and then to base64 string
        encoded_bytes = encoded.to_bytes(compr_mode='zstd')
        return encoded_bytes
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        encrypted_matrix = list(executor.map(encodeToBytes, matrix.flat))
    res = np.array(encrypted_matrix).reshape(matrix.shape)
    print(res.shape)
    print(matrix.shape)
    print(type(np.array(encrypted_matrix)))
    return res

def encryptMatrix(matrix, HE):
    matrix = np.array(matrix)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        encrypted_matrix = list(executor.map(HE.encrypt, matrix.flat))
    return np.array(encrypted_matrix).reshape(matrix.shape)

def encryptMatrixTo64(matrix, HE):
    matrix = np.array(matrix)
    
    def encrypt_and_encode(value):
        encrypted = HE.encrypt(value)
        # Convert to bytes and then to base64 string
        encrypted_bytes = encrypted.to_bytes(compr_mode='zstd')
        base64_str = base64.b64encode(encrypted_bytes).decode('utf-8')
        return base64_str
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        encrypted_matrix = list(executor.map(encrypt_and_encode, matrix.flat))
    
    return np.array(encrypted_matrix).reshape(matrix.shape)

def getEncodedParametersFromBytes(parametersBytes, HE):
    print("getting parameters from bytes...")
    encoded_parameters = {}
    
    for key, byte_matrix in parametersBytes.items():
        encoded_matrix = []
        for byte_value in byte_matrix.flat:
            # Convert bytes to PyPtxt object
            pyptxt_obj = PyPtxt(pyfhel=HE)
            pyptxt_obj.from_bytes(byte_value.item(), 'float')
            encoded_matrix.append(pyptxt_obj)
        
        encoded_parameters[key] = np.array(encoded_matrix).reshape(byte_matrix.shape)
    
    print("getting parameters from bytes done.")
    return encoded_parameters

def decryptMatrix(encrypted_matrix, HE):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        decrypted_matrix = list(executor.map(lambda x: HE.decrypt(x)[0], encrypted_matrix.flat))
    return np.array(decrypted_matrix).reshape(encrypted_matrix.shape)

def multiplePlain(x, y, HE):
    return HE.multiply_plain(x, y, in_new_ctxt=True)


def encrypted_dot_product(a, b, HE):
    timec = time.time()
    a = np.asarray(a)
    b = np.asarray(b)
    
    if a.ndim == 1 and b.ndim == 1:
        # Vector dot product
        if a.shape[0] != b.shape[0]:
            raise ValueError("Arrays must have the same length for vector dot product")
        products = np.array([multiplePlain(ai, bi, HE) for ai, bi in zip(a, b)])
        result = products[0]
        for product in products[1:]:
            result += product
        print(f"Dot product time: {time.time() - timec}")
        return result  # Return scalar result
    
    elif a.ndim == 2 and b.ndim == 1:
        # Matrix-vector multiplication
        if a.shape[1] != b.shape[0]:
            raise ValueError(f"Cannot multiply matrix of shape {a.shape} with vector of shape {b.shape}")
        result = np.empty(a.shape[0], dtype=object)
        for i in range(a.shape[0]):
            temp = multiplePlain(a[i, 0], b[0], HE)
            for k in range(1, a.shape[1]):
                temp += multiplePlain(a[i, k], b[k], HE)
            result[i] = temp
        print(f"Dot product time: {time.time() - timec}")
        return result
    
    elif a.ndim == 1 and b.ndim == 2:
        # Vector-matrix multiplication
        if a.shape[0] != b.shape[0]:
            raise ValueError(f"Cannot multiply vector of shape {a.shape} with matrix of shape {b.shape}")
        result = np.empty(b.shape[1], dtype=object)
        for j in range(b.shape[1]):
            temp = multiplePlain(a[0], b[0, j], HE)
            for k in range(1, a.shape[0]):
                temp += multiplePlain(a[k], b[k, j], HE)
            result[j] = temp
        print(f"Dot product time: {time.time() - timec}")
        return result
    
    elif a.ndim == 2 and b.ndim == 2:
        # Matrix multiplication
        if a.shape[1] != b.shape[0]:
            raise ValueError(f"Cannot multiply matrices of shape {a.shape} and {b.shape}")
        result = np.empty((a.shape[0], b.shape[1]), dtype=object)
        for i in range(a.shape[0]):
            for j in range(b.shape[1]):
                temp = multiplePlain(a[i, 0], b[0, j], HE)
                for k in range(1, a.shape[1]):
                    temp += multiplePlain(a[i, k], b[k, j], HE)
                result[i, j] = temp
        print(f"Dot product time: {time.time() - timec}")
        return result
    
    else:
        raise ValueError("Inputs must be 1-D or 2-D arrays")

if __name__ == '__main__':

    # a = np.array([3, 4])
    # b = np.array([5, 7])

    # res = encrypted_dot_product(a, b)
    # print(res)
    # print(np.dot(a, b))


    # encryptedA = [HE.encrypt(x).to_bytes(compr_mode='zstd') for x in a]
    # encryptedB = [HE.encrypt(x).to_bytes(compr_mode='zstd') for x in b]
    # encRes = np.dot(encryptedA, encryptedB)
    # decRes = decryptMatrix(encRes, HE)
    # res = np.dot(a, b)
    # print(decRes)
    # print(res)

    a = [2]
    PT = PyPtxt(pyfhel=HE)
    pt = PT.encode(a)
    print(type(pt.to_bytes(compr_mode='zstd')))


    # b = 5
    # ct = HE.encrypt(b)
    # res = HE.multiply_plain(ct, pt, in_new_ctxt=True)
    # res2 =HE.multiply_plain(res, pt, in_new_ctxt=True)
    # res3 = HE.multiply_plain(res2, pt, in_new_ctxt=True)
    # res4 = HE.multiply_plain(res3, pt, in_new_ctxt=True)

    # print(HE.decrypt(res4)[0])

    
    #hickle.dump(res, 'encrypted_value.hkl', mode='wb')



    # for i in range(0,7):
    #     res = res * encrypted
    #     res = ~(res)
    #     resa = resa * a
    # print(HE.decrypt(res)[0])
    # print(resa)



    # mat1 = np.array([[1, 2], [3, 4]])
    # mat2 = np.array([[5, 6], [7, 8]])
    # mat3 = np.array([[9, 10], [11, 12]])

    # eMat1 = encryptMatrix(mat1, HE)
    # eMat2 = encryptMatrix(mat2, HE)
    # eMat3 = encryptMatrix(mat3, HE)

    # # Perform dot product on encrypted matrices
    # res = encrypted_dot_product(eMat1, eMat2) + eMat3

    # dRes = decryptMatrix(res, HE)

    # print("Decrypted result:")
    # print(dRes)
    # print("\nExpected result:")
    # print(np.dot(mat1, mat2))