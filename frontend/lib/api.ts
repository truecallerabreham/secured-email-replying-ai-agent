import { clearSessionToken, getSessionToken } from "./session";

export type Message = {
  message_id: string;
  gmail_message_id: string;
  from_address: string;
  to_address?: string | null;
  subject: string;
  body: string;
  snippet: string;
  received_at?: string | null;
  in_reply_to?: string | null;
  references?: string | null;
};

export type Thread = {
  id: string;
  gmail_thread_id: string;
  subject: string;
  participants: string[];
  snippet: string;
  latest_from: string;
  latest_received_at?: string | null;
  messages: Message[];
};

export type DraftReplyResponse = {
  draft_id?: string | null;
  thread_id: string;
  model_name: string;
  draft_text: string;
  storage_backend: string;
  retrieval_sources: string[];
};

export type AuthStatus = {
  authenticated: boolean;
  email?: string | null;
  owner_email?: string | null;
};

export type SendReplyResponse = {
  sent_reply_id?: string | null;
  gmail_message_id: string;
  thread_id: string;
  storage_backend: string;
  sent_at: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getSessionToken();
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers
  });

  if (response.status === 401) {
    clearSessionToken();
  }

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Request failed.");
  }

  return (await response.json()) as T;
}

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

export function fetchAuthStatus(): Promise<AuthStatus> {
  return apiFetch<AuthStatus>("/api/auth/me");
}

export function fetchThreads(): Promise<Thread[]> {
  return apiFetch<Thread[]>("/api/threads");
}

export function createDraft(threadId: string): Promise<DraftReplyResponse> {
  return apiFetch<DraftReplyResponse>(`/api/replies/threads/${threadId}/draft`, {
    method: "POST",
    body: JSON.stringify({})
  });
}

export function sendReply(
  threadId: string,
  draftId: string | null,
  finalText: string
): Promise<SendReplyResponse> {
  return apiFetch<SendReplyResponse>(`/api/replies/threads/${threadId}/send`, {
    method: "POST",
    body: JSON.stringify({
      draft_id: draftId,
      final_text: finalText
    })
  });
}

export function logout(): Promise<AuthStatus> {
  return apiFetch<AuthStatus>("/api/auth/logout", {
    method: "POST"
  });
}
