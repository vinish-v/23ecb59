import requests
import json
import heapq
from datetime import datetime

# Token to query protected endpoints (Authentication payload)
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJ2aW5pdjY2ODdAZ21haWwuY29tIiwiZXhwIjoxNzgyODAwNjI5LCJpYXQiOjE3ODI3OTk3MjksImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiIxMDE2ODg2OC02OTcxLTQ5NjUtYmM1ZC1kMDk1NzlmNTJhMDkiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJ2aW5pc2ggdiIsInN1YiI6ImY0NzZkNDFlLTA1ODEtNGI2ZC1iYWFlLWMzODJjZDgyNWJkYSJ9LCJlbWFpbCI6InZpbml2NjY4N0BnbWFpbC5jb20iLCJuYW1lIjoidmluaXNoIHYiLCJyb2xsTm8iOiIyM2VjYjU5IiwiYWNjZXNzQ29kZSI6IldqTnlDVCIsImNsaWVudElEIjoiZjQ3NmQ0MWUtMDU4MS00YjZkLWJhYWUtYzM4MmNkODI1YmRhIiwiY2xpZW50U2VjcmV0Ijoic0p4YWphTXV5V0dmYXlGSiJ9.t67B69diED2cjKCyVd76RQdnFW8HVDsr8WcnLCJByAo"
URL = "http://4.224.186.213/evaluation-service/notifications"

# Define priority weights based on requirements: Placement (3) > Result (2) > Event (1)
WEIGHT_RULES = {
    "Placement": 3,
    "Result": 2,
    "Event": 1
}

class NotificationItem:
    """
    Represents a single campus notification.
    Implements comparison methods so it can be managed inside a Python Min-Heap.
    """
    def __init__(self, id_val: str, notif_type: str, message: str, timestamp_str: str):
        self.id = id_val
        self.type = notif_type
        self.message = message
        self.timestamp = timestamp_str
        
        # Convert the ISO timestamp string to a datetime object for comparison
        self.dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        
        # Lookup the numeric weight of this notification type
        self.weight = WEIGHT_RULES.get(notif_type, 0)
        
    def __lt__(self, other):
        # This determines the order in Python's heapq (Min-Heap).
        # A Min-Heap naturally keeps the SMALLER elements at the top.
        # We define a notification as having "lower priority" (smaller) if:
        # 1. Its weight is lower (e.g. Event is smaller than Placement)
        # 2. In case of a tie in weight, its timestamp is older (recency rule)
        if self.weight != other.weight:
            return self.weight < other.weight
        return self.dt < other.dt

    def to_dict(self) -> dict:
        """Helper to convert the class instance back to a plain dictionary."""
        return {
            "ID": self.id,
            "Type": self.type,
            "Message": self.message,
            "Timestamp": self.timestamp
        }

class PriorityInboxTracker:
    """
    Manages the Inbox buffer of top 'N' highest priority notifications.
    Uses a Min-Heap of size N to keep tracking operations efficient O(log N).
    """
    def __init__(self, limit: int = 10):
        self.limit = limit
        self.heap = []  # Internal storage list for the heap structure

    def insert(self, item: NotificationItem):
        # Case 1: Heap is not yet full. We simply push the new notification.
        if len(self.heap) < self.limit:
            heapq.heappush(self.heap, item)
        else:
            # Case 2: Heap is full.
            # We compare the new notification with the smallest (root) item in the heap: self.heap[0].
            # If the new notification is higher priority (greater) than the lowest priority item in the heap,
            # we pop the lowest priority item and insert the new one.
            if item > self.heap[0]:
                heapq.heappushpop(self.heap, item)

    def retrieve_ordered(self) -> list:
        # Extract items from the heap and sort them in descending order (highest priority first).
        sorted_items = sorted(self.heap, reverse=True)
        return [item.to_dict() for item in sorted_items]

def main():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("Connecting to endpoint and fetching campus notifications...")
    res = requests.get(URL, headers=headers)
    if res.status_code != 200:
        print(f"API Request Failure ({res.status_code}): {res.text}")
        return
        
    payload = res.json()
    raw_notifications = payload.get("notifications", [])
    print(f"Successfully downloaded {len(raw_notifications)} notifications.")
    
    # Instantiate the tracker to retain only the top 10 items
    tracker = PriorityInboxTracker(limit=10)
    
    # Process each notification to maintain the priority heap
    for n in raw_notifications:
        item = NotificationItem(
            id_val=n["ID"],
            notif_type=n["Type"],
            message=n["Message"],
            timestamp_str=n["Timestamp"]
        )
        tracker.insert(item)
        
    # Retrieve and print the top 10 list
    top_ten = tracker.retrieve_ordered()
    print("\n--- TOP 10 PRIORITY INBOX NOTIFICATIONS ---")
    print(json.dumps(top_ten, indent=2))

if __name__ == "__main__":
    main()
