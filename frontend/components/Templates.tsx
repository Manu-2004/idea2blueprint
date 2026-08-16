import { SHORTS, TEMPLATES } from "../lib/data";
import { ArrowRightIcon } from "./icons";

const GROUPS: { name: string; keys: string[] }[] = [
  { name: "SaaS dashboard tools", keys: ["saas", "churn", "ops"] },
  { name: "AI assistants and copilots", keys: ["copilot", "research", "onboard"] },
  { name: "Marketplaces and local services", keys: ["marketplace", "routes", "maintenance"] },
  { name: "Health and community", keys: ["meds", "volunteer", "waitlist"] },
];

export function Templates({ onUseTemplate }: { onUseTemplate: (key: string) => void }) {
  return (
    <div style={{ maxWidth: 840, padding: "56px 44px 96px", display: "grid", gap: 52 }}>
      <div style={{ maxWidth: 460 }}>
        <h2 style={{ marginBottom: 8 }}>Templates</h2>
        <p className="text-muted" style={{ fontSize: 14, margin: 0 }}>Pick one to fill the form with a worked answer set.</p>
      </div>
      {GROUPS.map((group) => (
        <div key={group.name} style={{ display: "grid", gap: 4 }}>
          <h5 style={{ margin: "0 0 12px", fontSize: 11, letterSpacing: "0.1em", textTransform: "uppercase", color: "color-mix(in srgb, var(--color-text) 40%, transparent)" }}>{group.name}</h5>
          {group.keys.map((k, i) => {
            const t = TEMPLATES[k];
            return (
              <a
                key={k}
                href="#"
                onClick={(e) => { e.preventDefault(); onUseTemplate(k); }}
                className="hover-surface-soft"
                style={{ display: "grid", gridTemplateColumns: "34px 1fr auto", alignItems: "center", gap: 18, padding: "20px 6px", textDecoration: "none", color: "var(--color-text)", borderTop: "1px solid var(--color-divider)" }}
              >
                <span style={{ fontSize: 11, fontFamily: "var(--font-heading)", color: "color-mix(in srgb, var(--color-text) 35%, transparent)" }}>{"0" + (i + 1)}</span>
                <span style={{ display: "grid", gap: 3 }}>
                  <span style={{ fontFamily: "var(--font-heading)", fontSize: 19, letterSpacing: "-0.01em" }}>{t.title}</span>
                  <span style={{ fontSize: 13, color: "color-mix(in srgb, var(--color-text) 48%, transparent)" }}>{SHORTS[k]}</span>
                </span>
                <ArrowRightIcon size={16} strokeWidth={1.5} />
              </a>
            );
          })}
        </div>
      ))}
    </div>
  );
}
