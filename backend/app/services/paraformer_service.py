"""DashScope Paraformer realtime speech-to-text service."""

from __future__ import annotations

import logging
import time
import wave
from pathlib import Path

from mutagen import MutagenError
from mutagen.mp3 import MP3

from app.config import get_dashscope_api_key

logger = logging.getLogger(__name__)

MODEL = "paraformer-realtime-v2"
MAX_ATTEMPTS = 3
BASE_BACKOFF_SECONDS = 1.0
SUPPORTED_AUDIO_TYPES = {".mp3", ".wav"}
SUPPORTED_SAMPLE_RATES = {8000, 16000}


class UnsupportedAudioError(ValueError):
    """Raised when an uploaded audio file is unsupported or invalid."""


class ParaformerServiceError(Exception):
    """Raised when DashScope transcription fails."""


def validate_audio_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_AUDIO_TYPES


def _get_audio_metadata(file_path: str) -> tuple[str, int]:
    audio_format = Path(file_path).suffix.lower().lstrip(".")
    if audio_format == "wav":
        try:
            with wave.open(file_path, "rb") as audio_file:
                if audio_file.getcomptype() != "NONE" or audio_file.getsampwidth() != 2:
                    raise UnsupportedAudioError(
                        "WAV audio must be uncompressed 16-bit PCM"
                    )
                sample_rate = audio_file.getframerate()
        except (EOFError, OSError, wave.Error) as exc:
            raise UnsupportedAudioError("Audio must be a valid PCM WAV file") from exc
    elif audio_format == "mp3":
        try:
            sample_rate = int(MP3(file_path).info.sample_rate)
        except (MutagenError, OSError, TypeError, ValueError) as exc:
            raise UnsupportedAudioError("Audio must be a valid MP3 file") from exc
    else:
        raise UnsupportedAudioError("Only MP3 and WAV audio files are supported")

    if sample_rate not in SUPPORTED_SAMPLE_RATES:
        raise UnsupportedAudioError(
            "Paraformer realtime supports audio sampled at 8000 or 16000 Hz"
        )

    return audio_format, sample_rate


def _get_client():
    try:
        import dashscope

        dashscope.api_key = get_dashscope_api_key()
        return dashscope.audio.asr
    except Exception as exc:
        logger.exception("Failed to initialize DashScope Paraformer")
        raise ParaformerServiceError("Unable to initialize transcription") from exc


def _submit_transcription(
    asr_client,
    file_path: str,
    audio_format: str,
    sample_rate: int,
) -> str:
    recognizer = asr_client.Recognition(
        model=MODEL,
        callback=asr_client.RecognitionCallback(),
        format=audio_format,
        sample_rate=sample_rate,
    )
    response = recognizer.call(file_path)
    if response.status_code != 200:
        raise ParaformerServiceError("DashScope transcription request failed")

    sentences = (response.output or {}).get("sentence", [])
    if isinstance(sentences, dict):
        sentences = [sentences]
    return " ".join(
        sentence.get("text", "").strip()
        for sentence in sentences
        if isinstance(sentence, dict) and sentence.get("text", "").strip()
    )


def transcribe_audio(file_path: str) -> str:
    if not validate_audio_file(file_path):
        raise UnsupportedAudioError("Only MP3 and WAV audio files are supported")

    audio_path = Path(file_path)
    if not audio_path.is_file() or audio_path.stat().st_size == 0:
        raise UnsupportedAudioError("Audio file is missing or empty")

    audio_format, sample_rate = _get_audio_metadata(file_path)
    asr_client = _get_client()
    last_error: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            transcript = _submit_transcription(
                asr_client,
                file_path,
                audio_format,
                sample_rate,
            )
            if not transcript.strip():
                raise ParaformerServiceError("DashScope returned an empty transcript")
            return transcript.strip()
        except Exception as exc:
            last_error = exc
            logger.exception(
                "DashScope Paraformer failed (attempt %d/%d)",
                attempt,
                MAX_ATTEMPTS,
            )
            if attempt < MAX_ATTEMPTS:
                time.sleep(BASE_BACKOFF_SECONDS * attempt)

    raise ParaformerServiceError(
        "Audio transcription failed after retries"
    ) from last_error