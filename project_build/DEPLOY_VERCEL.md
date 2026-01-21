# Deployment Guide to Vercel

This project is a monorepo containing a FastAPI backend and a Next.js frontend. To deploy it to Vercel, you should follow these steps to deploy them as two separate linked services.

## Prerequisites
- A GitHub repository with your current code pushed to it.
- A [Vercel](https://vercel.com) account.

---

## 1. Deploy the Backend (FastAPI)

1. **Log in** to your Vercel Dashboard.
2. Click **Add New** -> **Project**.
3. Import your GitHub repository.
4. In the **Configure Project** screen:
   - **Project Name**: `ppml-backend`
   - **Framework Preset**: Other (it will auto-detect the Python runtime)
   - **Root Directory**: Click "Edit" and select `project_build/backend`.
5. Click **Deploy**.
6. Once the deployment is finished, **copy the URL** of your backend (e.g., `https://ppml-backend.vercel.app`).

---

## 2. Deploy the Frontend (Next.js)

1. Go back to the Vercel Dashboard.
2. Click **Add New** -> **Project**.
3. Import the **same repository** again.
4. In the **Configure Project** screen:
   - **Project Name**: `ppml-frontend`
   - **Framework Preset**: Next.js
   - **Root Directory**: Click "Edit" and select `project_build/frontend`.
5. **Environment Variables**:
   - Expand the "Environment Variables" section.
   - Add a new variable:
     - **Key**: `NEXT_PUBLIC_API_URL`
     - **Value**: Paste your backend URL (e.g., `https://ppml-backend.vercel.app`)
6. Click **Deploy**.

---

## Technical Details
- **Encryption**: Real Homomorphic Encryption (Pyfhel) requires a complex build environment not natively supported by Vercel's serverless functions. The system will automatically fallback to **Mock Encryption Mode** on Vercel, which allows the app to function and demonstrate the Client-Server architecture logic.
- **CORS**: The backend is configured to accept requests from any origin, which allows your frontend and backend to talk to each other without issues.
