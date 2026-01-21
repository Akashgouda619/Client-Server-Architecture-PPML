# 🛡️ SecureInfer: Privacy-Preserving Health Prediction

**SecureInfer** is a state-of-the-art Client-Server system designed for secure medical inference. It uses **Homomorphic Encryption (CKKS scheme)** to allow diagnostic predictions (Diabetes and Heart Disease) to be performed on encrypted data, ensuring that sensitive patient information is never exposed to the server in plaintext.

---

## 🚀 Project Overview

In traditional cloud-based ML, the user must share their raw data with the server. **SecureInfer** breaks this paradigm by:
1. **Encrypting** data on the client side.
2. **Processing** the encrypted data using the server's encoded weights.
3. **Decrypting** the result only on the client side.

This ensures **End-to-End Privacy** for the user and **Model Security** for the service provider.

---

## 🛠️ Technology Stack

- **Frontend**: Next.js 15, Framer Motion, Lucide React, Tailwind CSS.
- **Backend**: FastAPI (Python), NumPy.
- **Encryption**: Homomorphic Encryption (CKKS) via Pyfhel (with Mock/Simulation fallback for serverless environments).
- **Deployment**: Vercel.

---

## 📂 Project Structure

This repository is organized as a monorepo:

- `/project_build/frontend`: The Next.js web dashboard.
- `/project_build/backend`: The FastAPI inference engine.
- `/project_build/docs`: Comprehensive project documentation and academic reports.
- `/project_build/training`: Scripts used for training the Diabetes and Heart Disease models.

---

## 🔧 Deployment to Vercel

For detailed deployment instructions, please refer to:
👉 **[project_build/DEPLOY_VERCEL.md](./project_build/DEPLOY_VERCEL.md)**

---

## 🎓 Academic Context
This project was developed as a comprehensive demonstration of **Client-Server Architecture in PPML**. It achieves high accuracy (Diabetes: ~76%, Heart: ~85%) with zero privacy loss during computation.
