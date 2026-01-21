import numpy as np
import concurrent.futures
import base64
import time
import sys
import os

# Try to import Pyfhel, otherwise fallback to mock
try:
    from Pyfhel import Pyfhel, PyCtxt, PyPtxt
    USE_MOCK = False
    print("Pyfhel imported successfully. Using Real Encryption.")
except ImportError:
    USE_MOCK = True
    print("Pyfhel not found. Switching to Mock Encryption.")

if USE_MOCK:
    from mock_encryption import initialize_HE, encodeMatrix, encryptMatrix, decryptMatrix, encrypted_dot_product
else:
    # --- Real Implementation ---
    
    def initialize_HE():
        n_mults = 7
        ckks_params = {
            'scheme': 'CKKS',
            'n': 2**14,  # Polynomial modulus degree 16384
            'scale': 2**31,  # Scale factor
            'qi_sizes': [60] + [31]*n_mults + [60]  # Adjusted coefficient modulus bit sizes
        }
        HE = Pyfhel()
        HE.contextGen(**ckks_params)
        HE.keyGen()
        HE.relinKeyGen()
        return HE

    def encodeMatrix(matrix, HE):
        matrix = np.array(matrix)
        PT = PyPtxt(pyfhel=HE)
        # Simplify parallelization for stability
        encoded_matrix = [PT.encode(x) for x in matrix.flat]
        return np.array(encoded_matrix).reshape(matrix.shape)

    def encryptMatrix(matrix, HE):
        matrix = np.array(matrix)
        encrypted_matrix = [HE.encrypt(x) for x in matrix.flat]
        return np.array(encrypted_matrix).reshape(matrix.shape)

    def decryptMatrix(encrypted_matrix, HE):
        # Handle cases where input might be scalar or list
        if hasattr(encrypted_matrix, 'flat'):
             decrypted = [HE.decrypt(x)[0] for x in encrypted_matrix.flat]
             return np.array(decrypted).reshape(encrypted_matrix.shape)
        else:
             # Single value
             return np.array([HE.decrypt(encrypted_matrix)[0]])

    def multiplePlain(x, y, HE):
        return HE.multiply_plain(x, y, in_new_ctxt=True)

    def encrypted_dot_product(a, b, HE):
        # a: Matrix (W), b: Vector (A_prev)
        # Standard Matrix * Vector
        
        # Ensure numpy
        a = np.array(a)
        b = np.array(b)
        
        if a.ndim == 2 and (b.ndim == 1 or (b.ndim==2 and b.shape[1]==1)):
            # Matrix-Vector Multiplication
            # Rows of A dot Vector B
            rows = a.shape[0]
            cols = a.shape[1]
            
            # Flatten B if it's (N,1)
            b_flat = b.flatten()
            
            result = np.empty((rows, 1), dtype=object)
            
            for i in range(rows):
                # Dot product of Row A[i] and Vector B
                # Initialize with first element
                accum = HE.multiply_plain(a[i, 0], b_flat[0], in_new_ctxt=True) 
                
                # Check for Relinearization need? CKKS usually needs it after Mult.
                # But here we are doing MultPlain (Cipher * Plain), which increases scale but not size usually?
                # Pyfhel manages this.
                
                for j in range(1, cols):
                    prod = HE.multiply_plain(a[i, j], b_flat[j], in_new_ctxt=True)
                    accum = accum + prod # Homomorphic Addition
                    
                result[i, 0] = accum
            return result
            
        else:
            raise ValueError(f"Shape mismatch or unsupported dimensions: {a.shape} vs {b.shape}")