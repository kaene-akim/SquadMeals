"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();
  useEffect(() => { if (!loading && user) router.replace("/app"); }, [loading, user, router]);

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-10">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--brand)] text-white font-bold">SM</div>
          <div>
            <div className="text-lg font-semibold tracking-tight">SquadMeals</div>
            <div className="text-sm muted">Plan together. Shop smarter.</div>
          </div>
        </div>
        <div className="flex gap-2">
          <Link className="btn btn-secondary" href="/login">Sign in</Link>
          <Link className="btn btn-primary" href="/register">Create account</Link>
        </div>
      </header>
      <section className="grid flex-1 items-center gap-10 py-14 lg:grid-cols-[1.1fr_0.9fr]">
        <div>
          <p className="pill pill-brand">Social meal prep + grocery optimisation</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight text-balance sm:text-5xl">Form a local meal-prep squad, plan the week, and buy ingredients at the best combined cost.</h1>
          <p className="mt-4 max-w-2xl text-lg muted">Discover nearby people, vote on recipes, consolidate ingredients across meals, compare simulated sample grocery prices, and split shopping fairly by cost and distance.</p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link className="btn btn-primary" href="/register">Get started</Link>
            <Link className="btn btn-secondary" href="/login">Explore with demo account</Link>
          </div>
          <p className="mt-3 text-sm muted">Demo: <span className="font-mono">demo@squadmeals.app</span> / <span className="font-mono">password123</span></p>
        </div>
        <div className="card p-6">
          <h2 className="text-base font-semibold">What the MVP demonstrates</h2>
          <ul className="mt-4 space-y-3 text-sm">
            {[
              "Location-aware discovery with privacy-conscious profiles",
              "Group meal planning with proposals, votes and approvals",
              "Automatic ingredient consolidation across approved recipes",
              "Grocery price comparison across nearby stores (simulated sample data)",
              "Intelligent shopping allocation with fairness and travel awareness",
              "Individual shopping lists and group progress tracking",
            ].map((t) => (
              <li key={t} className="flex gap-3"><span className="mt-1 h-2.5 w-2.5 rounded-full bg-[var(--brand)]" /><span>{t}</span></li>
            ))}
          </ul>
          <div className="mt-5 rounded-xl bg-[var(--accent-soft)] p-4 text-sm text-[#7a3b14]">
            Grocery prices in this MVP are simulated sample data. The pricing layer is designed so real retailer APIs can be integrated later.
          </div>
        </div>
      </section>
    </main>
  );
}
