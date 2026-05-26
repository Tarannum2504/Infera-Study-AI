# Deployment Guide: Infera Study AI to Streamlit Community Cloud

This guide provides step-by-step instructions to deploy **Infera Study AI** from your GitHub repository to **Streamlit Community Cloud** (a free, high-performance hosting platform optimized for Streamlit applications).

---

## Prerequisites
1. A GitHub account with access to the pushed repository: `https://github.com/Tarannum2504/Infera-Study-AI`.
2. A Hugging Face API token (your `HF_API_KEY` from the local `.env` file).

---

## Step-by-Step Deployment

### 1. Log In to Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Click **"Continue with GitHub"** and authorize Streamlit with your GitHub account.

### 2. Set Up a New App
1. Once logged in to the dashboard, click **"New app"** (or **"Create app"**) in the top right corner.
2. In the deployment form, configure the following fields:
   * **Repository**: Select `Tarannum2504/Infera-Study-AI` (or type the URL if not listed).
   * **Branch**: `master` (or the branch you committed to).
   * **Main file path**: `app.py`

### 3. Add Environment Secrets (Crucial)
Since your API keys are stored securely in `.env` and are not committed to GitHub, you must add your keys to the Streamlit cloud settings so that the AI Planner and Assistant can communicate with Hugging Face.

1. Click **"Advanced settings..."** at the bottom of the deployment window.
2. In the **Secrets** section, copy and paste the key-value pair exactly as follows:
   ```toml
   HF_API_KEY = "your_huggingface_api_key_here"
   ```
3. Click **"Save"**.

### 4. Deploy!
1. Click **"Deploy!"**.
2. Streamlit Cloud will set up a virtual environment, automatically install all dependencies listed in `requirements.txt`, and build the application container.
3. Once completed (usually 1-2 minutes), your application will be live at a custom sub-domain!

---

## Managing Your Deployed App
* **Automatic Redeploys**: Whenever you push updates to your GitHub `master` branch, Streamlit Community Cloud will automatically detect the changes and rebuild the app within seconds.
* **Persistent SQLite Database**: Note that Streamlit Community Cloud's file system is ephemeral. Any data stored in the local SQLite database (`infera.db`) will reset when the app container restarts.
  > [!TIP]
  > For production setups with permanent data retention, consider changing the SQLite database connection in [database/db.py](file:///c:/Users/l/Desktop/python/Data%20Analysis/infera_Study_AI/database/db.py) to a hosted PostgreSQL database (such as Neon, Supabase, or AWS RDS).
