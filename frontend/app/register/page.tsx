"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("password123");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("Create your account.");

  const persistToken = (token: string) => {
    localStorage.setItem("faceless_token", token);
  };

  const handleRegister = async () => {
    setLoading(true);
    setStatus("Creating account...");

    try {
      const res = await fetch(`${API_URL}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (!res.ok) {
        setStatus(data.detail || "Registration failed.");
        setLoading(false);
        return;
      }

      persistToken(data.access_token);
      setStatus("Account created successfully.");
      setLoading(false);
      router.push("/dashboard");
    } catch (error) {
      setStatus("Unable to reach the server.");
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 py-10 text-slate-100">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl">
        <p className="mb-3 text-xs font-medium uppercase tracking-[0.25em] text-cyan-400">Faceless Video App</p>
        <h1 className="text-3xl font-bold">Register</h1>

        <div className="mt-6 space-y-4">
          <label className="block text-sm text-slate-300">
            Email
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-cyan-500"
            />
          </label>

          <label className="block text-sm text-slate-300">
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-cyan-500"
            />
          </label>

          <button
            onClick={handleRegister}
            disabled={loading}
            className="w-full rounded-lg bg-cyan-500 px-4 py-2 font-medium text-slate-950 hover:bg-cyan-400 disabled:opacity-60"
          >
            {loading ? "Creating account..." : "Register"}
          </button>

          <Link
            href="/login"
            className="block w-full rounded-lg border border-slate-700 px-4 py-2 text-center font-medium hover:border-slate-500"
          >
            Back to login
          </Link>
        </div>

        <div className="mt-6 rounded-xl border border-slate-700 bg-slate-950/60 p-4 text-sm text-slate-300">
          {status}
        </div>
      </div>
    </main>
  );
}
