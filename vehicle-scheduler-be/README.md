# Vehicle Maintenance Scheduler Backend

A FastAPI-based microservice that calculates optimal vehicle maintenance schedules to maximize operational impact without exceeding daily mechanic-hour budget constraints.

## Setup Instructions

1. Install dependencies and the logging middleware:
   ```bash
   pip install -r requirements.txt
   pip install -e ../logging-middleware
   ```
2. Start the FastAPI server:
   ```bash
   python run.py
   ```
   The API will start running on `http://localhost:8000`.

## Testing the API
You can test the endpoint using Postman or cURL.

* **Endpoint**: `POST http://localhost:8000/schedule`
* **Body** (JSON):
  ```json
  {
    "depotId": 3
  }
  ```

> [!NOTE]
> **Troubleshooting missing depots**: The remote evaluation server API randomizes the active depot list on each query. If the server throws a `"Depot with ID X is not configured"` error, this is expected behavior from the test API. Simply **re-run/send the request again** in Postman, and the scheduler will calculate the output once the server includes that depot ID on the next query.
