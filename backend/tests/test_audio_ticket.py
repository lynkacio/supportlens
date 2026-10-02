import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://test:test@localhost/test",
)

from app.database import Base, get_db
from app.enums import Category, Priority
from app.models import Ticket
from app.routers import transcription as transcription_router
from app.routers import transcription as transcription_router
from app.services import paraformer_service, ticket_service
from app.services.llm_service import LLMServiceError, TicketAnalysis
import app.main as main_module


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def valid_analysis() -> TicketAnalysis:
    return TicketAnalysis(
        category=Category.account,
        priority=Priority.high,
        summary="Customer cannot sign in.",
        suggested_response="We will help restore your account access.",
    )


def test_create_analyzed_ticket_persists_all_fields_once(db_session, monkeypatch):
    calls = []
    commit_count = 0
    original_commit = db_session.commit

    def fake_analyze(message: str) -> TicketAnalysis:
        calls.append(message)
        return valid_analysis()

    def count_commit() -> None:
        nonlocal commit_count
        commit_count += 1
        original_commit()

    monkeypatch.setattr(ticket_service, "analyze_ticket", fake_analyze)
    monkeypatch.setattr(db_session, "commit", count_commit)

    ticket = ticket_service.create_analyzed_ticket_from_message(
        db_session,
        "Customer says they cannot log in to their account.",
    )

    assert calls == [ticket.customer_message]
    assert commit_count == 1
    assert ticket.ticket_id.startswith("AUDIO-")
    assert ticket.category == "account"
    assert ticket.priority == "high"
    assert ticket.summary == "Customer cannot sign in."
    assert ticket.suggested_response == "We will help restore your account access."
    assert db_session.query(Ticket).count() == 1


def test_analysis_failure_does_not_create_a_ticket(db_session, monkeypatch):
    def fail_analysis(_: str) -> TicketAnalysis:
        raise LLMServiceError("DeepSeek unavailable")

    monkeypatch.setattr(ticket_service, "analyze_ticket", fail_analysis)

    with pytest.raises(LLMServiceError):
        ticket_service.create_analyzed_ticket_from_message(db_session, "Transcript")

    assert db_session.query(Ticket).count() == 0


def test_database_failure_rolls_back_audio_ticket(db_session, monkeypatch):
    rollback_count = 0
    original_rollback = db_session.rollback

    def fail_commit() -> None:
        raise SQLAlchemyError("database unavailable")

    def count_rollback() -> None:
        nonlocal rollback_count
        rollback_count += 1
        original_rollback()

    monkeypatch.setattr(ticket_service, "analyze_ticket", lambda _: valid_analysis())
    monkeypatch.setattr(db_session, "commit", fail_commit)
    monkeypatch.setattr(db_session, "rollback", count_rollback)

    with pytest.raises(ticket_service.TicketPersistenceError):
        ticket_service.create_analyzed_ticket_from_message(db_session, "Transcript")

    assert rollback_count == 1
    assert db_session.query(Ticket).count() == 0


@pytest.fixture
def api_client(db_session):
    def override_get_db():
        yield db_session

    main_module.app.dependency_overrides[get_db] = override_get_db
    with TestClient(main_module.app) as client:
        yield client
    main_module.app.dependency_overrides.pop(get_db, None)


def test_audio_upload_creates_analyzed_ticket_once(
    api_client,
    db_session,
    monkeypatch,
):
    transcript = "Customer says they cannot log in to their account."
    received = {}
    analysis_calls = []

    def fake_transcribe(file_path: str) -> str:
        temporary_path = Path(file_path)
        received["path"] = temporary_path
        received["suffix"] = temporary_path.suffix
        received["contents"] = temporary_path.read_bytes()
        return transcript

    def fake_analyze(customer_message: str) -> TicketAnalysis:
        analysis_calls.append(customer_message)
        return valid_analysis()

    monkeypatch.setattr(transcription_router, "transcribe_audio", fake_transcribe)
    monkeypatch.setattr(ticket_service, "analyze_ticket", fake_analyze)

    response = api_client.post(
        "/api/tickets/audio-upload",
        files={"file": ("customer_call.mp3", b"mp3 bytes", "audio/mpeg")},
    )

    payload = response.json()
    assert response.status_code == 200
    assert payload["ticket_id"].startswith("AUDIO-")
    assert payload["customer_message"] == transcript
    assert payload["category"] == "account"
    assert payload["priority"] == "high"
    assert payload["summary"] == "Customer cannot sign in."
    assert payload["suggested_response"] == "We will help restore your account access."
    assert payload["created_at"]
    assert payload["processed_at"]
    assert analysis_calls == [transcript]
    assert received["suffix"] == ".mp3"
    assert received["contents"] == b"mp3 bytes"
    assert not received["path"].exists()
    assert db_session.query(Ticket).count() == 1


def test_transcription_failure_does_not_analyze_or_create_ticket(
    api_client,
    db_session,
    monkeypatch,
):
    temporary_paths = []

    def fail_transcription(file_path: str) -> str:
        temporary_paths.append(Path(file_path))
        raise paraformer_service.ParaformerServiceError("provider detail")

    monkeypatch.setattr(transcription_router, "transcribe_audio", fail_transcription)
    monkeypatch.setattr(
        ticket_service,
        "analyze_ticket",
        lambda _: pytest.fail("analysis must not run after transcription failure"),
    )

    response = api_client.post(
        "/api/tickets/audio-upload",
        files={"file": ("customer_call.wav", b"wav bytes", "audio/wav")},
    )

    assert response.status_code == 502
    assert response.json() == {"detail": "Audio transcription failed"}
    assert db_session.query(Ticket).count() == 0
    assert all(not path.exists() for path in temporary_paths)


def test_analysis_failure_does_not_create_ticket_and_cleans_upload(
    api_client,
    db_session,
    monkeypatch,
):
    temporary_paths = []

    def transcribe(file_path: str) -> str:
        temporary_paths.append(Path(file_path))
        return "Transcript"

    def fail_analysis(_: str) -> TicketAnalysis:
        raise LLMServiceError("provider detail")

    monkeypatch.setattr(transcription_router, "transcribe_audio", transcribe)
    monkeypatch.setattr(ticket_service, "analyze_ticket", fail_analysis)

    response = api_client.post(
        "/api/tickets/audio-upload",
        files={"file": ("customer_call.wav", b"wav bytes", "audio/wav")},
    )

    assert response.status_code == 502
    assert response.json() == {"detail": "Ticket analysis failed"}
    assert db_session.query(Ticket).count() == 0
    assert all(not path.exists() for path in temporary_paths)


def test_corrupt_audio_returns_400_and_cleans_upload(
    api_client,
    db_session,
    monkeypatch,
):
    temporary_paths = []

    def reject_corrupt_audio(file_path: str) -> str:
        temporary_paths.append(Path(file_path))
        raise paraformer_service.UnsupportedAudioError("invalid WAV")

    monkeypatch.setattr(
        transcription_router,
        "transcribe_audio",
        reject_corrupt_audio,
    )
    monkeypatch.setattr(
        ticket_service,
        "analyze_ticket",
        lambda _: pytest.fail("analysis must not run for corrupt audio"),
    )

    response = api_client.post(
        "/api/tickets/audio-upload",
        files={"file": ("corrupt.wav", b"not a wave file", "audio/wav")},
    )

    assert response.status_code == 400
    assert db_session.query(Ticket).count() == 0
    assert all(not path.exists() for path in temporary_paths)


def test_audio_ticket_database_failure_rolls_back_and_cleans_upload(
    api_client,
    db_session,
    monkeypatch,
):
    temporary_paths = []

    def transcribe(file_path: str) -> str:
        temporary_paths.append(Path(file_path))
        return "Transcript"

    def fail_commit() -> None:
        raise SQLAlchemyError("database detail")

    monkeypatch.setattr(transcription_router, "transcribe_audio", transcribe)
    monkeypatch.setattr(ticket_service, "analyze_ticket", lambda _: valid_analysis())
    monkeypatch.setattr(db_session, "commit", fail_commit)

    response = api_client.post(
        "/api/tickets/audio-upload",
        files={"file": ("customer_call.wav", b"wav bytes", "audio/wav")},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Ticket could not be saved"}
    assert db_session.query(Ticket).count() == 0
    assert all(not path.exists() for path in temporary_paths)


def test_audio_ticket_rejects_missing_empty_unsupported_and_oversized_uploads(
    api_client,
    monkeypatch,
):
    assert api_client.post("/api/tickets/audio-upload").status_code == 400
    assert api_client.post(
        "/api/tickets/audio-upload",
        files={"file": ("call.txt", b"text", "text/plain")},
    ).status_code == 400
    assert api_client.post(
        "/api/tickets/audio-upload",
        files={"file": ("call.mp3", b"", "audio/mpeg")},
    ).status_code == 400

    monkeypatch.setattr(transcription_router, "MAX_AUDIO_FILE_SIZE", 3)
    response = api_client.post(
        "/api/tickets/audio-upload",
        files={"file": ("call.mp3", b"four", "audio/mpeg")},
    )
    assert response.status_code == 413


def test_pure_transcription_endpoint_still_returns_transcript_only(
    api_client,
    db_session,
    monkeypatch,
):
    monkeypatch.setattr(
        transcription_router,
        "transcribe_audio",
        lambda _: "Standalone transcript",
    )
    monkeypatch.setattr(
        ticket_service,
        "analyze_ticket",
        lambda _: pytest.fail("pure transcription must not run ticket analysis"),
    )

    response = api_client.post(
        "/api/transcribe",
        files={"file": ("customer_call.mp3", b"mp3 bytes", "audio/mpeg")},
    )

    assert response.status_code == 200
    assert response.json() == {"transcript": "Standalone transcript"}
    assert db_session.query(Ticket).count() == 0
