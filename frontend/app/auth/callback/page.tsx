"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { setSessionToken } from "../../../lib/session";

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [message, setMessage] = useState("Finalizing secure sign-in...");

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setMessage("Missing session token from the backend callback.");
      return;
    }

    setSessionToken(token);
    router.replace("/dashboard");
  }, [router, searchParams]);

  return (
    <main className="shell">
      <div className="panel panel-padding">
        <div className="eyebrow">Authentication</div>
        <h1 style={{ fontFamily: "var(--font-heading)", margin: "8px 0 12px" }}>Signing you in</h1>
        <p className="muted">{message}</p>
      </div>
    </main>
  );
}
