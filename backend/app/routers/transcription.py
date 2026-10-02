import logging
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TicketResponse, TranscriptionResponse
from app.services.llm_service import LLMServiceError
from app.services.paraformer_service import (
    ParaformerServiceError,
    UnsupportedAudioError,
    transcribe_audio,
    validate_audio_file,
)
from app.services.ticket_service import (
    TicketPersistenceError,
    create_analyzed_ticket_from_message,
)

logger = logging.getLogger(__name__)
MAX_AUDIO_FILE_SIZE = 25 * 1024 * 1024
AUDIO_CHUNK_SIZE = 1024 * 1024

router = APIRouter(tags=["transcription"])


@contextmanager
def _temporary_audio_file(file: UploadFile) -> Iterator[Path]:
    temporary_path: Path | None = None
    total_bytes = 0

    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No audio file provided")
        if not validate_audio_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Only MP3 and WAV audio files are accepted",
            )

        extension = Path(file.filename).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as audio_file:
            temporary_path = Path(audio_file.name)
            while chunk := file.file.read(AUDIO_CHUNK_SIZE):
                total_bytes += len(chunk)
                if total_bytes > MAX_AUDIO_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Audio file exceeds 25 MB",
                    )
                audio_file.write(chunk)

        if total_bytes == 0:
            raise HTTPException(status_code=400, detail="Audio file is empty")

        yield temporary_path
    finally:
        try:
            file.file.close()
        except OSError:
            logger.exception("Failed to close uploaded audio file")
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                logger.exception("Failed to remove temporary audio file")


def _transcribe_or_raise(file_path: str) -> str:
    try:
        return transcribe_audio(file_path)
    except UnsupportedAudioError as exc:
        logger.exception("Uploaded audio file is invalid")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ParaformerServiceError as exc:
        logger.exception("Paraformer transcription failed")
        raise HTTPException(
            status_code=502,
            detail="Audio transcription failed",
        ) from exc


@router.post("/api/transcribe", response_model=TranscriptionResponse)
def transcribe_uploaded_audio(
    file: UploadFile | None = File(default=None),
) -> TranscriptionResponse:
    if file is None:
        raise HTTPException(status_code=400, detail="No audio file provided")

    with _temporary_audio_file(file) as temporary_path:
        transcript = _transcribe_or_raise(str(temporary_path))
        return TranscriptionResponse(transcript=transcript)


@router.post(
    "/api/tickets/audio-upload",
    response_model=TicketResponse,
)
def create_ticket_from_audio(
    file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
) -> TicketResponse:
    if file is None:
        raise HTTPException(status_code=400, detail="No audio file provided")

    with _temporary_audio_file(file) as temporary_path:
        transcript = _transcribe_or_raise(str(temporary_path))
        try:
            return create_analyzed_ticket_from_message(db, transcript)
        except LLMServiceError as exc:
            logger.exception("DeepSeek analysis failed for uploaded audio")
            raise HTTPException(
                status_code=502,
                detail="Ticket analysis failed",
            ) from exc
        except TicketPersistenceError as exc:
            logger.exception("Failed to save audio-created ticket")
            raise HTTPException(
                status_code=500,
                detail="Ticket could not be saved",
            ) from exc