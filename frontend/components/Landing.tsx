import { Logo } from "./icons";

export function Landing({
  onSignup,
  onSampleSpec,
}: {
  onSignup: () => void;
  onSampleSpec: () => void;
}) {
  return (
    <div style={{ position: "relative", minHeight: "100vh", overflow: "hidden", background: "var(--color-bg)" }}>
      <div style={{ position: "absolute", inset: "-20% -10% auto -10%", height: "78vh", pointerEvents: "none", filter: "blur(60px)", opacity: 0.85 }}>
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(100deg, transparent 8%, var(--color-accent-700) 34%, var(--color-accent) 52%, transparent 78%)", height: "34%", top: "6%", animation: "aurora-a 17s ease-in-out infinite" }} />
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(80deg, transparent 12%, var(--color-section) 30%, var(--color-accent-400) 55%, transparent 84%)", height: "26%", top: "26%", animation: "aurora-b 23s ease-in-out infinite" }} />
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(90deg, transparent 20%, var(--color-section-glow) 44%, var(--color-accent-600) 62%, transparent 88%)", height: "20%", top: "46%", animation: "aurora-c 29s ease-in-out infinite" }} />
      </div>
      <div style={{ position: "absolute", inset: 0, pointerEvents: "none", background: "radial-gradient(120% 60% at 20% 0%, transparent 30%, var(--color-bg) 78%)" }} />
      <div className="lighten" style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: "62vh", pointerEvents: "none", opacity: 0.72, maskImage: "linear-gradient(to top, rgba(0,0,0,0.95) 12%, transparent 92%)", WebkitMaskImage: "linear-gradient(to top, rgba(0,0,0,0.95) 12%, transparent 92%)" }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/landing-horizon.png" alt="" style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center 65%" }} />
      </div>
      <div style={{ position: "absolute", inset: 0, pointerEvents: "none", background: "linear-gradient(105deg, var(--color-bg) 8%, color-mix(in srgb, var(--color-bg) 78%, transparent) 42%, transparent 72%)" }} />

      <div style={{ position: "relative", maxWidth: 1180, margin: "0 auto", padding: "0 40px" }}>
        <nav className="nav" style={{ paddingLeft: 0, paddingRight: 0, paddingTop: 22 }}>
          <span className="nav-brand" style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <Logo />
            Idea2Blueprint
          </span>
        </nav>

        <div style={{ display: "grid", gap: 56, padding: "96px 0 120px", maxWidth: 820, animation: "rise .7s ease both" }}>
          <div style={{ display: "grid", gap: 24 }}>
            <span className="tag tag-outline" style={{ justifySelf: "start" }}>Idea to MVP spec, in one pass</span>
            <h1 style={{ fontSize: 76, lineHeight: 1.02, letterSpacing: "-0.03em", margin: 0 }}>
              Describe the idea.<br />Get the blueprint.
            </h1>
            <p style={{ fontSize: 19, lineHeight: 1.6, maxWidth: 560, margin: 0, color: "color-mix(in srgb, var(--color-text) 72%, transparent)", textWrap: "pretty" }}>
              Write your idea in plain words, answer six questions, and Idea2Blueprint returns a scoped MVP spec — problem, feature cuts, user stories, flows, stack and risks. Read it here, or take it away as PDF or Markdown.
            </p>
            <div style={{ display: "flex", gap: 12, alignItems: "center", paddingTop: 8 }}>
              <a href="#" className="btn btn-primary" style={{ fontSize: 15, padding: "11px 22px" }} onClick={(e) => { e.preventDefault(); onSignup(); }}>Get started</a>
              <a href="#" className="btn btn-secondary" style={{ fontSize: 15, padding: "11px 22px" }} onClick={(e) => { e.preventDefault(); onSampleSpec(); }}>See a sample spec</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
