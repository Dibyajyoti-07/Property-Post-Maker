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
  html, body { margin: 0; height: 100%; background: #0d0d0f; }
  #app { display: flex; flex-direction: column; height: 860px; max-width: 720px; margin: 0 auto; background: #0d0d0f; color: #e8e8ea; }
  #log { flex: 1; overflow-y: auto; padding: 20px 16px 8px; }
  .row { display: flex; margin: 10px 0; }
  .row.user { justify-content: flex-end; }
  .bubble { padding: 10px 16px; border-radius: 16px; max-width: 78%; line-height: 1.45; white-space: pre-wrap; }
  .row.user .bubble { background: #2a2a30; color: #f0f0f2; border-bottom-right-radius: 4px; }
  .row.bot .bubble { background: transparent; color: #d8d8dc; padding-left: 4px; max-width: 92%; }
  #composer { display: flex; align-items: center; gap: 8px; padding: 14px 16px; border-top: 1px solid #232326; }
  #plusBtn { width: 40px; height: 40px; border-radius: 50%; border: 1px solid #3a3a40; background: #1a1a1d; color: #ddd; font-size: 20px; cursor: pointer; flex: none; }
  #plusBtn:hover { background: #232327; }
  #userInput { flex: 1; padding: 12px 16px; border-radius: 22px; border: 1px solid #3a3a40; background: #1a1a1d; color: #f0f0f0; font-size: 15px; outline: none; }
  #sendBtn { width: 40px; height: 40px; border-radius: 50%; border: none; background: #5b8cff; color: white; cursor: pointer; flex: none; font-size: 16px; }
  #sendBtn:disabled { background: #33384a; cursor: not-allowed; }
  .status-line { display: flex; align-items: center; gap: 8px; color: #a8a8ae; font-size: 14px; margin: 4px 0 10px 4px; }
  .spark { display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #7c8cff; animation: pulse 1s ease-in-out infinite; }
  @keyframes pulse { 0%,100% { opacity: .3; transform: scale(.8);} 50% { opacity: 1; transform: scale(1.1);} }
  .shimmer-box { width: 100%; max-width: 420px; aspect-ratio: 1080 / 1527; border-radius: 16px;
    background: linear-gradient(110deg, #19191c 8%, #29292f 18%, #19191c 33%); background-size: 250% 100%;
    animation: shimmer 1.4s linear infinite; }
  @keyframes shimmer { to { background-position-x: -250%; } }
  .poster-wrap img { max-width: 100%; border-radius: 12px; display: block; }
  #downloadBtn { display: inline-block; margin-top: 10px; padding: 9px 18px; background: #16a34a; color: white; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; }
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
  <div id="log"></div>
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
  <div id="composer">
    <button id="plusBtn" title="Add custom logo">+</button>
    <input id="userInput" type="text" placeholder="Describe the property..." />
    <button id="sendBtn">&#8593;</button>
  </div>
</div>
<script src="https://js.puter.com/v2/"></script>
<script>
const BRAND = __BRAND_JSON__;
const DEFAULT_LOGO = __LOGO_DATA_URI__;
let customLogoDataUri = null;

const logEl = document.getElementById('log');
const inputEl = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const plusBtn = document.getElementById('plusBtn');
const modal = document.getElementById('modalOverlay');
const logoFile = document.getElementById('logoFile');
const logoPreview = document.getElementById('logoPreview');

let stage = 'collecting'; // collecting -> theme -> color -> generating -> done
let collectedText = '';
let fields = { property_type: null, location: null, price: null, highlights: null };
let resolvedTheme = null;
let resolvedColor = null;

function scrollBottom() { logEl.scrollTop = logEl.scrollHeight; }

function addBubble(text, who) {
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

async function askJSON(prompt) {
  const raw = await puter.ai.chat(prompt);
  const text = (typeof raw === 'string') ? raw : (raw && raw.message && raw.message.content) || String(raw);
  try {
    return JSON.parse(stripFences(text));
  } catch (e) {
    return null;
  }
}

addBubble('Describe the property you want to advertise — type, location, price, highlights, all in one go or however you like.', 'bot');

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
      '{"badge_text":"LUXURY CORNER VILLA FOR SALE","headline":"short punchy headline, 3-5 words","price_line":"STARTING FROM","price_value":"the price as given","spec_line":"short spec summary e.g. 4 BHK | 2 STORIES | STREET NAME","about_paragraph":"2-3 sentence description using the highlights","benefits":[{"title":"RESORT AMENITIES","desc":"short real description"},{"title":"HOST & CELEBRATE","desc":"short real description"},{"title":"PRIME LOCATION","desc":"short real description"}],' +
      '"hero_prompt":"a photorealistic real estate exterior photo prompt for an AI image generator, incorporating the property description, ' + resolvedTheme + ' lighting, and a subtle ' + resolvedColor.label + ' accent, no text or logos in the image","thumb_prompts":["photorealistic interior/amenity photo prompt 1 derived from the highlights, ' + resolvedTheme + ' lighting, no text","photorealistic interior/amenity photo prompt 2, no text","photorealistic interior/amenity photo prompt 3, no text"]}'
    );
    if (!plan) { throw new Error('Could not plan content.'); }

    // Puter's default txt2img model currently errors ("Missing `model`"), and the
    // Replicate-routed FLUX models are flaky (concurrency limits, malformed responses)
    // on the free tier. gpt-image-1 has tested reliably; revisit if it degrades.
    const IMG_MODEL = { model: 'gpt-image-1' };
    async function genImage(prompt, label) {
      setCaption(label);
      try {
        return await puter.ai.txt2img(prompt, IMG_MODEL);
      } catch (e) {
        await new Promise((r) => setTimeout(r, 2000));
        return await puter.ai.txt2img(prompt, IMG_MODEL);
      }
    }
    // sequential, not parallel: the free image backend throttles concurrent requests
    const hero = await genImage(plan.hero_prompt, 'Generating hero photo...');
    const t1 = await genImage(plan.thumb_prompts[0], 'Generating photo 1 of 3...');
    const t2 = await genImage(plan.thumb_prompts[1], 'Generating photo 2 of 3...');
    const t3 = await genImage(plan.thumb_prompts[2], 'Generating photo 3 of 3...');

    setCaption('Composing poster...');
    const dataUrl = await renderPoster(plan, [hero, t1, t2, t3]);

    captionRow.remove();
    shimmerRow.remove();
    const row = document.createElement('div');
    row.className = 'row bot';
    const wrap = document.createElement('div');
    wrap.className = 'poster-wrap';
    const img = document.createElement('img');
    img.src = dataUrl;
    wrap.appendChild(img);
    const a = document.createElement('a');
    a.id = 'downloadBtn';
    a.href = dataUrl;
    a.download = (fields.property_type || 'property-post').replace(/[^a-z0-9]+/gi, '-').toLowerCase() + '.png';
    a.textContent = 'Download Post';
    wrap.appendChild(a);
    row.appendChild(wrap);
    logEl.appendChild(row);
    scrollBottom();
    stage = 'done';
  } catch (err) {
    captionRow.remove();
    shimmerRow.remove();
    addBubble('Something went wrong generating your post: ' + err.message + '. Please reload and try again.', 'bot');
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
    out = _TEMPLATE
    out = out.replace("__BRAND_JSON__", branding_json)
    out = out.replace("__LOGO_DATA_URI__", logo_data_uri)
    return out
