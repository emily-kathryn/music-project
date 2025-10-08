import librosa
import numpy as np

def analyze_audio(file_path):
    y, sr = librosa.load(file_path)

    # --- Tempo (BPM) ---
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray):
        tempo = float(tempo.mean())

    # --- Key detection ---
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    key_index = np.argmax(chroma_mean)
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    key = keys[key_index]

    # --- Energy ---
    rms = librosa.feature.rms(y=y)
    avg_energy = float(np.mean(rms))

    # --- Loudness (in decibels) ---
    loudness_db = librosa.amplitude_to_db(rms, ref=np.max)
    avg_loudness_db = float(np.mean(loudness_db))

    # --- Duration ---
    duration_sec = librosa.get_duration(y=y, sr=sr)
    duration_min = round(duration_sec / 60, 2)

    return {
        "tempo": round(float(tempo)),
        "key": key,
        "energy": round(avg_energy, 4),
        "loudness_db": round(avg_loudness_db, 2),
        "duration_minutes": duration_min
    }