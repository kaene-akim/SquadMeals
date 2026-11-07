"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function DiscoverPage() {
  const [groups, setGroups] = useState<any[]>([]);
  const [people, setPeople] = useState<any[]>([]);
  const [err, setErr] = useState("");
  const [msg, setMsg] = useState("");
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", area_label: "Maplewood", latitude: "45.5225", longitude: "-122.6760", join_mode: "request" });

  async function load() {
    setErr("");
    try {
      const [g, p] = await Promise.allSettled([api<any[]>("/groups?scope=discover"), api<any[]>("/users/nearby")]);
      if (g.status === "fulfilled") setGroups(g.value); else setErr("Could not load groups. Add your location in Profile for distance filtering.");
      if (p.status === "fulfilled") setPeople(p.value);
    } catch (e) { setErr(e instanceof Error ? e.message : "Failed"); }
  }
  useEffect(() => { void load(); }, []);

  async function join(groupId: number) {
    setMsg(""); setErr("");
    try { const r = await api<any>(`/groups/${groupId}/join`, { method: "POST" }); setMsg(r.status === "already_member" ? "You are already a member." : "Join request sent."); await load(); }
    catch (e) { setErr(e instanceof Error ? e.message : "Failed"); }
  }
  async function create(e: React.FormEvent) {
    e.preventDefault(); setMsg(""); setErr("");
    try {
      const payload = { ...form, latitude: form.latitude ? Number(form.latitude) : null, longitude: form.longitude ? Number(form.longitude) : null };
      const g = await api<any>("/groups", { method: "POST", body: JSON.stringify(payload) });
      setMsg(`Created group “${g.name}”.`); setCreating(false); setForm({ name: "", description: "", area_label: "Maplewood", latitude: "45.5225", longitude: "-122.6760", join_mode: "request" }); await load();
    } catch (e) { setErr(e instanceof Error ? e.message : "Failed"); }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><h1 className="text-2xl font-semibold tracking-tight">Discover nearby people & groups</h1><p className="mt-1 muted">Find meal-prep communities in your area or start your own.</p></div>
        <button className="btn btn-primary" onClick={() => setCreating(v=>!v)}>{creating ? "Cancel" : "Create group"}</button>
      </div>
      {msg && <div className="rounded-xl bg-[var(--brand-soft)] p-3 text-sm text-[var(--brand)]">{msg}</div>}
      {err && <div className="rounded-xl bg-[var(--danger-soft)] p-3 text-sm text-[var(--danger)]">{err}</div>}
      {creating && (
        <form onSubmit={create} className="card p-5 grid gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2"><h2 className="font-semibold">New meal-prep group</h2></div>
          <div><label className="label">Name</label><input className="field" value={form.name} onChange={e=>setForm({...form,name:e.target.value})} required /></div>
          <div><label className="label">Area label</label><input className="field" value={form.area_label} onChange={e=>setForm({...form,area_label:e.target.value})} /></div>
          <div className="sm:col-span-2"><label className="label">Description</label><textarea className="field" rows={2} value={form.description} onChange={e=>setForm({...form,description:e.target.value})} /></div>
          <div><label className="label">Latitude (optional)</label><input className="field" value={form.latitude} onChange={e=>setForm({...form,latitude:e.target.value})} /></div>
          <div><label className="label">Longitude (optional)</label><input className="field" value={form.longitude} onChange={e=>setForm({...form,longitude:e.target.value})} /></div>
          <div><label className="label">Joining</label><select className="field" value={form.join_mode} onChange={e=>setForm({...form,join_mode:e.target.value})}><option value="request">Requests (members ask to join)</option><option value="invite">Invite only</option></select></div>
          <div className="sm:col-span-2"><button className="btn btn-primary">Create group</button></div>
        </form>
      )}
      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="card p-5">
          <h2 className="font-semibold">Groups in your area</h2>
          <div className="mt-4 space-y-3">
            {groups.length === 0 && <p className="text-sm muted">No groups found. Create one to start a local community.</p>}
            {groups.map(g => (
              <div key={g.id} className="rounded-xl border border-[var(--line)] p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div><div className="font-semibold">{g.name}</div><div className="text-sm muted">{g.area_label || "Local"}{g.distance_km != null ? ` · ${g.distance_km} km away` : ""} · {g.member_count} members</div></div>
                  <div className="flex gap-2"><Link href={`/app/groups/${g.id}`} className="btn btn-secondary py-1.5">View</Link><button className="btn btn-primary py-1.5" onClick={()=>join(g.id)}>Join</button></div>
                </div>
                {g.description && <p className="mt-2 text-sm">{g.description}</p>}
              </div>
            ))}
          </div>
        </section>
        <section className="card p-5">
          <h2 className="font-semibold">Nearby people</h2>
          <p className="mt-1 text-sm muted">Based on your location and radius. Exact addresses are not shown.</p>
          <div className="mt-4 space-y-3">
            {people.length === 0 && <p className="text-sm muted">No nearby users found yet. Make sure your profile has coordinates and a shopping radius.</p>}
            {people.map(p => (
              <div key={p.id} className="rounded-xl border border-[var(--line)] p-4">
                <div className="flex items-center justify-between gap-3"><div className="font-semibold">{p.name}</div><span className="pill">{p.distance_km} km</span></div>
                <div className="text-sm muted">{p.location_label}</div>
                <div className="mt-2 flex flex-wrap gap-2">{p.dietary_preferences && <span className="pill pill-brand">{p.dietary_preferences}</span>}{p.allergies && <span className="pill">Allergies: {p.allergies}</span>}</div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
