# Test Cases — Property Post Maker

## 1. Manual UI Test Cases

| ID | Case | Steps | Expected Result |
|---|---|---|---|
| UI-01 | All fields empty, submit | Leave all four fields blank, click Continue | Generation is blocked; inline error(s) identify which field(s) are missing. No chat step starts. |
| UI-02 | One field empty | Fill three fields, leave one (e.g. Highlights) blank, click Continue | Generation is blocked; error identifies the missing field specifically. |
| UI-03 | Typical/happy path | Fill all four fields with realistic values, answer "Day" then "lime green" in the chat | Two chat calls resolve immediately; content-planning call returns a full plan; four photos generate sequentially with status text; final 1080×1527 PNG poster matches the fields entered. **Verified 2026-08-31**: ran end-to-end via the villa example from the assignment brief — passed. |
| UI-03b | Ambiguous theme/color answer | Answer the theme question with something unresolvable (e.g. "maybe") | The bot re-asks once instead of guessing; a second unclear answer defaults to Day rather than hanging. Same for color. |
| UI-04 | Long Property & Type text | Enter a headline well beyond ~60 characters | Headline wraps inside its panel; no overflow past the card edge. |
| UI-05 | Long Highlights text | Enter 6+ highlight items | About paragraph and benefit tiles still fit their boxes; text wraps rather than overflowing. |
| UI-06 | ₹ symbol rendering | Enter Price with "₹2.3 Cr onwards" | ₹ glyph renders correctly on the canvas. |
| UI-07 | Emoji / unicode in input | Enter an emoji or non-Latin character in any field | App does not crash; the `</script>`-safe JSON embedding (generator_template._safe_json) prevents any input from breaking the embedded script tag. |
| UI-09 | Re-generate with new inputs | Reload the page, submit different field values | New chat session starts fresh; no state leaks from a prior generation (page reload creates a new Streamlit session). |
| UI-10 | Download | After a successful generation, click the download button | A `.png` file downloads with a filename derived from the property text; opens correctly; matches the on-screen preview. |

## 2. Auto-Added Elements Verification

| ID | Case | Expected Result |
|---|---|---|
| AUTO-01 | Logo present | Every generated poster shows the Merlin logo top-right of the badge strip — never missing, never user-removable from the UI. |
| AUTO-02 | Contact line present | Every generated poster shows the Get In Touch block with company name, manager name, phone, and address — never missing, never editable from the form. |
| AUTO-03 | No manual layout/style controls exposed | The UI exposes only the four content fields plus the two free-text style questions — no color picker, font picker, or logo upload widget is present. |
| AUTO-04 | Applicant credit visible | The app UI shows the applicant's build-credit caption under the title, and the poster's own bottom-left corner also carries a small credit line. |

## 3. Image Output Tests

| ID | Case | Expected Result |
|---|---|---|
| IMG-01 | Dimensions | Generated poster is exactly 1080×1527 pixels (`img.naturalWidth`/`naturalHeight`). |
| IMG-02 | Format validity | The download link's `href` starts with `data:image/png` and the `<img>` preview loads it successfully. |
| IMG-03 | Photo/box aspect handling | Hero and thumbnail photos, whatever aspect ratio the AI model returns, fill their boxes via `drawCover`'s manual center-crop without visible distortion or letterboxing. |
| IMG-04 | No clipping/overlap at edge-case lengths | For long-Highlights inputs, the About paragraph and benefit-tile text wrap rather than overlapping the section below. |
| IMG-05 | Filename on download | Downloaded file's filename is derived from Property & Type, lowercased and hyphenated (not generic/empty). |

## 4. AI Pipeline & Puter.js-Specific Tests

| ID | Case | Expected Result |
|---|---|---|
| AI-01 | Theme resolution | A clear "day"/"night" answer resolves in one round-trip; the model is instructed to return strict JSON and the client strips markdown fences before `JSON.parse`. |
| AI-02 | Color resolution | A clear color answer (name or hex) resolves to a valid `#RRGGBB`; an invalid/unresolvable hex from the model is rejected by the `/^#[0-9a-fA-F]{6}$/` check and triggers a re-ask, not a broken canvas fill. |
| AI-03 | Content-planning JSON | The planning prompt gives the model a concrete example (not literal placeholders like "...") so it fills in real derived values — **regression case**: an earlier prompt version caused the model to literally echo back `"LUXURY ... FOR SALE"` instead of substituting the property type; fixed by replacing the example with a concrete, non-ellipsis sample. |
| AI-04 | Image model reliability | `puter.ai.txt2img` is called with an explicit `{model: 'gpt-image-1'}` — Puter's default model currently errors with "Missing `model`", and Replicate-routed FLUX models returned intermittent 400s ("Too many concurrent requests", "Failed to extract image URL from Replicate response") during development. Re-test if this model is deprecated. |
| AI-05 | Sequential image generation | The four `txt2img` calls run sequentially (not `Promise.all`) with a status label per call — confirmed necessary because parallel calls triggered a "Too many concurrent requests" error on the free tier. |
| AI-06 | One retry on failure | A single injected `txt2img`/`chat` failure is retried once automatically (2s backoff) before surfacing a user-facing error bubble. |
| AI-07 | First-run Puter auth | On a visitor's very first AI call, Puter may show a one-time sign-in popup; generation resumes correctly once signed in. Not required for every session — anonymous/previously-authed sessions proceed without it. |

## 5. Known Placeholders (not test failures)

- Contact block phone/manager name are still `branding.py` placeholders (`+91-XXXXXXXXXX` / "Merlin Sales Team") pending real values.
- Applicant credit name is inferred as "Dibyajyoti Sarkar" from the project owner's email, pending confirmation.

## 6. Deployment Smoke Test

| ID | Case | Steps | Expected Result |
|---|---|---|---|
| DEPLOY-01 | Live URL loads | Open the `*.streamlit.app` URL in a fresh/incognito browser session | App loads fully, form is visible, no error banners. |
| DEPLOY-02 | Full generate cycle on live instance | On the live URL, fill all four fields and generate | Image previews correctly, matching local-run behavior. |
| DEPLOY-03 | Download on live instance | Click download on the live URL | PNG downloads successfully from the deployed instance, not just localhost. |
| DEPLOY-04 | Fresh session isolation | Open the live URL in a second, separate browser session and generate a different post | Second session's output is independent and correct — no leaked state from the first session. |
| DEPLOY-05 | Cold start | Reload the live URL after a period of inactivity (Streamlit Community Cloud free-tier apps can sleep) | App wakes and loads within a reasonable time, with no broken assets (fonts/logo still load correctly after a cold start). |

## 7. Exit Criteria

All UI, AUTO, and IMG manual cases pass by visual inspection; all UT automated tests pass (`pytest` green); all DEPLOY smoke tests pass against the actual live URL before it is submitted as the assignment's deliverable link.
