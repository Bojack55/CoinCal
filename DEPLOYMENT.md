# 🚀 Deployment Guide: CoinCal

This guide will help you deploy your Django backend to **Render.com** (Free) and build your Android app for production.

---

## Part 1: Backend Deployment (Render.com)

### 1. Push Code to GitHub
Ensure all your latest changes (including `build.sh` and `requirements.txt`) are pushed to GitHub.

### 2. Create Database
1.  Log in to [Render.com](https://render.com/).
2.  Click **New +** -> **PostgreSQL**.
3.  Name: `coincal-db`.
4.  Region: `Frankfurt` (or closest to you).
5.  Plan: **Free** (Note: Expires after 90 days, you can upgrade later).
6.  Click **Create Database**.
7.  **Copy the "Internal Database URL"** (you'll need it soon).

### 3. Create Web Service
1.  Click **New +** -> **Web Service**.
2.  Connect your GitHub repository `CoinCal`.
3.  **Name**: `coincal-api`.
4.  **Region**: Same as database.
5.  **Branch**: `main`.
6.  **Root Directory**: `backend` (Important!).
7.  **Runtime**: `Python 3`.
8.  **Build Command**: `./build.sh`
9.  **Start Command**: `gunicorn budget_nutritionist.wsgi:application`
10. **Plan**: Free.

### 4. Environment Variables
Scroll down to "Environment Variables" and add these:

| Key | Value |
| :--- | :--- |
| `PYTHON_VERSION` | `3.10.12` |
| `SECRET_KEY` | (Generate a random string) |
| `DEBUG` | `False` |
| `DATABASE_URL` | (Paste the **Internal Database URL** from Step 2) |
| `ALLOWED_HOSTS` | `.onrender.com` |

11. Click **Create Web Service**.

### 5. Verify Deployment
Wait for the build to finish. Once valid, you will see a URL like `https://coincal-api.onrender.com`.
Visit `https://coincal-api.onrender.com/api/dashboard/` to confirm it returns a 401 (Unauthorized) instead of 500.

---

## Part 2: Frontend Build (Android)

Now that your backend is live, build the app to point to it.

### 1. Get Your Backend URL
Copy your Render URL (e.g., `https://coincal-api.onrender.com/api`). **Make sure to include `/api` at the end if your app expects it.**

### 2. Build APK
Run this command in your terminal (inside `frontend/coincal_mobile`):

```bash
flutter build apk --release --dart-define=API_URL=https://coincal-api.onrender.com/api
```

*Note: Replace `https://coincal-api.onrender.com/api` with your actual URL.*

### 3. Install on Device
Transfer the built APK (`build/app/outputs/flutter-apk/app-release.apk`) to your phone and install it.

---

## 🛠️ Troubleshooting

- **500 Server Error**: Check Render logs. It might be a database migration issue.
- **Database Error**: Ensure `DATABASE_URL` is correct and starts with `postgres://`.
- **Static Files 404**: Ensure `whitenoise` is in `MIDDLEWARE` and `requirements.txt` (we added these).
