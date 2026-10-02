"""
HST Medical — prototype site assembler.

    python _src/build.py

Reads _src/products.json (from catalogue_parse.py) and writes every page to the site root as
<folder>/index.html (clean URLs, served natively by GitHub Pages and by classic WordPress permalinks).
Templates below map 1:1 to classic WordPress files — see WP-MAPPING.md.

Prototype flags: every page carries <meta name="robots" content="noindex,nofollow"> and robots.txt
disallows crawling (test link until sign-off). Flip PROTOTYPE = False to produce the indexable build.
"""
import json, os, re, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
BASE = "https://technextmarketing.github.io/hst-medical-website/"
V = "20261002a"           # cache-buster for CSS/JS
PROTOTYPE = True
TODAY = datetime.date.today().isoformat()

DATA = json.load(open(os.path.join(HERE, "products.json"), encoding="utf-8"))
CATS, PRODUCTS = DATA["categories"], DATA["products"]
BY_SLUG = {p["slug"]: p for p in PRODUCTS}
FOCUS_CATS = ["pain-relief", "cough-cold-flu"]
CAT_ORDER = ["pain-relief", "cough-cold-flu", "traditional-pain-relief", "bones-joints", "immunity-allergy",
             "immunity-energy", "beauty-wellness", "kids", "alertness-memory-vision", "stress-sleep", "heart-liver-vitality"]
RETAILERS = ["Guardian", "Watsons", "NHGP pharmacies", "Unity", "Selected clinics & TCM halls", "Online marketplaces"]

# Hand fixes where the catalogue layout differs from the standard sheet
OVERRIDES = {
    "rheuma-salve-pain-relief-patch-cool": {"description": "The Rheuma-Salve® Pain Relief Patch (Cool) is a plaster that delivers fast-acting, cool-sensation relief directly to the source of pain. Each pack contains 8 soft, flexible 10 × 7 cm patches that are gentle on the skin and engineered for muscle aches, sprains, strains, joint pain, backaches, sports recovery and delayed onset muscle soreness (DOMS).", "country": "Made in Taiwan exclusively for HST Medical Pte Ltd (brand of Singapore)"},
    "sinus-clear-2-in-1": {"tagline": "Relief from blocked nose and headaches"},
    "shou-wu-hair-plus": {"description": "A traditional herbal formula built around He Shou Wu and wolfberry to replenish vital essence and nourish the blood, with Chinese angelica, ginseng and cordyceps to improve circulation to the scalp and support healthy hair growth and natural colour."},
    "liver-gard-forte": {"benefits": ["Supports liver detoxification", "Protects liver cells from oxidative stress", "Supports healthy liver function and energy"]},
}
for slug, o in OVERRIDES.items():
    BY_SLUG[slug].update(o)
for p in PRODUCTS:
    if not p["tagline"]:
        p["tagline"] = CATS[p["category"]]["name"]

# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape(s, quote=True)

def money(v):
    return "S$%.2f" % v if v is not None else "Price on request"

def brand_class(b):
    return {"Heritage": "heritage", "Zoo-Vite": "zoo"}.get(b, "")

def brand_label(b):
    return {"Heritage": "Heritage®", "Zoo-Vite": "Zoo-Vite®", "HST Medical": "HST Medical®"}.get(b, b)

def cat_products(cid):
    return [p for p in PRODUCTS if p["category"] == cid]

def read(name):
    with open(os.path.join(HERE, "parts", name), encoding="utf-8") as f:
        return f.read()

def write(rel, content):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

def jsonld(obj):
    return '<script type="application/ld+json">%s</script>\n' % json.dumps(obj, ensure_ascii=False)

ORG = {"@type": "Organization", "@id": BASE + "#org", "name": "HST Medical Pte Ltd", "url": BASE,
       "logo": BASE + "assets/img/logo-hst-kowa.png", "parentOrganization": {"@type": "Organization", "name": "Kowa Company, Ltd."},
       "foundingDate": "1994", "address": {"@type": "PostalAddress", "addressCountry": "SG"},
       "sameAs": ["https://hstmedical.com"]}

# ---------------------------------------------------------------- layout
def product_card(p, root, reveal=True):
    img = "%sassets/img/products/%s-thumb.webp" % (root, p["image"])
    url = "%sproducts/%s/" % (root, p["slug"])
    search = ("%s %s %s %s" % (p["name"], p["brand"], CATS[p["category"]]["name"], p["tagline"])).lower()
    price = ("<span class='price'>%s <small>SGD</small></span>" % esc(money(p["price"]))) if p["price"] else "<span class='price small'>Price on request</span>"
    return f"""<article class="product{' reveal' if reveal else ''}" data-cat="{p['category']}" data-search="{esc(search)}">
  <a class="img" href="{url}" tabindex="-1" aria-hidden="true"><img src="{img}" alt="" width="360" height="360" loading="lazy" decoding="async"></a>
  <span class="brand-line {brand_class(p['brand'])}">{esc(brand_label(p['brand']))}</span>
  <h3><a href="{url}">{esc(p['name'])}</a></h3>
  <span class="size">{esc(p['size'])}</span>
  {price}
  <button class="btn btn-outline btn-sm" data-add="{p['slug']}" data-name="{esc(p['name'])}" data-price="{p['price'] or 0}" data-img="assets/img/products/{p['image']}-thumb.webp" data-url="products/{p['slug']}/">Add to cart</button>
</article>"""


def crumbs(root, items):
    """items = [(label, href|None)] — renders breadcrumbs + BreadcrumbList schema."""
    lis = ['<li><a href="%s">Home</a></li>' % root]
    ld = [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE}]
    for i, (label, href) in enumerate(items, start=2):
        lis.append('<li><a href="%s">%s</a></li>' % (href, esc(label)) if href else '<li aria-current="page">%s</li>' % esc(label))
        ld.append({"@type": "ListItem", "position": i, "name": label, **({"item": href.replace(root, BASE, 1)} if href else {})})
    return '<ol class="crumbs" aria-label="Breadcrumb">%s</ol>' % "".join(lis), jsonld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ld})


def page(out_rel, title, desc, body, active="", extra_head="", og_image=None, body_class="", root=None):
    depth = out_rel.count("/")
    root = ("../" * depth) if root is None else root
    canonical = BASE + (out_rel[:-len("index.html")] if out_rel.endswith("index.html") else out_rel)
    if canonical.endswith("/index.html"):
        canonical = canonical[:-10]
    robots = '<meta name="robots" content="noindex,nofollow">\n' if PROTOTYPE else ""
    og = og_image or (BASE + "assets/img/og-cover.png")
    head = read("head.html").replace("{{TITLE}}", esc(title)).replace("{{DESC}}", esc(desc)).replace("{{ROOT}}", root) \
        .replace("{{CANONICAL}}", canonical).replace("{{ROBOTS}}", robots).replace("{{V}}", V).replace("{{OG}}", og) \
        .replace("{{EXTRA}}", extra_head).replace("{{BODYCLASS}}", body_class)
    for nid in ["home", "shop", "pain", "cough", "brands", "resellers", "about", "blog", "contact"]:
        head = head.replace("{{A_%s}}" % nid, ' class="active"' if nid == active else "")
    foot = read("footer.html").replace("{{ROOT}}", root).replace("{{V}}", V).replace("{{YEAR}}", str(datetime.date.today().year))
    write(out_rel, head + body.replace("{{ROOT}}", root) + foot)
    return canonical


SITEMAP = []
def add_sitemap(url, prio="0.6"):
    SITEMAP.append((url, prio))

# ---------------------------------------------------------------- content: focus-category guides
GUIDES = {
    "pain-relief": {
        "intro": "Rheuma-Salve® has been Singapore's pharmacy-shelf pain relief since 1994. The range now comes in five formats, so the right pick depends on where it hurts, how long you need relief, and whether you are at home, at work or on the move.",
        "table": [
            ("Rheuma-Salve® Balm", "Deep joint and muscle pain, stiffness, chest congestion", "Rub in 3–4× a day", "rheuma-salve-balm"),
            ("Rheuma-Salve® Crème", "Everyday aches; non-greasy, absorbs fast under clothing", "Rub in 3–4× a day", "rheuma-salve-creme"),
            ("Rheuma-Salve® Liniment", "Fast penetrating oil for sprains and sports strains", "Massage into the area", "rheuma-salve-liniment"),
            ("Pain Relief Patch (Cool)", "Hands-free relief up to 6 hours: back, neck, shoulders, DOMS", "Apply to clean dry skin, 2–3× daily", "rheuma-salve-pain-relief-patch-cool"),
            ("On-the-Go Medi-Stick", "Pocket-sized, mess-free for desk, gym bag and travel", "Glide on as needed", "rheuma-salve-medi-stick"),
        ],
        "faq": [
            ("What is the difference between the balm and the crème?", "The balm is a snowy-white, menthol-rich salve with a stronger warming-cooling action for deep joint and muscle pain. The crème uses the same proprietary formula in a lighter, non-greasy base that absorbs quickly and does not stain clothing."),
            ("How long can I wear the Pain Relief Patch?", "Apply to clean, dry skin and remove after 6 hours. Use 2 to 3 patches a day at most, and do not apply to open wounds or during pregnancy or breastfeeding."),
            ("Is Rheuma-Salve® made in Singapore?", "Yes. The balm, crème, liniment and Medi-Stick are made in Singapore under GMP. The patch is manufactured in Taiwan exclusively for HST Medical."),
            ("Where can I buy Rheuma-Salve® in Singapore?", "Guardian, Watsons and NHGP pharmacies stock the range, and every product ships from this online store. Retailers and clinics can order through their HST Medical territory manager."),
        ],
    },
    "cough-cold-flu": {
        "intro": "Six herbal remedies cover the full arc of a cold, from the first tickle in the throat to a blocked nose that will not clear. All are formulated by HST Medical's pharmacists and TCM physicians, and most are Halal-certified.",
        "table": [
            ("Alievaid Herbal Drops", "Sore throat, irritating cough, fresh breath", "1 drop every 2–3 h (max 8/day), 12+ years", "alievaid-herbal-drops"),
            ("Cough Alievaid Herbal Lintus", "Productive cough with phlegm", "Syrup, by the label", "cough-alievaid-herbal-lintus"),
            ("Flu Gard Herbal Remedy", "Fever, body aches, runny nose, sneezing", "2–6 vegicaps, 3× daily after food", "flu-gard"),
            ("Ivy Leaf Cough Syrup", "Dry or chesty cough; single-dose sachets for travel", "1 sachet, by the label", "ivy-leaf-cough-syrup"),
            ("Ivy Leaf Drops", "Cough and sore throat relief on the go", "Dissolve slowly in the mouth", "ivy-leaf-drops"),
            ("Sinus Clear 2-in-1", "Blocked nose, sinus headache, insect bites", "Inhale; dab the applicator on temples", "sinus-clear-2-in-1"),
        ],
        "faq": [
            ("Which product should I take for a sore throat?", "Start with Alievaid Herbal Drops or Ivy Leaf Drops. Both are lozenges you dissolve slowly, with loquat leaf, jie geng and luo han guo (Alievaid) or ivy leaf extract (Ivy Leaf) to soothe the throat and calm an irritating cough."),
            ("Is Flu Gard suitable for children?", "Flu Gard is a traditional Chinese medicine formula in vegicaps for adults. Follow the label and consult a pharmacist for children, pregnancy or if symptoms persist beyond a few days."),
            ("Are these products Halal?", "Alievaid Herbal Drops carry Halal (Malaysia) certification and several other products in the range are Halal-certified. The certification mark is printed on each product page and pack."),
            ("Can I use Sinus Clear more than once?", "Yes. The bottom half is a refill: a few drops onto the inhaler's cotton stick restores it. Single-person use is recommended."),
        ],
    },
}

# ---------------------------------------------------------------- HOME
def build_home():
    root = ""
    focus_blocks = ""
    for cid in FOCUS_CATS:
        c = CATS[cid]; ps = cat_products(cid)
        cards = "\n".join(product_card(p, root) for p in ps[:4])
        focus_blocks += f"""
<section class="section{' tint' if cid == 'cough-cold-flu' else ''}" id="{cid}">
  <div class="container">
    <div class="toolbar section-head reveal">
      <div><span class="eyebrow">Featured range</span><h2>{esc(c['name'])}</h2><p>{esc(c['blurb'])}</p></div>
      <a class="btn btn-outline" href="shop/{cid}/">See all {len(ps)} products</a>
    </div>
    <div class="products">{cards}</div>
  </div>
</section>"""
    cat_cards = ""
    for cid in CAT_ORDER:
        c = CATS[cid]; n = len(cat_products(cid))
        cat_cards += f"""<a class="card cat-card card-link reveal{' focus' if cid in FOCUS_CATS else ''}" href="shop/{cid}/">
  {'<span class="badge">Featured</span>' if cid in FOCUS_CATS else ''}<h3>{esc(c['name'])}</h3><p>{esc(c['blurb'])}</p><span class="count">{n} product{'s' if n != 1 else ''} →</span></a>"""
    best = [BY_SLUG[s] for s in ["rheuma-salve-balm", "deep-sea-squalene", "pearl-powder", "crocodile-pure-skin-oil"]]
    best_cards = "\n".join(product_card(p, root) for p in best)
    posts_html = "\n".join(f"""<a class="card post-card card-link reveal" href="blog/{s}/"><time datetime="{d}">{d}</time><h3>{esc(t)}</h3><p>{esc(x)}</p></a>""" for s, t, d, x, _ in POSTS)
    body = f"""
<main id="main">
<section class="hero">
  <div class="container hero-inner">
    <div>
      <span class="eyebrow">HST Medical · a Kowa subsidiary · Singapore since 1994</span>
      <h1>Trusted relief and <em>daily wellness</em>, formulated by pharmacists and TCM physicians.</h1>
      <p class="lead">Home of Rheuma-Salve® pain relief, Heritage® tonics and Zoo-Vite® kids' supplements. Made under GMP, sold in Singapore's leading pharmacies and shipped from this store.</p>
      <div class="btn-row">
        <a class="btn btn-primary" href="shop/pain-relief/">Shop pain relief</a>
        <a class="btn btn-outline" href="shop/cough-cold-flu/">Cough, cold &amp; flu</a>
      </div>
      <ul class="trust">
        <li>{CHECK} GMP-certified manufacturing</li>
        <li>{CHECK} Halal-certified options</li>
        <li>{CHECK} In Guardian, Watsons &amp; NHGP</li>
        <li>{CHECK} 30 years in Singapore</li>
      </ul>
    </div>
    <figure class="hero-media">
      <img src="assets/img/products/p03.webp" alt="Heritage Rheuma-Salve Balm 50g jar and box" width="536" height="536" fetchpriority="high" decoding="async">
      <figcaption>Rheuma-Salve® Balm — Singapore's best-selling pain relief balm</figcaption>
    </figure>
  </div>
</section>
{focus_blocks}
<section class="section" id="shop-by-need">
  <div class="container">
    <div class="section-head reveal"><span class="eyebrow">Shop by need</span><h2>Eleven ranges, one quality standard.</h2><p>Every product is developed by HST Medical's own pharmacists and TCM physicians from ethically sourced ingredients, then tested for authenticity and safety before it reaches the shelf.</p></div>
    <div class="grid grid-3">{cat_cards}</div>
  </div>
</section>
<section class="section heritage-tint" id="brands">
  <div class="container">
    <div class="grid grid-2">
      <div class="reveal">
        <span class="eyebrow">Two brands, one standard</span>
        <h2>HST Medical® and Heritage®</h2>
        <p><strong>HST Medical®</strong> is the contemporary line: pharmaceutical-grade supplements, cough and cold remedies and sleep support with clear, evidence-led formulas.</p>
        <p><strong>Heritage®</strong> carries the traditional Asian remedies: Rheuma-Salve®, ginseng, cordyceps, lingzhi, pearl powder and medicated oils, prepared to modern GMP standards.</p>
        <p><strong>Zoo-Vite®</strong> brings the same care to children's gummies and jelly sticks. Since 2024 all three are part of <strong>Kowa</strong>, the Japanese pharmaceutical group behind Vantelin.</p>
        <div class="btn-row"><a class="btn btn-outline" href="brands/">Explore the brands</a></div>
      </div>
      <div class="grid" style="grid-template-columns:1fr 1fr;gap:1rem">
        <div class="card reveal"><div class="stat">1994</div><p>Founded in Singapore as a manufacturer and supplier to major pharmacies.</p></div>
        <div class="card reveal"><div class="stat">50+</div><p>Products across pain relief, immunity, beauty, kids, sleep and vitality.</p></div>
        <div class="card reveal"><div class="stat">GMP</div><p>Strict adherence to authority guidelines from R&amp;D to packaging.</p></div>
        <div class="card reveal"><div class="stat">5.0</div><p>Google customer rating on the current store (Trustindex-verified).</p></div>
      </div>
    </div>
  </div>
</section>
<section class="section" id="best-sellers">
  <div class="container">
    <div class="toolbar section-head reveal"><div><span class="eyebrow">Best sellers</span><h2>What Singapore buys most.</h2></div><a class="btn btn-outline" href="shop/">Browse the whole store</a></div>
    <div class="products">{best_cards}</div>
  </div>
</section>
<section class="section tint" id="where-to-buy">
  <div class="container">
    <div class="grid grid-2">
      <div class="reveal"><span class="eyebrow">Where to buy</span><h2>On the shelf at Singapore's leading pharmacies.</h2><p>Find HST Medical®, Heritage® and Zoo-Vite® at the retailers below, or order here with island-wide delivery.</p>
        <ul class="where">{''.join('<li>%s</li>' % esc(r) for r in RETAILERS)}</ul>
        <div class="btn-row"><a class="btn btn-ghost" href="where-to-buy/">Store locator and partners →</a></div></div>
      <div class="cta reveal"><div><h2 style="font-size:1.6rem">Retailers, clinics and distributors</h2><p>Open a trade account, download the product sheets and order through your HST Medical territory manager.</p></div><div><a class="btn btn-primary" href="resellers/">Become a reseller</a></div></div>
    </div>
  </div>
</section>
<section class="section" id="journal">
  <div class="container">
    <div class="toolbar section-head reveal"><div><span class="eyebrow">Health notes</span><h2>Short, practical reading.</h2></div><a class="btn btn-ghost" href="blog/">All articles →</a></div>
    <div class="grid grid-3">{posts_html}</div>
  </div>
</section>
</main>"""
    ld = jsonld({"@context": "https://schema.org", "@graph": [ORG, {"@type": "WebSite", "url": BASE, "name": "HST Medical", "publisher": {"@id": BASE + "#org"},
                 "potentialAction": {"@type": "SearchAction", "target": BASE + "shop/?q={search_term_string}", "query-input": "required name=search_term_string"}}]})
    page("index.html", "HST Medical Singapore — Rheuma-Salve® Pain Relief, Heritage® Tonics & Zoo-Vite® Kids Supplements",
         "HST Medical (a Kowa subsidiary) makes Singapore's trusted pain relief and health supplements since 1994. Shop Rheuma-Salve®, cough & cold remedies, Heritage® tonics and Zoo-Vite®. GMP, Halal options.",
         body, active="home", extra_head=ld)
    add_sitemap(BASE, "1.0")


CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>'

# ---------------------------------------------------------------- SHOP + CATEGORIES
def build_shop():
    root = "../"
    chips = '<a class="chip active" href="#" data-cat="all">All</a>' + "".join('<a class="chip" href="%s/" data-cat="%s">%s</a>' % (cid, cid, esc(CATS[cid]["name"])) for cid in CAT_ORDER)
    cards = "\n".join(product_card(p, root, reveal=False) for p in [p for cid in CAT_ORDER for p in cat_products(cid)])
    crumb, crumb_ld = crumbs(root, [("Store", None)])
    body = f"""
<main id="main">
<div class="container">{crumb}
<header class="page-hero"><span class="eyebrow">Store</span><h1>All products</h1><p class="lead">{len(PRODUCTS)} products across {len(CAT_ORDER)} ranges. Prices in Singapore dollars; free island-wide delivery on orders over S$60.</p></header>
<form class="search" role="search" action="" onsubmit="return false"><label class="sr-only" for="q">Search products</label><input id="q" type="search" name="q" placeholder="Search products, e.g. balm, melatonin, ginseng"></form>
<nav class="filters" aria-label="Filter by range">{chips}</nav>
<p class="result-count" id="result-count">{len(PRODUCTS)} products</p>
<div class="products" id="shop-grid">{cards}</div>
</div>
</main>"""
    page("shop/index.html", "Store — All HST Medical, Heritage & Zoo-Vite Products", "Browse every HST Medical®, Heritage® and Zoo-Vite® product: pain relief, cough & cold, tonics, beauty, kids, bones & joints, sleep and more. Ships island-wide from Singapore.", body, active="shop", extra_head=crumb_ld)
    add_sitemap(BASE + "shop/", "0.9")

    for cid in CAT_ORDER:
        c = CATS[cid]; ps = cat_products(cid); root = "../../"
        crumb, crumb_ld = crumbs(root, [("Store", root + "shop/"), (c["name"], None)])
        cards = "\n".join(product_card(p, root) for p in ps)
        guide = ""
        extra = crumb_ld + jsonld({"@context": "https://schema.org", "@type": "CollectionPage", "name": c["name"], "url": BASE + "shop/%s/" % cid, "description": c["blurb"],
                                   "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + "products/%s/" % p["slug"], "name": p["name"]} for i, p in enumerate(ps)]}})
        if cid in GUIDES:
            g = GUIDES[cid]
            rows = "".join(f"<tr><th scope='row'><a href='{root}products/{s}/'>{esc(n)}</a></th><td>{esc(b)}</td><td>{esc(u)}</td></tr>" for n, b, u, s in g["table"])
            faqs = "".join(f"<details class='acc'><summary>{esc(q)}</summary><div class='body'><p>{esc(a)}</p></div></details>" for q, a in g["faq"])
            guide = f"""
<section class="section tint" id="guide">
  <div class="container">
    <div class="grid grid-2" style="gap:3rem">
      <div class="prose reveal"><span class="eyebrow">How to choose</span><h2>Which one do I need?</h2><p>{esc(g['intro'])}</p>
        <div class="table-wrap"><table class="compare"><thead><tr><th>Product</th><th>Best for</th><th>How to use</th></tr></thead><tbody>{rows}</tbody></table></div></div>
      <div class="reveal"><span class="eyebrow">Questions</span><h2>Frequently asked</h2>{faqs}
        <p class="notice">This information is for general guidance. Always read the label and follow directions for use. Consult a pharmacist or doctor if symptoms persist.</p></div>
    </div>
  </div>
</section>"""
            extra += jsonld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in g["faq"]]})
        body = f"""
<main id="main">
<div class="container">{crumb}
<header class="page-hero"><span class="eyebrow">Store</span><h1>{esc(c['name'])}</h1><p class="lead">{esc(c['blurb'])}</p></header>
<div class="products">{cards}</div>
</div>
{guide}
</main>"""
        page("shop/%s/index.html" % cid, "%s — HST Medical Singapore" % c["name"], c["blurb"] + " Shop online or find a stockist in Singapore.", body,
             active={"pain-relief": "pain", "cough-cold-flu": "cough"}.get(cid, "shop"), extra_head=extra)
        add_sitemap(BASE + "shop/%s/" % cid, "0.8" if cid in FOCUS_CATS else "0.7")


# ---------------------------------------------------------------- PRODUCT PAGES
def build_products():
    for p in PRODUCTS:
        root = "../../"; c = CATS[p["category"]]
        crumb, crumb_ld = crumbs(root, [("Store", root + "shop/"), (c["name"], root + "shop/%s/" % p["category"]), (p["name"], None)])
        img = "%sassets/img/products/%s.webp" % (root, p["image"])
        variants = "".join(f"<li class='{'on' if i == 0 else ''}'><strong>{esc(s['size'])}</strong>{esc(s['name'].replace('Heritage ', ''))}<br><span class='small'>Item {s['code']}</span></li>" for i, s in enumerate(p["skus"][:5])) or f"<li class='on'><strong>{esc(p['size'])}</strong>Single pack</li>"
        benefits = "".join("<li>%s</li>" % esc(b) for b in p["benefits"]) or "<li>%s</li>" % esc(p["tagline"])
        usage = "".join("<li>%s</li>" % esc(u) for u in p["usage"]) or "<li>Use as directed on the label.</li>"
        ingr = "".join("<li>%s</li>" % esc(u) for u in p["ingredients"]) or "<li>See pack for the full ingredient list.</li>"
        related = [x for x in cat_products(p["category"]) if x["slug"] != p["slug"]][:4]
        rel_cards = "\n".join(product_card(x, root) for x in related)
        price_block = f"<div class='price-row'><span class='price'>{esc(money(p['price']))} <small>SGD, incl. GST</small></span></div>" if p["price"] else "<div class='price-row'><span class='price' style='font-size:1.2rem'>Price on request</span></div>"
        live = f"<a href='{esc(p['live_url'])}' rel='noopener' target='_blank'>current listing</a>" if p["live_url"] else "current store"
        halal = " · Halal-certified" if p["slug"] == "alievaid-herbal-drops" else ""
        body = f"""
<main id="main">
<div class="container">{crumb}
<div class="pdp">
  <figure class="pdp-media reveal"><img src="{img}" alt="{esc(p['name'])} — {esc(p['size'])}" width="900" height="900" fetchpriority="high" decoding="async"></figure>
  <div>
    <span class="eyebrow {brand_class(p['brand'])}">{esc(brand_label(p['brand']))} · {esc(c['name'])}</span>
    <h1>{esc(p['name'])}</h1>
    <p class="tagline">{esc(p['tagline'])}</p>
    {price_block}
    <h4>Pack size</h4>
    <ul class="variants">{variants}</ul>
    <div class="qty"><label for="qty">Quantity</label><input id="qty" type="number" min="1" value="1" inputmode="numeric"></div>
    <div class="buy">
      <button class="btn btn-primary" data-add="{p['slug']}" data-pdp data-name="{esc(p['name'])}" data-price="{p['price'] or 0}" data-img="assets/img/products/{p['image']}-thumb.webp" data-url="products/{p['slug']}/">Add to cart</button>
      <a class="btn btn-outline" href="{root}where-to-buy/">Find in store</a>
    </div>
    <div class="meta">
      <span><b>Origin:</b> {esc(p['country'] or 'See pack')}{halal}</span>
      <span><b>Delivery:</b> Island-wide; free over S$60. International shipping at checkout.</span>
      <span><b>Trade:</b> Retailers order via their territory manager or <a href="{root}resellers/">the reseller page</a>.</span>
    </div>
    <h4>Benefits</h4>
    <ul class="benefits">{benefits}</ul>
    <details class="acc" open><summary>Description</summary><div class="body"><p>{esc(p['description'])}</p></div></details>
    <details class="acc"><summary>Suggested usage</summary><div class="body"><ul>{usage}</ul></div></details>
    <details class="acc"><summary>Active ingredients</summary><div class="body"><ul>{ingr}</ul></div></details>
    <details class="acc"><summary>Where to buy</summary><div class="body"><ul class="where">{''.join('<li>%s</li>' % esc(r) for r in RETAILERS[:4])}</ul><p class="small" style="margin-top:.75rem">Also on the {live} at hstmedical.com.</p></div></details>
    <p class="notice">Always read the label and follow directions for use. This is a health supplement or external remedy, not a substitute for medical care.</p>
  </div>
</div>
</div>
<section class="section" id="related">
  <div class="container"><div class="toolbar section-head"><div><span class="eyebrow">More in {esc(c['name'])}</span><h2>You may also need</h2></div><a class="btn btn-ghost" href="{root}shop/{p['category']}/">See the range →</a></div>
  <div class="products">{rel_cards}</div></div>
</section>
</main>"""
        ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "brand": {"@type": "Brand", "name": brand_label(p["brand"]).replace("®", "")},
              "image": BASE + "assets/img/products/%s.webp" % p["image"], "description": p["description"][:300], "category": c["name"],
              "manufacturer": {"@id": BASE + "#org"}, "url": BASE + "products/%s/" % p["slug"]}
        if p["skus"]:
            ld["sku"] = p["skus"][0]["code"]
        if p["price"]:
            ld["offers"] = {"@type": "Offer", "priceCurrency": "SGD", "price": "%.2f" % p["price"], "availability": "https://schema.org/InStock",
                            "url": BASE + "products/%s/" % p["slug"], "seller": {"@id": BASE + "#org"}}
        page("products/%s/index.html" % p["slug"], "%s (%s) — %s | HST Medical" % (p["name"], p["size"], brand_label(p["brand"])),
             (p["tagline"] + ". " + p["description"])[:158], body, active={"pain-relief": "pain", "cough-cold-flu": "cough"}.get(p["category"], "shop"),
             extra_head=crumb_ld + jsonld(ld), og_image=BASE + "assets/img/products/%s.webp" % p["image"])
        add_sitemap(BASE + "products/%s/" % p["slug"], "0.8" if p["focus"] else "0.6")


# ---------------------------------------------------------------- STATIC PAGES
def simple(out_rel, title, desc, h1, lead, inner, active="", eyebrow="", extra=""):
    root = "../" * out_rel.count("/")
    crumb, crumb_ld = crumbs(root, [(h1, None)])
    body = f"""
<main id="main">
<div class="container">{crumb}
<header class="page-hero">{'<span class="eyebrow">%s</span>' % esc(eyebrow) if eyebrow else ''}<h1>{esc(h1)}</h1>{'<p class="lead">%s</p>' % lead if lead else ''}</header>
{inner}
</div>
</main>"""
    page(out_rel, title, desc, body, active=active, extra_head=crumb_ld + extra)
    add_sitemap(BASE + out_rel[:-len("index.html")])


def build_static():
    # ABOUT
    simple("about/index.html", "About HST Medical — Singapore's Trusted Supplement & Pain Relief Maker Since 1994",
           "Established in 1994 and part of Kowa since 2024, HST Medical formulates and supplies health supplements and pain relief remedies to Singapore's major pharmacies.",
           "About HST Medical", "Established in 1994, HST Medical is a trusted manufacturer and supplier of health supplements and pain relief remedies to major pharmacies and online marketplaces.",
           f"""
<div class="grid grid-2" style="gap:3rem;align-items:start">
  <div class="prose">
    <h2>Contemporary pharmaceuticals, traditional benefits</h2>
    <p>Packed with premium quality ingredients, HST Medical products provide the harmony of contemporary pharmaceuticals and the long-term health benefits of natural nutrients. The dedicated team of pharmacists and TCM physicians behind the range develops formulas for modern needs from ethically sourced ingredients around the world.</p>
    <h2>Quality and safety first</h2>
    <p>From research and development to packaging and manufacturing standards, HST Medical guarantees product safety through strict adherence to authority guidelines, approved procedures, manufacturing processes and premises. Ingredients are rigorously tested for authenticity, finished products are verified for safety, and third-party manufacturing is thoroughly vetted.</p>
    <h2>Part of Kowa</h2>
    <p>In 2024 HST Medical became a subsidiary of Kowa Company, Ltd., the Japanese pharmaceutical and trading group whose consumer brands include Vantelin and Three Dimension Mask. The partnership brings Kowa's research depth to HST Medical's Singapore-made range while keeping the brands you know on the shelf.</p>
  </div>
  <div class="flow">
    <div class="card"><div class="stat">1994</div><p>Founded in Singapore. Three decades supplying Guardian, Watsons, NHGP and online marketplaces.</p></div>
    <div class="card"><div class="stat">3</div><p>Brands: HST Medical®, Heritage® and Zoo-Vite®, plus Rheuma-Salve®, the flagship pain-relief line.</p></div>
    <div class="card"><div class="stat">GMP</div><p>Manufactured under Good Manufacturing Practice with Halal-certified and vegan options across the range.</p></div>
    <div class="card"><h3>Awards &amp; recognition</h3><ul class="benefits"><li>2024 Beauty Insider Awards — hair and wellness supplements</li><li>Guardian retailer award</li><li>5.0 Google rating (Trustindex-verified)</li></ul><p class="small">As listed on the current hstmedical.com. To be confirmed with the client.</p></div>
  </div>
</div>""", active="about", eyebrow="Our story")

    # BRANDS
    brand_cards = ""
    for name, cls, blurb, cid_list in [
        ("Rheuma-Salve®", "heritage", "Singapore's extra-strength pain relief since 1994: balm, crème, liniment, patch and Medi-Stick.", ["pain-relief"]),
        ("Heritage®", "heritage", "Traditional Asian remedies prepared to modern GMP standards: ginseng, cordyceps, lingzhi, pearl powder, squalene, crocodile oil and medicated oils.", ["immunity-energy", "beauty-wellness", "traditional-pain-relief"]),
        ("HST Medical®", "", "Pharmaceutical-grade supplements and herbal remedies for cough and cold, bones and joints, sleep, eyes, heart, liver and vitality.", ["cough-cold-flu", "bones-joints", "alertness-memory-vision", "stress-sleep", "immunity-allergy", "heart-liver-vitality"]),
        ("Zoo-Vite®", "zoo", "Kids' gummies and jelly sticks with characters children remember: Perky Penguin, Inspector Charley, Safari Buddies, Super Panda and Professor Skippy.", ["kids"]),
    ]:
        links = " ".join(f"<a class='chip' href='../shop/{c}/'>{esc(CATS[c]['name'])}</a>" for c in cid_list)
        brand_cards += f"<div class='card reveal'><span class='eyebrow {cls}'>Brand</span><h3>{esc(name)}</h3><p>{esc(blurb)}</p><div class='filters' style='margin-bottom:0'>{links}</div></div>"
    simple("brands/index.html", "Our Brands — Rheuma-Salve®, Heritage®, HST Medical®, Zoo-Vite® and Kowa",
           "Four brands under one quality standard, now part of the Kowa group alongside Vantelin and Three Dimension Mask.",
           "Our brands", "Four brands under one quality standard, now part of the Kowa group.",
           f"""<div class="grid grid-2">{brand_cards}</div>
<section class="section"><div class="cta reveal"><div><span class="eyebrow" style="color:#ffd1e0">Parent company</span><h2>Kowa — Japanese pharmaceutical heritage</h2><p>Kowa Company, Ltd. (Nagoya, est. 1894) owns consumer brands such as Vantelin topical pain relief and Three Dimension Mask. HST Medical joined the group in 2024, and Kowa's Singapore range will be cross-listed here as the partnership develops.</p></div><div><a class="btn btn-outline" href="../about/">Read our story</a></div></div></section>""",
           active="brands", eyebrow="Brands")

    # WHERE TO BUY
    simple("where-to-buy/index.html", "Where to Buy HST Medical Products in Singapore — Guardian, Watsons, NHGP & Online",
           "Find Rheuma-Salve®, Heritage® and Zoo-Vite® at Guardian, Watsons, NHGP pharmacies and selected clinics, or order online with island-wide delivery.",
           "Where to buy", "On the shelf at Singapore's leading pharmacies, and online with island-wide delivery.",
           f"""
<div class="grid grid-3">
  {''.join(f"<div class='card reveal'><h3>{esc(r)}</h3><p>{t}</p></div>" for r, t in [
      ("Guardian", "Rheuma-Salve®, Heritage® tonics and selected HST Medical® supplements in most outlets island-wide."),
      ("Watsons", "Pain relief, cough and cold and kids' ranges. Check in-store availability for tonics."),
      ("NHGP pharmacies", "National Healthcare Group polyclinic pharmacies carry the core pain-relief and cough range."),
      ("Unity", "Selected lines. Ask the pharmacist for the Rheuma-Salve® range."),
      ("Clinics &amp; TCM halls", "Many GP clinics and TCM halls stock Rheuma-Salve® and Heritage®. Clinics can open a trade account below."),
      ("Online", "This store ships island-wide (free over S$60) and internationally. Also listed on major marketplaces."),
  ])}
</div>
<section class="section tint" style="margin-top:3rem;border-radius:var(--radius)"><div class="container"><div class="grid grid-2"><div class="prose"><h2>Store locator</h2><p>A pharmacy-level locator (postcode search, opening hours) is planned for the production build. In the meantime, each retailer's own locator lists outlets: Guardian, Watsons and NHGP maintain up-to-date store finders.</p><p class="small">Placeholder for the Phase 2 locator widget.</p></div><div class="cta"><div><h2 style="font-size:1.5rem">Stock us</h2><p>Retailers, clinics and distributors can order direct.</p></div><div><a class="btn btn-primary" href="../resellers/">Trade enquiries</a></div></div></div></div></section>""",
           active="shop", eyebrow="Stockists")

    # RESELLERS (B2B)
    simple("resellers/index.html", "Become a Reseller — Trade Accounts for Pharmacies, Clinics & Distributors | HST Medical",
           "Open a trade account with HST Medical Singapore. Pharmacies, clinics, TCM halls and distributors order through a territory manager with product sheets, pricing tiers and marketing support.",
           "Become a reseller", "HST Medical supplies pharmacies, clinics, TCM halls, e-commerce sellers and overseas distributors directly. Tell us about your business and a territory manager will be in touch.",
           f"""
<div class="grid grid-2" style="gap:3rem;align-items:start">
  <div class="prose">
    <h2>What you get</h2>
    <ol class="steps">
      <li><strong>A territory manager.</strong> One point of contact for orders, re-orders and promotions.</li>
      <li><strong>Product sheets.</strong> Benefits, usage, active ingredients, item codes and pack configurations for all 50+ SKUs.</li>
      <li><strong>Trade pricing.</strong> Single, twin, triple and value-pack configurations with tiered pricing.</li>
      <li><strong>Shelf support.</strong> Point-of-sale material, product training and seasonal campaigns (cough &amp; cold, Lunar New Year gifting).</li>
    </ol>
    <h2>Already a reseller?</h2>
    <p>Email <a href="mailto:resellercontact@hstmedical.com">resellercontact@hstmedical.com</a> or contact your territory manager. A self-service reseller portal with order history, pricelists and one-click re-orders is proposed for Phase 2.</p>
  </div>
  <form class="form card" data-demo novalidate>
    <h3>Trade enquiry</h3>
    <div class="row"><label>Business name<input type="text" name="company" required></label><label>Business type<select name="type"><option>Pharmacy</option><option>Clinic / GP</option><option>TCM hall</option><option>E-commerce seller</option><option>Distributor (overseas)</option><option>Other</option></select></label></div>
    <div class="row"><label>Contact person<input type="text" name="name" required></label><label>Role<input type="text" name="role"></label></div>
    <div class="row"><label>Email<input type="email" name="email" required></label><label>Phone / WhatsApp<input type="tel" name="phone"></label></div>
    <label>Country / region<input type="text" name="country" value="Singapore"></label>
    <label>Ranges of interest<input type="text" name="ranges" placeholder="e.g. Rheuma-Salve®, cough & cold, Zoo-Vite®"></label>
    <label>Message<textarea name="message" placeholder="Number of outlets, expected volume, timing"></textarea></label>
    <label class="check"><input type="checkbox" name="consent" required> I agree to be contacted about a trade account and understand my details are handled under the privacy policy.</label>
    <button class="btn btn-primary" type="submit">Send enquiry</button>
    <p class="form-note">Prototype: no data is sent. Production form posts to the WordPress contact handler and notifies resellercontact@hstmedical.com.</p>
    <p class="ok">Thank you — a territory manager will contact you within two working days.</p>
  </form>
</div>""", active="resellers", eyebrow="Trade & B2B")

    # CONTACT
    simple("contact/index.html", "Contact HST Medical Singapore", "Customer service, order questions and trade enquiries for HST Medical Pte Ltd, Singapore.",
           "Contact us", "Questions about an order, a product or a trade account? We reply within two working days.",
           """
<div class="grid grid-2" style="gap:3rem;align-items:start">
  <div class="flow">
    <div class="card"><h3>Customer service</h3><p>Orders, delivery and product questions.<br><a href="mailto:hello@hstmedical.com">hello@hstmedical.com</a><br><span class="small">Placeholder address; confirm with client.</span></p></div>
    <div class="card"><h3>Trade &amp; resellers</h3><p><a href="mailto:resellercontact@hstmedical.com">resellercontact@hstmedical.com</a><br>or your HST Medical territory manager.</p></div>
    <div class="card"><h3>HST Medical Pte Ltd</h3><p>Singapore<br><span class="small">Registered address, phone and opening hours to be supplied by the client.</span></p></div>
  </div>
  <form class="form card" data-demo novalidate>
    <h3>Send a message</h3>
    <div class="row"><label>Name<input type="text" name="name" required></label><label>Email<input type="email" name="email" required></label></div>
    <label>Topic<select name="topic"><option>Order or delivery</option><option>Product question</option><option>Trade enquiry</option><option>Press</option><option>Other</option></select></label>
    <label>Message<textarea name="message" required></textarea></label>
    <button class="btn btn-primary" type="submit">Send</button>
    <p class="ok">Thanks — we have your message.</p>
  </form>
</div>""", active="contact", eyebrow="Get in touch")

    # CART
    simple("cart/index.html", "Your cart — HST Medical", "Review your HST Medical order before checkout.", "Your cart", "",
           """
<div class="checkout">
  <div id="cart-lines" data-root="../"><div class="empty">Your cart is empty. <a href="../shop/">Browse the store</a>.</div></div>
  <aside class="summary"><h3>Summary</h3><div class="line"><span>Subtotal</span><span data-sub>S$0.00</span></div><div class="line"><span>Delivery (free over S$60)</span><span data-ship>—</span></div><div class="total"><span>Total</span><span data-total>S$0.00</span></div><a class="btn btn-primary btn-block" href="../checkout/">Checkout</a><a class="btn btn-ghost btn-block" href="../shop/">Continue shopping</a><p class="small">Prototype cart stored in your browser only. Production uses WP EasyCart's cart, with the same layout applied through CSS overrides.</p></aside>
</div>""", active="shop", eyebrow="Store")

    # CHECKOUT
    simple("checkout/index.html", "Checkout — HST Medical", "Secure checkout for HST Medical orders.", "Checkout", "",
           """
<div class="checkout">
  <form class="form" data-demo novalidate>
    <h3>Contact</h3>
    <div class="row"><label>Email<input type="email" required></label><label>Mobile<input type="tel"></label></div>
    <h3>Delivery address</h3>
    <div class="row"><label>First name<input type="text" required></label><label>Last name<input type="text" required></label></div>
    <label>Address<input type="text" required></label>
    <div class="row"><label>Unit<input type="text"></label><label>Postal code<input type="text" inputmode="numeric" required></label><label>Country<select><option>Singapore</option><option>Malaysia</option><option>Other</option></select></label></div>
    <h3>Delivery method</h3>
    <label class="check"><input type="radio" name="ship" checked> Standard courier, 2–3 working days (free over S$60, otherwise S$4.50)</label>
    <label class="check"><input type="radio" name="ship"> Self-collection (by appointment)</label>
    <h3>Payment</h3>
    <label class="check"><input type="radio" name="pay" checked> Card (Visa / Mastercard / Amex)</label>
    <label class="check"><input type="radio" name="pay"> PayNow</label>
    <label class="check"><input type="radio" name="pay"> GrabPay / Apple Pay / Google Pay</label>
    <label class="check"><input type="checkbox" required> I accept the terms and the privacy policy.</label>
    <button class="btn btn-primary" type="submit">Place order</button>
    <p class="form-note">Prototype: nothing is charged. Production checkout is WP EasyCart with the configured gateway; this layout is applied via CSS overrides on EasyCart's checkout wrapper.</p>
    <p class="ok">Order placed (demo). A confirmation email would follow.</p>
  </form>
  <aside class="summary"><h3>Order summary</h3><div id="cart-lines" data-root="../"></div><div class="line"><span>Subtotal</span><span data-sub>S$0.00</span></div><div class="line"><span>Delivery</span><span data-ship>—</span></div><div class="total"><span>Total</span><span data-total>S$0.00</span></div></aside>
</div>""", active="shop", eyebrow="Store")

    # PRIVACY
    simple("privacy/index.html", "Privacy Policy — HST Medical", "How HST Medical Pte Ltd collects and uses personal data under Singapore's PDPA.", "Privacy policy", "",
           """<div class="prose"><p>HST Medical Pte Ltd collects personal data to process orders, respond to enquiries and, with consent, send product news. Data is handled under Singapore's Personal Data Protection Act (PDPA).</p><h2>What we collect</h2><ul><li>Contact and delivery details you enter at checkout or in forms</li><li>Order history and customer-service correspondence</li><li>Basic analytics (page views, device type) to improve the site</li></ul><h2>Your rights</h2><p>You can request access to, correction of, or deletion of your data by writing to our Data Protection Officer at the contact page.</p><p class="small">Placeholder text for the prototype. The production policy will be supplied by the client's legal team.</p></div>""", active="")


# ---------------------------------------------------------------- BLOG
POSTS = [
    ("balm-creme-liniment-or-patch", "Balm, crème, liniment or patch? Choosing the right Rheuma-Salve® format", "2026-10-02",
     "Five formats, one formula. Where it hurts and where you are decide which to reach for.",
     """<p>Rheuma-Salve® started as a single snowy-white balm in 1994. Thirty years later the proprietary blend of menthol, peppermint, wintergreen, camphor and eucalyptus comes in five formats. The active ingredients are consistent; what changes is how deep, how long and how tidy the relief is.</p>
<h2>Balm: deep and warming</h2><p>The classic 50g jar. Best for stiff knees, lower-back ache after a long day and tight shoulders. The balm sits on the skin longer than the crème, so the warming-cooling sensation builds. It also clears congestion when rubbed on the chest.</p>
<h2>Crème: light and tidy</h2><p>Same formula, non-greasy base. Absorbs in a minute and will not mark office clothes. The sensible choice for daily aches and for anyone who finds balms heavy.</p>
<h2>Liniment: fast and penetrating</h2><p>The 10ml oil is for sports strains and sprains. Massage it in before and after exercise. It is the format physios reach for.</p>
<h2>Patch (Cool): hands-free for six hours</h2><p>New to the range. Eight soft 10 × 7 cm patches with peppermint oil, menthol, centella, hops, frankincense and myrrh. Stick one on a sore neck or lower back, remove after six hours. Ideal for delayed onset muscle soreness after a hard session.</p>
<h2>Medi-Stick: pocket relief</h2><p>A 15g glide-on stick. No mess, no greasy fingers, fits a gym bag or handbag. Use it when you cannot stop to wash your hands.</p>
<blockquote>Rule of thumb: balm for deep joint pain, crème for daily aches, liniment for sports, patch for hands-free hours, stick for the road.</blockquote>
<p>Always read the label and follow directions for use. If pain persists beyond a week, see a doctor.</p>"""),
    ("cough-cold-or-flu-which-remedy", "Cough, cold or flu? Matching the symptom to the remedy", "2026-09-25",
     "Sore throat, chesty cough, fever or blocked nose: six herbal remedies, each with a job.",
     """<p>A cold rarely arrives all at once. It starts as a tickle, becomes a cough, sometimes turns into a fever and often ends with a nose that will not clear. HST Medical's cough, cold and flu range follows that arc.</p>
<h2>Day 1: sore, scratchy throat</h2><p>Alievaid Herbal Drops combine loquat leaf, jie geng, luo han guo and cordyceps with a strong cooling mint. Dissolve one slowly every two to three hours (maximum eight a day, age 12 and above). Ivy Leaf Drops do the same job with ivy leaf extract.</p>
<h2>Days 2–4: cough with phlegm</h2><p>Cough Alievaid Herbal Lintus is the syrup for a productive cough. Ivy Leaf Cough Syrup comes in single-dose 10ml sachets, convenient for travel and for children's bags (follow the label for ages).</p>
<h2>Fever, aches, sneezing</h2><p>Flu Gard is a 100 percent herbal TCM formula in vegicaps that reduces fever, eases body aches, runny nose and sneezing, relieves cough and reduces phlegm. Two to six vegicaps, three times a day after food.</p>
<h2>Blocked nose and sinus headache</h2><p>Sinus Clear 2-in-1 is a lipstick-sized inhaler with a refill applicator underneath: inhale for a blocked nose, dab on the temples for a headache. It is also handy for mosquito bites.</p>
<p>Always read the label and follow directions for use. See a doctor if fever lasts more than three days or if you have difficulty breathing.</p>"""),
    ("what-gmp-and-halal-mean", "What GMP and Halal certification mean for your supplements", "2026-09-18",
     "Two marks on the pack, and what each one guarantees about how the product was made.",
     """<p>Supplement packs carry a lot of small print. Two marks matter more than the rest: GMP and Halal.</p>
<h2>GMP: how it is made</h2><p>Good Manufacturing Practice is the set of rules a facility follows so that every batch is made the same way, from raw material testing to packaging. HST Medical manufactures under GMP and additionally verifies the authenticity of ingredients, tests finished products for safety and audits any third-party manufacturer.</p>
<h2>Halal: what goes in</h2><p>Halal certification confirms that ingredients and processes meet Islamic dietary requirements, with no porcine-derived gelatine or alcohol-based carriers. Several HST Medical products are certified, including Alievaid Herbal Drops (Halal Malaysia), and vegicaps are used across much of the range so that vegetarians and Muslim customers can take them with confidence.</p>
<h2>Why both matter</h2><p>GMP tells you the product is consistent and safe. Halal tells you what is inside is permissible. Together they are the reason pharmacies such as Guardian, Watsons and NHGP stock the range, and why we print both on the product page, not only on the pack.</p>"""),
]

def build_blog():
    root = "../"
    crumb, crumb_ld = crumbs(root, [("Health notes", None)])
    cards = "\n".join(f"""<a class="card post-card card-link reveal" href="{s}/"><time datetime="{d}">{d}</time><h3>{esc(t)}</h3><p>{esc(x)}</p></a>""" for s, t, d, x, _ in POSTS)
    body = f"""
<main id="main"><div class="container">{crumb}
<header class="page-hero"><span class="eyebrow">Health notes</span><h1>Short, practical reading.</h1><p class="lead">Guides written with HST Medical's pharmacists: how to choose, how to use, and what the marks on the pack mean.</p></header>
<div class="grid grid-3">{cards}</div></div></main>"""
    page("blog/index.html", "Health Notes — Guides from HST Medical's Pharmacists", "Practical guides on pain relief, cough and cold remedies, supplements and product certification from HST Medical Singapore.", body, active="blog", extra_head=crumb_ld)
    add_sitemap(BASE + "blog/", "0.6")
    for s, t, d, x, bodyhtml in POSTS:
        root = "../../"
        crumb, crumb_ld = crumbs(root, [("Health notes", root + "blog/"), (t, None)])
        ld = jsonld({"@context": "https://schema.org", "@type": "Article", "headline": t, "description": x, "datePublished": d, "dateModified": d,
                     "author": {"@type": "Organization", "name": "HST Medical"}, "publisher": {"@id": BASE + "#org"}, "mainEntityOfPage": BASE + "blog/%s/" % s})
        body = f"""
<main id="main"><div class="narrow">{crumb}
<article class="prose"><header class="page-hero"><span class="eyebrow">Health notes</span><h1>{esc(t)}</h1><p class="post-meta">Published <time datetime="{d}">{d}</time> · HST Medical</p></header>
{bodyhtml}
<hr><p><a href="{root}blog/">← All articles</a> · <a href="{root}shop/">Shop the range</a></p></article></div></main>"""
        page("blog/%s/index.html" % s, "%s — HST Medical" % t, x, body, active="blog", extra_head=crumb_ld + ld)
        add_sitemap(BASE + "blog/%s/" % s, "0.5")


# ---------------------------------------------------------------- 404, robots, sitemap, llms.txt
def build_misc():
    body = """
<main id="main"><div class="narrow" style="padding:4rem 0;text-align:center"><span class="eyebrow">404</span><h1>That page is not on the shelf.</h1><p class="lead">The link may be old, or the product has moved. Try the store or search.</p><div class="btn-row" style="justify-content:center"><a class="btn btn-primary" href="{{ROOT}}shop/">Go to the store</a><a class="btn btn-outline" href="{{ROOT}}">Home</a></div></div></main>"""
    # 404 is served from any path by GitHub Pages, so it uses an absolute root (the Pages sub-path)
    page("404.html", "Page not found — HST Medical", "The page you requested could not be found.", body, root="/hst-medical-website/")
    write("robots.txt", ("User-agent: *\nDisallow: /\n\n# Prototype build: crawling disabled until client sign-off.\n" if PROTOTYPE else "User-agent: *\nAllow: /\n\n") + "Sitemap: %ssitemap.xml\n" % BASE)
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u, pr in SITEMAP:
        sm += "  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n" % (u, TODAY, pr)
    write("sitemap.xml", sm + "</urlset>\n")
    # llms.txt — GEO: a plain-text map of the site for AI crawlers
    L = ["# HST Medical", "", "> HST Medical Pte Ltd (Singapore, est. 1994; a Kowa subsidiary since 2024) formulates and supplies health supplements and pain-relief remedies under the HST Medical®, Heritage®, Rheuma-Salve® and Zoo-Vite® brands. Products are GMP-manufactured, many Halal-certified, sold at Guardian, Watsons and NHGP pharmacies and shipped from this store in SGD.", "",
         "## Ranges"]
    for cid in CAT_ORDER:
        L.append("- [%s](%sshop/%s/): %s" % (CATS[cid]["name"], BASE, cid, CATS[cid]["blurb"]))
    L += ["", "## Featured products (Premium Pain Relief; Cough, Cold & Flu)"]
    for p in PRODUCTS:
        if p["focus"]:
            L.append("- [%s](%sproducts/%s/): %s. %s. %s" % (p["name"], BASE, p["slug"], p["tagline"], p["size"], money(p["price"]) if p["price"] else ""))
    L += ["", "## All products"]
    for p in PRODUCTS:
        if not p["focus"]:
            L.append("- [%s](%sproducts/%s/): %s, %s" % (p["name"], BASE, p["slug"], brand_label(p["brand"]), p["size"]))
    L += ["", "## Company", "- [About](%sabout/)" % BASE, "- [Brands](%sbrands/)" % BASE, "- [Where to buy](%swhere-to-buy/)" % BASE,
          "- [Become a reseller](%sresellers/): trade accounts for pharmacies, clinics, TCM halls and distributors; resellercontact@hstmedical.com" % BASE,
          "- [Health notes](%sblog/)" % BASE, "- [Contact](%scontact/)" % BASE]
    write("llms.txt", "\n".join(L) + "\n")


if __name__ == "__main__":
    build_home(); build_shop(); build_products(); build_static(); build_blog(); build_misc()
    print("built %d sitemap URLs, %d products, prototype=%s" % (len(SITEMAP), len(PRODUCTS), PROTOTYPE))
