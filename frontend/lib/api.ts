import type { FormFields, JobCreateResponse, JobStatusResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function createSpecJob(brief: FormFields): Promise<JobCreateResponse> {
  const res = await fetch(`${API_BASE_URL}/api/spec-jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(brief),
  });
  if (!res.ok) {
    throw new Error(`Failed to start spec generation (${res.status})`);
  }
  return res.json();
}

export async function getSpecJob(jobId: string): Promise<JobStatusResponse> {
  const res = await fetch(`${API_BASE_URL}/api/spec-jobs/${jobId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch spec status (${res.status})`);
  }
  return res.json();
}
