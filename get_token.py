import requests

# Credentials
EMAIL = "viniv6687@gmail.com"
NAME = "vinish v"
ROLL_NO = "23ecb59"
ACCESS_CODE = "WjNyCT"
CLIENT_ID = "f476d41e-0581-4b6d-baae-c382cd825bda"
CLIENT_SECRET = "sJxajaMuyWGfayFJ"

URL = "http://4.224.186.213/evaluation-service/auth"

def get_new_token():
    payload = {
        "email": EMAIL,
        "name": NAME,
        "rollNo": ROLL_NO,
        "accessCode": ACCESS_CODE,
        "clientID": CLIENT_ID,
        "clientSecret": CLIENT_SECRET
    }
    
    print("Requesting fresh access token...")
    response = requests.post(URL, json=payload)
    if response.status_code in [200, 201]:
        data = response.json()
        token = data.get("access_token")
        print("\n--- NEW ACCESS TOKEN ---")
        print(token)
        print("\nToken expires in 15 minutes.")
        return token
    else:
        print(f"Failed to authenticate: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    get_new_token()
