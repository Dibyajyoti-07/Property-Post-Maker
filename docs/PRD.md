# Product Requirements Document — Property Post Maker

## 1. Overview

Property Post Maker is a single-page web tool that lets a real-estate agent or builder turn four short pieces of listing information into a finished, ready-to-share property post — a designed square image carrying the listing details plus the agency's logo and contact information — without touching a design tool. The user types four fields, clicks generate, and downloads a PNG they can post directly to WhatsApp, Instagram, or Facebook.

This tool exists to satisfy the MLH Claude Intern practical assignment: build and deploy, using Claude Code, a live tool where a user fills four fields and gets an auto-generated, branded, postable property creative — with no paid services anywhere in the stack, and a working live link produced within 24 hours of receiving the brief.

## 2. Problem

Agents and small builders currently make property posts by hand in Canva or WhatsApp-forwarded templates, which is slow, inconsistent, and easy to get wrong (missing contact info, mismatched branding, typos carried over from copy-paste). A tool that takes just the facts and produces a consistent, correctly-branded post removes that friction entirely.

## 3. Target User

A real-estate agent, broker, or small builder/developer who lists properties and shares posts on WhatsApp groups and social media on a near-daily basis. They are not a designer and do not want to open Canva or Photoshop for every listing; they want to type a few facts and get something postable in seconds.

## 4. The Four Input Fields

These are the only fields the user fills in. All four are on one form, all four are required — the app will not generate a post with any of them empty, since a partial post is not a "ready-to-share" post.

| Field | Label shown in UI | Example value | Notes |
|---|---|---|---|
| 1 | Property & Type | "4 BHK Luxury Villa, Ansal Golf City" | Free text. Recommended max length ~60 characters so it fits the headline area without shrinking below a readable size; longer input is allowed but will wrap and may auto-shrink to fit. |
| 2 | Location | "Sushant Golf City, Lucknow" | Free text, shown as a secondary line under the headline. |
| 3 | Price | "₹2.5 Cr onwards" | Free text (not a strict number field) so the user can express ranges, "onwards", "negotiable", etc. Must render the ₹ symbol correctly. |
| 4 | Highlights | "3000 sq.ft · Corner plot · Ready to move" | Free text, expected to be a short list of highlights separated by any delimiter the user likes (·, comma, |). Rendered as a compact highlights row/strip near the bottom of the card, above the contact strip. |

Validation: all four fields required (empty submit is blocked with an inline message telling the user which field is missing). No format enforcement beyond required + a soft max length warning, since real listings vary too much for rigid parsing.

## 5. Auto-Added Elements (No User Input Required)

These appear on every generated post automatically — the user never types or configures them:

- **Layout & background** — one clean, pre-designed template (color palette, spacing, typography) applied automatically to whatever text is entered. The user does not pick colors, fonts, or arrange elements.
- **Logo / brand strip** — the agency/builder's logo, placed in a consistent position (top strip) on every post.
- **Contact line** — a fixed strip (typically bottom of the card) carrying the builder/company name, manager's name, phone/WhatsApp number, and office address, so every post is immediately actionable by whoever sees it.
- **Applicant credit** — per the assignment's requirement that the tool carry "your name," the app UI itself (not necessarily the generated image) shows a small, permanent credit line naming the person who built the tool.

The user cannot remove, hide, or edit these elements from the UI in v1 — they are fixed branding, which is the point: consistent output every time with zero extra typing.

## 6. Output

- A single generated image, square format, 1080×1080 pixels (matches Instagram/Facebook post dimensions).
- Format: PNG (lossless, universally supported, transparent-background-safe if ever needed later).
- Shown as an in-page preview immediately after generation, with a download button so the user can save it and post it directly — no email, no account, no extra step.

## 7. Out of Scope (v1)

- Multiple template/style choices — v1 ships one clean template, not a picker.
- User accounts, saved listing history, or multi-user support.
- Property photo upload/compositing into the card — v1 uses text + logo + brand elements only, no property photography.
- Multiple output sizes (portrait/story formats) — v1 is square only.
- Multi-language support — v1 is English/number-locale as typed by the user.
- Editing branding from the UI — branding (logo, contact, company name) is configured once by the tool owner, not per-post by the end user.

## 8. Success Criteria

- The generated post visually reads as a real, professional, postable creative — not a rough placeholder — matching the assignment's explicit "clean, postable creative" bar.
- All four user-entered fields and all three auto-added brand elements (logo, contact line, applicant credit) appear correctly on every single generation, with no missing or overlapping elements at typical input lengths.
- The tool is live at a public URL, reachable by anyone, with zero paid services or API keys required to run it.
- Delivered within the assignment's 24-hour window: live link, one sample generated post, a 1-minute recording of it being built with Claude Code, and the applicant's name visible in the tool.
