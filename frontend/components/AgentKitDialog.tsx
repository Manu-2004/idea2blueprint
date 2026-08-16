import { useEffect, useState } from "react";
import { generateHandoff } from "../lib/api";
import { downloadText } from "../lib/export";
import type { HandoffResponse } from "../lib/types";

type Tab = "prompt" | "agents";
type Status = "loading" | "ready" | "error";

export function AgentKitDialog({
  jobId,
  initial,
  onGenerated,
  onClose,
}: {
  jobId: string;
  initial: HandoffResponse | null;
  onGenerated: (result: HandoffResponse) => void;
  onClose: () => void;
}) {
  const [tab, setTab] = useState<Tab>("prompt");
  const [result, setResult] = useState<HandoffResponse | null>(initial);
  const [status, setStatus] = useState<Status>(initial ? "ready" : "loading");
  const [copied, setCopied] = useState(false);

  const runGenerate = () => {
    setStatus("loading");
    generateHandoff(jobId)
      .then((res) => {
        setResult(res);
        setStatus("ready");
        onGenerated(res);
      })
      .catch(() => setStatus("error"));
  };

  useEffect(() => {
    if (!result) runGenerate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId]);

  const content = tab === "prompt" ? result?.agent_prompt ?? "" : result?.agents_md ?? "";
  const filename = tab === "prompt" ? "agent-prompt.md" : "AGENTS.md";

  const handleCopy = () => {
    navigator.clipboard.writeText(content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  return (
    <div className="dialog-backdrop">
      <div className="dialog" style={{ width: "min(720px, 100%)" }}>
        <span className="dialog-title">Coding agent kit</span>
        <p className="dialog-body" style={{ margin: 0 }}>
          A kickoff prompt broken into build tasks, plus an AGENTS.md for the repo — ready to hand to a coding agent.
        </p>

        <div className="seg" style={{ width: "fit-content" }}>
          <label className="seg-opt">
            <input type="radio" name="kit-tab" checked={tab === "prompt"} onChange={() => setTab("prompt")} />
            Agent prompt
          </label>
          <label className="seg-opt">
            <input type="radio" name="kit-tab" checked={tab === "agents"} onChange={() => setTab("agents")} />
            AGENTS.md
          </label>
        </div>

        {status === "loading" && (
          <div className="text-muted" style={{ padding: "32px 0", textAlign: "center", fontSize: 14 }}>
            Generating…
          </div>
        )}
        {status === "error" && (
          <div className="text-muted" style={{ padding: "8px 0", fontSize: 14 }}>
            Couldn&apos;t generate the agent kit — try again.
          </div>
        )}
        {status === "ready" && result && (
          <pre
            style={{
              margin: 0,
              maxHeight: 420,
              overflow: "auto",
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              fontSize: 12.5,
              lineHeight: 1.6,
              padding: 14,
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-divider)",
              background: "color-mix(in srgb, var(--color-text) 4%, transparent)",
            }}
          >
            {content}
          </pre>
        )}

        <div className="dialog-actions">
          {status === "error" && (
            <a href="#" className="btn btn-secondary" onClick={(e) => { e.preventDefault(); runGenerate(); }}>Retry</a>
          )}
          <a href="#" className="btn btn-secondary" onClick={(e) => { e.preventDefault(); onClose(); }}>Close</a>
          {status === "ready" && result && (
            <>
              <a href="#" className="btn btn-secondary" onClick={(e) => { e.preventDefault(); handleCopy(); }}>
                {copied ? "Copied" : "Copy"}
              </a>
              <a href="#" className="btn btn-primary" onClick={(e) => { e.preventDefault(); downloadText(filename, content); }}>
                Download
              </a>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
