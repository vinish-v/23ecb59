import requests

def Log(stack: str, level: str, package: str, message: str):
    """
    Sends a structured log message to the remote evaluation server log endpoint.
    Ensures parameters conform to expected lowercase formats.
    """
    url = "http://4.224.186.213/evaluation-service/logs"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJ2aW5pdjY2ODdAZ21haWwuY29tIiwiZXhwIjoxNzgyNzk4MDQwLCJpYXQiOjE3ODI3OTcxNDAsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiJmZTUzOTFmYS01YmEwLTQ2NTYtYWZkMC03MTM3NWE4YmE1ZDciLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJ2aW5pc2ggdiIsInN1YiI6ImY0NzZkNDFlLTA1ODEtNGI2ZC1iYWFlLWMzODJjZDgyNWJkYSJ9LCJlbWFpbCI6InZpbml2NjY4N0BnbWFpbC5jb20iLCJuYW1lIjoidmluaXNoIHYiLCJyb2xsTm8iOiIyM2VjYjU5IiwiYWNjZXNzQ29kZSI6IldqTnlDVCIsImNsaWVudElEIjoiZjQ3NmQ0MWUtMDU4MS00YjZkLWJhYWUtYzM4MmNkODI1YmRhIiwiY2xpZW50U2VjcmV0Ijoic0p4YWphTXV5V0dmYXlGSiJ9.NAqmWZ2_7bJTvMn2_GU3U7_euEWdESKrAzmBHZnZVys"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "stack": stack.lower(),
        "level": level.lower(),
        "package": package.lower(),
        "message": message
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print(f"Log sent successfully to test server: {message}")
        else:
            print(f"Remote Log Error ({response.status_code}): {response.text}")
    except Exception as err:
        print(f"Exception trying to reach logging server: {err}")
