import numpy as np
from Pyfhel import Pyfhel
import base64

def initialize_HE():
    n_mults = 10
    ckks_params = {
        'scheme': 'CKKS',
        'n': 2**14,
        'scale': 2**31,
        'qi_sizes': [60] + [30]*n_mults + [60]
    }
    HE = Pyfhel()
    HE.contextGen(**ckks_params)
    HE.keyGen()
    HE.relinKeyGen()
    return HE

HE1 = initialize_HE()

publicKey = HE1.to_bytes_public_key(compr_mode=u'zstd')
publickKey64 = base64.b64encode(publicKey).decode('utf-8')
context = HE1.to_bytes_context(compr_mode='zstd')
context64 = base64.b64encode(context).decode('utf-8')
relinKey = HE1.to_bytes_relin_key(compr_mode='zstd')
relinKey64 = base64.b64encode(relinKey).decode('utf-8')


print(type(publickKey64))
HE2 = Pyfhel()
HE2.from_bytes_context(base64.b64decode(context64))
HE2.from_bytes_public_key(base64.b64decode(publickKey64))
HE2.from_bytes_relin_key(base64.b64decode(relinKey64))


a = 5
encA = HE2.encrypt(a)
decA = HE1.decrypt(encA)[0]
print(decA)

