import { useState } from "react";
import type { ClarificationAnswer, ClarifyingQuestion } from "../lib/types";

export function ClarifyQuestions({
  questions,
  submitting,
  onSubmit,
}: {
  questions: ClarifyingQuestion[];
  submitting: boolean;
  onSubmit: (answers: ClarificationAnswer[]) => void;
}) {
  const [values, setValues] = useState<Record<string, string>>({});

  const setValue = (key: string, value: string) => setValues((v) => ({ ...v, [key]: value }));

  const allAnswered = questions.every((q) => (values[q.key] ?? "").trim().length > 0);

  const handleSubmit = () => {
    if (!allAnswered || submitting) return;
    onSubmit(questions.map((q) => ({ key: q.key, question: q.question, answer: values[q.key].trim() })));
  };

  return (
    <div style={{ maxWidth: 640, padding: "56px 44px 96px", display: "grid", gap: 36 }}>
      <div>
        <h2 style={{ marginBottom: 8, fontSize: 29 }}>A couple of quick questions</h2>
        <p className="text-muted" style={{ fontSize: 14, margin: 0 }}>
          Your idea is ambiguous in a way that would change the spec — answer these and
          generation will continue.
        </p>
      </div>

      {questions.map((q) => {
        const value = values[q.key] ?? "";
        const isCustom = q.choices.indexOf(value) === -1;
        return (
          <div key={q.key} style={{ display: "grid", gap: 12 }}>
            <h4 style={{ margin: 0, fontSize: 17 }}>{q.question}</h4>
            {q.choices.length > 0 && (
              <div style={{ display: "grid", gap: 8 }}>
                {q.choices.map((c) => (
                  <label
                    key={c}
                    className="hover-surface"
                    style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 12, alignItems: "center", padding: "14px 16px", borderRadius: "var(--radius-md)", cursor: "pointer", fontSize: 15, background: "var(--color-surface)", boxShadow: "var(--shadow-sm)" }}
                  >
                    <span className="radio" style={{ pointerEvents: "none" }}>
                      <input
                        type="radio"
                        name={`clarify-${q.key}`}
                        checked={value === c}
                        onChange={() => setValue(q.key, c)}
                      />
                      <span className="dot" />
                    </span>
                    {c}
                  </label>
                ))}
              </div>
            )}
            <div className="field">
              <label>{q.choices.length > 0 ? "Or write your own answer" : "Your answer"}</label>
              <textarea
                className="input"
                style={{ minHeight: 76 }}
                value={isCustom ? value : ""}
                onChange={(e) => setValue(q.key, e.target.value)}
                placeholder="Type it in your own words"
              />
            </div>
          </div>
        );
      })}

      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <a
          href="#"
          className="btn btn-primary"
          style={{
            padding: "10px 20px",
            opacity: allAnswered && !submitting ? 1 : 0.5,
            pointerEvents: allAnswered && !submitting ? "auto" : "none",
          }}
          onClick={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
        >
          {submitting ? "Submitting…" : "Continue"}
        </a>
      </div>
    </div>
  );
}
