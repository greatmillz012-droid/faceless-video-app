"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type User = {
  id: number;
  email: string;
  created_at: string;
};

type Account = {
  id: number;
  platform: string;
  account_name: string | null;
  connected_at: string;
};

const PLATFORM_LABELS: Record<string, { label: string; icon: string }> = {
  youtube: { label: "YouTube", icon: "▶" },
  tiktok: { label: "TikTok", icon: "♪" },
  instagram: { label: "Instagram", icon: "◎" },
  facebook: { label: "Facebook", icon: "f" },
};

export default function AccountPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("faceless_token");
    if (!token) {
      router.replace("/login");
      return;
    }

    const load = async () => {
      setLoading(true);
      setError(null);
      const headers = { Authorization: `Bearer ${token}` };

      try {
        const [userRes, accountsRes] = await Promise.all([
          fetch(`${API_URL}/api/auth/me`, { headers }),
          fetch(`${API_URL}/api/social/accounts`, { headers }),
        ]);

        if (userRes.status === 401 || accountsRes.status === 401) {
          localStorage.removeItem("faceless_token");
          router.replace("/login");
          return;
        }

        if (userRes.ok) {
          setUser(await userRes.json());
        } else {
          setError("Could not load your account details.");
        }

        if (accountsRes.ok) {
          setAccounts(await accountsRes.json());
        }
      } catch (err) {
        setError("Unable to reach the server.");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [router]);

  const logout = () => {
    localStorage.removeItem("faceless_token");
    router.push("/login");
  };

  const createdAt = user?.created_at ? new Date(user.created_at) : null;

  return (
    <main className="dashboard-shell min-h-screen px-5 py-6 text-slate-100 sm:px-8 sm:py-10">
      <div className="mx-auto max-w-4xl space-y-8">
        <section className="dashboard-header flex flex-col justify-between gap-5 md:flex-row md:items-end">
          <div>
            <p className="eyebrow">Faceless Video App / Account</p>
            <h1 className="display-title">Your account is ready.</h1>
            <p className="mt-3 max-w-2xl text-slate-300">
              {user ? `Welcome, ${user.email}.` : "Loading your account overview..."}
            </p>
          </div>
          <button onClick={logout} className="quiet-button">
            Log out
          </button>
        </section>

        {loading && (
          <div className="feature-panel text-sm text-slate-400">Loading your account...</div>
        )}

        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
            {error}
          </div>
        )}

        {!loading && (
          <>
            <section className="status-banner">
              <div className="status-pulse" />
              <div>
                <p className="text-sm font-semibold text-emerald-100">Account created</p>
                <p className="mt-1 text-sm text-emerald-200/75">
                  {createdAt
                    ? `Created on ${createdAt.toLocaleDateString()} at ${createdAt.toLocaleTimeString()}`
                    : "Your account has been created successfully."}
                </p>
              </div>
            </section>

            <section className="feature-panel">
              <p className="eyebrow">Storage</p>
              <h2 className="panel-title">Your data is safely stored</h2>
              <p className="mt-3 text-sm leading-6 text-slate-400">
                Your account details, connected accounts, and video preferences are stored securely on
                our Railway server. You can update them at any time.
              </p>
            </section>

            <section className="feature-panel account-panel">
              <h2 className="text-xl font-semibold">Connected accounts</h2>
              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                {["youtube", "tiktok", "instagram", "facebook"].map((platform) => {
                  const account = accounts.find((a) => a.platform === platform);
                  const meta = PLATFORM_LABELS[platform];
                  return (
                    <div
                      key={platform}
                      className={`account-card rounded-xl border p-5 ${
                        account
                          ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-200"
                          : "border-slate-700 bg-slate-950/60 text-slate-400"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-xl">{meta.icon}</span>
                        <p className="text-sm font-medium">{meta.label}</p>
                      </div>
                      <p className="mt-3 break-words text-sm">
                        {account ? account.account_name || "Connected" : "Not connected"}
                      </p>
                    </div>
                  );
                })}
              </div>
            </section>

            <section className="feature-panel flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="eyebrow">Next step</p>
                <h2 className="panel-title">Configure your posting schedule</h2>
              </div>
              <Link
                href="/settings/video-schedule"
                className="rounded-lg bg-cyan-300 px-4 py-3 text-center text-sm font-bold text-slate-950 hover:bg-cyan-200"
              >
                Video schedule settings
              </Link>
            </section>
          </>
        )}
      </div>
    </main>
  );
}
