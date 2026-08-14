import { GEN_LABELS } from "../lib/data";
import { SpinnerIcon } from "./icons";

export function Generating({ genStep }: { genStep: number }) {
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
        <p className="text-muted" style={{ fontSize: 12, margin: 0 }}>Usually under a minute.</p>
      </div>
    </div>
  );
}
