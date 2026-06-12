// ===== Dharma AI — hand-drawn SVG guide avatars (animatable: blink + talking mouth) =====
// faceHTML(key) returns a circular avatar. Add class "talking" on a parent to animate the mouth.

(function () {
  const SMILE = `<path class="mouth-smile" d="M52,80 Q60,86 68,80" stroke="#6e3420" stroke-width="2.6" fill="none" stroke-linecap="round"/>`;
  const FLAT = `<path class="mouth-smile" d="M53,81 Q60,83.5 67,81" stroke="#6e3420" stroke-width="2.6" fill="none" stroke-linecap="round"/>`;
  const OPEN = (cy = 82) => `<ellipse class="mouth-open" cx="60" cy="${cy}" rx="6.4" ry="4.6" fill="#6e3420"/>`;
  const EYES_OPEN = `<g class="eyes"><circle cx="50" cy="63" r="2.7" fill="#241a12"/><circle cx="70" cy="63" r="2.7" fill="#241a12"/><circle cx="51" cy="62" r=".8" fill="#fff"/><circle cx="71" cy="62" r=".8" fill="#fff"/></g>`;
  const EYES_CLOSED = `<g><path d="M45,63 q5,4.5 10,0" stroke="#241a12" stroke-width="2.2" fill="none" stroke-linecap="round"/><path d="M65,63 q5,4.5 10,0" stroke="#241a12" stroke-width="2.2" fill="none" stroke-linecap="round"/></g>`;
  const BROWS = (c = "#3a2a1a", w = 2.2) => `<path d="M44,56 q6,-4 12,0" stroke="${c}" stroke-width="${w}" fill="none" stroke-linecap="round"/><path d="M64,56 q6,-4 12,0" stroke="${c}" stroke-width="${w}" fill="none" stroke-linecap="round"/>`;

  function svg(id, bg1, bg2, inner) {
    return `<svg class="face-svg" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
      <defs><radialGradient id="bg-${id}" cx="50%" cy="38%" r="75%">
        <stop offset="0%" stop-color="${bg1}"/><stop offset="100%" stop-color="${bg2}"/>
      </radialGradient></defs>
      <circle cx="60" cy="60" r="60" fill="url(#bg-${id})"/>
      <circle class="aura-pulse" cx="60" cy="60" r="56" fill="none" stroke="rgba(244,208,137,.0)" stroke-width="3"/>
      ${inner}</svg>`;
  }

  const head = (skin) => `<ellipse cx="33" cy="68" rx="4.5" ry="6.5" fill="${skin}"/><ellipse cx="87" cy="68" rx="4.5" ry="6.5" fill="${skin}"/><ellipse cx="60" cy="67" rx="26" ry="28" fill="${skin}"/>`;

  const FACES = {
    krishna: svg("kr", "#3d56c9", "#222f78", `
      <ellipse cx="60" cy="49" rx="29" ry="17" fill="#1d1b3a"/>
      ${head("#7da2f0")}
      <path d="M36,53 q24,-13 48,0 l-2.5,-7 q-21.5,-11 -43,0 z" fill="#e8b04b"/>
      <path d="M60,40 q0,-9 0,-15" stroke="#1f8a70" stroke-width="2" fill="none"/>
      <circle cx="60" cy="21" r="7" fill="#1f8a70"/><circle cx="60" cy="21" r="4.4" fill="#2456b8"/><circle cx="60" cy="21" r="1.9" fill="#0e2247"/>
      <path d="M60,56 v6" stroke="#e8b04b" stroke-width="2.4" stroke-linecap="round"/>
      ${BROWS("#1d1b3a")} ${EYES_OPEN} ${SMILE} ${OPEN()}`),

    buddha: svg("bu", "#8a5a2b", "#52340f", `
      ${head("#e9bd84")}
      <ellipse cx="33" cy="72" rx="4.5" ry="9" fill="#e9bd84"/><ellipse cx="87" cy="72" rx="4.5" ry="9" fill="#e9bd84"/>
      <path d="M34,60 q0,-25 26,-25 q26,0 26,25 l-5,1 q-1,-20 -21,-20 q-20,0 -21,20 z" fill="#2f2a52"/>
      <circle cx="60" cy="33" r="6" fill="#2f2a52"/>
      <circle cx="60" cy="52" r="1.7" fill="#8a5a2b"/>
      ${BROWS("#2f2a52", 2)} ${EYES_CLOSED} ${SMILE} ${OPEN()}`),

    vivekananda: svg("vi", "#c2511f", "#7e2d0d", `
      ${head("#d9a06b")}
      <path d="M32,58 q-3,-31 28,-31 q31,0 28,31 q-13,-9 -28,-9 q-15,0 -28,9 z" fill="#ef8f2d"/>
      <path d="M39,44 q21,-13 42,0" stroke="#c96a14" stroke-width="2" fill="none"/>
      <path d="M36,52 q24,-12 48,0" stroke="#c96a14" stroke-width="2" fill="none"/>
      ${BROWS("#4a2c14", 3)} ${EYES_OPEN} ${SMILE} ${OPEN()}`),

    chanakya: svg("ch", "#3f7d52", "#1e4a2a", `
      ${head("#cfa06a")}
      <ellipse cx="60" cy="46" rx="19" ry="9" fill="#d8ab75"/>
      <path d="M73,38 q9,-8 5,-15 q-3,9 -10,11 z" fill="#241f1a"/>
      <path d="M60,46 v10" stroke="#c0392b" stroke-width="3" stroke-linecap="round"/>
      <circle cx="33" cy="73" r="2" fill="#e8b04b"/>
      <path d="M44,58 l12,1.5" stroke="#3a2a1a" stroke-width="2.4" stroke-linecap="round"/>
      <path d="M76,58 l-12,1.5" stroke="#3a2a1a" stroke-width="2.4" stroke-linecap="round"/>
      ${EYES_OPEN} ${FLAT} ${OPEN()}`),

    ramana: svg("ra", "#7c4dff", "#41327e", `
      ${head("#d8b08c")}
      <path d="M34,60 a26,23 0 0,1 52,0 l-4.5,2 a21.5,18 0 0,0 -43,0 z" fill="#eee8df"/>
      <path d="M38,78 q2,18 22,18 q20,0 22,-18 q-10,9 -22,9 q-12,0 -22,-9 z" fill="#eee8df"/>
      ${BROWS("#cfc6b8", 2.4)} ${EYES_OPEN} <path class="mouth-smile" d="M52,78 Q60,84 68,78" stroke="#6e3420" stroke-width="2.6" fill="none" stroke-linecap="round"/> ${OPEN(80)}`),

    shankara: svg("sh", "#2bb6a8", "#135a66", `
      ${head("#d8a368")}
      <path d="M36,57 a25,21 0 0,1 48,0 l-4,2 a21,17 0 0,0 -40,0 z" fill="#241f1a"/>
      <circle cx="60" cy="33" r="6" fill="#241f1a"/>
      <path d="M51,47 h18 M51,51 h18" stroke="#e9dfb8" stroke-width="2" stroke-linecap="round"/>
      ${BROWS("#241f1a", 2)} ${EYES_OPEN} ${SMILE} ${OPEN()}`),
  };

  function glyph(id, ch, bg1, bg2, fs = 52) {
    return svg(id, bg1, bg2, `
      <circle class="glyph-pulse" cx="60" cy="60" r="34" fill="rgba(255,255,255,.10)"/>
      <text x="60" y="62" text-anchor="middle" dominant-baseline="central" font-size="${fs}" fill="#fff"
        font-family="'Nirmala UI','Noto Sans Devanagari',serif">${ch}</text>`);
  }
  FACES.guide = glyph("gu", "ॐ", "#e8a93a", "#b8410e");
  FACES.modern = glyph("mo", "✦", "#5c7cfa", "#33409c", 44);

  // Realistic public-domain portraits (Wikimedia Commons, license-checked) for the
  // historical guides; glyph medallions for the abstract ones (guide, modern).
  const PHOTOS = ["krishna", "buddha", "vivekananda", "chanakya", "ramana", "shankara"];

  // Each SVG render gets UNIQUE gradient ids. Shared ids break badly: when the first
  // occurrence sits in a hidden container (the login overlay), url(#...) lookups
  // fail and every face renders black.
  let uid = 0;
  window.faceHTML = function (key, cls = "") {
    if (PHOTOS.includes(key)) {
      return `<div class="avatar photo ${cls}" data-face="${key}"><img src="/icons/face-${key}.jpg" alt="" loading="lazy"/></div>`;
    }
    const raw = FACES[key] || FACES.guide;
    const u = ++uid;
    const svg = raw.replace(/bg-[a-z]{2}/g, (m) => `${m}-${u}`);
    return `<div class="avatar ${cls}" data-face="${key}">${svg}</div>`;
  };
})();
