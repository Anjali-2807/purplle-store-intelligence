# Apex Retail Store Intelligence Platform Demo Links

This document provides links and details to access the working prototype/demo dashboard of your **Apex Retail Store Intelligence Platform**.

## 🚀 Option 1: Live Cloudflare Tunnel (Active & Recommended)
This option is currently active. It is completely warning-free and password-free:

* **Live Dashboard**: [https://fiber-term-soldiers-closest.trycloudflare.com/dashboard](https://fiber-term-soldiers-closest.trycloudflare.com/dashboard)
* **API Health Status**: [https://fiber-term-soldiers-closest.trycloudflare.com/health](https://fiber-term-soldiers-closest.trycloudflare.com/health)

> [!NOTE]
> This tunnel runs directly from your local machine. It will remain active as long as your computer is awake and the terminal processes are running.

---

## 🛠️ Option 2: Permanent 24/7 Cloud Deployment (No Computer Dependency)
To get a permanent URL that runs 24/7 in the cloud (so you can close your laptop), follow these simple steps to deploy from your GitHub repository:

### Method A: Render (One-Click Blueprint)
I have configured a blueprint (`render.yaml`) for your repository. To deploy it to Render:
1. Click the following link: [Deploy to Render](https://render.com/deploy?repo=https://github.com/Anjali-2807/purplle-store-intelligence)
2. Connect your GitHub account if prompted.
3. Review the pre-filled service name, port `8000`, and runtime configs (all auto-populated from `render.yaml`).
4. Click **Apply / Deploy**. Render will automatically build the container and provide you with a clean, permanent `https://<your-app>.onrender.com` link.

### Method B: Hugging Face Spaces (100% Free & Fast)
1. Log in to [Hugging Face](https://huggingface.co/) and click **New Space**.
2. Name your Space, and under **SDK**, select **Docker**.
3. Choose the **Blank** template and make the Space **Public**.
4. Clone the Space repo locally, copy the contents of the `store-intelligence/` directory into it (ensuring the `Dockerfile` is at the root of the Space repository), and commit/push.
5. Hugging Face will automatically build and host the app at `https://<username>-<space-name>.hf.space`.
