// Dharma AI — frontend logic
const API = "";  // same origin
let currentPersona = "guide";

const chat = document.getElementById("chat");
const input = document.getElementById("input");
const composer = document.getElementById("composer");
const personasNav = document.getElementById("personas");
const micBtn = document.getElementById("micBtn");
const welcome = document.getElementById("welcome");

// ---------- helpers ----------
const escapeHtml = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// Turn [BG x.y] into clickable citation badges; preserve paragraphs.
function renderAnswer(text) {
  const safe = escapeHtml(text);
  const withCites = safe.replace(/\[BG\s*(\d+)\.(\d+)\]/g, (_m, c, v) =>
    `<a class="cite" data-ref="BG ${c}.${v}">BG ${c}.${v}</a>`
  );
  return withCites
    .split(/\n{2,}/)
    .map((p) => `<p>${p.replace(/\n/g, "<br>")}</p>`)
    .join("");
}

function scrollDown() {
  chat.scrollTop = chat.scrollHeight;
}

// ---------- personas ----------
async function loadPersonas() {
  try {
    const res = await fetch(`${API}/api/personas`);
    const list = await res.json();
    personasNav.innerHTML = "";
    list.forEach((p) => {
      const b = document.createElement("button");
      b.className = "persona-pill" + (p.key === currentPersona ? " active" : "");
      b.textContent = p.name;
      b.title = p.blurb;
      b.onclick = () => {
        currentPersona = p.key;
        document.querySelectorAll(".persona-pill").forEach((x) => x.classList.remove("active"));
        b.classList.add("active");
      };
      personasNav.appendChild(b);
    });
  } catch (e) {
    personasNav.innerHTML = '<span style="color:#b8410e;font-size:13px">Could not reach server.</span>';
  }
}

// ---------- messaging ----------
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

function renderResponse(wrap, data) {
  const verses = data.citations || [];
  const used = verses.filter((v) => v.used);
  const sourceList = (used.length ? used : verses);

  const versesHtml = sourceList
    .map(
      (v) => `
      <div class="verse" id="src-${v.ref.replace(/[^\\w]/g, "")}">
        <div class="verse-ref">${escapeHtml(v.ref)}</div>
        <div class="verse-trans">"${escapeHtml(v.translation)}"</div>
        ${v.transliteration ? `<div class="verse-sanskrit">${escapeHtml(v.transliteration)}</div>` : ""}
        <div class="verse-meta">Trans. ${escapeHtml(v.translator)} · Bhagavad Gita</div>
      </div>`
    )
    .join("");

  const followHtml = (data.followups || [])
    .map((f) => `<button class="followup">${escapeHtml(f)}</button>`)
    .join("");

  wrap.innerHTML = `
    <div class="answer-card">
      <span class="persona-tag">🪷 ${escapeHtml(data.persona_name || "Dharma Guide")}</span>
      <div class="answer-text">${renderAnswer(data.answer || "")}</div>
      ${sourceList.length ? `<div class="sources"><div class="sources-h">Sources · ${sourceList.length} verse${sourceList.length > 1 ? "s" : ""}</div>${versesHtml}</div>` : ""}
      ${followHtml ? `<div class="followups">${followHtml}</div>` : ""}
      <div class="row-actions">
        <button class="mini-btn listen">🔊 Listen</button>
      </div>
    </div>`;

  // citation click -> flash the source card
  wrap.querySelectorAll(".cite").forEach((c) => {
    c.onclick = () => {
      const id = "src-" + c.dataset.ref.replace(/[^\w]/g, "");
      const el = document.getElementById(id);
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.classList.add("flash");
        setTimeout(() => el.classList.remove("flash"), 1400);
      }
    };
  });

  // followups -> ask
  wrap.querySelectorAll(".followup").forEach((f) => {
    f.onclick = () => send(f.textContent);
  });

  // listen (TTS)
  const listenBtn = wrap.querySelector(".listen");
  listenBtn.onclick = () => speak(data.answer || "", listenBtn);

  scrollDown();
}

async function send(question) {
  question = (question || input.value).trim();
  if (!question) return;
  input.value = "";
  input.style.height = "auto";
  addUser(question);
  const wrap = addTyping();
  try {
    const res = await fetch(`${API}/api/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, persona: currentPersona }),
    });
    if (!res.ok) throw new Error("Server error " + res.status);
    const data = await res.json();
    renderResponse(wrap, data);
  } catch (e) {
    wrap.innerHTML = `<div class="answer-card"><div class="answer-text" style="color:#b8410e">🙏 Something went wrong: ${escapeHtml(e.message)}. Is the server running?</div></div>`;
  }
}

composer.addEventListener("submit", (e) => {
  e.preventDefault();
  send();
});

// Enter to send, Shift+Enter for newline; auto-grow
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});
input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 140) + "px";
});

// sample buttons
document.getElementById("samples")?.addEventListener("click", (e) => {
  if (e.target.tagName === "BUTTON") send(e.target.textContent);
});

// ---------- voice: speech-to-text ----------
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SR) {
  const rec = new SR();
  rec.lang = "en-IN";
  rec.interimResults = false;
  let listening = false;
  micBtn.onclick = () => {
    if (listening) { rec.stop(); return; }
    rec.start();
  };
  rec.onstart = () => { listening = true; micBtn.classList.add("listening"); };
  rec.onend = () => { listening = false; micBtn.classList.remove("listening"); };
  rec.onresult = (ev) => {
    const t = ev.results[0][0].transcript;
    input.value = t;
    send(t);
  };
  rec.onerror = () => { listening = false; micBtn.classList.remove("listening"); };
} else {
  micBtn.title = "Voice input not supported in this browser";
  micBtn.style.opacity = 0.4;
}

// ---------- voice: text-to-speech ----------
let speaking = false;
function speak(text, btn) {
  if (!("speechSynthesis" in window)) return;
  if (speaking) {
    window.speechSynthesis.cancel();
    speaking = false;
    document.querySelectorAll(".listen").forEach((b) => { b.classList.remove("speaking"); b.textContent = "🔊 Listen"; });
    return;
  }
  // strip citations + sanskrit-in-brackets for cleaner narration
  const clean = text.replace(/\[BG\s*\d+\.\d+\]/g, "").replace(/\s{2,}/g, " ");
  const u = new SpeechSynthesisUtterance(clean);
  u.lang = "en-IN";
  u.rate = 0.98;
  u.onend = () => { speaking = false; btn.classList.remove("speaking"); btn.textContent = "🔊 Listen"; };
  speaking = true;
  btn.classList.add("speaking");
  btn.textContent = "⏹ Stop";
  window.speechSynthesis.speak(u);
}

// ---------- PWA install ----------
let deferredPrompt = null;
const installBtn = document.getElementById("installBtn");
window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredPrompt = e;
  installBtn.hidden = false;
});
installBtn.onclick = async () => {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  await deferredPrompt.userChoice;
  deferredPrompt = null;
  installBtn.hidden = true;
};

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(() => {});
}

// init
loadPersonas();
