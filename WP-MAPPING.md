# Prototype → Classic WordPress theme mapping

The prototype is static HTML so the client can review design, structure, copy, SEO and GEO before any
WordPress work. Every template below maps 1:1 to a classic theme file (GeneratePress child theme or
standalone), with no blocks, no FSE and no theme.json layout dependency, as the RFP requires.

| Prototype | Classic WordPress file | Notes |
|---|---|---|
| `_src/parts/head.html` | `header.php` | `wp_head()`, `wp_nav_menu('primary')`, EasyCart cart link via `ec_cart_count` shortcode / template tag |
| `_src/parts/footer.html` | `footer.php` | Four Classic Widget areas (`register_sidebar`) + legal bar; `wp_footer()` |
| `index.html` (home) | `front-page.php` | Hero, two featured ranges (EasyCart category shortcodes), shop-by-need grid, brands, best sellers, where-to-buy, journal (latest 3 posts via `WP_Query`) |
| `shop/` | EasyCart store page (`[ec_store]`) wrapped by `page-store.php` | Filters/search = EasyCart's own; CSS overrides target `.ec_product_type1` etc. |
| `shop/<category>/` | EasyCart category view (`/store/<category>/`) + `page.php` guide blocks | "How to choose" table and FAQ live in the Classic Editor as HTML; FAQ schema via a tiny shortcode |
| `products/<slug>/` | EasyCart single product (`/store/<slug>/`) | Layout = CSS overrides on EasyCart's product wrapper; Benefits/Usage/Ingredients = EasyCart product tabs or native `<details>` in the description field |
| `cart/`, `checkout/` | EasyCart cart & checkout pages | Styled through `wp-easycart` CSS override file only; no template forking |
| `about/`, `brands/`, `where-to-buy/`, `resellers/`, `contact/`, `privacy/` | `page.php` | Classic Editor (TinyMCE) content; forms via the client's preferred classic form plugin |
| `blog/` | `index.php` / `archive.php` | Standard loop |
| `blog/<slug>/` | `single.php` | Article schema via `wp_head` hook |
| `404.html` | `404.php` | |
| `assets/css/style.css` | child theme `style.css` | `:root` tokens → GeneratePress Customizer colours and typography |
| `assets/js/site.js` | `assets/js/site.js` enqueued with `wp_enqueue_script(..., [], ver, true)` | ~3 KB, no jQuery; mobile nav, reveal, demo cart (removed in production; EasyCart handles the cart) |
| `sitemap.xml`, `robots.txt`, `llms.txt` | WordPress core sitemap + `robots.txt` filter; `llms.txt` served from the theme root via a rewrite rule | GEO: plain-text entity map for AI crawlers |
| JSON-LD (Organization, WebSite, Product+Offer, BreadcrumbList, CollectionPage/ItemList, FAQPage, Article) | `inc/schema.php` hooked to `wp_head` | Pulls product data from EasyCart tables, no SEO plugin lock-in |

## Performance budget carried into the theme
- One web font (Archivo, used at 400–700, `display=swap`) for display and body.
- No carousels, no animation libraries, no jQuery. Reveal effect is CSS + a 10-line IntersectionObserver, disabled under `prefers-reduced-motion`.
- Images as WebP with explicit `width`/`height` (CLS ≈ 0), `loading="lazy"` below the fold, `fetchpriority="high"` on the single hero/product image.
- Target: PageSpeed mobile ≥ 90 on a throttled 4G profile, total page weight < 400 KB on product pages.

## Editorial model (Classic Editor only)
- Menus: Primary (header), Footer Shop, Footer Company, Footer Help.
- Widget areas: Footer 1–4, Shop sidebar (optional), Product below-content.
- Product data stays in EasyCart; category guide and FAQ content is ordinary page HTML editable in TinyMCE.
