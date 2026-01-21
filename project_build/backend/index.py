from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pickle
import numpy as np
import os
import sys

# Import local encryption module (ensure it's in path)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from encryption import initialize_HE, encryptMatrix, decryptMatrix, encrypted_dot_product, encodeMatrix

app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Changed to False for better '*' compatibility
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# --- Global State ---
HE = None
MODELS = {}
ERRORS = []

class PredictionRequest(BaseModel):
    features: List[float]

# --- PPML Logic ---

def load_pickle_model(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)
    
    # If the scaler exists and is a scikit-learn object, extract mean/scale
    # This allows us to run inference without scikit-learn installed
    if 'scaler' in data:
        scaler_obj = data['scaler']
        if hasattr(scaler_obj, 'mean_'):
            data['scaler'] = {
                'mean': scaler_obj.mean_,
                'scale': scaler_obj.scale_
            }
    return data

def prepare_server_parameters(parameters, he_context):
    """
    Simulates Server Initialization: Encodes weights/biases using HE Context.
    Returns dictionary of encoded parameters (PyPtxt).
    """
    encoded_params = {}
    L = len(parameters) // 2
    for l in range(1, L + 1):
        W = parameters['W' + str(l)]
        b = parameters['b' + str(l)]
        # Encode W and b
        encoded_params['W' + str(l)] = encodeMatrix(W, he_context)
        # For bias, we can encode it or encrypt it. Encoding (Plaintext) is standard for server params.
        # However, adding Plain + Cipher works in CKKS.
        encoded_params['b' + str(l)] = encodeMatrix(b, he_context)
    return encoded_params

def secure_inference(inputs, model_data, encoded_params, he_context):
    """
    Simulates the full Client-Server interaction.
    inputs: Raw plaintext features (Client)
    model_data: dict with metadata (activations, scaler)
    encoded_params: Server's encoded weights/biases
    he_context: Shared context (in real world, public key)
    """
    # 1. Client: Preprocess & Encrypt Inputs
    if 'scaler' in model_data:
        # Manual scaling to avoid sklearn dependency
        # scaler is expected to be a dict with 'mean' and 'scale'
        scaler = model_data['scaler']
        X_raw = np.array(inputs)
        X_scaled = (X_raw - scaler['mean']) / scaler['scale']
        X = X_scaled.reshape(-1, 1)
    else:
        X = np.array(inputs).reshape(-1, 1)
        
    # Encrypt
    enc_X = encryptMatrix(X, he_context)
    
    # 2. Server: Forward Pass
    activations = model_data['activations']
    L = len(encoded_params) // 2
    
    A = enc_X
    
    for l in range(1, L + 1):
        A_prev = A
        W = encoded_params['W' + str(l)]
        b = encoded_params["b" + str(l)]
        activation_type = activations[l-1]
        
        # Linear Step (Encrypted Dot Product + Encoded Bias)
        Z = np.add(encrypted_dot_product(W, A_prev, he_context), b)
        
        # Activation Step (Delegated to Client)
        Z_decrypted = decryptMatrix(Z, he_context)
        
        if activation_type == "sigmoid":
            # Safety clamp for exp to prevent overflow
            Z_decrypted = np.clip(Z_decrypted, -500, 500)
            A_plain = 1 / (1 + np.exp(-Z_decrypted))
        elif activation_type == "relu":
            A_plain = np.maximum(0, Z_decrypted)
        elif activation_type == "tanh":
            A_plain = np.tanh(Z_decrypted)
        else:
            A_plain = Z_decrypted
            
        # Re-encrypt
        A = encryptMatrix(A_plain, he_context)
        
    # 4. Final Result (Client Function)
    final_output = decryptMatrix(A, he_context)
    return final_output

# --- Initializer ---

def ensure_initialized():
    global HE, MODELS, ERRORS
    if HE is None:
        try:
            HE = initialize_HE()
        except Exception as e:
            ERRORS.append(f"HE Init Error: {str(e)}")
            return
        
    if not MODELS:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Diabetes
        try:
            model_path = os.path.join(base_dir, "models/diabetes_model.pkl")
            if not os.path.exists(model_path):
                ERRORS.append(f"File not found: {model_path}")
            else:
                data_d = load_pickle_model(model_path)
                params_d = prepare_server_parameters(data_d['parameters'], HE)
                MODELS['diabetes'] = {'meta': data_d, 'params': params_d}
        except Exception as e: 
            ERRORS.append(f"Diabetes load err: {str(e)}")
            
        # Heart
        try:
            model_path = os.path.join(base_dir, "models/heart_model.pkl")
            if not os.path.exists(model_path):
                ERRORS.append(f"File not found: {model_path}")
            else:
                data_h = load_pickle_model(model_path)
                params_h = prepare_server_parameters(data_h['parameters'], HE)
                MODELS['heart'] = {'meta': data_h, 'params': params_h}
        except Exception as e: 
            ERRORS.append(f"Heart load err: {str(e)}")

# --- Endpoints ---

@app.get("/")
def read_root():
    ensure_initialized()
    return {
        "status": "PPML Server Running", 
        "models_loaded": list(MODELS.keys()),
        "errors": ERRORS
    }

@app.post("/predict/diabetes")
def predict_diabetes(req: PredictionRequest):
    ensure_initialized()
    if 'diabetes' not in MODELS:
        raise HTTPException(status_code=503, detail="Diabetes model not loaded")
    
    features = req.features # Expecting 8 features
    if len(features) != 8:
        raise HTTPException(status_code=400, detail=f"Expected 8 features, got {len(features)}")
        
    try:
        model = MODELS['diabetes']
        result = secure_inference(features, model['meta'], model['params'], HE)
        # Result is like [[0.65]]
        prediction_prob = result.flatten()[0]
        prediction_class = 1 if prediction_prob > 0.5 else 0
        return {
            "prediction": int(prediction_class),
            "probability": float(prediction_prob),
            "privacy_status": "Encrypted (CKKS)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/heart")
def predict_heart(req: PredictionRequest):
    ensure_initialized()
    if 'heart' not in MODELS:
        raise HTTPException(status_code=503, detail="Heart model not loaded")
    
    features = req.features # Expecting 13 features
    if len(features) != 13:
        raise HTTPException(status_code=400, detail=f"Expected 13 features, got {len(features)}")
        
    try:
        model = MODELS['heart']
        result = secure_inference(features, model['meta'], model['params'], HE)
        prediction_prob = result.flatten()[0]
        prediction_class = 1 if prediction_prob > 0.5 else 0
        return {
            "prediction_risk": int(prediction_class),
            "probability": float(prediction_prob),
            "privacy_status": "Encrypted (CKKS)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
