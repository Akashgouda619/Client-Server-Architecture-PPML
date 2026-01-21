# 🧬 Privacy-Preserving Liver Disease Prediction with Homomorphic Encryption

[📄 Research Paper](https://drive.google.com/file/d/1cWSbJfrUPq2okGLezd5frDsTuqPGLJ18/view)

A distributed **client–server framework** for privacy-preserving medical inference that integrates **CKKS Homomorphic Encryption**, **RPC-based communication**, and **multithreading**. The system achieves secure inference on sensitive medical data with **only a 0.4% accuracy loss** compared to the plaintext model.

---

## 🔐 Key Features

- **End-to-End Privacy:** Client’s raw medical data remains encrypted throughout inference using CKKS homomorphic encryption.  
- **Model Confidentiality:** Server-side neural network parameters are fully protected, preventing exposure even during computation.  
- **Encrypted Neural Network Inference:** Supports **secure linear layers (matrix multiplications)** directly on encrypted data; non-linear activations are securely delegated to the client with controlled noise to maintain model privacy.
- **RPC Communication:** Reliable, low-latency client–server interaction facilitates encrypted inference.  
- **Multithreading & Parallelization:** Neural network computations are parallelized for faster encrypted inference.  
- **High Accuracy:** Achieves **88.8% accuracy on encrypted inference** vs. 89.2% baseline (only 0.4% drop), demonstrating minimal performance loss under encryption.  
- **Performance:** Average inference time ~89.6 seconds with <200ms/layer communication overhead on 1Gbps, optimized for encrypted matrix operations.

---

## 🧪 Dataset

- **Records:** 1,700  
- **Features:** Age, Gender, BMI, Smoking, Alcohol Consumption, Diabetes, Hypertension, Genetic Risk, Physical Activity, Liver Function Tests  
- **Target:** Binary classification (liver disease diagnosis)  

---

## 🧠 Model Architecture

| Layer  | Activation | Units |
|--------|------------|-------|
| 1      | Tanh       | 47    |
| 2      | Tanh       | 62    |
| 3      | Sigmoid    | 67    |
| 4      | ReLU       | 72    |
| 5      | Sigmoid    | 62    |
| Output | Sigmoid    | 1     |

Hyperparameters were tuned using **random search** to balance accuracy and efficiency.  

---

## 🔐 CKKS Encryption Configuration

| Parameter                  | Value        |
|----------------------------|--------------|
| Scheme                     | CKKS         |
| Polynomial Modulus Degree  | 16,384       |
| Scale Factor               | 2³¹          |
| Coefficient Modulus Sizes  | [60, 30, …, 30, 60] (12 levels) |

---

## 🔁 Protocol Workflow

1. **Server Initialization**  
   - Pre-encodes model weights and biases as CKKS plaintext (no encryption keys required at this stage).  
   - Serializes encoded parameters into compact byte objects for efficient storage and reuse.  
   - ⚡ Parallelized with **multithreading**, reducing computational overhead.  

2. **Client Initialization**  
   - Generates encryption keys (public, private, relin).  
   - Keys remain local to the client; the server never has access.  

3. **Prediction Phase (Neural Network Inference)**  
   - **Input Encryption:** Client encrypts feature vectors and sends them to the server via **RPC**.  
   - **Layer Computation:** For each layer of the neural network, the server performs encrypted matrix multiplications with pre-encoded weights and biases.  
   - **Non-linear Activations:** Since activations (ReLU, sigmoid, tanh) cannot be applied directly on encrypted data, the server securely delegates intermediate results to the client.  
     - The client decrypts, applies the activation, re-encrypts, and sends results back.  
     - Controlled noise is added by the server to prevent reverse-engineering of the model.  
   - **Final Prediction:** Once the last layer is computed, the encrypted output is sent back to the client for decryption, yielding the disease prediction.  

---

## ⚙️ Performance

| Stage                    | Time (s) |
|---------------------------|----------|
| Input Encryption          | 0.23     |
| Parameter Deserialization | 14.25    |
| Layer 1 Computation       | 5.36     |
| Layer 2 Computation       | 13.08    |
| Layer 3 Computation       | 18.09    |
| Layer 4 Computation       | 19.18    |
| Layer 5 Computation       | 16.95    |
| Output Layer              | 2.47     |
| **Total Inference Time**  | **89.61** |

- **Encrypted Accuracy:** 88.8%  
- **Plaintext Accuracy:** 89.2%  
- **Accuracy Loss:** 0.4%  
- **Communication Overhead:** <200ms/layer on 1Gbps  

---

## 🔭 Future Work

- Hardware acceleration (GPU/FHE-specific hardware)  
- Improved noise management for tighter accuracy preservation  
- Integration with **Federated Learning** for cross-institution training  
- Scaling to more complex models and larger datasets  

---

## 👨‍💻 Authors

- **Tanish Malekar** – Vellore Institute of Technology  
- **Shrey Parekh** – D.J. Sanghvi College of Engineering  
- **Deep Kotecha** – Vellore Institute of Technology  
- **Yokesh Babu** – Vellore Institute of Technology  

---

## 📄 License

This project is intended for **academic and research purposes**. For commercial applications, please contact the authors.  
