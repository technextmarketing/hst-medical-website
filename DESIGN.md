---
name: HST Medical
description: A clean online-pharmacy shopfront in the logo's own colours, magenta, slate and white, where every product sits in a grey well with its name, its use and the real price for the pack you chose.
colors:
  bg: "#ffffff"
  surface: "#f4f6f8"
  surface-2: "#e9edf1"
  line: "#e5e9ee"
  line-2: "#d3dae2"
  ink: "#1f2933"
  slate: "#3d4a57"
  slate-deep: "#2b3640"
  ink-2: "#4b5563"
  muted: "#6b7280"
  brand: "#dd1860"
  brand-deep: "#b3124c"
  brand-ink: "#a8114a"
  brand-tint: "#fdeef3"
  brand-tint-2: "#fbdce6"
  on-brand: "#ffffff"
  on-brand-2: "#ffd6e3"
  mint: "#e6f4ec"
  gold-ink: "#7f6133"
  green-ink: "#226826"
  error: "#b42318"
typography:
  display:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2.1rem, 1.3rem + 3vw, 3.8rem)"
    fontWeight: 700
    lineHeight: 1.08
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(1.5rem, 1.15rem + 1.3vw, 2.1rem)"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.015em"
  title:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.35rem"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.015em"
  subtitle:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "0"
  lead:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.12rem"
    fontWeight: 400
    lineHeight: 1.6
  body:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.6
    fontFeature: "tabular-nums"
  small:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.9rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.82rem"
    fontWeight: 600
    lineHeight: 1.3
  price:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.9rem"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.02em"
    fontFeature: "tabular-nums"
  watermark:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(5rem, 16vw, 15rem)"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.04em"
rounded:
  block: "20px"
  panel: "14px"
  control: "10px"
  pill: "999px"
spacing:
  gutter: "clamp(16px, 2.5vw, 32px)"
  band: "clamp(2.5rem, 5vw, 4.5rem)"
  hero: "clamp(1.5rem, 4vw, 3.5rem)"
  panel: "1.5rem"
  stack: "1rem"
  flow: "0.5rem"
  chip-gap: "0.5rem"
components:
  button-default:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0.65rem 1.3rem"
    height: "46px"
  button-default-hover:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
  button-primary:
    backgroundColor: "{colors.brand}"
    textColor: "{colors.on-brand}"
    rounded: "{rounded.pill}"
    padding: "0.65rem 1.3rem"
    height: "46px"
  button-primary-hover:
    backgroundColor: "{colors.brand-deep}"
    textColor: "{colors.on-brand}"
  button-dark:
    backgroundColor: "{colors.slate}"
    textColor: "{colors.on-brand}"
    rounded: "{rounded.pill}"
    padding: "0.65rem 1.3rem"
    height: "46px"
  button-dark-hover:
    backgroundColor: "{colors.slate-deep}"
    textColor: "{colors.on-brand}"
  button-light:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.brand-ink}"
    rounded: "{rounded.pill}"
    padding: "0.65rem 1.3rem"
    height: "46px"
  button-light-hover:
    backgroundColor: "{colors.brand-tint}"
    textColor: "{colors.brand-ink}"
  button-ghost:
    textColor: "{colors.on-brand}"
    rounded: "{rounded.pill}"
    padding: "0.65rem 1.3rem"
    height: "46px"
  button-quiet:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0.65rem 1.3rem"
    height: "46px"
  button-quiet-hover:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.ink}"
  button-small:
    rounded: "{rounded.pill}"
    padding: "0.5rem 1rem"
    height: "44px"
  button-added:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-brand}"
    rounded: "{rounded.pill}"
  chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0.5rem 1rem"
    height: "44px"
  chip-hover:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.ink}"
  chip-stamped:
    backgroundColor: "{colors.brand-tint}"
    textColor: "{colors.brand-ink}"
    rounded: "{rounded.pill}"
  chip-stamped-hover:
    backgroundColor: "{colors.brand-tint-2}"
    textColor: "{colors.brand-ink}"
  chip-pressed:
    backgroundColor: "{colors.slate}"
    textColor: "{colors.on-brand}"
    rounded: "{rounded.pill}"
    padding: "0.4rem 0.9rem"
    height: "44px"
  header-band:
    backgroundColor: "{colors.brand-deep}"
    padding: "0.9rem {spacing.gutter} 0"
  header-bar:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0.4rem 0.5rem 0.4rem 1.1rem"
    height: "68px"
  header-search:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0 0.5rem 0 0.9rem"
    height: "44px"
    width: "200px to 300px"
  nav-link:
    textColor: "{colors.ink-2}"
    rounded: "{rounded.pill}"
    padding: "0.55rem 0.7rem"
  nav-link-hover:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
  nav-link-active:
    backgroundColor: "{colors.brand-tint}"
    textColor: "{colors.brand-ink}"
  bag-pill:
    backgroundColor: "{colors.brand}"
    textColor: "{colors.on-brand}"
    rounded: "{rounded.pill}"
    padding: "0.4rem 1rem"
    height: "46px"
  bag-pill-hover:
    backgroundColor: "{colors.brand-deep}"
    textColor: "{colors.on-brand}"
  bag-count:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.brand-ink}"
    rounded: "{rounded.pill}"
    size: "1.4rem"
  hero-block:
    backgroundColor: "{colors.brand-deep}"
    textColor: "{colors.on-brand}"
    rounded: "0 0 {rounded.block} {rounded.block}"
    padding: "{spacing.hero} 0 clamp(2rem, 5vw, 4rem)"
    height: "min(560px, 70vh)"
  hero-pack-card:
    backgroundColor: "{colors.bg}"
    rounded: "{rounded.block}"
    padding: "4%"
    width: "min(100%, 420px)"
  hero-float-card:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "0.75rem 0.9rem 0.75rem 0.75rem"
    width: "260px"
  hero-float-go:
    backgroundColor: "{colors.brand-tint}"
    textColor: "{colors.brand-ink}"
    rounded: "{rounded.pill}"
    size: "36px"
  counter-tile:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "14%"
  counter-tile-hover:
    backgroundColor: "{colors.surface-2}"
  counter-stamp:
    backgroundColor: "{colors.brand-tint}"
    textColor: "{colors.brand-ink}"
    rounded: "{rounded.pill}"
    padding: "0.2rem 0.6rem"
  strip:
    backgroundColor: "{colors.slate-deep}"
    textColor: "{colors.on-brand}"
    padding: "0.8rem {spacing.gutter}"
  panel:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "{spacing.panel}"
  panel-head:
    textColor: "{colors.muted}"
    typography: "{typography.small}"
    padding: "0.75rem 1.5rem"
  product-card:
    textColor: "{colors.ink}"
    padding: "0.9rem 0.25rem 0.4rem"
  product-card-image-well:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.panel}"
    padding: "1.25rem"
  product-card-button:
    backgroundColor: "{colors.slate}"
    textColor: "{colors.on-brand}"
    rounded: "{rounded.pill}"
    padding: "0.5rem 1rem"
    height: "44px"
  compare-thumb:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.control}"
    padding: "6px"
    size: "72px"
  band-brand:
    backgroundColor: "{colors.brand-deep}"
    textColor: "{colors.on-brand}"
    padding: "{spacing.band} {spacing.gutter}"
  fact-card:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "1.4rem 1.5rem"
  brand-chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0.6rem 1.1rem"
  shelf-tile:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "1.1rem 1.1rem 1rem"
    height: "120px"
  shelf-tile-pain:
    backgroundColor: "{colors.brand-tint}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
  pack-tile:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0.55rem 0.9rem 0.55rem 2.3rem"
    height: "56px"
  pack-tile-checked:
    backgroundColor: "{colors.brand-tint}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
  pack-tile-disabled:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.muted}"
  pdp-pack-well:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.panel} 0 0 {rounded.panel}"
    padding: "clamp(1rem, 3vw, 2.5rem)"
  input:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0.6rem 0.9rem"
    height: "46px"
  input-search:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0.5rem 1.1rem"
    height: "46px"
  qty-stepper:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    height: "46px"
  caution-note:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.control}"
    padding: "0.85rem 1rem"
    typography: "{typography.small}"
  success-note:
    backgroundColor: "{colors.brand-tint}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "1rem 1.25rem"
  empty-state:
    textColor: "{colors.ink-2}"
    rounded: "{rounded.panel}"
    padding: "2rem 1.5rem"
  toast:
    backgroundColor: "{colors.slate-deep}"
    textColor: "{colors.on-brand}"
    rounded: "{rounded.control}"
    padding: "0.8rem 1.1rem"
  meter-track:
    backgroundColor: "{colors.surface-2}"
    rounded: "{rounded.pill}"
    height: "6px"
  meter-fill:
    backgroundColor: "{colors.brand}"
    rounded: "{rounded.pill}"
  step-number:
    backgroundColor: "{colors.brand-tint}"
    textColor: "{colors.brand-ink}"
    rounded: "{rounded.pill}"
    size: "2rem"
  proto-notice:
    backgroundColor: "{colors.slate-deep}"
    textColor: "{colors.on-brand-2}"
    padding: "0.45rem {spacing.gutter}"
  footer:
    backgroundColor: "{colors.slate-deep}"
    textColor: "{colors.on-brand}"
    padding: "3rem {spacing.gutter} 1.25rem"
---

# Design System: HST Medical

## Overview

**Creative North Star: "The Pharmacy Shopfront in the Logo's Colours"**

HST Medical is the modern online-pharmacy shopfront the client pointed at (MediHeal / Pharmico style) rebuilt in the three colours already on the pack: the logo's magenta, the wordmark's slate and white. The page opens on a deep magenta block with rounded bottom corners; a white pill-shaped header floats on it carrying the logo, the need links, a grey search field and a magenta Bag. The headline is white on magenta, the first action is a white pill, the second an outline, and the Rheuma-Salve jar stands on a white rounded card with a small floating product card beside it. Everything below the block returns to white: six shop-by-need tiles whose packshots sit in light grey wells, a thin slate strip of benefits, product cards in grey wells with slate pill buttons, compare tables inside white panels on grey bands, one more magenta band of white fact cards, and a slate footer.

One typeface, Archivo, carries the whole site at five weights (400 to 800; 800 only for the faint "RELIEF" watermark). The colour roles are strict: magenta owns the hero block and exactly one lower band and otherwise appears only on the active element (the Bag, the primary Add to bag, the active nav pill, the checked pack tile, the checkout step bar, the free-delivery meter). Slate owns every dark control that is not the one primary action (product-card buttons, the pressed filter chip, the trade button) and the dark surfaces (strip, prototype notice, toast, footer). Light grey carries every product image, so packs photographed on white sit in the page without a cut-out edge (mix-blend-mode: multiply). The Rheuma-Salve mint survives only as a reserved token.

The structural model is unchanged: start-by-need tiles directly under the hero, compare tables before any product grid, honest pack sizes with real prices and item codes, a bag that counts, and a three-step gated checkout. Imagery is product photography only: no stock photos of people (none exist), no testimonials (none exist), no carousels. Motion is one authored moment (the pack-size reprint) plus short hover lifts, no scroll-reveal, no animation library. This rendition replaced the lighter "White Dispensing Counter" on 2026-10-02 at the client's request for the template look in the logo's colours.

**Key Characteristics:**
- Deep magenta (#b3124c) hero block with 20px rounded bottom corners and a white floating pill header; white ground below with light grey (#f4f6f8) wells and bands
- Palette is the logo's: magenta in three strengths plus two tints, the wordmark slate (#3d4a57 / #2b3640), white, two near-white greys and three inks
- Archivo only, weights 400/500/600/700/800, 17px body, tabular numerals, no eyebrows or kickers
- Four radii by role: 20px hero block and pack card, 14px panels, tiles and wells, 10px controls and thumbnails, pill for everything you press
- Every product image on a grey well, multiply-blended; cards have no border and no shadow, only the well
- Magenta for the hero, one band and the active element; slate for dark controls, strip, toast and footer
- Start-by-need tiles, compare-first categories, honest pack sizes, gated three-step checkout
- One authored motion (pack-size reprint) plus 3px hover lifts; reduced-motion keeps every state change
- Portable to a GeneratePress child theme and WP EasyCart CSS overrides

## Colors

The logo's palette and nothing else: magenta as a field, an action fill and an ink; slate as the dark neutral; white; two cool greys for wells and rules; three text inks; two range inks; one error. Twenty-one tokens on `:root`.

### Primary
- **Hero Magenta** (`brand-deep`, #b3124c): the deep field. The header band, the hero block, the "Dispensed by pharmacists" band, the theme-color, and the hover fill of the primary button and the Bag. White text on it reads at 6.7:1.
- **HST Magenta** (`brand`, #dd1860): the logo roundel colour, sampled from the live site. Action fills with white text (the Bag pill, the primary `.btn-stamp`, the hero float card's arrow disc on hover; white on it is 4.8:1) and thin marks: the checked pack ring and dot, the free-delivery meter fill, the current and done checkout steps, the form checkbox accent, the caret.
- **Magenta Ink** (`brand-ink`, #a8114a): magenta as small text on white or tint, 7.2:1 on white. Links (underline at 35% alpha, full on hover), the active nav label, stamped-chip text, the Start-here stamp, the counter and step-number digits, the fact-card figures, the benefit ticks, the required asterisk, the Bag count digits, the `.btn-light` label.
- **Magenta Tint** (`brand-tint`, #fdeef3): the soft fill under the active nav pill, the hero "Best seller" chip, the Start-here stamp, the checked pack tile, the pain-relief shelf tile, the step-number and float-arrow circles, article blockquotes, the form success note, and the hover fill of `.btn-light`.
- **Magenta Tint Deep** (`brand-tint-2`, #fbdce6): text selection, hover on stamped chips and on the pain-relief shelf tile.
- **On Magenta** (`on-brand`, #ffffff) and **On Magenta Soft** (`on-brand-2`, #ffd6e3): the only two text colours allowed on a magenta field. Headings, check text and button labels are white; the hero dose line, band intros, `.small` lines and strip ticks are the soft pink (9.9:1 on #b3124c). Grey text never sits on magenta.

### Secondary
- **Wordmark Slate** (`slate`, #3d4a57): the "MEDICAL" grey of the logo as the dark control colour. Product-card Add to bag buttons, the pressed filter chip, `.btn-dark` (Trade enquiries). White on it reads at 9.1:1.
- **Slate Deep** (`slate-deep`, #2b3640): the dark surfaces. The benefits strip, the prototype notice, the undo toast, the footer, and the hover fill of slate buttons. White on it is 12.3:1.

### Tertiary
- **Heritage Gold Ink** (`gold-ink`, #7f6133): the brand word on Heritage products (panel head and card brand line). A mark of range, not an accent.
- **Zoo-Vite Green Ink** (`green-ink`, #226826): the same role for Zoo-Vite products.
- **Pack Mint** (`mint`, #e6f4ec): the Rheuma-Salve pack colour, kept as a token for a rare tint. Nothing in the current stylesheet uses it; `.band.mint` now resolves to the light grey surface. Never a text colour, never a band.
- **Error Red** (`error`, #b42318): invalid field border (2px) and the "! " error message. Nothing else is red.

### Neutral
- **Counter White** (`bg`, #ffffff): the page below the hero, the header pill, every panel, the hero pack card and float card, the fact cards on the magenta band, controls and inputs.
- **Well Grey** (`surface`, #f4f6f8): every product image well (hero float thumbnail, shop-by-need tiles, product cards, compare thumbnails, the product-page pack figure, bag thumbnails), the alternate bands (`.band.paper`, `.band.mint`), the header search field, chips, quiet buttons, shelf tiles, brand chips, where-to-buy pills, the caution note, disabled pack tiles, hover fills on buttons, nav links and notes.
- **Well Grey Deep** (`surface-2`, #e9edf1): hover state of tiles, chips, shelf tiles and quiet buttons; the meter track; inactive checkout step bars.
- **Light Rule** (`line`, #e5e9ee): every 1px structural rule: panel borders, table rows, field rows, accordion edges, step and note dividers, the checkout assurance rule.
- **Control Rule** (`line-2`, #d3dae2): the 1.5px rule on things you touch: default buttons, inputs, pack tiles, the quantity stepper, the nav toggle, the dashed empty-state border, the scrollbar thumb.
- **Label Ink** (`ink`, #1f2933): headings, body, prices, product names, the added-state button, the focus ring.
- **Soft Ink** (`ink-2`, #4b5563): lead and dose lines on white, nav links at rest, "For:" lines, accordion bodies, cautions, panel-head bold facts, fact-card text, breadcrumb chevrons, the search button.
- **Muted Grey** (`muted`, #6b7280): captions, item codes, "incl. GST", table column heads, filter group names, breadcrumbs, field labels (dt), the panel head row, tile sublines, the hero float subline, pack-tile sublines. 5.3:1 on white, 4.9:1 on Well Grey; never on magenta or slate.

### Named Rules
**The Two Fields Rule.** Magenta is a field in exactly two places: the hero block (with the header band above it) and the "Dispensed by pharmacists" band. Everywhere else it marks the single active element: the Bag, the primary button, the active nav pill, the checked pack tile, the current checkout step, the free-delivery meter. A third magenta band, or a magenta section background anywhere else, is wrong.

**The Slate Controls Rule.** Dark controls that are not the one primary action are slate (#3d4a57, deeper #2b3640 on hover): product-card Add to bag, the pressed filter chip, Trade enquiries. The dark surfaces are slate-deep: strip, prototype notice, toast, footer. Slate never appears as a text colour; ink does that.

**The No Grey On Magenta Rule.** Muted grey (#6b7280) and soft ink (#4b5563) are allowed on white (5.3:1) and on well grey (4.9:1) only. On a magenta field every secondary line switches to On Magenta Soft (#ffd6e3, 9.9:1 on #b3124c); headings, checks and labels are white (6.7:1).

**The Magenta Ink Rule.** Magenta text is always brand-ink (#a8114a, 7.2:1 on white, 6.5:1 on the tint): links, the active nav label, chip and stamp text, the fact figures, the required asterisk, benefit ticks. The brighter brand (#dd1860) is reserved for fills with white text (4.8:1) and thin marks; brand-deep (#b3124c) is reserved for fields and hover fills.

## Typography

**Display Font:** Archivo (with Helvetica Neue, Arial, sans-serif)
**Body Font:** Archivo (same family)
**Label/Mono Font:** none; numbers use Archivo with tabular numerals

**Character:** One grotesque at five weights, set tight and bold at display sizes, relaxed at text sizes, white on magenta in the hero and ink on white below. It reads like the clean pharmacy template the client pointed at: confident headline, plain body, nothing ornamental. Google Fonts is asked for the static weights 400, 500, 600, 700 and 800 only (`Archivo:wght@400;500;600;700;800`); the width axis is no longer requested.

### Hierarchy
- **Display** (700, clamp(2.1rem, 1.3rem + 3vw, 3.8rem), 1.08, -0.025em): the hero h1 "Pain, cough or cold? Start here." in white, capped at 14ch. Inner-page h1s are smaller clamps: page head 2rem to 3rem, product page 1.8rem to 2.8rem capped at 18ch. Text is balanced (`text-wrap: balance`).
- **Headline** (700, clamp(1.5rem, 1.15rem + 1.3vw, 2.1rem), 1.15, -0.015em): band headings ("Best sellers", "Which pain relief do I need?", "Dispensed by pharmacists since 1994" in white), page sections; the checkout step questions and "Our brands" at 1.3rem to 1.35rem.
- **Title** (700, 1.35rem, 1.15, -0.015em): panel titles and the brand-band h3s; product-card names use 1.08rem/1.3 in the same weight.
- **Subtitle** (600, 1rem, 1.15, 0): minor headings inside panels, tile names (1rem/600), the hero float card title (0.95rem/600).
- **Lead** (400, 1.12rem, 1.6): the page-head intro in Soft Ink; the hero dose line is the same role at 1.15rem/1.55 in On Magenta Soft, max 46ch; the product-page dose is 1.1rem.
- **Body** (400, 17px, 1.6): everything else, tabular numerals on, antialiased. Paragraphs, list items and dd are capped at 68ch; articles at 70ch.
- **Small** (400, 0.9rem, 1.6): captions, item codes, "incl. GST", strip items (0.92rem/500), legal (0.85rem), tile and float sublines (0.85rem / 0.82rem), card brand line (0.82rem), pack-tile sublines (0.8rem), stamp (0.72rem, 600).
- **Label** (600, 0.82rem): compare-table column heads and filter group names in Muted Grey; field dt at 0.92rem; nav links 0.93rem/500.
- **Price** (700, 1.9rem, -0.02em, tabular): the product-page price that re-prints when the pack changes; fact-card figures are 1.5rem/700 in Magenta Ink; card and table prices are 600 to 700 at body size.
- **Watermark** (800, clamp(5rem, 16vw, 15rem), 1, -0.04em): the single word "RELIEF" at 9% white across the bottom of the hero block, `aria-hidden`, never selectable. The only use of weight 800.

### Named Rules
**The No Kicker Rule.** Nothing sits above a heading: no eyebrow, no category label, no icon. Context lives in the panel head row (muted facts in a line) or in the breadcrumb, never in small caps over an h1 or h2.

**The Tabular Price Rule.** Every number on the site, prices, item codes, dosages, quantities, is set in tabular numerals so columns and reprinted prices do not shift width. Prices carry the S$ prefix and two decimals, always.

## Layout

A single 1240px counter (`width: min(1240px, 100% - 2 * gutter)`, centred) with a fluid gutter of clamp(16px, 2.5vw, 32px). Inner pages place content on a twelve-column grid (`.grid12`, `repeat(12, minmax(0, 1fr))`, gap = gutter): guide text spans 5 columns and its answer 7, the article spans 7, contact facts 5 + form 7, and on the brand band where-to-buy spans 6 beside a 6-column trade panel. Below 900px every grid child collapses to the full width.

The page starts on magenta. The sticky header is a magenta band (0.9rem top padding) carrying a white pill bar (68px, 1240px wide, soft shadow) with the logo at 40px, the seven need links, the grey search field (200 to 300px, hidden under 1100px) and the magenta Bag. On inner pages a white pseudo-element fills the lower half of the band so the pill appears to sit on the seam between magenta and white; on the home page the band runs straight into the hero block. The hero block is full-bleed (negative gutter margins) with 20px rounded bottom corners, a 6fr / 6fr body (text left, pack card right) at least min(560px, 70vh) tall with clamp(1.5rem, 4vw, 3.5rem) top and clamp(2rem, 5vw, 4rem) bottom padding, and the watermark bleeding off its bottom edge. Directly under the block, on white, the six shop-by-need tiles run in one row with gutter gaps, then the slate strip.

Below that, pages are built from bands: full-bleed sections with clamp(2.5rem, 5vw, 4.5rem) vertical padding that alternate white and well grey (`.band.paper`; `.band.mint` is the same grey), with one magenta band (`.band.brand`) per page at most. Each band opens with a `.band-head`: heading and intro on the left, a quiet pill button on the right (`.btn-light` on the magenta band), wrapping on phones. Panels inside a band are white with a light rule on white and no rule on grey or magenta bands.

Fixed compositions: the product page is 5fr / 7fr with the pack figure in a grey well, sticky at top 110px, rounded only on the left; the bag and checkout pages are 7fr / 5fr (lines or steps left, summary panel right); the footer is 1.5fr 1fr 1fr 1fr. Product grids use `auto-fill, minmax(240px, 1fr)`; shop-by-need tiles are six equal columns; the shelf of ranges uses 220px tiles; facts use 220px auto-fit columns; filters 280px.

Density is calm: 1.5rem panel padding, 1.4rem fact cards, 0.9rem card body, 0.75rem gaps between chips and CTAs, 0.5rem between chips, 1rem between stacked blocks (`.stack`) and 0.5rem inside flowing text (`.flow`). Touch targets are 44px minimum (chips, stepper buttons, header search, nav toggle, Remove); buttons and the Bag are 46px.

Responsive sequence: 1100px the header search hides; 960px the nav hides behind a 44px pill toggle and opens as a white 14px sheet under the header with the soft shadow, the logo drops to 36px; 900px the hero stacks (pack card to 300px, the float card becomes a full-width static card under it), the tiles go three-up, the watermark grows to 22vw, grid12 children span full width; 860px the product page, bag grid and footer (to two columns) stack and the pack figure stops being sticky at 260px tall with top corners rounded; 760px the trade block stacks; 720px the compare table hides its head and renders each row as a 72px thumbnail beside a text block with "For:" and "Use:" prefixes; 640px bag lines reflow; 560px health-note rows stack; 520px tiles go two-up; 480px field rows and the footer go single column.

### Named Rules
**The Compare Before Grid Rule.** A category page shows which format fits which situation (the compare table: Product, Best for, How to use, Price, Add) before it shows a card grid. The home page does the same for the two focus ranges, after the best sellers.

**The Tiles Under The Block Rule.** The first viewport is the magenta block (header pill, h1, dose, two CTAs, two checks; pack card with its floating product card) and the shop-by-need tiles start immediately under its rounded corners on white. Nothing else sits between them. On phones the tiles form a three-column grid under the pack.

## Elevation & Depth

Mostly flat, with three deliberate floaters. Depth below the hero is drawn with tonal steps (grey well inside a white card, white panel on a grey band, white fact card on magenta) and 1px light rules, not with shadows. Product cards have no border and no shadow at all: the grey image well is the card. Panels on tinted bands simply drop their rule; they do not gain a shadow. The three things that float are the white header pill (sitting on the magenta band), the hero pack card and its floating product card (sitting on the hero field), and the undo toast. Hover feedback is a lift without a shadow: 3px on tiles and product cards, 2px on shelf tiles. The open mobile nav sheet reuses the header shadow because it is the header unfolding. No zero-offset halos, no hard offset shadows, no gradients, no glass or blur.

### Shadow Vocabulary
- **Soft float** (`box-shadow: 0 10px 30px -18px rgba(31,41,51,.25)`, token `--shadow`): the header pill bar, the hero floating product card, the open mobile nav sheet.
- **Pack lift** (`box-shadow: 0 24px 50px -20px rgba(0,0,0,.35)`): the hero pack card only, so the jar reads as standing on the magenta field.
- **Toast** (`box-shadow: 0 10px 30px -12px rgba(0,0,0,.4)`): the fixed undo toast only.

### Named Rules
**The Three Floaters Rule.** Only the header pill, the hero pack card with its product card, and the undo toast cast shadows. Panels, product cards, tiles and fact cards are flat at rest and flat on hover; their lift is a 2 to 3px translate, never a shadow.

## Shapes

Four radii, each tied to a role. The largest (20px, `--r`) belongs to the hero: the block's bottom corners and the white pack card. Containers and wells are 14px (`--r-m`): panels, product-card image wells, shop-by-need tiles, shelf tiles, fact cards, the hero float card, the mobile nav sheet, the empty state, the product-page pack figure. Fields, thumbnails and notes are a step tighter (10px, `--r-s`): inputs, selects, textareas, pack-size tiles, compare and bag thumbnails, the float card thumbnail, the caution and success notes, article blockquotes, the toast, the footer logo plate, the mobile nav links. Anything you press or that counts is a pill (999px): the header bar itself, buttons, chips, nav items, the search field, the Bag and its count, the quantity stepper, the stamp, the meter, where-to-buy and brand chips. The focus ring carries a 4px radius so it hugs square and round shapes alike. Radio dots, step numbers, the float card's arrow disc and the search button are true circles.

Borders are 1px Light Rule on structure and 1.5px Control Rule on controls; the ghost button is the only translucent border (55% white, full white on hover); the empty state is the only dashed border. Product images sit in their wells with `mix-blend-mode: multiply`, so the white of a packshot disappears into the grey and no cut-out edge shows. Nothing is clipped diagonally, no perforations, no dotted rules.

### Named Rules
**The Pill Means Action Rule.** Fully rounded (999px) shapes are reserved for things you press or pick, plus the header bar that holds them: buttons, chips, nav items, the search field, the Bag, the quantity stepper, the stamp, the meter. Containers, tiles and wells are 14px; fields, thumbnails and notes are 10px; only the hero block and pack card are 20px.

**The Grey Well Rule.** Every product image, from the 56px float thumbnail to the 520px product-page pack, sits on a Well Grey (#f4f6f8) rounded surface with the image multiply-blended into it. No product image is placed directly on white, on magenta, or inside a bordered box.

## Components

Every component is plain HTML styled by one class in `assets/css/style.css`, with behaviour from `assets/js/site.js` as progressive enhancement. Icons are one family of 1.5px-stroke SVGs (tick, plus, arrow, bag, search, menu) at 20px, 18px inside buttons, 16px in the strip, in currentColor. States shared by all interactive elements: focus-visible is a 2px Label Ink outline offset 3px (1px inside form fields and the header search); hover changes fill or rule, never hue; disabled is opacity .45 with `cursor: not-allowed`.

### Header, navigation, search and bag (`.site-header`, `.header-inner`, `.nav`, `.hsearch`, `.bag`, `.nav-toggle`)
A white pill floating on a magenta band.
- **Band:** sticky, Hero Magenta, 0.9rem top padding (0.6rem on phones). On inner pages the lower half of the band is white so the pill straddles the seam; on the home page the band flows into the hero block.
- **Bar:** 68px white pill, `.4rem .5rem .4rem 1.1rem` padding, soft float shadow, 1240px wide. Logo lock-up (HST roundel + wordmark + Kowa line, 74x40) on the left.
- **Links:** 500 weight, 0.93rem, Soft Ink, pill padding .55rem .7rem, no wrap. Hover: Label Ink on Well Grey. Active page: Magenta Ink on Magenta Tint.
- **Search:** a 44px Well Grey pill (200 to 300px, flexible) with a transparent input at 0.92rem and a 36px circular button in Soft Ink that turns white on hover; focus-within draws the 2px ink outline. Hidden under 1100px; the shop page has its own search.
- **Bag:** a 46px HST Magenta pill with white bag icon and "Bag" at 600/0.95rem; hover Hero Magenta. The count is a hidden white disc with Magenta Ink digits (0.78rem) that appears once an item is added; aria-label updates with the count.
- **Mobile (<=960px):** a 44px white pill toggle with a 1.5px Control Rule; the nav becomes a white 14px sheet under the bar with the soft float shadow, links at 1.05rem with 10px corners, `aria-expanded` toggled by JS; the logo drops to 36px.

### Prototype notice (`.proto`)
A 0.85rem On Magenta Soft line on Slate Deep above the header, centred, with a white link. Removed at launch.

### Hero block (`.hero`, `.hero-block`, `.hero-body`, `.dose`, `.hero-ctas`, `.checks`, `.hero-pack`, `.float`, `.watermark`)
The first viewport is the template's deep colour block in the logo's magenta.
- **Block:** Hero Magenta, full-bleed, 20px bottom corners, overflow hidden, white text. The panel chrome (border, head row) is suppressed inside the hero.
- **Body:** 6fr / 6fr, centred vertically, min-height min(560px, 70vh). Left: white h1 (14ch), the dose line in On Magenta Soft at 1.15rem/1.55 (46ch), the two CTAs (`.btn-light` "Shop pain relief" with arrow, `.btn-ghost` "Cough and cold"), then two check items in On Magenta Soft with white ticks.
- **Pack card:** the Rheuma-Salve jar and box image (536px source, fetchpriority high) on a white 20px card at min(100%, 420px) with 4% padding and the pack-lift shadow.
- **Float card:** anchored bottom-right of the figure: a white 14px card (min 260px) in a 56px / 1fr / auto grid: thumbnail in a 10px Well Grey square, "Rheuma-Salve Balm 50g" at 0.95rem/600 with "Best seller - S$10.10" in 0.82rem Muted Grey, and a 36px Magenta Tint disc with a Magenta Ink arrow that fills HST Magenta with a white arrow on hover. Links to the product page.
- **Watermark:** "RELIEF" at 800 weight, clamp(5rem, 16vw, 15rem), -0.04em, 9% white, centred and bleeding off the bottom (-.18em); `aria-hidden`, pointer-events none.
- **Phones (<=900px):** one column; pack card 300px; the float card becomes a full-width static card under it; the watermark grows to 22vw.

### Shop-by-need tiles (`.hero-foot`, `.counters`, `.tile`, `.stamp`)
Six image tiles on white directly under the block.
- **Grid:** six equal columns with gutter gaps and clamp(1.5rem, 3vw, 2.5rem) top padding; three columns under 900px (0.75rem gaps), two under 520px.
- **Tile:** a square Well Grey 14px well with 14% padding holding a 200px packshot, multiply-blended. Under it the need name at 1rem/600 and a subline in 0.85rem Muted Grey, centred. The first tile (Pain relief) adds a "Start here" stamp: 0.72rem/600 Magenta Ink on a Magenta Tint pill.
- **Hover:** the well turns Well Grey Deep and lifts 3px; no shadow, no border.

### Benefits strip (`.strip`)
A Slate Deep bar below the tiles with clamp(1.5rem, 3vw, 2.5rem) above it: a centred wrapping list of 0.92rem/500 white items ("Free island-wide delivery over S$60", "Made under GMP in Singapore", "Halal-certified options", ...) each led by a 16px tick in On Magenta Soft, gaps .5rem 2.25rem.

### Panel (`.label`, `.label-head`, `.label-body`, `.field`, `dl.fields`)
The universal container.
- **Style:** white, 1px Light Rule, 14px radius; on grey or magenta bands the rule becomes transparent (no shadow). Inside the magenta band the panel keeps ink text.
- **Head row:** 0.9rem Muted Grey facts in a wrapping line (brand in 600 Soft Ink, or Heritage Gold / Zoo-Vite Green by range; category; item code; "Made in Singapore" pushed right), .75rem 1.5rem padding, rule below.
- **Body:** 1.5rem padding. Field rows (`.field`) are a 5.5rem / 1fr grid with Muted Grey 600 terms and ink definitions, separated by Light Rules; they stack under 480px.

### Chips (`.tabs`, `.tab`, `.tab.stamped`, filter `[aria-pressed]`, `.brands-row`, `.where`)
- **Style:** 44px Well Grey pill, no visible border, 500 at 0.95rem, optional 0.8rem Muted Grey subline. Hover: Well Grey Deep.
- **Stamped:** Magenta Tint fill, Magenta Ink text and subline at 600 (hero best-seller, 404 shortcuts). Hover: Magenta Tint Deep.
- **Filter chips:** 44px, .4rem .9rem, 0.9rem/500, `role="button"` with `aria-pressed`; pressed state is Wordmark Slate with white text. Grouped under 0.82rem Muted Grey group names (Show / Relief / Every day / Family and beauty).
- **Brand chips and where-to-buy pills:** static Well Grey pills (0.95rem/600 for brands, 0.92rem/500 for retailers); on the magenta band the retailer pills become 14% white with white text.

### Buttons (`.btn`, `.btn-stamp`, `.btn-dark`, `.btn-light`, `.btn-ghost`, `.btn-quiet`, `.btn-sm`, `.btn-block`, `.is-added`, `[disabled]`)
- **Shape:** pill (999px), 46px, .65rem 1.3rem, 600 at 0.98rem, 18px icon with .5rem gap. Active: scale(.985).
- **Default:** white, 1.5px Control Rule, Label Ink text. Hover: Label Ink rule on Well Grey. Checkout Continue, the shop search button.
- **Primary (`.btn-stamp`):** HST Magenta fill and rule, white text; hover Hero Magenta. One per screen: Add to bag (product page), Checkout, Place order, Send enquiry, Send.
- **Dark (`.btn-dark`):** Wordmark Slate fill and rule, white text; hover Slate Deep. Product-card Add to bag (applied by `.plabel .btn`), Trade enquiries on the magenta band.
- **Light (`.btn-light`):** white fill and rule, Magenta Ink text; hover Magenta Tint. Only on magenta fields: the hero's "Shop pain relief", the brand band's "Our story".
- **Ghost (`.btn-ghost`):** transparent, 55% white rule, white text; hover 12% white fill and a full white rule. Only on magenta fields, beside a light button: the hero's "Cough and cold".
- **Quiet (`.btn-quiet`):** Well Grey fill, no visible rule; hover Well Grey Deep. Band-head links, Back, Keep shopping, Ask in store, Enquire on cards.
- **Small (`.btn-sm`):** 44px, .5rem 1rem, 0.92rem; row-level Add to bag in tables and cards.
- **Added (`.is-added`):** for 1.6s after a click the button turns Label Ink with white text, a tick and "In your bag"; the live region announces the bag count.
- **Disabled:** opacity .45, not-allowed cursor, no transform; `aria-disabled="true"` on the Checkout link until the bag has a line.

### Compare table (`.compare`, `.table-wrap`)
Columns: 72px thumbnail in a 10px Well Grey well (6px padding, multiply), Product (600 at 1.02rem, name as an underline-on-hover link, size in small), Best for, How to use, Price (600, nowrap), Add (small default button). Column heads are 0.82rem 600 Muted Grey; rows are separated by Light Rules with .9rem 1rem cells. The table lives inside a white panel on a grey band (pain relief, Heritage head colour) or on white (cough and cold). Under 720px the head hides and each row becomes a 72px / 1fr grid with "For:" and "Use:" prefixes in Muted Grey.

### Product card (`.plabel`, `.labels`)
- **Structure:** no border, no background. A square Well Grey 14px image well (1.25rem padding, image contained and multiply-blended, scale(1.04) on hover over .3s), then a body with .25rem side padding: brand + size at 0.82rem Muted Grey or range ink, name at 1.08rem/700 linking to the product, "For:" line at 0.9rem Soft Ink; a foot with the price (700 at 1.05rem, "incl. GST" or "ask in store" below in 0.78rem Muted Grey) and a small slate Add to bag, or a quiet Enquire when there is no price.
- **Hover:** 3px lift, no shadow; the name turns Magenta Ink.
- **Grid:** auto-fill at 240px minimum with gutter gaps; `[hidden]` cards leave the grid when filtered.

### Filters, search, result and empty state (`.filters`, `.search`, `.result`, `.empty`)
Filters are chip groups in a 280px auto-fit grid. The shop search is a 46px white pill input (1.5px Control Rule, focus 2px ink outline at 1px offset) beside a default button with the search icon, max 460px. The result line is a 1.1rem/600 h2 ("Showing 51 of 51 products"). The empty state is a 14px panel with a dashed Control Rule, Soft Ink text and a bold Label Ink first line, offering shelf links.

### Breadcrumbs and page head (`.crumbs`, `.page-head`)
0.88rem Muted Grey, separated by a Soft Ink chevron, links underline and darken on hover. The page head carries the h1 (2rem to 3rem) and a lead at 60ch.

### Product page (`.pdp`, `.pdp-pack`, `.print`, `.price-line`, `.packs`, `.pack`, `.qty`, `.buy`, `.checks`, `details.acc`, `.caution`)
The signature surface: one honest label per product.
- **Pack figure:** a Well Grey well with clamp(1rem, 3vw, 2.5rem) padding, left corners rounded 14px, image up to 520px tall, multiply-blended and sticky at 110px; stops being sticky under 860px at 260px tall with the top corners rounded instead.
- **Copy:** h1 (18ch), the dose line at 1.1rem Soft Ink, then field rows For / Use / Pack; the Pack value, the price line and the head-row item code carry `.print` and re-print when the pack changes.
- **Price line:** 1.9rem/700 price with -0.02em, tabular, beside 0.9rem Muted Grey meta ("SGD, incl. GST - free delivery over S$60"). "Price on request" replaces the number when no price exists.
- **Pack tiles:** native radios under 10px tiles (56px min, 9rem min width, 1.5px Control Rule) with a 16px radio dot drawn in `::before`; label in 600 with a 0.8rem Muted Grey price + item code line. Hover: ink rule. Checked: HST Magenta rule, Magenta Tint fill, magenta dot with a 3px white inner ring. Focus: 2px ink outline on the label. Disabled: Muted Grey text on Well Grey.
- **Buy row:** quantity stepper (pill, 44px minus/plus buttons, 52px tabular field, clamped 1..99), the primary magenta Add to bag, and a quiet Ask in store (always present on the balm; it replaces the primary when the pack has no price).
- **Checks:** benefit list with Magenta Ink ticks at 18px.
- **Accordions:** `<details>` separated by Light Rules, 600 summary with a Muted Grey plus that rotates 45deg when open (.25s), Soft Ink body. "What it is" opens by default.
- **Caution:** 0.9rem Soft Ink on Well Grey, 10px radius: "Always read the label and follow directions for use." plus the range-specific line.

### Shelf of ranges (`.shelf`, `.shelf a.pain`)
220px auto-fill tiles, Well Grey, 14px, 120px min: 600 name at 1.02rem, 0.9rem Soft Ink blurb, product count in Muted Grey pushed to the bottom. Pain relief sits on Magenta Tint (Magenta Tint Deep on hover). Hover: Well Grey Deep and a 2px lift.

### Brand band and fact cards (`.band.brand`, `.facts`, `.trade`)
The one lower magenta field.
- **Band:** Hero Magenta with white h2 and h3, On Magenta Soft intro and `.small` lines, a `.btn-light` in the band head.
- **Fact cards:** a 220px auto-fit grid of white 14px cards (1.4rem 1.5rem padding): 1.5rem/700 figure in Magenta Ink ("1994", "GMP", "Two lines", "Kowa") over a 0.95rem Soft Ink line. Inside a `.label` elsewhere, facts lose their gaps and become rows divided by Light Rules with 1.3rem ink figures.
- **Where / trade:** a 6 + 6 grid under the facts: retailer pills at 14% white, and a white panel whose body is a 1fr / auto `.trade` grid ending in a `.btn-dark` "Trade enquiries". Stacks under 900px / 760px.

### Notes and brands row (`.notes`, `.brands-row`)
Notes are a list of 7rem / 1fr rows inside a panel (date in 0.9rem Muted Grey, 1.05rem/600 title, Soft Ink summary) that fill Well Grey on hover; the date stacks over the title under 560px. The brands row is five Well Grey pills (Rheuma-Salve, Heritage, HST Medical, Zoo-Vite, Kowa) under a 1.3rem heading.

### Article and steps (`.article`, `.steps`)
Articles run at 70ch with 1.5rem h2s, 1em paragraph spacing, a Magenta Tint 10px blockquote in 500 weight and a Muted Grey meta line. The steps list numbers each item in a 2rem Magenta Tint circle with Magenta Ink digits (700, 0.9rem), rows divided by Light Rules.

### Forms (`.form`, `.req`, `[aria-invalid]`, `.err`, `.ok`, `.note`, `.check`)
- **Fields:** label text in 600 at 0.95rem; input, select and textarea are 46px, white, 1.5px Control Rule, 10px radius, .6rem .9rem padding, body font; textarea 120px and vertically resizable. Rows are an auto-fit grid at 200px.
- **Required:** a Magenta Ink asterisk after the label (`.req::after`).
- **Focus:** 2px Label Ink outline at 1px offset.
- **Error:** `aria-invalid="true"` sets a 2px Error Red border; the `.err` line (0.88rem, 500, "! " prefix) shows under the field; JS validates on submit and clears each field as it becomes valid, moving focus to the first invalid field and announcing via the live region.
- **Note and success:** `.note` is 0.88rem Muted Grey; `.ok` is a Magenta Tint 10px box with a Magenta Ink tick prefix that replaces the primary button once the demo form is sent.
- **Checkbox:** 20px native box with magenta accent colour, 400-weight wrapped text.

### Bag (`.bag-grid`, `.line`, `.summary`, `.meter`, `#toast`)
- **Lines:** 72px / 1fr / auto / auto rows (thumbnail in a 10px Well Grey well, multiply-blended; 600 name link; 0.9rem Muted Grey meta "size - S$ each - Item code"; underlined Remove in Muted Grey; quantity stepper; 700 line total right-aligned), divided by Light Rules; reflow at 640px.
- **Summary:** panel with Subtotal / Delivery / Total field rows (Total at 1.2rem/700), the free-delivery meter (6px Well Grey Deep track, HST Magenta fill scaling from the left over .3s), a Small line that says how much more earns free delivery, a full-width primary Checkout (disabled while empty) and a quiet Keep shopping.
- **Empty:** the dashed empty-state panel with shelf links.
- **Undo toast:** fixed bottom-centre, Slate Deep fill, white text, 10px radius, white-outlined pill Undo button, toast shadow, auto-hides after 6s; `role="status"`.

### Checkout (`.steps-bar`, `.step`, `.step-nav`, `.assure`)
Three gated steps in the left panel: a three-cell bar with 4px top rules (Well Grey Deep at rest, HST Magenta for the current step and for done steps, which gain a tick), 0.9rem Muted Grey labels (current in 600 Label Ink). Each `.step` is a section with a 1.35rem h2 that receives focus on change; Continue (default button) validates the current step before revealing the next, Back is quiet, Place order is primary and disabled while the bag is empty. The assurance strip below is a 180px auto-fit grid of 0.9rem Soft Ink facts with 600 Label Ink leads, above a Light Rule.

### Footer (`.site-footer`, `.footer-grid`, `.ft-h`, `.legal`)
Slate Deep, 3rem top padding, 0.95rem, 3rem above it. Four columns (1.5fr 1fr 1fr 1fr): the logo at 110px on a white 10px plate with the company line in a light grey-blue (#cbd3dc, about 8:1) and the label reminder in a dimmer one (#9aa6b2, about 5:1); Shop, HST Medical and Help lists with white 600 headings and #cbd3dc links that turn white and underline on hover. The legal bar sits above a 14% white rule in 0.85rem #9aa6b2. Two columns under 860px, one under 480px.

### Motion
One authored moment: choosing a pack size re-prints the label. JS toggles `.printing` on the product panel and every `.print` element (price, pack line, item code) runs `feed` for .4s on the site easing (`cubic-bezier(.2,.7,.2,1)`), fading from 25% to full opacity like paper leaving a printer. Everything else is state feedback at .18s: fills, rules, the 3px lift on tiles and product cards, the 2px lift on shelf tiles, the .3s image zoom on cards, the .3s meter fill, the .25s accordion plus, the scale(.985) press, the float card's arrow disc filling magenta. Under `prefers-reduced-motion` the feed is removed and the transitions on chips, buttons, pack tiles, cards, card images, the meter, tiles and shelf tiles drop to .01ms; the state changes still land, and JS skips the `.printing` class entirely. No scroll-reveal, no animation libraries, no autoplay, no carousels.

## Do's and Don'ts

### Do:
- **Do** open every page on the magenta band with the white pill header; on the home page let the band run into the hero block, on inner pages let the white half-band put the pill on the seam.
- **Do** keep the hero's first viewport exact: header pill, h1, dose, a light CTA plus a ghost CTA, two checks on the left; pack card with the floating product card on the right; the six shop-by-need tiles directly under the block on white.
- **Do** put every product image, at every size, in a Well Grey (#f4f6f8) rounded well with `mix-blend-mode: multiply`, 14px for tiles and cards, 10px for thumbnails.
- **Do** use magenta as a field in exactly two places (hero block, "Dispensed by pharmacists" band) and otherwise only on the active element: the Bag, the primary button, the active nav pill, the checked pack, the current step, the meter.
- **Do** make dark controls slate (#3d4a57): product-card Add to bag, the pressed filter chip, Trade enquiries; and dark surfaces slate-deep (#2b3640): strip, toast, footer, prototype notice.
- **Do** write secondary text on magenta in On Magenta Soft (#ffd6e3) and headings, checks and labels in white; keep Muted Grey (#6b7280) and Soft Ink (#4b5563) to white and grey surfaces.
- **Do** put the compare table (Product, Best for, How to use, Price, Add) before the product grid on every category page and for both focus ranges on the home page.
- **Do** show the pack size with its real price and item code, and re-print the price line when the pack changes; "Price on request" and "Ask in store" replace the number and the magenta button when no price exists.
- **Do** keep 44px minimum touch targets (chips, stepper buttons, header search, nav toggle) and the 17px body floor; the audience is 45+ on phones.
- **Do** keep the pharmacist register in copy: plain, direct, "Always read the label and follow directions for use" on every product page, cautions in the grey `.caution` box.
- **Do** keep everything portable to a GeneratePress child theme and WP EasyCart CSS overrides: tokens on :root, no template forking, see WP-MAPPING.md.

### Don't:
- **Don't** add eyebrow labels, kickers, small-caps category lines or icons above any heading.
- **Don't** put grey text (#6b7280 or #4b5563) on magenta or slate; use #ffd6e3 or white.
- **Don't** add a third magenta band, a magenta section background, magenta rules, decorative magenta icons or secondary links in #dd1860; magenta text is always #a8114a.
- **Don't** give product cards, panels, tiles or fact cards a shadow, at rest or on hover; only the header pill, the hero pack and float cards, and the toast float.
- **Don't** place a product image directly on white, on magenta or inside a bordered box; the grey well is the frame.
- **Don't** use stock photography of people, lifestyle imagery or illustrated characters; the only imagery is the packshots from the catalogue and the logo.
- **Don't** add carousels, sliders, scroll-reveal, parallax, animation libraries, autoplay or image-heavy heroes beyond the one pack card; the RFP budget is graphics-lite and instant on 4G.
- **Don't** invent testimonials, awards, ratings, pharmacist names, clinical claims or prices; there is no testimonial band because there are no testimonials. Unconfirmed facts carry a "to be confirmed" note.
- **Don't** make pack mint (#e6f4ec) a band, a text colour or a card fill; it is a reserved tint, currently unused.
- **Don't** mix radii: hero block and pack card 20px, panels, tiles and wells 14px, fields, thumbnails and notes 10px, pressables and the header bar 999px; no 4px or 6px one-offs except the focus ring.
- **Don't** let the bag or checkout proceed without items: the Checkout and Place order buttons stay disabled (opacity .45, aria-disabled) until the bag has a line.
