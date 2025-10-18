import os
import requests
from dotenv import load_dotenv

load_dotenv()

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_API_SECRET = os.getenv("LASTFM_API_SECRET")
LASTFM_BASE_URL = "http://ws.audioscrobbler.com/2.0/"


def get_lastfm_track_info(artist_name, track_name):
    """
    Get track information from Last.fm including tags which can help
    categorize the music style and energy.
    """
    params = {
        "method": "track.getInfo",
        "api_key": LASTFM_API_KEY,
        "artist": artist_name,
        "track": track_name,
        "format": "json",
    }
    
    try:
        response = requests.get(LASTFM_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "track" not in data:
            return None
            
        track = data["track"]
        
        # Extract tags
        tags = []
        if "toptags" in track and "tag" in track["toptags"]:
            tags = [tag["name"].lower() for tag in track["toptags"]["tag"]]
        
        return {
            "playcount": int(track.get("playcount", 0)),
            "listeners": int(track.get("listeners", 0)),
            "tags": tags,
            "duration": int(track.get("duration", 0)),  # in milliseconds
        }
    except Exception as e:
        print(f"⚠️ Last.fm track info error: {e}")
        return None


def estimate_features_from_tags(tags):
    """
    Estimate audio features based on Last.fm tags.
    Returns a dict with estimated values between 0-1.
    """
    tags_lower = [tag.lower() for tag in tags]
    
    # Energy estimation
    high_energy_tags = ["rock", "metal", "punk", "electronic", "dance", "edm", "techno", "hardcore"]
    low_energy_tags = ["ambient", "chill", "acoustic", "classical", "folk", "sleep"]
    
    energy = 0.5  # default
    if any(tag in tags_lower for tag in high_energy_tags):
        energy = 0.8
    elif any(tag in tags_lower for tag in low_energy_tags):
        energy = 0.3
    
    # Danceability estimation
    dance_tags = ["dance", "edm", "pop", "disco", "funk", "house", "techno"]
    if any(tag in tags_lower for tag in dance_tags):
        danceability = 0.8
    else:
        danceability = 0.5
    
    # Valence (happiness) estimation
    happy_tags = ["happy", "upbeat", "cheerful", "party", "fun", "summer"]
    sad_tags = ["sad", "melancholy", "depressing", "dark", "doom"]
    
    valence = 0.5
    if any(tag in tags_lower for tag in happy_tags):
        valence = 0.8
    elif any(tag in tags_lower for tag in sad_tags):
        valence = 0.3
    
    # Acousticness estimation
    acoustic_tags = ["acoustic", "folk", "classical", "unplugged"]
    if any(tag in tags_lower for tag in acoustic_tags):
        acousticness = 0.8
    else:
        acousticness = 0.3
    
    # Tempo estimation (BPM range)
    fast_tags = ["hardcore", "drum and bass", "speed metal", "thrash"]
    slow_tags = ["ambient", "downtempo", "chill", "slowcore"]
    
    tempo = 120  # default BPM
    if any(tag in tags_lower for tag in fast_tags):
        tempo = 160
    elif any(tag in tags_lower for tag in slow_tags):
        tempo = 80
    
    return {
        "energy": energy,
        "danceability": danceability,
        "valence": valence,
        "acousticness": acousticness,
        "tempo": tempo,
    }


def get_enhanced_features(artist_name, track_name):
    """
    Get enhanced track features by combining Last.fm data.
    This provides estimates when Spotify audio features aren't available.
    """
    lastfm_info = get_lastfm_track_info(artist_name, track_name)
    
    if not lastfm_info:
        return {
            "energy": None,
            "danceability": None,
            "valence": None,
            "acousticness": None,
            "tempo": None,
            "tags": [],
        }
    
    estimated = estimate_features_from_tags(lastfm_info["tags"])
    
    return {
        **estimated,
        "tags": lastfm_info["tags"][:5],  # Top 5 tags
        "playcount": lastfm_info["playcount"],
        "listeners": lastfm_info["listeners"],
    }