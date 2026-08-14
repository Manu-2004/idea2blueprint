const FORMATS = [
  { key: "PDF", label: "PDF", note: "Formatted, ready to send to a developer", size: "3 pages" },
  { key: "Markdown", label: "Markdown", note: "Drops into a repo or issue tracker", size: "11 KB" },
];

export function ExportDialog({
  format,
  onSelectFormat,
  onClose,
}: {
  format: string;
  onSelectFormat: (format: string) => void;
  onClose: () => void;
}) {
  return (
    <div className="dialog-backdrop">
      <div className="dialog">
        <span className="dialog-title">Download spec</span>
        <p className="dialog-body" style={{ margin: 0 }}>Invoice chaser for freelancers · 3 pages · 6 sections</p>
        <div style={{ display: "grid", gap: 8, paddingTop: 4 }}>
          {FORMATS.map((f) => (
            <label
              key={f.key}
              className="hover-surface"
              style={{ display: "grid", gridTemplateColumns: "auto 1fr auto", gap: 12, alignItems: "center", padding: "12px 14px", borderRadius: "var(--radius-md)", cursor: "pointer", border: "1px solid var(--color-divider)" }}
            >
              <span className="radio" style={{ pointerEvents: "none" }}>
                <input type="radio" name="fmt" checked={format === f.key} onChange={() => onSelectFormat(f.key)} />
                <span className="dot" />
              </span>
              <span style={{ display: "grid", gap: 2 }}>
                <span style={{ fontSize: 14 }}>{f.label}</span>
                <span style={{ fontSize: 12, color: "color-mix(in srgb, var(--color-text) 50%, transparent)" }}>{f.note}</span>
              </span>
              <span style={{ fontSize: 11, color: "color-mix(in srgb, var(--color-text) 45%, transparent)" }}>{f.size}</span>
            </label>
          ))}
        </div>
        <div className="dialog-actions">
          <a href="#" className="btn btn-secondary" onClick={(e) => { e.preventDefault(); onClose(); }}>Cancel</a>
          <a href="#" className="btn btn-primary" onClick={(e) => { e.preventDefault(); onClose(); }}>Download {format}</a>
        </div>
      </div>
    </div>
  );
}
