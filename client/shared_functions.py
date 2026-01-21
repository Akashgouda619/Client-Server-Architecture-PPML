import numpy as np
from Pyfhel import Pyfhel
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../encryption')))

from encryption import decryptMatrix, encryptMatrix


def getActivation(Z, activation):

    HE = Pyfhel()
    HE.load_context("context")
    HE.load_public_key( "pub.key")
    HE.load_secret_key("sec.key")
    HE.load_relin_key("relin.key")

    Z_decrypted = decryptMatrix(Z, HE)

    if activation== "sigmoid":
        A=1/(1+np.exp(-Z_decrypted))

    if activation== "relu":
        A = np.maximum(0,Z_decrypted)

    if activation=="tanh":
        A = np.tanh(Z_decrypted)

    return encryptMatrix(A, HE)


    # if activation== "sigmoid":
    #     A=1/(1+np.exp(-Z))

    # if activation== "relu":
    #     A = np.maximum(0,Z)

    # if activation=="tanh":
    #     A = np.tanh(Z)

    # return A