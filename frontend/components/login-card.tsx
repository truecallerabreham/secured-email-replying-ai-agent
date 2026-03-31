import { getApiBaseUrl } from "../lib/api";

export function LoginCard() {
  return (
    <div className="panel panel-padding">
      <div className="eyebrow">Phase 1</div>
      <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.8rem", margin: "8px 0 12px" }}>
        Owner-only draft review
      </h2>
      <p className="muted">
        Sign in with the Gmail owner account, load Primary inbox threads, generate a Gemini draft, edit it,
        and send only after explicit approval.
      </p>
      <div className="pill-row">
        <span className="pill">Google OAuth</span>
        <span className="pill">Gmail Primary inbox</span>
        <span className="pill">Manual send approval</span>
      </div>
      <div className="actions">
        <a className="button button-primary" href={`${getApiBaseUrl()}/api/auth/login`}>
          Continue with Google
        </a>
      </div>
    </div>
  );
}
