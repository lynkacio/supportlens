const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8000";

export interface UploadTicketsResponse {
  filename: string;
  tickets_processed: number;
  preview: Array<{
    ticket_id: string;
    customer_message: string;
    created_at: string;
  }>;
}

export async function getHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error("Backend health check failed");
  }

  return response.json();
}

export async function uploadTickets(
  file: File,
): Promise<UploadTicketsResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/tickets/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let errorMessage = "Ticket upload failed";

    try {
      const errorData = await response.json();
      if (typeof errorData.detail === "string") {
        errorMessage = errorData.detail;
      }
    } catch {
      // Use the fallback message when the backend response is not JSON.
    }

    throw new Error(errorMessage);
  }

  return response.json();
}