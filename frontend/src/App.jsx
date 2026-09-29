import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";

// Edit to match the status values your API already uses.
const STATUSES = ["pending", "in-progress", "completed"];

function AuthForm({ onLogin, notify }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    try {
      if (mode === "register") {
        await api("/auth/register", { method: "POST", body: form });
        notify("Account created. Please log in.", "ok");
        setMode("login");
      } else {
        const d = await api("/auth/login", {
          method: "POST",
          body: { email: form.email, password: form.password },
        });
        onLogin(d.access_token, d.user);
      }
    } catch (err) {
      notify(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="card auth" onSubmit={submit}>
      <h1>Task Manager</h1>
      <p className="muted">{mode === "login" ? "Sign in to your tasks" : "Create an account"}</p>
      {mode === "register" && (
        <input placeholder="Username" value={form.username} onChange={set("username")} required />
      )}
      <input type="email" placeholder="Email" value={form.email} onChange={set("email")} required />
      <input type="password" placeholder="Password" value={form.password} onChange={set("password")} required />
      <button disabled={busy}>{mode === "login" ? "Log in" : "Register"}</button>
      <button type="button" className="link" onClick={() => setMode(mode === "login" ? "register" : "login")}>
        {mode === "login" ? "Need an account? Register" : "Have an account? Log in"}
      </button>
    </form>
  );
}

function Tasks({ token, user, onLogout, notify }) {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState(STATUSES[0]);
  const [editing, setEditing] = useState(null);
  const [filter, setFilter] = useState("all");

  const call = useCallback(
    async (path, opts) => {
      try {
        return await api(path, { ...opts, token });
      } catch (err) {
        if (err.status === 401 || err.status === 422) {
          notify("Session expired. Please log in again.");
          onLogout();
        } else {
          notify(err.message);
        }
        throw err;
      }
    },
    [token, notify, onLogout]
  );

  const load = useCallback(() => call("/tasks").then(setTasks).catch(() => {}), [call]);
  useEffect(() => { load(); }, [load]);

  async function add(e) {
    e.preventDefault();
    if (!title.trim()) return;
    await call("/tasks", { method: "POST", body: { title, status } }).catch(() => {});
    setTitle("");
    load();
  }

  async function save(t) {
    await call(`/tasks/${t.id}`, { method: "PUT", body: { title: t.title, status: t.status } }).catch(() => {});
    setEditing(null);
    load();
  }

  async function remove(id) {
    if (!window.confirm("Delete this task?")) return;
    await call(`/tasks/${id}`, { method: "DELETE" }).catch(() => {});
    load();
  }

  const shown = filter === "all" ? tasks : tasks.filter((t) => t.status === filter);

  return (
    <div className="wrap">
      <header>
        <h1>My Tasks</h1>
        <div>
          <span className="muted">{user?.username}</span>
          <button className="ghost" onClick={onLogout}>Log out</button>
        </div>
      </header>

      <form className="card row" onSubmit={add}>
        <input placeholder="What needs doing?" value={title} onChange={(e) => setTitle(e.target.value)} />
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          {STATUSES.map((s) => <option key={s}>{s}</option>)}
        </select>
        <button>Add</button>
      </form>

      <div className="filters">
        {["all", ...STATUSES].map((s) => (
          <button key={s} className={filter === s ? "chip on" : "chip"} onClick={() => setFilter(s)}>
            {s} {s === "all" ? tasks.length : tasks.filter((t) => t.status === s).length}
          </button>
        ))}
      </div>

      {shown.length === 0 && <p className="muted center">No tasks here yet.</p>}
      {shown.map((t) =>
        editing?.id === t.id ? (
          <div className="card row" key={t.id}>
            <input value={editing.title} onChange={(e) => setEditing({ ...editing, title: e.target.value })} />
            <select value={editing.status} onChange={(e) => setEditing({ ...editing, status: e.target.value })}>
              {[...new Set([...STATUSES, editing.status])].map((s) => <option key={s}>{s}</option>)}
            </select>
            <button onClick={() => save(editing)}>Save</button>
            <button className="ghost" onClick={() => setEditing(null)}>Cancel</button>
          </div>
        ) : (
          <div className="card row" key={t.id}>
            <span className={t.status === "done" ? "grow done" : "grow"}>{t.title}</span>
            <span className={`badge ${t.status}`}>{t.status}</span>
            <button className="ghost" onClick={() => setEditing(t)}>Edit</button>
            <button className="ghost danger" onClick={() => remove(t.id)}>Delete</button>
          </div>
        )
      )}
    </div>
  );
}

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(JSON.parse(localStorage.getItem("user") || "null"));
  const [toast, setToast] = useState(null);

  const notify = useCallback((msg, kind = "err") => {
    setToast({ msg, kind });
    setTimeout(() => setToast(null), 4000);
  }, []);

  const login = (t, u) => {
    localStorage.setItem("token", t);
    localStorage.setItem("user", JSON.stringify(u));
    setToken(t);
    setUser(u);
  };
  const logout = useCallback(() => {
    localStorage.clear();
    setToken(null);
    setUser(null);
  }, []);

  return (
    <>
      {token ? (
        <Tasks token={token} user={user} onLogout={logout} notify={notify} />
      ) : (
        <AuthForm onLogin={login} notify={notify} />
      )}
      {toast && <div className={`toast ${toast.kind}`}>{toast.msg}</div>}
    </>
  );
}
