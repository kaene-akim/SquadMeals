"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function RecipesPage() {
  const [recipes, setRecipes] = useState<any[]>([]);
  const [q, setQ] = useState("");
  const [dietary, setDietary] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [maxMinutes, setMaxMinutes] = useState("");
  const [ingredient, setIngredient] = useState("");
  const [selected, setSelected] = useState<any>(null);
  const [err, setErr] = useState("");

  async function load() {
    setErr("");
    try {
      const params = new URLSearchParams();
      if (q) params.set("q", q);
      if (dietary) params.set("dietary", dietary);
      if (cuisine) params.set("cuisine", cuisine);
      if (maxMinutes) params.set("max_minutes", maxMinutes);
      if (ingredient) params.set("ingredient", ingredient);
      setRecipes(await api<any[]>(`/recipes?${params.toString()}`));
    } catch (e) { setErr(e instanceof Error ? e.message : "Failed"); }
  }
  useEffect(() => { void load(); }, []);

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-semibold tracking-tight">Recipes</h1><p className="mt-1 muted">Browse by ingredients, cuisine, preparation time and dietary requirements. Add recipes to a group meal plan from the group page.</p></div>
      <form onSubmit={e=>{e.preventDefault(); void load();}} className="card p-4 grid gap-3 md:grid-cols-5">
        <input className="field" placeholder="Search recipes" value={q} onChange={e=>setQ(e.target.value)} />
        <input className="field" placeholder="Ingredient" value={ingredient} onChange={e=>setIngredient(e.target.value)} />
        <input className="field" placeholder="Cuisine" value={cuisine} onChange={e=>setCuisine(e.target.value)} />
        <input className="field" placeholder="Dietary (e.g. vegetarian)" value={dietary} onChange={e=>setDietary(e.target.value)} />
        <div className="flex gap-2"><input className="field" placeholder="Max minutes" value={maxMinutes} onChange={e=>setMaxMinutes(e.target.value)} /><button className="btn btn-primary">Search</button></div>
      </form>
      {err && <div className="rounded-xl bg-[var(--danger-soft)] p-3 text-sm text-[var(--danger)]">{err}</div>}
      <div className="grid gap-6 lg:grid-cols-[1fr_0.95fr]">
        <div className="space-y-3">
          {recipes.map(r => (
            <button key={r.id} onClick={()=>setSelected(r)} className={`card w-full p-4 text-left ${selected?.id===r.id ? "border-[var(--brand)]" : ""}`}>
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div><div className="font-semibold">{r.name}</div><div className="text-sm muted">{r.cuisine} · {r.prep_minutes + r.cook_minutes} min · serves {r.servings}</div></div>
                <div className="flex flex-wrap gap-2">{r.dietary_tags?.split(",").filter(Boolean).slice(0,3).map((t:string)=><span key={t} className="pill pill-brand">{t}</span>)}</div>
              </div>
              <p className="mt-2 text-sm">{r.description}</p>
            </button>
          ))}
          {recipes.length===0 && <div className="card p-5 text-sm muted">No recipes match the current filters.</div>}
        </div>
        <div className="card p-5 min-h-[300px]">
          {!selected ? <p className="text-sm muted">Select a recipe to see ingredients and instructions.</p> : (
            <div>
              <h2 className="text-xl font-semibold">{selected.name}</h2>
              <p className="mt-1 text-sm muted">{selected.cuisine} · prep {selected.prep_minutes} min · cook {selected.cook_minutes} min · serves {selected.servings}</p>
              <h3 className="mt-5 font-semibold">Ingredients</h3>
              <ul className="mt-2 space-y-1 text-sm">{selected.ingredients?.map((i:any,idx:number)=><li key={idx}>• {i.quantity} {i.unit} {i.ingredient_name} <span className="muted">({i.category})</span></li>)}</ul>
              <h3 className="mt-5 font-semibold">Instructions</h3>
              <p className="mt-2 whitespace-pre-wrap text-sm">{selected.instructions}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
