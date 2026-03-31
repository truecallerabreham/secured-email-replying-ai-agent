"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { DraftPanel } from "../../components/draft-panel";
import { LogoutButton } from "../../components/logout-button";
import { ThreadList } from "../../components/thread-list";
import {
  Thread,
  createDraft,
  fetchAuthStatus,
  fetchThreads,
  sendReply
} from "../../lib/api";
import { clearSessionToken, getSessionToken } from "../../lib/session";

export default function DashboardPage() {
  const router = useRouter();
  const [email, setEmail] = useState<string | null>(null);
  const [threads, setThreads] = useState<Thread[]>([]);
  const [selectedThread, setSelectedThread] = useState<Thread | null>(null);
  const [draftText, setDraftText] = useState("");
  const [draftId, setDraftId] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusKind, setStatusKind] = useState<"error" | "success" | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    if (!getSessionToken()) {
      router.replace("/");
      return;
    }

    async function loadDashboard() {
      try {
        const auth = await fetchAuthStatus();
        setEmail(auth.email ?? null);

        const inboxThreads = await fetchThreads();
        setThreads(inboxThreads);
        setSelectedThread(inboxThreads[0] ?? null);
      } catch (error) {
        clearSessionToken();
        setStatusKind("error");
        setStatusMessage(error instanceof Error ? error.message : "Unable to load dashboard.");
        router.replace("/");
      } finally {
        setIsLoading(false);
      }
    }

    void loadDashboard();
  }, [router]);

  useEffect(() => {
    setDraftText("");
    setDraftId(null);
    setStatusMessage(null);
    setStatusKind(null);
  }, [selectedThread?.id]);

  async function handleGenerateDraft() {
    if (!selectedThread) {
      return;
    }

    setIsGenerating(true);
    setStatusMessage(null);
    setStatusKind(null);
    try {
      const draft = await createDraft(selectedThread.id);
      setDraftText(draft.draft_text);
      setDraftId(draft.draft_id ?? null);
      setStatusKind("success");
      setStatusMessage(`Draft generated with ${draft.model_name} and stored via ${draft.storage_backend}.`);
    } catch (error) {
      setStatusKind("error");
      setStatusMessage(error instanceof Error ? error.message : "Failed to generate a draft.");
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleSend() {
    if (!selectedThread || !draftText.trim()) {
      return;
    }

    setIsSending(true);
    setStatusMessage(null);
    setStatusKind(null);
    try {
      const result = await sendReply(selectedThread.id, draftId, draftText);
      setStatusKind("success");
      setStatusMessage(`Reply sent successfully at ${result.sent_at}. Gmail id: ${result.gmail_message_id}`);
    } catch (error) {
      setStatusKind("error");
      setStatusMessage(error instanceof Error ? error.message : "Failed to send reply.");
    } finally {
      setIsSending(false);
    }
  }

  if (isLoading) {
    return (
      <main className="shell">
        <div className="panel panel-padding">
          <div className="eyebrow">Loading</div>
          <p className="muted">Connecting to the secure inbox workspace...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="shell">
      <section className="panel panel-padding" style={{ marginBottom: "24px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: "16px", flexWrap: "wrap" }}>
          <div>
            <div className="eyebrow">Phase 1 Workspace</div>
            <h1 style={{ margin: "8px 0 8px", fontFamily: "var(--font-heading)" }}>Draft review dashboard</h1>
            <p className="muted" style={{ margin: 0 }}>
              Signed in as {email ?? "owner"}. Gmail replies remain manual and editable before send.
            </p>
          </div>
          <LogoutButton />
        </div>
      </section>

      <section className="grid-two">
        <ThreadList
          onSelect={setSelectedThread}
          selectedThreadId={selectedThread?.id ?? null}
          threads={threads}
        />
        <div className="stack">
          <DraftPanel
            draftText={draftText}
            isGenerating={isGenerating}
            isSending={isSending}
            onDraftChange={setDraftText}
            onGenerateDraft={handleGenerateDraft}
            onSend={handleSend}
            thread={selectedThread}
          />
          {statusMessage ? <div className={`status ${statusKind ?? ""}`}>{statusMessage}</div> : null}
        </div>
      </section>
    </main>
  );
}
