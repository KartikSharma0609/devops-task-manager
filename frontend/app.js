(() => {
  "use strict";
  // Same-origin: nginx serves /app/ and proxies API routes on the same host.
  const API = "";
  const STATUSES = [["pending", "Pending"], ["in_progress", "In progress"], ["completed", "Completed"]];
  const label = (s) => (STATUSES.find((x) => x[0] === s) || [s, s])[1];
  const state = { tasks: [], filter: "all", q: "", editing: null };
  const $ = (s) => document.querySelector(s);

  function el(tag, props = {}, ...kids) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(props)) {
      if (k === "class") n.className = v;
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
      else if (v !== false && v != null) n.setAttribute(k, v === true ? "" : v);
    }
    n.append(...kids);
    return n;
  }

  // ---- session (sessionStorage: cleared when the tab closes) ----
  const getToken = () => sessionStorage.getItem("token");
  function expired(t) {
    try {
      const p = JSON.parse(atob(t.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));
      return p.exp && p.exp * 1000 <= Date.now() + 5000;
    } catch { return true; }
  }
  function logout(msg) {
    sessionStorage.removeItem("token");
    state.tasks = [];
    showAuth(msg);
  }

  class ApiError extends Error { constructor(status, msg) { super(msg); this.status = status; } }

  async function api(path, { method = "GET", body, auth = true } = {}) {
    const headers = {};
    if (body) headers["Content-Type"] = "application/json";
    if (auth) {
      const t = getToken();
      if (!t || expired(t)) { logout("Your session expired. Sign in again."); throw new ApiError(401, "expired"); }
      headers.Authorization = "Bearer " + t;
    }
    let res;
    try {
      res = await fetch(API + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
    } catch { throw new ApiError(0, "Can't reach the server. Check your connection and try again."); }
    let data = null;
    try { data = await res.json(); } catch { /* non-JSON error page */ }
    if (auth && (res.status === 401 || res.status === 422)) {
      logout("Your session expired. Sign in again.");
      throw new ApiError(res.status, "expired");
    }
    if (!res.ok) {
      const m = data && (data.error || data.message || data.msg);
      throw new ApiError(res.status, m || "Something went wrong (" + res.status + "). Try again.");
    }
    return data;
  }

  // ---- ui helpers ----
  let toastTimer;
  function toast(msg, err) {
    const t = $("#toast");
    t.textContent = msg; t.className = "toast" + (err ? " err" : ""); t.hidden = false;
    clearTimeout(toastTimer); toastTimer = setTimeout(() => (t.hidden = true), 3500);
  }
  function authMsg(msg, info) {
    const m = $("#auth-msg");
    m.textContent = msg || ""; m.className = "msg" + (info ? " info" : ""); m.hidden = !msg;
  }
  function showAuth(msg) {
    $("#app").hidden = true; $("#auth").hidden = false; authMsg(msg, false);
  }
  function tab(which) {
    const login = which === "login";
    $("#login-form").hidden = !login; $("#register-form").hidden = login;
    $("#tab-login").setAttribute("aria-selected", login);
    $("#tab-register").setAttribute("aria-selected", !login);
    authMsg("");
  }
  function statusSelect(value, props = {}) {
    const opts = STATUSES.slice();
    if (!opts.some((o) => o[0] === value)) opts.push([value, value]);
    const s = el("select", props, ...opts.map(([v, l]) => el("option", { value: v, selected: v === value }, l)));
    s.value = value;
    return s;
  }
  async function guarded(btn, fn) {
    if (btn) btn.disabled = true;
    try { await fn(); } catch (e) { if (e.message !== "expired") toast(e.message, true); }
    finally { if (btn) btn.disabled = false; }
  }

  // ---- rendering ----
  function render() {
    const counts = { all: state.tasks.length };
    state.tasks.forEach((t) => (counts[t.status] = (counts[t.status] || 0) + 1));
    const f = $("#filters"); f.replaceChildren();
    [["all", "All"], ...STATUSES].forEach(([v, l]) =>
      f.append(el("button", { type: "button", "aria-pressed": state.filter === v, onclick: () => { state.filter = v; render(); } },
        `${l} ${counts[v] || 0}`)));

    const q = state.q.trim().toLowerCase();
    const shown = state.tasks
      .filter((t) => (state.filter === "all" || t.status === state.filter) && t.title.toLowerCase().includes(q))
      .sort((a, b) => b.id - a.id);
    const list = $("#list"); list.replaceChildren(...shown.map(row));
    const empty = $("#empty");
    empty.hidden = shown.length > 0;
    empty.textContent = state.tasks.length ? "No tasks match this filter." : "No tasks yet. Add your first one above.";
  }

  function row(t) {
    const li = el("li", { class: "item", "data-status": t.status });
    if (state.editing === t.id) {
      const input = el("input", { class: "title", maxlength: 100, value: t.title, "aria-label": "Task title" });
      const save = el("button", { type: "button", class: "primary" }, "Save");
      const cancel = el("button", { type: "button", onclick: () => { state.editing = null; render(); } }, "Cancel");
      const commit = () => guarded(save, async () => {
        const title = input.value.trim();
        if (!title) return toast("Title is required.", true);
        replace(await api("/tasks/" + t.id, { method: "PUT", body: { title, status: t.status } }));
        state.editing = null; render(); toast("Task updated.");
      });
      save.addEventListener("click", commit);
      input.addEventListener("keydown", (e) => { if (e.key === "Enter") commit(); if (e.key === "Escape") cancel.click(); });
      li.append(input, save, cancel);
      setTimeout(() => input.focus(), 0);
      return li;
    }
    const sel = statusSelect(t.status, { "aria-label": "Status for " + t.title });
    sel.addEventListener("change", () => guarded(sel, async () => {
      try {
        replace(await api("/tasks/" + t.id, { method: "PUT", body: { title: t.title, status: sel.value } }));
        toast("Marked " + label(sel.value).toLowerCase() + ".");
      } catch (e) { sel.value = t.status; throw e; }
      render();
    }));
    const del = el("button", { type: "button", class: "danger" }, "Delete");
    del.addEventListener("click", () => {
      if (!confirm('Delete "' + t.title + '"?')) return;
      guarded(del, async () => {
        try { await api("/tasks/" + t.id, { method: "DELETE" }); }
        catch (e) { if (e.status !== 404) throw e; }
        state.tasks = state.tasks.filter((x) => x.id !== t.id); render(); toast("Task deleted.");
      });
    });
    li.append(el("span", { class: "title" }, t.title), sel,
      el("button", { type: "button", onclick: () => { state.editing = t.id; render(); } }, "Edit"), del);
    return li;
  }
  function replace(t) { state.tasks = state.tasks.map((x) => (x.id === t.id ? t : x)); }

  // ---- flows ----
  async function login(email, password) {
    const d = await api("/auth/login", { method: "POST", auth: false, body: { email, password } }).catch((e) => {
      // the API's 401 body carries no message, so use a fixed one
      throw e.status === 401 ? new ApiError(401, "Invalid email or password.") : e;
    });
    if (!d || !d.access_token) throw new ApiError(500, "Unexpected response from the server.");
    sessionStorage.setItem("token", d.access_token);
    await openApp();
  }
  async function openApp() {
    const me = await api("/auth/me");
    $("#who").textContent = me.username;
    $("#auth").hidden = true; $("#app").hidden = false;
    state.filter = "all"; state.q = ""; state.editing = null; $("#search").value = "";
    state.tasks = await api("/tasks");
    render(); checkHealth();
  }
  async function checkHealth() {
    try {
      const r = await fetch(API + "/system/health");
      const d = await r.json();
      const ok = r.ok && d.status === "healthy";
      $("#dot").className = "dot " + (ok ? "ok" : "bad");
      $("#health").textContent = ok ? "API online" : "API reports a problem";
    } catch { $("#dot").className = "dot bad"; $("#health").textContent = "API unreachable"; }
  }

  function init() {
    const sel = $("#add-form select");
    STATUSES.forEach(([v, l]) => sel.append(el("option", { value: v }, l)));
    $("#tab-login").onclick = () => tab("login");
    $("#tab-register").onclick = () => tab("register");
    $("#logout").onclick = () => logout("You signed out.");
    $("#search").oninput = (e) => { state.q = e.target.value; render(); };

    $("#login-form").onsubmit = (e) => {
      e.preventDefault();
      const f = e.target, btn = f.querySelector("button");
      btn.disabled = true; authMsg("");
      login(f.email.value.trim(), f.password.value)
        .then(() => f.reset())
        .catch((err) => { if (err.message !== "expired") authMsg(err.message); })
        .finally(() => (btn.disabled = false));
    };
    $("#register-form").onsubmit = (e) => {
      e.preventDefault();
      const f = e.target, btn = f.querySelector("button");
      const email = f.email.value.trim(), password = f.password.value;
      btn.disabled = true; authMsg("");
      api("/auth/register", { method: "POST", auth: false, body: { username: f.username.value.trim(), email, password } })
        .then(() => login(email, password))
        .then(() => f.reset())
        .catch((err) => { if (err.message !== "expired") authMsg(err.message); })
        .finally(() => (btn.disabled = false));
    };
    $("#add-form").onsubmit = (e) => {
      e.preventDefault();
      const f = e.target;
      guarded(f.querySelector("button"), async () => {
        const title = f.title.value.trim();
        if (!title) return toast("Title is required.", true);
        state.tasks.push(await api("/tasks", { method: "POST", body: { title, status: f.status.value } }));
        f.title.value = ""; render(); toast("Task added.");
      });
    };

    const t = getToken();
    if (t && !expired(t)) openApp().catch(() => {}); else showAuth(t ? "Your session expired. Sign in again." : "");
  }
  init();
})();
