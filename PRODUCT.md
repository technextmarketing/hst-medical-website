# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Static HTML/CSS/JS prototype assembled by `_src/build.py` from `_src/products.json` and `_src/parts/`. It stands in for the production target the RFP mandates: a classic WordPress theme (GeneratePress child allowed, strictly no Gutenberg/FSE) with WP EasyCart as the store. Every template must remain portable to `header.php`, `footer.php`, `front-page.php`, `page.php`, `single.php`, `404.php` and EasyCart CSS overrides (see WP-MAPPING.md). Hosted as an unlisted GitHub Pages test link until client sign-off.

## Users

Primary (confirmed 2026-10-02): the Singapore consumer, typically 45+, who already knows Rheuma-Salve®, Heritage® or Zoo-Vite® from a Guardian, Watsons or NHGP shelf, and arrives in pain, with a cough or cold, or shopping for family. They need to pick the right format (balm, crème, liniment, patch, stick; lozenge, syrup, capsule, inhaler), see the price and pack sizes, and either buy with island-wide delivery or find a stockist. Most arrive on a phone.

Secondary: trade buyers (pharmacy category managers, GP clinics, TCM halls, e-commerce sellers, overseas distributors) who evaluate the range and order through an HST Medical territory manager or resellercontact@hstmedical.com. They need product sheets, pack configurations and a clear enquiry path, not a storefront.

Tertiary: the RFP evaluators at HST Medical / Kowa and the issuing agency (McGallen & Bolden), judging whether the design is typography-centric, mobile-first, graphics-lite and portable to classic WordPress.

## Product Purpose

hstmedical.com is the brand home and direct store for HST Medical Pte Ltd, a Singapore manufacturer and supplier of health supplements and pain-relief remedies since 1994, a Kowa subsidiary since 2024. The site must make the right product easy to choose and buy, route trade enquiries to territory managers, and present the brand with pharmacy-counter credibility. Success: a visitor in pain or with a cough identifies the right product within one screen, adds the correct pack size at the correct price, and reaches checkout with no unanswered question about delivery, safety or where else to buy.

## Positioning

Formulated by HST Medical's own pharmacists and TCM physicians, made under GMP in Singapore, and stocked in the national pharmacy chains for thirty years. The range deliberately spans two registers that competitors sell separately: contemporary pharmaceutical-grade supplements (HST Medical®) and traditional Asian remedies prepared to modern standards (Heritage®, Rheuma-Salve®). Kowa's ownership adds Japanese pharmaceutical lineage (Vantelin, Three Dimension Mask) that no local supplement brand can claim.

## Operating Context

- Two focus ranges for this engagement: Premium Pain Relief (6 Rheuma-Salve® SKUs) and Cough, Cold & Flu (6 SKUs), taken from the last page of the product-sheet catalogue.
- 51 SKUs across 11 ranges; many sold as single, twin, triple, value and travel packs with distinct item codes. Live SGD prices exist for 48 SKUs (scraped from the current EasyCart store); Maxi-Cal, Sleep Fast Gummies and Libi-Max have no public price.
- Retail: Guardian, Watsons, NHGP pharmacies (confirmed on the current site). Unity, clinics and online marketplaces are unconfirmed and marked as such.
- Trade ordering today runs on email and territory managers; the catalogue prints "For orders please contact your HST Medical territory manager" on every sheet.
- Regulatory tone: every product page carries "Always read the label and follow directions for use." Health claims are limited to the catalogue's own benefit statements.
- Languages: the current site mixes seven; the prototype is English-only. Chinese product names exist in live store titles. Decision pending with the client.

## Capabilities and Constraints

- Store, category, product, cart and checkout layouts must be achievable as CSS overrides on WP EasyCart's wrappers (`.ec_product_*`, `.ec_cart_*`, `.ec_checkout_*`). Variant-to-price binding is an EasyCart product-option feature; the prototype must model it honestly.
- Performance budget from the RFP: mobile-first, instant on 4G/LTE, no carousels, no heavy animation scripts, minimal payload. Current home page is 26 KB HTML, 18 KB CSS, 5.5 KB JS, product images as WebP with explicit dimensions.
- SEO and GEO: semantic HTML5, clean permalinks, JSON-LD (Organization, WebSite, Product+Offer, BreadcrumbList, CollectionPage, FAQPage, Article), sitemap, llms.txt, content readable without JavaScript.
- Code must pass WordPress.org Theme Check and GPL review when ported.
- Prototype flag: `PROTOTYPE = True` in `_src/build.py` adds noindex to every page and a robots Disallow; the "Design prototype" top bar is removed at launch.
- Undecided: language strategy, store-locator depth, whether Vantelin / Three Dimension Mask are listed, customer-service contact details, exact retailer list, free-delivery threshold (S$60 assumed).

## Brand Commitments

Confirmed binding on 2026-10-02:
- The HST Medical logo (magenta roundel with the figure mark, "HST MEDICAL" wordmark, "Kowa Subsidiary" line) and its magenta (#dd1860 sampled) stay.
- The Kowa relationship is shown, not hidden.
- Pack colours may become system colours: Rheuma-Salve® mint green and gold, Heritage® cream-and-gold boxes, HST Medical® teal/colour-coded packs, Zoo-Vite® primaries.
- Brand names carry ® on first use per range: HST Medical®, Heritage®, Rheuma-Salve®, Zoo-Vite®.
- Voice: plain, pharmacist-direct, no hype, no medical overreach.
- No brand kit exists; typography, grid and components are open within the RFP's typography-centric, graphics-lite rule.
- Standing visual preference (user, 2026-10-02, two rounds): first "much cleaner and simpler, softer"; then a reference to modern online-pharmacy templates (MediHeal / Pharmico style: deep solid colour hero block with rounded corners, white floating header bar with logo, categories, search and cart, white headline on colour, pill CTAs, large product shot with a floating product card, category tiles with product images on light grey, product cards in grey wells with dark pill buttons, benefits strip, coloured testimonial band) "but follow the logo colour scheme, still clean". Palette is therefore the logo's: HST magenta (#dd1860 / #b3124c fields) + the wordmark slate (#3d4a57) + white, with light grey wells. No stock photography of people (none exists; never fabricate), no testimonials (none exist), no carousels. Keep the structural model (start-by-need tiles, compare-first categories, honest pack sizes, gated checkout).

## Evidence on Hand

- Product-sheet catalogue PDF (54 pages, Heyzine flipbook 1cbc07dcc6): descriptions, benefits, usage, active ingredients, origin, item codes for all 51 SKUs. Parsed to `_src/products.json`.
- Product images extracted from the catalogue to `assets/img/products/` (51 WebP at up to 900 px plus thumbnails). Sinus Clear (p31) is a tall narrow inhaler crop that reads poorly at thumbnail size.
- Logo PNG from the live site at `assets/img/logo-hst-kowa.png`.
- Live store prices and URLs for 48 SKUs (`ext/store.json` in the session scratchpad; values embedded in products.json).
- Current-site claims not yet substantiated by the client: 5.0 Google rating (Trustindex), 2024 Beauty Insider Awards, Guardian award. Shown with a "to be confirmed" note.
- Absent, must not be fabricated: customer testimonials, clinical studies, sales figures, pharmacist names, exact outlet counts, lifestyle photography, customer-service phone and address.

## Product Principles

1. Lead with the buyer's problem, not the brand's story: pain, cough, cold, kids, sleep.
2. Choosing comes before buying: every range shows which format fits which situation before it shows a grid.
3. Honest commerce: the pack size you choose is the price you pay; no claim without a label behind it.
4. Pharmacy-counter trust: GMP, Halal, origin, usage and cautions are first-class content, not footnotes.
5. Light enough for a 4G phone and plain enough for the Classic Editor: no effect that WordPress editors cannot maintain.

## Accessibility & Inclusion

Primary users skew 45+ and shop on phones: body text at 17 px minimum, touch targets at 44 px, AA contrast on all text including small labels, keyboard-operable variant selection and accordions, reduced-motion alternatives that preserve state changes rather than a global kill.
