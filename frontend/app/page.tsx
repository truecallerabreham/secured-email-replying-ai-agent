import { LoginCard } from "../components/login-card";

export default function HomePage() {
  return (
    <main className="shell">
      <section className="hero">
        <div className="panel panel-padding">
          <div className="eyebrow">Secured Email Replying Agent</div>
          <h1 className="headline">Human-approved AI replies for your Gmail Primary inbox.</h1>
          <p className="lede">
            Phase 1 focuses on owner-only login, Primary inbox review, Gemini draft generation, editable replies,
            and explicit send approval. The backend is prepared for Supabase-backed draft storage now and vector
            retrieval next.
          </p>
          <div className="pill-row">
            <span className="pill">FastAPI on Railway</span>
            <span className="pill">Next.js on Vercel</span>
            <span className="pill">Gemini drafts</span>
          </div>
        </div>
        <LoginCard />
      </section>
    </main>
  );
}
