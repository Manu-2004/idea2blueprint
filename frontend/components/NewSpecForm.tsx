import { QUESTIONS } from "../lib/data";
import type { FormFields } from "../lib/types";

export function NewSpecForm({
  form,
  formSource,
  step,
  onIdeaChange,
  onChoiceSelect,
  onCustomChange,
  onNext,
  onBack,
}: {
  form: FormFields;
  formSource: string;
  step: number;
  onIdeaChange: (value: string) => void;
  onChoiceSelect: (key: keyof FormFields, value: string) => void;
  onCustomChange: (key: keyof FormFields, value: string) => void;
  onNext: () => void;
  onBack: () => void;
}) {
  const q = step > 0 ? QUESTIONS[step - 1] : null;
  const stepCounter = step === 0 ? "Your idea" : `Question ${step} of ${QUESTIONS.length}`;
  const progressPct = Math.round((step / (QUESTIONS.length + 1)) * 100) + "%";
  const nextLabel = step === QUESTIONS.length ? "Generate spec" : "Continue";
  const backLabel = step === 0 ? "Cancel" : "Back";
  const qCustom = q && q.choices.indexOf(form[q.key]) === -1 ? form[q.key] : "";

  return (
    <div style={{ maxWidth: 640, padding: "56px 44px 96px", display: "grid", gap: 36 }}>
      <div style={{ display: "grid", gap: 14 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16 }}>
          <span style={{ fontSize: 11, letterSpacing: "0.1em", textTransform: "uppercase", color: "color-mix(in srgb, var(--color-text) 45%, transparent)" }}>{stepCounter}</span>
          <span className="text-muted" style={{ fontSize: 11 }}>{formSource}</span>
        </div>
        <div style={{ height: 2, borderRadius: 2, background: "var(--color-neutral-800)", overflow: "hidden" }}>
          <div style={{ height: "100%", background: "var(--color-accent)", width: progressPct }} />
        </div>
      </div>

      {step === 0 && (
        <div style={{ display: "grid", gap: 20 }}>
          <div>
            <h2 style={{ marginBottom: 8, fontSize: 29 }}>What is the idea?</h2>
            <p className="text-muted" style={{ fontSize: 14, margin: 0 }}>Plain words are fine. Six questions follow.</p>
          </div>
          <textarea
            className="input"
            style={{ minHeight: 150, fontSize: 16, lineHeight: 1.55, padding: 14 }}
            value={form.idea}
            onChange={(e) => onIdeaChange(e.target.value)}
            placeholder="A tool that chases unpaid invoices for freelancers so they stop doing it by hand."
          />
        </div>
      )}

      {q && (
        <div style={{ display: "grid", gap: 24 }}>
          <div>
            <h2 style={{ marginBottom: 8, fontSize: 29 }}>{q.label}</h2>
            <p className="text-muted" style={{ fontSize: 14, margin: 0 }}>{q.help}</p>
          </div>
          <div style={{ display: "grid", gap: 8 }}>
            {q.choices.map((c) => (
              <label
                key={c}
                className="hover-surface"
                style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 12, alignItems: "center", padding: "14px 16px", borderRadius: "var(--radius-md)", cursor: "pointer", fontSize: 15, background: "var(--color-surface)", boxShadow: "var(--shadow-sm)" }}
              >
                <span className="radio" style={{ pointerEvents: "none" }}>
                  <input type="radio" name="qchoice" checked={form[q.key] === c} onChange={() => onChoiceSelect(q.key, c)} />
                  <span className="dot" />
                </span>
                {c}
              </label>
            ))}
          </div>
          <div className="field">
            <label>Or write your own answer</label>
            <textarea
              className="input"
              style={{ minHeight: 76 }}
              value={qCustom}
              onChange={(e) => onCustomChange(q.key, e.target.value)}
              placeholder="Type it in your own words"
            />
          </div>
        </div>
      )}

      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <a href="#" className="btn btn-primary" style={{ padding: "10px 20px" }} onClick={(e) => { e.preventDefault(); onNext(); }}>{nextLabel}</a>
        <a href="#" className="btn btn-secondary" onClick={(e) => { e.preventDefault(); onBack(); }}>{backLabel}</a>
        <span className="text-muted" style={{ fontSize: 12, marginLeft: "auto" }}>Uses 1 of your 10 monthly specs</span>
      </div>
    </div>
  );
}
