# ============================================================
# transcriber.py — Whisper Audio Transcription
# Ported from Blocks 3+4 (Colab)
# ============================================================

import whisper
import tempfile
import os

# ── Load model once at startup (downloads ~1.4GB first time) ─
print("⏳ Loading Whisper model... (this may take a moment)")
whisper_model = whisper.load_model("medium")
print("✅ Whisper model loaded!")


def transcribe_audio(audio_bytes: bytes, file_extension: str = "webm") -> dict:
    """
    Receives raw audio bytes, saves to a temp file,
    runs Whisper, returns the transcript.

    Parameters
    ----------
    audio_bytes    : raw bytes from the uploaded audio file
    file_extension : format of the audio (webm, wav, mp3, etc.)

    Returns
    -------
    dict with keys: transcript, language, duration
    """

    # ── Save bytes to a temporary file ──────────────────────
    with tempfile.NamedTemporaryFile(
        suffix=f".{file_extension}",
        delete=False
    ) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        # ── Run Whisper ──────────────────────────────────────
        result = whisper_model.transcribe(tmp_path)

        return {
            "transcript": result["text"].strip(),
            "language"  : result.get("language", "unknown"),
        }

    finally:
        # ── Always clean up the temp file ───────────────────
        os.remove(tmp_path)