import base64
import json


def _safe_json(obj) -> str:
    # prevent user text containing "</script>" from breaking out of the embedded <script> tag
    return json.dumps(obj).replace("</", "<\\/")


def encode_logo(logo_path: str) -> str:
    with open(logo_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{data}"


_TEMPLATE = r"""
<style>
  * { box-sizing: border-box; font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; }
  #app { --bg: #0d0d0f; --fg: #e8e8ea; --panel: #16161a; --border: #2c2c30; --bubble-user: #2a2a30;
    --bubble-user-fg: #f0f0f2; --muted: #a8a8ae; --greeting: #f2f2f4; }
  #app[data-theme="light"] { --bg: #ffffff; --fg: #1c1c1f; --panel: #f2f2f3; --border: #e0e0e3;
    --bubble-user: #e8e8ec; --bubble-user-fg: #1c1c1f; --muted: #6b6b70; --greeting: #16161a; }
  html, body { margin: 0; height: 100%; background: #0d0d0f; }
  #app { position: relative; display: flex; flex-direction: column; height: 100%; width: 100%; background: var(--bg); color: var(--fg); }
  #topbar { flex: none; padding: 16px 28px; border-bottom: 1px solid var(--border); font-size: 15px; font-weight: 600; }
  #log { flex: 1; overflow-y: auto; padding: 24px clamp(16px, 8vw, 220px); display: flex; flex-direction: column; }
  #log.empty { justify-content: center; }
  #greeting { text-align: center; font-size: 26px; font-weight: 600; color: var(--greeting); }
  #promptSuggestion { margin: 18px auto 0; max-width: 460px; padding: 12px 16px; border: 1px solid var(--border);
    border-radius: 12px; background: var(--panel); color: var(--muted); font-size: 13px; line-height: 1.4;
    text-align: center; cursor: pointer; }
  #promptSuggestion:hover { color: var(--fg); border-color: #5b8cff; }
  #promptSuggestion b { color: var(--fg); font-weight: 600; }
  .row { display: flex; margin: 10px 0; }
  .row.user { justify-content: flex-end; }
  .bubble { padding: 10px 16px; border-radius: 16px; max-width: 78%; line-height: 1.45; white-space: pre-wrap; }
  .row.user .bubble { background: var(--bubble-user); color: var(--bubble-user-fg); border-bottom-right-radius: 4px; }
  .row.bot .bubble { background: transparent; color: var(--fg); padding-left: 4px; max-width: 92%; }
  #composer { display: flex; align-items: center; gap: 6px; margin: 16px clamp(16px, 8vw, 220px) 22px; padding: 6px 8px 6px 18px; background: var(--panel); border: 1px solid var(--border); border-radius: 30px; flex: none; }
  #plusBtn { width: 34px; height: 34px; border-radius: 50%; border: none; background: transparent; color: var(--muted); font-size: 19px; cursor: pointer; flex: none; }
  #plusBtn:hover { background: var(--border); color: var(--fg); }
  #userInput { flex: 1; padding: 12px 6px; border: none; background: transparent; color: var(--fg); font-size: 15px; outline: none; }
  #sendBtn { width: 38px; height: 38px; border-radius: 50%; border: none; background: #5b8cff; color: white; cursor: pointer; flex: none; font-size: 16px; }
  #sendBtn:disabled { background: #33384a; cursor: not-allowed; }
  .status-line { display: flex; align-items: center; gap: 8px; color: var(--muted); font-size: 14px; margin: 4px 0 10px 4px; }
  .spark { display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #7c8cff; animation: pulse 1s ease-in-out infinite; }
  @keyframes pulse { 0%,100% { opacity: .3; transform: scale(.8);} 50% { opacity: 1; transform: scale(1.1);} }
  .shimmer-box { width: 100%; max-width: 260px; aspect-ratio: 1080 / 1527; border-radius: 16px;
    background: linear-gradient(110deg, #19191c 8%, #29292f 18%, #19191c 33%); background-size: 250% 100%;
    animation: shimmer 1.4s linear infinite; }
  @keyframes shimmer { to { background-position-x: -250%; } }
  .poster-wrap { position: relative; display: inline-block; max-width: 260px; }
  .poster-wrap img { width: 100%; border-radius: 12px; display: block; }
  .poster-wrap #downloadBtn { position: absolute; top: 8px; right: 8px; width: 34px; height: 34px; display: flex;
    align-items: center; justify-content: center; border-radius: 50%; background: rgba(20,20,22,.85);
    color: white; text-decoration: none; font-size: 16px; opacity: 0; transition: opacity .15s; }
  .poster-wrap:hover #downloadBtn { opacity: 1; }
  #themeToggle { position: absolute; top: 64px; right: 16px; width: 36px; height: 36px; border-radius: 50%; z-index: 20;
    border: 1px solid var(--border); background: var(--panel); color: var(--fg); font-size: 15px; cursor: pointer; }
  #themeToggle:hover { filter: brightness(1.15); }
  #lightboxOverlay { position: absolute; inset: 0; background: rgba(0,0,0,.8); display: none; align-items: center; justify-content: center; z-index: 30; }
  #lightboxOverlay.open { display: flex; }
  #lightboxCard { position: relative; max-width: min(560px, 90%); max-height: 90%; }
  #lightboxCard img { max-width: 100%; max-height: 90vh; border-radius: 12px; display: block; }
  #lightboxDownload { position: absolute; top: 10px; right: 10px; width: 38px; height: 38px; display: flex;
    align-items: center; justify-content: center; border-radius: 50%; background: rgba(20,20,22,.85); color: white;
    text-decoration: none; font-size: 18px; }
  #lightboxClose { position: absolute; top: -14px; right: -14px; width: 30px; height: 30px; border-radius: 50%;
    border: none; background: #2a2a30; color: #eee; font-size: 16px; cursor: pointer; }
  #modalOverlay { position: fixed; inset: 0; background: rgba(0,0,0,.6); display: none; align-items: center; justify-content: center; z-index: 10; }
  #modalOverlay.open { display: flex; }
  #modalCard { background: #1a1a1d; border: 1px solid #333; border-radius: 14px; padding: 22px; width: 320px; color: #eee; }
  #modalCard h3 { margin: 0 0 14px; font-size: 16px; }
  #modalCard input[type=file] { color: #ccc; font-size: 13px; margin-bottom: 14px; width: 100%; }
  #logoPreview { max-width: 100%; max-height: 80px; margin-bottom: 12px; display: none; border-radius: 6px; background: #fff; padding: 4px; }
  .modal-actions { display: flex; justify-content: flex-end; gap: 8px; }
  .modal-actions button { padding: 8px 14px; border-radius: 8px; border: none; cursor: pointer; font-size: 13px; }
  #modalSave { background: #5b8cff; color: white; }
  #modalCancel { background: #33333a; color: #ddd; }
</style>
<div id="app">
  <button id="themeToggle" title="Toggle theme">&#127769;</button>
  <div id="topbar">Property Post Maker</div>
  <div id="log" class="empty">
    <div id="greeting">Describe the property you want to advertise</div>
    <div id="promptSuggestion">Try: <b>"4 BHK, 2 stories corner villa at Golf Green Street with pool, gym, indoor-outdoor games, banquet hall and a garden, price 2.3 Cr onwards"</b></div>
  </div>
  <div id="modalOverlay">
    <div id="modalCard">
      <h3>Custom logo</h3>
      <img id="logoPreview" />
      <input id="logoFile" type="file" accept="image/*" />
      <div class="modal-actions">
        <button id="modalCancel">Cancel</button>
        <button id="modalSave">Save</button>
      </div>
    </div>
  </div>
  <div id="lightboxOverlay">
    <div id="lightboxCard">
      <button id="lightboxClose">&times;</button>
      <img id="lightboxImg" />
      <a id="lightboxDownload" title="Download">&#8681;</a>
    </div>
  </div>
  <div id="composer">
    <button id="plusBtn" title="Add custom logo">+</button>
    <input id="userInput" type="text" placeholder="Describe the property..." />
    <button id="sendBtn">&#8593;</button>
  </div>
</div>
<script>
const BRAND = __BRAND_JSON__;
const GROQ = __GROQ_JSON__;
const DEFAULT_LOGO = __LOGO_DATA_URI__;
let customLogoDataUri = null;

const appEl = document.getElementById('app');
const logEl = document.getElementById('log');
const inputEl = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const plusBtn = document.getElementById('plusBtn');
const modal = document.getElementById('modalOverlay');
const logoFile = document.getElementById('logoFile');
const logoPreview = document.getElementById('logoPreview');
const lightbox = document.getElementById('lightboxOverlay');

function openLightbox(dataUrl, filename) {
  document.getElementById('lightboxImg').src = dataUrl;
  const dl = document.getElementById('lightboxDownload');
  dl.href = dataUrl;
  dl.download = filename;
  lightbox.classList.add('open');
}
document.getElementById('lightboxClose').addEventListener('click', () => lightbox.classList.remove('open'));
lightbox.addEventListener('click', (e) => { if (e.target === lightbox) lightbox.classList.remove('open'); });

let stage = 'collecting'; // collecting -> theme -> color -> generating -> done
let collectedText = '';
let fields = { property_type: null, location: null, price: null, highlights: null };
let resolvedTheme = null;
let resolvedColor = null;

// Size this iframe to the actual visible viewport instead of a fixed Python-side
// height, so the page never scrolls regardless of screen size/zoom.
function fitFrame() {
  try {
    const fe = window.frameElement;
    if (!fe) return;
    const top = fe.getBoundingClientRect().top;
    fe.style.height = Math.max(480, window.parent.innerHeight - top) + 'px';
  } catch (e) { /* cross-origin fallback: keep Python-supplied height */ }
}
fitFrame();
window.addEventListener('resize', fitFrame);
try { window.parent.addEventListener('resize', fitFrame); } catch (e) {}

const themeToggle = document.getElementById('themeToggle');
function applyTheme(theme) {
  if (theme === 'light') { appEl.dataset.theme = 'light'; themeToggle.innerHTML = '&#9728;'; }
  else { delete appEl.dataset.theme; themeToggle.innerHTML = '&#127769;'; }
}
themeToggle.addEventListener('click', () => {
  const next = appEl.dataset.theme === 'light' ? 'dark' : 'light';
  applyTheme(next);
  try { localStorage.setItem('ppm-theme', next); } catch (e) {}
});
try { applyTheme(localStorage.getItem('ppm-theme') || 'dark'); } catch (e) { applyTheme('dark'); }

const SUGGESTION_TEXT = '4 BHK, 2 stories corner villa at Golf Green Street with pool, gym, indoor-outdoor games, banquet hall and a garden, price 2.3 Cr onwards';
document.getElementById('promptSuggestion').addEventListener('click', () => {
  inputEl.value = SUGGESTION_TEXT;
  inputEl.focus();
});

function scrollBottom() { logEl.scrollTop = logEl.scrollHeight; }

function clearGreeting() {
  if (logEl.classList.contains('empty')) {
    logEl.classList.remove('empty');
    logEl.innerHTML = '';
  }
}

function addBubble(text, who) {
  clearGreeting();
  const row = document.createElement('div');
  row.className = 'row ' + who;
  const b = document.createElement('div');
  b.className = 'bubble';
  b.textContent = text;
  row.appendChild(b);
  logEl.appendChild(row);
  scrollBottom();
  return b;
}

function addStatusLine(text) {
  const row = document.createElement('div');
  row.className = 'status-line';
  row.innerHTML = '<span class="spark"></span><span class="label"></span>';
  row.querySelector('.label').textContent = text;
  logEl.appendChild(row);
  scrollBottom();
  return row;
}

function addShimmer() {
  const row = document.createElement('div');
  row.className = 'row bot';
  const wrap = document.createElement('div');
  wrap.className = 'shimmer-box';
  row.appendChild(wrap);
  logEl.appendChild(row);
  scrollBottom();
  return row;
}

plusBtn.addEventListener('click', () => { modal.classList.add('open'); });
document.getElementById('modalCancel').addEventListener('click', () => { modal.classList.remove('open'); });
logoFile.addEventListener('change', () => {
  const f = logoFile.files[0];
  if (!f) return;
  const reader = new FileReader();
  reader.onload = () => { logoPreview.src = reader.result; logoPreview.style.display = 'block'; };
  reader.readAsDataURL(f);
});
document.getElementById('modalSave').addEventListener('click', () => {
  const f = logoFile.files[0];
  if (f) {
    const reader = new FileReader();
    reader.onload = () => {
      customLogoDataUri = reader.result;
      modal.classList.remove('open');
      addBubble('Custom logo added — it will be used on the poster.', 'bot');
    };
    reader.readAsDataURL(f);
  } else {
    modal.classList.remove('open');
  }
});

function stripFences(s) {
  return s.replace(/```json/gi, '').replace(/```/g, '').trim();
}

// Text runs on Groq (openai/gpt-oss-120b), not Puter: Puter's anonymous chat
// quota runs out with regular use same as its image credits did, and
// Pollinations' text API blocks programmatic calls (Cloudflare bot-check).
// Groq's free tier needs a real API key with no per-user login, and its API
// allows direct browser CORS calls - confirmed by testing directly.
async function askJSON(prompt) {
  let text;
  try {
    const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + GROQ.api_key },
      body: JSON.stringify({ model: GROQ.model, messages: [{ role: 'user', content: prompt }] }),
    });
    if (!r.ok) return null;
    const j = await r.json();
    text = j.choices && j.choices[0] && j.choices[0].message && j.choices[0].message.content;
  } catch (e) {
    return null;
  }
  if (!text) return null;
  try {
    return JSON.parse(stripFences(text));
  } catch (e) {
    return null;
  }
}

sendBtn.addEventListener('click', handleSend);
inputEl.addEventListener('keydown', (e) => { if (e.key === 'Enter') handleSend(); });

async function handleSend() {
  const text = inputEl.value.trim();
  if (!text) return;
  addBubble(text, 'user');
  inputEl.value = '';
  sendBtn.disabled = true;
  try {
    if (stage === 'collecting') {
      await handleCollecting(text);
    } else if (stage === 'theme') {
      await handleThemeAnswer(text);
    } else if (stage === 'color') {
      await handleColorAnswer(text);
    } else if (stage === 'done') {
      await handleRefinement(text);
    }
  } finally {
    sendBtn.disabled = false;
  }
}

async function handleCollecting(text) {
  collectedText += (collectedText ? '\n' : '') + text;
  const status = addStatusLine('Reading your description...');
  const parsed = await askJSON(
    'Extract property-listing fields from this user description for an ad-generation tool. Full text so far:\n<<<\n' +
    collectedText.replace(/<<<|>>>/g, "'") + '\n>>>\n' +
    'If Location is not clearly stated anywhere, INVENT a plausible, realistic-sounding neighborhood + city yourself — never leave it null and never list it as missing. ' +
    'Property type, price, and highlights must come from the user; only list a field in "missing" if it is genuinely absent from the text. ' +
    'Reply with ONLY strict JSON, no prose, no markdown fences: {"property_type": string or null, "location": string, "price": string or null, "highlights": string or null, "missing": array of any of "property_type","price","highlights"}'
  );
  status.remove();
  if (!parsed) {
    addBubble("Sorry, I couldn't quite parse that — could you describe the property again?", 'bot');
    return;
  }
  fields.property_type = parsed.property_type || fields.property_type;
  fields.location = parsed.location || fields.location;
  fields.price = parsed.price || fields.price;
  fields.highlights = parsed.highlights || fields.highlights;
  const missing = Array.isArray(parsed.missing) ? parsed.missing : [];
  if (missing.length > 0) {
    const names = { property_type: 'the property type', price: 'the price', highlights: 'a few highlights' };
    const ask = missing.map((m) => names[m] || m).join(' and ');
    addBubble('Got it so far. Could you also tell me ' + ask + '?', 'bot');
    return;
  }
  addBubble('Perfect. Should the post use a Day or Night theme?', 'bot');
  stage = 'theme';
}

async function handleThemeAnswer(text, retried) {
  const status = addStatusLine('Thinking...');
  const parsed = await askJSON(
    'The user was asked whether they want a "day" or "night" theme for a property ad. ' +
    'Their reply was: "' + text.replace(/"/g, "'") + '". ' +
    'Reply with ONLY strict JSON, no prose, no markdown fences: {"theme":"day"} or {"theme":"night"} or {"theme":"unclear"}.'
  );
  status.remove();
  if (parsed && (parsed.theme === 'day' || parsed.theme === 'night')) {
    resolvedTheme = parsed.theme;
    addBubble('Got it — ' + resolvedTheme + ' theme. What color scheme should the ad use?', 'bot');
    stage = 'color';
  } else if (!retried) {
    addBubble('Sorry, I did not catch that — Day or Night?', 'bot');
  } else {
    resolvedTheme = 'day';
    addBubble("I'll default to Day theme. What color scheme should the ad use?", 'bot');
    stage = 'color';
  }
}

async function handleColorAnswer(text, retried) {
  const status = addStatusLine('Thinking...');
  const parsed = await askJSON(
    'The user was asked what color scheme to use for a property ad. Their reply was: "' + text.replace(/"/g, "'") + '". ' +
    'Resolve this to a single representative CSS hex color and a short label. ' +
    'Reply with ONLY strict JSON, no prose, no markdown fences: {"hex":"#RRGGBB","label":"Lime Green","resolved":true} ' +
    'or {"resolved":false} if you truly cannot determine a color.'
  );
  status.remove();
  if (parsed && parsed.resolved && /^#[0-9a-fA-F]{6}$/.test(parsed.hex)) {
    resolvedColor = parsed;
    stage = 'generating';
    addBubble('Great — ' + parsed.label + '. Generating your post now...', 'bot');
    generatePost();
  } else if (!retried) {
    addBubble('Sorry, what color or color scheme would you like?', 'bot');
  } else {
    resolvedColor = { hex: '#2563eb', label: 'Blue' };
    stage = 'generating';
    addBubble("I'll default to Blue. Generating your post now...", 'bot');
    generatePost();
  }
}

function wrapText(ctx, text, maxWidth) {
  const words = String(text).split(/\s+/);
  const lines = [];
  let line = '';
  for (const w of words) {
    const test = line ? line + ' ' + w : w;
    if (ctx.measureText(test).width > maxWidth && line) {
      lines.push(line);
      line = w;
    } else {
      line = test;
    }
  }
  if (line) lines.push(line);
  return lines;
}

function drawCover(ctx, img, dx, dy, dw, dh) {
  const iw = img.naturalWidth || img.width, ih = img.naturalHeight || img.height;
  const ir = iw / ih, dr = dw / dh;
  let sx, sy, sw, sh;
  if (ir > dr) { sh = ih; sw = ih * dr; sx = (iw - sw) / 2; sy = 0; }
  else { sw = iw; sh = iw / dr; sx = 0; sy = (ih - sh) / 2; }
  ctx.drawImage(img, sx, sy, sw, sh, dx, dy, dw, dh);
}

function pickIcon(title) {
  const t = title.toLowerCase();
  if (/locat|address|street|corner|prime/.test(t)) return '\u{1F4CD}';
  if (/pool|gym|wellness|fitness|lifestyle/.test(t)) return '\u{1F3CA}';
  if (/communit|invest|value|banquet|hall/.test(t)) return '\u{1F3D9}';
  return '\u{2B50}';
}

async function loadImgEl(imgOrUrl) {
  if (imgOrUrl instanceof HTMLImageElement) {
    if (imgOrUrl.complete) return imgOrUrl;
    await new Promise((res) => { imgOrUrl.onload = res; imgOrUrl.onerror = res; });
    return imgOrUrl;
  }
  const im = new Image();
  im.crossOrigin = 'anonymous';
  im.src = imgOrUrl;
  await new Promise((res) => { im.onload = res; im.onerror = res; });
  return im;
}

let lastPlan = null;
let lastImages = null; // { hero, t1, t2, t3 } loaded <img> elements, keyed to lastPlan's prompts

const PLAN_SHAPE = '{"badge_text":"LUXURY CORNER VILLA FOR SALE","headline":"short punchy headline, 3-5 words","price_line":"STARTING FROM","price_value":"the price as given","spec_line":"short spec summary e.g. 4 BHK | 2 STORIES | STREET NAME","about_paragraph":"2-3 sentence description using the highlights","benefits":[{"title":"RESORT AMENITIES","desc":"short real description"},{"title":"HOST & CELEBRATE","desc":"short real description"},{"title":"PRIME LOCATION","desc":"short real description"}],' +
  '"hero_prompt":"a photorealistic real estate exterior photo prompt for an AI image generator, incorporating the property description, THEME lighting, and a subtle COLOR accent, no text or logos in the image","thumb_prompts":["photorealistic interior/amenity photo prompt 1 derived from the highlights, THEME lighting, no text","photorealistic interior/amenity photo prompt 2, no text","photorealistic interior/amenity photo prompt 3, no text"]}';

// Images: Pollinations.ai's Flux endpoint, free/unlimited/no-login, no Puter
// involved. A prior attempt via puter.net.fetch (to work around Pollinations
// blocking programmatic fetch/XHR reads) hit an unrelated Puter relay outage;
// this fetches Pollinations directly instead. Automated/headless browser
// testing trips Pollinations' bot-check on this fetch - a real interactive
// browser session generally shouldn't.
function pollinationsUrl(prompt, w, h) {
  const seed = Math.floor(Math.random() * 1e9);
  return 'https://image.pollinations.ai/prompt/' + encodeURIComponent(prompt) +
    '?width=' + w + '&height=' + h + '&model=flux&nologo=true&seed=' + seed;
}

function withTimeout(promise, ms) {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error('timed out after ' + ms + 'ms')), ms);
    promise.then((v) => { clearTimeout(t); resolve(v); }, (e) => { clearTimeout(t); reject(e); });
  });
}

async function fetchPollinationsImg(url) {
  const resp = await withTimeout(fetch(url), 25000);
  if (!resp.ok) return null;
  const blob = await resp.blob();
  const img = await loadImgEl(URL.createObjectURL(blob));
  return img.naturalWidth ? img : null;
}

async function genImage(prompt, label, setCaption, w, h) {
  setCaption(label);
  const url = pollinationsUrl(prompt, w, h);
  let img = null;
  try { img = await fetchPollinationsImg(url); } catch (e) { /* retry below */ }
  if (!img) {
    await new Promise((r) => setTimeout(r, 3000));
    try { img = await fetchPollinationsImg(pollinationsUrl(prompt, w, h)); } catch (e) { /* fall through */ }
  }
  if (!img) throw new Error('Photo generation failed (image service unavailable)');
  return img;
}

// Regenerates only the photos whose prompt actually changed vs. the previous plan
// (e.g. a copy-only tweak like "shorten the headline" needs no new photos at all);
// prevPlan/prevImages null forces generating all four, as on the first pass.
async function getImagesForPlan(plan, prevPlan, prevImages, setCaption) {
  const slots = [
    ['hero', plan.hero_prompt, 'Generating hero photo...', 900, 700],
    ['t1', plan.thumb_prompts[0], 'Generating photo 1 of 3...', 700, 700],
    ['t2', plan.thumb_prompts[1], 'Generating photo 2 of 3...', 700, 700],
    ['t3', plan.thumb_prompts[2], 'Generating photo 3 of 3...', 700, 700],
  ];
  const result = {};
  for (const [key, prompt, label, w, h] of slots) {
    const prevPrompt = prevPlan && key === 'hero' ? prevPlan.hero_prompt
      : prevPlan && key === 't1' ? prevPlan.thumb_prompts[0]
      : prevPlan && key === 't2' ? prevPlan.thumb_prompts[1]
      : prevPlan && key === 't3' ? prevPlan.thumb_prompts[2]
      : null;
    if (prevPlan && prevImages && prevPrompt === prompt) {
      result[key] = prevImages[key];
    } else {
      // sequential, not parallel: anonymous Pollinations requests are rate-limited to ~1 per 15s
      result[key] = await genImage(prompt, label, setCaption, w, h);
    }
  }
  return result;
}

function appendPosterMessage(dataUrl) {
  const row = document.createElement('div');
  row.className = 'row bot';
  const wrap = document.createElement('div');
  wrap.className = 'poster-wrap';
  const img = document.createElement('img');
  img.src = dataUrl;
  img.style.cursor = 'zoom-in';
  wrap.appendChild(img);
  const a = document.createElement('a');
  a.id = 'downloadBtn';
  a.href = dataUrl;
  a.download = (fields.property_type || 'property-post').replace(/[^a-z0-9]+/gi, '-').toLowerCase() + '.png';
  a.title = 'Download';
  a.innerHTML = '&#8681;';
  wrap.appendChild(a);
  wrap.addEventListener('click', (e) => { if (e.target !== a) openLightbox(dataUrl, a.download); });
  row.appendChild(wrap);
  logEl.appendChild(row);
  scrollBottom();
}

async function generatePost() {
  const shimmerRow = addShimmer();
  const captionRow = document.createElement('div');
  captionRow.className = 'status-line';
  captionRow.innerHTML = '<span class="spark"></span><span class="label"></span>';
  logEl.insertBefore(captionRow, shimmerRow);
  const setCaption = (t) => { captionRow.querySelector('.label').textContent = t; };
  scrollBottom();
  try {
    setCaption('Analyzing flyer layout...');
    const plan = await askJSON(
      'You are writing copy for a real-estate property advertisement poster. Given:\n' +
      'Property & Type: ' + fields.property_type + '\n' +
      'Location: ' + fields.location + '\n' +
      'Price: ' + fields.price + '\n' +
      'Highlights: ' + fields.highlights + '\n' +
      'Theme: ' + resolvedTheme + ' (lighting mood)\n' +
      'Color accent: ' + resolvedColor.label + ' (' + resolvedColor.hex + ')\n\n' +
      'Reply with ONLY strict JSON, no prose, no markdown fences, matching exactly this shape (these are illustrative EXAMPLE values for a different property - replace every value with real content derived from the actual inputs above, never copy the examples or leave literal placeholder text like ellipses):\n' +
      PLAN_SHAPE.replace(/THEME/g, resolvedTheme).replace(/COLOR/g, resolvedColor.label)
    );
    if (!plan) { throw new Error('Could not plan content.'); }

    const images = await getImagesForPlan(plan, null, null, setCaption);
    setCaption('Composing poster...');
    const dataUrl = await renderPoster(plan, [images.hero, images.t1, images.t2, images.t3]);

    captionRow.remove();
    shimmerRow.remove();
    appendPosterMessage(dataUrl);
    lastPlan = plan;
    lastImages = images;
    stage = 'done';
    inputEl.placeholder = 'Suggest a change to refine it...';
  } catch (err) {
    captionRow.remove();
    shimmerRow.remove();
    const detail = (err && err.message) || (err && err.error) || (typeof err === 'string' ? err : JSON.stringify(err)) || 'unknown error';
    addBubble('Something went wrong generating your post: ' + detail + '. Please reload and try again.', 'bot');
  }
}

async function handleRefinement(text) {
  const status = addStatusLine('Applying your changes...');
  try {
    const plan = await askJSON(
      'You already produced this property-ad poster plan (strict JSON): ' + JSON.stringify(lastPlan) + '\n' +
      'Current theme: ' + resolvedTheme + '. Current color accent: ' + resolvedColor.label + ' (' + resolvedColor.hex + ').\n' +
      'The user has now requested this change: "' + text.replace(/"/g, "'") + '"\n' +
      'Produce an UPDATED plan reflecting ONLY the requested change(s) - keep every other field exactly as it was unless the change requires it to differ. ' +
      'If the request changes the theme or color, include updated "theme" ("day" or "night") and "color_hex"/"color_label" fields; omit them if unchanged. ' +
      'Only rewrite hero_prompt/thumb_prompts if the requested change actually affects what the photos should show (e.g. a lighting/color/scene change) - leave them byte-identical to the previous plan if the change is copy-only (e.g. wording, price, headline).\n' +
      'Reply with ONLY strict JSON, no prose, no markdown fences, matching this shape:\n' + PLAN_SHAPE.replace(/THEME/g, resolvedTheme).replace(/COLOR/g, resolvedColor.label)
    );
    if (!plan) { throw new Error('Could not apply that change.'); }
    if (plan.theme === 'day' || plan.theme === 'night') resolvedTheme = plan.theme;
    if (plan.color_hex && /^#[0-9a-fA-F]{6}$/.test(plan.color_hex)) {
      resolvedColor = { hex: plan.color_hex, label: plan.color_label || resolvedColor.label };
    }

    const setCaption = (t) => { status.querySelector('.label').textContent = t; };
    const images = await getImagesForPlan(plan, lastPlan, lastImages, setCaption);
    setCaption('Composing poster...');
    const dataUrl = await renderPoster(plan, [images.hero, images.t1, images.t2, images.t3]);

    status.remove();
    addBubble("Here's the updated version:", 'bot');
    appendPosterMessage(dataUrl);
    lastPlan = plan;
    lastImages = images;
  } catch (err) {
    status.remove();
    const detail = (err && err.message) || (err && err.error) || (typeof err === 'string' ? err : JSON.stringify(err)) || 'unknown error';
    addBubble('Could not apply that change: ' + detail + '. Try describing it differently.', 'bot');
  }
}

async function renderPoster(plan, images) {
  const [heroRaw, t1Raw, t2Raw, t3Raw] = images;
  const [hero, t1, t2, t3] = await Promise.all([heroRaw, t1Raw, t2Raw, t3Raw].map(loadImgEl));
  const logo = await loadImgEl(customLogoDataUri || DEFAULT_LOGO);

  const W = 1080, H = 1527;
  const canvas = document.createElement('canvas');
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');
  const accent = resolvedColor.hex;
  const dark = resolvedTheme === 'night';

  ctx.fillStyle = dark ? '#111318' : '#ffffff';
  ctx.fillRect(0, 0, W, H);

  ctx.fillStyle = dark ? '#1c1f26' : '#f0f0f0';
  ctx.fillRect(0, 0, W, 90);
  ctx.fillStyle = accent;
  ctx.fillRect(0, 0, 10, 90);
  ctx.fillStyle = dark ? '#eee' : '#333';
  ctx.font = '600 26px sans-serif';
  ctx.fillText((plan.badge_text || 'PROPERTY FOR SALE').toUpperCase(), 36, 54);
  drawCover(ctx, logo, W - 220, 15, 180, 60);

  const heroY = 110, heroH = 620, heroW = Math.round(W * 0.58);
  drawCover(ctx, hero, 0, heroY, heroW, heroH);
  ctx.fillStyle = accent;
  ctx.fillRect(heroW, heroY, W - heroW, heroH);
  ctx.fillStyle = '#ffffff';
  ctx.font = '700 54px sans-serif';
  const headLines = wrapText(ctx, plan.headline || fields.property_type, W - heroW - 60);
  let ty = heroY + 90;
  for (const l of headLines) { ctx.fillText(l, heroW + 30, ty); ty += 62; }
  ty += 20;
  ctx.font = '400 22px sans-serif';
  ctx.fillText((plan.price_line || 'PRICE').toUpperCase(), heroW + 30, ty); ty += 44;
  ctx.font = '700 42px sans-serif';
  for (const l of wrapText(ctx, plan.price_value || fields.price, W - heroW - 60)) { ctx.fillText(l, heroW + 30, ty); ty += 48; }
  ty += 16;
  ctx.font = '600 20px sans-serif';
  for (const l of wrapText(ctx, plan.spec_line || fields.highlights, W - heroW - 60)) { ctx.fillText(l, heroW + 30, ty); ty += 28; }

  let y = heroY + heroH + 40;
  ctx.fillStyle = dark ? '#eee' : '#222';
  ctx.font = '700 26px sans-serif';
  ctx.fillText('OVERVIEW', 36, y);
  ctx.fillStyle = accent;
  ctx.fillRect(220, y - 8, W - 256, 3);
  y += 24;
  const thumbGap = 16, thumbW = (W - 72 - thumbGap * 2) / 3, thumbH = 180;
  [t1, t2, t3].forEach((im, i) => drawCover(ctx, im, 36 + i * (thumbW + thumbGap), y, thumbW, thumbH));
  y += thumbH + 50;

  ctx.fillStyle = dark ? '#eee' : '#222';
  ctx.font = '700 26px sans-serif';
  ctx.fillText('ABOUT THE PROPERTY', 36, y);
  ctx.fillStyle = accent;
  ctx.fillRect(340, y - 8, W - 376, 3);
  y += 34;
  ctx.fillStyle = dark ? '#ccc' : '#444';
  ctx.font = '400 21px sans-serif';
  for (const l of wrapText(ctx, plan.about_paragraph || '', W - 72)) { ctx.fillText(l, 36, y); y += 30; }
  y += 30;

  ctx.fillStyle = dark ? '#eee' : '#222';
  ctx.font = '700 26px sans-serif';
  ctx.fillText('PROPERTY BENEFITS', 36, y);
  ctx.fillStyle = accent;
  ctx.fillRect(300, y - 8, W - 336, 3);
  y += 44;
  const benefits = (plan.benefits || []).slice(0, 3);
  const colW = (W - 72) / 3;
  benefits.forEach((b, i) => {
    const bx = 36 + i * colW;
    ctx.font = '32px sans-serif';
    ctx.fillStyle = accent;
    ctx.fillText(pickIcon(b.title || ''), bx, y + 32);
    ctx.fillStyle = dark ? '#eee' : '#222';
    ctx.font = '700 18px sans-serif';
    let by = y + 70;
    for (const l of wrapText(ctx, (b.title || '').toUpperCase(), colW - 24)) { ctx.fillText(l, bx, by); by += 24; }
    ctx.fillStyle = dark ? '#bbb' : '#555';
    ctx.font = '400 16px sans-serif';
    for (const l of wrapText(ctx, b.desc || '', colW - 24)) { ctx.fillText(l, bx, by); by += 22; }
  });
  y += 150;

  ctx.fillStyle = dark ? '#eee' : '#222';
  ctx.font = '700 26px sans-serif';
  ctx.fillText('GET IN TOUCH', 36, y);
  ctx.fillStyle = accent;
  ctx.fillRect(230, y - 8, W - 266, 3);
  y += 34;
  ctx.font = '400 18px sans-serif';
  ctx.fillStyle = dark ? '#ccc' : '#333';
  ctx.fillText('M: ' + BRAND.phone + '  (' + BRAND.manager_name + ')', 36, y);
  const addrLines = wrapText(ctx, BRAND.address, 420);
  let ay = y - 22;
  for (const l of addrLines) { ctx.fillText(l, W - 456, ay); ay += 24; }
  y += 30;
  ctx.fillText('E: info@' + BRAND.company_name.toLowerCase() + '.com', 36, y);

  ctx.fillStyle = dark ? '#666' : '#999';
  ctx.font = '400 14px sans-serif';
  ctx.fillText(BRAND.applicant_credit, 36, H - 14);

  return canvas.toDataURL('image/png');
}
</script>
"""


def build_component_html(branding: dict) -> str:
    branding_json = _safe_json(
        {
            "company_name": branding["company_name"],
            "address": branding["address"],
            "manager_name": branding["manager_name"],
            "phone": branding["phone"],
            "applicant_credit": branding["applicant_credit"],
        }
    )
    logo_data_uri = _safe_json(branding["logo_data_uri"])
    groq_json = _safe_json(
        {"api_key": branding["groq_api_key"], "model": branding["groq_model"]}
    )
    out = _TEMPLATE
    out = out.replace("__BRAND_JSON__", branding_json)
    out = out.replace("__LOGO_DATA_URI__", logo_data_uri)
    out = out.replace("__GROQ_JSON__", groq_json)
    return out
