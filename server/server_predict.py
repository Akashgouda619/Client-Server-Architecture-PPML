import pickle
import numpy as np
import time
import hickle as hkl

import sqlite3
import json
from Pyfhel import Pyfhel, PyPtxt
import base64
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../client')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../encryption')))

from shared_functions import getActivation
from encryption import decryptMatrix, encryptMatrix, encryptMatrixTo64, getEncodedParametersFromBytes, encrypted_dot_product, encodeMatrix, encodeMatrixToBytes

layerDims=[10, 47, 62, 67, 72, 62, 1]
activationFunctions = ["tanh", "tanh", "tanh", "sigmoid", "relu", "sigmoid"]

def getOutputLayer(encryptedInput, publickKey64, context64, relinKey64):
    HE = Pyfhel()
    HE.from_bytes_context(base64.b64decode(context64))
    HE.from_bytes_public_key(base64.b64decode(publickKey64))
    HE.from_bytes_relin_key(base64.b64decode(relinKey64))
    encryptedParams = getEncodedParameters(HE)
    outputLayer = l_LayerForwardEncrypted(encryptedInput, encryptedParams, layerDims, HE)
    return outputLayer


def getEncodedParameters(HE):
    # conn = sqlite3.connect('ppml.db')
    # cursor = conn.cursor()
    # cursor.execute('''
    #     SELECT encrypted_parameters FROM user_details WHERE id = 1
    # ''')
    # encryptedParameters = json.loads(cursor.fetchone()[0])
    # return encryptedParameters

    print("reading encrypted parameters...")
    timec = time.time()
    paramatersInBytes=hkl.load(open("/Users/tanishmalekar/Library/CloudStorage/OneDrive-BajajFinanceLimited/Desktop/Research Paper/client/encodedParameters.hkl", 'rb'))    
    print("Time for reading encoeded byte parameters: ", time.time() - timec)
    timec = time.time()
    encodedParameters = getEncodedParametersFromBytes(paramatersInBytes, HE)
    print("Time for getting encoded parameters: ", time.time() - timec)
    return encodedParameters

    # paramaters=pickle.load(open("/Users/tanishmalekar/Library/CloudStorage/OneDrive-BajajFinanceLimited/Desktop/Research Paper/deep-learning/model_details.pkl", 'rb'))
    # return paramaters

    # paramaters=pickle.load(open("/Users/tanishmalekar/Library/CloudStorage/OneDrive-BajajFinanceLimited/Desktop/Research Paper/deep-learning/model_details.pkl", 'rb'))
    # return encodeParameters(paramaters, HE)


def encodeParameters(parameters, HE):
    print("encoding parameters...")
    encodedParameters = {}
    for key, value in parameters.items():
        encodedParameters[key] = encodeMatrixToBytes(value, HE)
    print("encoding done.")
    print(encodedParameters["W1"])
    print(type(encodedParameters["W1"][0][0]))
    return encodedParameters


def l_LayerForwardEncrypted(encryptedInput, encryptedParams, layerdims, HE):
    L =  len(layerdims)-1
    A = encryptedInput

    for l in range(1,L+1):
        A_prev = A
        print("layer: ", l)
        A = forward(A_prev, encryptedParams["W"+str(l)], encryptedParams["b"+str(l)], activationFunctions[l-1], HE)

    return A


def forward(A_prev, W, b, activation, HE):
    
    
    Z = np.add(encrypted_dot_product(A_prev, W, HE), b)


    A = calculateActivationFunction(Z, activation)

    return A


def add_random_noise(Z):
    noise_indices = []
    
    # Flatten Z and compute min and max values
    Z_flat = Z.flatten()
    min_val, max_val = Z_flat.min(), Z_flat.max()
    
    Z_noisy = []
    for i in range(len(Z)):
        if np.random.rand() > 0.5:  # Randomly decide whether to add noise
            noise = np.random.uniform(min_val, max_val, 1)  # Generate random value within the range
            Z_noisy.append(noise)  # Append noise
            noise_indices.append(len(Z_noisy))  # Record index where noise was added
        Z_noisy.append(Z[i])
    
    return np.array(Z_noisy), noise_indices

def remove_noise(Z, noise_indices):
    Z_cleaned = np.delete(Z, noise_indices, 0)
    return Z_cleaned


def calculateActivationFunction(Z, activation):
    # Z_noisy, noise_indices = add_random_noise(Z)
    # activationFromClient= getActivationFromClient(Z_noisy, activation)
    # activationFromClient_cleaned = remove_noise(activationFromClient, noise_indices)
    # return activationFromClient_cleaned
    return getActivationFromClient(Z, activation)


def getActivationFromClient(Z, activation):
    # TODO: Call client to get activation
    return getActivation(Z, activation)


def initializeServer(publickKey64, context64, relinKey64):
    print("hi from server")
    # conn = sqlite3.connect('ppml.db')
    # cursor = conn.cursor()
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS user_details
    #     (id INTEGER PRIMARY KEY,
    #     encrypted_parameters TEXT)
    # ''')

    HE = Pyfhel()
    HE.from_bytes_context(base64.b64decode(context64))
    HE.from_bytes_public_key(base64.b64decode(publickKey64))
    HE.from_bytes_relin_key(base64.b64decode(relinKey64))

    paramaters=pickle.load(open("/Users/tanishmalekar/Library/CloudStorage/OneDrive-BajajFinanceLimited/Desktop/Research Paper/deep-learning/model_details.pkl", 'rb'))
  
    curr_time = time.time()
    encodedParameters = encodeParameters(paramaters, HE)
    print("Encoding time: ", time.time() - curr_time)
    # with open('encrypted_parameters.pkl', 'wb') as file:
    #     pickle.dump(encryptedParameters, file)
    print("dumping parameters...")
    curr_time = time.time()
    hkl.dump(encodedParameters, 'encodedParameters.hkl', mode='wb')
    print("dumping time: ", time.time() - curr_time)
    print("dumping done.")

   
    # encryptedParametersJSON = json.dumps(encryptedParameters)
    
    # cursor.execute('''
    #     INSERT INTO user_details (id, encrypted_parameters)
    #     VALUES (?, ?)
    # ''', (1, encryptedParametersJSON ))