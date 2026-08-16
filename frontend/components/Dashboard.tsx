import { TEMPLATES } from "../lib/data";
import type { SpecJobSummary } from "../lib/types";
import { ArrowRightIcon, TrashIcon } from "./icons";

const RECENT_KEYS = ["saas", "copilot", "research"];

const STATUS_BADGE: Record<SpecJobSummary["status"], { label: string; bg: string; fg: string }> = {
  draft: { label: "Draft", bg: "oklch(0.355 0.01 260)", fg: "oklch(0.930 0.01 260)" },
  done: { label: "Ready", bg: "oklch(0.355 0.062 150)", fg: "oklch(0.930 0.048 150)" },
  pending: { label: "Generating", bg: "oklch(0.355 0.062 85)", fg: "oklch(0.930 0.060 85)" },
  running: { label: "Generating", bg: "oklch(0.355 0.062 85)", fg: "oklch(0.930 0.060 85)" },
  needs_input: { label: "Needs input", bg: "oklch(0.355 0.062 85)", fg: "oklch(0.930 0.060 85)" },
  failed: { label: "Failed", bg: "oklch(0.355 0.09 25)", fg: "oklch(0.930 0.07 25)" },
};

function formatRelativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const minutes = Math.round(diffMs / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  return `${days}d ago`;
}

export function Dashboard({
  specs,
  loading,
  onOpenSpec,
  onDeleteSpec,
  onGoTemplates,
  onUseTemplate,
}: {
  specs: SpecJobSummary[];
  loading: boolean;
  onOpenSpec: (id: string) => void;
  onDeleteSpec: (id: string) => void;
  onGoTemplates: () => void;
  onUseTemplate: (key: string) => void;
}) {
  const subtitle = loading
    ? "Loading your specs…"
    : specs.length === 0
      ? "No specs yet — start from a blank idea or a template below."
      : `${specs.length} spec${specs.length === 1 ? "" : "s"} so far.`;

  return (
    <div className="page-pad" style={{ maxWidth: 1020, display: "grid", gap: 40 }}>
      <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: 24, flexWrap: "wrap" }}>
        <div>
          <h2 style={{ marginBottom: 6 }}>Your specs</h2>
          <p className="text-muted" style={{ fontSize: 14, margin: 0 }}>{subtitle}</p>
        </div>
        
      </div>

      {specs.length > 0 && (
        <div style={{ display: "grid", gap: 14 }}>
          {specs.map((spec) => {
            const badge = STATUS_BADGE[spec.status];
            return (
              <div
                key={spec.id}
                role="button"
                tabIndex={0}
                onClick={() => onOpenSpec(spec.id)}
                onKeyDown={(e) => { if (e.key === "Enter") onOpenSpec(spec.id); }}
                className="hover-shadow-md"
                style={{ display: "grid", gridTemplateColumns: "1fr auto auto", gap: 24, alignItems: "center", padding: "18px 20px", borderRadius: "var(--radius-md)", cursor: "pointer", color: "var(--color-text)", background: "var(--color-surface)", boxShadow: "var(--shadow-sm)" }}
              >
                <div style={{ display: "grid", gap: 5, minWidth: 0 }}>
                  <span style={{ fontFamily: "var(--font-heading)", fontSize: 17 }}>{spec.title}</span>
                  <span style={{ fontSize: 12, color: "color-mix(in srgb, var(--color-text) 50%, transparent)" }}>edited {formatRelativeTime(spec.updated_at)}</span>
                </div>
                <span style={{ justifySelf: "end", display: "inline-flex", alignItems: "center", fontSize: 11, letterSpacing: "0.02em", padding: "3px 10px", borderRadius: 6, background: badge.bg, color: badge.fg }}>{badge.label}</span>
                <button
                  type="button"
                  aria-label={`Delete ${spec.title}`}
                  className="hover-surface"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm(`Delete "${spec.title}"? This can't be undone.`)) onDeleteSpec(spec.id);
                  }}
                  style={{ display: "grid", placeItems: "center", width: 30, height: 30, padding: 0, border: "none", borderRadius: "var(--radius-sm)", background: "transparent", color: "color-mix(in srgb, var(--color-text) 45%, transparent)", cursor: "pointer" }}
                >
                  <TrashIcon />
                </button>
              </div>
            );
          })}
        </div>
      )}

      <div style={{ display: "grid", gap: 18 }}>
        <h5 style={{ margin: 0, fontSize: 11, letterSpacing: "0.1em", textTransform: "uppercase", color: "color-mix(in srgb, var(--color-text) 40%, transparent)" }}>Start from a template</h5>
        <div className="grid-templates" style={{ display: "grid", gap: 14 }}>
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
