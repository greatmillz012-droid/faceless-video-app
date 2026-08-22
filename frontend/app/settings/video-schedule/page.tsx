"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const VOICE_OPTIONS = [
  { value: "natural", label: "Natural" },
  { value: "robotic", label: "Robotic" },
  { value: "slow_and_clear", label: "Slow & Clear" },
  { value: "fast_and_energetic", label: "Fast & Energetic" },
  { value: "whispering", label: "Whispering" },
  { value: "cheerful", label: "Cheerful" },
  { value: "deep_and_resonant", label: "Deep & Resonant" },
];

type Preferences = {
  daily_videos: number;
  post_times: string[];
  voice_effect: string;
};

const DEFAULT_PREFERENCES: Preferences = {
  daily_videos: 1,
  post_times: [],
  voice_effect: "natural",
};

export default function VideoSchedulePage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<Preferences>(DEFAULT_PREFERENCES);
  const [newTime, setNewTime] = useState("09:00");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("faceless_token");
    if (!saved) {
      router.replace("/login");
      return;
    }
    setToken(saved);

    const load = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_URL}/api/settings/preferences`, {
          headers: { Authorization: `Bearer ${saved}` },
        });
        if (res.status === 401) {
          localStorage.removeItem("faceless_token");
          router.replace("/login");
          return;
        }
        if (res.ok) {
          const data = await res.json();
          setPreferences({
            daily_videos: data.daily_videos ?? DEFAULT_PREFERENCES.daily_videos,
            post_times: data.post_times ?? DEFAULT_PREFERENCES.post_times,
            voice_effect: data.voice_effect ?? DEFAULT_PREFERENCES.voice_effect,
          });
        }
      } catch (err) {
        // Keep defaults if the endpoint isn't available yet.
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [router]);

  const addTime = () => {
    if (!newTime) return;
    if (preferences.post_times.includes(newTime)) return;
    const updated = [...preferences.post_times, newTime].sort();
    setPreferences({ ...preferences, post_times: updated });
  };

  const removeTime = (time: string) => {
    setPreferences({
      ...preferences,
      post_times: preferences.post_times.filter((t) => t !== time),
    });
  };

  const formatTime = (time: string) => {
    const [hoursStr, minutesStr] = time.split(":");
    const hours = Number(hoursStr);
    const minutes = Number(minutesStr);
    if (Number.isNaN(hours) || Number.isNaN(minutes)) return time;
    const period = hours >= 12 ? "PM" : "AM";
    const displayHour = hours % 12 === 0 ? 12 : hours % 12;
    return `${displayHour}:${minutesStr.padStart(2, "0")} ${period}`;
  };

  const saveSettings = async () => {
    if (!token) return;
    setSaving(true);
    setMessage(null);

    try {
      const res = await fetch(`${API_URL}/api/settings/preferences`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(preferences),
      });

      if (res.status === 401) {
        localStorage.removeItem("faceless_token");
        router.replace("/login");
        return;
      }

      if (res.ok) {
        setMessage({ type: "success", text: "Your video schedule settings have been saved." });
      } else {
        setMessage({ type: "error", text: "Could not save your settings. Please try again." });
      }
    } catch (err) {
      setMessage({ type: "error", text: "Unable to reach the server." });
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="dashboard-shell min-h-screen px-5 py-6 text-slate-100 sm:px-8 sm:py-10">
      <div className="mx-auto max-w-3xl space-y-8">
        <section className="dashboard-header flex flex-col justify-between gap-5 md:flex-row md:items-end">
          <div>
            <p className="eyebrow">Faceless Video App / Settings</p>
            <h1 className="display-title">Video schedule</h1>
            <p className="mt-3 max-w-2xl text-slate-300">
              Choose how many videos to post each day, when they go live, and the voice style used
              for narration.
            </p>
          </div>
          <Link href="/account" className="quiet-button">
            Back to account
          </Link>
        </section>

        {loading ? (
          <div className="feature-panel text-sm text-slate-400">Loading your settings...</div>
        ) : (
          <>
            <section className="feature-panel">
              <p className="eyebrow">Frequency</p>
              <h2 className="panel-title">Daily videos</h2>
              <label className="field-label mt-5 block max-w-xs">
                Number of videos per day
                <select
                  className="field-input"
                  value={preferences.daily_videos}
                  onChange={(event) =>
                    setPreferences({ ...preferences, daily_videos: Number(event.target.value) })
                  }
                >
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
              </label>
            </section>

            <section className="feature-panel">
              <p className="eyebrow">Timing</p>
              <h2 className="panel-title">Post times</h2>
              <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-end">
                <label className="field-label flex-1">
                  Add a time
                  <input
                    type="time"
                    className="field-input"
                    value={newTime}
                    onChange={(event) => setNewTime(event.target.value)}
                  />
                </label>
                <button
                  onClick={addTime}
                  className="h-fit rounded-lg bg-cyan-300 px-4 py-3 text-sm font-bold text-slate-950 hover:bg-cyan-200"
                >
                  Add time
                </button>
              </div>

              <div className="mt-5 space-y-2">
                {preferences.post_times.length === 0 && (
                  <p className="text-sm text-slate-400">No post times added yet.</p>
                )}
                {preferences.post_times.map((time) => (
                  <div
                    key={time}
                    className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-950/60 px-4 py-3 text-sm"
                  >
                    <span className="time-chip">{formatTime(time)}</span>
                    <button
                      onClick={() => removeTime(time)}
                      className="text-xs font-semibold text-red-300 hover:text-red-200"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            </section>

            <section className="feature-panel">
              <p className="eyebrow">Narration</p>
              <h2 className="panel-title">Voice effect</h2>
              <label className="field-label mt-5 block max-w-sm">
                Voice style
                <select
                  className="field-input"
                  value={preferences.voice_effect}
                  onChange={(event) =>
                    setPreferences({ ...preferences, voice_effect: event.target.value })
                  }
                >
                  {VOICE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
            </section>

            <section className="feature-panel">
              <button
                onClick={saveSettings}
                disabled={saving}
                className="w-full rounded-lg bg-cyan-300 px-4 py-3 text-sm font-bold text-slate-950 hover:bg-cyan-200 disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save settings"}
              </button>

              {message && (
                <div
                  className={`mt-4 rounded-lg border p-4 text-sm ${
                    message.type === "success"
                      ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-200"
                      : "border-red-500/30 bg-red-500/10 text-red-200"
                  }`}
                >
                  {message.text}
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </main>
  );
}
