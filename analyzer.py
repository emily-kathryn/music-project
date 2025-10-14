def key_to_name(key_num, mode=None):
    """Convert Spotify key integer (0–11) to musical note."""
    key_map = {
        0: "C", 1: "C♯ / D♭", 2: "D", 3: "D♯ / E♭", 4: "E",
        5: "F", 6: "F♯ / G♭", 7: "G", 8: "G♯ / A♭", 9: "A",
        10: "A♯ / B♭", 11: "B"
    }

    if key_num is None or key_num not in key_map:
        return "Unknown"

    note = key_map[key_num]
    if mode == 1:
        return f"{note} major"
    elif mode == 0:
        return f"{note} minor"
    else:
        return note


def analyze_audio_features(track_data):
    """Prepare track analysis results for display in HTML."""
    result = {}

    # Copy main track details from Spotify data
    result["track"] = track_data.get("track")
    result["artist"] = track_data.get("artist")
    result["album_art"] = track_data.get("album_art")
    result["spotify_url"] = track_data.get("spotify_url")
    result["preview_url"] = track_data.get("preview_url")
    result["popularity"] = track_data.get("popularity")

    # Convert tempo and loudness
    tempo = track_data.get("tempo")
    result["tempo"] = round(tempo, 2) if tempo else None

    loudness = track_data.get("loudness")
    result["loudness"] = round(loudness, 2) if loudness else None

    # Convert duration from ms to minutes
    duration_ms = track_data.get("duration_ms")
    if duration_ms:
        result["duration_minutes"] = round(duration_ms / 60000, 2)

    # Energy
    result["energy"] = track_data.get("energy")

    # Convert numeric key and mode → readable name
    key_val = track_data.get("key")
    mode_val = track_data.get("mode")
    result["key"] = key_to_name(key_val, mode_val)

    return result