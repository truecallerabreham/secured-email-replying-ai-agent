import { Thread } from "../lib/api";

type ThreadListProps = {
  threads: Thread[];
  selectedThreadId: string | null;
  onSelect: (thread: Thread) => void;
};

export function ThreadList({ threads, selectedThreadId, onSelect }: ThreadListProps) {
  if (!threads.length) {
    return (
      <div className="panel panel-padding">
        <div className="eyebrow">Inbox</div>
        <p className="muted">No Primary inbox threads were returned yet.</p>
      </div>
    );
  }

  return (
    <div className="panel panel-padding">
      <div className="eyebrow">Inbox</div>
      <h2 style={{ margin: "8px 0 14px", fontFamily: "var(--font-heading)" }}>Primary threads</h2>
      <div className="stack">
        {threads.map((thread) => (
          <button
            className={`thread-button ${selectedThreadId === thread.id ? "active" : ""}`}
            key={thread.id}
            onClick={() => onSelect(thread)}
            type="button"
          >
            <p className="thread-title">{thread.subject || "(No subject)"}</p>
            <div className="thread-meta">{thread.latest_from}</div>
            <div className="thread-meta">{thread.latest_received_at || "Unknown date"}</div>
            <div className="thread-meta" style={{ marginTop: "10px" }}>
              {thread.snippet}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
