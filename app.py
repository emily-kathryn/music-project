from flask import Flask, render_template, request
from spotify_features import get_spotify_features
from recommender import get_recommendations
from analyzer import analyze_audio_features
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    recommendations = None

    if request.method == "POST":
        artist_name = request.form.get("artist_name", "").strip()
        track_name = request.form.get("track_name", "").strip()

        if not artist_name or not track_name:
            error = "Please enter both artist and track name."
        else:
            try:
                print(f"🎶 Fetching Spotify features for {track_name} by {artist_name}...")
                track_data = get_spotify_features(artist_name, track_name)
                result = analyze_audio_features(track_data)

                print("🎧 Getting similar tracks from Last.fm...")
                recommendations = get_recommendations(artist_name, track_name)

            except Exception as e:
                error = f"Error: {e}"
                print(error)

    return render_template("index.html", result=result, error=error, recommendations=recommendations)


if __name__ == "__main__":
    spotify_id = os.getenv("SPOTIFY_CLIENT_ID")
    print(f"SPOTIFY_CLIENT_ID: {'set' if spotify_id else 'not set'}")
    app.run(debug=True)