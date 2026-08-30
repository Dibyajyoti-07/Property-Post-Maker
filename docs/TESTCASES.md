# Test Cases — Property Post Maker

## 1. Manual UI Test Cases

| ID | Case | Steps | Expected Result |
|---|---|---|---|
| UI-01 | All fields empty, submit | Leave all four fields blank, click Generate | Generation is blocked; inline error(s) identify which field(s) are missing. No image is produced. |
| UI-02 | One field empty | Fill three fields, leave one (e.g. Highlights) blank, click Generate | Generation is blocked; error identifies the missing field specifically. |
| UI-03 | Typical/happy path | Fill all four fields with the assignment's example values ("4 BHK Luxury Villa, Ansal Golf City" / "Sushant Golf City, Lucknow" / "₹2.5 Cr onwards" / "3000 sq.ft · Corner plot · Ready to move") | A 1080×1080 PNG is generated and previewed; all four values are legible and correctly placed; logo and contact strip are present. |
| UI-04 | Long Property & Type text | Enter a headline well beyond ~60 characters | Text wraps and/or auto-shrinks to stay inside its box; no overflow past the card edge; no overlap with the location line below it. |
| UI-05 | Long Highlights text | Enter 6+ highlight items separated by `·` | Highlights row wraps to multiple lines/rows as needed; does not overlap the contact strip beneath it. |
| UI-06 | ₹ symbol rendering | Enter Price with "₹2.5 Cr onwards" | ₹ glyph renders correctly (not a missing-glyph box) using the bundled font. |
| UI-07 | Emoji / unicode in input | Enter an emoji or non-Latin character in any field | App does not crash; character either renders (if font supports it) or degrades gracefully without breaking layout of surrounding text. |
| UI-08 | Delimiter variety in Highlights | Test Highlights with `,` and `|` delimiters instead of `·` | Highlights still split and lay out into a readable row/block regardless of which delimiter was used. |
| UI-09 | Re-generate with new inputs | Generate once, change one field, generate again | New image reflects only the updated field; old preview is fully replaced, not stacked/duplicated. |
| UI-10 | Download | After a successful generation, click the download button | A `.png` file downloads, opens correctly in a standard image viewer, matches the on-screen preview exactly. |

## 2. Auto-Added Elements Verification

| ID | Case | Expected Result |
|---|---|---|
| AUTO-01 | Logo present | Every generated image (across UI-03 through UI-09) shows the configured logo in the same fixed top-strip position — never missing, never user-removable from the UI. |
| AUTO-02 | Contact line present | Every generated image shows the fixed bottom contact strip with company name, manager name, phone/WhatsApp, and address — never missing, never editable from the form. |
| AUTO-03 | No manual layout controls exposed | The UI exposes only the four content fields — no color picker, font picker, logo upload, or contact-info fields are present, confirming branding is fully automatic per the PRD. |
| AUTO-04 | Applicant credit visible | The app UI (outside the generated image) always shows the applicant's build-credit footer line, satisfying "your name in the tool." |

## 3. Image Output Tests

| ID | Case | Expected Result |
|---|---|---|
| IMG-01 | Dimensions | Generated image is exactly 1080×1080 pixels. |
| IMG-02 | Format validity | Output bytes decode as a valid PNG (openable by Pillow/any standard viewer without error). |
| IMG-03 | No clipping/overlap at typical lengths | For the example values in UI-03, no text element visually overlaps another element or the logo/contact strip. |
| IMG-04 | No clipping/overlap at edge-case lengths | For the long-text cases (UI-04, UI-05), text wrapping/shrinking keeps all elements inside the canvas and non-overlapping. |
| IMG-05 | Filename on download | Downloaded file has a sensible, non-empty filename derived from the listing (not a generic/empty name). |

## 4. Automated Unit Tests (`tests/test_card_generator.py`, pytest)

| ID | Test | Assertion |
|---|---|---|
| UT-01 | `test_output_size` | Calling `generate_post` with normal example inputs returns bytes that decode (via Pillow) to an image of size exactly (1080, 1080). |
| UT-02 | `test_output_is_valid_png` | Returned bytes, opened with `PIL.Image.open`, have `format == "PNG"`. |
| UT-03 | `test_long_highlights_does_not_raise` | Calling `generate_post` with a Highlights string far longer than typical (e.g. 300+ characters) completes without raising an exception. |
| UT-04 | `test_unicode_and_currency_symbol` | Calling `generate_post` with `₹` and an emoji embedded in the input strings completes without raising an exception. |
| UT-05 | `test_missing_logo_file_handled` | If `branding.LOGO_PATH` points to a missing file, `generate_post` either raises a clear, specific error or falls back gracefully — behavior is deliberate, not an unhandled crash (guards against a broken deploy if the logo asset is ever missing). |
| UT-06 | `test_deterministic_output` | Calling `generate_post` twice with identical inputs produces byte-identical (or pixel-identical) output, confirming no hidden randomness/state. |

## 5. Deployment Smoke Test

| ID | Case | Steps | Expected Result |
|---|---|---|---|
| DEPLOY-01 | Live URL loads | Open the `*.streamlit.app` URL in a fresh/incognito browser session | App loads fully, form is visible, no error banners. |
| DEPLOY-02 | Full generate cycle on live instance | On the live URL, fill all four fields and generate | Image previews correctly, matching local-run behavior. |
| DEPLOY-03 | Download on live instance | Click download on the live URL | PNG downloads successfully from the deployed instance, not just localhost. |
| DEPLOY-04 | Fresh session isolation | Open the live URL in a second, separate browser session and generate a different post | Second session's output is independent and correct — no leaked state from the first session. |
| DEPLOY-05 | Cold start | Reload the live URL after a period of inactivity (Streamlit Community Cloud free-tier apps can sleep) | App wakes and loads within a reasonable time, with no broken assets (fonts/logo still load correctly after a cold start). |

## 6. Exit Criteria

All UI, AUTO, and IMG manual cases pass by visual inspection; all UT automated tests pass (`pytest` green); all DEPLOY smoke tests pass against the actual live URL before it is submitted as the assignment's deliverable link.
