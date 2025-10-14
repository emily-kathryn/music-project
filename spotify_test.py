import os, requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# Step 1: Request a client credentials token
token_resp = requests.post(
    "https://accounts.spotify.com/api/token",
    data={"grant_type": "client_credentials"},
    auth=(client_id, client_secret),
)

print("Token status:", token_resp.status_code)
print(token_resp.json())

if token_resp.status_code != 200:
    print("❌ Token request failed — check client_id/client_secret.")
    exit()

access_token = token_resp.json().get("access_token")

# Step 2: Test audio features endpoint directly
headers = {"Authorization": f"Bearer {access_token}"}
track_id = "4evLyY5Ue1Wesc61t2KXAU"  # you can change this to any valid ID
resp = requests.get(f"https://api.spotify.com/v1/audio-features/{track_id}", headers=headers)
print("Audio features status:", resp.status_code)
print(resp.json())