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
  body { margin: 0; background: #f4f4f4; }
  #chat { max-width: 640px; margin: 0 auto; padding: 12px; }
  .bubble { padding: 10px 14px; border-radius: 12px; margin: 6px 0; max-width: 80%; line-height: 1.4; }
  .bot { background: #e9edf3; align-self: flex-start; }
  .user { background: #2563eb; color: white; margin-left: auto; }
  #messages { display: flex; flex-direction: column; }
  #inputRow { display: flex; gap: 8px; margin-top: 10px; }
  #userInput { flex: 1; padding: 10px; border-radius: 8px; border: 1px solid #ccc; }
  #sendBtn { padding: 10px 18px; border-radius: 8px; border: none; background: #2563eb; color: white; cursor: pointer; }
  #sendBtn:disabled { background: #999; cursor: not-allowed; }
  #status { color: #666; font-style: italic; margin: 8px 0; }
  #result { text-align: center; margin-top: 16px; }
  #result img { max-width: 100%; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,.15); }
  #downloadBtn { display: inline-block; margin-top: 12px; padding: 10px 20px; background: #16a34a; color: white; border-radius: 8px; text-decoration: none; font-weight: 600; }
  .error { color: #b91c1c; }
</style>
<div id="chat">
  <div id="messages"></div>
  <div id="status" style="display:none;"></div>
  <div id="inputRow">
    <input id="userInput" type="text" placeholder="Type your answer..." />
    <button id="sendBtn">Send</button>
  </div>
  <div id="result"></div>
</div>
<script src="https://js.puter.com/v2/"></script>
<script>
const FIELDS = __FIELDS_JSON__;
const BRAND = __BRAND_JSON__;
const LOGO_DATA_URI = __LOGO_DATA_URI__;

const messagesEl = document.getElementById('messages');
const statusEl = document.getElementById('status');
const inputEl = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const resultEl = document.getElementById('result');

let stage = 'theme'; // theme -> color -> done
let resolvedTheme = null;
let resolvedColor = null;

function addBubble(text, who) {
  const d = document.createElement('div');
  d.className = 'bubble ' + who;
  d.textContent = text;
  messagesEl.appendChild(d);
  d.scrollIntoView({behavior: 'smooth'});
}

function setStatus(text) {
  statusEl.style.display = text ? 'block' : 'none';
  statusEl.textContent = text || '';
}

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

addBubble('Should the post use a Day or Night theme?', 'bot');

sendBtn.addEventListener('click', handleSend);
inputEl.addEventListener('keydown', (e) => { if (e.key === 'Enter') handleSend(); });

async function handleSend() {
  const text = inputEl.value.trim();
  if (!text) return;
  addBubble(text, 'user');
  inputEl.value = '';
  sendBtn.disabled = true;

  if (stage === 'theme') {
    await handleThemeAnswer(text);
  } else if (stage === 'color') {
    await handleColorAnswer(text);
  }
  sendBtn.disabled = false;
}

async function handleThemeAnswer(text, retried) {
  setStatus('Thinking...');
  const parsed = await askJSON(
    'The user was asked whether they want a "day" or "night" theme for a property ad. ' +
    'Their reply was: "' + text.replace(/"/g, "'") + '". ' +
    'Reply with ONLY strict JSON, no prose, no markdown fences: {"theme":"day"} or {"theme":"night"} or {"theme":"unclear"}.'
  );
  setStatus('');
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
  setStatus('Thinking...');
  const parsed = await askJSON(
    'The user was asked what color scheme to use for a property ad. Their reply was: "' + text.replace(/"/g, "'") + '". ' +
    'Resolve this to a single representative CSS hex color and a short label. ' +
    'Reply with ONLY strict JSON, no prose, no markdown fences: {"hex":"#RRGGBB","label":"Lime Green","resolved":true} ' +
    'or {"resolved":false} if you truly cannot determine a color.'
  );
  setStatus('');
  if (parsed && parsed.resolved && /^#[0-9a-fA-F]{6}$/.test(parsed.hex)) {
    resolvedColor = parsed;
    stage = 'done';
    addBubble('Great — ' + parsed.label + '. Generating your post now, this can take up to a minute...', 'bot');
    inputEl.style.display = 'none';
    sendBtn.style.display = 'none';
    generatePost();
  } else if (!retried) {
    addBubble('Sorry, what color or color scheme would you like?', 'bot');
  } else {
    resolvedColor = {hex: '#2563eb', label: 'Blue'};
    stage = 'done';
    addBubble("I'll default to Blue. Generating your post now, this can take up to a minute...", 'bot');
    inputEl.style.display = 'none';
    sendBtn.style.display = 'none';
    generatePost();
  }
}

async function generatePost() {
  try {
    setStatus('Planning content...');
    const plan = await askJSON(
      'You are writing copy for a real-estate property advertisement poster. Given:\n' +
      'Property & Type: ' + FIELDS.property_type + '\n' +
      'Location: ' + FIELDS.location + '\n' +
      'Price: ' + FIELDS.price + '\n' +
      'Highlights: ' + FIELDS.highlights + '\n' +
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
      setStatus('Generating ' + label + '...');
      try {
        return await puter.ai.txt2img(prompt, IMG_MODEL);
      } catch (e) {
        await new Promise((r) => setTimeout(r, 2000));
        return await puter.ai.txt2img(prompt, IMG_MODEL);
      }
    }
    // sequential, not parallel: the free image backend throttles concurrent requests
    const hero = await genImage(plan.hero_prompt, 'hero photo');
    const t1 = await genImage(plan.thumb_prompts[0], 'photo 1 of 3');
    const t2 = await genImage(plan.thumb_prompts[1], 'photo 2 of 3');
    const t3 = await genImage(plan.thumb_prompts[2], 'photo 3 of 3');

    setStatus('Composing poster...');
    const dataUrl = await renderPoster(plan, [hero, t1, t2, t3]);
    setStatus('');

    resultEl.innerHTML = '';
    const img = document.createElement('img');
    img.src = dataUrl;
    resultEl.appendChild(img);
    const a = document.createElement('a');
    a.id = 'downloadBtn';
    a.href = dataUrl;
    a.download = (FIELDS.property_type || 'property-post').replace(/[^a-z0-9]+/gi, '-').toLowerCase() + '.png';
    a.textContent = 'Download Post';
    resultEl.appendChild(a);
  } catch (err) {
    setStatus('');
    addBubble('Something went wrong generating your post: ' + err.message + '. Please reload and try again.', 'bot');
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

async function renderPoster(plan, images) {
  const [heroRaw, t1Raw, t2Raw, t3Raw] = images;
  const [hero, t1, t2, t3] = await Promise.all([heroRaw, t1Raw, t2Raw, t3Raw].map(loadImgEl));
  const logo = await loadImgEl(LOGO_DATA_URI);

  const W = 1080, H = 1527;
  const canvas = document.createElement('canvas');
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');
  const accent = resolvedColor.hex;
  const dark = resolvedTheme === 'night';

  ctx.fillStyle = dark ? '#111318' : '#ffffff';
  ctx.fillRect(0, 0, W, H);

  // Header strip
  ctx.fillStyle = dark ? '#1c1f26' : '#f0f0f0';
  ctx.fillRect(0, 0, W, 90);
  ctx.fillStyle = accent;
  ctx.fillRect(0, 0, 10, 90);
  ctx.fillStyle = dark ? '#eee' : '#333';
  ctx.font = '600 26px sans-serif';
  ctx.fillText((plan.badge_text || 'PROPERTY FOR SALE').toUpperCase(), 36, 54);
  drawCover(ctx, logo, W - 220, 15, 180, 60);

  // Hero + info panel
  const heroY = 110, heroH = 620, heroW = Math.round(W * 0.58);
  drawCover(ctx, hero, 0, heroY, heroW, heroH);
  ctx.fillStyle = accent;
  ctx.fillRect(heroW, heroY, W - heroW, heroH);
  ctx.fillStyle = '#ffffff';
  ctx.font = '700 54px sans-serif';
  const headLines = wrapText(ctx, plan.headline || FIELDS.property_type, W - heroW - 60);
  let ty = heroY + 90;
  for (const l of headLines) { ctx.fillText(l, heroW + 30, ty); ty += 62; }
  ty += 20;
  ctx.font = '400 22px sans-serif';
  ctx.fillText((plan.price_line || 'PRICE').toUpperCase(), heroW + 30, ty); ty += 44;
  ctx.font = '700 42px sans-serif';
  for (const l of wrapText(ctx, plan.price_value || FIELDS.price, W - heroW - 60)) { ctx.fillText(l, heroW + 30, ty); ty += 48; }
  ty += 16;
  ctx.font = '600 20px sans-serif';
  for (const l of wrapText(ctx, plan.spec_line || FIELDS.highlights, W - heroW - 60)) { ctx.fillText(l, heroW + 30, ty); ty += 28; }

  // Overview thumbnails
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

  // About
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

  // Benefits
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

  // Contact
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

  // Credit
  ctx.fillStyle = dark ? '#666' : '#999';
  ctx.font = '400 14px sans-serif';
  ctx.fillText(BRAND.applicant_credit, 36, H - 14);

  return canvas.toDataURL('image/png');
}
</script>
"""


def build_component_html(fields: dict, branding: dict) -> str:
    fields_json = _safe_json(fields)
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
    out = out.replace("__FIELDS_JSON__", fields_json)
    out = out.replace("__BRAND_JSON__", branding_json)
    out = out.replace("__LOGO_DATA_URI__", logo_data_uri)
    return out
