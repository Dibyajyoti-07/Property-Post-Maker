# Execution Prompt — Property Post Maker (Puter.js build)

Paste everything below the line into a fresh Claude Code session (after loading the recommended skills) to execute the build in one pass.

Recommended skills to load first: `ponytail` (lean implementation, no over-engineering), `task-observer` (capture any corrections as reusable lessons), `caveman` (optional, terse chat only — does not affect code/doc quality).

---

## Goal

Build and deploy a live "Property Post Maker": a Streamlit app where a user fills 4 fields (Property & Type, Location, Price, Highlights), then has a free-text AI chat exchange to pick a Day/Night theme and a color scheme, and the app generates a full AI-composed property flyer (photorealistic hero photo + 3 amenity thumbnails + written copy + benefit tiles + logo + contact strip) as a downloadable PNG — matching the quality/layout bar of the reference image `template.png` in the project root. Zero paid services anywhere in the stack.

## Hard constraints

- No paid APIs, no API keys, no paid hosting, no paid fonts/assets. AI generation runs entirely through **Puter.js** (`https://js.puter.com/v2/`), loaded client-side — free under Puter's "User-Pays" model (visitor signs into their own free Puter account on first AI call via a one-time popup; this costs the app owner nothing).
- Deploy target: Streamlit Community Cloud, connected to the existing GitHub repo `https://github.com/Dibyajyoti-07/Property-Post-Maker.git` (remote already configured, `main` branch already pushed once).
- Keep Streamlit as the Python shell for the 4-field form. All AI calls, the chat UI, image generation, canvas compositing, and the PNG download happen inside one embedded `st.components.v1.html(...)` block — do not build a separate backend, do not call any AI API from Python.
- Reference files already in the project root: `logo.png` (Merlin logo, use as-is), `image.png` (earlier generic layout reference — secondary, lower priority than `template.png`), `template.png` (**the canonical visual target — match its structure**: top badge strip + logo top-right, hero photo + colored info panel with headline/price/spec, 3 overview thumbnail photos in a row, "About the property" paragraph block, 3 benefit tiles with short titles/descriptions, "Get In Touch" contact block).
- Branding data: `COMPANY_NAME = "Merlin"`, `ADDRESS = "22, Prince Anwar Shah Road, 2nd Floor, Merlin Oxford, Kolkata - 700033"`. `MANAGER_NAME` and `PHONE`/WhatsApp are **not yet supplied** — use clearly-labeled placeholders (e.g. `"Merlin Sales Team"` / `"+91-XXXXXXXXXX"`) so the app is fully demoable now; isolate these in `branding.py` so swapping later is a one-line edit. Applicant credit: infer `"Dibyajyoti Sarkar"` from the project owner's email (`dibyajyotisarkar07@gmail.com`) as a placeholder build-credit line, clearly a placeholder pending confirmation.
- Existing planning docs (`docs/PRD.md`, `docs/TRD.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/TESTCASES.md`) describe an earlier Pillow/static-card approach — **this is superseded**. Update all four docs to describe this Puter.js/AI-chat/canvas architecture instead, so they stay accurate as required assignment deliverables. Do not leave them describing the old approach.
- `.gitignore` already exists and is correct — do not commit secrets (none are needed here; branding data is intentionally public-facing).

## Task graph

Nodes and dependencies — build roughly in this order, parallelizing independent nodes where obvious:

```
A: branding.py (constants + placeholders)          [no deps]
B: logo → base64 inline helper (Python, reads logo.png)   [no deps]
C: generator_template.py — HTML/JS component string      [depends on A, B for interpolation points]
D: app.py — Streamlit form (4 fields, validation)         [no deps]
E: wire D → C via st.components.v1.html(...)              [depends on C, D]
F: local run + manual QA against docs/TESTCASES.md-style checks   [depends on E]
G: update docs/PRD.md, TRD.md, IMPLEMENTATION_PLAN.md, TESTCASES.md to match reality   [depends on E, can start once architecture is stable, finish after F]
H: git add/commit/push to existing origin/main            [depends on F, G]
I: deploy on Streamlit Community Cloud (connect repo, app.py entrypoint)   [depends on H]
J: smoke-test the live URL end to end                     [depends on I]
K: generate the one required sample post from the LIVE url [depends on J]
L: record the 1-minute Claude Code build walkthrough       [independent, do anytime, ideally covering A–I]
```

## Node details

**A — `branding.py`**
```python
COMPANY_NAME = "Merlin"
ADDRESS = "22, Prince Anwar Shah Road, 2nd Floor, Merlin Oxford, Kolkata - 700033"
MANAGER_NAME = "Merlin Sales Team"  # placeholder — swap when supplied
PHONE = "+91-XXXXXXXXXX"            # placeholder — swap when supplied
LOGO_PATH = "logo.png"
APPLICANT_CREDIT = "Built by Dibyajyoti Sarkar with Claude Code"  # placeholder name, confirm
```

**B — logo inlining**
The embedded component runs in a sandboxed `srcdoc` iframe with no access to relative file paths — the logo must travel as a `data:image/png;base64,...` URI built in Python (`base64.b64encode(open(LOGO_PATH,'rb').read())`) and interpolated directly into the HTML/JS string, not referenced by path.

**C — `generator_template.py` (HTML/JS string, function `build_component_html(fields: dict, branding: dict) -> str`)**
Inside the returned HTML:
1. `<script src="https://js.puter.com/v2/"></script>`.
2. Chat-bubble UI. Bot asks: *"Day or Night theme?"* User types free text. Call `puter.ai.chat(...)` instructed to reply with **only** strict JSON `{"theme":"day"|"night"|"unclear"}`. Parse defensively (strip code fences before `JSON.parse`); on `"unclear"` or a parse failure, re-ask once with a clarifying nudge before giving up gracefully.
3. Bot asks: *"What color scheme should the ad use?"* Free text reply → `puter.ai.chat(...)` instructed to reply with strict JSON `{"hex":"#RRGGBB","label":"Lime Green","resolved":true|false}`. Same defensive-parse + one re-ask pattern.
4. One content-planning `puter.ai.chat(...)` call given the 4 raw field values + resolved theme + resolved color, instructed to return strict JSON:
   ```json
   {
     "headline": "...", "sub_headline": "...", "price_line": "...", "spec_line": "...",
     "about_paragraph": "...",
     "benefits": [{"title": "...", "desc": "..."}, {"title": "...", "desc": "..."}, {"title": "...", "desc": "..."}],
     "hero_prompt": "...", "thumb_prompts": ["...", "...", "..."]
   }
   ```
   `hero_prompt`/`thumb_prompts` must explicitly bake in the resolved day/night lighting and the resolved color accent so the generated photos visually match the chosen theme. `benefits`/`about_paragraph` must be derived from what the user actually typed in Highlights, not generic filler.
5. Four `puter.ai.txt2img(prompt)` calls in parallel (`Promise.all`) — hero + 3 thumbnails.
6. Canvas compositing matching `template.png`'s structure: top badge strip (derived headline + property type) with the inlined base64 logo top-right; hero photo left + colored info panel right (panel fill = resolved hex; headline/price/spec text); 3 overview thumbnails row; About paragraph block; 3 benefit tiles (title + desc, icon as a simple unicode glyph or basic canvas shape — no icon library dependency); Get In Touch block using `branding` values; small applicant-credit line. Since `txt2img` results won't reliably match each box's aspect ratio, compute a manual center-crop rectangle for each `drawImage` call (canvas has no CSS `object-fit`) so photos fill their boxes without distortion.
7. `canvas.toBlob('image/png')` → object URL → an in-iframe `<a download>` element/button + `<img>` preview. No Python round-trip needed for the download.
8. One retry on any failed `chat`/`txt2img` call, then a plain in-UI error message — no elaborate retry framework.

**D — `app.py`**
4 Streamlit inputs (Property & Type, Location, Price, Highlights), all required, inline `st.error` per missing field on submit, soft max-length hint (not hard enforcement). On valid submit, call `build_component_html(fields, branding)` and render via `st.components.v1.html(html, height=<enough for chat + poster>, scrolling=True)`.

**F — manual QA** (see `docs/TESTCASES.md`, which should already be updated per node G by this point): run through the assignment's own villa example, deliberately give one ambiguous theme/color answer to confirm the re-ask path, confirm final poster visually matches `template.png`'s structure, confirm PNG downloads and opens correctly, confirm the one-time Puter sign-in popup appears and generation resumes correctly afterward.

**G — docs update**: rewrite `docs/PRD.md` (fields/flow: now includes the theme/color chat step and the AI-generated-photo output, not a flat card), `docs/TRD.md` (stack: Streamlit shell + Puter.js client-side AI, no Pillow needed for the live path, no backend), `docs/IMPLEMENTATION_PLAN.md` (this task graph, essentially), `docs/TESTCASES.md` (add chat-parsing edge cases, image-crop/aspect-ratio cases, Puter auth-popup case, alongside the existing manual/auto-element/image/deploy cases). Keep all four internally consistent with each other and with the actual code.

**H/I — commit, push, deploy**: standard `git add` (specific files, not `-A`), commit, push to the existing `origin/main`. Connect the repo at share.streamlit.io with `app.py` as entrypoint if not already connected; Streamlit Cloud auto-redeploys on every push once connected.

**J/K — live smoke test + sample post**: on the actual deployed `*.streamlit.app` URL (not just localhost), run the full flow once with the assignment's own example values and save that output as the one required sample post.

## Known open items (flag back, don't silently invent)

- Manager name and phone/WhatsApp number: still placeholders — real values needed before final submission, single-line swap in `branding.py` once supplied.
- Applicant credit name inferred from email as "Dibyajyoti Sarkar" — confirm this is correct/how the applicant wants their name to appear.
- 1-minute build recording and final "reply within 24h" submission (live link + sample post + recording + name-in-tool) are on the user, not something to be done by the coding agent.

## Acceptance checklist

- [ ] `app.py` runs locally with `streamlit run app.py`, form validates all 4 required fields.
- [ ] Chat step correctly resolves an unambiguous theme/color answer on the first try, and correctly re-asks on an ambiguous one.
- [ ] Generated poster contains: logo, all 4 user-entered values reflected somewhere, hero photo + 3 thumbnails, About paragraph, 3 benefit tiles, contact block (Merlin + address + placeholder phone/manager), applicant credit line.
- [ ] Downloaded PNG opens correctly and visually matches `template.png`'s layout structure.
- [ ] All 4 docs under `docs/` describe this architecture, not the old Pillow one.
- [ ] Code pushed to `origin/main`; live Streamlit Cloud URL confirmed working end to end.
