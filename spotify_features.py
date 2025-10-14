import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Cache for token and expiry time
_token_data = {"access_token": None, "expires_at": 0}


def get_spotify_token():
    """Fetch or refresh Spotify API token automatically."""
    global _token_data
    now = time.time()

    # Reuse valid token
    if _token_data["access_token"] and now < _token_data["expires_at"]:
        return _token_data["access_token"]

    print("🔑 Requesting new Spotify token...")
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )

    if response.status_code != 200:
        raise Exception(f"Failed to get Spotify token: {response.text}")

    token_data = response.json()
    _token_data["access_token"] = token_data["access_token"]
    _token_data["expires_at"] = now + token_data["expires_in"] - 30  # 30s buffer

    print(f"✅ Token received, expires in {token_data['expires_in']} seconds.")
    return _token_data["access_token"]


def spotify_get(endpoint):
    """Perform authenticated GET requests to the Spotify API."""
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api.spotify.com/v1/{endpoint}", headers=headers)

    # If token expired or invalid, retry once
    if response.status_code in (401, 403):
        print(f"⚠️ Refreshing token due to {response.status_code} error...")
        _token_data["access_token"] = None
        token = get_spotify_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"https://api.spotify.com/v1/{endpoint}", headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Error {response.status_code} from Spotify API for '{endpoint}': {response.text}"
        )

    return response.json()


def get_track_info(artist_name, track_name):
    """Search for a track by artist and title."""
    query = f"track:{track_name} artist:{artist_name}"
    search_url = f"search?q={requests.utils.quote(query)}&type=track&limit=1"

    search_data = spotify_get(search_url)

    if not search_data.get("tracks") or not search_data["tracks"]["items"]:
        raise Exception(f"No results found for '{track_name}' by {artist_name}")

    track = search_data["tracks"]["items"][0]
    track_id = track["id"]
    print(f"✅ Found track: {track['name']} by {track['artists'][0]['name']}")

    return {
        "id": track_id,
        "track": track["name"],
        "artist": track["artists"][0]["name"],
        "album_art": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
        "popularity": track.get("popularity"),
        "spotify_url": track["external_urls"]["spotify"],
        "preview_url": track.get("preview_url"),
        "duration_ms": track["duration_ms"],
    }


def get_audio_features(track_id):
    """Get detailed audio features (tempo, key, energy, loudness, etc.)."""
    try:
        data = spotify_get(f"audio-features/{track_id}")
        return data
    except Exception as e:
        print(f"⚠️ Audio features unavailable ({e}). Falling back to /tracks data.")
        track_data = spotify_get(f"tracks/{track_id}")
        # partial fallback
        return {
            "tempo": None,
            "key": None,
            "energy": None,
            "loudness": None,
            "duration_ms": track_data.get("duration_ms"),
        }


def get_spotify_features(artist_name, track_name):
    """Combine metadata and audio analysis."""
    track_info = get_track_info(artist_name, track_name)
    features = get_audio_features(track_info["id"])

    # Combine everything into a single dictionary
    return {
        **track_info,
        "tempo": features.get("tempo"),
        "key": features.get("key"),
        "energy": features.get("energy"),
        "loudness": features.get("loudness"),
    }