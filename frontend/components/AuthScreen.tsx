"use client";

import { useState } from "react";
import { Logo } from "./icons";
import type { AuthMode } from "../lib/types";

export function AuthScreen({
  authMode,
  onSetLogin,
  onSetSignup,
  onSubmit,
}: {
  authMode: AuthMode;
  onSetLogin: () => void;
  onSetSignup: () => void;
  onSubmit: (fields: { name: string; email: string; password: string }) => Promise<void>;
}) {
  const isLogin = authMode === "login";
  const isSignup = authMode === "signup";
  const authCta = isLogin ? "Log in" : "Create account";
  const authFootnote = isLogin ? "No account yet? Switch to sign up." : "Free plan, ten specs a month. No card.";

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setError(null);
    setSubmitting(true);
    try {
      await onSubmit({ name, email, password });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const switchMode = (next: AuthMode) => {
    setError(null);
    if (next === "login") onSetLogin();
    else onSetSignup();
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--color-bg)" }}>
      <div style={{ position: "relative", overflow: "hidden", minHeight: "100vh", padding: 40, display: "grid", gridTemplateRows: "auto 1fr auto", justifyItems: "start" }}>
        <div style={{ position: "absolute", inset: "-10% -20% auto -20%", height: "80vh", filter: "blur(80px)", opacity: 0.65, pointerEvents: "none" }}>
          <div style={{ position: "absolute", inset: 0, height: "38%", top: "14%", background: "linear-gradient(100deg, transparent 10%, var(--color-accent-700) 40%, var(--color-accent) 58%, transparent 82%)", animation: "aurora-a 21s ease-in-out infinite" }} />
          <div style={{ position: "absolute", inset: 0, height: "24%", top: "44%", background: "linear-gradient(80deg, transparent 14%, var(--color-section) 34%, var(--color-accent-400) 58%, transparent 86%)", animation: "aurora-b 27s ease-in-out infinite" }} />
        </div>
        <div className="lighten" style={{ position: "absolute", inset: 0, pointerEvents: "none", opacity: 0.75 }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/landing-horizon.png" alt="" style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center 62%" }} />
        </div>
        <div style={{ position: "absolute", inset: 0, pointerEvents: "none", background: "radial-gradient(70% 55% at 50% 50%, color-mix(in srgb, var(--color-bg) 82%, transparent) 0%, color-mix(in srgb, var(--color-bg) 35%, transparent) 55%, transparent 100%)" }} />

        <span className="nav-brand" style={{ position: "relative", display: "flex", alignItems: "center", gap: 10 }}>
          <Logo />
          Idea2Blueprint
        </span>
        <div style={{ position: "relative", display: "grid", placeItems: "center", width: "100%", padding: "32px 0" }}>
          <div style={{ width: "100%", maxWidth: 372, display: "grid", gap: 20, padding: 28, borderRadius: "var(--radius-lg)", background: "color-mix(in srgb, var(--color-surface) 88%, transparent)", boxShadow: "var(--shadow-md)", backdropFilter: "blur(14px)" }}>
            <div className="seg" style={{ width: "100%" }}>
              <label className="seg-opt" style={{ flex: 1, justifyContent: "center" }}>
                <input type="radio" name="authmode" checked={isLogin} onChange={() => switchMode("login")} />
                Log in
              </label>
              <label className="seg-opt" style={{ flex: 1, justifyContent: "center" }}>
                <input type="radio" name="authmode" checked={isSignup} onChange={() => switchMode("signup")} />
                Sign up
              </label>
            </div>
            <div style={{ display: "grid", gap: 12 }}>
              {isSignup && (
                <div className="field">
                  <label>Name</label>
                  <input className="input" placeholder="Priya Raman" value={name} onChange={(e) => setName(e.target.value)} />
                </div>
              )}
              <div className="field">
                <label>Email</label>
                <input className="input" type="email" placeholder="you@studio.com" value={email} onChange={(e) => setEmail(e.target.value)} />
              </div>
              <div className="field">
                <label>Password</label>
                <input className="input" type="password" placeholder="••••••••••" value={password} onChange={(e) => setPassword(e.target.value)} />
              </div>
            </div>
            {error && <p style={{ margin: 0, fontSize: 12, color: "var(--color-accent)" }}>{error}</p>}
            <div style={{ display: "grid", gap: 10 }}>
              <a
                href="#"
                className="btn btn-primary btn-block"
                style={{ padding: 10, opacity: submitting ? 0.7 : 1, pointerEvents: submitting ? "none" : "auto" }}
                onClick={(e) => { e.preventDefault(); handleSubmit(); }}
              >
                {submitting ? "Please wait…" : authCta}
              </a>
              <p className="text-muted" style={{ fontSize: 12, margin: 0, textAlign: "center" }}>{authFootnote}</p>
            </div>
          </div>
        </div>
        <p className="text-muted" style={{ position: "relative", fontSize: 12, margin: 0 }}>Ten specs a month, no card.</p>
      </div>
    </div>
  );
}
