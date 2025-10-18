from flask import Flask, render_template, request
from lasfm_features import get_enhanced_features
from recommender import get_recommendations
from analyzer import analyze_audio, analyze_audio_features
from spotify_features import get_spotify_features
import os
import tempfile
from dotenv import load_dotenv

# Optional: allow uploads for local analysis fallback
ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.flac'}

def allowed_file(filename: str):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS

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
        uploaded = request.files.get("audio_file")

        if not artist_name or not track_name:
            error = "Please enter both artist and track name."
        else:
            try:
                # 1) Try Spotify first (real audio features)
                use_spotify = bool(os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET"))
                if use_spotify:
                    try:
                        print(f"🎶 Fetching Spotify features for {track_name} by {artist_name}...")
                        sp = get_spotify_features(artist_name, track_name)
                        result = analyze_audio_features(sp)
                    except Exception as sp_err:
                        print(f"⚠️ Spotify failed: {sp_err}. Falling back to Last.fm estimates.")
                        use_spotify = False

                # 2) Fallback to Last.fm tag-based estimate if Spotify not used/failed
                if not use_spotify:
                    print(f"🎶 Fetching Last.fm features for {track_name} by {artist_name}...")
                    lf = get_enhanced_features(artist_name, track_name)
                    result = {
                        "artist": artist_name,
                        "track": track_name,
                        "key": None,
                        "tempo": lf.get("tempo"),
                        "energy": lf.get("energy"),
                        "loudness_db": None,
                        "duration_minutes": None,
                        "popularity": None,  # keep key for template compatibility
                        "tags": lf.get("tags"),
                        "playcount": lf.get("playcount"),
                        "listeners": lf.get("listeners"),
                    }

                # 3) If a file is uploaded, prefer precise local BPM/key over estimates
                temp_path = None
                try:
                    if uploaded and uploaded.filename and allowed_file(uploaded.filename):
                        # Save to a temp file
                        fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(uploaded.filename)[1])
                        with os.fdopen(fd, 'wb') as f:
                            f.write(uploaded.read())

                        local = analyze_audio(temp_path)
                        # Override with precise local values when available
                        if local.get("tempo"):
                            result["tempo"] = local.get("tempo")
                        if local.get("key"):
                            result["key"] = local.get("key")
                        if not result.get("energy") and local.get("energy"):
                            result["energy"] = local.get("energy")
                        if not result.get("loudness_db") and local.get("loudness_db"):
                            result["loudness_db"] = local.get("loudness_db")
                        if not result.get("duration_minutes") and local.get("duration_minutes"):
                            result["duration_minutes"] = local.get("duration_minutes")
                finally:
                    # Clean up temp file if created
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except Exception:
                            pass

                # Fetch recommendations
                print("🎧 Getting similar tracks from Last.fm...")
                recommendations = get_recommendations(artist_name, track_name)

            except Exception as e:
                error = f"Error: {e}"
                print(error)

    return render_template("index.html", result=result, error=error, recommendations=recommendations)


if __name__ == "__main__":
    app.run(debug=True)