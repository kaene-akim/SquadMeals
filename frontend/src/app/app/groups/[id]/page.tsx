"use client";
import { Suspense } from "react";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

function GroupDetailInner() {
  const params = useParams<{ id: string }>();
  const groupId = Number(params.id);
  const { user } = useAuth();
  const [group, setGroup] = useState<any>(null);
  const [members, setMembers] = useState<any[]>([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [plans, setPlans] = useState<any[]>([]);
  const [recipes, setRecipes] = useState<any[]>([]);
  const [requests, setRequests] = useState<any[]>([]);
  const [cooking, setCooking] = useState<any[]>([]);
  const [msgText, setMsgText] = useState("");
  const [newRecipeId, setNewRecipeId] = useState("");
  const [activePlan, setActivePlan] = useState<number | null>(null);
  const [ingredients, setIngredients] = useState<any[] | null>(null);
  const [comparison, setComparison] = useState<any[] | null>(null);
  const [assignments, setAssignments] = useState<any[] | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState("");

  const load = useCallback(async () => {
    setError("");
    try {
      const g = await api<any>(`/groups/${groupId}`);
      setGroup(g);
      if (g.is_member) {
        const [m, msgs, p, r, c] = await Promise.all([
          api<any[]>(`/groups/${groupId}/members`),
          api<any[]>(`/groups/${groupId}/messages`),
          api<any[]>(`/groups/${groupId}/plans`),
          api<any[]>(`/recipes`),
          api<any[]>(`/groups/${groupId}/cooking`),
        ]);
        setMembers(m); setMessages(msgs); setPlans(p); setRecipes(r); setCooking(c);
        if (g.my_role === "admin") setRequests(await api<any[]>(`/groups/${groupId}/requests`).catch(()=>[]));
        if (!activePlan && p.length) setActivePlan(p[0].id);
      }
    } catch (e) { setError(e instanceof Error ? e.message : "Failed to load group"); }
  }, [groupId, activePlan]);

  useEffect(() => { void load(); }, [load]);

  async function act(label: string, fn: () => Promise<void>) {
    setBusy(label); setError(""); setNotice("");
    try { await fn(); setNotice(`${label} completed.`); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : "Action failed"); }
    finally { setBusy(""); }
  }

  async function selectPlan(planId: number) {
    setActivePlan(planId); setIngredients(null); setComparison(null); setAssignments(null);
    try { setAssignments(await api<any[]>(`/groups/${groupId}/plans/${planId}/assignments`)); } catch {}
  }

  const plan = plans.find(p => p.id === activePlan) || null;

  if (!group) return <div className="muted">Loading group...</div>;

  if (!group.is_member) {
    return (
      <div className="max-w-2xl space-y-4">
        <div className="card p-6">
          <h1 className="text-2xl font-semibold">{group.name}</h1>
          <p className="mt-2 muted">{group.area_label} · {group.member_count} members</p>
          <p className="mt-3">{group.description}</p>
          {group.join_request_status === "pending" ? <div className="mt-4 pill pill-accent">Join request pending</div> :
            <button className="btn btn-primary mt-4" disabled={!!busy} onClick={()=>act("Join request", async()=>{ await api(`/groups/${groupId}/join`, {method:"POST"}); })}>Request to join</button>}
          {error && <div className="mt-3 text-sm text-[var(--danger)]">{error}</div>}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{group.name}</h1>
          <p className="mt-1 muted">{group.area_label} · {group.member_count} members · your role: {group.my_role}</p>
          <p className="mt-1 text-sm">{group.description}</p>
        </div>
      </div>
      {notice && <div className="rounded-xl bg-[var(--brand-soft)] p-3 text-sm text-[var(--brand)]">{notice}</div>}
      {error && <div className="rounded-xl bg-[var(--danger-soft)] p-3 text-sm text-[var(--danger)]">{error}</div>}

      <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
        <section className="space-y-6">
          <div className="card p-5">
            <h2 className="font-semibold">Members</h2>
            <div className="mt-3 space-y-2">{members.map(m => <div key={m.id} className="flex items-center justify-between rounded-lg border border-[var(--line)] px-3 py-2 text-sm"><span>{m.name}</span><span className="pill">{m.role}</span></div>)}</div>
            {group.my_role === "admin" && requests.length > 0 && (
              <div className="mt-4">
                <h3 className="text-sm font-semibold">Pending requests</h3>
                {requests.map(r => <div key={r.user_id} className="mt-2 flex items-center justify-between text-sm"><span>{r.name}</span><button className="btn btn-secondary py-1" onClick={()=>act("Approval", async()=>{ await api(`/groups/${groupId}/requests/${r.user_id}/approve`, {method:"POST"}); })}>Approve</button></div>)}
              </div>
            )}
          </div>
          <div className="card p-5">
            <h2 className="font-semibold">Group discussion</h2>
            <div className="mt-3 max-h-64 space-y-2 overflow-auto pr-1">
              {messages.map(m => <div key={m.id} className="rounded-lg bg-[var(--surface-2)] p-2 text-sm"><span className="font-semibold">{m.user_name}:</span> {m.content}</div>)}
              {messages.length===0 && <p className="text-sm muted">No messages yet.</p>}
            </div>
            <form className="mt-3 flex gap-2" onSubmit={e=>{e.preventDefault(); if(!msgText.trim()) return; void act("Message", async()=>{ await api(`/groups/${groupId}/messages`, {method:"POST", body: JSON.stringify({content: msgText})}); setMsgText(""); });}}>
              <input className="field" value={msgText} onChange={e=>setMsgText(e.target.value)} placeholder="Share an update..." />
              <button className="btn btn-primary">Send</button>
            </form>
          </div>
          <div className="card p-5">
            <h2 className="font-semibold">Cooking sessions</h2>
            <div className="mt-3 space-y-2">{cooking.map(c => <div key={c.id} className="rounded-lg border border-[var(--line)] p-3 text-sm"><div className="font-semibold">{c.title}</div><div className="muted">{c.status}{c.scheduled_at ? ` · ${new Date(c.scheduled_at).toLocaleString()}` : ""}</div><div className="mt-2 flex gap-2">{c.status!=="done" && <button className="btn btn-secondary py-1" onClick={()=>act("Session update", async()=>{ await api(`/groups/${groupId}/cooking/${c.id}?status=${c.status==="planned"?"in_progress":"done"}`, {method:"PATCH"}); })}>{c.status==="planned"?"Start":"Mark done"}</button>}</div></div>)}{cooking.length===0 && <p className="text-sm muted">No cooking sessions yet.</p>}</div>
            <button className="btn btn-secondary mt-3" onClick={()=>{ const title = prompt("Cooking session title"); if(title) void act("Cooking session", async()=>{ await api(`/groups/${groupId}/cooking`, {method:"POST", body: JSON.stringify({title, meal_plan_id: activePlan})}); }); }}>Schedule cooking session</button>
          </div>
        </section>

        <section className="space-y-6">
          <div className="card p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="font-semibold">Weekly meal plans</h2>
              <button className="btn btn-secondary" onClick={()=>{ const ws = prompt("Week start date (YYYY-MM-DD)", new Date().toISOString().slice(0,10)); if(ws) void act("Meal plan", async()=>{ await api(`/groups/${groupId}/plans`, {method:"POST", body: JSON.stringify({week_start: ws, portions_per_member: 1})}); }); }}>New plan</button>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">{plans.map(p => <button key={p.id} className={`pill ${activePlan===p.id?"pill-brand":""}`} onClick={()=>void selectPlan(p.id)}>{p.week_start} · {p.status}</button>)}</div>
            {!plan ? <p className="mt-4 text-sm muted">Create or select a meal plan.</p> : (
              <div className="mt-4 space-y-4">
                <div className="flex flex-wrap items-center gap-2">
                  <select className="field max-w-xs" value={newRecipeId} onChange={e=>setNewRecipeId(e.target.value)}>
                    <option value="">Propose a recipe...</option>
                    {recipes.map(r => <option key={r.id} value={r.id}>{r.name} ({r.dietary_tags || "general"})</option>)}
                  </select>
                  <button className="btn btn-primary" disabled={!newRecipeId||!!busy} onClick={()=>void act("Recipe proposal", async()=>{ await api(`/groups/${groupId}/plans/${plan.id}/recipes`, {method:"POST", body: JSON.stringify({recipe_id:Number(newRecipeId)})}); setNewRecipeId(""); })}>Add to plan</button>
                  <button className="btn btn-secondary" disabled={!!busy} onClick={()=>void act("Finalize plan", async()=>{ await api(`/groups/${groupId}/plans/${plan.id}/finalize`, {method:"POST"}); })}>Finalize</button>
                </div>
                <div className="space-y-2">
                  {plan.recipes.map((r:any) => (
                    <div key={r.id} className="rounded-xl border border-[var(--line)] p-3">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div><div className="font-semibold">{r.recipe_name}</div><div className="text-sm muted">Votes: {r.votes} · {r.approved ? "approved" : "proposed"}</div></div>
                        <div className="flex gap-2">
                          <button className="btn btn-secondary py-1" onClick={()=>void act("Vote", async()=>{ await api(`/groups/${groupId}/plans/${plan.id}/recipes/${r.id}/vote`, {method:"POST", body: JSON.stringify({value:1})}); })}>Upvote</button>
                          <button className="btn btn-secondary py-1" onClick={()=>void act("Vote", async()=>{ await api(`/groups/${groupId}/plans/${plan.id}/recipes/${r.id}/vote`, {method:"POST", body: JSON.stringify({value:-1})}); })}>Downvote</button>
                          <button className="btn btn-primary py-1" onClick={()=>void act("Approval", async()=>{ await api(`/groups/${groupId}/plans/${plan.id}/recipes/${r.id}/approve?approved=${!r.approved}`, {method:"POST"}); })}>{r.approved?"Unapprove":"Approve"}</button>
                        </div>
                      </div>
                    </div>
                  ))}
                  {plan.recipes.length===0 && <p className="text-sm muted">No recipes proposed yet.</p>}
                </div>
                <div className="flex flex-wrap gap-2">
                  <button className="btn btn-secondary" onClick={()=>void act("Ingredient consolidation", async()=>{ setIngredients(await api<any[]>(`/groups/${groupId}/plans/${plan.id}/ingredients`)); })}>Consolidate ingredients</button>
                  <button className="btn btn-secondary" onClick={()=>void act("Price comparison", async()=>{ setComparison(await api<any[]>(`/groups/${groupId}/plans/${plan.id}/price-comparison`)); })}>Compare grocery prices</button>
                  <button className="btn btn-primary" onClick={()=>void act("Shopping allocation", async()=>{ setAssignments(await api<any[]>(`/groups/${groupId}/plans/${plan.id}/allocate`, {method:"POST"})); })}>Generate shopping allocation</button>
                  <button className="btn btn-secondary" onClick={()=>void act("Assignments refresh", async()=>{ setAssignments(await api<any[]>(`/groups/${groupId}/plans/${plan.id}/assignments`)); })}>Refresh assignments</button>
                </div>
              </div>
            )}
          </div>

          {ingredients && (
            <div className="card p-5">
              <h2 className="font-semibold">Consolidated ingredients</h2>
              <p className="mt-1 text-sm muted">Duplicate ingredients across approved recipes are combined and scaled to the group’s portion count.</p>
              <div className="mt-3 overflow-x-auto"><table className="w-full text-sm"><thead><tr className="text-left text-[var(--muted)]"><th className="py-1 pr-3">Ingredient</th><th className="py-1 pr-3">Total</th><th className="py-1">Sources</th></tr></thead><tbody>{ingredients.map((i:any)=> <tr key={`${i.ingredient_id}-${i.unit}`} className="border-t border-[var(--line)]"><td className="py-2 pr-3 font-medium">{i.ingredient_name}</td><td className="py-2 pr-3">{i.total_quantity} {i.unit}</td><td className="py-2 muted">{i.source_recipes.join(", ")}</td></tr>)}</tbody></table></div>
            </div>
          )}

          {comparison && (
            <div className="card p-5">
              <h2 className="font-semibold">Grocery price comparison</h2>
              <div className="mt-2 rounded-xl bg-[var(--accent-soft)] p-3 text-sm text-[#7a3b14]">Prices shown are <strong>simulated sample data</strong> for the MVP. The pricing service is designed for later retailer API/data provider integration.</div>
              <div className="mt-4 space-y-4">{comparison.map((c:any)=> (
                <div key={c.ingredient_id} className="rounded-xl border border-[var(--line)] p-4">
                  <div className="font-semibold">{c.ingredient_name} <span className="font-normal muted">({c.required_quantity} {c.unit} needed)</span></div>
                  {c.best_option ? <div className="mt-1 text-sm">Best option: <span className="font-semibold">{c.best_option.store.name}</span> · {c.best_option.brand} · {c.best_option.packages_needed} package(s) · ${c.best_option.total_cost.toFixed(2)} {c.best_option.store.distance_km!=null?`· ${c.best_option.store.distance_km} km`:''}</div> : <div className="mt-1 text-sm muted">No compatible price options found.</div>}
                  <details className="mt-2"><summary className="cursor-pointer text-sm text-[var(--brand)]">All options</summary>
                    <div className="mt-2 space-y-1 text-sm">{c.options.map((o:any,i:number)=><div key={i} className="flex justify-between gap-3 border-t border-[var(--line)] py-1"><span>{o.store.name} · {o.brand} · {o.package_size}{o.unit}</span><span>${o.total_cost.toFixed(2)} <span className="muted">(${o.price}/pkg)</span></span></div>)}</div>
                  </details>
                </div>
              ))}</div>
            </div>
          )}

          {assignments && (
            <div className="card p-5">
              <h2 className="font-semibold">Shopping assignments & progress</h2>
              <p className="mt-1 text-sm muted">Allocation considers estimated grocery cost, store distance and fairness across members. Mark items purchased to update group progress.</p>
              <div className="mt-4 space-y-4">{assignments.map((a:any)=> (
                <div key={a.id} className="rounded-xl border border-[var(--line)] p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2"><div className="font-semibold">{a.user_name}{a.user_id===user?.id?" (you)":""} <span className="font-normal muted">· {a.store_name||"assigned store"}</span></div><span className={`pill ${a.status==="done"?"pill-brand":""}`}>{a.status} · ${a.estimated_total?.toFixed(2)}</span></div>
                  <div className="mt-3 space-y-2">{a.items.map((item:any)=> (
                    <label key={item.id} className="flex cursor-pointer items-start gap-3 text-sm"><input type="checkbox" checked={item.purchased} onChange={()=>void act("Item update", async()=>{ await api(`/shopping/assignments/${a.id}/items/${item.id}?purchased=${!item.purchased}`, {method:"PATCH"}); const updated = await api<any[]>(`/groups/${groupId}/plans/${activePlan}/assignments`); setAssignments(updated); })} className="mt-1" /><span className={item.purchased?"line-through muted":""}>{item.description} <span className="muted">({item.quantity} {item.unit}, ${item.estimated_price?.toFixed(2)})</span></span></label>
                  ))}</div>
                </div>
              ))}</div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default function GroupDetailPage() {
  return <Suspense fallback={<div className="muted">Loading group...</div>}><GroupDetailInner /></Suspense>;
}
