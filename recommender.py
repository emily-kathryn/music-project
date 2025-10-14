import os
import requests
from dotenv import load_dotenv

load_dotenv()

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")

def get_recommendations(artist_name, track_name):
    """Fetch similar tracks from Last.fm."""
    try:
        url = "https://ws.audioscrobbler.com/2.0/"
        params = {
            "method": "track.getsimilar",
            "artist": artist_name,
            "track": track_name,
            "api_key": LASTFM_API_KEY,
            "format": "json",
            "limit": 5
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        tracks = data.get("similartracks", {}).get("track", [])
        recommendations = []

        for t in tracks:
            if isinstance(t, dict):
                rec_name = t.get("name", "Unknown Track")
                artist = t.get("artist", {}).get("name", "Unknown Artist")
                recommendations.append({"name": rec_name, "artist": artist})

        return recommendations if recommendations else None

    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        return None