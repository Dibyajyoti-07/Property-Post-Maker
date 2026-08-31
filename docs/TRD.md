# Technical Requirements Document — Property Post Maker

## 1. Technology Stack

- **Language / shell:** Python 3 + Streamlit — renders the page and injects config into the embedded component. No Python image library is used for the live generation path.
- **AI text (chat/extraction/planning):** **Groq** (`api.groq.com/openai/v1/chat/completions`, model `openai/gpt-oss-120b`), called directly from the browser — no login prompt for the visitor, ever. Requires a Groq API key, read server-side from `.env` (local) and injected into the component's HTML at render time.
- **AI image generation:** **Pollinations.ai**'s Flux endpoint (`image.pollinations.ai/prompt/...`), fetched directly from the browser — free, unlimited, no login, no API key, no Puter involved.
- **Compositing:** the browser's HTML5 `<canvas>` API draws the final poster (badge strip, hero + info panel, thumbnails, copy, benefit tiles, contact block, logo) — no server-side image library needed.
- **No backend for AI calls.** Generation happens entirely in the visitor's browser; the Streamlit process only serves the page and injects field/branding/key config into the embedded component's HTML at render time.
- **One real secret:** the Groq API key, in a gitignored `.env` (`GROQ_API_KEY`, `GROQ_MODEL`), loaded by a tiny hand-rolled parser in `app.py` (no new pip dependency). It reaches the browser as part of the rendered page — there's no backend to keep it server-side-only, so it's visible via devtools to anyone who inspects the deployed page. Acceptable for a free-tier key with no billing attached; rotate it if it's ever abused.
- **No Puter dependency anywhere.** Earlier iterations used Puter for both text and (briefly, via a `puter.net.fetch` CORS-relay workaround) images; both were removed at the user's request. Text is Groq, images are direct Pollinations fetches, no login of any kind for visitors.

### 1a. Pollinations and automated testing

Pollinations' image endpoint occasionally challenges programmatic `fetch()` requests with a bot-check, which was tripped consistently during this project's own Claude-Code-driven browser automation testing (a well-known signal for headless/CDP-driven traffic). A real interactive browser session generally shouldn't trip it the same way. Because of this, the image-generation path was implemented directly against Pollinations but **not** re-verified end-to-end via automated browser testing after the Puter removal — verify manually in a normal browser session before relying on it for the assignment's sample post.

## 2. Architecture

The whole experience is one continuous chat, entirely inside a single embedded component — there is no separate Streamlit form.

1. `app.py` loads `GROQ_API_KEY`/`GROQ_MODEL` from `.env`, then calls `generator_template.build_component_html(branding_data)` on every page load — `branding_data` includes the Merlin logo (base64-inlined via `generator_template.encode_logo`, since the component runs in a sandboxed `srcdoc` iframe with no access to relative file paths) plus the Groq config. Rendered via `st.components.v1.html(html, height=700, scrolling=False)`.
2. Inside the component, a client-side state machine (`stage`: `collecting` → `theme` → `color` → `generating` → `done`) drives everything, with every JSON-extraction step going through `askJSON()` (a thin wrapper around a Groq chat-completions `fetch()` call):
   - **collecting**: the assistant asks the user to describe the property; each reply is appended to an accumulating text buffer and sent through `askJSON()`, instructed to extract `{property_type, location, price, highlights, missing}` as strict JSON — Location is never listed as missing (the model is told to invent a plausible one itself); if `property_type`/`price`/`highlights` are still absent, the assistant asks specifically for those and loops.
   - **theme**: "Day or Night?" — free-text reply resolved to strict JSON `{"theme":"day"|"night"|"unclear"}`; unclear triggers one re-ask before defaulting.
   - **color**: same pattern, resolved to `{"hex":"#RRGGBB","label":"...","resolved":true|false}`.
   - **generating**: a content-planning call, given the four fields plus the resolved theme/color, returns strict JSON (badge text, headline, price/spec lines, About paragraph, three benefit tiles, and four image prompts baking in the theme's lighting and the accent color).
3. Four photos (hero + three thumbnails) are fetched from Pollinations' Flux endpoint via plain `fetch()` (`pollinationsUrl()`/`fetchPollinationsImg()`), each wrapped in a 25-second timeout; the response is read as a `Blob` and loaded from an object URL so canvas export stays untainted. Calls run **sequentially**, not in parallel (anonymous Pollinations requests are rate-limited to roughly one every 15 seconds); each call gets one automatic retry on failure. While each photo generates, an animated shimmer placeholder (CSS gradient sweep, sized to the poster's aspect ratio) plus a rotating status caption ("Generating hero photo...", etc.) render inline in the chat, mirroring a ChatGPT/Gemini-style image-generation loading state.
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

- **Cost:** $0. Groq's free-tier API key has no billing attached; Pollinations image generation is free and unlimited; hosting is Streamlit Community Cloud's free tier.
- **No sign-in of any kind.** Neither text (Groq) nor images (Pollinations) ever prompt the visitor to log in or create an account.
- **Latency:** generation is not instant — chat/planning calls plus four sequential image calls typically take well under a minute; the UI shows status text throughout ("Generating hero photo...", etc.) so this reads as progress, not a hang.
- **Portability:** the embedded component is plain HTML/CSS/JS with no build step, so it renders identically regardless of host OS.

## 5. Deployment

- Source hosted at `github.com/Dibyajyoti-07/Property-Post-Maker` (public, required for the free Streamlit Community Cloud connection flow).
- `requirements.txt` pins only `streamlit`.
- Deploy via share.streamlit.io: connect the GitHub repo, `app.py` as entry point; Streamlit Cloud rebuilds on every push to `main`.

## 6. File/Folder Layout

```
Property Post Maker/
  app.py                   # Streamlit shell: loads .env, injects config, renders the component
  generator_template.py    # logo base64 helper + embedded HTML/JS component (chat, AI calls, canvas render)
  branding.py               # branding constants (placeholders for manager name / phone)
  .env                       # GROQ_API_KEY, GROQ_MODEL - gitignored, never committed
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

To satisfy "no paid services": no paid OpenAI/Anthropic/Google API keys (Groq's free tier and Pollinations' free image endpoint are used instead), no paid stock-photo/icon APIs, no paid font licenses (system sans-serif fonts via canvas), no paid hosting tier, no paid domain. Groq's key is a free-tier key with no billing method attached to the account.

## 8. Deployment Note: Secrets

`.env` is local-only (gitignored). When deploying to Streamlit Community Cloud, set `GROQ_API_KEY` (and optionally `GROQ_MODEL`) via the app's "Secrets" panel in the Streamlit Cloud dashboard. `app.py`'s `_secret()` helper checks `st.secrets` first, falling back to `os.environ` (populated from `.env` locally) — covers both Streamlit Cloud's secrets.toml mechanism and local dev without a code change between them.
