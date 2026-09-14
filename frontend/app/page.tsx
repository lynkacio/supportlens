'use client';

import { FormEvent, useState } from "react";
import {
  AlertCircle,
  ArrowUpRight,
  CheckCircle2,
  FileText,
  UploadCloud,
} from "lucide-react";

import { uploadTickets, UploadTicketsResponse } from "@/lib/api";

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFileName, setSelectedFileName] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] =
    useState<UploadTicketsResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  function handleFileChange(file: File | undefined) {
    setSelectedFile(file ?? null);
    setSelectedFileName(file?.name ?? "");
    setUploadResult(null);
    setErrorMessage("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedFile || isUploading) {
      return;
    }

    setIsUploading(true);
    setUploadResult(null);
    setErrorMessage("");

    try {
      const result = await uploadTickets(selectedFile);
      setUploadResult(result);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Ticket upload failed",
      );
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <main className="min-h-screen px-5 py-8 text-slate-900 sm:px-8 lg:px-12 lg:py-10">
      <div className="mx-auto max-w-6xl">
        <header className="flex flex-col justify-between gap-5 border-b border-slate-200 pb-8 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">
              Workspace / Overview
            </p>
            <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              Turn ticket volume into clarity
            </h1>
            <p className="mt-3 max-w-xl text-base leading-7 text-slate-600">
              Upload a support-ticket CSV to prepare your team&apos;s next view of customer pain points.
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <span className="size-2 rounded-full bg-emerald-500" />
            Local workspace
          </div>
        </header>

        <div className="mt-8 grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
          <form
            onSubmit={handleSubmit}
            className="border border-slate-200 bg-white p-6 shadow-[0_14px_40px_rgba(15,23,42,0.05)] sm:p-8"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-teal-700">01 / Import data</p>
                <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">
                  Upload support tickets
                </h2>
                <p className="mt-2 max-w-lg text-sm leading-6 text-slate-600">
                  Start with a CSV containing your ticket ID, customer message, and creation date.
                </p>
              </div>
              <div className="hidden size-11 items-center justify-center rounded-xl bg-teal-50 text-teal-700 sm:flex">
                <UploadCloud size={21} />
              </div>
            </div>

            <label htmlFor="ticket-file" className="mt-8 block text-sm font-semibold text-slate-800">
              CSV file
            </label>
            <input
              id="ticket-file"
              name="ticket-file"
              type="file"
              accept=".csv,text/csv"
              onChange={(event) => handleFileChange(event.target.files?.[0])}
              className="mt-3 block w-full cursor-pointer rounded-lg border border-dashed border-slate-300 bg-slate-50 text-sm text-slate-700 file:mr-4 file:border-0 file:bg-slate-900 file:px-4 file:py-2.5 file:text-sm file:font-semibold file:text-white hover:border-teal-500 hover:file:bg-teal-800"
            />
            <p className="mt-3 flex items-center gap-2 text-sm text-slate-500" aria-live="polite">
              <FileText size={16} />
              {selectedFileName ? `Selected file: ${selectedFileName}` : "No file selected"}
            </p>

            <button
              type="submit"
              disabled={!selectedFile || isUploading}
              className="mt-8 inline-flex items-center gap-2 rounded-lg bg-teal-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              {isUploading ? "Uploading..." : "Upload"}
              {!isUploading && <ArrowUpRight size={16} />}
            </button>
          </form>

          <div className="space-y-6">
            <section aria-labelledby="results-heading" className="border border-slate-200 bg-white p-6">
              <div className="flex items-center gap-3">
                <div className="flex size-9 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                  <CheckCircle2 size={18} />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">Status</p>
                  <h2 id="results-heading" className="mt-1 text-lg font-semibold text-slate-950">Results</h2>
                </div>
              </div>
              <div className="mt-6 min-h-20 text-sm text-slate-600" aria-live="polite">
                {uploadResult ? (
                  <p className="leading-6">
                    Successfully processed <strong className="text-slate-950">{uploadResult.tickets_processed}</strong> ticket{uploadResult.tickets_processed === 1 ? "" : "s"}.
                  </p>
                ) : (
                  <p className="leading-6 text-slate-400">Your import summary will appear here.</p>
                )}
              </div>
            </section>

            <section aria-labelledby="errors-heading" className="border border-slate-200 bg-white p-6">
              <div className="flex items-center gap-3">
                <div className="flex size-9 items-center justify-center rounded-lg bg-amber-50 text-amber-700">
                  <AlertCircle size={18} />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">Needs attention</p>
                  <h2 id="errors-heading" className="mt-1 text-lg font-semibold text-slate-950">Errors</h2>
                </div>
              </div>
              <div className="mt-6 min-h-20 text-sm text-red-700" aria-live="assertive">
                {errorMessage ? <p className="leading-6">{errorMessage}</p> : <p className="leading-6 text-slate-400">Validation messages will appear here.</p>}
              </div>
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}