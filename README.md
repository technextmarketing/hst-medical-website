# HST Medical — website design prototype

Static prototype built for the hstmedical.com redesign RFP (classic WordPress + WP EasyCart,
typography-centric, mobile-first, SEO + GEO). Reviewed as an unlisted test link; every page is
`noindex,nofollow` and `robots.txt` disallows crawling until client sign-off.

Design (2026-10-02, after the Impeccable audit + redesign): clean, soft and white, close to the live
hstmedical.com, with a pharmacy-counter structure: start-by-need counters on the home page, "Which one
do I need?" compare tables before any product grid, honest pack-size radios that re-price the product
page, a bag with steppers, undo and a free-delivery meter, and a gated three-step checkout. Design
decisions live in `DESIGN.md`; product truth in `PRODUCT.md`; the direction contract in
`.impeccable/surfaces/index-html.md`.

- Test link: https://technextsg.github.io/hst-medical-website/
- Local preview: `serve-hst-medical.bat` at the Marketing drive root → http://localhost:3973 (launch name `hst-medical`)
- Source of truth: `_src/` (templates + data). Edit there, then run `python _src/build.py` from this folder.

## Structure
```
_src/build.py            page assembler (templates for every page type; PROTOTYPE flag)
_src/catalogue_parse.py  catalogue PDF → products.json (51 SKUs, prices from the live store)
_src/products.json       product data
_src/parts/              head.html (header + nav), footer.html
assets/css/style.css     design tokens + components (maps to a GeneratePress child theme)
assets/js/site.js        ~3 KB progressive enhancement
assets/img/products/     51 WebP product images (900px + 360px thumb) from the product-sheet catalogue
index.html, shop/, shop/<category>/ (11), products/<slug>/ (51), about/, brands/, where-to-buy/,
resellers/, blog/ (+3 posts), contact/, cart/, checkout/, privacy/, 404.html
sitemap.xml, robots.txt, llms.txt
```
See `WP-MAPPING.md` for how each template becomes a classic WordPress file, and `TASKS.md` for the
remaining work.
