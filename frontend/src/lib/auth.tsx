"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { api, getToken, setToken } from "./api";

export type User = {
  id: number; email: string; name: string; profile_picture: string | null;
  location_label: string | null; latitude: number | null; longitude: number | null;
  share_exact_location: boolean; shopping_radius_km: number; dietary_preferences: string;
  allergies: string; weekly_budget: number | null; meal_prep_preferences: string;
};

type AuthState = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
};

const Ctx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    const token = getToken();
    if (!token) { setUser(null); setLoading(false); return; }
    try { setUser(await api<User>("/auth/me")); }
    catch { setToken(null); setUser(null); }
    finally { setLoading(false); }
  }

  useEffect(() => { void refresh(); }, []);

  async function login(email: string, password: string) {
    const data = await api<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
    setToken(data.access_token);
    await refresh();
  }
  async function register(name: string, email: string, password: string) {
    const data = await api<{ access_token: string }>("/auth/register", { method: "POST", body: JSON.stringify({ name, email, password }) });
    setToken(data.access_token);
    await refresh();
  }
  function logout() { setToken(null); setUser(null); }

  return <Ctx.Provider value={{ user, loading, login, register, logout, refresh }}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useAuth outside provider");
  return v;
}
