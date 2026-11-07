import { useCallback, useEffect, useRef, useState } from "react";
import History from "./pages/History.jsx";

async function request(path, options = {}) {
  const response = await fetch(path, { credentials: "include", ...options });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const error = new Error(body.detail || `Request failed (${response.status})`);
    error.status = response.status;
    throw error;
  }
  if (response.status === 204) return null;
  return response.json();
}

export default function App() {
  const [user, setUser] = useState(null);
  const [guest, setGuest] = useState(false);
  const [guestModeEnabled, setGuestModeEnabled] = useState(false);
  const [guestJobTtlHours, setGuestJobTtlHours] = useState(24);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [signup, setSignup] = useState(false);
  const [mode, setMode] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const fileInput = useRef(null);
  const modeRef = useRef(null);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    try {
      setHistory(await request("/api/conversions"));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    request("/api/config").then((config) => {
      setGuestModeEnabled(config.guest_mode);
      setGuestJobTtlHours(config.guest_job_ttl_hours);
    }).catch((err) => {
      setError(err.message);
    });
    request("/api/auth/me").then(setUser).catch((err) => {
      if (err.status !== 401) setError(err.message);
    });
  }, []);

  useEffect(() => {
    if (user || guest) loadHistory();
  }, [user, guest, loadHistory]);

  useEffect(() => {
    const pending = history.some((item) => ["pending", "processing"].includes(item.status));
    if (!pending) return undefined;
    const timer = window.setInterval(loadHistory, 2500);
    return () => window.clearInterval(timer);
  }, [history, loadHistory]);

  async function submitAuth(event) {
    event.preventDefault();
    setError("");
    try {
      setUser(await request(`/api/auth/${signup ? "signup" : "login"}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      }));
      setPassword("");
    } catch (err) {
      setError(err.message);
    }
  }

  function chooseFile(nextMode) {
    modeRef.current = nextMode;
    setMode(nextMode);
    setError("");
    if (fileInput.current) {
      fileInput.current.accept = nextMode === "compress"
        ? ".pdf,application/pdf"
        : ".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document";
    }
    fileInput.current?.click();
  }

  async function upload(event) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || !modeRef.current) return;
    setLoading(true);
    setError("");
    setNotice("");
    const form = new FormData();
    form.append("file", file);
    try {
      const result = await request(`/api/${modeRef.current}`, { method: "POST", body: form });
      setNotice(`Job #${result.id} added to the queue.`);
      await loadHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    await request("/api/auth/logout", { method: "POST" });
    setUser(null);
    setHistory([]);
  }

  if (!user && !guest) {
    return (
      <main className="mx-auto flex min-h-screen max-w-md items-center px-5">
        <form onSubmit={submitAuth} className="w-full rounded-3xl bg-white p-8 shadow-xl shadow-slate-200/60">
          <p className="text-sm font-bold uppercase tracking-widest text-indigo-600">Conprezer</p>
          <h1 className="mt-3 text-3xl font-bold">{signup ? "Create your account" : "Welcome back"}</h1>
          <p className="mt-2 text-slate-500">Your files stay private and are processed by your local service.</p>
          <label className="mt-7 block text-sm font-medium">Email</label>
          <input required type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-indigo-500" />
          <label className="mt-4 block text-sm font-medium">Password (at least 8 characters)</label>
          <input required minLength={8} type="password" autoComplete={signup ? "new-password" : "current-password"} value={password} onChange={(e) => setPassword(e.target.value)} className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-indigo-500" />
          {error && <p role="alert" className="mt-4 text-sm text-red-600">{error}</p>}
          <button className="mt-6 w-full rounded-xl bg-indigo-600 px-4 py-3 font-semibold text-white hover:bg-indigo-700">{signup ? "Sign up" : "Sign in"}</button>
          <button type="button" onClick={() => { setSignup(!signup); setError(""); }} className="mt-4 w-full text-sm text-slate-600 hover:text-indigo-600">
            {signup ? "Already have an account? Sign in" : "New here? Create an account"}
          </button>
          {guestModeEnabled && (
            <button type="button" onClick={() => { setGuest(true); setError(""); }} className="mt-3 w-full rounded-xl border border-slate-200 px-4 py-3 font-semibold text-slate-700 hover:border-indigo-300 hover:text-indigo-600">
              Continue as guest
            </button>
          )}
        </form>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-5xl px-5 py-10 md:py-16">
      <header className="flex items-center justify-between">
        <div>
          <p className="text-sm font-bold uppercase tracking-widest text-indigo-600">Conprezer</p>
          <h1 className="mt-2 text-3xl font-bold md:text-4xl">PDF tools, privately.</h1>
        </div>
        {user
          ? <button onClick={logout} className="rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-white">Sign out</button>
          : <button onClick={() => { setGuest(false); setHistory([]); setError(""); }} className="rounded-lg px-3 py-2 text-sm text-indigo-600 hover:bg-white">Sign in</button>}
      </header>
      <p className="mt-3 text-slate-500">
        {user ? `Signed in as ${user.email}.` : `Using guest mode. Your job and download are available for ${guestJobTtlHours} hours.`} Uploads are limited to 25 MiB.
      </p>
      <section className="mt-9 grid gap-4 md:grid-cols-2">
        <button onClick={() => chooseFile("convert")} disabled={loading} className="rounded-2xl bg-indigo-600 p-7 text-left text-white shadow-lg shadow-indigo-200 transition hover:-translate-y-0.5 hover:bg-indigo-700 disabled:opacity-60">
          <span className="text-2xl">DOCX → PDF</span>
          <span className="mt-2 block text-sm text-indigo-100">Choose a Word document to convert</span>
        </button>
        <button onClick={() => chooseFile("compress")} disabled={loading} className="rounded-2xl bg-white p-7 text-left shadow-lg shadow-slate-200/60 transition hover:-translate-y-0.5 disabled:opacity-60">
          <span className="text-2xl font-semibold">Compress PDF</span>
          <span className="mt-2 block text-sm text-slate-500">Reduce the size of a PDF document</span>
        </button>
      </section>
      <input ref={fileInput} type="file" accept={mode === "compress" ? ".pdf,application/pdf" : ".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"} onChange={upload} className="hidden" />
      {loading && <p role="status" className="mt-5 text-sm text-indigo-600">Working…</p>}
      {notice && <p className="mt-5 text-sm text-emerald-700">{notice}</p>}
      {error && <p role="alert" className="mt-5 text-sm text-red-600">{error}</p>}
      <section className="mt-10 rounded-2xl bg-white p-6 shadow-sm shadow-slate-200/70 md:p-8">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold">{guest ? "Guest jobs" : "Your history"}</h2>
          <button onClick={loadHistory} className="text-sm font-medium text-indigo-600 hover:text-indigo-800">Refresh</button>
        </div>
        <History items={history} loading={loading && !history.length} onDownload={(url) => window.open(url, "_blank", "noopener,noreferrer")} />
      </section>
      <p className="mt-6 text-center text-xs text-slate-400">MVP: DOCX-to-PDF and PDF compression. Files remain on this deployment.</p>
    </main>
  );
}
