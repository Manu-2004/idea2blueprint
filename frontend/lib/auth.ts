import { apiFetch, clearToken, setToken } from "./api";
import type { AuthResponse, User } from "./types";

export async function signup(name: string, email: string, password: string): Promise<User> {
  const res = await apiFetch<AuthResponse>("/api/auth/signup", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });
  setToken(res.token);
  return res.user;
}

export async function login(email: string, password: string): Promise<User> {
  const res = await apiFetch<AuthResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(res.token);
  return res.user;
}

export async function me(): Promise<User> {
  return apiFetch<User>("/api/auth/me");
}

export async function logout(): Promise<void> {
  try {
    await apiFetch<void>("/api/auth/logout", { method: "POST" });
  } finally {
    clearToken();
  }
}
