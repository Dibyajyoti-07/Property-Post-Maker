# Implementation Plan — Property Post Maker

This plan sequences the build described in the PRD and TRD against the assignment's 24-hour deadline. Steps 1–8 need no external input and can run back-to-back in one session. Steps 9–10 need real branding assets and the applicant's display name from the user — everything is designed so that gap doesn't block getting a live, demoable link first.

## Phase 1 — Scaffold (no blocking input)

1. **Repo scaffold.** Create the file/folder layout from the TRD: `app.py`, `card_generator.py`, `branding.py`, `requirements.txt`, `assets/fonts/`, `assets/logo.png` (placeholder), `tests/`. Initialize a git repo in the project directory.
2. **Branding config with placeholders.** Write `branding.py` with clearly-labeled placeholder constants (company name, manager name, phone, address, logo path, applicant credit placeholder) so every later step has something concrete to render against.
3. **Fonts.** Download or generate two OFL-licensed `.ttf` files (bold + regular weight of one family, e.g. Poppins) into `assets/fonts/`, committed to the repo.

## Phase 2 — Core image logic (no blocking input)

4. **`card_generator.py`.** Implement `generate_post(property_type, location, price, highlights)`:
   - fixed 1080×1080 canvas + background fill,
   - headline + location text drawing with wrapping and auto-shrink-to-fit,
   - price zone,
   - highlights row (split on `·`/`,`/`|`, wrap into a compact block),
   - logo paste into a fixed top brand strip (reads `branding.LOGO_PATH`),
   - fixed bottom contact strip using `branding.py` constants,
   - return PNG bytes via in-memory buffer (no disk writes).
5. Sanity-check the function directly (a throwaway script or Python REPL call) with the assignment's own example values (villa/location/price/highlights from the brief) before wiring up the UI, so any layout issues are caught before the UI is built on top of it.

## Phase 3 — UI wiring (no blocking input)

6. **`app.py`.** Build the Streamlit form: four inputs, submit button, required-field validation with inline errors, call into `card_generator.generate_post`, `st.image` preview, `st.download_button` for the PNG, and a small always-visible footer line for the applicant credit (placeholder text until the real name is supplied).
7. **Local run + manual QA.** `streamlit run app.py` locally; walk through the manual test cases in `TESTCASES.md` (empty fields, long text, ₹ symbol, emoji, typical example) and fix any layout issues found.

## Phase 4 — Automated tests

8. **`tests/test_card_generator.py`.** Pytest cases covering: output image has the expected 1080×1080 size and PNG-decodable bytes for a normal input; the function does not raise for edge-case inputs (very long highlights string, empty-ish but non-empty single character, unicode/₹/emoji). Run the suite and confirm it's green before deploying.

## Phase 5 — Deploy (no blocking input)

9. **GitHub.** Create a public GitHub repository, push the committed code (placeholders included — nothing here is secret, so it's safe to commit and push as-is).
10. **Streamlit Community Cloud.** Connect the GitHub repo at share.streamlit.io, set `app.py` as the entry point, deploy. Confirm the live `*.streamlit.app` URL loads and a full generate → preview → download cycle works end to end on the deployed instance (not just locally).

## Phase 6 — Real branding + deliverables (blocked on user input)

11. **Swap real branding.** Once the user supplies manager name, phone/WhatsApp, logo file, builder/company name, office address, and their own display name for the applicant credit: update `branding.py` and replace `assets/logo.png`, commit, push — Streamlit Community Cloud auto-redeploys on push, so this is a single fast iteration, not a rebuild.
12. **Sample post.** Generate and save the one required sample post from the live deployed tool (not a local-only run), using realistic example values (e.g. the brief's own villa example or a real listing the user provides).
13. **1-minute build recording.** Record a concise walkthrough of building this with Claude Code, per the assignment's requirement.
14. **Final submission check.** Confirm all four deliverables are ready together: live link, one sample post image, the recording, and the applicant's name visibly present in the running tool.

## Rough time budget (24h window)

- Phases 1–5 (scaffold through live deploy, placeholder branding): the bulk of engineering time, targeted for the first working session — this alone produces a live, fully functional link.
- Phase 6: fast once real assets arrive (single config/asset swap + redeploy), but is entirely gated on the user providing those assets — flagging this early so it isn't the thing that runs the clock down near the deadline.
