// ================= Dharma AI — frontend =================
const API = "";
let currentPersona = "guide";
let currentLanguage = "english";
let currentMode = "converse"; // converse | perspectives | daily
const LANG_BCP = { english: "en-IN" };

const chat = document.getElementById("chat");
const input = document.getElementById("input");
const composer = document.getElementById("composer");
const personasNav = document.getElementById("personas");
const micBtn = document.getElementById("micBtn");
const welcome = document.getElementById("welcome");
const languageSel = document.getElementById("language");

const bcp47 = () => LANG_BCP[currentLanguage] || "en-IN";
const escapeHtml = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// ---- persona medallion art (symbol + gradient per guide) ----
const PERSONA_ART = {
  guide:       { grad: ["#e8b04b", "#f0962e"], om: true },
  krishna:     { grad: ["#3a6ed8", "#2bb6c4"], svg: '<g fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><line x1="4" y1="19" x2="20" y2="6"/></g><g fill="#fff"><circle cx="9.5" cy="14.5" r="1"/><circle cx="12.5" cy="12" r="1"/><circle cx="15.5" cy="9.5" r="1"/></g>' },
  buddha:      { grad: ["#e8b04b", "#d9701a"], svg: '<path d="M12 2C8 7 6 12 12 22C18 12 16 7 12 2Z" fill="#fff"/>' },
  vivekananda: { grad: ["#f0962e", "#d23b1a"], svg: '<path d="M12 2c3 5 6 7 4 12a4 4 0 1 1-8 0C6 10 9 8 12 2Z" fill="#fff"/>' },
  chanakya:    { grad: ["#3f7d52", "#7d9b2f"], svg: '<g fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 19C9 12 14 7 20 4c-1 7-5 13-12 16"/><line x1="5" y1="19" x2="10" y2="14"/></g>' },
  ramana:      { grad: ["#7c4dff", "#c45c9a"], svg: '<g fill="#fff"><circle cx="12" cy="6.5" r="2.3"/><path d="M3 20 L10 10 L13.5 14.5 L16.5 10.5 L21 20 Z"/></g>' },
  shankara:    { grad: ["#2bb6a8", "#1f7a86"], svg: '<g fill="none" stroke="#fff" stroke-width="2"><circle cx="12" cy="12" r="8"/></g><circle cx="12" cy="12" r="1.8" fill="#fff"/>' },
  modern:      { grad: ["#5c7cfa", "#3b5bdb"], svg: '<g fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><line x1="12" y1="21" x2="12" y2="12"/></g><path d="M12 12c0-3.5 2.5-6 6-6 0 3.5-2.5 6-6 6Z" fill="#fff"/>' },
  child:       { grad: ["#ff9a3c", "#ff6f91"], svg: '<path d="M12 2.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16l-5.2 2.6 1-5.8-4.3-4.1 5.9-.9z" fill="#fff"/>' },
  meditation:  { grad: ["#7e57c2", "#4a3a8c"], svg: '<g fill="#fff"><circle cx="12" cy="6" r="2.4"/><path d="M4 19c0-3 3.5-5 8-5s8 2 8 5c0 1-1 1.5-3 1.5H7c-2 0-3-.5-3-1.5Z"/></g>' },
};

function medallionHTML(key) {
  const a = PERSONA_ART[key] || PERSONA_ART.guide;
  const bg = `background:linear-gradient(135deg,${a.grad[0]},${a.grad[1]})`;
  const inner = a.om
    ? '<span style="color:#fff;font-size:26px;line-height:1">ॐ</span>'
    : `<svg viewBox="0 0 24 24">${a.svg}</svg>`;
  return `<div class="persona-medallion" style="${bg}">${inner}</div>`;
}

function scrollDown() { chat.scrollTop = chat.scrollHeight; }

function renderAnswer(text) {
  const safe = escapeHtml(text);
  // Match any source tag like [BG 2.47], [Dhammapada 5], [Katha Upanishad 1.2.20]
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

// ---- personas ----
let personaMeta = {};
async function loadPersonas() {
  try {
    const list = await (await fetch(`${API}/api/personas`)).json();
    personasNav.innerHTML = "";
    list.forEach((p) => {
      personaMeta[p.key] = p;
      const card = document.createElement("button");
      card.type = "button";
      card.className = "persona-card" + (p.key === currentPersona ? " active" : "");
      card.dataset.key = p.key;
      card.innerHTML = `${medallionHTML(p.key)}<div class="persona-name">${escapeHtml(p.name)}</div><div class="persona-essence">${escapeHtml(p.blurb || "")}</div>`;
      card.onclick = () => {
        currentPersona = p.key;
        document.querySelectorAll(".persona-card").forEach((x) => x.classList.toggle("active", x.dataset.key === p.key));
      };
      personasNav.appendChild(card);
    });
  } catch (e) {
    personasNav.innerHTML = '<span style="color:#f4d089;font-size:13px;padding:8px">Could not reach the server.</span>';
  }
}

// ---- languages ----
async function loadLanguages() {
  try {
    const list = await (await fetch(`${API}/api/languages`)).json();
    languageSel.innerHTML = "";
    list.forEach((l) => {
      LANG_BCP[l.key] = l.bcp47;
      const opt = document.createElement("option");
      opt.value = l.key;
      opt.textContent = l.key === "english" ? "English" : `${l.native} · ${l.name}`;
      languageSel.appendChild(opt);
    });
    languageSel.value = currentLanguage;
    languageSel.onchange = () => { currentLanguage = languageSel.value; };
  } catch (e) { /* default English */ }
}

// ---- messaging ----
function addUser(text) {
  if (welcome) welcome.remove();
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

function sourcesBlock(citations) {
  const used = citations.filter((v) => v.used);
  const sources = used.length ? used : citations;
  if (!sources.length) return "";
  return `<div class="sources"><div class="sources-h">Sources · ${sources.length} verse${sources.length > 1 ? "s" : ""}</div>${versesHtml(sources)}</div>`;
}

function renderResponse(wrap, data) {
  const followHtml = (data.followups || []).map((f) => `<button class="followup">${escapeHtml(f)}</button>`).join("");
  wrap.innerHTML = `
    <div class="answer-card">
      <div class="answer-head">
        ${medallionHTML(data.persona || "guide")}
        <div>
          <div class="answer-persona-name">${escapeHtml(data.persona_name || "Dharma Guide")}</div>
          <div class="answer-persona-sub">grounded in the Bhagavad Gita</div>
        </div>
      </div>
      <div class="answer-text">${renderAnswer(data.answer || "")}</div>
      ${sourcesBlock(data.citations || [])}
      ${followHtml ? `<div class="followups">${followHtml}</div>` : ""}
      <div class="actions"><button class="mini-btn listen">🔊 Listen</button></div>
    </div>`;
  wireCitations(wrap);
  wrap.querySelectorAll(".followup").forEach((f) => { f.onclick = () => send(f.textContent.replace(/^↳\s*/, "")); });
  wrap.querySelector(".listen").onclick = (e) => speak(data.answer || "", e.currentTarget);
  scrollDown();
}

function renderPerspectives(wrap, data) {
  const views = (data.perspectives || []).map((p) => `
    <div class="pview">
      ${medallionHTML(p.key)}
      <div class="pview-body">
        <div class="pview-name">${escapeHtml(p.tradition)}</div>
        <div class="pview-text">${renderAnswer(p.view)}</div>
      </div>
    </div>`).join("");
  wrap.innerHTML = `
    <div class="perspectives-card">
      <div class="perspectives-q">“${escapeHtml(data.question)}”</div>
      <div class="perspectives-sub">Wisdom from many traditions</div>
      ${views}
      ${sourcesBlock(data.citations || [])}
      <div class="actions"><button class="mini-btn listen">🔊 Listen all</button></div>
    </div>`;
  wireCitations(wrap);
  const spoken = (data.perspectives || []).map((p) => `${p.tradition}. ${p.view}`).join(" ");
  wrap.querySelector(".listen").onclick = (e) => speak(spoken, e.currentTarget);
  scrollDown();
}

function renderDaily(data) {
  if (welcome) welcome.remove();
  const wrap = document.createElement("div");
  wrap.className = "msg ai";
  wrap.innerHTML = `
    <div class="daily-card">
      <div class="daily-eyebrow">${escapeHtml(data.period)} · ${escapeHtml(data.date)}</div>
      <div class="daily-verse">“${escapeHtml(data.verse.translation)}”</div>
      <a class="cite daily-verse-ref" data-ref="${escapeHtml(data.verse.ref)}">${escapeHtml(data.verse.ref)}</a>
      <div class="daily-block"><div class="daily-h">Reflection</div><p>${escapeHtml(data.reflection)}</p></div>
      <div class="daily-block"><div class="daily-h">${data.period === "morning" ? "Today's practice" : "Evening practice"}</div><p>${escapeHtml(data.practice)}</p></div>
      <div class="daily-journal">✍️ ${escapeHtml(data.journal_prompt)}</div>
      <div class="actions"><button class="mini-btn listen">🔊 Listen</button></div>
      ${sourcesBlock([data.verse])}
    </div>`;
  chat.appendChild(wrap);
  wireCitations(wrap);
  const spoken = `${data.reflection} ${data.practice}`;
  wrap.querySelector(".listen").onclick = (e) => speak(spoken, e.currentTarget);
  scrollDown();
}

async function loadDaily() {
  const wrap = addTyping();
  try {
    const res = await fetch(`${API}/api/daily?language=${currentLanguage}`);
    wrap.remove();
    renderDaily(await res.json());
  } catch (e) {
    wrap.innerHTML = `<div class="answer-card"><div class="answer-text" style="color:#b8410e">Could not load today's guidance.</div></div>`;
  }
}

async function send(question) {
  question = (question || input.value).trim();
  if (!question) return;
  input.value = ""; input.style.height = "auto";
  addUser(question);
  const wrap = addTyping();
  const perspectivesMode = currentMode === "perspectives";
  try {
    const url = perspectivesMode ? `${API}/api/perspectives` : `${API}/api/ask`;
    const body = perspectivesMode
      ? { question, language: currentLanguage }
      : { question, persona: currentPersona, language: currentLanguage };
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error("server " + res.status);
    const data = await res.json();
    if (perspectivesMode) renderPerspectives(wrap, data);
    else renderResponse(wrap, data);
  } catch (e) {
    wrap.innerHTML = `<div class="answer-card"><div class="answer-text" style="color:#b8410e">🙏 Something interrupted us: ${escapeHtml(e.message)}.</div></div>`;
  }
}

// ---- mode tabs ----
function setMode(mode) {
  currentMode = mode;
  document.querySelectorAll(".mode-tab").forEach((t) => t.classList.toggle("active", t.dataset.mode === mode));
  personasNav.style.display = mode === "converse" ? "flex" : "none";
  if (mode === "perspectives") input.placeholder = "Ask once, hear every tradition…";
  else if (mode === "converse") input.placeholder = "Ask your guide…";
  composer.style.display = mode === "daily" ? "none" : "flex";
  if (mode === "daily") loadDaily();
}
document.getElementById("modebar").addEventListener("click", (e) => {
  const tab = e.target.closest(".mode-tab");
  if (tab) setMode(tab.dataset.mode);
});

composer.addEventListener("submit", (e) => { e.preventDefault(); send(); });
input.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
input.addEventListener("input", () => { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 140) + "px"; });
document.getElementById("samples")?.addEventListener("click", (e) => { if (e.target.classList.contains("sample")) send(e.target.textContent); });

// ---- voice: speech-to-text (in the chosen language) ----
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
  micBtn.title = "Voice input needs Chrome/Safari over HTTPS"; micBtn.style.opacity = 0.4;
}

// ---- voice: text-to-speech (in the chosen language) ----
let speaking = false;
function speak(text, btn) {
  if (!("speechSynthesis" in window)) return;
  if (speaking) {
    window.speechSynthesis.cancel(); speaking = false;
    document.querySelectorAll(".listen").forEach((b) => { b.classList.remove("speaking"); b.textContent = "🔊 Listen"; });
    return;
  }
  const clean = text.replace(/\[BG\s*\d+\.\d+\]/g, "").replace(/\s{2,}/g, " ");
  const u = new SpeechSynthesisUtterance(clean);
  u.lang = bcp47();
  const voices = window.speechSynthesis.getVoices();
  const v = voices.find((x) => x.lang === u.lang) || voices.find((x) => x.lang.startsWith(u.lang.slice(0, 2)));
  if (v) u.voice = v;
  u.rate = 0.98;
  u.onend = () => { speaking = false; btn.classList.remove("speaking"); btn.textContent = "🔊 Listen"; };
  speaking = true; btn.classList.add("speaking"); btn.textContent = "⏹ Stop";
  window.speechSynthesis.speak(u);
}
if ("speechSynthesis" in window) window.speechSynthesis.onvoiceschanged = () => {};

// ---- PWA ----
let deferredPrompt = null;
const installBtn = document.getElementById("installBtn");
window.addEventListener("beforeinstallprompt", (e) => { e.preventDefault(); deferredPrompt = e; installBtn.hidden = false; });
installBtn.onclick = async () => { if (!deferredPrompt) return; deferredPrompt.prompt(); await deferredPrompt.userChoice; deferredPrompt = null; installBtn.hidden = true; };
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});

// ---- init ----
loadPersonas();
loadLanguages();
