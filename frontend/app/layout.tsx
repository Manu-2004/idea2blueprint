import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Idea2Blueprint",
  description: "Describe the idea. Get the blueprint. Turn a plain-language idea into a scoped MVP spec.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
