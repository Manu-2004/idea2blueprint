import { useEffect, useRef, useState, type ReactNode } from "react";
import { CloseIcon, Logo, MenuIcon } from "./icons";
import type { Screen, User } from "../lib/types";

const NAV_ITEMS: { key: Screen; label: string }[] = [
  { key: "dashboard", label: "Dashboard" },
  { key: "templates", label: "Templates" },
];

const SPEC_QUOTA = 10;

function initialsFor(name: string): string {
  return (
    name
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase())
      .join("") || "?"
  );
}

export function AppShell({
  screen,
  user,
  specsUsed,
  onGo,
  onNew,
  onLogout,
  children,
}: {
  screen: Screen;
  user: User | null;
  specsUsed: number;
  onGo: (screen: Screen) => void;
  onNew: () => void;
  onLogout: () => void;
  children: ReactNode;
}) {
  const quotaUsed = Math.min(specsUsed, SPEC_QUOTA);
  const [menuOpen, setMenuOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!menuOpen) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen]);

  // Screen changes (nav clicks, "New spec") should close the mobile drawer too.
  const go = (next: Screen) => { setSidebarOpen(false); onGo(next); };
  const startNew = () => { setSidebarOpen(false); onNew(); };

  return (
    <div className="app-shell" style={{ minHeight: "100vh", display: "grid", background: "var(--color-bg)" }}>
      <div className="app-topbar">
        <button
          type="button"
          aria-label="Open menu"
          className="btn btn-icon btn-secondary"
          onClick={() => setSidebarOpen(true)}
        >
          <MenuIcon />
        </button>
        <span className="nav-brand" style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 15 }}>
          <Logo size={16} />
          Idea2Blueprint
        </span>
      </div>

      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />}

      <aside className={`app-sidebar${sidebarOpen ? " open" : ""}`} style={{ display: "flex", flexDirection: "column", gap: 20, padding: "22px 16px", background: "linear-gradient(180deg, #1a1c2c, var(--color-bg))", boxShadow: "inset -1px 0 0 var(--color-divider)" }}>
        <div style={{ position: "absolute", top: -40, bottom: -40, left: "-40%", right: "-40%", filter: "blur(64px)", opacity: 0.42, pointerEvents: "none" }}>
          <div style={{ position: "absolute", left: 0, right: 0, top: "2%", height: "26%", background: "linear-gradient(100deg, transparent 6%, var(--color-accent-700) 38%, var(--color-accent) 60%, transparent 86%)", animation: "aurora-a 19s ease-in-out infinite" }} />
          <div style={{ position: "absolute", left: 0, right: 0, top: "34%", height: "22%", background: "linear-gradient(80deg, transparent 10%, var(--color-section) 34%, var(--color-accent-400) 58%, transparent 88%)", animation: "aurora-b 25s ease-in-out infinite" }} />
          <div style={{ position: "absolute", left: 0, right: 0, top: "64%", height: "24%", background: "linear-gradient(90deg, transparent 14%, var(--color-section-glow) 42%, var(--color-accent-600) 64%, transparent 90%)", animation: "aurora-c 31s ease-in-out infinite" }} />
        </div>
        <div style={{ position: "absolute", inset: 0, pointerEvents: "none", background: "linear-gradient(180deg, transparent 0%, color-mix(in srgb, var(--color-bg) 45%, transparent) 55%, color-mix(in srgb, var(--color-bg) 62%, transparent) 100%)" }} />

        <div style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 6px" }}>
          <span className="nav-brand" style={{ display: "flex", alignItems: "center", gap: 9, fontSize: 16 }}>
            <Logo size={18} />
            Idea2Blueprint
          </span>
          <button
            type="button"
            aria-label="Close menu"
            className="btn btn-icon hover-surface"
            style={{ display: sidebarOpen ? "grid" : "none" }}
            onClick={() => setSidebarOpen(false)}
          >
            <CloseIcon size={16} />
          </button>
        </div>
        <a href="#" className="btn btn-primary btn-block" style={{ position: "relative", margin: 0 }} onClick={(e) => { e.preventDefault(); startNew(); }}>New spec</a>
        <nav style={{ position: "relative", display: "grid", gap: 2 }}>
          {NAV_ITEMS.map((item) => {
            const active = screen === item.key;
            return (
              <a
                key={item.key}
                href="#"
                className="nav-item hover-surface"
                style={{ display: "flex", alignItems: "center", gap: 9, padding: "8px 10px", borderRadius: "var(--radius-md)", fontSize: 14, textDecoration: "none", color: "var(--color-text)" }}
                data-active={active ? "true" : "false"}
                onClick={(e) => { e.preventDefault(); go(item.key); }}
              >
                <span style={{ width: 5, height: 5, borderRadius: "50%", background: "var(--color-accent)", opacity: 0.9, visibility: active ? "visible" : "hidden" }} />
                {item.label}
              </a>
            );
          })}
        </nav>
        <div style={{ position: "relative", display: "grid", gap: 10, padding: 12, borderRadius: "var(--radius-md)", background: "var(--color-surface)", boxShadow: "var(--shadow-sm)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, letterSpacing: "0.06em", textTransform: "uppercase", color: "color-mix(in srgb, var(--color-text) 55%, transparent)" }}>
            <span>This month</span><span>{quotaUsed} of {SPEC_QUOTA} specs</span>
          </div>
          <div style={{ height: 3, borderRadius: 2, background: "var(--color-neutral-800)", overflow: "hidden" }}>
            <div style={{ height: "100%", width: `${(quotaUsed / SPEC_QUOTA) * 100}%`, background: "var(--color-accent)" }} />
          </div>
          <p className="text-muted" style={{ fontSize: 11, margin: 0 }}>Free plan. Resets 1 Sep.</p>
        </div>
        {user ? (
          <div ref={menuRef} style={{ position: "relative" }}>
            <a
              href="#"
              className="hover-surface"
              style={{ position: "relative", display: "flex", alignItems: "center", gap: 9, padding: "4px 6px", borderRadius: "var(--radius-md)", textDecoration: "none", color: "var(--color-text)" }}
              onClick={(e) => { e.preventDefault(); setMenuOpen((v) => !v); }}
            >
              <span style={{ width: 26, height: 26, borderRadius: "50%", display: "grid", placeItems: "center", fontSize: 11, background: "var(--color-accent-800)", color: "var(--color-accent-100)" }}>{initialsFor(user.name)}</span>
              <span style={{ fontSize: 13 }}>{user.name}</span>
            </a>
            {menuOpen && (
              <div style={{ position: "absolute", bottom: "calc(100% + 6px)", left: 0, right: 0, borderRadius: "var(--radius-md)", background: "var(--color-surface)", boxShadow: "var(--shadow-md)", border: "1px solid var(--color-divider)", overflow: "hidden", zIndex: 50 }}>
                <a
                  href="#"
                  className="hover-surface"
                  style={{ display: "block", padding: "10px 12px", fontSize: 13, textDecoration: "none", color: "var(--color-text)" }}
                  onClick={(e) => { e.preventDefault(); setMenuOpen(false); onLogout(); }}
                >
                  Log out
                </a>
              </div>
            )}
          </div>
        ) : (
          <a
            href="#"
            className="hover-surface"
            style={{ position: "relative", display: "flex", alignItems: "center", gap: 9, padding: "4px 6px", borderRadius: "var(--radius-md)", textDecoration: "none", color: "var(--color-text)" }}
            onClick={(e) => { e.preventDefault(); go("auth"); }}
          >
            <span style={{ width: 26, height: 26, borderRadius: "50%", display: "grid", placeItems: "center", fontSize: 11, background: "var(--color-accent-800)", color: "var(--color-accent-100)" }}>?</span>
            <span style={{ fontSize: 13 }}>Log in — previewing a sample</span>
          </a>
        )}
      </aside>

      <main style={{ minWidth: 0, position: "relative" }}>
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: 640,
            overflow: "hidden",
            pointerEvents: "none",
            maskImage: "linear-gradient(180deg, transparent 0%, black 45%, black 100%)",
            WebkitMaskImage: "linear-gradient(180deg, transparent 0%, black 45%, black 100%)",
          }}
        >
          <div className="lighten" style={{ position: "absolute", inset: 0, opacity: 0.35 }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/layered-waves-haikei.png" alt="" style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center bottom" }} />
          </div>
        </div>
        <div style={{ position: "relative", zIndex: 1 }}>{children}</div>
      </main>
    </div>
  );
}
