import numpy as np
from Pyfhel import Pyfhel, PyPtxt
import pandas as pd
from sklearn.preprocessing import StandardScaler
import time


import sys
import os
import base64

# Add the client directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../server')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../encryption')))

from server_predict import getOutputLayer, initializeServer
from encryption import decryptMatrix, encryptMatrix


def initialize_HE():
    n_mults = 10
    ckks_params = {
        'scheme': 'CKKS',
        'n': 2**15,
        'scale': 2**31,
        'qi_sizes': [60] + [31]*n_mults + [60]
    }
    HE = Pyfhel()
    HE.contextGen(**ckks_params)
    HE.keyGen()
    HE.relinKeyGen()
    return HE

#global in client
HE = initialize_HE()
HE.save_context("context")
HE.save_public_key( "pub.key")
HE.save_secret_key("sec.key")
HE.save_relin_key("relin.key")


def initiateConnection():
    publicKey = HE.to_bytes_public_key(compr_mode=u'zstd')
    publickKey64 = base64.b64encode(publicKey).decode('utf-8')
    context = HE.to_bytes_context(compr_mode='zstd')
    context64 = base64.b64encode(context).decode('utf-8')
    relinKey = HE.to_bytes_relin_key(compr_mode='zstd')
    relinKey64 = base64.b64encode(relinKey).decode('utf-8')

    sendInitializationToServer(publickKey64, context64, relinKey64)


def sendInitializationToServer(publickKey64, context64, relinKey64):
    initializeServer(publickKey64, context64, relinKey64)


def getPrediction(input):
    timec = time.time()
    encryptedInput = getEncryptedInput(input)
    print("Time for input encryption: ", time.time() - timec)

    publicKey = HE.to_bytes_public_key(compr_mode=u'zstd')
    publickKey64 = base64.b64encode(publicKey).decode('utf-8')
    context = HE.to_bytes_context(compr_mode='zstd')
    context64 = base64.b64encode(context).decode('utf-8')
    relinKey = HE.to_bytes_relin_key(compr_mode='zstd')
    relinKey64 = base64.b64encode(relinKey).decode('utf-8')


    outputLayer = getOutputLayerFromServer(encryptedInput, publickKey64, context64, relinKey64)
    return getResultFromOutputLayer(outputLayer)


def getEncryptedInput(input):
    encryptedInput = encryptMatrix(input, HE)
    return encryptedInput
    # return input

def getResultFromOutputLayer(outputLayer):
    decryptedOutputLayer = decryptMatrix(outputLayer, HE)
    print(decryptedOutputLayer)
    decryptedOutputLayer=decryptedOutputLayer.reshape(-1)
    predicted=np.where(decryptedOutputLayer>0.5, 1, 0)
    return predicted
    # print(outputLayer)
    # outputLayer=outputLayer.reshape(-1)
    # predicted=np.where(outputLayer>0.5, 1, 0)
    # return predicted

def getOutputLayerFromServer(encryptedInput, publickKey64, context64, relinKey64):
    # TODO: Call server to get output layer
    return getOutputLayer(encryptedInput, publickKey64, context64, relinKey64)

# def getActivation(Z, activation):
#     if activation== "sigmoid":
#         A=1/(1+np.exp(-Z))

#     if activation== "relu":
#         A = np.maximum(0,Z)

#     if activation=="tanh":
#         A = np.tanh(Z)

#     return A


def main():
    #dummy:
    data = pd.read_csv('/Users/tanishmalekar/Library/CloudStorage/OneDrive-BajajFinanceLimited/Desktop/Research Paper/deep-learning/dataset/Liver_disease_data.csv')
    X = data.drop(columns=['Diagnosis'])
    Y = data['Diagnosis']

    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    print("Actual: ", Y.values[0])
    timec = time.time()
    print("Predicted: ", getPrediction(X[0]))
    print("total Time taken: ", time.time() - timec)

    # initiateConnection()
    # n_mults = 10
    # ckks_params = {
    #     'scheme': 'CKKS',
    #     'n': 2**15,
    #     'scale': 2**31,
    #     'qi_sizes': [60] + [31]*n_mults + [60]
    # }
    # HE1 = Pyfhel()
    # HE1.contextGen(**ckks_params)
    # PT = PyPtxt(pyfhel=HE1)
    # a = 5
    # eA = PT.encode(a)
    # HE2 = Pyfhel()
    # HE2.contextGen(**ckks_params)
    # HE2.keyGen()
    # HE2.relinKeyGen()
    # b = 2
    # eB = HE2.encrypt(b)
    # res = HE1.multiply_plain(eB, eA)
    # print(HE1.decrypt(res))


    

if __name__ == "__main__":
    main()

