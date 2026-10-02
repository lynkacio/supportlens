from pathlib import Path

from app.services.paraformer_service import transcribe_audio


def main() -> None:
    audio_file = Path(__file__).resolve().parents[1] / "test_audio" / "test_audiocustomer_call.mp3"
    transcript = transcribe_audio(str(audio_file))
    print("TRANSCRIPT:")
    print(transcript)


if __name__ == "__main__":
    main()