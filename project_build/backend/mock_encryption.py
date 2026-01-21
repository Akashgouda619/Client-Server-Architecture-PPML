import numpy as np
import pickle
import base64

# Mock Classes to simulate Pyfhel objects
class MockPyfhel:
    def __init__(self):
        self.context = "MOCK_CONTEXT"
        self.public_key = "MOCK_PK"
        self.relin_key = "MOCK_RELIN"
    
    def contextGen(self, **kwargs):
        return "success"
    
    def keyGen(self):
        pass
        
    def relinKeyGen(self):
        pass
        
    def encrypt(self, value):
        return value
        
    def decrypt(self, ciphertext):
        return np.array([ciphertext])
        
    def multiply_plain(self, ctxt, ptxt, in_new_ctxt=True):
        return ctxt * ptxt
        
    def add(self, ctxt1, ctxt2, in_new_ctxt=True):
        return ctxt1 + ctxt2

class MockCiphertext:
    def __init__(self, value):
        self.value = value

class MockPlaintext:
    def __init__(self, value):
        self.value = value

# Redefine the high-level functions from encryption.py to use numpy directy
# This allows the rest of main.py to run unchanged

def initialize_HE():
    print("[WARNING] Running in SIMULATION MODE (Mock Encryption).")
    print("[INFO] Real Homomorphic Encryption is disabled because Pyfhel is not installed.")
    return MockPyfhel()

def encodeMatrix(matrix, HE):
    return np.array(matrix) 

def encryptMatrix(matrix, HE):
    return np.array(matrix)

def decryptMatrix(matrix, HE):
    return np.array(matrix)

def encrypted_dot_product(W, A, HE):
    # Standard dot product for mock mode
    W = np.array(W)
    A = np.array(A)
    return np.dot(W, A)
