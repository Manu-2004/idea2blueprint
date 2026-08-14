import { SPECS, TEMPLATES } from "../lib/data";
import { ArrowRightIcon } from "./icons";

const RECENT_KEYS = ["saas", "copilot", "research"];

export function Dashboard({
  onOpenSpec,
  onOpenForm,
  onGoTemplates,
  onUseTemplate,
}: {
  onOpenSpec: () => void;
  onOpenForm: () => void;
  onGoTemplates: () => void;
  onUseTemplate: (key: string) => void;
}) {
  return (
    <div style={{ maxWidth: 1020, padding: "40px 44px 80px", display: "grid", gap: 40 }}>
      <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: 24, flexWrap: "wrap" }}>
        <div>
          <h2 style={{ marginBottom: 6 }}>Your specs</h2>
          <p className="text-muted" style={{ fontSize: 14, margin: 0 }}>Three in progress, two shipped to a build.</p>
        </div>
        <a href="#" className="btn btn-secondary" onClick={(e) => { e.preventDefault(); onGoTemplates(); }}>Browse templates</a>
      </div>

      <div style={{ display: "grid", gap: 14 }}>
        {SPECS.map((spec) => (
          <a
            key={spec.title}
            href="#"
            onClick={(e) => { e.preventDefault(); spec.open ? onOpenSpec() : onOpenForm(); }}
            className="hover-shadow-md"
            style={{ display: "grid", gridTemplateColumns: "1fr 190px 120px", gap: 24, alignItems: "center", padding: "18px 20px", borderRadius: "var(--radius-md)", textDecoration: "none", color: "var(--color-text)", background: "var(--color-surface)", boxShadow: "var(--shadow-sm)" }}
          >
            <div style={{ display: "grid", gap: 5, minWidth: 0 }}>
              <span style={{ fontFamily: "var(--font-heading)", fontSize: 17 }}>{spec.title}</span>
              <span style={{ fontSize: 12, color: "color-mix(in srgb, var(--color-text) 50%, transparent)" }}>{spec.meta}</span>
            </div>
            <div style={{ display: "grid", gap: 7 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "color-mix(in srgb, var(--color-text) 55%, transparent)" }}>
                <span>{spec.stage}</span><span>{spec.pct}</span>
              </div>
              <div style={{ height: 3, borderRadius: 2, background: "var(--color-neutral-800)", overflow: "hidden" }}>
                <div style={{ height: "100%", background: "var(--color-accent)", width: spec.pct }} />
              </div>
            </div>
            {spec.status === "Ready" && (
              <span style={{ justifySelf: "end", display: "inline-flex", alignItems: "center", fontSize: 11, letterSpacing: "0.02em", padding: "3px 10px", borderRadius: 6, background: "oklch(0.355 0.062 150)", color: "oklch(0.930 0.048 150)", gridColumn: 3, gridRow: 1 }}>Ready</span>
            )}
            {spec.status === "Draft" && (
              <span style={{ justifySelf: "end", display: "inline-flex", alignItems: "center", fontSize: 11, letterSpacing: "0.02em", padding: "3px 10px", borderRadius: 6, background: "oklch(0.355 0.062 85)", color: "oklch(0.930 0.060 85)", gridColumn: 3, gridRow: 1 }}>Draft</span>
            )}
          </a>
        ))}
      </div>

      <div style={{ display: "grid", gap: 18 }}>
        <h5 style={{ margin: 0, fontSize: 11, letterSpacing: "0.1em", textTransform: "uppercase", color: "color-mix(in srgb, var(--color-text) 40%, transparent)" }}>Start from a template</h5>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
          {RECENT_KEYS.map((k) => {
            const t = TEMPLATES[k];
            return (
              <a
                key={k}
                href="#"
                onClick={(e) => { e.preventDefault(); onUseTemplate(k); }}
                className="hover-shadow-md"
                style={{ position: "relative", overflow: "hidden", display: "grid", gap: 10, alignContent: "start", minHeight: 132, padding: 18, borderRadius: "var(--radius-md)", textDecoration: "none", color: "var(--color-text)", background: "var(--color-surface)", boxShadow: "var(--shadow-sm)" }}
              >
                <span style={{ position: "absolute", right: -30, top: -40, width: 120, height: 120, borderRadius: "50%", background: "radial-gradient(circle, var(--color-accent-700), transparent 70%)", opacity: 0.5, filter: "blur(18px)", pointerEvents: "none" }} />
                <span style={{ position: "relative", fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--color-accent-300)" }}>{t.kicker}</span>
                <span style={{ position: "relative", fontFamily: "var(--font-heading)", fontSize: 18, lineHeight: 1.25, letterSpacing: "-0.01em" }}>{t.title}</span>
                <span style={{ position: "relative", display: "flex", alignItems: "center", gap: 7, marginTop: "auto", fontSize: 12, color: "color-mix(in srgb, var(--color-text) 55%, transparent)" }}>
                  Use template
                  <ArrowRightIcon size={13} strokeWidth={1.8} />
                </span>
              </a>
            );
          })}
        </div>
      </div>
    </div>
  );
}
