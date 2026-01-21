# Project Documentation: Privacy-Preserving Machine Learning (PPML) System

## 1. Project Workflow
The system follows a **Client-Server Architecture** designed to keep patient data private at all times.

### Step-by-Step Flow:
1.  **User Input (Client)**: The doctor/user enters patient data (e.g., Age, Blood Pressure) into the Dashboard.
2.  **Encryption (Client)**:
    *   The browser (conceptually) or client-side logic generates a **Public/Private Key Pair**.
    *   The input numbers are converted into **Ciphertext** (gibberish strings) using the Public Key.
    *   *Note: In our simulation mode, this is visualized in the logs.*
3.  **Transmission**: The **Ciphertext** (NOT the real numbers) is sent to the Backend Server via an API request.
4.  **Secure Computation (Server)**:
    *   The Server receives the encrypted vector.
    *   It performs **Linear Operations** (Matrix Multiplication) using its pre-trained Model Weights.
    *   The result is a new Encrypted Vector (the "pre-activation" values).
5.  **Hybrid Protocol (Ping-Pong)**:
    *   Since the Server cannot perform non-linear functions (like Sigmoid) on encrypted data easily, it sends the intermediate encrypted result back to the Client.
    *   The Client **Decrypts** it, applies the **Activation Function** (e.g., Sigmoid), re-encrypts it, and sends it back (or finalizing the prediction).
6.  **Final Result**: The Client receives the final encrypted prediction, decrypts it using the Private Key, and displays the Risk Score (e.g., "85%") on the screen.

---

## 2. Tools & Technologies Used

### Frontend (User Interface)
*   **Next.js (React Framework)**: Used to build the interactive dashboard. It allows for fast, server-rendered pages and a smooth user experience.
*   **Tailwind CSS**: A utility-first CSS framework used for styling. It gives the app its modern "glassmorphism" look, gradients, and responsive layout.
*   **Lucide React**: Provides the beautiful icons (Shield, Heart, Lock) used in the UI.
*   **TypeScript**: Ensures code safety by defining strict types (e.g., ensuring `features` passed to the API are always numbers).

### Backend (The "Brain")
*   **FastAPI**: A high-performance Python web framework. It handles the HTTP requests (POST /predict) and connects the frontend to the ML logic.
*   **Uvicorn**: An ASGI server that runs the FastAPI application.
*   **Pickle**: Used to serialize and load the trained Machine Learning models (`.pkl` files).
*   **NumPy**: The fundamental package for scientific computing. It handles all the matrix math (dot products) for the Neural Network.

### Machine Learning & Cryptography
*   **Scikit-Learn**: Used to generate the synthetic training datasets and initially train the models.
*   **Pyfhel (Python For Homomorphic Encryption Libraries)**:
    *   This is the core "Magic" tool.
    *   It implements **CKKS (Cheon-Kim-Kim-Song)**, a Homomorphic Encryption scheme specifically designed for floating-point numbers (perfect for ML).
    *   It allows the server to add and multiply numbers while they remain encrypted.
*   **Mock Encryption Module**: A fallback tool we built. If `Pyfhel` fails to install (common on Windows without C++ tools), this module simulates the encryption workflow mathematically so the app keeps functioning for demonstration.

---

## 3. detailed Backend Computations

The "Brain" of the system is a **Multi-Layer Perceptron (MLP)** Neural Network adapted for encryption.

### The Problem
A Neural Network is composed of layers. Each layer does two things:
1.  **Linear**: `Z = (Weights * Input) + Bias`
2.  **Non-Linear**: `Output = Sigmoid(Z)`

**Homomorphic Encryption (CKKS)** can do step 1 (Add/Multiply) easily. It CANNOT do step 2 (Sigmoid) efficiently because Sigmoid is a complex curve.

### Your Solution: The "Split" Computation
We split the math between Server and Client:

#### A. Data Preparation (Startup)
1.  **Model Loading**: The Server loads the trained `weights` (W) and `biases` (b).
2.  **Encoding**: The Server converts these W and b matrices into **Plaintext Polynomials** (PyPtxt) so they can be multiplied with the encrypted input.

#### B. The Inference Loop
For each layer in the network:
1.  **Encrypted Dot Product (Server)**:
    *   Equation: `Z_enc = (W_encoded • Input_enc) + b_encoded`
    *   The server takes the Encrypted Input (`Input_enc`).
    *   It multiplies it by the Weights (`W_encoded`).
    *   It adds the Bias (`b_encoded`).
    *   **Result**: `Z_enc` is the encrypted calculation. The server has the result but *cannot read it*.
2.  **Activation Delegation (Client)**:
    *   The Server sends `Z_enc` to the Client.
    *   **Client Decrypts**: `Z = Decrypt(Z_enc)`
    *   **Client Activates**: `A = Sigmoid(Z)` (e.g., `1 / (1 + e^-z)`)
    *   **Client Encrypts**: `A_enc = Encrypt(A)`
    *   The Client sends `A_enc` back to the Server as the input for the next layer.

This cycle repeats until the final layer outputs the prediction probability!
