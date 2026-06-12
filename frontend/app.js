// ================= Dharma AI — frontend v2 =================
const API = "";
let currentPersona = "krishna";
let currentLanguage = "english";
let currentMode = "converse"; // converse | perspectives | daily
let currentUser = "";
let history = [];
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
    <p>You are sitting with <b>${escapeHtml(personaName(currentPersona))}</b>.<br/>Speak or type what weighs on your heart — every answer carries its true verse.</p>
    <div class="samples" id="samples">
      <button class="sample">I feel stuck in life</button>
      <button class="sample">How do I find peace?</button>
      <button class="sample">Why do I overthink?</button>
      <button class="sample">What is my duty?</button>
    </div>
  </div>`;
}

function clearChat() {
  history = [];
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
  return sources.map((v) => `
    <div class="verse" id="src-${v.ref.replace(/[^\w]/g, "")}">
      <div class="verse-ref">${escapeHtml(v.ref)}</div>
      <div class="verse-trans">“${escapeHtml(v.translation)}”</div>
      ${v.transliteration ? `<div class="verse-sanskrit">${escapeHtml(v.transliteration)}</div>` : ""}
      <div class="verse-meta">Trans. ${escapeHtml(v.translator)} · ${escapeHtml(v.source || "Bhagavad Gita")}</div>
    </div>`).join("");
}

function wireCitations(wrap) {
  wrap.querySelectorAll(".cite").forEach((c) => {
    c.onclick = () => {
      const el = document.getElementById("src-" + c.dataset.ref.replace(/[^\w]/g, ""));
      if (el) { el.scrollIntoView({ behavior: "smooth", block: "center" }); el.classList.add("flash"); setTimeout(() => el.classList.remove("flash"), 1400); }
    };
  });
}

function sourcesBlock(citations) {
  const used = citations.filter((v) => v.used);
  const sources = used.length ? used : citations;
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
      ${sourcesBlock(data.citations || [])}
      ${followHtml ? `<div class="followups">${followHtml}</div>` : ""}
      <div class="actions"><button class="mini-btn listen">🔊 Listen</button></div>
    </div>`;
  wireCitations(wrap);
  wrap.querySelectorAll(".followup").forEach((f) => { f.onclick = () => send(f.textContent.replace(/^↳\s*/, "")); });
  wrap.querySelector(".listen").onclick = (e) => speak(data.answer || "", e.currentTarget, data.persona || "guide");
  scrollDown();
}

function renderPerspectives(wrap, data) {
  const views = (data.perspectives || []).map((p) => `
    <div class="pview">
      ${faceHTML(p.key)}
      <div class="pview-body">
        <div class="pview-name">${escapeHtml(p.tradition)}</div>
        <div class="pview-text">${renderAnswer(p.view)}</div>
      </div>
    </div>`).join("");
  wrap.innerHTML = `
    <div class="perspectives-card">
      <div class="perspectives-q">“${escapeHtml(data.question)}”</div>
      <div class="perspectives-sub">Five traditions answer, each from its own scripture</div>
      ${views}
      ${sourcesBlock(data.citations || [])}
      <div class="actions"><button class="mini-btn listen">🔊 Listen all</button></div>
    </div>`;
  wireCitations(wrap);
  const spoken = (data.perspectives || []).map((p) => `${p.tradition}. ${p.view}`).join(" ");
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
      <div class="daily-verse">“${escapeHtml(data.verse.translation)}”</div>
      <a class="cite" data-ref="${escapeHtml(data.verse.ref)}">${escapeHtml(data.verse.ref)}</a>
      <div class="daily-block"><div class="daily-h">Reflection</div><p>${escapeHtml(data.reflection)}</p></div>
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
      <div class="actions"><button class="mini-btn listen">🔊 Listen</button></div>
      ${sourcesBlock([data.verse])}
    </div>`;
  chat.appendChild(wrap);
  wireCitations(wrap);
  wrap.querySelector(".listen").onclick = (e) => speak(`${data.reflection} ${data.practice}`, e.currentTarget, "guide");
  wrap.querySelector("#journalSave").onclick = () => {
    const txt = wrap.querySelector("#journalText").value.trim();
    if (txt) saveJournal(txt, data.journal_prompt, wrap.querySelector("#journalStatus"));
  };
  scrollDown();
}

// ================= ask =================
async function send(question) {
  question = (question || input.value).trim();
  if (!question) return;
  if (!token) { showLogin(true); return; }
  input.value = ""; input.style.height = "auto";
  addUser(question);
  const wrap = addTyping();
  const perspectivesMode = currentMode === "perspectives";
  try {
    const url = perspectivesMode ? `/api/perspectives` : `/api/ask`;
    const body = perspectivesMode
      ? { question, language: currentLanguage }
      : { question, persona: currentPersona, language: currentLanguage, history: history.slice(-6) };
    const data = await apiFetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (perspectivesMode) {
      renderPerspectives(wrap, data);
    } else {
      renderResponse(wrap, data);
      history.push({ role: "user", content: question });
      history.push({ role: "assistant", content: data.answer || "" });
    }
  } catch (e) {
    wrap.innerHTML = `<div class="answer-card"><div class="answer-text" style="color:#b8410e">🙏 ${escapeHtml(e.message)}</div></div>`;
  }
}

composer.addEventListener("submit", (e) => { e.preventDefault(); send(); });
input.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
input.addEventListener("input", () => { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 130) + "px"; });
chat.addEventListener("click", (e) => { const s = e.target.closest(".sample"); if (s) send(s.textContent); });

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

// ================= voice: speech-to-text =================
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
  micBtn.title = "Voice input needs Chrome/Safari over HTTPS";
  micBtn.style.opacity = 0.4;
}

// ================= voice: talking avatar (TTS) =================
let speakingBtn = null;

function stopSpeaking() {
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  speakOverlay.hidden = true;
  if (speakingBtn) { speakingBtn.classList.remove("speaking"); speakingBtn.textContent = "🔊 Listen"; speakingBtn = null; }
}

function speak(text, btn, personaKey) {
  if (!("speechSynthesis" in window)) return;
  if (speakingBtn) { stopSpeaking(); return; }
  const clean = text.replace(/\[[^\]]*\d[^\]]*\]/g, "").replace(/\s{2,}/g, " ").trim();
  if (!clean) return;

  // open the talking-avatar view
  document.getElementById("speakFace").innerHTML = faceHTML(personaKey);
  document.getElementById("speakName").textContent = personaKey === "guide" ? "Dharma Guide" : personaName(personaKey);
  speakOverlay.hidden = false;

  const u = new SpeechSynthesisUtterance(clean);
  u.lang = bcp47();
  const voices = window.speechSynthesis.getVoices();
  const v = voices.find((x) => x.lang === u.lang) || voices.find((x) => x.lang.startsWith(u.lang.slice(0, 2)));
  if (v) u.voice = v;
  u.rate = 0.97;
  u.onend = stopSpeaking;
  u.onerror = stopSpeaking;

  speakingBtn = btn;
  btn.classList.add("speaking");
  btn.textContent = "⏹ Stop";
  window.speechSynthesis.speak(u);
}

speakOverlay.addEventListener("click", stopSpeaking);
if ("speechSynthesis" in window) window.speechSynthesis.onvoiceschanged = () => {};

// ================= PWA =================
let deferredPrompt = null;
const installBtn = document.getElementById("installBtn");
window.addEventListener("beforeinstallprompt", (e) => { e.preventDefault(); deferredPrompt = e; installBtn.hidden = false; });
installBtn.onclick = async () => { if (!deferredPrompt) return; deferredPrompt.prompt(); await deferredPrompt.userChoice; deferredPrompt = null; installBtn.hidden = true; };
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});

// ================= init =================
document.getElementById("loginFaces").innerHTML =
  faceHTML("krishna") + faceHTML("buddha") + faceHTML("vivekananda") + faceHTML("chanakya") + faceHTML("ramana");
clearChat();
initAuth();
loadPersonas();
loadLanguages();
