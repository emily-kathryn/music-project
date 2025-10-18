import math

try:
    import librosa
    import numpy as np
except Exception:
    librosa = None
    np = None
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


def analyze_audio(file_path):
    """Analyze a local audio file to estimate tempo, key, energy, loudness (dB), and duration (minutes).

    Returns a dict with keys: tempo (int), key (str), energy (float), loudness_db (float), duration_minutes (float)
    """
    if librosa is None or np is None:
        raise RuntimeError("librosa/numpy not available for local audio analysis")

    # Load audio
    y, sr = librosa.load(file_path, mono=True)

    # Tempo (BPM)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray):
        tempo = float(np.mean(tempo))

    # Key detection via chroma
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    key_index = int(np.argmax(chroma_mean))
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    key_name = keys[key_index % 12]

    # Energy (RMS)
    rms = librosa.feature.rms(y=y)
    avg_energy = float(np.mean(rms))

    # Loudness in dB
    loudness_db = float(np.mean(librosa.amplitude_to_db(rms, ref=np.max)))

    # Duration in minutes
    duration_sec = float(librosa.get_duration(y=y, sr=sr))
    duration_min = round(duration_sec / 60.0, 2)

    return {
        "tempo": int(round(float(tempo))) if tempo else None,
        "key": key_name,
        "energy": round(avg_energy, 4),
        "loudness_db": round(loudness_db, 2),
        "duration_minutes": duration_min,
    }