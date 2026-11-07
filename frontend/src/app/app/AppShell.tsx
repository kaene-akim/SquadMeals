"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";

const nav = [
  { href: "/app", label: "Home" },
  { href: "/app/discover", label: "Discover" },
  { href: "/app/groups", label: "Groups" },
  { href: "/app/recipes", label: "Recipes" },
  { href: "/app/shopping", label: "Shopping" },
  { href: "/app/profile", label: "Profile" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => { if (!loading && !user) router.replace("/login"); }, [loading, user, router]);
  if (loading) return <div className="flex min-h-screen items-center justify-center muted">Loading your workspace...</div>;
  if (!user) return null;

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-[var(--line)] bg-[color:rgba(246,244,239,0.92)] backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3 sm:px-6">
          <Link href="/app" className="flex items-center gap-2 font-semibold tracking-tight">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--brand)] text-sm text-white">SM</span>
            <span className="hidden sm:inline">SquadMeals</span>
          </Link>
          <nav className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto">
            {nav.map((item) => {
              const active = item.href === "/app" ? pathname === "/app" : pathname.startsWith(item.href);
              return (
                <Link key={item.href} href={item.href} className={`rounded-lg px-3 py-2 text-sm font-medium whitespace-nowrap ${active ? "bg-[var(--brand-soft)] text-[var(--brand)]" : "text-[var(--muted)] hover:bg-[var(--surface)]"}`}>
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="hidden items-center gap-3 md:flex">
            <span className="text-sm muted">{user.name}</span>
            <button className="btn btn-secondary py-1.5" onClick={() => { logout(); router.push("/"); }}>Sign out</button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">{children}</main>
    </div>
  );
}
