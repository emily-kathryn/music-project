import requests

LASTFM_API_KEY = "ec967c7bbb7cc77ee4696cb322731434"  # replace with your real key

def get_recommendations(artist, track):
    # Try to get similar tracks based on the song
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.getsimilar",
        "artist": artist,
        "track": track,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": 5
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "similartracks" in data and "track" in data["similartracks"]:
        recs = data["similartracks"]["track"]
        return [{"name": t["name"], "artist": t["artist"]["name"]} for t in recs]

    # If no track-based recs, fallback to artist-based
    params = {
        "method": "artist.getsimilar",
        "artist": artist,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": 5
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "similarartists" in data and "artist" in data["similarartists"]:
        recs = data["similarartists"]["artist"]
        return [{"name": r["name"], "artist": "Various"} for r in recs]

    return []