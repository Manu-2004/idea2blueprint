import type { FormFields, JobCreateResponse, JobStatusResponse, SpecJobSummary } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const TOKEN_KEY = "i2b_auth_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(init.headers ?? {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const res = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    const detail = await res
      .json()
      .then((body: { detail?: string }) => body.detail)
      .catch(() => undefined);
    throw new Error(detail ?? `Request failed (${res.status})`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export async function createSpecJob(brief: FormFields): Promise<JobCreateResponse> {
  return apiFetch<JobCreateResponse>("/api/spec-jobs", {
    method: "POST",
    body: JSON.stringify(brief),
  });
}

export async function getSpecJob(jobId: string): Promise<JobStatusResponse> {
  return apiFetch<JobStatusResponse>(`/api/spec-jobs/${jobId}`);
}

export async function listSpecJobs(): Promise<SpecJobSummary[]> {
  return apiFetch<SpecJobSummary[]>("/api/spec-jobs");
}
