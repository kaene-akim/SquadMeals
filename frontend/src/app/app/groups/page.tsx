"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function GroupsPage() {
  const [groups, setGroups] = useState<any[]>([]);
  const [err, setErr] = useState("");
  useEffect(() => { api<any[]>("/groups?scope=mine").then(setGroups).catch(e=>setErr(e.message)); }, []);
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><h1 className="text-2xl font-semibold tracking-tight">Your groups</h1><p className="mt-1 muted">Manage meal plans, shopping and cooking with your groups.</p></div>
        <Link href="/app/discover" className="btn btn-primary">Find or create a group</Link>
      </div>
      {err && <div className="rounded-xl bg-[var(--danger-soft)] p-3 text-sm text-[var(--danger)]">{err}</div>}
      <div className="grid gap-4 md:grid-cols-2">
        {groups.length === 0 && <div className="card p-5 text-sm muted">You are not in any groups yet.</div>}
        {groups.map(g => (
          <Link key={g.id} href={`/app/groups/${g.id}`} className="card block p-5 hover:border-[var(--brand)]">
            <div className="flex items-start justify-between gap-3"><h2 className="text-lg font-semibold">{g.name}</h2><span className="pill">{g.member_count} members</span></div>
            <p className="mt-2 text-sm muted">{g.description || "Collaborative meal planning and grocery optimisation."}</p>
            <div className="mt-4 text-sm font-medium text-[var(--brand)]">Open group →</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
