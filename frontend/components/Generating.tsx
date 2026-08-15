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
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 40 }}>
      <div style={{ width: "100%", maxWidth: 420, display: "grid", gap: 28 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <SpinnerIcon size={18} />
          <h4 style={{ margin: 0 }}>Building your blueprint</h4>
        </div>
        <div style={{ display: "grid", gap: 14 }}>
          {GEN_LABELS.map((label, i) => {
            const opacity = i < genStep ? 1 : i === genStep ? 0.95 : 0.35;
            const fill = i < genStep ? "var(--color-accent)" : "transparent";
            const mark = i < genStep ? "✓" : "";
            const scale = i < genStep ? 1 : i === genStep ? 0.45 : 0;
            return (
              <div key={label} style={{ display: "grid", gridTemplateColumns: "16px 1fr", gap: 12, alignItems: "center", opacity }}>
                <span style={{ width: 16, height: 16, borderRadius: "50%", display: "grid", placeItems: "center", fontSize: 9, border: "1px solid var(--color-accent)", background: fill, color: "var(--color-bg)" }}>{mark}</span>
                <div style={{ display: "grid", gap: 6 }}>
                  <span style={{ fontSize: 14 }}>{label}</span>
                  <div style={{ height: 2, background: "var(--color-neutral-800)", borderRadius: 2, overflow: "hidden" }}>
                    <div style={{ height: "100%", background: "var(--color-accent)", transformOrigin: "left", width: "100%", transform: `scaleX(${scale})` }} />
                  </div>
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
