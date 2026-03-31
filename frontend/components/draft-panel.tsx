import { Thread } from "../lib/api";

type DraftPanelProps = {
  thread: Thread | null;
  draftText: string;
  isGenerating: boolean;
  isSending: boolean;
  onDraftChange: (value: string) => void;
  onGenerateDraft: () => void;
  onSend: () => void;
};

export function DraftPanel({
  thread,
  draftText,
  isGenerating,
  isSending,
  onDraftChange,
  onGenerateDraft,
  onSend
}: DraftPanelProps) {
  if (!thread) {
    return (
      <div className="panel panel-padding">
        <div className="eyebrow">Workspace</div>
        <h2 style={{ margin: "8px 0 14px", fontFamily: "var(--font-heading)" }}>Select a thread</h2>
        <p className="muted">Choose a Primary inbox thread to inspect the conversation and generate a draft.</p>
      </div>
    );
  }

  return (
    <div className="panel panel-padding">
      <div className="eyebrow">Review</div>
      <h2 style={{ margin: "8px 0 12px", fontFamily: "var(--font-heading)" }}>{thread.subject || "(No subject)"}</h2>
      <p className="muted">Participants: {thread.participants.join(", ")}</p>

      <div style={{ marginTop: "18px" }}>
        {thread.messages.map((message) => (
          <div className="message-card" key={message.gmail_message_id}>
            <div className="thread-title">{message.from_address}</div>
            <div className="thread-meta">{message.received_at || "Unknown date"}</div>
            <p style={{ marginBottom: 0, whiteSpace: "pre-wrap" }}>{message.body}</p>
          </div>
        ))}
      </div>

      <div style={{ marginTop: "22px" }}>
        <label className="label" htmlFor="draft-body">
          Draft reply
        </label>
        <textarea
          className="textarea"
          id="draft-body"
          onChange={(event) => onDraftChange(event.target.value)}
          placeholder="Generate a reply draft, then edit it before sending."
          value={draftText}
        />
      </div>

      <div className="actions">
        <button className="button button-secondary" disabled={isGenerating} onClick={onGenerateDraft} type="button">
          {isGenerating ? "Generating..." : "Generate draft"}
        </button>
        <button
          className="button button-primary"
          disabled={isSending || !draftText.trim()}
          onClick={onSend}
          type="button"
        >
          {isSending ? "Sending..." : "Approve and send"}
        </button>
      </div>
    </div>
  );
}
