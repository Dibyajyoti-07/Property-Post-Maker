# Technical Requirements Document — Property Post Maker

## 1. Technology Stack

- **Language:** Python 3.
- **UI framework:** Streamlit — chosen because it turns a plain Python script into a hosted web form with zero frontend code, and it deploys for free on Streamlit Community Cloud, matching the "no paid services" constraint.
- **Image generation:** Pillow (PIL fork) — pure-Python image compositing (draw text, paste logo, fill shapes). No paid image-generation API (no OpenAI images, no DALL·E, no cloud design API) is used or needed; the post is built deterministically from a fixed layout template plus the four user-entered strings.
- **Fonts:** a small set of open-license (SIL Open Font License) Google Fonts `.ttf` files (e.g. Poppins/Montserrat family — one bold weight for the headline, one regular weight for body text) bundled inside the repo under `assets/fonts/`. Bundling avoids depending on system fonts being present on the Streamlit Cloud host, which cannot be assumed.
- **No backend, no database.** The app is fully stateless: each generation is a pure function of the four form inputs plus the fixed branding config. Nothing is persisted server-side between users or sessions.
- **No secrets required.** Branding data (company name, manager name, phone, address) is intentionally public-facing information meant to appear on every post, so it lives in a plain committed config file, not in Streamlit secrets or environment variables.

## 2. Architecture

Single-process, single-page Streamlit app. Request flow:

1. `app.py` renders a form with the four fields described in the PRD (`st.text_input` / `st.text_area`), plus a "Generate Post" submit button.
2. On submit, `app.py` validates that all four fields are non-empty (inline `st.error` per missing field; generation is blocked until all four are filled).
3. `app.py` calls `card_generator.generate_post(property_type, location, price, highlights)`, passing the four validated strings.
4. `card_generator.py` builds the image entirely in memory:
   - opens/creates the fixed 1080×1080 canvas (flat background or a bundled background template image),
   - draws the headline (Property & Type) and location using the bundled bold/regular fonts, with automatic text wrapping and a font-size step-down loop if the string is too long to fit its box at the default size,
   - draws the price prominently in its own zone,
   - draws the highlights row (splits on common delimiters — `·`, `,`, `|` — and lays them out as a compact row or wrapped block),
   - pastes the logo image (from `branding.py`'s configured path) into the fixed top brand strip, keeping aspect ratio,
   - draws the fixed bottom contact strip using the company name, manager name, phone/WhatsApp, and address constants from `branding.py`.
   - returns the finished image as PNG bytes (via an in-memory `io.BytesIO` buffer — no temp files written to disk, so it works unmodified on Streamlit Cloud's ephemeral filesystem).
5. `app.py` displays the returned PNG with `st.image` and offers it via `st.download_button` (`mime="image/png"`, filename derived from the property/location text).
6. A small, always-visible footer in `app.py` (outside the generated image) shows the applicant's build credit, satisfying "your name in the tool."

## 3. Branding Configuration

All brand constants live in one file, `branding.py`, so real assets can be dropped in with a single edit and no logic changes:

```python
COMPANY_NAME = "..."      # builder/company name
MANAGER_NAME = "..."      # manager's name shown on the contact line
PHONE = "..."             # phone / WhatsApp number
ADDRESS = "..."           # builder's office address
LOGO_PATH = "assets/logo.png"
APPLICANT_CREDIT = "Built by ... for the MLH Claude Intern task"
```

Until the user supplies the real logo file and contact details, this file ships with clearly-labeled placeholder values so the app is fully runnable and demoable end to end; swapping to real values is a same-file text/asset replacement with no code change elsewhere.

## 4. Non-Functional Requirements

- **Cost:** $0. Every dependency (Streamlit, Pillow, the bundled fonts) is free and open-source; hosting is Streamlit Community Cloud's free tier; no API keys, no metered services.
- **Statelessness / concurrency safety:** because generation is a pure function of its inputs with no shared mutable state or disk writes, concurrent users on the same deployed instance cannot interfere with each other's output.
- **Performance:** generation must complete well under 2 seconds for typical input lengths — pure in-memory Pillow drawing on a 1080×1080 canvas, no network calls, so this is not a practical concern.
- **Portability:** must run identically on the developer's local machine (Windows) and on Streamlit Community Cloud's Linux containers — achieved by bundling fonts/assets in-repo (no reliance on OS-installed fonts) and using only cross-platform, pure-Python libraries.

## 5. Deployment

- Source hosted in a public GitHub repository (required for the free Streamlit Community Cloud connection flow).
- `requirements.txt` pins the two runtime dependencies: `streamlit` and `Pillow`.
- Deploy via share.streamlit.io: connect the GitHub repo, point at `app.py` as the entry point; Streamlit Cloud builds and serves the app at a public `*.streamlit.app` URL automatically on every push to the connected branch.
- No `Procfile`, Docker, or custom server config needed — Streamlit Community Cloud handles the run command natively for a Streamlit entry-point script.

## 6. Proposed File/Folder Layout

```
Property Post Maker/
  app.py                     # Streamlit UI + form + orchestration
  card_generator.py          # Pillow-based image compositing logic
  branding.py                # Branding constants (placeholder until real assets supplied)
  requirements.txt           # streamlit, Pillow
  assets/
    fonts/                   # bundled OFL-licensed .ttf files
    logo.png                 # placeholder until real logo supplied
    background/              # optional fixed background/template image
  docs/
    PRD.md
    TRD.md
    IMPLEMENTATION_PLAN.md
    TESTCASES.md
  tests/
    test_card_generator.py   # pytest unit tests for the image-generation logic
```

## 7. Explicitly Not Used

To satisfy "no paid services": no OpenAI/Anthropic/Google image-generation APIs, no paid stock-photo/icon APIs, no paid font licenses, no paid hosting tier, no paid domain (the default `*.streamlit.app` subdomain is used), no third-party SaaS for storage (images are generated on demand and downloaded directly, never stored).
