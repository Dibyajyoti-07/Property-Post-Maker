# Technical Requirements Document — Property Post Maker

## 1. Technology Stack

- **Language / shell:** Python 3 + Streamlit — renders the 4-field form and hosts the page. No Python image library is used for the live generation path.
- **AI text (chat/planning):** **Puter.js** (`https://js.puter.com/v2/`), loaded client-side inside an embedded HTML/JS component. `puter.ai.chat()` handles the theme/color free-text resolution and the content-planning step (copy + image prompts). Free under Puter's "User-Pays" model — no API keys, no backend, no cost to the app owner.
- **AI image generation:** **Pollinations.ai**'s Flux endpoint (`image.pollinations.ai/prompt/...`) — free, unlimited, no login or API key required at all. Puter's own `puter.ai.txt2img()` was used originally, but it's billed against the signed-in account's free credit allotment, which exhausts with regular use; switched to Pollinations to remove that ceiling entirely without giving up photo quality.
- **Compositing:** the browser's HTML5 `<canvas>` API draws the final poster (badge strip, hero + info panel, thumbnails, copy, benefit tiles, contact block, logo) — no server-side image library needed.
- **No backend, no database.** Generation happens entirely in the visitor's browser; the Streamlit process only serves the form and injects the four field values plus branding constants into the embedded component's HTML.
- **No secrets required.** Branding data (company name, manager name, phone, address) is public-facing by design and lives in a plain committed `branding.py`.

## 2. Architecture

The whole experience is one continuous chat, entirely inside a single embedded component — there is no separate Streamlit form.

1. `app.py` calls `generator_template.build_component_html(branding_data)` on every page load — `branding_data` includes the Merlin logo read from disk and base64-inlined as a `data:image/png;base64,...` URI (`generator_template.encode_logo`), since the component runs in a sandboxed `srcdoc` iframe with no access to relative file paths. Rendered via `st.components.v1.html(html, height=900, scrolling=True)`.
2. Inside the component, a client-side state machine (`stage`: `collecting` → `theme` → `color` → `generating` → `done`) drives everything:
   - **collecting**: the assistant asks the user to describe the property; each reply is appended to an accumulating text buffer and sent to `puter.ai.chat()`, instructed to extract `{property_type, location, price, highlights, missing}` as strict JSON — Location is never listed as missing (the model is told to invent a plausible one itself); if `property_type`/`price`/`highlights` are still absent, the assistant asks specifically for those and loops.
   - **theme**: "Day or Night?" — free-text reply resolved via `puter.ai.chat()` to strict JSON `{"theme":"day"|"night"|"unclear"}`; unclear triggers one re-ask before defaulting.
   - **color**: same pattern, resolved to `{"hex":"#RRGGBB","label":"...","resolved":true|false}`.
   - **generating**: a content-planning `puter.ai.chat()` call, given the four fields plus the resolved theme/color, returns strict JSON (badge text, headline, price/spec lines, About paragraph, three benefit tiles, and four image prompts baking in the theme's lighting and the accent color).
3. Four photos (hero + three thumbnails) are fetched from Pollinations' Flux endpoint. Pollinations allows a plain `<img>` embed but returns 403 for any CORS-mode read (`img.crossOrigin`, plain `fetch()`) — confirmed by testing both directly — which would otherwise taint the canvas and break `toDataURL()`. The fetch is routed through `puter.net.fetch()` instead (a free CORS-bypass relay included in Puter.js, unrelated to the AI-generation credit pool); the response bytes are read as a `Blob`, turned into an object URL, and loaded into an `<img>` from there, which canvas can safely read. Calls run **sequentially**, not in parallel (Pollinations rate-limits anonymous requests to roughly one every 15 seconds); each call gets one automatic retry on failure. While each photo generates, an animated shimmer placeholder (CSS gradient sweep, sized to the poster's aspect ratio) plus a rotating status caption ("Generating hero photo...", etc.) render inline in the chat, mirroring a ChatGPT/Gemini-style image-generation loading state.
4. The component draws everything onto a 1080×1527 `<canvas>`, computing a manual center-crop for each photo (canvas has no CSS `object-fit`), fills the accent-colored info panel and section rules with the resolved hex, and renders the contact block from the branding constants, using either the default logo or a user-supplied custom logo (see §2a) drawn top-right.
5. `canvas.toDataURL('image/png')` produces the final image, shown inline as the assistant's final chat message (replacing the shimmer placeholder) with a download link — no round-trip back to Python is needed for the download.

## 2a. Custom Logo Upload

A "+" button beside the chat's send button opens a modal with a file input. Selecting an image reads it via `FileReader.readAsDataURL` into a `customLogoDataUri` JS variable (with a live preview in the modal before saving); once saved, that data URI is used instead of the default branding logo for any poster generated in that browser session. Nothing is uploaded to a server — the file never leaves the browser.

## 3. Branding Configuration

All brand constants live in `branding.py`:

```python
COMPANY_NAME = "Merlin"
ADDRESS = "22, Prince Anwar Shah Road, 2nd Floor, Merlin Oxford, Kolkata - 700033"
MANAGER_NAME = "Merlin Sales Team"  # placeholder - swap when supplied
PHONE = "+91-XXXXXXXXXX"  # placeholder - swap when supplied
LOGO_PATH = "logo.png"
APPLICANT_CREDIT = "Built by Dibyajyoti Sarkar with Claude Code"  # placeholder name, confirm
```

`MANAGER_NAME` and `PHONE` are still placeholders pending real values; swapping is a one-line edit with no other code change.

## 4. Non-Functional Requirements

- **Cost:** $0. Puter.js AI usage is free under the User-Pays model; hosting is Streamlit Community Cloud's free tier; no API keys, no metered services.
- **First-run auth:** a visitor's first AI call may prompt a one-time Puter sign-in popup (free account) — this is expected behavior, not an error.
- **Latency:** generation is not instant — two chat calls plus a planning call plus four sequential image calls typically take well under a minute but noticeably longer than the old flat-card approach; the UI shows status text throughout ("Generating hero photo...", etc.) so this reads as progress, not a hang.
- **Portability:** the embedded component is plain HTML/CSS/JS with no build step, so it renders identically regardless of host OS.

## 5. Deployment

- Source hosted at `github.com/Dibyajyoti-07/Property-Post-Maker` (public, required for the free Streamlit Community Cloud connection flow).
- `requirements.txt` pins only `streamlit`.
- Deploy via share.streamlit.io: connect the GitHub repo, `app.py` as entry point; Streamlit Cloud rebuilds on every push to `main`.

## 6. File/Folder Layout

```
Property Post Maker/
  app.py                   # Streamlit form + orchestration
  generator_template.py    # logo base64 helper + embedded HTML/JS component (chat, AI calls, canvas render)
  branding.py               # branding constants (placeholders for manager name / phone)
  requirements.txt          # streamlit
  logo.png                  # Merlin logo
  template.png               # visual reference used to design the poster layout
  docs/
    PRD.md
    TRD.md
    IMPLEMENTATION_PLAN.md
    TESTCASES.md
    EXECUTION_PROMPT.md
```

## 7. Explicitly Not Used

To satisfy "no paid services": no OpenAI/Anthropic/Google API keys of our own (Puter.js's free User-Pays model is used instead), no paid stock-photo/icon APIs, no paid font licenses (system sans-serif fonts via canvas), no paid hosting tier, no paid domain.
