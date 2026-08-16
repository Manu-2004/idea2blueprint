export type ToastTone = "success" | "error";
export type ToastItem = { id: number; message: string; tone: ToastTone };

function ToastIcon({ tone }: { tone: ToastTone }) {
  if (tone === "error") {
    return (
      <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="oklch(0.7 0.14 25)" strokeWidth="2" strokeLinecap="round">
        <path d="M12 8v5M12 16h.01M12 3 2 20h20L12 3Z" />
      </svg>
    );
  }
  return (
    <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}

export function ToastStack({ toasts, onDismiss }: { toasts: ToastItem[]; onDismiss: (id: number) => void }) {
  if (toasts.length === 0) return null;

  return (
    <div style={{ position: "fixed", right: 20, bottom: 20, zIndex: 200, display: "grid", gap: 8, justifyItems: "end", maxWidth: "min(340px, calc(100vw - 40px))" }}>
      {toasts.map((t) => (
        <div
          key={t.id}
          role="status"
          style={{
            display: "grid",
            gridTemplateColumns: "auto 1fr auto",
            alignItems: "center",
            gap: 10,
            padding: "12px 14px",
            borderRadius: "var(--radius-md)",
            background: "var(--color-surface)",
            boxShadow: "var(--shadow-lg)",
            animation: "rise .25s ease both",
          }}
        >
          <ToastIcon tone={t.tone} />
          <span style={{ fontSize: 13, lineHeight: 1.4 }}>{t.message}</span>
          <button
            type="button"
            aria-label="Dismiss notification"
            onClick={() => onDismiss(t.id)}
            style={{ display: "grid", placeItems: "center", width: 22, height: 22, padding: 0, border: "none", borderRadius: "var(--radius-sm)", background: "transparent", color: "color-mix(in srgb, var(--color-text) 50%, transparent)", cursor: "pointer" }}
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}
