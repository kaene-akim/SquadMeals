export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api";

export type ApiError = { detail?: string };

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("squadmeals_token");
}

export function setToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (token) localStorage.setItem("squadmeals_token", token);
  else localStorage.removeItem("squadmeals_token");
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && init.body && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(`${API_BASE}${path}`, { ...init, headers, cache: "no-store" });
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const data = (await res.json()) as ApiError;
      if (data.detail) msg = data.detail;
    } catch {}
    throw new Error(msg);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}
