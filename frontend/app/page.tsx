"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("faceless_token") : null;
    router.replace(token ? "/dashboard" : "/login");
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-100">
      <p className="text-sm uppercase tracking-[0.25em] text-cyan-400">Loading...</p>
    </main>
  );
}
