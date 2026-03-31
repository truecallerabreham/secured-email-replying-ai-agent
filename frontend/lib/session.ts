const SESSION_STORAGE_KEY = "secured-email-agent-session";

export function getSessionToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(SESSION_STORAGE_KEY);
}

export function setSessionToken(token: string): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(SESSION_STORAGE_KEY, token);
}

export function clearSessionToken(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(SESSION_STORAGE_KEY);
}
