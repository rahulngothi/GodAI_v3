// ================= Dharma AI — frontend v3 =================
const API = "";
let currentPersona = "krishna";
let currentLanguage = "english";
let currentMode = "converse"; // converse | perspectives | daily
let currentUser = "";
let currentDisplayName = "";
let history = [];
let chatId = null;
const LANG_BCP = { english: "en-IN" };

const chat = document.getElementById("chat");
const input = document.getElementById("input");
const composer = document.getElementById("composer");
const personasNav = document.getElementById("personas");
const micBtn = document.getElementById("micBtn");
const languageSel = document.getElementById("language");
const loginOverlay = document.getElementById("loginOverlay");
const logoutBtn = document.getElementById("logoutBtn");
const profileBtn = document.getElementById("profileBtn");
const speakOverlay = document.getElementById("speakOverlay");

const bcp47 = () => LANG_BCP[currentLanguage] || "en-IN";
const escapeHtml = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const scrollDown = () => { chat.scrollTop = chat.scrollHeight; };

let personaMeta = {};
const personaName = (k) => (personaMeta[k] && personaMeta[k].name) || "Dharma Guide";

// ================= auth =================
let token = localStorage.getItem("dharma_token") || "";
let isSignupMode = false;

function showLogin(show) {
  loginOverlay.hidden = !show;
  logoutBtn.hidden = show;
  profileBtn.hidden = show;
}

async function apiFetch(path, opts = {}) {
  opts.headers = { ...(opts.headers || {}), Authorization: `Bearer ${token}` };
  const res = await fetch(`${API}${path}`, opts);
  if (res.status === 401) {
    token = ""; localStorage.removeItem("dharma_token");
    showLogin(true);
    throw new Error("Please sign in.");
  }
  if (!res.ok) {
    let msg = "Something went wrong (" + res.status + ")";
    try { const j = await res.json(); if (j.detail) msg = j.detail; } catch (e) {}
    throw new Error(msg);
  }
  return res.json();
}

// ── signup/login toggle ──
document.getElementById("toggleAuth").addEventListener("click", () => {
  isSignupMode = !isSignupMode;
  document.querySelectorAll(".signup-only").forEach((el) => {
    el.style.display = isSignupMode ? "" : "none";
  });
  document.getElementById("loginSubmit").textContent = isSignupMode ? "Create account 🙏" : "Begin 🙏";
  document.getElementById("toggleMsg").textContent = isSignupMode ? "Already have an account?" : "New here?";
  document.getElementById("toggleAuth").textContent = isSignupMode ? "Sign in" : "Create account";
  document.getElementById("loginUser").autocomplete = isSignupMode ? "username" : "username";
  document.getElementById("loginPass").autocomplete = isSignupMode ? "new-password" : "current-password";
  document.getElementById("loginError").hidden = true;
});

document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errEl = document.getElementById("loginError");
  const btn = document.getElementById("loginSubmit");
  errEl.hidden = true;
  btn.disabled = true;
  btn.textContent = isSignupMode ? "Creating account…" : "Opening the door…";

  const username = document.getElementById("loginUser").value.trim();
  const password = document.getElementById("loginPass").value;

  try {
    if (isSignupMode) {
      const confirm = document.getElementById("signupConfirm").value;
      if (password !== confirm) throw new Error("Passwords do not match.");
      const displayName = document.getElementById("signupName").value.trim();
      const res = await fetch(`${API}/api/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, display_name: displayName }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Signup failed");
      const data = await res.json();
      token = data.token;
      currentUser = data.username;
      localStorage.setItem("dharma_token", token);
    } else {
      const res = await fetch(`${API}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Sign-in failed");
      const data = await res.json();
      token = data.token;
      currentUser = data.username;
      localStorage.setItem("dharma_token", token);
    }
    showLogin(false);
    await loadProfileData();
    clearChat();
    renderDrawer();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.hidden = false;
  } finally {
    btn.disabled = false;
    btn.textContent = isSignupMode ? "Create account 🙏" : "Begin 🙏";
  }
});

logoutBtn.addEventListener("click", () => {
  token = ""; currentUser = ""; currentDisplayName = "";
  localStorage.removeItem("dharma_token");
  stopSpeaking();
  clearChat();
  showLogin(true);
});

async function initAuth() {
  if (!token) { showLogin(true); return; }
  try {
    const me = await apiFetch("/api/auth/me");
    currentUser = me.username;
    currentDisplayName = me.display_name || me.username;
    showLogin(false);
    await loadProfileData();
    clearChat();
    renderDrawer();
  } catch (e) { /* login already shown */ }
}

// ================= profile =================
const profileOverlay = document.getElementById("profileOverlay");

async function loadProfileData() {
  try {
    const p = await apiFetch("/api/profile");
    currentDisplayName = p.display_name || currentUser;
    // Sync language selector if profile has a preference.
    if (p.preferred_language && p.preferred_language !== currentLanguage) {
      currentLanguage = p.preferred_language;
      if (languageSel) languageSel.value = currentLanguage;
    }
  } catch (e) { /* quiet */ }
}

profileBtn.addEventListener("click", openProfile);
document.getElementById("profileClose").addEventListener("click", () => { profileOverlay.hidden = true; });

async function openProfile() {
  try {
    const p = await apiFetch("/api/profile");
    document.getElementById("profileName").value = p.display_name || "";
    // Populate language options into profile lang select.
    const pLang = document.getElementById("profileLang");
    pLang.innerHTML = languageSel.innerHTML;
    pLang.value = p.preferred_language || currentLanguage;
    document.getElementById("profileStyle").value = p.answer_style || "deep";
    document.getElementById("profileStatus").hidden = true;
  } catch (e) { /* show stale */ }
  profileOverlay.hidden = false;
}

document.getElementById("profileSave").addEventListener("click", async () => {
  const statusEl = document.getElementById("profileStatus");
  statusEl.hidden = true;
  const payload = {
    display_name: document.getElementById("profileName").value.trim() || undefined,
    preferred_language: document.getElementById("profileLang").value || undefined,
    answer_style: document.getElementById("profileStyle").value || undefined,
  };
  try {
    const p = await apiFetch("/api/profile", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    currentDisplayName = p.display_name || currentUser;
    if (p.preferred_language) { currentLanguage = p.preferred_language; if (languageSel) languageSel.value = currentLanguage; }
    statusEl.textContent = "Saved 🙏";
    statusEl.hidden = false;
    setTimeout(() => { profileOverlay.hidden = true; }, 1000);
  } catch (e) {
    statusEl.textContent = e.message;
    statusEl.style.color = "#ffb38a";
    statusEl.hidden = false;
  }
});

// ================= welcome / modes =================
function greeting() {
  const h = new Date().getHours();
  return h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
}

function welcomeHTML() {
  const who = currentDisplayName ? `, ${currentDisplayName}` : (currentUser ? `, ${currentUser}` : "");
  return `
  <div class="welcome" id="welcome">
    ${faceHTML(currentPersona)}
    <h2>${greeting()}${escapeHtml(who)} 🙏</h2>
    <p>You are sitting with <b>${escapeHtml(personaName(currentPersona))}</b>.<br/>Tap their face to talk, or type below — every answer carries its true verse.</p>
    <div class="samples" id="samples">
      <button class="sample talk-chip" style="background:linear-gradient(135deg,#e8b04b,#f0962e);color:#2a1800;font-weight:700;border-color:transparent">🎙️ Talk with ${escapeHtml(personaName(currentPersona))}</button>
      <button class="sample">I feel stuck in life</button>
      <button class="sample">How do I find peace?</button>
      <button class="sample">Why do I overthink?</button>
      <button class="sample">What is my duty?</button>
    </div>
  </div>`;
}

function clearChat() {
  history = [];
  chatId = null;
  setSidebarActive(null);
  stopSpeaking();
  if (currentMode === "converse") {
    chat.innerHTML = welcomeHTML();
  } else if (currentMode === "perspectives") {
    chat.innerHTML = `
      <div class="welcome" id="welcome">
        <div style="display:flex;justify-content:center;gap:6px;margin-bottom:14px">
          ${faceHTML("krishna")}${faceHTML("buddha")}${faceHTML("shankara")}${faceHTML("vivekananda")}${faceHTML("modern")}
        </div>
        <h2>One question.<br/>Five timeless answers.</h2>
        <p>Ask once — hear Krishna, Buddha, Shankaracharya, Vivekananda and a modern voice, side by side.</p>
        <div class="samples"><button class="sample">What is attachment?</button><button class="sample">Why do good people suffer?</button></div>
      </div>`;
    chat.querySelectorAll(".welcome .avatar").forEach((a) => { a.style.width = "52px"; a.style.height = "52px"; a.style.margin = "0"; a.style.boxShadow = "0 4px 14px rgba(0,0,0,.3)"; });
  } else {
    chat.innerHTML = "";
  }
}

function setMode(mode) {
  currentMode = mode;
  document.querySelectorAll(".nav-tab").forEach((t) => t.classList.toggle("active", t.dataset.mode === mode));
  personasNav.style.display = mode === "converse" ? "flex" : "none";
  composer.style.display = mode === "daily" ? "none" : "flex";
  input.placeholder = mode === "perspectives" ? "Ask once, hear every tradition…" : "Share what's on your mind…";
  clearChat();
  if (mode === "daily") loadDaily();
}
document.getElementById("modebar").addEventListener("click", (e) => {
  const tab = e.target.closest(".nav-tab");
  if (tab) setMode(tab.dataset.mode);
});
document.getElementById("clearBtn").addEventListener("click", () => { clearChat(); if (currentMode === "daily") loadDaily(); });

// ================= persistent sidebar =================
const drawer = document.getElementById("drawer");
const drawerBackdrop = document.getElementById("drawerBackdrop");
const drawerList = document.getElementById("drawerList");

const isDesktop = () => window.innerWidth >= 768;

// Restore collapse state from previous session
if (localStorage.getItem("dharma_sidebar") === "collapsed") {
  document.body.classList.add("sidebar-collapsed");
}

function collapseSidebar() {
  document.body.classList.add("sidebar-collapsed");
  localStorage.setItem("dharma_sidebar", "collapsed");
}
function expandSidebar() {
  document.body.classList.remove("sidebar-collapsed");
  localStorage.setItem("dharma_sidebar", "expanded");
  renderDrawer();
}

// histBtn: expand sidebar on desktop, open overlay on mobile
document.getElementById("histBtn").addEventListener("click", () => {
  if (!token) { showLogin(true); return; }
  if (isDesktop()) expandSidebar(); else openDrawer();
});

// Sidebar toggle button: collapse on desktop, close overlay on mobile
document.getElementById("sidebarToggle").addEventListener("click", () => {
  if (isDesktop()) collapseSidebar(); else closeDrawer();
});

// ---- mobile overlay ----
let _drawerTrigger = null;
function openDrawer() {
  if (!token) { showLogin(true); return; }
  _drawerTrigger = document.activeElement;
  drawer.classList.add("open");
  drawerBackdrop.hidden = false;
  renderDrawer();
  const first = drawer.querySelector("button:not([disabled])");
  if (first) first.focus();
}
function closeDrawer() {
  drawer.classList.remove("open");
  drawerBackdrop.hidden = true;
  if (_drawerTrigger) { _drawerTrigger.focus(); _drawerTrigger = null; }
}
drawerBackdrop.addEventListener("click", closeDrawer);

// Escape closes mobile overlay
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !isDesktop() && drawer.classList.contains("open")) closeDrawer();
});

// Focus trap inside drawer when used as mobile overlay
drawer.addEventListener("keydown", (e) => {
  if (e.key !== "Tab" || isDesktop()) return;
  const focusable = [...drawer.querySelectorAll('button:not([disabled]),[href],input,[tabindex]:not([tabindex="-1"])')];
  if (focusable.length < 2) return;
  const first = focusable[0], last = focusable[focusable.length - 1];
  if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
  else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
});

document.getElementById("newChatBtn").addEventListener("click", () => {
  if (!isDesktop()) closeDrawer();
  if (currentMode !== "converse") setMode("converse"); else clearChat();
});

// ---- date helpers ----
function _parseDate(updated) { return new Date(updated.replace(" ", "T")); }

function formatChatDate(updated) {
  const d = _parseDate(updated);
  const now = new Date();
  if (d.toDateString() === now.toDateString())
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  if (d.toDateString() === new Date(now - 864e5).toDateString()) return "Yesterday";
  return d.toLocaleDateString([], { month: "short", day: "numeric" });
}

function groupChats(chats) {
  const now = new Date();
  const todayStr = now.toDateString();
  const yestStr = new Date(now - 864e5).toDateString();
  const weekAgo = new Date(now - 7 * 864e5);
  const groups = [
    { label: "Today", items: [] },
    { label: "Yesterday", items: [] },
    { label: "Previous 7 days", items: [] },
    { label: "Older", items: [] },
  ];
  for (const c of chats) {
    const d = _parseDate(c.updated);
    if (d.toDateString() === todayStr) groups[0].items.push(c);
    else if (d.toDateString() === yestStr) groups[1].items.push(c);
    else if (d >= weekAgo) groups[2].items.push(c);
    else groups[3].items.push(c);
  }
  return groups.filter((g) => g.items.length > 0);
}

// ---- render sidebar list ----
async function renderDrawer() {
  if (!token) return;
  drawerList.innerHTML = `<div class="drawer-empty">…</div>`;
  try {
    const chats = await apiFetch("/api/chats");
    drawerList.innerHTML = "";
    if (!chats.length) {
      drawerList.innerHTML = `<div class="drawer-empty">No conversations yet.<br/>Ask your first question 🙏</div>`;
      return;
    }
    groupChats(chats).forEach(({ label, items }) => {
      const lbl = document.createElement("div");
      lbl.className = "drawer-group-label";
      lbl.textContent = label;
      drawerList.appendChild(lbl);
      items.forEach(buildChatItem);
    });
  } catch (e) {
    drawerList.innerHTML = `<div class="drawer-empty">${escapeHtml(e.message)}</div>`;
  }
}

function buildChatItem(c) {
  const item = document.createElement("div");
  item.className = "chat-item" + (c.id === chatId ? " current" : "");
  item.dataset.chatId = c.id;
  item.setAttribute("role", "listitem");
  item.innerHTML = `${faceHTML(c.persona)}
    <div class="chat-item-body">
      <div class="chat-item-title">${escapeHtml(c.title)}</div>
      ${c.preview ? `<div class="chat-item-preview">${escapeHtml(c.preview)}</div>` : ""}
      <div class="chat-item-meta">${escapeHtml(personaName(c.persona))} · ${escapeHtml(formatChatDate(c.updated))}</div>
    </div>
    <button class="chat-item-del" title="Delete" aria-label="Delete conversation">🗑</button>`;
  item.querySelector(".chat-item-del").onclick = async (e) => {
    e.stopPropagation();
    await apiFetch(`/api/chats/${c.id}`, { method: "DELETE" });
    if (c.id === chatId) clearChat();
    item.remove();
    // Clean up now-empty group labels
    drawerList.querySelectorAll(".drawer-group-label").forEach((lbl) => {
      if (!lbl.nextElementSibling || lbl.nextElementSibling.classList.contains("drawer-group-label"))
        lbl.remove();
    });
  };
  item.onclick = (e) => {
    if (e.target.closest(".chat-item-del")) return;
    if (!isDesktop()) closeDrawer();
    loadChat(c.id);
  };
  drawerList.appendChild(item);
}

// Update the active highlight without re-fetching the list
function setSidebarActive(id) {
  drawerList.querySelectorAll(".chat-item").forEach((el) => {
    el.classList.toggle("current", el.dataset.chatId === id);
  });
}

function forceConverseUI() {
  currentMode = "converse";
  document.querySelectorAll(".nav-tab").forEach((t) => t.classList.toggle("active", t.dataset.mode === "converse"));
  personasNav.style.display = "flex";
  composer.style.display = "flex";
  input.placeholder = "Share what's on your mind…";
}

async function loadChat(id) {
  try {
    forceConverseUI();
    const c = await apiFetch(`/api/chats/${id}`);
    chatId = c.id;
    setSidebarActive(chatId);
    currentPersona = c.persona || "guide";
    currentLanguage = c.language || currentLanguage;
    languageSel.value = currentLanguage;
    document.querySelectorAll(".story").forEach((x) => x.classList.toggle("active", x.dataset.key === currentPersona));
    history = [];
    chat.innerHTML = "";
    (c.turns || []).forEach((t) => {
      if (t.role === "user") {
        addUser(t.content || "");
        history.push({ role: "user", content: t.content || "" });
      } else {
        const wrap = document.createElement("div");
        wrap.className = "msg ai";
        chat.appendChild(wrap);
        renderResponse(wrap, t);
        history.push({ role: "assistant", content: t.answer || "" });
      }
    });
    scrollDown();
  } catch (e) {
    chat.innerHTML = `<div class="hist-sub">${escapeHtml(e.message)}</div>`;
  }
}


// ================= personas =================
async function loadPersonas() {
  try {
    const list = await (await fetch(`${API}/api/personas`)).json();
    personasNav.innerHTML = "";
    list.forEach((p) => {
      personaMeta[p.key] = p;
      const b = document.createElement("button");
      b.type = "button";
      b.className = "story" + (p.key === currentPersona ? " active" : "");
      b.dataset.key = p.key;
      b.title = p.blurb || "";
      b.innerHTML = `<div class="story-ring">${faceHTML(p.key)}</div><span class="story-name">${escapeHtml(p.name.replace("Swami ", "").replace("Gautama ", "").replace("Maharshi", "").trim())}</span>`;
      b.onclick = () => {
        currentPersona = p.key;
        history = [];
        document.querySelectorAll(".story").forEach((x) => x.classList.toggle("active", x.dataset.key === p.key));
        if (document.getElementById("welcome")) chat.innerHTML = welcomeHTML();
      };
      personasNav.appendChild(b);
    });
    if (document.getElementById("welcome") && currentMode === "converse") chat.innerHTML = welcomeHTML();
  } catch (e) {
    personasNav.innerHTML = '<span style="color:#f4d089;font-size:13px;padding:8px">Could not reach the server.</span>';
  }
}

// ================= languages =================
async function loadLanguages() {
  try {
    const list = await (await fetch(`${API}/api/languages`)).json();
    languageSel.innerHTML = "";
    list.forEach((l) => {
      LANG_BCP[l.key] = l.bcp47;
      const opt = document.createElement("option");
      opt.value = l.key;
      opt.textContent = l.key === "english" ? "English" : `${l.native}`;
      languageSel.appendChild(opt);
    });
    languageSel.value = currentLanguage;
    languageSel.onchange = () => { currentLanguage = languageSel.value; };
  } catch (e) { /* default English */ }
}

// ================= rendering =================
function renderAnswer(text) {
  const safe = escapeHtml(text);
  const withCites = safe.replace(/\[([A-Za-z][^\]]*?\d[^\]]*)\]/g, (_m, ref) => {
    const r = ref.trim();
    return `<a class="cite" data-ref="${r}">${r}</a>`;
  });
  return withCites.split(/\n{2,}/).map((p) => `<p>${p.replace(/\n/g, "<br>")}</p>`).join("");
}

function versesHtml(sources) {
  return sources.map((v) => {
    const teacher = v.layer === "teacher";
    const badge = teacher
      ? `<span class="layer-badge teacher">Teacher's words</span>`
      : `<span class="layer-badge scripture">Scripture</span>`;
    return `
    <div class="verse" id="src-${v.ref.replace(/[^\w]/g, "")}">
      <div class="verse-ref">${escapeHtml(v.ref)} ${badge}</div>
      <div class="verse-trans">"${escapeHtml(v.translation)}"</div>
      ${v.transliteration ? `<div class="verse-sanskrit">${escapeHtml(v.transliteration)}</div>` : ""}
      <div class="verse-meta">${teacher ? "" : "Trans. "}${escapeHtml(v.translator)} · ${escapeHtml(v.source || "Bhagavad Gita")}</div>
    </div>`;
  }).join("");
}

function wireCitations(wrap) {
  wrap.querySelectorAll(".cite").forEach((c) => {
    c.onclick = () => {
      const el = document.getElementById("src-" + c.dataset.ref.replace(/[^\w]/g, ""));
      if (el) { el.scrollIntoView({ behavior: "smooth", block: "center" }); el.classList.add("flash"); setTimeout(() => el.classList.remove("flash"), 1400); }
    };
  });
}

function sourcesBlock(citations, showAllIfNoneUsed = false) {
  const used = citations.filter((v) => v.used);
  const sources = used.length ? used : (showAllIfNoneUsed ? citations : []);
  if (!sources.length) return "";
  return `<div class="sources"><div class="sources-h">Sources · ${sources.length} verse${sources.length > 1 ? "s" : ""}</div>${versesHtml(sources)}</div>`;
}

function addUser(text) {
  document.getElementById("welcome")?.remove();
  const wrap = document.createElement("div");
  wrap.className = "msg user";
  wrap.innerHTML = `<div class="bubble-user"></div>`;
  wrap.querySelector(".bubble-user").textContent = text;
  chat.appendChild(wrap);
  scrollDown();
}

function addTyping() {
  const wrap = document.createElement("div");
  wrap.className = "msg ai";
  wrap.innerHTML = `<div class="answer-card"><div class="typing"><span></span><span></span><span></span></div></div>`;
  chat.appendChild(wrap);
  scrollDown();
  return wrap;
}

function renderResponse(wrap, data) {
  const followHtml = (data.followups || []).map((f) => `<button class="followup">${escapeHtml(f)}</button>`).join("");
  wrap.innerHTML = `
    <div class="answer-card">
      <div class="answer-head">
        ${faceHTML(data.persona || "guide")}
        <div>
          <div class="answer-persona-name">${escapeHtml(data.persona_name || "Dharma Guide")}</div>
          <div class="answer-persona-sub">grounded in scripture · tap a tag to see the verse</div>
        </div>
      </div>
      <div class="answer-text">${renderAnswer(data.answer || "")}</div>
      ${(() => {
        const src = sourcesBlock(data.citations || []);
        const note = src
          ? `<div class="ai-note">🪷 ${escapeHtml(data.persona_name || "This guide")}'s reply is an <b>AI interpretation</b>, grounded in the labeled sources above — scripture and teachers' words are quoted exactly as translated.</div>`
          : `<div class="ai-note">🪷 Spoken as an <b>AI interpretation</b> in ${escapeHtml(data.persona_name || "this guide")}'s voice. When scripture is quoted, its source appears here.</div>`;
        return src + note;
      })()}
      ${followHtml ? `<div class="followups">${followHtml}</div>` : ""}
      <div class="actions"><button class="mini-btn listen">🔊 Listen</button></div>
    </div>`;
  wireCitations(wrap);
  wrap.querySelectorAll(".followup").forEach((f) => { f.onclick = () => send(f.textContent.replace(/^↳\s*/, "")); });
  wrap.querySelector(".listen").onclick = (e) => speak(data.answer || "", e.currentTarget, data.persona || "guide");
  scrollDown();
}

function renderPerspectives(wrap, data) {
  const perspectives = data.perspectives || [];
  if (!perspectives.length) {
    wrap.innerHTML = `<div class="answer-card"><div class="answer-text" style="color:#b8410e">🙏 The council fell silent for a moment — please ask once more.</div></div>`;
    return;
  }
  const views = perspectives.map((p, i) => `
    <div class="pview">
      ${faceHTML(p.key)}
      <div class="pview-body">
        <div class="pview-name">${escapeHtml(p.tradition)} <button class="pview-listen" data-i="${i}" title="Listen">🔊</button></div>
        <div class="pview-text">${renderAnswer(p.view)}</div>
      </div>
    </div>`).join("");
  wrap.innerHTML = `
    <div class="perspectives-card">
      <div class="perspectives-q">"${escapeHtml(data.question)}"</div>
      <div class="perspectives-sub">Five traditions answer, each from its own scripture</div>
      ${views}
      ${sourcesBlock(data.citations || [], true)}
      <div class="ai-note">🪷 Each view is an <b>AI interpretation</b> in that tradition's voice, grounded only in its own labeled sources above.</div>
      <div class="actions"><button class="mini-btn listen">🔊 Listen all</button></div>
    </div>`;
  wireCitations(wrap);
  wrap.querySelectorAll(".pview-listen").forEach((b) => {
    b.onclick = () => {
      const p = perspectives[parseInt(b.dataset.i, 10)];
      speak(p.view, null, p.key);
    };
  });
  const spoken = perspectives.map((p) => `${p.tradition}. ${p.view}`).join(" ");
  wrap.querySelector(".listen").onclick = (e) => speak(spoken, e.currentTarget, "guide");
  scrollDown();
}

function renderDaily(data) {
  document.getElementById("welcome")?.remove();
  const wrap = document.createElement("div");
  wrap.className = "msg ai";
  wrap.innerHTML = `
    <div class="daily-card">
      <div class="daily-eyebrow">${escapeHtml(data.period)} · ${escapeHtml(data.date)}</div>
      <div class="daily-verse">"${escapeHtml(data.verse.translation)}"</div>
      <a class="cite" data-ref="${escapeHtml(data.verse.ref)}">${escapeHtml(data.verse.ref)}</a>
      <div class="daily-block"><div class="daily-h">Reflection <span class="layer-badge teacher" style="vertical-align:middle">AI interpretation</span></div><p>${escapeHtml(data.reflection)}</p></div>
      <div class="daily-block"><div class="daily-h">${data.period === "morning" ? "Today's practice" : "Evening practice"}</div><p>${escapeHtml(data.practice)}</p></div>
      <div class="daily-journal">✍️ ${escapeHtml(data.journal_prompt)}</div>
      <div class="journal-box">
        <textarea id="journalText" placeholder="Write your reflection here…"></textarea>
        <div class="journal-actions">
          <button class="mini-btn" id="journalSave">💾 Save to journal</button>
          <span class="journal-saved" id="journalStatus"></span>
        </div>
        <div class="journal-list" id="journalList"></div>
      </div>
      <div class="actions">
        <button class="mini-btn listen">🔊 Listen</button>
        <button class="mini-btn" id="pushBell">🔔 Daily verse alerts</button>
      </div>
      ${sourcesBlock([data.verse])}
    </div>`;
  chat.appendChild(wrap);
  wireCitations(wrap);
  wrap.querySelector(".listen").onclick = (e) => speak(`${data.reflection} ${data.practice}`, e.currentTarget, "guide");
  wrap.querySelector("#journalSave").onclick = () => {
    const txt = wrap.querySelector("#journalText").value.trim();
    if (txt) saveJournal(txt, data.journal_prompt, wrap.querySelector("#journalStatus"));
  };
  initPushBell(wrap.querySelector("#pushBell"));
  scrollDown();
}

// ---- Daily Guidance push notifications ----
function b64ToUint8(b64) {
  const pad = "=".repeat((4 - (b64.length % 4)) % 4);
  const raw = atob((b64 + pad).replace(/-/g, "+").replace(/_/g, "/"));
  return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)));
}

async function initPushBell(btn) {
  if (!btn) return;
  if (!("serviceWorker" in navigator) || !("PushManager" in window)) { btn.hidden = true; return; }
  try {
    const { publicKey, enabled } = await (await fetch(`${API}/api/push/vapid`)).json();
    if (!enabled) { btn.hidden = true; return; }
    const reg = await navigator.serviceWorker.ready;
    const existing = await reg.pushManager.getSubscription();
    const setLabel = (on) => { btn.textContent = on ? "🔕 Stop daily alerts" : "🔔 Daily verse alerts"; };
    setLabel(!!existing);
    btn.onclick = async () => {
      try {
        const cur = await reg.pushManager.getSubscription();
        if (cur) {
          await apiFetch("/api/push/unsubscribe", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ endpoint: cur.endpoint }),
          });
          await cur.unsubscribe();
          setLabel(false);
          return;
        }
        const perm = await Notification.requestPermission();
        if (perm !== "granted") { btn.textContent = "🔕 Notifications blocked"; return; }
        const sub = await reg.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: b64ToUint8(publicKey),
        });
        await apiFetch("/api/push/subscribe", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(sub.toJSON()),
        });
        setLabel(true);
      } catch (e) { btn.textContent = "🔔 " + e.message; }
    };
  } catch (e) { btn.hidden = true; }
}

// ================= ask =================

// Streaming send — used for converse mode (eliminates the 10-12s silence)
async function sendStreaming(question, wrap) {
  let streamBuf = "";
  let streamEl = null;   // element showing live tokens
  let sseRemainder = ""; // incomplete SSE line carried across chunks

  const resp = await fetch(`${API}/api/ask/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({
      question, persona: currentPersona, language: currentLanguage,
      history: history.slice(-6), chat_id: chatId,
    }),
  });

  if (resp.status === 401) {
    token = ""; localStorage.removeItem("dharma_token"); showLogin(true);
    throw new Error("Please sign in.");
  }
  if (!resp.ok) {
    let msg = "Something went wrong (" + resp.status + ")";
    try { const j = await resp.json(); if (j.detail) msg = j.detail; } catch (_) {}
    throw new Error(msg);
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    sseRemainder += decoder.decode(value, { stream: true });
    const lines = sseRemainder.split("\n");
    sseRemainder = lines.pop(); // keep incomplete line for next chunk

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      let evt;
      try { evt = JSON.parse(line.slice(6)); } catch (_) { continue; }

      if (evt.token !== undefined) {
        // First token: replace typing dots with a live streaming view
        if (!streamEl) {
          wrap.innerHTML = `<div class="answer-card"><div class="answer-text stream-live"></div></div>`;
          streamEl = wrap.querySelector(".answer-text");
        }
        streamBuf += evt.token;
        streamEl.innerHTML = renderAnswer(streamBuf);
        scrollDown();

      } else if (evt.replaced !== undefined) {
        // Post-stream correction (wrong language or moderation fix)
        streamBuf = evt.answer || streamBuf;
        if (streamEl) {
          streamEl.innerHTML = `<em style="opacity:.55;font-size:.93em">${escapeHtml(evt.replaced)}</em>`;
          setTimeout(() => {
            if (streamEl) streamEl.innerHTML = renderAnswer(streamBuf);
            scrollDown();
          }, 700);
        }

      } else if (evt.done) {
        // Final event — render the full response card (with citations, followups)
        renderResponse(wrap, evt);
        if (evt.chat_id) chatId = evt.chat_id;
        history.push({ role: "user", content: question });
        history.push({ role: "assistant", content: evt.answer || "" });
      }
    }
  }
}

async function send(question) {
  question = (question || input.value).trim();
  if (!question) return;
  if (!token) { showLogin(true); return; }
  stopSpeaking();  // cancel any audio playing when user sends a new message
  input.value = ""; input.style.height = "auto";
  addUser(question);
  const wrap = addTyping();
  const perspectivesMode = currentMode === "perspectives";
  const wasNewChat = !chatId;
  try {
    if (perspectivesMode) {
      const data = await apiFetch(`/api/perspectives`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, language: currentLanguage }),
      });
      renderPerspectives(wrap, data);
    } else {
      // Use streaming endpoint for converse mode
      await sendStreaming(question, wrap);
    }
  } catch (e) {
    wrap.innerHTML = `<div class="answer-card"><div class="answer-text" style="color:#b8410e">🙏 ${escapeHtml(e.message)}</div></div>`;
  }
}

composer.addEventListener("submit", (e) => { e.preventDefault(); send(); });
input.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
input.addEventListener("input", () => { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 130) + "px"; });
chat.addEventListener("click", (e) => {
  const s = e.target.closest(".sample");
  if (s && !s.classList.contains("talk-chip")) send(s.textContent);
});

// ================= daily / journal =================
async function loadDaily() {
  const wrap = addTyping();
  try {
    const data = await apiFetch(`/api/daily?language=${currentLanguage}`);
    wrap.remove();
    renderDaily(data);
    loadJournal();
  } catch (e) {
    wrap.innerHTML = `<div class="answer-card"><div class="answer-text" style="color:#b8410e">${escapeHtml(e.message)}</div></div>`;
  }
}

async function saveJournal(text, prompt, statusEl) {
  try {
    await apiFetch("/api/journal", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, prompt }),
    });
    statusEl.textContent = "Saved 🙏";
    loadJournal();
  } catch (e) { statusEl.textContent = e.message; }
}

async function loadJournal() {
  const listEl = document.getElementById("journalList");
  if (!listEl) return;
  try {
    const entries = await apiFetch("/api/journal");
    listEl.innerHTML = entries.length
      ? `<div class="sources-h">Your journal</div>` + entries.map((en) => `
        <div class="journal-entry">
          <div class="journal-entry-date">${escapeHtml(en.date)}</div>
          ${en.prompt ? `<div class="journal-entry-prompt">${escapeHtml(en.prompt)}</div>` : ""}
          <div class="journal-entry-text">${escapeHtml(en.text)}</div>
        </div>`).join("")
      : "";
  } catch (e) { /* quiet */ }
}

// ================= voice: speech-to-text (Whisper) =================
// Records via MediaRecorder, POSTs to /api/stt (server-side Whisper).
// Falls back to browser Web Speech API if MediaRecorder is unavailable.

function _whisperMic(btn, onResult, onStatus) {
  if (!navigator.mediaDevices || !window.MediaRecorder) return false;

  let recorder = null;
  let chunks = [];
  let active = false;
  let autoStopTimer = null;
  const origLabel = btn.textContent;

  function _stop() {
    if (autoStopTimer) { clearTimeout(autoStopTimer); autoStopTimer = null; }
    if (recorder && recorder.state !== "inactive") recorder.stop();
  }

  btn.addEventListener("click", async () => {
    if (active) { _stop(); return; }

    active = true;
    chunks = [];
    btn.classList.add("listening");
    btn.textContent = "⏹ Done";
    if (onStatus) onStatus("listening… tap Done when finished");

    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (e) {
      active = false;
      btn.classList.remove("listening");
      btn.textContent = origLabel;
      if (onStatus) onStatus("mic access denied");
      return;
    }

    const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
      ? "audio/webm;codecs=opus"
      : MediaRecorder.isTypeSupported("audio/webm")
      ? "audio/webm"
      : "";
    recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
    // collect data every 250 ms so chunks are never empty on short clips
    recorder.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
    recorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      btn.classList.remove("listening");
      btn.textContent = origLabel;
      active = false;
      if (!chunks.length) return;
      if (onStatus) onStatus("transcribing…");
      btn.disabled = true;

      try {
        const blob = new Blob(chunks, { type: recorder.mimeType || "audio/webm" });
        const form = new FormData();
        form.append("audio", blob, "audio.webm");
        form.append("language", "hi");
        const resp = await fetch(`${API}/api/stt`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: form,
        });
        if (resp.ok) {
          const data = await resp.json();
          if (data.text) onResult(data.text);
          else if (onStatus) onStatus("nothing heard — try again");
        } else {
          if (onStatus) onStatus("couldn't hear — try again");
        }
      } catch (e) {
        if (onStatus) onStatus("couldn't hear — try again");
      } finally {
        btn.disabled = false;
        if (onStatus) onStatus("");
      }
    };
    recorder.start(250);  // fire ondataavailable every 250 ms
    // Auto-stop after 15 s so the user doesn't have to remember to tap Done
    autoStopTimer = setTimeout(_stop, 15000);
  });

  return true;
}

// Main chat mic
const _mainMicReady = _whisperMic(
  micBtn,
  (text) => { input.value = text; send(text); },
  null,
);
if (!_mainMicReady) {
  // Browser STT fallback
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SR) {
    const rec = new SR();
    rec.interimResults = false;
    let listening = false;
    micBtn.onclick = () => { if (listening) { rec.stop(); return; } rec.lang = bcp47(); rec.start(); };
    rec.onstart = () => { listening = true; micBtn.classList.add("listening"); };
    rec.onend = () => { listening = false; micBtn.classList.remove("listening"); };
    rec.onresult = (ev) => { const t = ev.results[0][0].transcript; input.value = t; send(t); };
    rec.onerror = () => { listening = false; micBtn.classList.remove("listening"); };
  } else {
    micBtn.title = "Voice input needs mic permission";
    micBtn.style.opacity = 0.4;
  }
}

// ================= voice: talking avatar (TTS) =================
let speakingBtn = null;
let activeStage = null;

let _currentAudio = null;
let _currentBlobUrl = null;
let _ttsFetch = null;

function _playServerAudio(arrayBuffer) {
  if (_currentAudio) { _currentAudio.pause(); _currentAudio.src = ""; _currentAudio = null; }
  if (_currentBlobUrl) { URL.revokeObjectURL(_currentBlobUrl); _currentBlobUrl = null; }
  const blob = new Blob([arrayBuffer], { type: "audio/mpeg" });
  _currentBlobUrl = URL.createObjectURL(blob);
  _currentAudio = new Audio(_currentBlobUrl);
  _currentAudio.volume = 1.0;
  return new Promise((resolve, reject) => {
    _currentAudio.onended = () => { if (_currentBlobUrl) { URL.revokeObjectURL(_currentBlobUrl); _currentBlobUrl = null; } _currentAudio = null; resolve(); };
    _currentAudio.onerror = () => { if (_currentBlobUrl) { URL.revokeObjectURL(_currentBlobUrl); _currentBlobUrl = null; } _currentAudio = null; reject(new Error("audio playback error")); };
    _currentAudio.play().catch((err) => { if (_currentBlobUrl) { URL.revokeObjectURL(_currentBlobUrl); _currentBlobUrl = null; } _currentAudio = null; reject(err); });
  });
}


let _voicesPromise = null;
function loadVoices() {
  if (_voicesPromise) return _voicesPromise;
  _voicesPromise = new Promise((resolve) => {
    const have = window.speechSynthesis.getVoices();
    if (have.length) return resolve(have);
    window.speechSynthesis.onvoiceschanged = () => resolve(window.speechSynthesis.getVoices());
    setTimeout(() => resolve(window.speechSynthesis.getVoices()), 1500);
  });
  return _voicesPromise;
}

function pickVoice(voices, lang) {
  const two = lang.slice(0, 2);
  const pref = /(ravi|hemant|prabhat|madhur|swara|valluvar|male)/i;
  const natural = /(natural|neural|online|google)/i;
  return (
    voices.find((v) => v.lang === lang && pref.test(v.name)) ||
    voices.find((v) => v.lang.startsWith(two) && pref.test(v.name)) ||
    voices.find((v) => v.lang === lang && natural.test(v.name)) ||
    voices.find((v) => v.lang === lang) ||
    voices.find((v) => v.lang.replace("_", "-").startsWith(two))
  );
}

function cleanForSpeech(text) {
  return text.replace(/\[[^\]]*\d[^\]]*\]/g, "").replace(/\s{2,}/g, " ").trim();
}

const LANG_LABEL = { hi: "Hindi", mr: "Marathi", ta: "Tamil", te: "Telugu", kn: "Kannada", bn: "Bengali", en: "English" };

function speakRaw(text, stageEl, onend, onnovoice) {
  window.speechSynthesis.cancel();
  loadVoices().then((voices) => {
    const lang = bcp47();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang;
    const v = pickVoice(voices, lang);
    if (v) u.voice = v;
    u.rate = 0.95;
    u.pitch = 0.82;
    activeStage = stageEl;
    stageEl.classList.add("talking");
    let spoke = false;
    u.onstart = () => { spoke = true; };
    const done = () => {
      stageEl.classList.remove("talking");
      activeStage = null;
      if (!spoke && !v && lang.slice(0, 2) !== "en" && onnovoice) {
        onnovoice(LANG_LABEL[lang.slice(0, 2)] || lang);
      }
      if (onend) onend();
    };
    u.onend = done;
    u.onerror = done;
    window.speechSynthesis.speak(u);
    setTimeout(() => { if (!spoke && !v && lang.slice(0, 2) !== "en") { window.speechSynthesis.cancel(); } }, 3000);
  });
}

function stopSpeaking() {
  // Cancel any in-flight server TTS fetch
  if (_ttsFetch) { _ttsFetch.abort(); _ttsFetch = null; }
  // Stop <audio> element playback
  if (_currentAudio) { _currentAudio.pause(); _currentAudio.src = ""; _currentAudio = null; }
  if (_currentBlobUrl) { URL.revokeObjectURL(_currentBlobUrl); _currentBlobUrl = null; }
  // Stop browser speech synthesis
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  if (activeStage) { activeStage.classList.remove("talking", "loading"); activeStage = null; }
  speakOverlay.hidden = true;
  if (speakingBtn) { speakingBtn.classList.remove("speaking"); speakingBtn.textContent = "🔊 Listen"; speakingBtn = null; }
}

// speak() — primary entry point.
// 1. Tries POST /api/tts (HF indic-parler-tts — authentic Indian voice).
// 2. On 503 / network error falls back to browser Web Speech API.
// Calling speak() while already speaking stops playback (toggle).
async function speak(text, btn, personaKey) {
  if (speakingBtn || _ttsFetch) { stopSpeaking(); return; }
  const clean = cleanForSpeech(text);
  if (!clean) return;

  document.getElementById("speakFace").innerHTML = faceHTML(personaKey);
  document.getElementById("speakName").textContent = personaKey === "guide" ? "Dharma Guide" : personaName(personaKey);
  speakOverlay.hidden = false;
  const stage = document.getElementById("speakStage");
  stage.classList.add("loading");  // slow-pulse rings while fetching

  speakingBtn = btn;
  if (btn) { btn.classList.add("speaking"); btn.textContent = "⏹ Stop"; }

  // ── Try server TTS ──────────────────────────────────────────────────────
  if (token) {
    try {
      _ttsFetch = new AbortController();
      const resp = await fetch(`${API}/api/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ text: clean, language: currentLanguage }),
        signal: _ttsFetch.signal,
      });
      _ttsFetch = null;

      if (resp.ok) {
        const buf = await resp.arrayBuffer();
        stage.classList.remove("loading");
        stage.classList.add("talking");
        activeStage = stage;
        await _playServerAudio(buf);
        stopSpeaking();
        return;
      }

      if (resp.status !== 503) throw new Error(`TTS ${resp.status}`);
    } catch (e) {
      _ttsFetch = null;
      if (e.name === "AbortError") return;
      // fall through to browser
    }
  }

  // ── Browser Web Speech API fallback ────────────────────────────────────
  stage.classList.remove("loading");
  speakRaw(clean, stage, () => { stopSpeaking(); }, (langName) => {
    document.querySelector(".speak-hint").textContent = `your device has no ${langName} voice installed — reply shown as text in the chat 🙏`;
  });
}

speakOverlay.addEventListener("click", stopSpeaking);
if ("speechSynthesis" in window) window.speechSynthesis.onvoiceschanged = () => {};

// ================= conversation mode =================
const convoOverlay = document.getElementById("convoOverlay");
const convoStage = document.getElementById("convoStage");
const convoText = document.getElementById("convoText");
const convoStatus = document.getElementById("convoStatus");
const convoMic = document.getElementById("convoMic");
let convoBusy = false;

function openConvo() {
  if (!token) { showLogin(true); return; }
  document.getElementById("convoFace").innerHTML = faceHTML(currentPersona);
  document.getElementById("convoName").textContent = personaName(currentPersona);
  convoText.textContent = "";
  convoStatus.textContent = "tap the mic and speak";
  convoOverlay.hidden = false;
}

function closeConvo() {
  stopSpeaking();
  convoStage.classList.remove("talking");
  convoOverlay.classList.remove("talking");
  convoOverlay.hidden = true;
}
document.getElementById("convoClose").addEventListener("click", closeConvo);

async function convoAsk(question) {
  if (convoBusy) return;
  convoBusy = true;
  convoStatus.textContent = "listening…";
  convoText.textContent = "“" + question + "”";
  addUser(question);
  const wrap = addTyping();
  try {
    // Stream in the background; collect the final answer for TTS
    let finalAnswer = "";
    let sseRemainder = "";
    const resp = await fetch(`${API}/api/ask/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ question, persona: currentPersona, language: currentLanguage, history: history.slice(-6), chat_id: chatId }),
    });
    if (!resp.ok) throw new Error("Something went wrong (" + resp.status + ")");
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let streamEl = null;
    let streamBuf = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      sseRemainder += decoder.decode(value, { stream: true });
      const lines = sseRemainder.split("\n");
      sseRemainder = lines.pop();
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        let evt;
        try { evt = JSON.parse(line.slice(6)); } catch (_) { continue; }
        if (evt.token !== undefined) {
          if (!streamEl) {
            wrap.innerHTML = `<div class="answer-card"><div class="answer-text stream-live"></div></div>`;
            streamEl = wrap.querySelector(".answer-text");
          }
          streamBuf += evt.token;
          streamEl.innerHTML = renderAnswer(streamBuf);
          scrollDown();
        } else if (evt.replaced !== undefined) {
          streamBuf = evt.answer || streamBuf;
          if (streamEl) streamEl.innerHTML = renderAnswer(streamBuf);
        } else if (evt.done) {
          renderResponse(wrap, evt);
          if (evt.chat_id) chatId = evt.chat_id;
          history.push({ role: "user", content: question });
          history.push({ role: "assistant", content: evt.answer || "" });
          finalAnswer = evt.answer || "";
        }
      }
    }
    const spoken = cleanForSpeech(finalAnswer);
    convoText.textContent = spoken;
    convoStatus.textContent = personaName(currentPersona) + " is speaking…";
    convoOverlay.classList.add("talking");

    // Try server TTS first; fall back to browser speakRaw
    let usedServerTTS = false;
    if (token && spoken) {
      try {
        _ttsFetch = new AbortController();
        const resp = await fetch(`${API}/api/tts`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ text: spoken, language: currentLanguage }),
          signal: _ttsFetch.signal,
        });
        _ttsFetch = null;
        if (resp.ok) {
          const buf = await resp.arrayBuffer();
          await _playServerAudio(buf);
          usedServerTTS = true;
        }
      } catch (e) {
        _ttsFetch = null;
        if (e.name === "AbortError") { convoOverlay.classList.remove("talking"); convoBusy = false; return; }
      }
    }

    if (!usedServerTTS) {
      await new Promise((resolve) => {
        speakRaw(spoken, convoStage, resolve, (langName) => {
          convoStatus.dataset.novoice = "1";
          convoStatus.textContent = `⚠ your device has no ${langName} voice — read the reply below, then tap the mic`;
        });
      });
    }

    convoOverlay.classList.remove("talking");
    if (!convoStatus.dataset.novoice) convoStatus.textContent = "tap the mic to reply";
    delete convoStatus.dataset.novoice;
  } catch (e) {
    wrap.innerHTML = `<div class="answer-card"><div class="answer-text" style="color:#b8410e">🙏 ${escapeHtml(e.message)}</div></div>`;
    convoStatus.textContent = e.message;
  } finally {
    convoBusy = false;
  }
}

// Whisper mic with browser SR fallback
const _convoMicReady = _whisperMic(
  convoMic,
  (text) => { stopSpeaking(); convoOverlay.classList.remove("talking"); convoAsk(text); },
  (msg) => { convoStatus.textContent = msg; },
);
if (!_convoMicReady) {
  const SR2 = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SR2) {
    const crec = new SR2();
    crec.interimResults = false;
    let clistening = false;
    convoMic.onclick = () => {
      if (clistening) { crec.stop(); return; }
      stopSpeaking();
      convoOverlay.classList.remove("talking");
      crec.lang = bcp47();
      try { crec.start(); } catch (e) {}
    };
    crec.onstart = () => { clistening = true; convoMic.classList.add("listening"); convoStatus.textContent = "listening…"; };
    crec.onend = () => { clistening = false; convoMic.classList.remove("listening"); };
    crec.onresult = (ev) => convoAsk(ev.results[0][0].transcript);
    crec.onerror = () => { clistening = false; convoMic.classList.remove("listening"); convoStatus.textContent = "didn’t catch that — tap the mic again"; };
  } else {
    convoMic.style.opacity = 0.4;
    convoStatus.textContent = "voice needs mic permission";
  }
}

chat.addEventListener("click", (e) => {
  if (e.target.closest(".talk-chip") || e.target.closest("#welcome .avatar")) openConvo();
});

// ================= PWA =================
let deferredPrompt = null;
const installBtn = document.getElementById("installBtn");
window.addEventListener("beforeinstallprompt", (e) => { e.preventDefault(); deferredPrompt = e; installBtn.hidden = false; });
installBtn.onclick = async () => { if (!deferredPrompt) return; deferredPrompt.prompt(); await deferredPrompt.userChoice; deferredPrompt = null; installBtn.hidden = true; };
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});

// ================= audio unlock (mobile autoplay gate) =================
// Browsers require a user gesture before audio can play.
// We capture the first tap/click anywhere on the page to unlock AudioContext.
// Auto-speak then fires without needing another gesture.

// ================= init =================
document.getElementById("loginFaces").innerHTML =
  faceHTML("krishna") + faceHTML("buddha") + faceHTML("vivekananda") + faceHTML("chanakya") + faceHTML("ramana");
clearChat();
initAuth();
loadPersonas();
loadLanguages();
