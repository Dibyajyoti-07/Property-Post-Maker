# Technical Requirements Document — Property Post Maker

## 1. Technology Stack

- **Language / shell:** Python 3 + Streamlit — renders the 4-field form and hosts the page. No Python image library is used for the live generation path.
- **AI + image generation:** **Puter.js** (`https://js.puter.com/v2/`), loaded client-side inside an embedded HTML/JS component. `puter.ai.chat()` handles the theme/color free-text resolution and the content-planning step (copy + image prompts); `puter.ai.txt2img()` generates the hero photo and three amenity thumbnails. Free under Puter's "User-Pays" model — no API keys, no backend, no cost to the app owner.
- **Compositing:** the browser's HTML5 `<canvas>` API draws the final poster (badge strip, hero + info panel, thumbnails, copy, benefit tiles, contact block, logo) — no server-side image library needed.
- **No backend, no database.** Generation happens entirely in the visitor's browser; the Streamlit process only serves the form and injects the four field values plus branding constants into the embedded component's HTML.
- **No secrets required.** Branding data (company name, manager name, phone, address) is public-facing by design and lives in a plain committed `branding.py`.

## 2. Architecture

1. `app.py` renders the 4-field Streamlit form (`st.text_input` / `st.text_area`) with a submit button; validates all four are non-empty (inline `st.error` per missing field).
2. On valid submit, `app.py` calls `generator_template.build_component_html(fields, branding_data)` — `branding_data` includes the Merlin logo read from disk and base64-inlined as a `data:image/png;base64,...` URI (`generator_template.encode_logo`), since the component runs in a sandboxed `srcdoc` iframe with no access to relative file paths.
3. `app.py` renders the returned HTML via `st.components.v1.html(html, height=1700, scrolling=True)`.
4. Inside the component: a chat-bubble UI asks "Day or Night theme?" — the user's free-text reply goes to `puter.ai.chat()` with an instruction to reply with strict JSON (`{"theme":"day"|"night"|"unclear"}`); an `"unclear"` result triggers one re-ask before defaulting.
5. Same pattern for "What color scheme?" — resolved to `{"hex":"#RRGGBB","label":"...","resolved":true|false}`.
6. A content-planning `puter.ai.chat()` call, given the four fields plus the resolved theme/color, returns strict JSON: badge text, headline, price/spec lines, an About paragraph, three benefit tiles, and four image prompts (hero + three thumbnails) that explicitly bake in the theme's lighting and the accent color.
7. Four `puter.ai.txt2img()` calls generate the hero and three thumbnail photos, using the `gpt-image-1` model explicitly (Puter's default model and the Replicate-routed FLUX models were unreliable on the free tier during development — see code comment in `generator_template.py`). Calls run **sequentially**, not in parallel, because the free image backend throttles concurrent requests; each call gets one automatic retry on failure.
8. The component draws everything onto a 1080×1527 `<canvas>`, computing a manual center-crop for each photo (canvas has no CSS `object-fit`), fills the accent-colored info panel and section rules with the resolved hex, and renders the contact block from the branding constants.
9. `canvas.toBlob`/`toDataURL('image/png')` produces the final image; an in-component `<img>` preview and `<a download>` link are shown — no round-trip back to Python is needed for the download.

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
