import numpy as np
import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# --- MLP Library (Based on server_training.py but cleaned up) ---

def initialize_parameters(layer_dims):
    np.random.seed(3)
    parameters = {}
    L = len(layer_dims)
    for l in range(1, L):
        parameters['W' + str(l)] = np.random.randn(layer_dims[l], layer_dims[l-1]) * np.sqrt(2. / layer_dims[l-1]) # He initialization
        parameters['b' + str(l)] = np.zeros((layer_dims[l], 1))
    return parameters

def sigmoid(Z):
    return 1 / (1 + np.exp(-Z)), Z

def relu(Z):
    return np.maximum(0, Z), Z

def forward_linear_activation(A_prev, W, b, activation):
    Z = np.dot(W, A_prev) + b
    if activation == "sigmoid":
        A, activation_cache = sigmoid(Z)
    elif activation == "relu":
        A, activation_cache = relu(Z)
    
    linear_cache = (A_prev, W, b)
    cache = (linear_cache, activation_cache)
    return A, cache

def L_model_forward(X, parameters, layer_configs):
    # layer_configs is a list of activation strings for each layer (excluding input)
    caches = []
    A = X
    L = len(parameters) // 2
    
    for l in range(1, L + 1):
        A_prev = A
        activation = layer_configs[l-1]
        W = parameters['W' + str(l)]
        b = parameters['b' + str(l)]
        A, cache = forward_linear_activation(A_prev, W, b, activation)
        caches.append(cache)
        
    return A, caches

def compute_cost(AL, Y):
    m = Y.shape[1]
    cost = -np.sum(np.multiply(Y, np.log(AL + 1e-8)) + np.multiply(1-Y, np.log(1-AL + 1e-8))) / m # Added epsilon
    return np.squeeze(cost)

def sigmoid_backward(dA, cache):
    Z = cache
    s = 1 / (1 + np.exp(-Z))
    dZ = dA * s * (1-s)
    return dZ

def relu_backward(dA, cache):
    Z = cache
    dZ = np.array(dA, copy=True)
    dZ[Z <= 0] = 0
    return dZ

def linear_backward(dZ, cache):
    A_prev, W, b = cache
    m = A_prev.shape[1]
    dW = np.dot(dZ, A_prev.T) / m
    db = np.sum(dZ, axis=1, keepdims=True) / m
    dA_prev = np.dot(W.T, dZ)
    return dA_prev, dW, db

def linear_activation_backward(dA, cache, activation):
    linear_cache, activation_cache = cache
    if activation == "relu":
        dZ = relu_backward(dA, activation_cache)
    elif activation == "sigmoid":
        dZ = sigmoid_backward(dA, activation_cache)
    
    dA_prev, dW, db = linear_backward(dZ, linear_cache)
    return dA_prev, dW, db

def L_model_backward(AL, Y, caches, layer_configs):
    grads = {}
    L = len(caches)
    m = AL.shape[1]
    Y = Y.reshape(AL.shape)
    
    dAL = - (np.divide(Y, AL + 1e-8) - np.divide(1 - Y, 1 - AL + 1e-8))
    
    current_cache = caches[L-1]
    activation = layer_configs[L-1]
    dA_prev_temp, dW_temp, db_temp = linear_activation_backward(dAL, current_cache, activation)
    grads["dA" + str(L-1)] = dA_prev_temp
    grads["dW" + str(L)] = dW_temp
    grads["db" + str(L)] = db_temp
    
    for l in reversed(range(L-1)):
        current_cache = caches[l]
        activation = layer_configs[l]
        dA_prev_temp, dW_temp, db_temp = linear_activation_backward(grads["dA" + str(l+1)], current_cache, activation)
        grads["dA" + str(l)] = dA_prev_temp
        grads["dW" + str(l+1)] = dW_temp
        grads["db" + str(l+1)] = db_temp
        
    return grads

def update_parameters(parameters, grads, learning_rate):
    L = len(parameters) // 2
    for l in range(L):
        parameters["W" + str(l+1)] = parameters["W" + str(l+1)] - learning_rate * grads["dW" + str(l+1)]
        parameters["b" + str(l+1)] = parameters["b" + str(l+1)] - learning_rate * grads["db" + str(l+1)]
    return parameters

def train_model(X, Y, layer_dims, layer_activations, learning_rate=0.0075, num_iterations=3000):
    parameters = initialize_parameters(layer_dims)
    
    for i in range(0, num_iterations):
        AL, caches = L_model_forward(X, parameters, layer_activations)
        cost = compute_cost(AL, Y)
        grads = L_model_backward(AL, Y, caches, layer_activations)
        parameters = update_parameters(parameters, grads, learning_rate)
        
        if i % 100 == 0:
            print ("Cost after iteration %i: %f" %(i, cost))
            
    return parameters

# --- Data Loading & Main Execution ---

def load_dataset(filename, target_col_index=-1):
    # Load Real Dataset from CSV
    print(f"Loading {filename}...")
    try:
        df = pd.read_csv(filename)
        data = df.values
        X = data[:, :target_col_index]
        y = data[:, target_col_index]
        y = y.reshape(1, -1)
        X = X.T
        return X, y
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None, None

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_path, 'datasets')
    
    # 1. Diabetes Dataset
    # Expecting: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age, Outcome
    diabetes_path = os.path.join(data_dir, 'diabetes.csv')
    X_diabetes, y_diabetes = load_dataset(diabetes_path, target_col_index=8)
    
    if X_diabetes is not None:
        # Scale data
        scaler_d = StandardScaler()
        X_diabetes = scaler_d.fit_transform(X_diabetes.T).T
        
        print("Training Diabetes Model (Real Data)...")
        # Architecture: Input(8) -> Relu(16) -> Relu(8) -> Sigmoid(1)
        diabetes_dims = [8, 16, 8, 1]
        diabetes_activations = ["relu", "relu", "sigmoid"]
        diabetes_params = train_model(X_diabetes, y_diabetes, diabetes_dims, diabetes_activations, num_iterations=5000, learning_rate=0.005)
        
        # Save Model
        output_dir = os.path.join(base_path, '..', 'backend', 'models')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(os.path.join(output_dir, 'diabetes_model.pkl'), 'wb') as f:
            pickle.dump({
                'parameters': diabetes_params, 
                'dims': diabetes_dims, 
                'activations': diabetes_activations,
                'scaler': scaler_d  # SAVE THE SCALER
            }, f)
        print(f"Diabetes Model Saved to {output_dir}.")
    else:
        print("Skipping Diabetes training due to load error.")

    # 2. Heart Disease Dataset
    heart_path = os.path.join(data_dir, 'heart.csv')
    X_heart, y_heart = load_dataset(heart_path, target_col_index=-1)
    
    if X_heart is not None:
         # Scale data
        scaler_h = StandardScaler()
        X_heart = scaler_h.fit_transform(X_heart.T).T
        
        print("Training Heart Disease Model (Real Data)...")
        n_features = X_heart.shape[0]
        heart_dims = [n_features, 20, 10, 1] 
        heart_activations = ["relu", "relu", "sigmoid"]
        heart_params = train_model(X_heart, y_heart, heart_dims, heart_activations, num_iterations=5000, learning_rate=0.005)
        
        output_dir = os.path.join(base_path, '..', 'backend', 'models')
        with open(os.path.join(output_dir, 'heart_model.pkl'), 'wb') as f:
             pickle.dump({
                 'parameters': heart_params, 
                 'dims': heart_dims, 
                 'activations': heart_activations,
                 'scaler': scaler_h  # SAVE THE SCALER
             }, f)
        print(f"Heart Model Saved to {output_dir}.")
    else:
        print("Skipping Heart training due to load error.")

    print("Done! All available models trained.")

if __name__ == "__main__":
    main()
