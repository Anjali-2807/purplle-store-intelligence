# Apex Retail Store Intelligence Platform Demo Links

This document provides links and details to access the working prototype/demo dashboard of your **Apex Retail Store Intelligence Platform**.

## 🚀 Live Cloud Deployment (Permanent & 24/7)
The application has been successfully deployed to Render and is running in the cloud. It does not depend on your local machine and will remain online 24/7 for the reviewers:

* **Live Dashboard Link**: [https://purplle-store-intelligence-xxm1.onrender.com/dashboard](https://purplle-store-intelligence-xxm1.onrender.com/dashboard)
* **API Health Check**: [https://purplle-store-intelligence-xxm1.onrender.com/health](https://purplle-store-intelligence-xxm1.onrender.com/health)

---

## 🛠️ Key Production Features Implemented
1. **Viewport Constraints (PC Layout)**: Designed to fit 100% above the fold on desktop screens (`100vh` height limits, scrollbar-free).
2. **Dynamic Simulation Replays**: Fully supports switching stores (`STORE_BLR_002` / `ST1008`) and re-running simulations by dynamically mapping unique IDs to bypass database primary key constraints.
3. **Reset Endpoint**: Integrated a `POST /stores/{id}/reset` API and header button to drop events and reset dashboard states back to 0.
4. **Graceful DB Degradation**: Maps operational connection failures (like SQLite unavailability) directly to a clean **HTTP 503 Service Unavailable** JSON response, ensuring zero stack-trace leakage.

---

## 💻 Local Verification & Development
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
