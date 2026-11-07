"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (password.length < 6) { setError("Password must be at least 6 characters."); return; }
    setBusy(true);
    try { await register(name, email, password); router.push("/app/profile?setup=1"); }
    catch (err) { setError(err instanceof Error ? err.message : "Registration failed"); }
    finally { setBusy(false); }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-6 py-10">
      <form onSubmit={submit} className="card w-full p-6">
        <Link href="/" className="text-sm muted hover:underline">← Back</Link>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight">Create your account</h1>
        <p className="mt-1 text-sm muted">Set up your profile, then discover nearby meal-prep groups.</p>
        {error && <div className="mt-4 rounded-xl bg-[var(--danger-soft)] p-3 text-sm text-[var(--danger)]">{error}</div>}
        <div className="mt-5 space-y-4">
          <div><label className="label">Name</label><input className="field" value={name} onChange={e=>setName(e.target.value)} required minLength={2} /></div>
          <div><label className="label">Email</label><input className="field" type="email" value={email} onChange={e=>setEmail(e.target.value)} required /></div>
          <div><label className="label">Password</label><input className="field" type="password" value={password} onChange={e=>setPassword(e.target.value)} required minLength={6} /></div>
        </div>
        <button className="btn btn-primary mt-5 w-full" disabled={busy}>{busy ? "Creating account..." : "Create account"}</button>
        <p className="mt-4 text-sm muted">Already registered? <Link href="/login" className="font-semibold text-[var(--brand)]">Sign in</Link></p>
      </form>
    </main>
  );
}
