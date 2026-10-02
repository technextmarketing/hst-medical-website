---
name: HST Medical
description: A pharmacy-counter store in white, soft and clean, where every product is handed over with its name, its use and the real price for the pack you chose.
colors:
  bg: "#ffffff"
  surface: "#f6f8f7"
  surface-2: "#eef3f0"
  mint: "#e6f4ec"
  mint-2: "#cfe9db"
  line: "#e6eae8"
  line-2: "#d5dcd8"
  ink: "#1f2933"
  ink-2: "#4b5563"
  muted: "#6b7280"
  brand: "#dd1860"
  brand-deep: "#b3124c"
  brand-tint: "#fdeef3"
  gold-ink: "#7f6133"
  green-ink: "#226826"
  error: "#b42318"
typography:
  display:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2rem, 1.3rem + 2.6vw, 3.4rem)"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.02em"
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
rounded:
  panel: "14px"
  control: "10px"
  pill: "999px"
spacing:
  gutter: "clamp(16px, 2.5vw, 32px)"
  band: "clamp(2.5rem, 5vw, 4.5rem)"
  panel: "1.5rem"
  stack: "1rem"
  flow: "0.5rem"
  chip-gap: "0.5rem"
components:
  button-default:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0.65rem 1.25rem"
    height: "46px"
  button-default-hover:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
  button-primary:
    backgroundColor: "{colors.brand}"
    textColor: "{colors.bg}"
    rounded: "{rounded.pill}"
    padding: "0.65rem 1.25rem"
    height: "46px"
  button-primary-hover:
    backgroundColor: "{colors.brand-deep}"
    textColor: "{colors.bg}"
  button-quiet:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0.65rem 1.25rem"
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
    textColor: "{colors.bg}"
    rounded: "{rounded.pill}"
  chip:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0.5rem 1rem"
    height: "44px"
  chip-hover:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
  chip-stamped:
    backgroundColor: "{colors.brand-tint}"
    textColor: "{colors.brand-deep}"
    rounded: "{rounded.pill}"
  chip-pressed:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.bg}"
    rounded: "{rounded.pill}"
    padding: "0.35rem 0.85rem"
    height: "40px"
  nav-link:
    textColor: "{colors.ink-2}"
    rounded: "{rounded.pill}"
    padding: "0.55rem 0.75rem"
  nav-link-hover:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
  nav-link-active:
    backgroundColor: "{colors.brand-tint}"
    textColor: "{colors.brand-deep}"
  bag-pill:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0.4rem 0.95rem"
    height: "44px"
  bag-count:
    backgroundColor: "{colors.brand}"
    textColor: "{colors.bg}"
    rounded: "{rounded.pill}"
    size: "1.4rem"
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
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "1rem 1.1rem"
  product-card-image-well:
    backgroundColor: "{colors.surface}"
    padding: "1.25rem"
  counter-card:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "1rem 1.1rem"
    height: "92px"
  counter-card-pain:
    backgroundColor: "{colors.mint}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
  stamp-badge:
    backgroundColor: "{colors.brand}"
    textColor: "{colors.bg}"
    rounded: "{rounded.pill}"
    padding: "0.2rem 0.6rem"
  hero-pack-panel:
    backgroundColor: "{colors.mint}"
    rounded: "{rounded.panel}"
    padding: "1.5rem"
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
    backgroundColor: "{colors.mint}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "1rem 1.25rem"
  empty-state:
    textColor: "{colors.ink-2}"
    rounded: "{rounded.panel}"
    padding: "2rem 1.5rem"
  toast:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.bg}"
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
    textColor: "{colors.brand-deep}"
    rounded: "{rounded.pill}"
    size: "2rem"
  footer:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink-2}"
    padding: "2.5rem {spacing.gutter} 1.25rem"
---

# Design System: HST Medical

## Overview

**Creative North Star: "The White Dispensing Counter"**

HST Medical is a pharmacy counter rendered in white: the product is handed over the way a pharmacist hands it over, name large, what it is for, how to use it, the pack beside it, and the price for the pack you actually chose. The ground is white, the alternate bands are a barely-there paper grey, rules are one pixel and light, and every panel has gently rounded 14px corners. Product photography is the only imagery; nothing decorative sits above a heading.

One typeface, Archivo, carries the whole site at four weights. Magenta is the brand and the single accent: it marks the one thing you can do next (the primary button, the active nav item, the selected pack size, checkout progress, the free-delivery meter) and nothing else. The Rheuma-Salve pack mint appears only as a soft tint on the hero pack panel and the pain-relief tiles, so the flagship range is recognisable from across the room without competing with the action colour.

The density is that of a well-kept counter rather than a wellness brand: compare tables come before product grids, five start-by-need cards sit under the headline, honest pack sizes carry real prices and item codes, and checkout is gated in three plain steps. Motion is limited to one authored moment, the pack-size reprint, plus 2px hover lifts; nothing scrolls into view and no animation library is loaded. The client declined the earlier heavy-display "Dispensing Counter" rendition (dark grounds, dense label chrome, dotted thermal rules, narrow 900-weight type) in favour of this lighter one on 2026-10-02.

**Key Characteristics:**
- White ground, soft paper (#f6f8f7) alternate bands, 1px light rules; flat by default
- 14px rounded panels, 10px inputs and pack tiles, pill (999px) buttons, chips, nav and bag
- Archivo only, weights 400/500/600/700, 17px body, tabular numerals, no eyebrows or kickers
- Magenta (#dd1860) is the single accent and marks only the active element
- Pack mint (#e6f4ec) is a tint, never a text colour and never a surface for grey text
- Compare-first categories, start-by-need counters, honest pack sizes, gated three-step checkout
- One authored motion (pack-size reprint) plus 2px hover lifts; reduced-motion keeps every state change
- Portable to a GeneratePress child theme and WP EasyCart CSS overrides

## Colors

A white counter with two near-white greys, one soft mint tint, one magenta in three strengths, and a small set of inks. Sixteen tokens on `:root`, nothing else.

### Primary
- **HST Magenta** (`brand`, #dd1860): the logo roundel colour, sampled from the live site. Used as a fill with white text (primary button, bag count, Start-here stamp; white on it is 4.8:1) and as a thin mark (checked pack ring and dot, free-delivery meter fill, current and done checkout steps, form checkbox accent, caret).
- **Magenta Ink** (`brand-deep`, #b3124c): the magenta for text, 6.8:1 on white. Links (underline at 35% alpha, full on hover), the active nav label, stamped-chip text, the benefit tick icons, the required asterisk, the step-number digits, primary-button hover fill, footer link hover.
- **Magenta Tint** (`brand-tint`, #fdeef3): the soft fill under the active nav pill, the hero "Best seller" chip, the checked pack tile and the numbered-step circles. Hover on a stamped chip deepens to #fbdce6 (a one-off; not a token).

### Secondary
- **Pack Mint** (`mint`, #e6f4ec): Rheuma-Salve pack colour as a tint only. The hero pack panel, the pain-relief counter card and shelf tile, the mint band (`.band.mint`), article blockquotes and the form success note. Never a text colour. Secondary text on it uses Soft Ink, never Muted Grey.
- **Pack Mint Deep** (`mint-2`, #cfe9db): text selection highlight only.

### Tertiary
- **Heritage Gold Ink** (`gold-ink`, #7f6133): the brand word on Heritage products (panel head and card brand line). A mark of range, not an accent.
- **Zoo-Vite Green Ink** (`green-ink`, #226826): the same role for Zoo-Vite products.
- **Error Red** (`error`, #b42318): invalid field border (2px) and the "! " error message. Nothing else is red.

### Neutral
- **Counter White** (`bg`, #ffffff): the page, every panel, card, control and the image wells inside compare tables.
- **Soft Paper** (`surface`, #f6f8f7): alternate bands (`.band.paper`), the prototype notice, the footer, product-card image wells, bag thumbnails, the quiet button, hover fill on buttons, chips and nav, the caution note, disabled pack tiles.
- **Paper Deep** (`surface-2`, #eef3f0): quiet-button hover, the meter track, inactive checkout step bars.
- **Light Rule** (`line`, #e6eae8): every 1px structural rule: panel borders, table rows, field rows, accordion edges, header and legal bottom borders, counter and shelf tile borders.
- **Control Rule** (`line-2`, #d5dcd8): the slightly firmer 1.5px rule on things you touch: buttons, chips, the bag, inputs, pack tiles, the quantity stepper, the where-to-buy chips, the dashed empty-state border; also the hover border on counters.
- **Label Ink** (`ink`, #1f2933): headings, body, prices, product names, the pressed filter chip fill, the added-state button, the undo toast, the focus ring.
- **Soft Ink** (`ink-2`, #4b5563): lead and dose lines, nav links at rest, "For:" lines, accordion bodies, cautions, footer links, panel-head bold facts, and every secondary line that sits on mint.
- **Muted Grey** (`muted`, #6b7280): captions, item codes, "incl. GST", table column heads, filter group names, breadcrumbs, field labels (dt), the panel head row. 4.8:1 on white, 4.5:1 on Soft Paper; not permitted on mint.

### Named Rules
**The One Accent Rule.** Magenta marks the single thing you can do next on a screen: the primary button, the active nav item, the checked pack tile, the current checkout step, the free-delivery meter, the Start-here stamp. Everything else is ink, grey, white or a light rule. If two magenta elements compete on one phone screen, one of them is wrong.

**The No Grey On Mint Rule.** Muted grey (#6b7280) is allowed on white (4.8:1) and on soft paper (4.5:1) only. On the mint tint it falls below AA, so every secondary line inside a mint panel or tile switches to soft ink (#4b5563).

**The Magenta Ink Rule.** Magenta text is always brand-deep (#b3124c, 6.8:1 on white): links, the active nav label, chip text, the required asterisk, benefit ticks. The brighter brand (#dd1860) is reserved for fills with white text on top (4.8:1) and for thin marks such as the meter and the step bar.

## Typography

**Display Font:** Archivo (with Helvetica Neue, Arial, sans-serif)
**Body Font:** Archivo (same family)
**Label/Mono Font:** none; numbers use Archivo with tabular numerals

**Character:** One grotesque at four weights, set tight at display sizes and relaxed at text sizes. It reads like a well-printed dispensing label: clear, direct, nothing ornamental. The variable font is loaded from Google Fonts with the width axis (75..100) and weight axis (400..900), but the site uses only normal width and weights 400, 500, 600 and 700; the narrow 900 display of the declined rendition is gone.

### Hierarchy
- **Display** (700, clamp(2rem, 1.3rem + 2.6vw, 3.4rem), 1.15, -0.02em): the page h1 and the hero question "Pain, cough or cold? Start here." Hero h1 is capped at 16ch; the product-page h1 is a smaller clamp (1.8rem to 2.8rem) capped at 18ch. Text is balanced (`text-wrap: balance`).
- **Headline** (700, clamp(1.5rem, 1.15rem + 1.3vw, 2.1rem), 1.15, -0.015em): band headings ("Which pain relief do I need?"), page sections, the checkout step questions at 1.35rem.
- **Title** (700, 1.35rem, 1.15, -0.015em): panel titles; product-card names use 1.15rem/1.25 in the same weight.
- **Subtitle** (600, 1rem, 1.15, 0): minor headings inside panels; facts figures are 700 at 1.3rem with -0.01em.
- **Lead** (400, 1.12rem, 1.6): the page-head intro in Soft Ink; the hero dose line is the same role at 1.15rem/1.55, max 50ch.
- **Body** (400, 17px, 1.6): everything else, tabular numerals on, antialiased. Paragraphs, list items and dd are capped at 68ch; articles at 70ch.
- **Small** (400, 0.9rem, 1.6): captions, item codes, "incl. GST", legal (0.85rem), pack-tile sublines (0.8rem), card brand line (0.82rem), stamp badge (0.72rem, 600).
- **Label** (600, 0.82rem): compare-table column heads and filter group names in Muted Grey; field dt at 0.92rem.
- **Price** (700, 1.9rem, -0.02em, tabular): the product-page price that re-prints when the pack changes; card and table prices are 600 to 700 at body size.

### Named Rules
**The No Kicker Rule.** Nothing sits above a heading: no eyebrow, no category label, no icon. Context lives in the panel head row (muted facts in a line) or in the breadcrumb, never in small caps over an h1 or h2.

**The Tabular Price Rule.** Every number on the site, prices, item codes, dosages, quantities, is set in tabular numerals so columns and reprinted prices do not shift width. Prices carry the S$ prefix and two decimals, always.

## Layout

A single 1200px counter (`width: min(1200px, 100% - 2 * gutter)`, centred) with a fluid gutter of clamp(16px, 2.5vw, 32px). Inner pages place content on a twelve-column grid (`.grid12`, `repeat(12, minmax(0, 1fr))`, gap = gutter): guide text spans 5 columns and its answer 7 (category FAQ), the article spans 7, contact facts 5 + form 7. Below 900px every grid child collapses to the full width.

Pages are built from bands: full-bleed sections with clamp(2.5rem, 5vw, 4.5rem) vertical padding that alternate white, soft paper (`.band.paper`) and mint (`.band.mint`). Each band opens with a `.band-head`: heading and intro on the left, a quiet pill button on the right, wrapping on phones. Panels inside a band are white and separated from the band by a light rule on white or the soft shadow on tinted bands.

Fixed compositions: the hero is 7fr / 5fr (text left, mint pack panel right) followed by a row of five equal counter cards; the product page is 5fr / 7fr with the pack figure on soft paper, sticky at top 92px, and its corners rounded only on the left; the bag and checkout pages are 7fr / 5fr (lines or steps left, summary panel right); the footer is 1.5fr 1fr 1fr 1fr. Product grids use `auto-fill, minmax(250px, 1fr)`; the shelf of ranges uses 220px tiles; facts use 240px columns with top rules.

Density is calm: 1.5rem panel padding, 1rem card body, 0.75rem gaps between tiles, 0.5rem between chips, 1rem between stacked blocks (`.stack`) and 0.5rem inside flowing text (`.flow`). Touch targets are 44px minimum (chips, stepper buttons, bag, nav toggle); buttons are 46px.

Responsive sequence: 960px the nav hides behind a pill toggle and opens as a white sheet under the sticky header; 900px the hero stacks and the counters go two-up with the fifth full width, the Start-here stamp moving inline; 860px product page, bag grid and footer (to 2 columns) stack and the pack image stops being sticky; 760px facts regain row rules and the trade block stacks; 720px the compare table hides its head and renders each row as a 72px thumbnail beside a text block with "For:" and "Use:" prefixes; 640px bag lines reflow; 560px health-note rows stack; 480px field rows and the footer go single column. The sticky header is 70px tall, 94% white with an 8px blur and a light bottom rule.

### Named Rules
**The Compare Before Grid Rule.** A category page shows which format fits which situation (the compare table: Product, Best for, How to use, Price, Add) before it shows a card grid. The home page does the same for the two focus ranges.

## Elevation & Depth

Flat by default. Depth is drawn with 1px Light Rules and tonal steps (white panel on soft paper, soft paper well inside a white card), not with shadows. There is exactly one soft shadow and it appears in two situations: a panel sitting on a tinted band, where its border turns transparent and the shadow takes over, and the hover lift on counters, shelf tiles and product cards (translateY(-2px) with the shadow fading in over .18s). The open mobile nav sheet uses the same shadow. No zero-offset halos, no hard offset shadows, no gradients, no glass beyond the 94% white blurred header.

### Shadow Vocabulary
- **Soft lift** (`box-shadow: 0 6px 20px -14px rgba(31,41,51,.18)`): panels on paper or mint bands; hover state of counters, shelf tiles and product cards; the open mobile nav.
- **Toast** (`box-shadow: 0 10px 30px -12px rgba(0,0,0,.4)`): the fixed undo toast only, because it genuinely floats over the page.

### Named Rules
**The Flat Paper Rule.** Surfaces are flat at rest and separated by 1px light rules. The one soft shadow appears in exactly two cases: a panel sitting on a tinted band (where its rule becomes transparent), and the 2px hover lift on counters, shelf tiles and product cards. Nothing floats at rest except the undo toast.

## Shapes

Three radii, each tied to a role. Containers are gently rounded (14px): panels, product cards, counter cards, shelf tiles, the hero pack panel, the empty state. Fields and things you pick are a step tighter (10px): inputs, selects, textareas, pack-size tiles, the caution and success notes, the toast, thumbnails, the mobile nav links. Anything you press or that counts is a pill (999px): buttons, chips, nav items, the bag and its count, the quantity stepper, the stamp badge, the meter track and fill, the where-to-buy chips. The focus ring carries a 4px radius so it hugs square and round shapes alike. Radio dots and step numbers are true circles.

Borders are 1px Light Rule on structure and 1.5px Control Rule on controls; the empty state is the only dashed border. Nothing is clipped diagonally, no perforations, no dotted rules: the declined rendition's tear-off tabs and thermal rules are gone. Product cards clip their image well to the card radius; the product-page figure is rounded only on its outer corners.

### Named Rules
**The Pill Means Action Rule.** Fully rounded (999px) shapes are reserved for things you press or pick: buttons, chips, nav items, the bag, the quantity stepper, the stamp badge, the meter track. Containers are 14px; fields and pack tiles are 10px.

## Components

Every component is plain HTML styled by one class in `assets/css/style.css`, with behaviour from `assets/js/site.js` as progressive enhancement. Icons are one family of 1.5px-stroke SVGs (tick, plus, arrow, bag, search, menu) at 20px, 18px inside buttons, in currentColor. States shared by all interactive elements: focus-visible is a 2px Label Ink outline offset 3px (1px inside form fields); hover changes fill or rule, never colour hue; disabled is opacity .45 with `cursor: not-allowed`.

### Header, navigation and bag (`.site-header`, `.nav`, `.bag`, `.nav-toggle`)
A quiet, sticky white bar.
- **Style:** 70px, 94% white with 8px blur, 1px Light Rule below. Logo lock-up (HST roundel + wordmark + Kowa line) at 42px on the left.
- **Links:** 500 weight, 0.95rem, Soft Ink, pill padding .55rem .75rem. Hover: Label Ink on Soft Paper. Active page: Magenta Ink on Magenta Tint, the only magenta in the bar unless the bag has items.
- **Bag:** a 44px pill with a 1.5px Control Rule, bag icon, "Bag" and a hidden count that appears as a magenta disc with white digits (0.78rem) once an item is added; aria-label updates with the count.
- **Mobile (<=960px):** a 44px pill toggle; the nav becomes a white sheet under the header with the soft shadow, links at 1.05rem with 10px corners, `aria-expanded` toggled by JS.

### Prototype notice (`.proto`)
A 0.85rem Muted Grey line on Soft Paper above the header, centred, with an inherited-colour link. Removed at launch.

### Hero (`.hero`, `.hero-body`, `.dose`, `.checks`, `.hero-pack`, `.counters`)
The first viewport asks the buyer's question.
- **Composition:** no panel chrome (border and head row are suppressed in the hero). Left: h1 (16ch), the dose line in Soft Ink at 1.15rem, three check items with Magenta Ink ticks. Right: the Rheuma-Salve jar on a Pack Mint 14px panel with a stamped chip "Rheuma-Salve Balm 50g / Best seller - S$10.10".
- **Counters:** five equal 14px cards (min 92px, 1.05rem/600 name plus an 0.85rem Muted Grey subline). The first is pain relief: Pack Mint fill, transparent border, Soft Ink subline, and the only "Start here" stamp (0.72rem white on magenta pill, top right). Hover: Control Rule border, soft shadow, -2px lift. On phones two-up, the fifth full width, stamp inline.

### Panel (`.label`, `.label-head`, `.label-body`, `.field`, `dl.fields`)
The universal container, formerly the "label".
- **Style:** white, 1px Light Rule, 14px radius; on paper or mint bands the rule drops and the soft shadow appears.
- **Head row:** 0.9rem Muted Grey facts in a wrapping line (brand in 600 Soft Ink, or Heritage Gold / Zoo-Vite Green by range; category; item code; "Made in Singapore" pushed right), .75rem 1.5rem padding, rule below.
- **Body:** 1.5rem padding. Field rows (`.field`) are a 5.5rem / 1fr grid with Muted Grey 600 terms and ink definitions, separated by Light Rules; they stack under 480px.

### Chips (`.tabs`, `.tab`, `.tab.stamped`, filter `[aria-pressed]`)
- **Style:** 44px white pill, 1px Control Rule, 600 at 0.95rem, optional 0.8rem Muted Grey subline. Hover: Label Ink rule on Soft Paper.
- **Stamped:** Magenta Tint fill, transparent rule, Magenta Ink text and subline (hero best-seller, 404 shortcuts). Hover deepens the tint.
- **Filter chips:** 40px, 500 weight, `role="button"` with `aria-pressed`; pressed state is Label Ink fill with white text. Grouped under 0.82rem Muted Grey group names (Show / Relief / Every day / Family and beauty).

### Buttons (`.btn`, `.btn-stamp`, `.btn-quiet`, `.btn-sm`, `.btn-block`, `.is-added`, `[disabled]`)
- **Shape:** pill (999px), 46px, .65rem 1.25rem, 600 at 0.98rem, 18px icon with .5rem gap.
- **Default:** white, 1.5px Control Rule, Label Ink text. Hover: Label Ink rule on Soft Paper. Active: scale(.985).
- **Primary (`.btn-stamp`):** HST Magenta fill and rule, white text; hover Magenta Ink. One per screen: Add to bag (product page), Checkout, Place order, Send enquiry, Send.
- **Quiet (`.btn-quiet`):** Soft Paper fill, no visible rule; hover Paper Deep. Band-head links, Back, Keep shopping, Ask in store, Enquire.
- **Small (`.btn-sm`):** 44px, .5rem 1rem, 0.92rem; row-level Add to bag in tables and cards.
- **Added (`.is-added`):** for 1.6s after a click the button turns Label Ink with white text, a tick and "In your bag"; the live region announces the bag count.
- **Disabled:** opacity .45, not-allowed cursor, no transform; `aria-disabled="true"` on the Checkout link until the bag has a line.

### Compare table (`.compare`, `.table-wrap`)
Columns: 72px thumbnail on white (10px radius), Product (600 at 1.02rem, name as an underline-on-hover link, size in small), Best for, How to use, Price (600, nowrap), Add (small default button). Column heads are 0.82rem 600 Muted Grey; rows are separated by Light Rules with .9rem 1rem cells. Under 720px the head hides and each row becomes a 72px / 1fr grid with "For:" and "Use:" prefixes in Muted Grey.

### Product card (`.plabel`, `.labels`)
- **Structure:** panel with a square Soft Paper image well (1.25rem padding, image contained, scale(1.03) on hover over .3s), body (brand + size at 0.82rem Muted Grey or range colour, name at 1.15rem/700 linking to the product, "For:" line at 0.92rem Soft Ink), foot (price 700 at 1.05rem with "incl. GST" or "ask in store" below in 0.78rem Muted Grey, small Add to bag or quiet Enquire).
- **Hover:** soft shadow and -2px lift; name turns Magenta Ink.
- **Grid:** auto-fill at 250px minimum with gutter gaps; `[hidden]` cards leave the grid when filtered.

### Filters, search, result and empty state (`.filters`, `.search`, `.result`, `.empty`)
Filters are chip groups in a 280px auto-fit grid. Search is a 46px pill input (1.5px Control Rule, focus 2px ink outline at 1px offset) beside a default button with the search icon, max 460px. The result line is a 1.1rem/600 h2 ("Showing 51 of 51 products"). The empty state is a 14px panel with a dashed Control Rule, Soft Ink text and a bold Label Ink first line, offering shelf links.

### Breadcrumbs and page head (`.crumbs`, `.page-head`)
0.88rem Muted Grey, separated by a Soft Ink chevron, links underline and darken on hover. The page head carries the h1 and a lead at 60ch.

### Product page (`.pdp`, `.pdp-pack`, `.print`, `.price-line`, `.packs`, `.pack`, `.qty`, `.buy`, `.checks`, `details.acc`, `.caution`)
The signature surface: the dispensing label, now in white.
- **Pack figure:** Soft Paper well, left corners rounded, image up to 520px tall and sticky at 92px; stops being sticky under 860px at 320px tall.
- **Copy:** h1, dose line, then field rows For / Use / Pack; the Pack value, the price line and the head-row item code carry `.print` and re-print when the pack changes.
- **Price line:** 1.9rem/700 price with -0.02em, tabular, beside 0.9rem Muted Grey meta ("SGD, incl. GST - free delivery over S$60"). "Price on request" replaces the number when no price exists.
- **Pack tiles:** native radios under 10px tiles (56px min, 9rem min width, 1.5px Control Rule) with a 16px radio dot drawn in `::before`; label in 600 with a 0.8rem Muted Grey price + item code line. Checked: HST Magenta rule, Magenta Tint fill, magenta dot with a 3px white inner ring. Focus: 2px ink outline on the label. Disabled: Muted Grey text on Soft Paper.
- **Buy row:** quantity stepper (pill, 44px minus/plus buttons, 52px tabular field, clamped 1..99), the primary Add to bag, and a quiet Ask in store that swaps in when the pack has no price.
- **Checks:** benefit list with Magenta Ink ticks at 18px.
- **Accordions:** `<details>` separated by Light Rules, 600 summary with a Muted Grey plus that rotates 45deg when open (.25s), Soft Ink body. "What it is" opens by default.
- **Caution:** 0.9rem Soft Ink on Soft Paper, 10px radius: "Always read the label and follow directions for use." plus the range-specific line.

### Shelf of ranges (`.shelf`, `.shelf a.pain`)
220px auto-fill tiles, 14px, 120px min: 600 name, 0.9rem Soft Ink blurb, product count in Muted Grey pushed to the bottom. Pain relief sits on Pack Mint with transparent rule and Soft Ink text. Hover: soft shadow and -2px lift.

### Facts, where-to-buy, trade and notes (`.facts`, `.where`, `.trade`, `.notes`)
Facts are a 240px auto-fit grid inside a panel: 1.3rem/700 figure ("1994", "GMP", "Kowa") over a 0.95rem Soft Ink line, cells divided by Light Rules. Where-to-buy is a row of 0.92rem/500 white pills with a Control Rule (Guardian, Watsons, NHGP pharmacies). Trade is a 1fr / auto panel body with a quiet or primary button on the right. Notes are a list of 7rem / 1fr rows (date in 0.9rem Muted Grey, 1.05rem/600 title, Soft Ink summary) that fill Soft Paper on hover.

### Article and steps (`.article`, `.steps`)
Articles run at 70ch with 1.5rem h2s, 1em paragraph spacing, a Pack Mint 10px blockquote in 500 weight and a Muted Grey meta line. The steps list numbers each item in a 2rem Magenta Tint circle with Magenta Ink digits, rows divided by Light Rules.

### Forms (`.form`, `.req`, `[aria-invalid]`, `.err`, `.ok`, `.note`, `.check`)
- **Fields:** label text in 600 at 0.95rem; input, select and textarea are 46px, white, 1.5px Control Rule, 10px radius, .6rem .9rem padding, body font; textarea 120px and vertically resizable. Rows are an auto-fit grid at 200px.
- **Required:** a Magenta Ink asterisk after the label (`.req::after`).
- **Focus:** 2px Label Ink outline at 1px offset.
- **Error:** `aria-invalid="true"` sets a 2px Error Red border; the `.err` line (0.88rem, 500, "! " prefix) shows under the field; JS validates on submit and clears each field as it becomes valid, moving focus to the first invalid field and announcing via the live region.
- **Note and success:** `.note` is 0.88rem Muted Grey; `.ok` is a Pack Mint 10px box with a tick prefix that replaces the primary button once the demo form is sent.
- **Checkbox:** 20px native box with magenta accent colour, 400-weight wrapped text.

### Bag (`.bag-grid`, `.line`, `.summary`, `.meter`, `#toast`)
- **Lines:** 72px / 1fr / auto / auto rows (thumbnail on Soft Paper at 10px, 600 name link, 0.9rem Muted Grey meta "size - S$ each - Item code", underlined Remove in Muted Grey, quantity stepper, 700 line total right-aligned), divided by Light Rules; reflow at 640px.
- **Summary:** panel with Subtotal / Delivery / Total field rows (Total at 1.2rem/700), the free-delivery meter (6px Paper Deep track, magenta fill scaling from the left over .3s), a Small line that says how much more earns free delivery, a full-width primary Checkout (disabled while empty) and a quiet Keep shopping.
- **Empty:** the dashed empty-state panel with shelf links.
- **Undo toast:** fixed bottom-centre, Label Ink fill, white text, 10px radius, white-outlined pill Undo button, auto-hides after 6s; `role="status"`.

### Checkout (`.steps-bar`, `.step`, `.step-nav`, `.assure`)
Three gated steps in the left panel: a three-cell bar with 4px top rules (Paper Deep at rest, HST Magenta for the current step and for done steps, which gain a tick), 0.9rem labels (current in 600 Label Ink). Each `.step` is a section with a 1.35rem h2 that receives focus on change; Continue (default button) validates the current step before revealing the next, Back is quiet, Place order is primary and disabled while the bag is empty. The assurance strip below is a 180px auto-fit grid of 0.9rem Soft Ink facts with 600 Label Ink leads, above a Light Rule.

### Footer (`.site-footer`, `.footer-grid`, `.ft-h`, `.legal`)
Soft Paper, 2.5rem top padding, 0.95rem. Four columns (1.5fr 1fr 1fr 1fr): logo at 110px with the company line and the label reminder in Small; Shop, HST Medical and Help lists with 600 headings and Soft Ink links that turn Magenta Ink and underline on hover. The legal bar sits above a Light Rule in 0.85rem Muted Grey. Two columns under 860px, one under 480px.

### Motion
One authored moment: choosing a pack size re-prints the label. JS toggles `.printing` on the product panel and every `.print` element (price, pack line, item code) runs `feed` for .4s on the site easing (`cubic-bezier(.2,.7,.2,1)`), fading from 25% to full opacity like paper leaving a printer. Everything else is state feedback at .18s: fills, rules, the -2px hover lift and soft shadow, the .3s image zoom on cards, the .3s meter fill, the .25s accordion plus, the scale(.985) press. Under `prefers-reduced-motion` the feed is removed and all transitions drop to .01ms; the state changes still land, and JS skips the `.printing` class entirely. No scroll-reveal, no animation libraries, no autoplay.

## Do's and Don'ts

### Do:
- **Do** lead with the buyer's need: the h1 asks "Pain, cough or cold? Start here." and the five start-by-need counters follow it before any brand story.
- **Do** put the compare table (Product, Best for, How to use, Price, Add) before the product grid on every category page and for both focus ranges on the home page.
- **Do** show the pack size with its real price and item code, and re-print the price line when the pack changes; "Price on request" and "Ask in store" replace the number and the magenta button when no price exists.
- **Do** keep one magenta element per phone screen: the primary button, or the active nav, or the checked pack, never two fighting for the eye.
- **Do** write secondary text inside mint panels and tiles in soft ink (#4b5563), and keep muted grey (#6b7280) to white and soft-paper surfaces.
- **Do** keep 44px minimum touch targets (chips, stepper buttons, nav toggle, bag) and the 17px body floor; the audience is 45+ on phones.
- **Do** give every panel a 1px light rule on white, and swap the rule for the soft shadow only when the panel sits on a paper or mint band.
- **Do** keep every pack image on a white or soft-paper well with explicit width and height, loaded lazily below the fold and fetchpriority=high for the one hero or product image.
- **Do** keep the pharmacist register in copy: plain, direct, "Always read the label and follow directions for use" on every product page, cautions in the soft-paper .caution box.
- **Do** keep everything portable to a GeneratePress child theme and WP EasyCart CSS overrides: tokens on :root, no template forking, see WP-MAPPING.md.

### Don't:
- **Don't** add eyebrow labels, kickers, small-caps category lines or icons above any heading.
- **Don't** use magenta for anything but the active element: no magenta rules, backgrounds for whole sections, decorative icons or secondary links in #dd1860.
- **Don't** put grey text (#6b7280) on mint (#e6f4ec); it fails AA.
- **Don't** add carousels, sliders, scroll-reveal, parallax, animation libraries or image-heavy heroes; the RFP budget is graphics-lite and instant on 4G.
- **Don't** invent testimonials, awards, ratings, pharmacist names, clinical claims or prices; unconfirmed facts carry a "to be confirmed" note.
- **Don't** reintroduce the declined heavy rendition: dark grounds, Archivo 900 or narrow widths, dense label chrome, dotted thermal rules, perforated tabs, or a label header strip on the hero.
- **Don't** use zero-offset halos, hard offset shadows, gradients or more than the one soft shadow (0 6px 20px -14px rgba(31,41,51,.18)).
- **Don't** make pack mint a text colour or a full-page background; it is a tint for the hero pack panel, the pain-relief tiles, blockquotes and the form success note only.
- **Don't** mix radii: containers 14px, fields and pack tiles 10px, pressables 999px; no 4px or 6px one-offs except the focus ring.
- **Don't** let the bag or checkout proceed without items: the Checkout and Place order buttons stay disabled (opacity .45, aria-disabled) until the bag has a line.
