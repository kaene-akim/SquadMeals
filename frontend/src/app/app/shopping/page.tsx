"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function ShoppingPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [err, setErr] = useState("");
  const [msg, setMsg] = useState("");

  async function load() { try { setRows(await api<any[]>("/shopping/my")); } catch (e) { setErr(e instanceof Error ? e.message : "Failed"); } }
  useEffect(() => { void load(); }, []);

  async function toggle(row: any, item: any) {
    setErr(""); setMsg("");
    try {
      await api(`/shopping/assignments/${row.assignment.id}/items/${item.id}?purchased=${!item.purchased}`, { method: "PATCH" });
      setMsg("Shopping progress updated.");
      await load();
    } catch (e) { setErr(e instanceof Error ? e.message : "Failed"); }
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-semibold tracking-tight">Shopping</h1><p className="mt-1 muted">Your individual shopping assignments across groups. Grocery prices shown in comparisons/allocations are simulated sample data in this MVP.</p></div>
      {msg && <div className="rounded-xl bg-[var(--brand-soft)] p-3 text-sm text-[var(--brand)]">{msg}</div>}
      {err && <div className="rounded-xl bg-[var(--danger-soft)] p-3 text-sm text-[var(--danger)]">{err}</div>}
      {rows.length===0 && <div className="card p-5 text-sm muted">No assignments yet. In a group, finalise an approved meal plan and generate a shopping allocation.</div>}
      <div className="space-y-4">
        {rows.map((row, idx) => (
          <section key={idx} className="card p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="font-semibold">{row.group?.name || "Group"} · week of {row.week_start}</h2>
                <div className="text-sm muted">Store: {row.assignment.store_name || "Multiple/assigned"} · Estimated total ${row.assignment.estimated_total?.toFixed(2)} (simulated)</div>
              </div>
              <span className={`pill ${row.assignment.status==='done'?'pill-brand':''}`}>{row.assignment.status}</span>
            </div>
            <div className="mt-4 space-y-2">
              {row.assignment.items?.map((item:any) => (
                <label key={item.id} className="flex cursor-pointer items-start gap-3 rounded-xl border border-[var(--line)] p-3 text-sm hover:bg-[var(--surface-2)]">
                  <input type="checkbox" checked={item.purchased} onChange={() => void toggle(row, item)} className="mt-1" />
                  <span>
                    <span className={item.purchased ? "line-through muted" : "font-medium"}>{item.description}</span>
                    <span className="muted"> — {item.quantity} {item.unit}, est. ${item.estimated_price?.toFixed(2)}</span>
                  </span>
                </label>
              ))}
            </div>
            {row.group_id && <p className="mt-3 text-xs muted">Updates are shared with your group. <a className="text-[var(--brand)] font-medium" href={`/app/groups/${row.group_id}`}>Open group plan</a></p>}

          </section>
        ))}
      </div>
    </div>
  );
}
