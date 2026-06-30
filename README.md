# Logistics & Campus Notification Platform Backend

This repository contains the backend components and design specifications for the evaluation pretest.

## Project Structure

The project is split into the following directories:

*   **`logging-middleware/`**: A reusable Python logging package that formats log entries (`stack`, `level`, `package`, `message`) and forwards them to the remote evaluation server.
*   **`vehicle-scheduler-be/`**: A FastAPI microservice that fetches logistics depot mechanic hour constraints and vehicle tasks to calculate the optimal subset of vehicles to service (solved using the dynamic programming 0/1 Knapsack algorithm).
*   **`notification-app-be/`**: A lightweight Python implementation of the Priority Inbox algorithm for campus notifications.
*   **`notification-system-design.md`**: Architectural design documentation answering Stages 1 through 6 of the campus notification system setup.
*   **`get_token.py`**: A helper utility to request fresh JWT access tokens from the authorization server.

---

## Getting Started

### 1. Set Up Virtual Environment
Initialize and activate a virtual environment from the root directory:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Packages
Install the reusable logging middleware in editable mode, along with the scheduler app dependencies:
```bash
pip install -e ./logging-middleware
pip install -r ./vehicle-scheduler-be/requirements.txt
```

### 3. Generate a Fresh Token
JWT access tokens expire every 15 minutes. To fetch a fresh token, run:
```bash
python get_token.py
```
Copy the token printed in the terminal. You can replace the hardcoded token in the following configuration files if testing locally:
*   `vehicle-scheduler-be/app/config.py`
*   `logging-middleware/middleware.py`
*   `notification-app-be/priority_inbox.py`

---

## Running & Testing

### Vehicle Scheduler Microservice
To start the FastAPI server:
```bash
cd vehicle-scheduler-be
python run.py
```
Query the optimization endpoint with a POST request:
*   **URL**: `POST http://localhost:8000/schedule`
*   **Headers**: `Content-Type: application/json`
*   **Body**:
    ```json
    {
      "depotId": 3
    }
    ```

> [!NOTE]
> **Troubleshooting missing depots**: The remote evaluation server API randomizes the active depot list on each query. If the server throws a `"Depot with ID X is not configured"` error, this is expected behavior from the test API. Simply **re-run/send the request again** in Postman, and the scheduler will calculate the output once the server includes that depot ID on the next query.

### Priority Inbox Script
To run the Priority Inbox script:
```bash
cd notification-app-be
python priority_inbox.py
```
This downloads all active campus notifications and prints the top 10 prioritized items based on weight and recency.
