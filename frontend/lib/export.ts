import type { Spec } from "./types";

function slugify(title: string): string {
  return title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "spec";
}

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function downloadText(filename: string, content: string): void {
  triggerDownload(new Blob([content], { type: "text/markdown;charset=utf-8" }), filename);
}

export function specToMarkdown(spec: Spec): string {
  const lines: string[] = [`# ${spec.title}`, "", spec.summary];
  for (const section of spec.sections) {
    lines.push("", `## ${section.num}  ${section.title}`, "", section.lead);
    for (const group of section.groups) {
      lines.push("", `**${group.label}**`, "");
      for (const item of group.items) {
        lines.push(`- ${item.text}`);
      }
    }
  }
  return lines.join("\n") + "\n";
}

export function downloadSpecAsMarkdown(spec: Spec): void {
  const blob = new Blob([specToMarkdown(spec)], { type: "text/markdown;charset=utf-8" });
  triggerDownload(blob, `${slugify(spec.title)}.md`);
}

export async function downloadSpecAsPdf(spec: Spec): Promise<void> {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF({ unit: "pt", format: "a4" });

  const marginX = 48;
  const marginBottom = 56;
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const maxWidth = pageWidth - marginX * 2;
  let y = 56;

  const ensureSpace = (needed: number) => {
    if (y + needed > pageHeight - marginBottom) {
      doc.addPage();
      y = 56;
    }
  };

  const writeBlock = (text: string, size: number, lineHeight: number, style: "normal" | "bold" = "normal") => {
    if (!text) return;
    doc.setFont("helvetica", style);
    doc.setFontSize(size);
    for (const line of doc.splitTextToSize(text, maxWidth)) {
      ensureSpace(lineHeight);
      doc.text(line, marginX, y);
      y += lineHeight;
    }
  };

  writeBlock(spec.title, 20, 25, "bold");
  y += 4;
  writeBlock(spec.summary, 11, 15);
  y += 12;

  for (const section of spec.sections) {
    ensureSpace(28);
    writeBlock(`${section.num}  ${section.title}`, 14, 19, "bold");
    y += 2;
    writeBlock(section.lead, 10.5, 14);
    y += 4;

    for (const group of section.groups) {
      ensureSpace(15);
      writeBlock(group.label.toUpperCase(), 9, 13, "bold");
      for (const item of group.items) {
        writeBlock(`•  ${item.text}`, 10, 13.5);
      }
      y += 6;
    }
    y += 10;
  }

  doc.save(`${slugify(spec.title)}.pdf`);
}
