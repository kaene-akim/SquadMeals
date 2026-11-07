"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function AppHome() {
  const { user } = useAuth();
  const [groups, setGroups] = useState<any[]>([]);
  const [shopping, setShopping] = useState<any[]>([]);
  const [err, setErr] = useState("");
  useEffect(() => {
    (async () => {
      try {
        const [g, s] = await Promise.all([api<any[]>("/groups?scope=mine"), api<any[]>("/shopping/my")]);
        setGroups(g); setShopping(s);
      } catch (e) { setErr(e instanceof Error ? e.message : "Failed to load"); }
    })();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Welcome back, {user?.name?.split(" ")[0]}</h1>
          <p className="mt-1 muted">Your meal-prep groups, upcoming plans and shopping assignments.</p>
        </div>
        <div className="flex gap-2">
          <Link href="/app/discover" className="btn btn-secondary">Discover groups</Link>
          <Link href="/app/recipes" className="btn btn-primary">Browse recipes</Link>
        </div>
      </div>
      {err && <div className="rounded-xl bg-[var(--danger-soft)] p-3 text-sm text-[var(--danger)]">{err}</div>}
      {!user?.location_label && (
        <div className="card p-4 flex flex-wrap items-center justify-between gap-3">
          <div><div className="font-semibold">Add your location to unlock nearby discovery</div><div className="text-sm muted">Your exact address is never shown publicly. Set an area label and optional coordinates in your profile.</div></div>
          <Link href="/app/profile" className="btn btn-primary">Complete profile</Link>
        </div>
      )}
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="card p-5">
          <div className="flex items-center justify-between"><h2 className="font-semibold">Your groups</h2><Link href="/app/groups" className="text-sm text-[var(--brand)] font-medium">View all</Link></div>
          <div className="mt-4 space-y-3">
            {groups.length === 0 && <p className="text-sm muted">No groups yet. Discover a nearby group or create one.</p>}
            {groups.map(g => (
              <Link key={g.id} href={`/app/groups/${g.id}`} className="block rounded-xl border border-[var(--line)] p-4 hover:bg-[var(--surface-2)]">
                <div className="flex items-center justify-between gap-3"><div className="font-semibold">{g.name}</div><span className="pill">{g.member_count} members</span></div>
                <div className="mt-1 text-sm muted">{g.area_label || "Local group"} · {g.description || "Collaborative meal planning"}</div>
              </Link>
            ))}
          </div>
        </section>
        <section className="card p-5">
          <div className="flex items-center justify-between"><h2 className="font-semibold">Your shopping assignments</h2><Link href="/app/shopping" className="text-sm text-[var(--brand)] font-medium">Open shopping</Link></div>
          <div className="mt-4 space-y-3">
            {shopping.length === 0 && <p className="text-sm muted">No shopping assignments yet. Finalise a group meal plan and generate an allocation.</p>}
            {shopping.slice(0,4).map((s, i) => (
              <div key={i} className="rounded-xl border border-[var(--line)] p-4">
                <div className="flex items-center justify-between gap-3"><div className="font-semibold">{s.group?.name || "Group plan"}</div><span className={`pill ${s.assignment.status === 'done' ? 'pill-brand' : ''}`}>{s.assignment.status}</span></div>
                <div className="mt-1 text-sm muted">Week of {s.week_start} · {s.assignment.items?.length || 0} items · est. ${s.assignment.estimated_total?.toFixed(2)}</div>
                <div className="mt-1 text-xs muted">Prices are simulated sample data.</div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
