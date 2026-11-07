import { Suspense } from "react";
import { AppShell } from "./AppShell";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center muted">Loading...</div>}>
      <AppShell>{children}</AppShell>
    </Suspense>
  );
}

