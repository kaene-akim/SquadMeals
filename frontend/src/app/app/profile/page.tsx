"use client";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

function ProfileInner() {
  const { user, refresh } = useAuth();
  const search = useSearchParams();
  const setup = search.get("setup");
  const [form, setForm] = useState<any>(null);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => { if (user) setForm({ ...user, weekly_budget: user.weekly_budget ?? "", latitude: user.latitude ?? "", longitude: user.longitude ?? "" }); }, [user]);

  async function save(e: React.FormEvent) {
    e.preventDefault(); setErr(""); setMsg(""); setBusy(true);
    try {
      const payload = { ...form, weekly_budget: form.weekly_budget === "" ? null : Number(form.weekly_budget), latitude: form.latitude === "" ? null : Number(form.latitude), longitude: form.longitude === "" ? null : Number(form.longitude), shopping_radius_km: Number(form.shopping_radius_km) };
      await api("/users/me", { method: "PUT", body: JSON.stringify(payload) });
      await refresh(); setMsg("Profile saved.");
    } catch (e) { setErr(e instanceof Error ? e.message : "Save failed"); }
    finally { setBusy(false); }
  }

  if (!form) return <div className="muted">Loading profile...</div>;
  const set = (k: string, v: any) => setForm((f: any) => ({ ...f, [k]: v }));

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Profile & preferences</h1>
        <p className="mt-1 muted">Manage your account, location privacy, dietary needs and meal-prep preferences.</p>
      </div>
      {setup && <div className="rounded-xl bg-[var(--brand-soft)] p-4 text-sm text-[var(--brand)]">Complete your profile so nearby people and groups can find you by area and distance. Exact coordinates are never shown publicly unless you explicitly allow it.</div>}
      {msg && <div className="rounded-xl bg-[var(--brand-soft)] p-3 text-sm text-[var(--brand)]">{msg}</div>}
      {err && <div className="rounded-xl bg-[var(--danger-soft)] p-3 text-sm text-[var(--danger)]">{err}</div>}
      <form onSubmit={save} className="card p-5 space-y-5">
        <div className="grid gap-4 sm:grid-cols-2">
          <div><label className="label">Name</label><input className="field" value={form.name} onChange={e=>set("name", e.target.value)} required /></div>
          <div><label className="label">Email</label><input className="field" value={form.email} disabled /></div>
          <div><label className="label">Area / neighbourhood (public label)</label><input className="field" value={form.location_label || ""} onChange={e=>set("location_label", e.target.value)} placeholder="e.g. Maplewood, North Block" /></div>
          <div><label className="label">Preferred shopping radius (km)</label><input className="field" type="number" min="0.5" max="100" step="0.5" value={form.shopping_radius_km} onChange={e=>set("shopping_radius_km", e.target.value)} /></div>
          <div><label className="label">Latitude (private, for distance)</label><input className="field" type="number" step="any" value={form.latitude} onChange={e=>set("latitude", e.target.value)} placeholder="45.5231" /></div>
          <div><label className="label">Longitude (private, for distance)</label><input className="field" type="number" step="any" value={form.longitude} onChange={e=>set("longitude", e.target.value)} placeholder="-122.6765" /></div>
        </div>
        <label className="flex items-start gap-3 rounded-xl border border-[var(--line)] p-3 text-sm">
          <input type="checkbox" checked={!!form.share_exact_location} onChange={e=>set("share_exact_location", e.target.checked)} className="mt-1" />
          <span><span className="font-semibold">Share exact coordinates publicly</span><br/><span className="muted">Off by default. When off, others only see your area label and approximate distance where available.</span></span>
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <div><label className="label">Dietary preferences</label><input className="field" value={form.dietary_preferences || ""} onChange={e=>set("dietary_preferences", e.target.value)} placeholder="vegetarian, high-protein..." /></div>
          <div><label className="label">Allergies</label><input className="field" value={form.allergies || ""} onChange={e=>set("allergies", e.target.value)} placeholder="peanuts, shellfish..." /></div>
          <div><label className="label">Approx. weekly food budget</label><input className="field" type="number" min="0" step="1" value={form.weekly_budget} onChange={e=>set("weekly_budget", e.target.value)} placeholder="60" /></div>
          <div><label className="label">Meal-prepping preferences</label><input className="field" value={form.meal_prep_preferences || ""} onChange={e=>set("meal_prep_preferences", e.target.value)} placeholder="batch cooking, quick lunches..." /></div>
        </div>
        <div><label className="label">Profile picture URL (optional)</label><input className="field" value={form.profile_picture || ""} onChange={e=>set("profile_picture", e.target.value)} placeholder="https://..." /></div>
        <button className="btn btn-primary" disabled={busy}>{busy ? "Saving..." : "Save profile"}</button>
      </form>
    </div>
  );
}

export default function ProfilePage() {
  return <Suspense fallback={<div className="muted">Loading...</div>}><ProfileInner /></Suspense>;
}
