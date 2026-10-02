import os
import tempfile
import wave
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://test:test@localhost/test",
)

import app.main as main_module
from app.routers import transcription as transcription_router
from app.services import paraformer_service


def create_wav_file(sample_rate: int = 16000, content: bytes | None = None) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
        file_path = audio_file.name

    with wave.open(file_path, "wb") as audio_file:
        audio_file.setnchannels(1)
        audio_file.setsampwidth(2)
        audio_file.setframerate(sample_rate)
        audio_file.writeframes(content if content is not None else b"\x00\x00" * sample_rate)

    return file_path


def make_fake_asr(response, received: dict):
    class FakeRecognition:
        def __init__(self, **kwargs):
            received.update(kwargs)

        def call(self, file_path):
            received["file_path"] = file_path
            return response

    return SimpleNamespace(
        Recognition=FakeRecognition,
        RecognitionCallback=lambda: None,
    )


def test_mp3_and_wav_extensions_are_supported():
    assert paraformer_service.validate_audio_file("call.mp3")
    assert paraformer_service.validate_audio_file("call.wav")
    assert not paraformer_service.validate_audio_file("call.txt")


def test_transcribe_wav_uses_local_file_and_returns_sentences(monkeypatch):
    file_path = create_wav_file()
    received = {}
    response = SimpleNamespace(
        status_code=200,
        output={"sentence": [{"text": "First."}, {"text": "Second."}]},
    )
    monkeypatch.setattr(
        paraformer_service,
        "_get_client",
        lambda: make_fake_asr(response, received),
    )

    try:
        transcript = paraformer_service.transcribe_audio(file_path)
    finally:
        Path(file_path).unlink(missing_ok=True)

    assert transcript == "First. Second."
    assert received["model"] == "paraformer-realtime-v2"
    assert received["format"] == "wav"
    assert received["sample_rate"] == 16000
    assert received["file_path"] == file_path


def test_transcribe_mp3_uses_mutagen_sample_rate(monkeypatch):
    file_path = Path(__file__).resolve().parents[1] / "test_audio" / "test_audiocustomer_call.mp3"
    received = {}
    response = SimpleNamespace(
        status_code=200,
        output={"sentence": [{"text": "Recognized MP3."}]},
    )
    monkeypatch.setattr(
        paraformer_service,
        "_get_client",
        lambda: make_fake_asr(response, received),
    )

    assert paraformer_service.transcribe_audio(str(file_path)) == "Recognized MP3."
    assert received["format"] == "mp3"
    assert received["sample_rate"] == 8000
    assert received["file_path"] == str(file_path)


def test_transcribe_rejects_invalid_audio_before_provider_call(monkeypatch):
    file_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    file_path.write(b"not a wave file")
    file_path.close()
    monkeypatch.setattr(
        paraformer_service,
        "_get_client",
        lambda: pytest.fail("provider must not be initialized for corrupt audio"),
    )

    try:
        with pytest.raises(paraformer_service.UnsupportedAudioError):
            paraformer_service.transcribe_audio(file_path.name)
    finally:
        Path(file_path.name).unlink(missing_ok=True)


def test_transcribe_rejects_unsupported_wav_sample_rate():
    file_path = create_wav_file(sample_rate=44100)
    try:
        with pytest.raises(paraformer_service.UnsupportedAudioError):
            paraformer_service.transcribe_audio(file_path)
    finally:
        Path(file_path).unlink(missing_ok=True)


def test_route_returns_400_when_file_is_missing():
    response = TestClient(main_module.app).post("/api/transcribe")
    assert response.status_code == 400


def test_route_rejects_unsupported_extension():
    response = TestClient(main_module.app).post(
        "/api/transcribe",
        files={"file": ("call.txt", b"audio", "text/plain")},
    )
    assert response.status_code == 400


def test_route_rejects_empty_upload():
    response = TestClient(main_module.app).post(
        "/api/transcribe",
        files={"file": ("call.mp3", b"", "audio/mpeg")},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [("call.mp3", "audio/mpeg"), ("call.wav", "audio/wav")],
)
def test_route_preserves_extension_and_cleans_temp_file(
    monkeypatch,
    filename: str,
    content_type: str,
):
    received = {}

    def fake_transcribe(file_path: str) -> str:
        temporary_path = Path(file_path)
        received["path"] = temporary_path
        received["suffix"] = temporary_path.suffix
        received["contents"] = temporary_path.read_bytes()
        return "Transcript text"

    monkeypatch.setattr(transcription_router, "transcribe_audio", fake_transcribe)
    response = TestClient(main_module.app).post(
        "/api/transcribe",
        files={"file": (filename, b"audio bytes", content_type)},
    )

    assert response.status_code == 200
    assert response.json() == {"transcript": "Transcript text"}
    assert received["suffix"] == Path(filename).suffix
    assert received["contents"] == b"audio bytes"
    assert not received["path"].exists()


def test_route_returns_413_and_cleans_temp_file(monkeypatch):
    monkeypatch.setattr(transcription_router, "MAX_AUDIO_FILE_SIZE", 3)
    temporary_paths = []
    original_named_temporary_file = transcription_router.tempfile.NamedTemporaryFile

    def capture_temporary_file(*args, **kwargs):
        temporary_file = original_named_temporary_file(*args, **kwargs)
        temporary_paths.append(Path(temporary_file.name))
        return temporary_file

    monkeypatch.setattr(
        transcription_router.tempfile,
        "NamedTemporaryFile",
        capture_temporary_file,
    )
    response = TestClient(main_module.app).post(
        "/api/transcribe",
        files={"file": ("call.mp3", b"four", "audio/mpeg")},
    )

    assert response.status_code == 413
    assert temporary_paths
    assert all(not path.exists() for path in temporary_paths)


def test_route_hides_provider_error_and_cleans_temp_file(monkeypatch):
    temporary_paths = []

    def fail_transcription(file_path: str) -> str:
        temporary_paths.append(Path(file_path))
        raise paraformer_service.ParaformerServiceError("private provider detail")

    monkeypatch.setattr(transcription_router, "transcribe_audio", fail_transcription)
    response = TestClient(main_module.app).post(
        "/api/transcribe",
        files={"file": ("call.wav", b"audio", "audio/wav")},
    )

    assert response.status_code == 502
    assert response.json() == {"detail": "Audio transcription failed"}
    assert all(not path.exists() for path in temporary_paths)


def test_health_ticket_routes_and_local_cors_are_preserved():
    client = TestClient(main_module.app)
    health_response = client.get("/health")
    preflight_response = client.options(
        "/api/transcribe",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    paths = client.get("/openapi.json").json()["paths"]

    assert health_response.status_code == 200
    assert preflight_response.status_code == 200
    assert preflight_response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "/api/tickets/upload" in paths
    assert "/api/tickets/analyze" in paths