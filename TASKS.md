# HST Medical website — remaining tasks

Status as of 2026-10-02. The design prototype (this repo) is done and pushed as an unlisted test link.
Everything below is what stands between the prototype and a submitted proposal / a production site.

## A. Before the proposal is submitted (marketing + sales)
1. **Client review of the prototype.** Walk HST / McGallen & Bolden through the test link; collect feedback on tone, hierarchy, the two featured ranges and the reseller flow.
2. **Confirm facts flagged as placeholders** in the prototype: customer-service email, registered address and phone, retailer list beyond Guardian / Watsons / NHGP (Unity, clinics), awards wording, Halal-certified SKU list, free-delivery threshold (S$60 assumed), GST-inclusive pricing.
3. **Decide the language strategy.** The current site mixes seven languages; the prototype is English-only. Recommend EN + ZH on product pages, with Chinese product names already present in the live store titles.
4. **Write the RFP response document**: approach & architecture (classic theme on GeneratePress, EasyCart compatibility plan), portfolio (TRE Singapore, HummingBeing, technext.asia as lightweight typography-led builds), timeline & milestones, fixed fee + maintenance tiers. Attach the prototype link and the performance budget from WP-MAPPING.md.
5. **Optional annex: Odoo B2B reseller portal** (trade accounts, pricelists, re-orders, territory-manager routing). Positioned as Phase 2, never as a replacement for the WordPress storefront the RFP mandates.
6. **Content inventory of hstmedical.com**: full URL list for the 301 redirect map, existing blog posts, policy pages, multilingual pages, Trustindex reviews, award assets.

## A2. Done 2026-10-02: Impeccable audit + redesign
Critique scored the first prototype 23/40 (full report in `.impeccable/critique/`). Redesign shipped (finish review: ship):
start-by-need counters, compare tables before grids on the two focus ranges, real pack-size radios that re-price the
product page, bag with steppers/undo/free-delivery meter, gated 3-step checkout with inline validation and aria-live,
store search with empty state, cart icon outside the hamburger, heading order fixed, 44px targets, soft white rendition
pinned by the client. Polish leftovers (not blockers): SVG instead of the two ✓ glyphs in form success and step bar;
hover state on pack tiles; chevron instead of rotated + on open accordions; cap the phone product image height; move
item codes off consumer pack chips; trim the Google Fonts request to the four weights used; brand line under the card
title; drop the border on hover-lifted cards. Re-run `/impeccable critique` after these to record the new score.

## B. Design and content completion (prototype → final design)
7. **Product copy pass on all 51 SKUs.** Catalogue text is lifted verbatim; the 12 focus SKUs need a benefit-led rewrite and the remaining 39 need a consistency edit (tagline, 3–5 benefits, usage, ingredients, origin).
8. **Photography.** Product images come from the catalogue PDF (max ~900px, some with box-and-jar composites). Request original packshots (2000px, transparent background) and 2–3 lifestyle images per featured range.
9. **Hero and OG imagery**: one lifestyle hero per featured range; a proper 1200×630 OG image per key page (currently a logo placeholder).
10. **Where-to-buy locator**: decide between a static retailer list (as now) and a postcode locator (Phase 2 widget).
11. **Kowa cross-brand block**: confirm whether Vantelin / Three Dimension Mask are to be listed or linked (shown in the client's brand banner).
12. **Legal pages**: privacy (PDPA), terms of sale, shipping & returns, cookie notice; supplied by the client.
13. **Accessibility audit** (WCAG 2.2 AA): colour contrast on magenta text, focus order in the mobile nav, form labels and error states, `details` keyboard behaviour.
14. **Blog programme**: three sample articles exist; agree a 12-article editorial calendar (seasonal cough & cold, pain-relief how-tos, certification explainers, kids' nutrition).

## C. WordPress build (production, per RFP)
15. **Scaffold the classic child theme** on GeneratePress (header.php, footer.php, front-page.php, page.php, index.php, single.php, 404.php, functions.php, style.css), porting the tokens from `assets/css/style.css`.
16. **EasyCart integration**: store, category, product, cart and checkout wrappers; CSS override file for `.ec_product_*`, `.ec_cart_*`, `.ec_checkout_*`; product tabs for Benefits / Usage / Ingredients; pack-size variants mapped to EasyCart options.
17. **Menus and widget areas** registered; Classic Editor + Classic Widgets enforced; Gutenberg disabled.
18. **Schema module** (`inc/schema.php`): Organization, WebSite, Product + Offer from EasyCart data, BreadcrumbList, CollectionPage/ItemList, FAQPage, Article.
19. **GEO files**: llms.txt served from theme root, clean permalinks, no JS-dependent content.
20. **Performance pass**: WebP pipeline, explicit image dimensions, font subsetting, no jQuery, defer scripts, cache headers; measure with PageSpeed on the throttled 4G mobile profile and document the Core Web Vitals report (RFP deliverable).
21. **Theme Check**: zero errors/warnings; GPL headers; WordPress.org review readiness (RFP deliverable).
22. **Widget & menu configuration guide** for the client's editors (RFP deliverable).
23. **Migration**: content and product import from the current Astra/Elementor site, 301 redirect map (old `/store/<slug>/` URLs kept where possible), multilingual decision applied.
24. **Analytics**: GA4 + GTM with EasyCart ecommerce events (view_item, add_to_cart, purchase) and reseller-form conversion; Search Console verification and sitemap submission.
25. **Staging → launch**: staging on the client's host, UAT checklist, DNS cut-over, post-launch crawl and 404 sweep.

## D. Marketing follow-through (after launch)
26. Reseller nurture (email sequence to trade enquiries), seasonal cough & cold campaign landing pages, Rheuma-Salve® patch launch content, retailer co-marketing with Guardian / Watsons, review collection (Trustindex → Google), and quarterly SEO/GEO reporting.
