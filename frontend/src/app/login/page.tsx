"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("demo@squadmeals.app");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(""); setBusy(true);
    try { await login(email, password); router.push("/app"); }
    catch (err) { setError(err instanceof Error ? err.message : "Login failed"); }
    finally { setBusy(false); }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-6 py-10">
      <form onSubmit={submit} className="card w-full p-6">
        <Link href="/" className="text-sm muted hover:underline">← Back</Link>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight">Sign in</h1>
        <p className="mt-1 text-sm muted">Use the demo account or your own.</p>
        {error && <div className="mt-4 rounded-xl bg-[var(--danger-soft)] p-3 text-sm text-[var(--danger)]">{error}</div>}
        <div className="mt-5 space-y-4">
          <div><label className="label">Email</label><input className="field" type="email" value={email} onChange={e=>setEmail(e.target.value)} required /></div>
          <div><label className="label">Password</label><input className="field" type="password" value={password} onChange={e=>setPassword(e.target.value)} required /></div>
        </div>
        <button className="btn btn-primary mt-5 w-full" disabled={busy}>{busy ? "Signing in..." : "Sign in"}</button>
        <p className="mt-4 text-sm muted">No account? <Link href="/register" className="font-semibold text-[var(--brand)]">Register</Link></p>
      </form>
    </main>
  );
}
