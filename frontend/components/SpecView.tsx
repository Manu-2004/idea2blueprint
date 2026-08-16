import type { Section } from "../lib/types";

export function SpecView({
  title,
  summary,
  sections,
  onRegenerate,
  onOpenExport,
  onOpenAgentKit,
}: {
  title: string;
  summary: string;
  sections: Section[];
  onRegenerate: () => void;
  onOpenExport: () => void;
  onOpenAgentKit?: () => void;
}) {
  return (
    <div className="spec-layout" style={{ display: "grid", gap: 0, alignItems: "start" }}>
      <div className="page-pad" style={{ paddingTop: "clamp(24px, 5vw, 36px)", maxWidth: 820 }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 24, flexWrap: "wrap", paddingBottom: 28 }}>
          <div style={{ display: "grid", gap: 8 }}>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <span className="tag tag-accent">MVP spec</span>
              <span className="text-muted" style={{ fontSize: 12 }}>v1 · generated 14 Aug 2026</span>
            </div>
            <h2 style={{ margin: 0, fontSize: "clamp(24px, 5vw, 34px)" }}>{title}</h2>
            <p className="text-muted" style={{ fontSize: 14, margin: 0, maxWidth: 560 }}>
              {summary}
            </p>
          </div>
          <div className="actions-row" style={{ display: "flex", gap: 8 }}>
            <a href="#" className="btn btn-secondary" onClick={(e) => { e.preventDefault(); onRegenerate(); }}>Regenerate</a>
            <a href="#" className="btn btn-primary" onClick={(e) => { e.preventDefault(); onOpenExport(); }}>Download</a>
            {onOpenAgentKit && (
              <a href="#" className="btn btn-primary btn-glow" onClick={(e) => { e.preventDefault(); onOpenAgentKit(); }}>Agent kit</a>
            )}
          </div>
        </div>
        <hr className="hr" style={{ margin: "0 0 32px" }} />

        <div style={{ display: "grid", gap: 44 }}>
          {sections.map((s) => (
            <section key={s.id} id={s.id} style={{ display: "grid", gap: 14, scrollMarginTop: 24 }}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
                <span style={{ fontSize: 12, fontFamily: "var(--font-heading)", color: "var(--color-accent)" }}>{s.num}</span>
                <h3 style={{ margin: 0, fontSize: 24 }}>{s.title}</h3>
              </div>
              <p style={{ margin: 0, fontSize: 15, lineHeight: 1.6, color: "color-mix(in srgb, var(--color-text) 82%, transparent)", textWrap: "pretty" }}>{s.lead}</p>
              {s.groups.map((g) => (
                <div key={g.label} style={{ display: "grid", gap: 8, paddingTop: 10 }}>
                  <span style={{ fontSize: 11, fontFamily: "var(--font-heading)", fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase", color: "var(--color-accent)" }}>{g.label}</span>
                  <div style={{ display: "grid", gap: 7 }}>
                    {g.items.map((it) => (
                      <div key={it.text} style={{ display: "grid", gridTemplateColumns: "14px 1fr", gap: 10, fontSize: 14, lineHeight: 1.55 }}>
                        <span style={{ color: "var(--color-accent-500)", paddingTop: 1 }}>&middot;</span>
                        <span style={{ color: "color-mix(in srgb, var(--color-text) 88%, transparent)" }}>{it.text}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </section>
          ))}
        </div>
      </div>

      <div className="spec-toc" style={{ position: "sticky", top: 0, height: "100vh", padding: "44px 20px", gap: 6, alignContent: "start", background: "linear-gradient(180deg, color-mix(in srgb, var(--color-surface) 70%, transparent), transparent 70%)", boxShadow: "inset 1px 0 0 var(--color-divider)" }}>
        <span style={{ fontSize: 10, letterSpacing: "0.12em", textTransform: "uppercase", color: "color-mix(in srgb, var(--color-text) 38%, transparent)", padding: "0 10px 8px" }}>Sections</span>
        {sections.map((s) => (
          <a
            key={s.id}
            href={`#${s.id}`}
            className="hover-underline-accent"
            style={{ display: "block", fontSize: 13, lineHeight: 1.35, textDecoration: "none", padding: "7px 10px", borderRadius: "var(--radius-sm)", color: "color-mix(in srgb, var(--color-text) 62%, transparent)" }}
          >
            {s.num}&nbsp;&nbsp;{s.title}
          </a>
        ))}
      </div>
    </div>
  );
}
