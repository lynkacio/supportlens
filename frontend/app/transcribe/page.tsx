'use client';

import { FormEvent, useState } from "react";
import {
  AlertCircle,
  AudioLines,
  CheckCircle2,
  FileAudio,
  UploadCloud,
} from "lucide-react";

import PageContainer from "@/components/PageContainer";
import { createAudioTicket, type TicketResponse } from "@/lib/api";

const SUPPORTED_AUDIO_EXTENSIONS = [".mp3", ".wav"];

function isSupportedAudioFile(file: File): boolean {
  const filename = file.name.toLowerCase();
  return SUPPORTED_AUDIO_EXTENSIONS.some((extension) =>
    filename.endsWith(extension),
  );
}

export default function TranscribePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [transcript, setTranscript] = useState("");
  const [createdTicket, setCreatedTicket] = useState<TicketResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isTranscribing, setIsTranscribing] = useState(false);

  function handleFileChange(file: File | undefined) {
    setTranscript("");
    setCreatedTicket(null);
    setErrorMessage("");

    if (file && !isSupportedAudioFile(file)) {
      setSelectedFile(null);
      setErrorMessage("Choose an MP3 or PCM WAV file at 8 kHz or 16 kHz.");
      return;
    }

    setSelectedFile(file ?? null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile || isTranscribing) return;

    setIsTranscribing(true);
    setTranscript("");
    setCreatedTicket(null);
    setErrorMessage("");

    try {
      const ticket = await createAudioTicket(selectedFile);
      setTranscript(ticket.customer_message);
      setCreatedTicket(ticket);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Audio ticket creation failed",
      );
    } finally {
      setIsTranscribing(false);
    }
  }

  return (
    <PageContainer>
      <header className="border-b border-slate-200 pb-7">
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal-700">
          Workspace / Audio
        </p>
        <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
          Transcribe audio
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          Transcribe a customer call, analyze it, and create a support ticket.
        </p>
      </header>

      <div className="mt-7 grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
        <form
          onSubmit={handleSubmit}
          className="border border-slate-200 bg-white p-6 shadow-[0_14px_40px_rgba(15,23,42,0.05)] sm:p-8"
        >
          <div className="flex items-start gap-4">
            <div className="flex size-11 shrink-0 items-center justify-center rounded-lg bg-teal-50 text-teal-700">
              <AudioLines size={21} />
            </div>
            <div>
              <p className="text-sm font-semibold text-teal-700">01 / Select recording</p>
              <h2 className="mt-1 text-xl font-semibold tracking-tight text-slate-950">
                Add an audio file
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Supports MP3 or 16-bit PCM WAV at 8 kHz or 16 kHz, up to 25 MB.
              </p>
            </div>
          </div>

          <label
            htmlFor="audio-file"
            className="mt-7 flex min-h-36 cursor-pointer flex-col items-center justify-center border border-dashed border-slate-300 bg-slate-50 px-5 py-6 text-center transition hover:border-teal-500 hover:bg-teal-50/40"
          >
            <UploadCloud size={25} className="text-teal-700" />
            <span className="mt-3 text-sm font-semibold text-slate-800">
              {selectedFile ? selectedFile.name : "Choose an audio file"}
            </span>
            <span className="mt-1 text-xs text-slate-500">
              {selectedFile
                ? `${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB`
                : "Select from your device"}
            </span>
            <input
              id="audio-file"
              name="file"
              type="file"
              accept={SUPPORTED_AUDIO_EXTENSIONS.join(",")}
              onChange={(event) => handleFileChange(event.target.files?.[0])}
              className="sr-only"
            />
          </label>

          <button
            type="submit"
            disabled={!selectedFile || isTranscribing}
            className="mt-6 inline-flex items-center gap-2 rounded-lg bg-teal-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {isTranscribing
              ? "Transcribing and analyzing..."
              : "Analyze audio and create ticket"}
            {!isTranscribing && <AudioLines size={17} />}
          </button>
        </form>

        <div className="space-y-6">
          <section
            aria-labelledby="transcript-heading"
            className="border border-slate-200 bg-white p-6"
          >
            <div className="flex items-center gap-3">
              <div className="flex size-9 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                {transcript ? <CheckCircle2 size={18} /> : <FileAudio size={18} />}
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">
                  Output
                </p>
                <h2
                  id="transcript-heading"
                  className="mt-1 text-lg font-semibold text-slate-950"
                >
                  Transcript
                </h2>
              </div>
            </div>
            <div
              className="mt-5 max-h-[28rem] min-h-24 overflow-y-auto whitespace-pre-wrap text-sm leading-6 text-slate-700"
              aria-live="polite"
            >
              {transcript || (
                <span className="text-slate-400">
                  Your transcription will appear here.
                </span>
              )}
            </div>
          </section>

          {createdTicket && (
            <section
              aria-labelledby="ticket-created-heading"
              className="border border-emerald-200 bg-emerald-50/60 p-6"
              role="status"
            >
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-emerald-700">
                Ticket created
              </p>
              <h2
                id="ticket-created-heading"
                className="mt-1 text-lg font-semibold text-slate-950"
              >
                {createdTicket.ticket_id}
              </h2>
              <dl className="mt-4 space-y-3 text-sm">
                <div className="flex gap-2">
                  <dt className="font-semibold text-slate-700">Category</dt>
                  <dd className="text-slate-600">{createdTicket.category}</dd>
                </div>
                <div className="flex gap-2">
                  <dt className="font-semibold text-slate-700">Priority</dt>
                  <dd className="text-slate-600">{createdTicket.priority}</dd>
                </div>
                <div>
                  <dt className="font-semibold text-slate-700">Summary</dt>
                  <dd className="mt-1 leading-6 text-slate-600">
                    {createdTicket.summary}
                  </dd>
                </div>
                <div>
                  <dt className="font-semibold text-slate-700">
                    Suggested response
                  </dt>
                  <dd className="mt-1 leading-6 text-slate-600">
                    {createdTicket.suggested_response}
                  </dd>
                </div>
              </dl>
            </section>
          )}

          {errorMessage && (
            <section
              aria-label="Transcription error"
              className="border border-amber-200 bg-amber-50 p-5"
              role="alert"
            >
              <div className="flex items-start gap-3 text-amber-800">
                <AlertCircle size={18} className="mt-0.5 shrink-0" />
                <p className="text-sm leading-6">{errorMessage}</p>
              </div>
            </section>
          )}
        </div>
      </div>
    </PageContainer>
  );
}