// ================= Dharma AI — frontend v2 =================
const API = "";
let currentPersona = "krishna";
let currentLanguage = "english";
let currentMode = "converse"; // converse | perspectives | daily
let currentUser = "";
let history = [];
let chatId = null;   // saved-conversation id (server-side)
const LANG_BCP = { english: "en-IN" };

const chat = document.getElementById("chat");
const input = document.getElementById("input");
const composer = document.getElementById("composer");
const personasNav = document.getElementById("personas");
const micBtn = document.getElementById("micBtn");
const languageSel = document.getElementById("language");
const loginOverlay = document.getElementById("loginOverlay");
const logoutBtn = document.getElementById("logoutBtn");
const speakOverlay = document.getElementById("speakOverlay");

const bcp47 = () => LANG_BCP[currentLanguage] || "en-IN";
const escapeHtml = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const scrollDown = () => { chat.scrollTop = chat.scrollHeight; };

let personaMeta = {};
const personaName = (k) => (personaMeta[k] && personaMeta[k].name) || "Dharma Guide";

// ================= auth =================
let token = localStorage.getItem("dharma_token") || "";

function showLogin(show) {
  loginOverlay.hidden = !show;
  logoutBtn.hidden = show;
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

document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errEl = document.getElementById("loginError");
  const btn = document.getElementById("loginSubmit");
  errEl.hidden = true;
  btn.disabled = true; btn.textContent = "Opening the door…";
  try {
    const res = await fetch(`${API}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: document.getElementById("loginUser").value.trim(),
        password: document.getElementById("loginPass").value,
      }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Sign-in failed");
    const data = await res.json();
    token = data.token;
    currentUser = data.username;
    localStorage.setItem("dharma_token", token);
    showLogin(false);
    clearChat();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.hidden = false;
  } finally {
    btn.disabled = false; btn.textContent = "Begin 🙏";
  }
});

logoutBtn.addEventListener("click", () => {
  token = ""; currentUser = "";
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
    showLogin(false);
    clearChat();
  } catch (e) { /* login already shown */ }
}

// ================= welcome / modes =================
function greeting() {
  const h = new Date().getHours();
  return h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
}

function welcomeHTML() {
  const who = currentUser ? `, ${currentUser}` : "";
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

// ================= conversations drawer (ChatGPT-style) =================
const drawer = document.getElementById("drawer");
const drawerBackdrop = document.getElementById("drawerBackdrop");
const drawerList = document.getElementById("drawerList");

function openDrawer() {
  if (!token) { showLogin(true); return; }
  drawer.classList.add("open");
  drawerBackdrop.hidden = false;
  renderDrawer();
}
function closeDrawer() {
  drawer.classList.remove("open");
  drawerBackdrop.hidden = true;
}

async function renderDrawer() {
  drawerList.innerHTML = `<div class="drawer-empty">…</div>`;
  try {
    const chats = await apiFetch("/api/chats");
    drawerList.innerHTML = "";
    if (!chats.length) {
      drawerList.innerHTML = `<div class="drawer-empty">No conversations yet.<br/>Ask your first question 🙏</div>`;
      return;
    }
    chats.forEach((c) => {
      const item = document.createElement("div");
      item.className = "chat-item" + (c.id === chatId ? " current" : "");
      item.innerHTML = `${faceHTML(c.persona)}<div class="chat-item-body">
          <div class="chat-item-title">${escapeHtml(c.title)}</div>
          <div class="chat-item-meta">${escapeHtml(personaName(c.persona))} · ${escapeHtml(c.updated)}</div>
        </div><button class="chat-item-del" title="Delete">🗑</button>`;
      item.querySelector(".chat-item-del").onclick = async (e) => {
        e.stopPropagation();
        await apiFetch(`/api/chats/${c.id}`, { method: "DELETE" });
        if (c.id === chatId) { clearChat(); }
        item.remove();
      };
      item.onclick = () => { closeDrawer(); loadChat(c.id); };
      drawerList.appendChild(item);
    });
  } catch (e) {
    drawerList.innerHTML = `<div class="drawer-empty">${escapeHtml(e.message)}</div>`;
  }
}

document.getElementById("histBtn").addEventListener("click", openDrawer);
document.getElementById("drawerClose").addEventListener("click", closeDrawer);
drawerBackdrop.addEventListener("click", closeDrawer);
document.getElementById("newChatBtn").addEventListener("click", () => {
  closeDrawer();
  if (currentMode !== "converse") { setMode("converse"); } else { clearChat(); }
});

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

  btn.addEventListener("click", async () => {
    if (active) {
      // Second click — stop recording
      recorder && recorder.stop();
      return;
    }
    active = true;
    chunks = [];
    btn.classList.add("listening");
    if (onStatus) onStatus("listening…");

    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (e) {
      active = false;
      btn.classList.remove("listening");
      if (onStatus) onStatus("mic access denied");
      return;
    }

    // Prefer WebM Opus (Chrome); fall back to whatever the browser supports
    const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
      ? "audio/webm;codecs=opus"
      : MediaRecorder.isTypeSupported("audio/webm")
      ? "audio/webm"
      : "";
    recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
    recorder.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
    recorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      btn.classList.remove("listening");
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
    recorder.start();
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

// Server-side audio playback — uses a plain <audio> element (reliable MP3 support).
let _currentAudio = null;  // current HTMLAudioElement
let _currentBlobUrl = null;
let _ttsFetch = null;      // AbortController for the in-flight /api/tts fetch

// Play raw MP3 bytes returned by /api/tts.
// Returns a Promise that resolves when playback ends or rejects on error.
function _playServerAudio(arrayBuffer) {
  // Clean up any previous audio element
  if (_currentAudio) {
    _currentAudio.pause();
    _currentAudio.src = "";
    _currentAudio = null;
  }
  if (_currentBlobUrl) { URL.revokeObjectURL(_currentBlobUrl); _currentBlobUrl = null; }

  const blob = new Blob([arrayBuffer], { type: "audio/mpeg" });
  _currentBlobUrl = URL.createObjectURL(blob);
  _currentAudio = new Audio(_currentBlobUrl);
  _currentAudio.volume = 1.0;

  return new Promise((resolve, reject) => {
    _currentAudio.onended = () => {
      if (_currentBlobUrl) { URL.revokeObjectURL(_currentBlobUrl); _currentBlobUrl = null; }
      _currentAudio = null;
      resolve();
    };
    _currentAudio.onerror = () => {
      if (_currentBlobUrl) { URL.revokeObjectURL(_currentBlobUrl); _currentBlobUrl = null; }
      _currentAudio = null;
      reject(new Error("audio playback error"));
    };
    _currentAudio.play().catch((err) => {
      if (_currentBlobUrl) { URL.revokeObjectURL(_currentBlobUrl); _currentBlobUrl = null; }
      _currentAudio = null;
      reject(err);
    });
  });
}

// Voices load ASYNC in browsers — getVoices() is often empty on first call.
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

// Prefer deep male Indian voices, then natural ones; match by language family.
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
    u.pitch = 0.82; // deeper, calmer — no baby voice
    activeStage = stageEl;
    stageEl.classList.add("talking");
    let spoke = false;
    u.onstart = () => { spoke = true; };
    const done = () => {
      stageEl.classList.remove("talking");
      activeStage = null;
      // Device has no voice for this language: tell the user instead of silent failure.
      if (!spoke && !v && lang.slice(0, 2) !== "en" && onnovoice) {
        onnovoice(LANG_LABEL[lang.slice(0, 2)] || lang);
      }
      if (onend) onend();
    };
    u.onend = done;
    u.onerror = done;
    window.speechSynthesis.speak(u);
    // Safety: if nothing started within 3s and no voice exists, surface the issue.
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
  convoText.textContent = "\u201c" + question + "\u201d";
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

// Conversation overlay mic — Whisper with browser SR fallback
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
    crec.onerror = () => { clistening = false; convoMic.classList.remove("listening"); convoStatus.textContent = "didn't catch that — tap the mic again"; };
  } else {
    convoMic.style.opacity = 0.4;
    convoStatus.textContent = "voice needs mic permission";
  }
}

// open conversation mode by tapping the big welcome avatar or the talk chip
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
