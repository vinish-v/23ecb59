import requests
import json

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJ2aW5pdjY2ODdAZ21haWwuY29tIiwiZXhwIjoxNzgyODAwNjI5LCJpYXQiOjE3ODI3OTk3MjksImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiIxMDE2ODg2OC02OTcxLTQ5NjUtYmM1ZC1kMDk1NzlmNTJhMDkiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJ2aW5pc2ggdiIsInN1YiI6ImY0NzZkNDFlLTA1ODEtNGI2ZC1iYWFlLWMzODJjZDgyNWJkYSJ9LCJlbWFpbCI6InZpbml2NjY4N0BnbWFpbC5jb20iLCJuYW1lIjoidmluaXNoIHYiLCJyb2xsTm8iOiIyM2VjYjU5IiwiYWNjZXNzQ29kZSI6IldqTnlDVCIsImNsaWVudElEIjoiZjQ3NmQ0MWUtMDU4MS00YjZkLWJhYWUtYzM4MmNkODI1YmRhIiwiY2xpZW50U2VjcmV0Ijoic0p4YWphTXV5V0dmYXlGSiJ9.t67B69diED2cjKCyVd76RQdnFW8HVDsr8WcnLCJByAo"
URL = "http://4.224.186.213/evaluation-service/notifications"

WEIGHTS = {
    "Placement": 3,
    "Result": 2,
    "Event": 1
}

def get_priority_key(notif: dict) -> tuple:
  
    weight = WEIGHTS.get(notif.get("Type"), 0)
    timestamp = notif.get("Timestamp", "")
    return (weight, timestamp)

def main():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("Fetching from server")
    res = requests.get(URL, headers=headers)
    if res.status_code != 200:
        print(f"Error : {res.status_code}")
        return
        
    raw_notifications = res.json().get("notifications", [])
    print(f"Downloaded {len(raw_notifications)} notifications.")
  
    sorted_notifs = sorted(raw_notifications, key=get_priority_key, reverse=True)
    top_10 = sorted_notifs[:10]

    print("TOP NOTIFICATIONS")
    print(json.dumps(top_10, indent=2))

if __name__ == "__main__":
    main()
