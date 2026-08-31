# Property Post Maker

A chat-first web tool that turns a plain-English property description into a ready-to-share, branded real-estate advertisement poster — no design tool, no typing into a form. Built for the MLH Claude Intern practical assignment.

**Live demo:** _add your Streamlit Cloud URL here once deployed_

![Sample generated poster](template.png)

## What it does

Describe a property in your own words:

> "4 BHK, 2 stories corner villa at Golf Green Street with pool, gym, indoor-outdoor games, banquet hall and a garden, price 2.3 Cr onwards"

The assistant:
1. Extracts **property type, location, price, and highlights** from that one message — and asks a follow-up only for whatever's genuinely missing (never for location; it invents a plausible one if you don't give it).
2. Asks whether you want a **Day or Night** theme, and what **color scheme** to use — plain free-text answers, no dropdowns.
3. Writes the poster copy (headline, price line, an "About the property" paragraph, three benefit tiles) and generates a photorealistic hero photo plus three amenity photos to match your description and chosen theme/color.
4. Composites everything — your logo, the photos, the copy, a contact block — into one downloadable PNG poster.

Click the poster to enlarge it, hover for a one-click download, or just keep chatting ("make the price ₹2.8 Cr", "switch to night theme") to refine it — each refinement reuses whatever didn't change instead of regenerating from scratch.

## Features

- **Full chat interface** — one continuous conversation, not a form
- **AI-generated photography** — hero + 3 amenity photos matching the actual description, theme, and color
- **Iterative refinement** — keep chatting after generation to tweak the result with context of what was already made
- **Custom logo upload** — swap the branding logo per-session via the "+" button
- **Dark/light theme toggle**, themed scrollbar, responsive to any screen size
- **Zero paid services** — every AI call runs through [Puter.js](https://puter.com)'s free client-side SDK; no API keys, no backend, no cost to run

## Tech stack

- **Python 3 + Streamlit** — thin shell that renders one embedded HTML/JS component
- **Puter.js** — `puter.ai.chat()` for text (extraction, theme/color resolution, content planning), `puter.ai.txt2img()` for the four photos
- **HTML5 Canvas** — composites the final poster client-side, no server-side image library
- Full architecture write-up: [`docs/TRD.md`](docs/TRD.md)

## Running locally

```bash
git clone https://github.com/Dibyajyoti-07/Property-Post-Maker.git
cd Property-Post-Maker
pip install -r requirements.txt
streamlit run app.py
```

No API keys or `.env` needed — Puter.js prompts a free, one-time sign-in popup the first time it's actually needed.

## Deploying

Push to a public GitHub repo, then on [share.streamlit.io](https://share.streamlit.io): **Create app → Deploy a public app from GitHub**, pick this repo, branch `main`, main file `app.py`, **Deploy**. No secrets to configure.

## Project structure

```
app.py                  # Streamlit shell — renders the embedded component
generator_template.py   # The embedded chat UI: HTML/CSS/JS, AI calls, canvas rendering
branding.py              # Company name, address, contact, logo path, applicant credit
logo.png                 # Company logo
docs/                    # PRD, TRD, implementation plan, test cases
```

## Branding

Edit [`branding.py`](branding.py) to point this at a different company — swap `LOGO_PATH` for a different logo file and update the constants; everything else (contact block, credit line) picks it up automatically.

---

Built by Dibyajyoti Sarkar with Claude Code.
