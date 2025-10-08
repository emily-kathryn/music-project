from flask import Flask, render_template, request
from spotify_features import get_audio_features
from recommender import get_recommendations

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def analyze_and_recommend():
    result = None
    recommendations = []
    error = None

    if request.method == "POST":
        artist = request.form.get("artist_name")
        track = request.form.get("track_name")

        if not artist or not track:
            error = "Please enter both artist and track name."
        else:
            result = get_audio_features(artist, track)
            if not result:
                error = "Song not found on Spotify."
            else:
                recommendations = get_recommendations(result["artist"], result["track"])

    return render_template("index.html", result=result, recommendations=recommendations, error=error)

if __name__ == "__main__":
    app.run(debug=True)