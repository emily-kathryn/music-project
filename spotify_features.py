import os
import requests
import base64

# Read Spotify credentials from environment variables to avoid committing secrets
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_spotify_token():
    try:
        # Ensure credentials are present
        if not CLIENT_ID or not CLIENT_SECRET:
            return {"error": "Spotify credentials not set. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your environment."}

        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()

        headers = {"Authorization": f"Basic {b64_auth_str}"}
        data = {"grant_type": "client_credentials"}
        response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        response.raise_for_status()
        token = response.json().get("access_token")
        return token
    except Exception as e:
        print(f"❌ Token error: {e}")
        return None


# --- Song Data Fetcher ---
def get_audio_features(artist, track):
    token = get_spotify_token()
    if not token:
        print("⚠️ Could not get Spotify token.")
        return None

    headers = {"Authorization": f"Bearer {token}"}
    search_url = "https://api.spotify.com/v1/search"
    params = {"q": f"{artist} {track}", "type": "track", "limit": 1}

    try:
        search_res = requests.get(search_url, headers=headers, params=params)
        search_data = search_res.json()
        if not search_data.get("tracks", {}).get("items"):
            print("⚠️ No track found.")
            return None

        item = search_data["tracks"]["items"][0]
        track_id = item["id"]
        artist_name = item["artists"][0]["name"]
        track_name = item["name"]
        duration = round(item["duration_ms"] / 60000, 2)
        popularity = item["popularity"]

        print(f"🎵 Found {track_name} by {artist_name} (ID: {track_id})")

        # First try /audio-features
        features_url = f"https://api.spotify.com/v1/audio-features/{track_id}"
        feat_res = requests.get(features_url, headers=headers)
        if feat_res.status_code == 200:
            features = feat_res.json()
        else:
            print("⚠️ audio-features blocked, using audio-analysis fallback.")
            features = {}

        # Fallback /audio-analysis if needed
        if not features or not features.get("tempo"):
            analysis_url = f"https://api.spotify.com/v1/audio-analysis/{track_id}"
            ana_res = requests.get(analysis_url, headers=headers)
            if ana_res.status_code == 200:
                analysis_data = ana_res.json()
                if "track" in analysis_data:
                    features["tempo"] = analysis_data["track"].get("tempo", 0)
                    features["key"] = analysis_data["track"].get("key", -1)
                    features["loudness"] = analysis_data["track"].get("loudness", 0)
            else:
                print(f"⚠️ audio-analysis failed ({ana_res.status_code})")

        # Build result safely
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key_name = keys[features.get("key", 0) % 12] if "key" in features else "N/A"

        return {
            "artist": artist_name,
            "track": track_name,
            "tempo": round(features.get("tempo", 0), 2) if "tempo" in features else "N/A",
            "energy": round(features.get("energy", 0.0), 3) if "energy" in features else "N/A",
            "loudness_db": round(features.get("loudness", 0.0), 2) if "loudness" in features else "N/A",
            "duration_minutes": duration,
            "popularity": popularity,
            "key": key_name,
        }

    except Exception as e:
        print(f"❌ Spotify API error: {e}")
        return None