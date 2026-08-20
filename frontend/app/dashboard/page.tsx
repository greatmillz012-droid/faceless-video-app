"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Account = {
  id: number;
  platform: string;
  account_name: string | null;
  connected_at: string;
  extra_data?: Record<string, string>;
};

type Settings = {
  niche: string;
  posts_per_day: number;
  posting_times: string;
  video_length_seconds: number;
  voice_style: string;
  auto_post_enabled: boolean;
};

type Video = {
  id: number;
  status: string;
  file_path: string | null;
  script_text: string | null;
  created_at: string;
};

export default function DashboardPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [settings, setSettings] = useState<Settings | null>(null);
  const [videos, setVideos] = useState<Video[]>([]);
  const [savingSettings, setSavingSettings] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("Ready to connect your social accounts.");

  const loadAccounts = async (jwt: string) => {
    const headers = { Authorization: `Bearer ${jwt}` };
    const [accountsRes, settingsRes, videosRes] = await Promise.all([
      fetch(`${API_URL}/api/social/accounts`, { headers }),
      fetch(`${API_URL}/api/settings`, { headers }),
      fetch(`${API_URL}/api/videos`, { headers }),
    ]);
    if (accountsRes.ok) setAccounts(await accountsRes.json());
    if (settingsRes.ok) setSettings(await settingsRes.json());
    if (videosRes.ok) setVideos(await videosRes.json());
  };

  useEffect(() => {
    const saved = localStorage.getItem("faceless_token");
    if (!saved) {
      router.replace("/login");
      return;
    }

    setToken(saved);
    loadAccounts(saved);
  }, [router]);

  const handleConnect = (platform: "youtube" | "meta") => {
    if (!token) {
      setStatus("Please sign in first.");
      return;
    }

    const url = `${API_URL}/api/social/${platform}/connect?token=${encodeURIComponent(token)}`;
    setStatus(`Redirecting to ${platform} OAuth...`);
    window.location.href = url;
  };

  const logout = () => {
    localStorage.removeItem("faceless_token");
    setToken(null);
    setAccounts([]);
    setStatus("Logged out.");
    router.push("/login");
  };

  const saveSettings = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token || !settings) return;
    setSavingSettings(true);
    setStatus("Saving your publishing schedule...");
    const response = await fetch(`${API_URL}/api/settings`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });
    setSavingSettings(false);
    setStatus(response.ok ? "Schedule saved. Your next video will be uploaded automatically." : "Could not save the schedule.");
    if (response.ok) setSettings(await response.json());
  };

  const youtube = accounts.find((account) => account.platform === "youtube");
  const latestVideo = videos[0];
  const nextPostingTime = settings?.posting_times.split(",").map((time) => time.trim()).find(Boolean) || "Not scheduled";
  const videoUrl = latestVideo?.file_path
    ? `${API_URL}/static/videos/${latestVideo.file_path.split(/[\\/]/).slice(-2).join("/")}`
    : null;

  return (
    <main className="dashboard-shell min-h-screen px-5 py-6 text-slate-100 sm:px-8 sm:py-10">
      <div className="mx-auto max-w-6xl space-y-8">
        <section className="dashboard-header flex flex-col justify-between gap-5 md:flex-row md:items-end">
          <div>
            <p className="eyebrow">Faceless Video App / Control Room</p>
            <h1 className="display-title">Your channel is ready.</h1>
            <p className="mt-3 max-w-2xl text-slate-300">Connected accounts, scheduled publishing, and the next video in one place.</p>
          </div>
          <button onClick={logout} className="quiet-button">Log out</button>
        </section>

        <section className="status-banner">
          <div className="status-pulse" />
          <div>
            <p className="text-sm font-semibold text-emerald-100">Account connected</p>
            <p className="mt-1 text-sm text-emerald-200/75">
              {youtube ? `${youtube.account_name || "YouTube"} is connected. Videos will be uploaded automatically.` : "Connect YouTube to enable automatic uploads."}
            </p>
          </div>
          <span className="ml-auto hidden rounded-full border border-emerald-400/30 px-3 py-1 text-xs text-emerald-200 sm:block">{settings?.auto_post_enabled ? "AUTOMATION ON" : "AUTOMATION OFF"}</span>
        </section>

        <div className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
          <section className="feature-panel">
            <div className="flex items-start justify-between gap-4">
              <div><p className="eyebrow">Next in the queue</p><h2 className="panel-title">Your next video will be posted soon.</h2></div>
              <span className="time-chip">{nextPostingTime}</span>
            </div>
            <div className="mt-8 grid gap-5 sm:grid-cols-[170px_1fr]">
              <div className="video-placeholder"><span className="text-3xl">▶</span><span className="mt-2 text-[10px] uppercase tracking-[0.2em] text-slate-400">Preview pending</span></div>
              <div className="flex flex-col justify-between gap-5">
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-cyan-300">{settings?.niche || "Your chosen niche"}</p>
                  <h3 className="mt-2 text-2xl font-semibold">{latestVideo?.script_text?.slice(0, 90) || "AI script is being prepared"}</h3>
                  <p className="mt-3 text-sm leading-6 text-slate-400">The pipeline generates the script, voiceover, footage, captions, and finished Short automatically.</p>
                </div>
                <div className="flex flex-wrap gap-2 text-xs text-slate-300"><span className="meta-chip">{settings?.video_length_seconds || 60}s short</span><span className="meta-chip">{settings?.voice_style || "professional"} voice</span><span className="meta-chip">YouTube Shorts</span></div>
              </div>
            </div>
          </section>

          <section className="feature-panel">
            <p className="eyebrow">Publishing rhythm</p><h2 className="panel-title">Configure automation</h2>
            {settings && <form onSubmit={saveSettings} className="mt-6 space-y-4">
              <label className="field-label">Niche<input className="field-input" value={settings.niche} onChange={(event) => setSettings({ ...settings, niche: event.target.value })} /></label>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="field-label">Videos per day<input className="field-input" type="number" min="1" max="3" value={settings.posts_per_day} onChange={(event) => setSettings({ ...settings, posts_per_day: Number(event.target.value) })} /></label>
                <label className="field-label">Video length<input className="field-input" type="number" min="30" max="90" value={settings.video_length_seconds} onChange={(event) => setSettings({ ...settings, video_length_seconds: Number(event.target.value) })} /></label>
              </div>
              <label className="field-label">Posting times<input className="field-input" placeholder="09:00,13:00,18:00" value={settings.posting_times} onChange={(event) => setSettings({ ...settings, posting_times: event.target.value })} /></label>
              <label className="field-label">Voice style<select className="field-input" value={settings.voice_style} onChange={(event) => setSettings({ ...settings, voice_style: event.target.value })}><option value="professional">Professional</option><option value="casual">Casual</option><option value="energetic">Energetic</option></select></label>
              <label className="flex items-center gap-3 text-sm text-slate-300"><input type="checkbox" checked={settings.auto_post_enabled} onChange={(event) => setSettings({ ...settings, auto_post_enabled: event.target.checked })} /> Enable automatic uploads</label>
              <button disabled={savingSettings} className="w-full bg-cyan-300 px-4 py-3 text-sm font-bold text-slate-950 disabled:opacity-50">{savingSettings ? "Saving..." : "Save schedule"}</button>
            </form>}
            <div className="mt-5 border-t border-white/10 pt-4 text-sm text-slate-400">{status}</div>
          </section>
        </div>

        <div className="grid gap-6 lg:grid-cols-[360px_minmax(0,1fr)]">
          <section className="feature-panel">
            <h2 className="text-xl font-semibold">Account access</h2>
            <div className="mt-5 space-y-4">
              <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-200">
                Authenticated successfully.
              </div>
              <button
                onClick={logout}
                className="w-full rounded-lg border border-slate-700 px-4 py-2 font-medium text-slate-100 hover:border-slate-500"
              >
                Log out
              </button>
            </div>
          </section>

          <section className="feature-panel">
            <div className="flex items-center justify-between gap-4"><div><p className="eyebrow">Latest render</p><h2 className="panel-title">Video activity</h2></div><span className="text-xs text-slate-400">{videos.length} total</span></div>
            {latestVideo ? <div className="mt-6 overflow-hidden rounded-xl border border-white/10 bg-black/20">{videoUrl ? <video controls className="aspect-video w-full bg-black" src={videoUrl} /> : <div className="flex aspect-video items-center justify-center text-sm text-slate-500">Video is still rendering</div>}<div className="flex items-center justify-between gap-4 p-4"><div><p className="text-sm font-medium">Video #{latestVideo.id}</p><p className="mt-1 text-xs uppercase tracking-[0.16em] text-cyan-300">{latestVideo.status}</p></div><span className="text-xs text-slate-400">{new Date(latestVideo.created_at).toLocaleDateString()}</span></div></div> : <div className="mt-6 rounded-xl border border-dashed border-white/15 p-8 text-center text-sm text-slate-400">Your first generated video will appear here.</div>}
          </section>

          <section className="feature-panel account-panel lg:col-span-2">
            <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
              <h2 className="text-xl font-semibold">Connected accounts</h2>
            </div>

            <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {[
                { platform: "youtube", label: "YouTube Shorts", color: "bg-red-500/10 text-red-200 border-red-500/30" },
                { platform: "meta", label: "Facebook", color: "bg-blue-500/10 text-blue-200 border-blue-500/30" },
              ].map((item) => {
                const account = accounts.find((a) => a.platform === item.platform);
                return (
                  <div key={item.platform} className={`account-card rounded-xl border p-5 ${item.color}`}>
                    <p className="break-words text-sm font-medium">{item.label}</p>
                    <p className="mt-2 min-h-10 break-words text-sm text-slate-200">
                      {account ? account.account_name || "Connected" : "Not connected"}
                    </p>
                    <button
                      onClick={() => handleConnect(item.platform as "youtube" | "meta")}
                      className="connect-button mt-4 min-h-11 w-full rounded-lg bg-slate-950/70 px-4 py-3 text-sm font-semibold hover:bg-slate-900"
                    >
                      {account ? "Reconnect" : "Connect"}
                    </button>
                  </div>
                );
              })}
            </div>

            <div className="mt-6 break-words rounded-xl border border-slate-700 bg-slate-950/60 p-4 text-sm text-slate-300">
              {status}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
