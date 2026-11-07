import os
import io
import tempfile
from typing import Dict, Any, Tuple, Optional

class SpeechService:
    def __init__(self):
        self._model = None
        self._model_name = "base"
        self._whisper_available = False
        self._check_availability()

    def _check_availability(self):
        try:
            import faster_whisper
            self._whisper_available = True
        except ImportError:
            self._whisper_available = False

    def is_available(self) -> bool:
        return self._whisper_available

    def get_status(self) -> Dict[str, Any]:
        return {
            "available": self._whisper_available,
            "engine": "faster-whisper" if self._whisper_available else "web-speech-api-fallback",
            "message": "Faster-Whisper is ready for offline transcription." if self._whisper_available else (
                "Faster-Whisper is not installed. Native Browser Web Speech API is active for English, Hindi, and Marathi voice recognition. "
                "To enable server-side offline Whisper, run: pip install faster-whisper"
            )
        }

    def transcribe_audio_bytes(self, audio_bytes: bytes, filename: str = "audio.wav") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Transcribes audio bytes to text using faster-whisper if installed, or explains fallback.
        """
        if not self._whisper_available:
            return False, "", {
                "error": "faster-whisper not installed",
                "message": (
                    "Server-side Faster-Whisper is not installed. "
                    "Use the built-in browser Web Speech API (click the mic button in Chrome/Edge) "
                    "or type your command in the text box."
                )
            }

        try:
            import faster_whisper
            if self._model is None:
                # Load multilingual model
                self._model = faster_whisper.WhisperModel(self._model_name, device="cpu", compute_type="int8")

            # Write temporary audio file
            ext = os.path.splitext(filename)[1] or ".wav"
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_audio:
                temp_audio.write(audio_bytes)
                temp_path = temp_audio.name

            try:
                segments, info = self._model.transcribe(temp_path, beam_size=5)
                transcribed_text = " ".join([seg.text for seg in segments]).strip()
                detected_lang = info.language
                return True, transcribed_text, {
                    "language": detected_lang,
                    "probability": info.language_probability
                }
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            return False, "", {"error": str(e), "message": f"Transcription failed: {str(e)}"}

speech_service = SpeechService()
