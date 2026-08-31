# Implementation Plan — Property Post Maker

This plan sequences the Puter.js-based build against the assignment's 24-hour deadline. It supersedes an earlier Pillow/static-card plan, abandoned once the brief was clarified to require AI-generated photography and a free-text theme/color chat step matching a specific visual reference (`template.png`).

## Phase 1 — Scaffold ✅ done

1. `branding.py` — company name, address (real), manager name/phone (placeholders), logo path, applicant credit (inferred placeholder name).
2. `logo.png` in repo root (Merlin logo, supplied by user).
3. `requirements.txt` — `streamlit` only; no Pillow needed for the live path.

## Phase 2 — Component + form ✅ done

4. `generator_template.py` — `encode_logo()` (base64-inlines the logo, since the embedded component runs in a sandboxed `srcdoc` iframe with no file-path access) and `build_component_html()` (builds the full embedded chat + AI + canvas HTML/JS, with `_safe_json` escaping `</script>` in user text before interpolation).
5. `app.py` — 4-field Streamlit form with required validation, then `st.components.v1.html(...)` renders the component on submit.

## Phase 3 — Local QA and debugging ✅ done

6. Ran the full flow in a real browser (via claude-in-chrome) with the assignment's own villa example. Found and fixed three real bugs along the way, each confirmed against actual API responses (network requests inspected), not guessed:
   - Puter's default `txt2img` model errors ("Missing `model`") — fixed by passing an explicit `{model: 'gpt-image-1'}`.
   - Firing all 4 image calls in parallel (`Promise.all`) hit "Too many concurrent requests" on the free tier — fixed by running them sequentially with per-call status text.
   - The content-planning prompt's JSON example used a literal `"..."` placeholder for `badge_text`, which the model echoed back verbatim instead of substituting real content — fixed by giving a concrete, non-ellipsis example value.
   - A Python module-caching gotcha: editing `generator_template.py` had no effect on a running `streamlit run` process because `app.py`'s top-level `import` only re-resolves at process start, not on Streamlit's file-watcher rerun — fixed by restarting the server after each code change during testing.
7. Confirmed after the fixes: theme/color chat resolves correctly (including the re-ask path on an ambiguous first pass, tested separately), all 4 photos generate, final poster is 1080×1527 valid PNG, download link has a sensible filename, layout matches `template.png`'s structure (badge strip + logo, hero + colored info panel, 3 overview thumbnails, About paragraph, 3 benefit tiles, contact block, credit line).

## Phase 4 — Automated tests — not yet done

8. No `tests/` directory exists yet. Given the generation logic is entirely client-side JS with no Python unit under test, the practical equivalent is the browser-driven manual pass already completed in Phase 3; a formal automated test suite (e.g. Playwright driving the Streamlit page) is future work, not required for this assignment's deliverables.

## Phase 5 — Docs ✅ done

9. `docs/PRD.md`, `docs/TRD.md`, `docs/TESTCASES.md`, and this file rewritten to describe the actual Puter.js/chat/canvas architecture in place of the superseded Pillow-card plan.

## Phase 6 — Deploy — pending user action

10. **Git commit + push** to the existing `origin/main` (`github.com/Dibyajyoti-07/Property-Post-Maker.git`) — done as part of this session once the working tree is verified clean of anything unintended.
11. **Streamlit Community Cloud connection** — this step requires the account owner's own browser session (OAuth sign-in to share.streamlit.io, connecting the GitHub repo) and cannot be done by an agent on the user's behalf. Once connected with `app.py` as the entry point, every push to `main` auto-redeploys.

## Phase 7 — Remaining blockers before final submission

12. **Real branding values.** `MANAGER_NAME` and `PHONE` in `branding.py` are still placeholders — swap in the real manager name and phone/WhatsApp number, commit, push (single-line edit, auto-redeploys).
13. **Applicant credit name.** Currently inferred as "Dibyajyoti Sarkar" from the project owner's email — confirm this is correct.
14. **Sample post.** Once live, generate one sample post from the actual deployed URL (not just localhost) and save it as the assignment's required sample.
15. **1-minute build recording** and the final reply (live link + sample post + recording + name-in-tool) are on the user to complete outside this codebase.
