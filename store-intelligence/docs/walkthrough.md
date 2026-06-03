# Apex Retail Store Intelligence Platform Demo Links

This document provides links and details to access the working prototype/demo dashboard of your **Apex Retail Store Intelligence Platform**.

## 🚀 Live Cloud Deployment (Permanent & 24/7)
The application has been successfully deployed to Render and is running in the cloud. It does not depend on your local machine and will remain online 24/7 for the reviewers:

* **Live Dashboard Link**: [https://purplle-store-intelligence-xxm1.onrender.com/dashboard](https://purplle-store-intelligence-xxm1.onrender.com/dashboard)
* **API Health Check**: [https://purplle-store-intelligence-xxm1.onrender.com/health](https://purplle-store-intelligence-xxm1.onrender.com/health)

---

## 🛠️ Local Verification & Development
If you need to run the application locally or run the automated test suite, use the following commands:

### 1. Run local FastAPI dev server
```bash
PYTHONPATH=./store-intelligence python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Then navigate to `http://localhost:8000/dashboard` in your browser.

### 2. Run test suite
```bash
PYTHONPATH=./store-intelligence pytest store-intelligence/tests/ -v
```
