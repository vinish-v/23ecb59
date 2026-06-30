import requests

def Log(stack: str, level: str, package: str, message: str):
    """Sends a structured log message to the remote evaluation server log endpoint.Ensures parameters conform to expected lowercase formats."""
    url = "http://4.224.186.213/evaluation-service/logs"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJ2aW5pdjY2ODdAZ21haWwuY29tIiwiZXhwIjoxNzgyODAwNjI5LCJpYXQiOjE3ODI3OTk3MjksImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiIxMDE2ODg2OC02OTcxLTQ5NjUtYmM1ZC1kMDk1NzlmNTJhMDkiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJ2aW5pc2ggdiIsInN1YiI6ImY0NzZkNDFlLTA1ODEtNGI2ZC1iYWFlLWMzODJjZDgyNWJkYSJ9LCJlbWFpbCI6InZpbml2NjY4N0BnbWFpbC5jb20iLCJuYW1lIjoidmluaXNoIHYiLCJyb2xsTm8iOiIyM2VjYjU5IiwiYWNjZXNzQ29kZSI6IldqTnlDVCIsImNsaWVudElEIjoiZjQ3NmQ0MWUtMDU4MS00YjZkLWJhYWUtYzM4MmNkODI1YmRhIiwiY2xpZW50U2VjcmV0Ijoic0p4YWphTXV5V0dmYXlGSiJ9.t67B69diED2cjKCyVd76RQdnFW8HVDsr8WcnLCJByAo"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    truncated_msg = message[:48] if len(message) > 48 else message
    
    payload = {
        "stack": stack.lower(),
        "level": level.lower(),
        "package": package.lower(),
        "message": truncated_msg
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            print(f"Log sent successfully to test server: {truncated_msg}")
        else:
            print(f"Remote Log Error ({response.status_code}): {response.text}")
    except Exception as err:
        print(f"Exception trying to reach logging server: {err}")
