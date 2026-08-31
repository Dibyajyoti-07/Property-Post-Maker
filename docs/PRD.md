# Product Requirements Document — Property Post Maker

## 1. Overview

Property Post Maker is a web tool that turns four short pieces of listing information into a finished, ready-to-share property advertisement poster — complete with an AI-generated photorealistic hero photo, three matching amenity photos, written copy, and the agency's logo and contact information — without the user touching a design tool or writing a single line of image-generation prompt themselves. The user types four fields, has a short back-and-forth with the assistant to pick a Day/Night theme and a color scheme, and downloads a PNG poster ready to post to WhatsApp, Instagram, or Facebook.

This tool exists to satisfy the MLH Claude Intern practical assignment: build and deploy, using Claude Code, a live tool where a user fills four fields and gets an auto-generated, branded, postable property creative — with no paid services anywhere in the stack, and a working live link produced within 24 hours of receiving the brief.

## 2. Problem

Agents and small builders currently make property posts by hand in Canva or WhatsApp-forwarded templates, which is slow, inconsistent, and easy to get wrong (missing contact info, mismatched branding, stock photos that don't match the actual property description). A tool that takes just the facts, a couple of style preferences, and produces a fully-illustrated, correctly-branded poster removes that friction entirely.

## 3. Target User

A real-estate agent, broker, or small builder/developer who lists properties and shares posts on WhatsApp groups and social media on a near-daily basis. They are not a designer and do not want to open Canva or Photoshop, or hunt for stock photography, for every listing.

## 4. The Four Input Fields — Collected Conversationally

The tool is a single continuous chat, not a form. The user describes the property in their own words, in one message or several — e.g. "a 4 bhk 2 stories corner villa at golf green street with pool and gym, indoor-outdoor games, banquet, town hall, garden and children's park, price 2.3 cr". The assistant extracts four fields from whatever was said:

| Field | Example value | Notes |
|---|---|---|
| 1 | Property & Type | "4 BHK, 2 Stories Corner Villa" — used as the poster headline and folded into the AI content-planning and photo prompts. |
| 2 | Location | "Golf Green Street, Kolkata" — if the user never states one, the assistant invents a plausible, realistic-sounding location itself rather than asking or leaving it blank (see §5a). |
| 3 | Price | "₹2.3 Cr onwards" — free-form, must render the ₹ symbol correctly. |
| 4 | Highlights | "Pool, gym, indoor-outdoor games, banquet, town hall, garden and children's park" — drives the About paragraph, the three benefit tiles, and which amenities the AI illustrates in the overview photos. |

## 4a. Missing-Field Follow-Up

If Property & Type, Price, or Highlights cannot be determined from what the user has said so far, the assistant asks specifically for just the missing ones (e.g. "Could you also tell me the price?") and re-extracts once the user replies — looping until all three are present. **Location is the one exception:** it is never asked for; if absent, the assistant silently fills in a plausible dummy location so the flow is never blocked on it.

## 5. Guided Style Questions

1. **Theme** — "Should the post use a Day or Night theme?" The user's free-text reply (e.g. "day", "let's go night mode") is resolved by the assistant to `day` or `night`; an unclear answer is re-asked once before defaulting.
2. **Color scheme** — "What color scheme should the ad use?" The user's free-text reply (e.g. "lime green", "navy and gold") is resolved to a specific accent color used throughout the poster; an unclear answer is re-asked once before defaulting.

These two answers, together with the four fields, drive everything that follows — the user never picks a template, a font, or a layout directly.

## 6. Auto-Added Elements (No User Input Required)

These appear on every generated poster automatically:

- **Layout** — one fixed poster structure (badge strip, hero + info panel, overview photo row, About section, three benefit tiles, contact block) applied automatically. The user does not arrange elements.
- **AI-generated photography** — a photorealistic hero exterior photo plus three amenity/overview photos, generated to match the property description, the chosen theme's lighting, and the chosen accent color — no stock photos, no user-supplied images.
- **Written copy** — headline, spec line, an "About the property" paragraph, and three benefit tiles with titles and descriptions, all generated from the user's own Highlights text, not generic filler.
- **Logo / brand strip** — the agency/builder's logo, placed in a consistent top-right position on every poster. Defaults to the configured company logo; the user can optionally override it per-session via a "+" button beside the chat send button, which opens a popup to upload a custom logo image used on that poster instead.
- **Contact block** — company name, manager's name, phone/WhatsApp number, and office address, so every post is immediately actionable.
- **Applicant credit** — a small, permanent credit line naming the person who built the tool, shown in the app UI, satisfying the assignment's "your name in the tool" requirement.

The user cannot remove, hide, or edit these elements from the UI — they are fixed branding and layout, which is the point: consistent, professional output every time with minimal typing.

## 7. Output

- A single generated poster image, portrait format, 1080×1527 pixels.
- Format: PNG.
- Shown as an in-page preview immediately after generation, with a download button so the user can save it and post it directly.

## 8. Out of Scope (v1)

- Multiple poster layouts/templates — v1 ships one fixed structure.
- User accounts, saved listing history, or multi-user support.
- User-uploaded property photos — v1 illustrates the property entirely via AI-generated imagery from the description.
- Editing branding from the UI — branding (logo, contact, company name) is configured once by the tool owner via `branding.py`, not per-post by the end user.
- Retrying/regenerating individual photos independently — a failed image call is retried once automatically; there is no manual "regenerate this photo" control.

## 9. Success Criteria

- The generated poster visually reads as a real, professional, postable creative — matching the visual bar of the reference example (a Merlin-branded "Luxury Corner Villa" poster) — not a rough placeholder.
- All four user-entered fields, both style answers, and all auto-added brand/photo elements appear correctly on every generation, with no missing elements or broken layout at typical input lengths.
- The tool is live at a public URL, reachable by anyone, with zero paid services or API keys required to run it (AI generation runs through Puter.js's free, client-side, no-API-key model).
- Delivered within the assignment's 24-hour window: live link, one sample generated post, a 1-minute recording of it being built with Claude Code, and the applicant's name visible in the tool.
