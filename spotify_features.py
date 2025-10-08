
from dotenv import load_dotenv
load_dotenv()
import os
import requests
import base64
import json

# Masked status print for debugging (no secrets printed)
_cid = os.getenv("SPOTIFY_CLIENT_ID")
if _cid:
    print("SPOTIFY_CLIENT_ID:", _cid[:4] + "..." + _cid[-4:])
else:
    print("SPOTIFY_CLIENT_ID: not set")

# Read Spotify credentials from environment variables to avoid committing secrets
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


def get_access_token():
    """
    Always fetch a fresh token from Spotify using Client Credentials flow.
    """
    if not CLIENT_ID or not CLIENT_SECRET:
        return {"error": "Spotify credentials not set in environment."}

    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"},
        timeout=10
    )
    try:
        data = resp.json()
    except Exception:
        data = {"error": "invalid_json_response"}

    if resp.status_code != 200:
        print("⚠️ Token request failed:", data)
        return {"error": data}

    return data.get("access_token")

def get_audio_features(artist_name, track_name):
    token = get_access_token()   # <–– ensure this is inside the function
    headers = {"Authorization": f"Bearer {token}"}
    
    search_queries = [
        f"track:{track_name} artist:{artist_name}",
        f"{track_name} {artist_name}",
        track_name
    ]
    
    track_data = None
    for query in search_queries:
        search_url = "https://api.spotify.com/v1/search"
        params = {"q": query, "type": "track", "limit": 1}
        search_res = requests.get(search_url, headers=headers, params=params)
        data = search_res.json()
        print("🔍 Search response for", query, "→", data)
        if data.get("tracks", {}).get("items"):
            track_data = data["tracks"]["items"][0]
            break
    
    if not track_data:
        print("⚠️ No track found on Spotify for:", artist_name, "-", track_name)
        return None

    track_id = track_data["id"]
    print(f"✅ Found track: {track_data['name']} by {track_data['artists'][0]['name']}")
    
    features_url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    features_res = requests.get(features_url, headers=headers)
    features = features_res.json()
    print("🎧 Audio features:", json.dumps(features, indent=2))
    
    if "error" in features:
        return None

    return {
        "artist": track_data["artists"][0]["name"],
        "track": track_data["name"],
        "key": features.get("key"),
        "tempo": features.get("tempo"),
        "energy": features.get("energy"),
        "loudness": features.get("loudness"),
        "duration": round(track_data["duration_ms"] / 60000, 2),
        "popularity": track_data.get("popularity")
    }