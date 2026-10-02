"""
HST Medical — prototype site assembler ("The Dispensing Counter" world).

    python _src/build.py

Reads _src/products.json (catalogue_parse.py) and _src/store.json (live store prices) and writes every page
to the site root as <folder>/index.html (clean URLs). Templates map 1:1 to classic WordPress files; see
WP-MAPPING.md. PROTOTYPE = True adds noindex to every page and a robots Disallow (unlisted test link).
"""
import json, os, re, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
BASE = "https://technextmarketing.github.io/hst-medical-website/"
V = "20261002e"
PROTOTYPE = True
TODAY = datetime.date.today().isoformat()

DATA = json.load(open(os.path.join(HERE, "products.json"), encoding="utf-8"))
STORE = json.load(open(os.path.join(HERE, "store.json"), encoding="utf-8"))
CATS, PRODUCTS = DATA["categories"], DATA["products"]
BY_SLUG = {p["slug"]: p for p in PRODUCTS}
FOCUS_CATS = ["pain-relief", "cough-cold-flu"]
CAT_ORDER = ["pain-relief", "cough-cold-flu", "traditional-pain-relief", "bones-joints", "immunity-allergy",
             "immunity-energy", "alertness-memory-vision", "stress-sleep", "kids", "beauty-wellness", "heart-liver-vitality"]
FILTER_GROUPS = [("Relief", ["pain-relief", "traditional-pain-relief", "cough-cold-flu", "bones-joints"]),
                 ("Every day", ["immunity-allergy", "immunity-energy", "alertness-memory-vision", "stress-sleep"]),
                 ("Family and beauty", ["kids", "beauty-wellness", "heart-liver-vitality"])]
COUNTERS = [("pain-relief", "Pain relief", "Balm, crème, liniment, patch, stick"), ("cough-cold-flu", "Cough and cold", "Lozenges, syrups, flu remedy, inhaler"),
            ("kids", "Kids", "Zoo-Vite gummies and jelly sticks"), ("stress-sleep", "Sleep", "Melatonin and magnesium"), ("immunity-energy", "Tonics", "Ginseng, cordyceps, lingzhi")]
RETAILERS_CONFIRMED = ["Guardian", "Watsons", "NHGP pharmacies"]
RETAILERS_TBC = ["Unity (to confirm)", "GP clinics and TCM halls (to confirm)", "Online marketplaces (to confirm)"]

OVERRIDES = {
    "rheuma-salve-pain-relief-patch-cool": {"description": "The Rheuma-Salve® Pain Relief Patch (Cool) is a plaster that delivers fast-acting, cool-sensation relief directly to the source of pain. Each pack holds 8 soft, flexible 10 × 7 cm patches that are gentle on the skin and made for muscle aches, sprains, strains, joint pain, backaches, sports recovery and delayed onset muscle soreness.", "country": "Made in Taiwan for HST Medical Pte Ltd (brand of Singapore)"},
    "sinus-clear-2-in-1": {"tagline": "Relief from blocked nose and headaches"},
    "shou-wu-hair-plus": {"description": "A traditional herbal formula built around He Shou Wu and wolfberry to replenish vital essence and nourish the blood, with Chinese angelica, ginseng and cordyceps to improve circulation to the scalp and support healthy hair growth and natural colour."},
    "liver-gard-forte": {"benefits": ["Supports liver detoxification", "Protects liver cells from oxidative stress", "Supports healthy liver function and energy"]},
}
for slug, o in OVERRIDES.items():
    BY_SLUG[slug].update(o)
for p in PRODUCTS:
    if not p["tagline"]:
        p["tagline"] = CATS[p["category"]]["name"]

# "For:" lines in plain words (pharmacist register) for the focus products; others fall back to benefits
FOR = {
    "rheuma-salve-balm": "Deep joint and muscle pain, stiffness, chest congestion",
    "rheuma-salve-creme": "Everyday aches; absorbs fast, will not stain clothes",
    "rheuma-salve-liniment": "Sprains and sports strains; fast penetrating oil",
    "rheuma-salve-pain-relief-patch-cool": "Hands-free relief for up to 6 hours: back, neck, shoulders, sore muscles",
    "rheuma-salve-medi-stick": "Pocket relief at the desk, gym or on the road; no mess",
    "alievaid-herbal-drops": "Sore throat and irritating cough; freshens breath",
    "cough-alievaid-herbal-lintus": "Cough with phlegm",
    "flu-gard": "Fever, body aches, runny nose and sneezing",
    "ivy-leaf-cough-syrup": "Dry or chesty cough; single-dose sachets for travel",
    "ivy-leaf-drops": "Cough and sore throat relief on the go",
    "sinus-clear-2-in-1": "Blocked nose, sinus headache, insect bites",
}

# ---------------------------------------------------------------- variant pricing from the live store
FAMILY = {  # slug -> store-title keywords (lower-case) that belong to this product family
    "rheuma-salve-balm": ["pain relief balm", "pain-relief balm"], "rheuma-salve-creme": ["crème", "creme"],
    "rheuma-salve-liniment": ["liniment"], "rheuma-salve-pain-relief-patch-cool": ["patch"], "rheuma-salve-medi-stick": ["medi-stick"],
    "alievaid-herbal-drops": ["alievaid herbal drops"], "cough-alievaid-herbal-lintus": ["cough alievaid"], "flu-gard": ["flu gard"],
    "ivy-leaf-cough-syrup": ["ivy leaf cough syrup"], "ivy-leaf-drops": ["ivy leaf drops"], "sinus-clear-2-in-1": ["sinus clear"],
}
VAR_RE = re.compile(r"\[([^\]]+)\]|\((?P<p>[^)]*(?:pack|bundle|buy 1|tablets|bottle)[^)]*)\)|(Bundle of \d+ Packs)|(Travel Pack 10 Sachets)", re.I)

def variant_label(title):
    m = VAR_RE.search(title)
    if not m:
        return "Single pack"
    lab = (m.group(1) or m.group("p") or m.group(3) or m.group(4) or "").strip()
    lab = re.sub(r"\s+", " ", lab)
    return "Single pack" if lab.lower() in ("single pack", "single") else lab[0].upper() + lab[1:]

def variants_for(p):
    keys = FAMILY.get(p["slug"])
    if not keys:
        base = (p.get("live_url") or "").rstrip("/").split("/")[-1]
        hits = [s for s in STORE if p["live_url"] and (s["url"] == p["live_url"] or s["url"].rstrip("/").startswith(p["live_url"].rstrip("/") + "-") or
                                                      (s["url"].rstrip("/").split("/")[-1].replace("-twin-pack", "").replace("-triple-pack", "") == base))]
    else:
        hits = [s for s in STORE if any(k in s["title"].lower() for k in keys)]
        if p["slug"] == "alievaid-herbal-drops":
            hits = [s for s in hits if "cough alievaid" not in s["title"].lower()]
    out, seen = [], set()
    for s in hits:
        lab = variant_label(s["title"])
        if p["slug"] == "rheuma-salve-balm" and "travel" in s["title"].lower() and "twin" in s["title"].lower():
            lab = "20g twin pack (travel)"
        if lab in seen:
            continue
        seen.add(lab)
        # tidy the store's pack wording into label language
        lab = re.sub(r"\s*Jars?\b", "", lab); lab = re.sub(r"Bundle of (\d+) Packs", r"Bundle of \1", lab); lab = re.sub(r"\s*\bPack\b", " pack", lab)
        lab = re.sub(r"\s+Bundle$", " pack", lab); lab = re.sub(r"(\d+\s?[a-zA-Z]*)\s*[xX]\s*(\d+)", r"\1 × \2", lab)
        lab = re.sub(r"^Travel (\d+\w* × \d+) pack$", r"\1 travel pack", lab); lab = re.sub(r"^(\d+\w*) twin pack \(travel\)$", r"\1 × 2 travel twin pack", lab)
        lab = re.sub(r"\s{2,}", " ", lab).strip()
        lab = lab[0].upper() + lab[1:]
        code, best = "", 0
        ltoks = set(re.findall(r"twin|triple|value|travel|bundle|sachet|box", lab.lower())) | set(re.findall(r"×\s*(\d+)", lab))
        for sku in p["skus"]:
            stoks = set(re.findall(r"twin|triple|value|travel|bundle|sachet|box", sku["name"].lower())) | set(re.findall(r"[xX]\s*(\d+)", sku["size"]))
            score = len(ltoks & stoks)
            if ltoks and score > best and not (("twin" in ltoks) != ("twin" in stoks)):
                code, best = sku["code"], score
        if not code and lab == "Single pack" and p["skus"]:
            code = p["skus"][0]["code"]
        out.append({"label": lab, "price": s["price"], "code": code, "url": s["url"]})
    out.sort(key=lambda v: (v["label"] != "Single pack", v["price"] or 0))
    if not out:
        out.append({"label": "Single pack", "price": p["price"], "code": p["skus"][0]["code"] if p["skus"] else "", "url": p.get("live_url")})
    return out

for p in PRODUCTS:
    p["variants"] = variants_for(p)
    p["price"] = p["variants"][0]["price"]
    p["for"] = FOR.get(p["slug"]) or (", ".join(b.rstrip(".") for b in p["benefits"][:2]) if p["benefits"] else p["tagline"])

# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape(str(s), quote=True)

def money(v):
    return "S$%.2f" % v if v else "Price on request"

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
    os.makedirs(os.path.dirname(path) or OUT, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

def jsonld(obj):
    return '<script type="application/ld+json">%s</script>\n' % json.dumps(obj, ensure_ascii=False)

IC = {
    "tick": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
    "plus": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
    "arrow": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "bag": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8h12l1 12H5z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>',
    "search": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
}

ORG = {"@type": "Organization", "@id": BASE + "#org", "name": "HST Medical Pte Ltd", "url": BASE,
       "logo": BASE + "assets/img/logo-hst-kowa.png", "parentOrganization": {"@type": "Organization", "name": "Kowa Company, Ltd."},
       "foundingDate": "1994", "address": {"@type": "PostalAddress", "addressCountry": "SG"}, "sameAs": ["https://hstmedical.com"]}

SITEMAP = []
def add_sitemap(url, prio="0.6"):
    SITEMAP.append((url, prio))

def add_btn(p, root, cls="btn btn-sm", from_pdp=False, label="Add to bag"):
    v = p["variants"][0]
    if not v["price"]:
        return '<a class="%s btn-quiet" href="%scontact/">Enquire</a>' % (cls, root)
    return ('<button class="%s" data-add data-id="%s" data-name="%s" data-price="%s" data-variant="%s" data-code="%s" data-img="assets/img/products/%s-thumb.webp" data-url="products/%s/"%s>%s %s</button>'
            % (cls, p["slug"], esc(p["name"]), v["price"], esc(v["label"]), v["code"], p["image"], p["slug"], " data-from-pdp" if from_pdp else "", IC["bag"], label))

def product_label(p, root):
    img = "%sassets/img/products/%s-thumb.webp" % (root, p["image"])
    url = "%sproducts/%s/" % (root, p["slug"])
    search = ("%s %s %s %s %s" % (p["name"], p["brand"], CATS[p["category"]]["name"], p["tagline"], p["for"])).lower()
    return f"""<article class="label plabel {brand_class(p['brand'])}" data-cat="{p['category']}" data-search="{esc(search)}">
  <a class="img" href="{url}" tabindex="-1" aria-hidden="true"><img src="{img}" alt="" width="360" height="360" loading="lazy" decoding="async"></a>
  <div class="body"><span class="brand {brand_class(p['brand'])}">{esc(brand_label(p['brand']))} · {esc(p['size'])}</span>
  <h3><a href="{url}">{esc(p['name'])}</a></h3>
  <p class="for">For: {esc(p['for'])}</p></div>
  <div class="foot"><span class="price">{esc(money(p['price']))}<small>{'incl. GST' if p['price'] else 'ask in store'}</small></span>{add_btn(p, root)}</div>
</article>"""

def compare_table(cid, root, with_price=True):
    rows = ""
    for p in cat_products(cid):
        usage = (p["usage"][0] if p["usage"] else "Use as directed on the label").split(". ")[0].rstrip(".")
        usage = re.sub(r"^(How To Use|Caution|Storage):\s*", "", usage)
        rows += f"""<tr><td class="img"><img class="thumb" src="{root}assets/img/products/{p['image']}-thumb.webp" alt="" width="72" height="72" loading="lazy"></td>
<th scope="row"><a href="{root}products/{p['slug']}/">{esc(p['name'])}</a><br><span class="small">{esc(p['size'])}</span></th>
<td class="for">{esc(p['for'])}</td><td class="use">{esc(usage)}</td>
<td class="price">{esc(money(p['price']))}</td><td class="act">{add_btn(p, root)}</td></tr>"""
    return f"""<div class="table-wrap"><table class="compare"><thead><tr><th scope="col"><span class="sr-only">Pack</span></th><th scope="col">Product</th><th scope="col">Best for</th><th scope="col">How to use</th><th scope="col">Price</th><th scope="col"><span class="sr-only">Add</span></th></tr></thead><tbody>{rows}</tbody></table></div>"""

def crumbs(root, items):
    lis = ['<li><a href="%s">Home</a></li>' % root]
    ld = [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE}]
    for i, (label, href) in enumerate(items, start=2):
        lis.append('<li><a href="%s">%s</a></li>' % (href, esc(label)) if href else '<li aria-current="page">%s</li>' % esc(label))
        ld.append({"@type": "ListItem", "position": i, "name": label, **({"item": href.replace(root, BASE, 1)} if href else {})})
    return '<ol class="crumbs" aria-label="Breadcrumb">%s</ol>' % "".join(lis), jsonld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ld})

NAV_IDS = ["pain", "cough", "shop", "where", "resellers", "about", "blog"]
def page(out_rel, title, desc, body, active="", extra_head="", og_image=None, root=None):
    depth = out_rel.count("/")
    root = ("../" * depth) if root is None else root
    canonical = BASE + (out_rel[:-len("index.html")] if out_rel.endswith("index.html") else out_rel)
    robots = '<meta name="robots" content="noindex,nofollow">\n' if PROTOTYPE else ""
    head = read("head.html").replace("{{TITLE}}", esc(title)).replace("{{DESC}}", esc(desc)).replace("{{ROOT}}", root) \
        .replace("{{CANONICAL}}", canonical).replace("{{ROBOTS}}", robots).replace("{{V}}", V).replace("{{OG}}", og_image or BASE + "assets/img/og-cover.png") \
        .replace("{{EXTRA}}", extra_head)
    for nid in NAV_IDS:
        head = head.replace("{{A_%s}}" % nid, ' class="active"' if nid == active else "")
    foot = read("footer.html").replace("{{ROOT}}", root).replace("{{V}}", V).replace("{{YEAR}}", str(datetime.date.today().year))
    write(out_rel, head + body.replace("{{ROOT}}", root) + foot)

def label_head(left, right=""):
    return '<div class="label-head">%s%s</div>' % (left, '<span class="right">%s</span>' % right if right else "")

# ---------------------------------------------------------------- guides (focus categories)
GUIDES = {
    "pain-relief": {
        "intro": "Rheuma-Salve® has been Singapore's pharmacy-shelf pain relief since 1994. One formula, five formats. The right pick depends on where it hurts, how long you need relief, and whether you are at home, at work or on the move.",
        "faq": [
            ("What is the difference between the balm and the crème?", "The balm is a snowy-white, menthol-rich salve with a stronger warming-cooling action for deep joint and muscle pain. The crème uses the same proprietary formula in a lighter, non-greasy base that absorbs quickly and does not stain clothing."),
            ("How long can I wear the Pain Relief Patch?", "Apply to clean, dry skin and remove after 6 hours. Use 2 to 3 patches a day at most, and do not apply to open wounds or during pregnancy or breastfeeding."),
            ("Is Rheuma-Salve® made in Singapore?", "Yes. The balm, crème, liniment and Medi-Stick are made in Singapore under GMP. The patch is manufactured in Taiwan exclusively for HST Medical."),
            ("Who should not use Rheuma-Salve®?", "External use only. Do not use on broken skin, on children under two, or during pregnancy or breastfeeding without asking a pharmacist. Stop and seek advice if irritation occurs."),
        ],
    },
    "cough-cold-flu": {
        "intro": "Six herbal remedies cover the arc of a cold, from the first tickle in the throat to a blocked nose that will not clear. All are formulated by HST Medical's pharmacists and TCM physicians.",
        "faq": [
            ("Which product should I take for a sore throat?", "Start with Alievaid Herbal Drops or Ivy Leaf Drops. Both are lozenges you dissolve slowly, with loquat leaf, jie geng and luo han guo (Alievaid) or ivy leaf extract (Ivy Leaf) to soothe the throat and calm an irritating cough."),
            ("Is Flu Gard suitable for children?", "Flu Gard is a traditional Chinese medicine formula in vegicaps for adults. Follow the label and ask a pharmacist for children, during pregnancy, or if symptoms last more than a few days."),
            ("Are these products Halal?", "Alievaid Herbal Drops carry Halal (Malaysia) certification. The certification mark is printed on each pack; the full list of certified products is being confirmed with HST Medical."),
            ("Can I use Sinus Clear more than once?", "Yes. The bottom half is a refill: a few drops onto the inhaler's cotton stick restores it. Single-person use is recommended."),
        ],
    },
}

# ---------------------------------------------------------------- HOME
def build_home():
    root = ""
    counters = "".join(f"""<a href="shop/{cid}/"{' class="pain"' if i == 0 else ''}>{esc(name)}<small>{esc(sub)}</small>{'<span class="stamp">Start here</span>' if i == 0 else ''}</a>""" for i, (cid, name, sub) in enumerate(COUNTERS))
    shelf = "".join(f"""<a href="shop/{cid}/"{' class="pain"' if cid == 'pain-relief' else ''}><b>{esc(CATS[cid]['name'])}</b><span>{esc(CATS[cid]['blurb'])}</span><small>{len(cat_products(cid))} products</small></a>""" for cid in CAT_ORDER)
    notes = "".join(f"""<a href="blog/{s}/"><time datetime="{d}">{d}</time><span><b>{esc(t)}</b>{esc(x)}</span></a>""" for s, t, d, x, _ in POSTS)
    body = f"""
<main id="main">
<section class="hero" aria-labelledby="h1">
  <div class="counter"><div class="label">
    {label_head('<b>HST Medical</b> <span>Dispensed for you</span> <span>Formulated by pharmacists and TCM physicians</span>', 'Singapore · since 1994 · a Kowa company')}
    <div class="hero-body">
      <div>
        <h1 id="h1">Pain, cough or cold? Start here.</h1>
        <p class="dose">Singapore-made remedies you already know from the Guardian, Watsons and NHGP shelf. Pick the format that fits, see the real price for the real pack, and we deliver island-wide.</p>
        <ul class="checks" style="margin-top:1.25rem">
          <li>{IC['tick']}<span>Made under GMP in Singapore; Halal-certified options</span></li>
          <li>{IC['tick']}<span>Thirty years on the pharmacy shelf; a Kowa subsidiary since 2024</span></li>
          <li>{IC['tick']}<span>Free island-wide delivery over S$60</span></li>
        </ul>
      </div>
      <figure class="hero-pack">
        <img src="assets/img/products/p03.webp" alt="Heritage Rheuma-Salve Balm 50g jar and box" width="536" height="536" fetchpriority="high" decoding="async">
        <a class="tab stamped" href="products/rheuma-salve-balm/">Rheuma-Salve® Balm 50g <small>Best seller · {esc(money(BY_SLUG['rheuma-salve-balm']['price']))}</small></a>
      </figure>
    </div>
    <nav class="counters" aria-label="Start by need">{counters}</nav>
  </div></div>
</section>

<section class="band" aria-labelledby="h-pain">
  <div class="counter">
    <div class="band-head"><div><h2 id="h-pain">Which pain relief do I need?</h2><p>{esc(GUIDES['pain-relief']['intro'])}</p></div><a class="btn btn-quiet" href="shop/pain-relief/">The pain relief counter {IC['arrow']}</a></div>
    <div class="label heritage"><div class="label-body">{compare_table('pain-relief', root)}</div></div>
  </div>
</section>

<section class="band paper" aria-labelledby="h-cough">
  <div class="counter">
    <div class="band-head"><div><h2 id="h-cough">Cough, cold or flu: match the symptom</h2><p>{esc(GUIDES['cough-cold-flu']['intro'])}</p></div><a class="btn btn-quiet" href="shop/cough-cold-flu/">The cough and cold counter {IC['arrow']}</a></div>
    <div class="label"><div class="label-body">{compare_table('cough-cold-flu', root)}</div></div>
  </div>
</section>

<section class="band" aria-labelledby="h-shelf">
  <div class="counter">
    <div class="band-head"><div><h2 id="h-shelf">Eleven shelves, one standard</h2><p>Every product is developed by HST Medical's own pharmacists and TCM physicians from ethically sourced ingredients, then tested for authenticity and safety before it reaches the counter.</p></div><a class="btn btn-quiet" href="shop/">All 51 products {IC['arrow']}</a></div>
    <nav class="shelf" aria-label="Ranges">{shelf}</nav>
  </div>
</section>

<section class="band paper" aria-labelledby="h-trust">
  <div class="counter grid12" style="align-items:start">
    <div style="grid-column:1 / span 7"><h2 id="h-trust">Dispensed by pharmacists since 1994</h2>
      <div class="label" style="margin-top:1.25rem"><div class="facts">
        <div><b>1994</b><p>Founded in Singapore as a manufacturer and supplier to the major pharmacy chains.</p></div>
        <div><b>GMP</b><p>Made under Good Manufacturing Practice, with Halal-certified and vegan options across the range.</p></div>
        <div><b>Two lines</b><p>HST Medical® for contemporary formulas; Heritage® for traditional Asian remedies prepared to modern standards.</p></div>
        <div><b>Kowa</b><p>A subsidiary of Kowa Company, Ltd. since 2024, the Japanese group behind Vantelin.</p></div>
      </div></div></div>
    <div style="grid-column:8 / span 5"><h2 style="font-size:1.4rem">Where to buy</h2>
      <p style="margin:.5rem 0 .25rem">On the shelf at:</p><ul class="where">{''.join('<li>%s</li>' % esc(r) for r in RETAILERS_CONFIRMED)}</ul>
      <p class="small" style="margin-top:.75rem">Other stockists are being confirmed with HST Medical. <a href="where-to-buy/">Stockist list and delivery details</a>.</p>
      <div class="label" style="margin-top:1.5rem"><div class="label-body trade"><div><h3>Pharmacies, clinics and distributors</h3><p class="small" style="margin-top:.25rem">Open a trade account, download the product sheets and order through your HST Medical territory manager.</p></div><a class="btn" href="resellers/">Trade enquiries</a></div></div>
    </div>
  </div>
</section>

<section class="band" aria-labelledby="h-notes">
  <div class="counter">
    <div class="band-head"><div><h2 id="h-notes">Health notes</h2><p>Short, practical reading written with HST Medical's pharmacists.</p></div><a class="btn btn-quiet" href="blog/">All notes {IC['arrow']}</a></div>
    <div class="label"><nav class="notes" aria-label="Latest health notes">{notes}</nav></div>
  </div>
</section>
</main>"""
    ld = jsonld({"@context": "https://schema.org", "@graph": [ORG, {"@type": "WebSite", "url": BASE, "name": "HST Medical", "publisher": {"@id": BASE + "#org"},
                 "potentialAction": {"@type": "SearchAction", "target": BASE + "shop/?q={search_term_string}", "query-input": "required name=search_term_string"}}]})
    page("index.html", "HST Medical Singapore — Rheuma-Salve® Pain Relief, Cough & Cold Remedies, Heritage® Tonics",
         "Pain, cough or cold? Start at the HST Medical counter: Rheuma-Salve®, Alievaid, Flu Gard and 51 pharmacist-formulated products made in Singapore since 1994. A Kowa subsidiary. GMP, Halal options.",
         body, extra_head=ld)
    add_sitemap(BASE, "1.0")

# ---------------------------------------------------------------- SHOP + CATEGORIES
def filters_html(root, active=None):
    groups = ""
    for gname, cids in FILTER_GROUPS:
        tabs = "".join(f'<a class="tab" role="button" aria-pressed="{"true" if cid == active else "false"}" href="{root}shop/{cid}/" data-cat="{cid}">{esc(CATS[cid]["name"])}</a>' for cid in cids)
        groups += f'<div class="group"><span>{gname}</span><div class="tabs">{tabs}</div></div>'
    return f"""<div class="filters"><div class="group"><span>Show</span><div class="tabs"><a class="tab" role="button" aria-pressed="{"true" if active is None else "false"}" href="{root}shop/" data-cat="all">All products</a></div></div>{groups}</div>"""

def build_shop():
    root = "../"
    crumb, crumb_ld = crumbs(root, [("All products", None)])
    cards = "\n".join(product_label(p, root) for cid in CAT_ORDER for p in cat_products(cid))
    body = f"""
<main id="main"><div class="counter">{crumb}
<header class="page-head"><h1>All products</h1><p class="lead">{len(PRODUCTS)} products across {len(CAT_ORDER)} shelves. Prices in Singapore dollars including GST. Free island-wide delivery on orders over S$60.</p></header>
<form class="search" role="search" action="" onsubmit="return false"><label class="sr-only" for="q">Search products</label><input id="q" type="search" name="q" placeholder="Search: balm, melatonin, ginseng, kids…" autocomplete="off"><button class="btn" type="submit" aria-label="Search">{IC['search']}</button></form>
{filters_html(root)}
<h2 class="result" id="result">Showing {len(PRODUCTS)} of {len(PRODUCTS)} products</h2>
<div class="empty" id="shop-empty" hidden><b>No match.</b>Try a shorter word, or start from a shelf: <a href="pain-relief/">pain relief</a>, <a href="cough-cold-flu/">cough and cold</a>, <a href="kids/">kids</a>, <a href="stress-sleep/">sleep</a>.</div>
<div class="labels" id="shop-grid">{cards}</div>
</div></main>"""
    page("shop/index.html", "All products — HST Medical Singapore", "Every HST Medical®, Heritage® and Zoo-Vite® product: pain relief, cough and cold, tonics, kids, sleep, bones and joints and more. Island-wide delivery from Singapore.", body, active="shop", extra_head=crumb_ld)
    add_sitemap(BASE + "shop/", "0.9")

    for cid in CAT_ORDER:
        c = CATS[cid]; ps = cat_products(cid); root = "../../"
        crumb, crumb_ld = crumbs(root, [("All products", root + "shop/"), (c["name"], None)])
        cards = "\n".join(product_label(p, root) for p in ps)
        extra = crumb_ld + jsonld({"@context": "https://schema.org", "@type": "CollectionPage", "name": c["name"], "url": BASE + "shop/%s/" % cid, "description": c["blurb"],
                                   "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + "products/%s/" % p["slug"], "name": p["name"]} for i, p in enumerate(ps)]}})
        guide = faq = ""
        if cid in GUIDES:
            g = GUIDES[cid]
            guide = f"""<section aria-labelledby="h-guide" style="margin-bottom:2.5rem"><h2 id="h-guide" style="margin-bottom:.5rem">Which one do I need?</h2><p style="margin-bottom:1rem">{esc(g['intro'])}</p><div class="label {'heritage' if cid == 'pain-relief' else ''}"><div class="label-body">{compare_table(cid, root)}</div></div></section>"""
            faqs = "".join(f"<details class='acc'><summary>{esc(q)}{IC['plus']}</summary><div class='body'><p>{esc(a)}</p></div></details>" for q, a in g["faq"])
            faq = f"""<section class="band paper" aria-labelledby="h-faq"><div class="counter grid12"><div style="grid-column:1 / span 5"><h2 id="h-faq">Ask the pharmacist</h2><p style="margin-top:.5rem">Common questions at the {esc(c['name'].lower())} counter.</p><p class="caution">This information is general guidance. Always read the label and follow directions for use. See a pharmacist or doctor if symptoms persist.</p></div><div style="grid-column:6 / span 7">{faqs}</div></div></section>"""
            extra += jsonld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in g["faq"]]})
        body = f"""
<main id="main"><div class="counter">{crumb}
<header class="page-head"><h1>{esc(c['name'])}</h1><p class="lead">{esc(c['blurb'])}</p></header>
{guide}
{filters_html(root, cid)}
<h2 class="result">All {len(ps)} product{'s' if len(ps) != 1 else ''} on this shelf</h2>
<div class="labels">{cards}</div>
</div>
{faq}
</main>"""
        page("shop/%s/index.html" % cid, "%s — HST Medical Singapore" % c["name"], c["blurb"] + " Shop online or find a stockist in Singapore.", body,
             active={"pain-relief": "pain", "cough-cold-flu": "cough"}.get(cid, "shop"), extra_head=extra)
        add_sitemap(BASE + "shop/%s/" % cid, "0.8" if cid in FOCUS_CATS else "0.7")

# ---------------------------------------------------------------- PRODUCT PAGES
def build_products():
    for p in PRODUCTS:
        root = "../../"; c = CATS[p["category"]]; v0 = p["variants"][0]
        crumb, crumb_ld = crumbs(root, [("All products", root + "shop/"), (c["name"], root + "shop/%s/" % p["category"]), (p["name"], None)])
        packs = ""
        for i, v in enumerate(p["variants"]):
            packs += f"""<div class="pack"><input type="radio" name="pack" id="pack{i}" value="{esc(v['label'])}" data-price="{v['price'] or ''}" data-code="{v['code']}" data-size="{esc(v['label'])}"{' checked' if i == 0 else ''}><label for="pack{i}">{esc(v['label'])}<small>{esc(money(v['price']))}{(' · Item ' + v['code']) if v['code'] else ''}</small></label></div>"""
        other_skus = [s for s in p["skus"] if s["code"] not in {v["code"] for v in p["variants"]}]
        other = ("<p class='small' style='margin-top:.5rem'>Also in store: " + "; ".join("%s %s (item %s)" % (esc(s["name"].replace("Heritage ", "")), esc(s["size"]), s["code"]) for s in other_skus) + ".</p>") if other_skus else ""
        benefits = "".join("<li>%s<span>%s</span></li>" % (IC["tick"], esc(b)) for b in p["benefits"]) or "<li>%s<span>%s</span></li>" % (IC["tick"], esc(p["tagline"]))
        usage = "".join("<li>%s</li>" % esc(u) for u in p["usage"]) or "<li>Use as directed on the label.</li>"
        ingr = "".join("<li>%s</li>" % esc(u) for u in p["ingredients"]) or "<li>See pack for the full ingredient list.</li>"
        related = [x for x in cat_products(p["category"]) if x["slug"] != p["slug"]][:4]
        rel = "\n".join(product_label(x, root) for x in related)
        halal = " · Halal (Malaysia)" if p["slug"] == "alievaid-herbal-drops" else ""
        body = f"""
<main id="main"><div class="counter">{crumb}
<article class="label {brand_class(p['brand'])}" data-pdp style="margin-top:1rem">
  {label_head('<b>%s</b> <span>%s</span> <span class="print" data-code-out>Item %s</span>' % (esc(brand_label(p['brand'])), esc(c['name']), v0['code'] or '—'), esc(p['country'] or 'See pack') + halal)}
  <div class="pdp">
    <figure class="pdp-pack"><img src="{root}assets/img/products/{p['image']}.webp" alt="{esc(p['name'])}, {esc(p['size'])}" width="900" height="900" fetchpriority="high" decoding="async"></figure>
    <div class="pdp-main">
      <h1>{esc(p['name'])}</h1>
      <p class="dose">{esc(p['tagline'])}</p>
      <dl class="fields"><div class="field"><dt>For</dt><dd>{esc(p['for'])}</dd></div><div class="field"><dt>Use</dt><dd>{esc(p['usage'][0] if p['usage'] else 'As directed on the label.')}</dd></div><div class="field"><dt>Pack</dt><dd class="print" data-size-out>{esc(v0['label'])}</dd></div></dl>
      <div class="price-line print"><span class="price" data-price-out>{esc(money(v0['price']))}</span><span class="meta">SGD, incl. GST · free delivery over S$60</span></div>
      <fieldset><legend>Pack size</legend><div class="packs">{packs}</div>{other}</fieldset>
      <div class="buy">
        <div class="qty" aria-label="Quantity"><button type="button" data-step="-1" aria-label="Decrease quantity">−</button><input id="qty" type="number" min="1" max="99" value="1" inputmode="numeric" aria-label="Quantity"><button type="button" data-step="1" aria-label="Increase quantity">+</button></div>
        {add_btn(p, root, cls='btn btn-stamp', from_pdp=True)}
        <a class="btn btn-quiet" href="{root}where-to-buy/" data-enquire{' hidden' if v0['price'] else ''}>Ask in store</a>
      </div>
      <ul class="checks" style="margin-bottom:1.25rem">{benefits}</ul>
      <details class="acc" open><summary>What it is {IC['plus']}</summary><div class="body"><p>{esc(p['description'])}</p></div></details>
      <details class="acc"><summary>How to use {IC['plus']}</summary><div class="body"><ul>{usage}</ul></div></details>
      <details class="acc"><summary>Active ingredients {IC['plus']}</summary><div class="body"><ul>{ingr}</ul></div></details>
      <details class="acc"><summary>Where else to buy {IC['plus']}</summary><div class="body"><ul class="where">{''.join('<li>%s</li>' % esc(r) for r in RETAILERS_CONFIRMED)}</ul><p class="small" style="margin-top:.75rem">Also on the current store at hstmedical.com{(' (<a href="%s" rel="noopener">listing</a>)' % esc(v0['url'])) if v0.get('url') else ''}.</p></div></details>
      <p class="caution">Always read the label and follow directions for use. {'External use only. Not for broken skin; ask a pharmacist before use in pregnancy or for young children.' if p['category'] in ('pain-relief', 'traditional-pain-relief') else 'A health supplement or herbal remedy, not a substitute for medical care. Ask a pharmacist if symptoms persist.'}</p>
    </div>
  </div>
</article>
</div>
<section class="band" aria-labelledby="h-rel"><div class="counter"><div class="band-head"><h2 id="h-rel">Also at the {esc(c['name'].lower())} counter</h2><a class="btn btn-quiet" href="{root}shop/{p['category']}/">The whole shelf {IC['arrow']}</a></div><div class="labels">{rel}</div></div></section>
</main>"""
        offers = [{"@type": "Offer", "name": v["label"], "priceCurrency": "SGD", "price": "%.2f" % v["price"], "availability": "https://schema.org/InStock", "sku": v["code"] or None, "url": BASE + "products/%s/" % p["slug"]} for v in p["variants"] if v["price"]]
        for o in offers:
            if o["sku"] is None: del o["sku"]
        ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "brand": {"@type": "Brand", "name": brand_label(p["brand"]).replace("®", "")},
              "image": BASE + "assets/img/products/%s.webp" % p["image"], "description": p["description"][:300], "category": c["name"],
              "manufacturer": {"@id": BASE + "#org"}, "url": BASE + "products/%s/" % p["slug"]}
        if offers:
            ld["offers"] = offers if len(offers) > 1 else offers[0]
        page("products/%s/index.html" % p["slug"], "%s (%s) — %s | HST Medical" % (p["name"], p["size"], brand_label(p["brand"])),
             ("%s. For %s. %s" % (p["tagline"], p["for"], p["description"]))[:158], body, active={"pain-relief": "pain", "cough-cold-flu": "cough"}.get(p["category"], "shop"),
             extra_head=crumb_ld + jsonld(ld), og_image=BASE + "assets/img/products/%s.webp" % p["image"])
        add_sitemap(BASE + "products/%s/" % p["slug"], "0.8" if p["focus"] else "0.6")

# ---------------------------------------------------------------- STATIC PAGES
def simple(out_rel, title, desc, h1, lead, inner, active="", extra=""):
    root = "../" * out_rel.count("/")
    crumb, crumb_ld = crumbs(root, [(h1, None)])
    body = f"""
<main id="main"><div class="counter">{crumb}
<header class="page-head"><h1>{esc(h1)}</h1>{'<p class="lead">%s</p>' % lead if lead else ''}</header>
{inner}
</div></main>"""
    page(out_rel, title, desc, body, active=active, extra_head=crumb_ld + extra)
    add_sitemap(BASE + out_rel[:-len("index.html")])

def field(name, label, typ="text", req=False, **attrs):
    a = " ".join('%s="%s"' % (k.replace("_", "-"), esc(v)) for k, v in attrs.items())
    return f"""<label><span class="{'req' if req else ''}">{label}</span><input type="{typ}" name="{name}"{' required' if req else ''} {a}><span class="err">{label} is needed.</span></label>"""

def build_static():
    simple("about/index.html", "About HST Medical — Singapore's Pharmacy-Shelf Remedies Since 1994",
           "Established in 1994 and part of Kowa since 2024, HST Medical formulates and supplies health supplements and pain relief remedies to Singapore's major pharmacies.",
           "About HST Medical", "Established in 1994, HST Medical is a manufacturer and supplier of health supplements and pain relief remedies to major pharmacies and online marketplaces.",
           f"""
<div class="grid12" style="align-items:start">
  <div class="article" style="grid-column:1 / span 7">
    <h2>Contemporary pharmaceuticals, traditional benefits</h2>
    <p>HST Medical products pair contemporary pharmaceuticals with the long-term benefits of natural nutrients. The pharmacists and TCM physicians behind the range develop formulas for modern needs from ethically sourced ingredients around the world.</p>
    <h2>Quality and safety first</h2>
    <p>From research and development to packaging and manufacturing, HST Medical follows authority guidelines, approved procedures and inspected premises. Ingredients are tested for authenticity, finished products are verified for safety, and third-party manufacturing is audited.</p>
    <h2>Part of Kowa</h2>
    <p>In 2024 HST Medical became a subsidiary of Kowa Company, Ltd., the Japanese pharmaceutical and trading group whose consumer brands include Vantelin and Three Dimension Mask. Kowa's research depth joins HST Medical's Singapore-made range while the brands on the shelf stay the same.</p>
  </div>
  <div style="grid-column:8 / span 5" class="stack">
    <div class="label"><div class="facts" style="grid-template-columns:1fr"><div><b>1994</b><p>Founded in Singapore. Thirty years supplying Guardian, Watsons, NHGP and online marketplaces.</p></div><div><b>Three brands</b><p>HST Medical®, Heritage® and Zoo-Vite®, plus Rheuma-Salve®, the flagship pain-relief line.</p></div><div><b>GMP</b><p>Manufactured under Good Manufacturing Practice with Halal-certified and vegan options.</p></div></div></div>
    <div class="label"><div class="label-body"><h3>Recognition</h3><ul class="checks" style="margin-top:.5rem"><li>{IC['tick']}<span>2024 Beauty Insider Awards, hair and wellness supplements</span></li><li>{IC['tick']}<span>Guardian retailer award</span></li><li>{IC['tick']}<span>5.0 Google rating (Trustindex)</span></li></ul><p class="small" style="margin-top:.75rem">As listed on the current hstmedical.com; to be confirmed with the client.</p></div></div>
  </div>
</div>""", active="about")

    brand_rows = ""
    for name, cls, blurb, cids in [
        ("Rheuma-Salve®", "heritage", "Singapore's extra-strength pain relief since 1994: balm, crème, liniment, patch and Medi-Stick.", ["pain-relief"]),
        ("Heritage®", "heritage", "Traditional Asian remedies prepared to modern GMP standards: ginseng, cordyceps, lingzhi, pearl powder, squalene, crocodile oil and medicated oils.", ["immunity-energy", "beauty-wellness", "traditional-pain-relief"]),
        ("HST Medical®", "", "Pharmaceutical-grade supplements and herbal remedies for cough and cold, bones and joints, sleep, eyes, heart, liver and vitality.", ["cough-cold-flu", "bones-joints", "alertness-memory-vision", "stress-sleep", "immunity-allergy", "heart-liver-vitality"]),
        ("Zoo-Vite®", "zoo", "Kids' gummies and jelly sticks with characters children remember: Perky Penguin, Inspector Charley, Safari Buddies, Super Panda and Professor Skippy.", ["kids"]),
    ]:
        links = "".join(f"<a class='tab' href='../shop/{c}/'>{esc(CATS[c]['name'])}</a>" for c in cids)
        brand_rows += f"<div class='label {cls}'><div class='label-body'><h2>{esc(name)}</h2><p style='margin:.5rem 0 1rem'>{esc(blurb)}</p><div class='tabs'>{links}</div></div></div>"
    simple("brands/index.html", "Our Brands — Rheuma-Salve®, Heritage®, HST Medical®, Zoo-Vite® and Kowa",
           "Four brands under one quality standard, part of the Kowa group alongside Vantelin and Three Dimension Mask.",
           "Our brands", "Four brands, one standard, one parent: Kowa.",
           f"""<div class="labels" style="grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr))">{brand_rows}</div>
<div class="label" style="margin-top:var(--gutter)"><div class="label-body trade"><div><h2 style="font-size:1.4rem">Kowa: Japanese pharmaceutical heritage</h2><p style="margin-top:.5rem">Kowa Company, Ltd. (Nagoya, est. 1894) owns consumer brands such as Vantelin topical pain relief and Three Dimension Mask. HST Medical joined the group in 2024. Whether Kowa's Singapore range is listed here is still to be decided with the client.</p></div><a class="btn btn-quiet" href="../about/">Our story</a></div></div>""", active="about")

    simple("where-to-buy/index.html", "Where to Buy HST Medical Products in Singapore — Guardian, Watsons, NHGP and Online",
           "Find Rheuma-Salve®, Heritage® and Zoo-Vite® at Guardian, Watsons and NHGP pharmacies, or order online with island-wide delivery.",
           "Where to buy", "On the shelf at Singapore's pharmacy chains, and online with island-wide delivery.",
           f"""
<div class="grid12" style="align-items:start">
  <div style="grid-column:1 / span 7" class="label"><div class="facts" style="grid-template-columns:1fr">
    {''.join(f"<div><b>{esc(r)}</b><p>{t}</p></div>" for r, t in [
        ("Guardian", "Rheuma-Salve®, Heritage® tonics and selected HST Medical® supplements in most outlets island-wide."),
        ("Watsons", "Pain relief, cough and cold and kids' ranges. Check in-store availability for tonics."),
        ("NHGP pharmacies", "National Healthcare Group polyclinic pharmacies carry the core pain-relief and cough range."),
        ("Online", "This store ships island-wide (free over S$60) and internationally at checkout."),
    ])}
  </div></div>
  <div style="grid-column:8 / span 5" class="stack">
    <div class="label"><div class="label-body"><h2 style="font-size:1.3rem">To be confirmed</h2><p class="small" style="margin:.5rem 0">Stockists reported but not yet verified with HST Medical:</p><ul class="where">{''.join('<li>%s</li>' % esc(r) for r in RETAILERS_TBC)}</ul><p class="small" style="margin-top:.75rem">A postcode store locator is planned for the production build.</p></div></div>
    <div class="label"><div class="label-body trade"><div><h2 style="font-size:1.3rem">Stock us</h2><p class="small" style="margin-top:.25rem">Retailers, clinics and distributors order direct.</p></div><a class="btn" href="../resellers/">Trade enquiries</a></div></div>
  </div>
</div>""", active="where")

    simple("resellers/index.html", "Trade and Resellers — Pharmacies, Clinics and Distributors | HST Medical",
           "Open a trade account with HST Medical Singapore. Pharmacies, clinics, TCM halls and distributors order through a territory manager with product sheets and pack configurations.",
           "Trade and resellers", "HST Medical supplies pharmacies, clinics, TCM halls, e-commerce sellers and overseas distributors directly. Tell us about your business and a territory manager will be in touch within two working days.",
           f"""
<div class="grid12" style="align-items:start">
  <div style="grid-column:1 / span 5" class="stack">
    <div class="label"><div class="label-body"><h2 style="font-size:1.3rem">What a trade account includes</h2>
      <ol class="steps" style="margin-top:.75rem"><li><b>A territory manager.</b> One contact for orders, re-orders and promotions.</li><li><b>Product sheets.</b> Benefits, usage, active ingredients, item codes and pack configurations for all 51 products.</li><li><b>Trade pricing.</b> Single, twin, triple, value and travel packs with tiered pricing.</li><li><b>Shelf support.</b> Point-of-sale material, product training and seasonal campaigns.</li></ol></div></div>
    <div class="label"><div class="label-body"><h2 style="font-size:1.3rem">Already a reseller?</h2><p style="margin-top:.5rem">Email <a href="mailto:resellercontact@hstmedical.com">resellercontact@hstmedical.com</a> or contact your territory manager. A self-service portal with order history and one-click re-orders is proposed for Phase 2.</p></div></div>
  </div>
  <form class="label form" style="grid-column:6 / span 7;padding:1.5rem" data-demo novalidate>
    <h2 style="font-size:1.3rem">Trade enquiry</h2>
    <div class="row">{field('company', 'Business name', req=True, autocomplete='organization')}<label><span class="req">Business type</span><select name="type" required><option value="">Choose…</option><option>Pharmacy</option><option>Clinic / GP</option><option>TCM hall</option><option>E-commerce seller</option><option>Distributor (overseas)</option><option>Other</option></select><span class="err">Business type is needed.</span></label></div>
    <div class="row">{field('name', 'Contact person', req=True, autocomplete='name')}{field('role', 'Role')}</div>
    <div class="row">{field('email', 'Email', 'email', True, autocomplete='email', inputmode='email')}{field('phone', 'Phone or WhatsApp', 'tel', autocomplete='tel')}</div>
    {field('country', 'Country or region', value='Singapore')}
    {field('ranges', 'Ranges of interest', placeholder='e.g. Rheuma-Salve®, cough and cold, Zoo-Vite®')}
    <label><span>Message</span><textarea name="message" placeholder="Number of outlets, expected volume, timing"></textarea></label>
    <label class="check"><input type="checkbox" name="consent" required><span>I agree to be contacted about a trade account; my details are handled under the <a href="../privacy/">privacy policy</a>.</span></label><span class="err" style="margin-top:-.5rem">Please tick the consent box.</span>
    <button class="btn btn-stamp" type="submit">Send enquiry {IC['arrow']}</button>
    <p class="note">Prototype: nothing is sent. The production form posts to the WordPress contact handler and notifies resellercontact@hstmedical.com.</p>
    <p class="ok">Thank you. A territory manager will contact you within two working days.</p>
  </form>
</div>""", active="resellers")

    simple("contact/index.html", "Contact HST Medical Singapore", "Customer service, order questions and trade enquiries for HST Medical Pte Ltd, Singapore.",
           "Contact us", "Questions about an order, a product or a trade account? We reply within two working days.",
           f"""
<div class="grid12" style="align-items:start">
  <div style="grid-column:1 / span 5" class="label"><div class="facts" style="grid-template-columns:1fr">
    <div><b>Customer service</b><p>Orders, delivery and product questions.<br><a href="mailto:hello@hstmedical.com">hello@hstmedical.com</a><br><span class="small">Placeholder address; to confirm with the client.</span></p></div>
    <div><b>Trade</b><p><a href="mailto:resellercontact@hstmedical.com">resellercontact@hstmedical.com</a><br>or your HST Medical territory manager.</p></div>
    <div><b>HST Medical Pte Ltd</b><p>Singapore<br><span class="small">Registered address, phone and opening hours to be supplied by the client.</span></p></div>
  </div></div>
  <form class="label form" style="grid-column:6 / span 7;padding:1.5rem" data-demo novalidate>
    <h2 style="font-size:1.3rem">Send a message</h2>
    <div class="row">{field('name', 'Name', req=True, autocomplete='name')}{field('email', 'Email', 'email', True, autocomplete='email')}</div>
    <label><span>Topic</span><select name="topic"><option>Order or delivery</option><option>Product question</option><option>Trade enquiry</option><option>Press</option><option>Other</option></select></label>
    <label><span class="req">Message</span><textarea name="message" required></textarea><span class="err">A message is needed.</span></label>
    <button class="btn btn-stamp" type="submit">Send {IC['arrow']}</button>
    <p class="ok">Thanks. We have your message and will reply within two working days.</p>
  </form>
</div>""")

    simple("cart/index.html", "Your bag — HST Medical", "Review your HST Medical order before checkout.", "Your bag", "",
           f"""
<div class="bag-grid">
  <div class="label"><div class="lines" id="bag-lines" data-root="../"><div class="empty"><b>Your bag is empty.</b>Start at the counter: <a href="../shop/pain-relief/">pain relief</a>, <a href="../shop/cough-cold-flu/">cough and cold</a>, or <a href="../shop/">all products</a>.</div></div></div>
  <aside class="label summary" aria-labelledby="h-sum"><div class="label-body"><h2 id="h-sum" style="font-size:1.3rem;margin-bottom:.75rem">Summary</h2>
    <dl class="fields"><div class="field"><dt>Subtotal</dt><dd data-sub>S$0.00</dd></div><div class="field"><dt>Delivery</dt><dd data-ship>—</dd></div><div class="field total"><dt>Total</dt><dd data-total>S$0.00</dd></div></dl>
    <div class="meter" aria-hidden="true"><i></i></div><p class="small" data-free>Free delivery on orders over S$60.</p>
    <div class="stack" style="margin-top:1rem"><a class="btn btn-stamp btn-block" href="../checkout/" data-needs-items aria-disabled="true">Checkout {IC['arrow']}</a><a class="btn btn-quiet btn-block" href="../shop/">Keep shopping</a></div>
    <p class="note small" style="margin-top:1rem">Prototype bag stored in your browser only. Production uses WP EasyCart's cart with this layout applied through CSS overrides.</p>
  </div></aside>
</div>""", active="shop")

    simple("checkout/index.html", "Checkout — HST Medical", "Secure checkout for HST Medical orders.", "Checkout", "",
           f"""
<div class="bag-grid">
  <form class="label form" style="padding:1.5rem" data-demo novalidate>
    <ol class="steps-bar" aria-label="Checkout steps"><li aria-current="step">1 · Contact</li><li>2 · Delivery</li><li>3 · Payment</li></ol>
    <section class="step"><h2>Who is this order for?</h2>
      <div class="row">{field('email', 'Email', 'email', True, autocomplete='email', inputmode='email')}{field('mobile', 'Mobile', 'tel', True, autocomplete='tel', inputmode='tel')}</div>
      <p class="note">We use these for the order confirmation and delivery updates only.</p>
      <div class="step-nav"><span></span><button class="btn" type="button" data-next>Continue to delivery {IC['arrow']}</button></div></section>
    <section class="step" hidden><h2>Where should we deliver?</h2>
      <div class="row">{field('first', 'First name', req=True, autocomplete='given-name')}{field('last', 'Last name', req=True, autocomplete='family-name')}</div>
      {field('address', 'Address', req=True, autocomplete='street-address')}
      <div class="row">{field('unit', 'Unit', autocomplete='address-line2')}{field('postal', 'Postal code', req=True, inputmode='numeric', autocomplete='postal-code', pattern='[0-9]{{6}}')}<label><span>Country</span><select name="country" autocomplete="country-name"><option>Singapore</option><option>Malaysia</option><option>Other</option></select></label></div>
      <div class="lbl"><span>Delivery method</span><label class="check"><input type="radio" name="ship" checked><span>Courier, 2 to 3 working days (free over S$60, otherwise S$4.50)</span></label><label class="check"><input type="radio" name="ship"><span>Self-collection, by appointment</span></label></div>
      <div class="step-nav"><button class="btn btn-quiet" type="button" data-prev>Back</button><button class="btn" type="button" data-next>Continue to payment {IC['arrow']}</button></div></section>
    <section class="step" hidden><h2>How would you like to pay?</h2>
      <div class="lbl"><span>Payment</span><label class="check"><input type="radio" name="pay" checked><span>Card (Visa, Mastercard, Amex)</span></label><label class="check"><input type="radio" name="pay"><span>PayNow</span></label><label class="check"><input type="radio" name="pay"><span>GrabPay, Apple Pay, Google Pay</span></label></div>
      <label class="check"><input type="checkbox" name="terms" required><span class="req">I accept the terms of sale and the <a href="../privacy/">privacy policy</a></span></label><span class="err" style="margin-top:-.5rem">Please accept the terms to place the order.</span>
      <div class="step-nav"><button class="btn btn-quiet" type="button" data-prev>Back</button><button class="btn btn-stamp" type="submit" data-needs-items>Place order {IC['arrow']}</button></div>
      <div class="assure"><div><b>Secure payment</b>Card details are handled by the payment gateway, never stored here.</div><div><b>Delivery 2 to 3 working days</b>Island-wide courier; tracking by email.</div><div><b>Questions?</b><a href="../contact/">Contact us</a> before or after your order.</div></div>
      <p class="caution">Always read the label and follow directions for use.</p></section>
    <p class="note">Prototype: nothing is charged. Production checkout is WP EasyCart with the configured gateway; this layout is applied via CSS overrides on EasyCart's checkout wrapper.</p>
    <p class="ok">Order placed (demo). A confirmation email would follow with your order number.</p>
  </form>
  <aside class="label summary" aria-labelledby="h-sum"><div class="label-body"><h2 id="h-sum" style="font-size:1.3rem;margin-bottom:.75rem">Your bag</h2>
    <div id="bag-lines" data-root="../"></div>
    <dl class="fields" style="margin-top:.5rem"><div class="field"><dt>Subtotal</dt><dd data-sub>S$0.00</dd></div><div class="field"><dt>Delivery</dt><dd data-ship>—</dd></div><div class="field total"><dt>Total</dt><dd data-total>S$0.00</dd></div></dl>
    <p class="small" data-free>Free delivery on orders over S$60.</p>
  </div></aside>
</div>""", active="shop")

    simple("privacy/index.html", "Privacy Policy — HST Medical", "How HST Medical Pte Ltd collects and uses personal data under Singapore's PDPA.", "Privacy policy", "",
           """<div class="label"><div class="label-body article"><p>HST Medical Pte Ltd collects personal data to process orders, respond to enquiries and, with consent, send product news. Data is handled under Singapore's Personal Data Protection Act (PDPA).</p><h2>What we collect</h2><ul><li>Contact and delivery details you enter at checkout or in forms</li><li>Order history and customer-service correspondence</li><li>Basic analytics (page views, device type) to improve the site</li></ul><h2>Your rights</h2><p>You can request access to, correction of, or deletion of your data by writing to our Data Protection Officer through the contact page.</p><p class="small" style="margin-top:1rem">Placeholder text for the prototype. The production policy will be supplied by the client's legal team.</p></div></div>""")

# ---------------------------------------------------------------- BLOG
POSTS = [
    ("balm-creme-liniment-or-patch", "Balm, crème, liniment or patch? Choosing the right Rheuma-Salve® format", "2026-10-02",
     "Five formats, one formula. Where it hurts and where you are decide which to reach for.",
     """<p>Rheuma-Salve® started as a single snowy-white balm in 1994. Thirty years later the proprietary blend of menthol, peppermint, wintergreen, camphor and eucalyptus comes in five formats. The active ingredients are consistent; what changes is how deep, how long and how tidy the relief is.</p>
<h2>Balm: deep and warming</h2><p>The classic 50g jar. Best for stiff knees, lower-back ache after a long day and tight shoulders. The balm sits on the skin longer than the crème, so the warming-cooling sensation builds. It also clears congestion when rubbed on the chest.</p>
<h2>Crème: light and tidy</h2><p>Same formula, non-greasy base. Absorbs in a minute and will not mark office clothes. The sensible choice for daily aches and for anyone who finds balms heavy.</p>
<h2>Liniment: fast and penetrating</h2><p>The 10ml oil is for sports strains and sprains. Massage it in before and after exercise.</p>
<h2>Patch (Cool): hands-free for six hours</h2><p>Eight soft 10 × 7 cm patches with peppermint oil, menthol, centella, hops, frankincense and myrrh. Stick one on a sore neck or lower back, remove after six hours. Ideal for delayed onset muscle soreness after a hard session.</p>
<h2>Medi-Stick: pocket relief</h2><p>A 15g glide-on stick. No mess, no greasy fingers, fits a gym bag or handbag.</p>
<blockquote>Rule of thumb: balm for deep joint pain, crème for daily aches, liniment for sports, patch for hands-free hours, stick for the road.</blockquote>
<p>Always read the label and follow directions for use. If pain persists beyond a week, see a doctor.</p>"""),
    ("cough-cold-or-flu-which-remedy", "Cough, cold or flu? Matching the symptom to the remedy", "2026-09-25",
     "Sore throat, chesty cough, fever or blocked nose: six herbal remedies, each with a job.",
     """<p>A cold rarely arrives all at once. It starts as a tickle, becomes a cough, sometimes turns into a fever and often ends with a nose that will not clear. HST Medical's cough, cold and flu range follows that arc.</p>
<h2>Day 1: sore, scratchy throat</h2><p>Alievaid Herbal Drops combine loquat leaf, jie geng, luo han guo and cordyceps with a strong cooling mint. Dissolve one slowly every two to three hours (maximum eight a day, age 12 and above). Ivy Leaf Drops do the same job with ivy leaf extract.</p>
<h2>Days 2 to 4: cough with phlegm</h2><p>Cough Alievaid Herbal Lintus is the syrup for a productive cough. Ivy Leaf Cough Syrup comes in single-dose 10ml sachets, convenient for travel (follow the label for ages).</p>
<h2>Fever, aches, sneezing</h2><p>Flu Gard is a 100 percent herbal TCM formula in vegicaps that reduces fever, eases body aches, runny nose and sneezing, relieves cough and reduces phlegm. Two to six vegicaps, three times a day after food.</p>
<h2>Blocked nose and sinus headache</h2><p>Sinus Clear 2-in-1 is a lipstick-sized inhaler with a refill applicator underneath: inhale for a blocked nose, dab on the temples for a headache. It is also handy for mosquito bites.</p>
<p>Always read the label and follow directions for use. See a doctor if fever lasts more than three days or if you have difficulty breathing.</p>"""),
    ("what-gmp-and-halal-mean", "What GMP and Halal certification mean for your supplements", "2026-09-18",
     "Two marks on the pack, and what each one guarantees about how the product was made.",
     """<p>Supplement packs carry a lot of small print. Two marks matter more than the rest: GMP and Halal.</p>
<h2>GMP: how it is made</h2><p>Good Manufacturing Practice is the set of rules a facility follows so that every batch is made the same way, from raw material testing to packaging. HST Medical manufactures under GMP and additionally verifies the authenticity of ingredients, tests finished products for safety and audits any third-party manufacturer.</p>
<h2>Halal: what goes in</h2><p>Halal certification confirms that ingredients and processes meet Islamic dietary requirements, with no porcine-derived gelatine or alcohol-based carriers. Alievaid Herbal Drops carry Halal (Malaysia) certification, and vegicaps are used across much of the range.</p>
<h2>Why both matter</h2><p>GMP tells you the product is consistent and safe. Halal tells you what is inside is permissible. Together they are part of the reason pharmacies such as Guardian, Watsons and NHGP stock the range, and why we print both on the product page, not only on the pack.</p>"""),
]

def build_blog():
    root = "../"
    crumb, crumb_ld = crumbs(root, [("Health notes", None)])
    notes = "".join(f"""<a href="{s}/"><time datetime="{d}">{d}</time><span><b>{esc(t)}</b>{esc(x)}</span></a>""" for s, t, d, x, _ in POSTS)
    body = f"""
<main id="main"><div class="counter">{crumb}
<header class="page-head"><h1>Health notes</h1><p class="lead">Short, practical reading written with HST Medical's pharmacists: how to choose, how to use, and what the marks on the pack mean.</p></header>
<div class="label"><nav class="notes" aria-label="Health notes">{notes}</nav></div></div></main>"""
    page("blog/index.html", "Health Notes — Guides from HST Medical's Pharmacists", "Practical guides on pain relief, cough and cold remedies, supplements and product certification from HST Medical Singapore.", body, active="blog", extra_head=crumb_ld)
    add_sitemap(BASE + "blog/", "0.6")
    for s, t, d, x, bodyhtml in POSTS:
        root = "../../"
        crumb, crumb_ld = crumbs(root, [("Health notes", root + "blog/"), (t, None)])
        ld = jsonld({"@context": "https://schema.org", "@type": "Article", "headline": t, "description": x, "datePublished": d, "dateModified": d,
                     "author": {"@type": "Organization", "name": "HST Medical"}, "publisher": {"@id": BASE + "#org"}, "mainEntityOfPage": BASE + "blog/%s/" % s})
        body = f"""
<main id="main"><div class="counter">{crumb}
<article class="label" style="margin-top:1rem"><div class="label-body" style="padding:clamp(1.25rem,3vw,2.5rem)"><div class="article"><h1 style="font-size:clamp(1.9rem,1.2rem+2.2vw,3rem)">{esc(t)}</h1><p class="meta">Published <time datetime="{d}">{d}</time> · HST Medical</p>
{bodyhtml}
<hr class="rule"><p><a href="{root}blog/">All health notes</a> · <a href="{root}shop/">All products</a></p></div></div></article></div></main>"""
        page("blog/%s/index.html" % s, "%s — HST Medical" % t, x, body, active="blog", extra_head=crumb_ld + ld)
        add_sitemap(BASE + "blog/%s/" % s, "0.5")

# ---------------------------------------------------------------- 404, robots, sitemap, llms.txt
def build_misc():
    body = """
<main id="main"><div class="counter"><div class="label" style="margin:2rem auto;max-width:720px"><div class="label-body" style="padding:2.5rem"><h1 style="font-size:2.4rem">That page is not on the shelf.</h1><p class="lead" style="margin:1rem 0 1.5rem">The link may be old, or the product has moved. Start again at the counter.</p><div class="tabs"><a class="tab stamped" href="{{ROOT}}shop/pain-relief/">Pain relief</a><a class="tab" href="{{ROOT}}shop/cough-cold-flu/">Cough and cold</a><a class="tab" href="{{ROOT}}shop/">All products</a><a class="tab" href="{{ROOT}}">Home</a></div></div></div></div></main>"""
    page("404.html", "Page not found — HST Medical", "The page you requested could not be found.", body, root="/hst-medical-website/")
    write("robots.txt", ("User-agent: *\nDisallow: /\n\n# Prototype build: crawling disabled until client sign-off.\n" if PROTOTYPE else "User-agent: *\nAllow: /\n\n") + "Sitemap: %ssitemap.xml\n" % BASE)
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u, pr in SITEMAP:
        sm += "  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n" % (u, TODAY, pr)
    write("sitemap.xml", sm + "</urlset>\n")
    L = ["# HST Medical", "", "> HST Medical Pte Ltd (Singapore, est. 1994; a Kowa subsidiary since 2024) formulates and supplies health supplements and pain-relief remedies under the HST Medical®, Heritage®, Rheuma-Salve® and Zoo-Vite® brands. Products are GMP-manufactured, some Halal-certified, sold at Guardian, Watsons and NHGP pharmacies and shipped from this store in SGD.", "", "## Ranges"]
    for cid in CAT_ORDER:
        L.append("- [%s](%sshop/%s/): %s" % (CATS[cid]["name"], BASE, cid, CATS[cid]["blurb"]))
    L += ["", "## Featured products (Premium Pain Relief; Cough, Cold & Flu)"]
    for p in PRODUCTS:
        if p["focus"]:
            L.append("- [%s](%sproducts/%s/): for %s. %s. %s." % (p["name"], BASE, p["slug"], p["for"].lower(), p["size"], money(p["price"])))
    L += ["", "## All products"]
    for p in PRODUCTS:
        if not p["focus"]:
            L.append("- [%s](%sproducts/%s/): %s, %s, %s" % (p["name"], BASE, p["slug"], brand_label(p["brand"]), p["size"], money(p["price"])))
    L += ["", "## Company", "- [About](%sabout/)" % BASE, "- [Brands](%sbrands/)" % BASE, "- [Where to buy](%swhere-to-buy/)" % BASE,
          "- [Trade and resellers](%sresellers/): trade accounts for pharmacies, clinics, TCM halls and distributors; resellercontact@hstmedical.com" % BASE,
          "- [Health notes](%sblog/)" % BASE, "- [Contact](%scontact/)" % BASE]
    write("llms.txt", "\n".join(L) + "\n")

if __name__ == "__main__":
    build_home(); build_shop(); build_products(); build_static(); build_blog(); build_misc()
    print("built %d sitemap URLs, %d products, prototype=%s" % (len(SITEMAP), len(PRODUCTS), PROTOTYPE))
    for s in ("rheuma-salve-balm", "rheuma-salve-creme", "alievaid-herbal-drops", "cordyceps-cs-4", "maxi-cal"):
        print(s, [(v["label"], v["price"], v["code"]) for v in BY_SLUG[s]["variants"]])
