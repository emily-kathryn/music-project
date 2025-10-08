import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --- Spotify API credentials ---
client_id = "9aa7f71bfa3f4506b3d51572e42c0f9f"
client_secret = "f9914eedb1f742759f9c7c1ab83eda07"
redirect_uri = "https://127.0.0.1.nip.io:8888/callback"

# --- AUTHENTICATE WITH SPOTIFY ---
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="user-read-private"
))

# --- ASK FOR A SONG NAME ---
song_name = input("🎵 Enter a song name: ")

# --- SEARCH FOR THE SONG ---
results = sp.search(q=song_name, type="track", limit=1)

if results['tracks']['items']:
    track = results['tracks']['items'][0]
    name = track['name']
    artist = track['artists'][0]['name']
    popularity = track['popularity']
    duration_ms = track['duration_ms']
    duration_min = round(duration_ms / 60000, 2)

    print(f"\n🎵 Found: {name} by {artist}")
    print(f"💫 Popularity: {popularity}")
    print(f"⏱ Duration: {duration_min} minutes")
else:
    print("🚫 No song found.")