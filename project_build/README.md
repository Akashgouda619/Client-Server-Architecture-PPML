# Privacy-Preserving ML Dashboard

This project demonstrates a Client-Server architecture for Privacy-Preserving Machine Learning (PPML) using Homomorphic Encryption (CKKS).

## Components

1.  **Backend (FastAPI)**: Simulates the Server (Model Owner) and Client (Data Owner). Uses `Pyfhel` for encryption.
    *   Models: Diabetes Prediction (Binary), Academic Performance (Binary).
2.  **Frontend (Next.js)**: Modern Dashboard interface.

## Prerequisites

*   Python 3.8+
*   Node.js 18+
*   C++ Compiler (for Pyfhel) - Visual Studio Build Tools usually required on Windows.

## Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Usage

Open [http://localhost:3000](http://localhost:3000) in your browser.
Switch between "Diabetes" and "Academic" modes.

## Deployment to Vercel

*   **Frontend**: Can be deployed directly to Vercel (Import `project_build/frontend`).
*   **Backend**: Due to `Pyfhel` (C++) dependencies, the backend **cannot** be deployed to standard Vercel Serverless Functions easily. It is recommended to deploy the backend to a container service like **Render**, **Railway**, or **AWS EC2**, and update the `API_URL` in the frontend code.
