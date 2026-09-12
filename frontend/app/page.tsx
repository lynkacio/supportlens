'use client';

import { FormEvent, useState } from "react";

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
    <main className="flex-1 bg-slate-50 px-6 py-12 text-slate-900">
      <div className="mx-auto max-w-2xl">
        <header className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight">SupportLens</h1>
          <p className="mt-3 text-lg text-slate-600">
            Upload your support-ticket data in CSV format to get started.
          </p>
        </header>

        <form
          onSubmit={handleSubmit}
          className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
        >
          <h2 className="text-xl font-semibold">Upload support tickets</h2>
          <p className="mt-2 text-sm text-slate-600">
            Choose a CSV file containing your customer support tickets.
          </p>

          <label
            htmlFor="ticket-file"
            className="mt-6 block text-sm font-medium text-slate-700"
          >
            CSV file
          </label>
          <input
            id="ticket-file"
            name="ticket-file"
            type="file"
            accept=".csv,text/csv"
            onChange={(event) => handleFileChange(event.target.files?.[0])}
            className="mt-2 block w-full cursor-pointer rounded-md border border-slate-300 bg-slate-50 text-sm text-slate-700 file:mr-4 file:border-0 file:bg-slate-800 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-slate-700"
          />
          <p className="mt-3 text-sm text-slate-600" aria-live="polite">
            {selectedFileName
              ? `Selected file: ${selectedFileName}`
              : "No file selected"}
          </p>

          <button
            type="submit"
            disabled={!selectedFile || isUploading}
            className="mt-6 rounded-md bg-slate-800 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {isUploading ? "Uploading..." : "Upload"}
          </button>
        </form>

        <section
          aria-labelledby="results-heading"
          className="mt-6 rounded-lg border border-dashed border-slate-300 bg-white p-6"
        >
          <h2 id="results-heading" className="text-lg font-semibold">
            Results
          </h2>
          <div className="mt-4 min-h-20" aria-live="polite">
            {uploadResult && (
              <p>
                Successfully processed {uploadResult.tickets_processed} ticket
                {uploadResult.tickets_processed === 1 ? "" : "s"}.
              </p>
            )}
          </div>
        </section>

        <section
          aria-labelledby="errors-heading"
          className="mt-4 rounded-lg border border-dashed border-slate-300 bg-white p-6"
        >
          <h2 id="errors-heading" className="text-lg font-semibold">
            Errors
          </h2>
          <div className="mt-4 min-h-20 text-red-700" aria-live="assertive">
            {errorMessage && <p>{errorMessage}</p>}
          </div>
        </section>
      </div>
    </main>
  );
}