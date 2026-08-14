export function Logo({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" strokeWidth="1.6">
      <path d="M12 2.6 21 7.4v9.2L12 21.4 3 16.6V7.4z" />
      <path d="M12 21.4V12l9-4.6M12 12 3 7.4" />
    </svg>
  );
}

export function ArrowRightIcon({ size = 16, strokeWidth = 1.5 }: { size?: number; strokeWidth?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" strokeWidth={strokeWidth}>
      <path d="M5 12h13M12 6l6 6-6 6" />
    </svg>
  );
}

export function SpinnerIcon({ size = 18 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="var(--color-accent)"
      strokeWidth="2"
      style={{ animation: "spin 1.1s linear infinite" }}
    >
      <path d="M12 3a9 9 0 1 0 9 9" />
    </svg>
  );
}
