---
version: 1
slug: "index-html"
primary_target: "index.html"
related_targets: ["shop/index.html","products/rheuma-salve-balm/index.html","checkout/index.html"]
---

# Surface brief: hstmedical.com prototype (home + store + product + cart/checkout + company pages)

Scope: the whole static prototype (79 pages built by `_src/build.py`). Visitor mode: Persuade on the home page and category guides; Operate on store, product, cart and checkout; Read on health notes.

Audience and job: a Singapore consumer, typically 45+, on a phone, in pain or with a cough, who knows Rheuma-Salve, Heritage or Zoo-Vite from a Guardian, Watsons or NHGP shelf. Job: pick the right format, see the real price for the real pack size, buy with delivery or find a stockist. Secondary: trade buyers reaching a territory manager.

Proof and content on hand: 51 SKUs with catalogue descriptions, benefits, usage, active ingredients, origin and item codes; live SGD prices for 48; product images from the catalogue; the HST logo with Kowa lock-up; retailer names (Guardian, Watsons, NHGP confirmed). No testimonials, no clinical studies, no lifestyle photography: none may be invented.

Constraints: RFP rules bind strictly (typography-centric, graphics-lite, no carousels, no animation libraries, mobile-first, 4G budget, portable to classic WordPress + WP EasyCart CSS overrides). Brand commitments: logo and magenta stay; pack colours may become system colours. Prototype remains noindex until sign-off.

Memorable moment: the dispensing label. Choosing a pack size re-prints the label (price, item code, pack) with a short paper-feed motion; "Add to bag" stamps it.

Unresolved: language strategy, store-locator depth, customer-service details, Vantelin cross-listing.

## Direction contract

> Amended 2026-10-02 after the first build: the client reviewed the Dispensing Counter rendition and pinned a lighter rendition ("much cleaner and simpler, softer, use the website's current design"). The structure, story and raises below stand; the OWN-WORLD block is superseded by: white ground, soft surface band (#f6f8f7), 1px light rules (#e6eae8), 14px rounded panels with a soft shadow only on tinted bands, Archivo at 400/600/700 (no narrow/900 display), pack mint (#e6f4ec) as a tint on the hero pack panel and the pain-relief tile, magenta (#dd1860) as the only accent (primary button, active nav, selected pack, progress), pill chips and buttons, no dotted thermal rules, no label header strip on the hero. FIRST VIEWPORT keeps the h1 "Pain, cough or cold? Start here.", the three checks, the Rheuma-Salve jar on a mint panel with a soft "Best seller" chip, and the five start-by-need counters as rounded cards.

THESIS: Every product is handed over the way a pharmacist hands it over: name large, what it is for, how to use it, in plain words on a printed label, with the pack beside it. The label is the unit of the whole site. It refuses the lifestyle-hero-plus-card-grid wellness store, and it refuses the kicker-above-heading habit outright.

OWN-WORLD: Counter-mint laminate ground (#dfeae3) with white label paper panels; near-black label ink (#141a1f); magenta (#dd1860) only as the stamp on the active control and the logo; Heritage gold (#b8924a) as a thin crest rule on Heritage items; Rheuma-Salve pack mint (#a9d8c3) as the pain-relief bay colour. One typeface, Archivo variable, set heavy and slightly narrow for label names, regular for everything else; tabular numerals for prices and dosages. Dotted thermal rules separate label fields; price and pack sizes are tear-off tabs with a perforation edge; selected tab sits proud with a tick. No cards-with-icons, no eyebrows, no gradients, no shadows beyond a 1px paper lift. Icons are 1.5px stroke SVG, one family. Raises from the declined hand: labelled physical controls (cassette deck), gated block-stepped checkout (installer), state by mark not hue (jackfield), one twelve-column counter grid (oscilloscope), one dominant action per phone screen (rain garden), colour only on the active element (plankton).

STORY: The visitor reads "What are you here for?", picks pain or cough, is shown which format fits which situation before any grid, sees one honest label per product with the pack size they chose and its price, adds it to a bag that counts like a collection ticket, and checks out in three gated steps with delivery, safety and stockist answers in sight. They believe this is a pharmacy, not a wellness brand.

FIRST VIEWPORT: Desktop: a counter-wide label panel spanning 10 of 12 columns, top-left the HST logo lock-up on the paper; label block reads "HST MEDICAL · DISPENSED FOR YOU" as a plain first line in regular weight (not a kicker: it is the label's own header row with a dotted rule under it), then the h1 in Archivo 900 narrow at ~5rem: "Pain, cough or cold? Start here." Under it a dosage-style line: "Pharmacist-formulated remedies, made in Singapore since 1994, on the shelf at Guardian, Watsons and NHGP." Right third of the panel: the real Rheuma-Salve 50g jar standing on the mint counter, with its own small tear-off tab "Best seller · S$10.10". Bottom row of the panel: five large labelled counters, each a tab: Pain relief, Cough and cold, Kids, Sleep, Tonics; the first carries the magenta stamp "Start here". Phone: the h1 and the five counters only; the jar sits below the counters.

FORM: The Dispensing Counter (Singapore polyclinic and Guardian dispensary: printed dispensing label, pigeonhole shelf, queue board); candidate 7 on my ordered grounded list; seed key 65499c71; code-led.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.
