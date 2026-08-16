import { GEN_LABELS } from "../lib/data";
import type { JobError } from "../lib/types";
import { SpinnerIcon } from "./icons";

const ERROR_COPY: Record<JobError["type"], string> = {
  openai_rate_limit: "The model is rate-limited right now.",
  openai_timeout: "The request to the model timed out.",
  openai_content_policy: "That idea couldn't be processed as written — try rephrasing it.",
  openai_error: "The model provider rejected the request.",
  internal_error: "Something went wrong while generating your spec.",
  irrelevant_input:
    "That doesn't look like a product idea. Go back and describe what you want to build, who it's for, and what problem it solves.",
};

const ERROR_KICKER: Record<JobError["type"], string> = {
  openai_rate_limit: "Generation failed",
  openai_timeout: "Generation failed",
  openai_content_policy: "Generation failed",
  openai_error: "Generation failed",
  internal_error: "Generation failed",
  irrelevant_input: "Needs a real idea",
};

export function Generating({
  genStep,
  error,
  onRetry,
  onEdit,
  revisionRound = 0,
  maxRevisionRounds = 0,
}: {
  genStep: number;
  error?: JobError | null;
  onRetry?: () => void;
  onEdit?: () => void;
  revisionRound?: number;
  maxRevisionRounds?: number;
}) {
  if (error) {
    // Resubmitting the exact same input will just fail intake again, so this one case
    // sends the user back to edit the brief rather than retrying the job as-is.
    const isIrrelevant = error.type === "irrelevant_input";
    const action = isIrrelevant ? onEdit ?? onRetry : onRetry;
    const actionLabel = isIrrelevant ? "Edit idea" : "Try again";

    return (
      <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 40 }}>
        <div className="card elev-sm" style={{ width: "100%", maxWidth: 420 }}>
          <span className="card-kicker">{ERROR_KICKER[error.type]}</span>
          <p className="card-body" style={{ margin: 0 }}>{ERROR_COPY[error.type]}</p>
          {action && (
            <a
              href="#"
              className="btn btn-primary"
              style={{ justifySelf: "start" }}
              onClick={(e) => { e.preventDefault(); action(); }}
            >
              {actionLabel}
            </a>
          )}
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 40, position: "relative", overflow: "hidden" }}>
      <div
        aria-hidden
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: 520,
          height: 520,
          borderRadius: "50%",
          background: "radial-gradient(circle, color-mix(in srgb, var(--color-accent) 22%, transparent) 0%, transparent 70%)",
          filter: "blur(10px)",
          animation: "gen-orb-pulse 4.5s ease-in-out infinite",
          pointerEvents: "none",
        }}
      />
      <div style={{ width: "100%", maxWidth: 420, display: "grid", gap: 32, position: "relative" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <SpinnerIcon size={18} />
          <h4 style={{ margin: 0 }}>Building your blueprint</h4>
        </div>
        <div style={{ display: "grid" }}>
          {GEN_LABELS.map((label, i) => {
            const done = i < genStep;
            const active = i === genStep;
            const opacity = done ? 1 : active ? 1 : 0.35;
            const last = i === GEN_LABELS.length - 1;

            let lineState: "done" | "active" | "pending" = "pending";
            if (i < genStep - 1) lineState = "done";
            else if (i === genStep - 1) lineState = "active";

            const lineBackground =
              lineState === "done"
                ? "var(--color-accent)"
                : lineState === "active"
                  ? "linear-gradient(90deg, var(--color-accent) 0%, color-mix(in srgb, var(--color-accent) 90%, transparent) 20%, transparent 40%, transparent 60%, color-mix(in srgb, var(--color-accent) 90%, transparent) 80%, var(--color-accent) 100%)"
                  : "var(--color-neutral-800)";

            return (
              <div key={label} style={{ display: "grid", gridTemplateColumns: "20px 1fr", columnGap: 14, opacity, transition: "opacity 0.5s ease" }}>
                <div style={{ display: "grid", justifyItems: "center" }}>
                  <span
                    key={`${label}-${done}`}
                    style={{
                      width: 20,
                      height: 20,
                      borderRadius: "50%",
                      display: "grid",
                      placeItems: "center",
                      fontSize: 10,
                      border: `1px solid ${done || active ? "var(--color-accent)" : "var(--color-neutral-700)"}`,
                      background: done ? "var(--color-accent)" : "transparent",
                      color: "var(--color-bg)",
                      transition: "background 0.4s ease, border-color 0.4s ease",
                      animation: done
                        ? "gen-dot-flash 0.7s ease-out"
                        : active
                          ? "gen-ring-pulse 1.8s ease-out infinite"
                          : undefined,
                    }}
                  >
                    {done ? "✓" : active ? <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--color-accent)" }} /> : ""}
                  </span>
                  {!last && (
                    <div
                      style={{
                        width: 2,
                        flex: 1,
                        minHeight: 26,
                        marginTop: 2,
                        borderRadius: 2,
                        background: lineBackground,
                        backgroundSize: lineState === "active" ? "220% 100%" : undefined,
                        animation: lineState === "active" ? "gen-line-shimmer 1.6s linear infinite" : undefined,
                        transition: "background 0.6s ease",
                      }}
                    />
                  )}
                </div>
                <div style={{ paddingBottom: last ? 0 : 22 }}>
                  <span
                    style={{
                      fontSize: 14,
                      color: done || active ? "var(--color-text)" : "var(--color-neutral-500)",
                      animation: active ? "gen-text-glow 1.8s ease-in-out infinite" : undefined,
                    }}
                  >
                    {label}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
        {revisionRound > 0 ? (
          <p className="text-muted" style={{ fontSize: 12, margin: 0 }}>
            Refining based on review (round {revisionRound} of {maxRevisionRounds})
          </p>
        ) : (
          <p className="text-muted" style={{ fontSize: 12, margin: 0 }}>Usually under a minute.</p>
        )}
      </div>
    </div>
  );
}
