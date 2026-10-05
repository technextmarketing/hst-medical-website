"""
HST Medical — prototype site assembler ("The Dispensing Counter" world).

    python _src/build.py

Reads _src/products.json (catalogue_parse.py) and _src/store.json (live store prices) and writes every page
to the site root as <folder>/index.html (clean URLs). Templates map 1:1 to classic WordPress files; see
WP-MAPPING.md. PROTOTYPE = True adds noindex to every page and a robots Disallow (unlisted test link).
"""
import json, os, re, html, datetime, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import home_sections, page_where, page_about
import chat_kb

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
BASE = "https://technextmarketing.github.io/hst-medical-website/"
V = "20261007d"
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
COUNTERS = [("pain-relief", "Pain relief", "Balm, crème, patch, stick", "p03"), ("cough-cold-flu", "Cough and cold", "Lozenges, syrups, inhaler", "p27"),
            ("kids", "Kids", "Gummies and jelly sticks", "p23"), ("stress-sleep", "Sleep", "Melatonin and magnesium", "p43"),
            ("immunity-energy", "Tonics", "Ginseng, cordyceps, lingzhi", "p09"), ("", "All products", "51 products, 11 shelves", "p13")]
BENEFITS = ["Free Singapore delivery above S$30", "Made under GMP", "Halal-certified options", "Formulated by pharmacists and TCM physicians", "On the shelf at Guardian, Watsons and NHGP", "Part of Kowa Pharmaceutical Asia since 2026"]
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
    "rheuma-salve-liniment": "Sudden headache, giddiness or motion sickness; blocked nose",
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
       "logo": BASE + "assets/img/logo-hst-kowa.png", "parentOrganization": {"@type": "Organization", "name": "Kowa Pharmaceutical Asia Pte. Ltd.", "parentOrganization": {"@type": "Organization", "name": "Kowa Company, Ltd."}},
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
def page(out_rel, title, desc, body, active="", extra_head="", og_image=None, root=None, body_class=""):
    depth = out_rel.count("/")
    root = ("../" * depth) if root is None else root
    canonical = BASE + (out_rel[:-len("index.html")] if out_rel.endswith("index.html") else out_rel)
    robots = '<meta name="robots" content="noindex,nofollow">\n' if PROTOTYPE else ""
    head = read("head.html").replace("{{TITLE}}", esc(title)).replace("{{DESC}}", esc(desc)).replace("{{ROOT}}", root) \
        .replace("{{CANONICAL}}", canonical).replace("{{ROBOTS}}", robots).replace("{{V}}", V).replace("{{OG}}", og_image or BASE + "assets/img/og-cover.png") \
        .replace("{{EXTRA}}", extra_head).replace("{{BODYCLASS}}", body_class)
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


# ---------------------------------------------------------------- home: assurance band, bento, story, map
AIC = {
    "truck": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h11v10H3zM14 9h4l3 3v4h-7"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/></svg>',
    "shield": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6z"/><path d="m9 12 2 2 4-4"/></svg>',
    "flask": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 3h6M10 3v6L5 18a2 2 0 0 0 1.8 3h10.4A2 2 0 0 0 19 18l-5-9V3"/><path d="M7.5 14h9"/></svg>',
    "leaf": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19C5 10 10 5 20 4c0 10-5 15-14 15z"/><path d="M5 19c3-4 6-7 10-9"/></svg>',
    "store": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h16l-1.5-5h-13zM5 9v11h14V9"/><path d="M10 20v-6h4v6"/></svg>',
    "kowa": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M8 12h8M12 8v8"/></svg>',
}
ASSURE = [("truck", "Free delivery over S$30", "S$1.99 below that"), ("shield", "100% genuine", "Direct from HST Medical"),
          ("flask", "Made under GMP", "Pharmacist-formulated"), ("leaf", "Halal options", "Marked on each pack"),
          ("store", "On the shelf", "Guardian, Watsons, NHGP"), ("kowa", "Part of Kowa", "Kowa Pharmaceutical Asia")]
BENTO_IMG = {"pain-relief": "p03", "cough-cold-flu": "p27", "kids": "p23", "stress-sleep": "p43", "immunity-energy": "p09", "beauty-wellness": "p13"}
TIMELINE = [("1930", "Heng Say Tong medical hall opens"), ("1994", "HST Medical Pte Ltd is incorporated"),
            ("2024", "Beauty Insider and Guardian awards"), ("2026", "Joins Kowa Pharmaceutical Asia (29 May)")]
MAP_Q = "HST+Medical+Pte+Ltd,+152+Paya+Lebar+Road,+Citipoint+Industrial+Complex,+Singapore+409020"


def map_embed(title):
    return ('<figure class="map"><iframe title="%s" src="https://maps.google.com/maps?q=%s&amp;z=16&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>'
            '<figcaption><a href="https://www.google.com/maps/search/?api=1&amp;query=%s" target="_blank" rel="noopener">Open in Google Maps</a></figcaption></figure>') % (esc(title), MAP_Q, MAP_Q)


def live_manifest():
    path = os.path.join(OUT, "assets", "img", "live", "manifest.json")
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return []


AWARD_TEXT = {  # the award artwork's own wording
    "award-beauty-insider-2024-shou-wu.webp": "Beauty Insider Health & Wellness Awards 2024: HST Medical Shou Wu Hair Plus, Best Hair Supplements (Beauty Insiders' Choice)",
    "award-beauty-insider-2024-sleep-aid.webp": "Beauty Insider Health & Wellness Awards 2024: HST Medical Sleep Aid, Best Wellness Supplement (Readers' Choice)",
    "award-guardian-2024.webp": "The Guardian Awards 2024: winner",
}


def story_awards(root):
    aw = [m for m in live_manifest() if m.get("kind") == "award"][:3]
    if not aw:
        return ""
    order = [1, 0, 2] if len(aw) == 3 else list(range(len(aw)))
    cards = ""
    for slot, k in enumerate(order):
        m = aw[k]
        t = AWARD_TEXT.get(m["file"], m.get("alt") or "Award")
        cards += '<figure class="award a%d"><img src="%sassets/img/live/%s" alt="%s" width="%s" height="%s" loading="lazy" decoding="async"><figcaption>%s</figcaption></figure>' % (
            slot, root, m["file"], esc(t), m.get("width", 600), m.get("height", 600), esc(t))
    return '<div class="awards" aria-label="Awards">%s</div><p class="small award-note">Award artwork as published on hstmedical.com.</p>' % cards




def story_journey(root):
    """Milestones (home story + about heritage): items for an <ol class="tline">. Text only, styled in components.css."""
    steps = [
        ("1930", "The medical hall", "Heng Say Tong, the family medical hall behind the HST name, opens."),
        ("1994", "HST Medical is incorporated", "Pharmacists and TCM physicians begin formulating for Singapore's pharmacies."),
        ("2024", "Award-winning", "Beauty Insider Health & Wellness Awards and The Guardian Awards."),
        ("2026", "Part of Kowa", "Joins Kowa Pharmaceutical Asia on 29 May, within the Japanese Kowa group."),
    ]
    return "".join(f"""<li class="tl"><span class="tl-dot" aria-hidden="true"></span><b class="tl-year"><time datetime="{y}">{y}</time></b><h3>{esc(t)}</h3><p>{esc(x)}</p></li>""" for y, t, x in steps)


FLIPBOOK = "https://technextmarketing.github.io/hst-medical-catalogue/#p=1"


FLIPBOOK_BASE = FLIPBOOK.split("#")[0]


def catalogue_section(root):
    """Home, closing block of "Shop by range": the product catalogue as the store's table of contents. The book wears
    thumb-index tabs for its 11 real chapters; each tab runs into a contents row (chapter, dotted leader, page). Hover or
    focus turns the book to that chapter's first sheet (hero.js); every row opens the flipbook at that page in a new tab.
    Page images: assets/img/catalogue/pNNN(-640).webp, copied from the flipbook repo; chapters from _src/catalogue_index.json."""
    idx = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalogue_index.json"), encoding="utf-8"))
    img = lambda n, big=True: "%sassets/img/catalogue/p%03d%s.webp" % (root, n, "-640" if big else "")
    rows = "".join(
        f"""<li><a href="{FLIPBOOK_BASE}#p={c['page']}" target="_blank" rel="noopener" data-page="{c['page']}" data-img="{img(c['page'])}" style="--i:{n}"><span class="cbk-tab" aria-hidden="true">{c['no']}</span><span class="cbk-name">{esc(c['title'])}</span><span class="cbk-dots" aria-hidden="true"></span><span class="cbk-pg"><span class="sr-only">page </span>{c['page']}</span><span class="sr-only"> (opens the catalogue in a new tab)</span></a></li>"""
        for n, c in enumerate(idx["chapters"]))
    strip = "".join(
        f"""<li><a href="{FLIPBOOK_BASE}#p={c['page']}" target="_blank" rel="noopener"><img src="{img(c['page'], False)}" alt="" width="339" height="480" loading="lazy" decoding="async"><span><b>{esc(c['title'])}</b><small>Page {c['page']}</small></span></a></li>"""
        for c in idx["chapters"])
    return f"""<div class="cbk" data-cbk aria-labelledby="h-cat">
      <div class="cbk-copy">
        <h3 id="h-cat">Every range, page by page</h3>
        <p>The product catalogue has a sheet for each of the 51 products: what it is for, how to use it, ingredients, cautions and item codes. Every sheet links back to its page in this store.</p>
        <p class="cbk-meta"><span>{idx['pageCount']} pages</span><span>{len(idx['chapters'])} chapters</span><span>51 product sheets</span></p>
        <a class="btn btn-stamp" href="{FLIPBOOK}" target="_blank" rel="noopener">Open the catalogue {IC['arrow']}<span class="sr-only"> (opens in a new tab)</span></a>
      </div>
      <div class="cbk-index">
        <a class="cbk-vol" href="{FLIPBOOK}" target="_blank" rel="noopener" aria-label="Open the HST Medical product catalogue (opens in a new tab)">
          <span class="cbk-edge" aria-hidden="true"></span>
          <img class="cbk-page" src="{img(1)}" alt="" width="640" height="905" loading="lazy" decoding="async">
        </a>
        <ol class="cbk-toc" aria-label="Catalogue chapters">{rows}</ol>
      </div>
      <ul class="cbk-strip" aria-label="Catalogue chapters">{strip}</ul>
    </div>"""


def kowa_band(root):
    k = {m["file"]: m for m in live_manifest() if m.get("kind") == "kowa"}
    m, sg = k.get("kowa-joined-banner.webp"), k.get("kowa-joined-signing.webp")
    if not m:
        return ""
    inset = ('<img class="kowa-inset" src="%sassets/img/live/%s" alt="%s" width="%s" height="%s" loading="lazy" decoding="async">'
             % (root, sg["file"], esc(sg.get("alt") or ""), sg.get("width", 1400), sg.get("height", 933))) if sg else ""
    facts = "".join('<li>%s<span>%s</span></li>' % (AIC[i], esc(t)) for i, t in [
        ("kowa", "Part of Kowa Pharmaceutical Asia Pte. Ltd. since 29 May 2026"),
        ("shield", "Within the Japanese Kowa group, the makers of Vantelin"),
        ("store", "Same brands, same pharmacists, same shelves")])
    return f"""<section class="band kowa-band" aria-labelledby="h-kowa">
  <div class="counter kowa-grid">
    <div class="kowa-media">
      <span class="kowa-shape" aria-hidden="true"></span>
      <figure class="kowa-photo"><img src="{root}assets/img/live/{m['file']}" alt="{esc(m.get('alt') or 'Management and staff from Kowa and HST Medical')}" width="{m.get('width', 1400)}" height="{m.get('height', 933)}" loading="lazy" decoding="async"></figure>
      {inset}
      <span class="kowa-badge"><b>29 May</b><small>2026</small></span>
    </div>
    <div class="kowa-copy">
      <h2 id="h-kowa">We have joined <em>Kowa Pharmaceutical Asia</em></h2>
      <p>HST Medical is now part of the Japanese Kowa group. Kowa's research depth joins a Singapore range built since 1994, and the brands on the shelf, and the pharmacists behind them, stay the same.</p>
      <ul class="kowa-facts">{facts}</ul>
      <a class="btn btn-stamp" href="{root}about/">Read our story {IC['arrow']}</a>
    </div>
  </div>
</section>"""


# ---------------------------------------------------------------- ABOUT (live hstmedical.com/about/ content + images)
def page_ctx(root):
    """Helpers handed to the page modules (_src/page_*.py), which own their markup."""
    return {"root": root, "esc": esc, "IC": IC, "money": money, "map_embed": map_embed, "live_manifest": live_manifest,
            "AWARD_TEXT": AWARD_TEXT, "TIMELINE": TIMELINE, "PRODUCTS": PRODUCTS, "CATS": CATS, "BY_SLUG": BY_SLUG,
            "cat_products": cat_products, "product_label": product_label, "add_btn": add_btn, "RETAILERS_TBC": RETAILERS_TBC, "story_journey": story_journey,
            "OUT": OUT, "V": V}


def build_where():
    root = "../"
    crumb, crumb_ld = crumbs(root, [("Where to buy", None)])
    page("where-to-buy/index.html", "Where to Buy HST Medical Products in Singapore — Guardian, Watsons, NHGP and Online",
         "Find Rheuma-Salve®, Heritage® and Zoo-Vite® at Guardian, Watsons and NHGP pharmacies, or order online with island-wide delivery.",
         page_where.render(page_ctx(root), crumb), active="where",
         extra_head=crumb_ld + '<link rel="stylesheet" href="../assets/css/where.css?v=%s">\n' % V, body_class="pg-where")
    add_sitemap(BASE + "where-to-buy/")


def build_about():
    root = "../"
    crumb, crumb_ld = crumbs(root, [("About HST Medical", None)])
    page("about/index.html", "About HST Medical — Higher, Stronger, Together | Since 1930 in Singapore",
         "HST Medical (博诚药业): Singapore's home of Rheuma-Salve® pain relief and Zoo-Vite® kids' vitamins, from the Heng Say Tong medical hall (1930), incorporated 1994, part of Kowa Pharmaceutical Asia since 29 May 2026.",
         page_about.render(page_ctx(root), crumb), active="about",
         extra_head=crumb_ld + '<link rel="stylesheet" href="../assets/css/about.css?v=%s">\n' % V, body_class="pg-about")
    add_sitemap(BASE + "about/")


# hero cut-out sizes (assets/img/hero/rs-*.webp, made by _src/hero_cutouts.py + hero_compose.py)
HERO_DIMS = {"balm": (459, 324), "creme": (496, 590), "liniment": (370, 758), "patch": (414, 502), "stick": (516, 554)}


# ---------------------------------------------------------------- HOME HERO v7: three cinematic scenes
# Product (the Rheuma-Salve line-up), Company (the 51-remedy "medicine cabinet") and People (formulators, pharmacists,
# Kowa). Scenes share one grid cell; hero.js runs the chapters (autoplay, holds, swipe, parallax, light sweep) and
# home.css owns the look. Every fact is already on the site (guides, story, about, where-to-buy data).
HX_PACKS = [  # turntable order (front first): slug, cut-out, label, display height (% of the stage at the front)
    ("rheuma-salve-balm", "balm", "Balm", 50), ("rheuma-salve-creme", "creme", "Crème", 64), ("rheuma-salve-liniment", "liniment", "Liniment", 70),
    ("rheuma-salve-pain-relief-patch-cool", "patch", "Patch", 62), ("rheuma-salve-medi-stick", "stick", "Medi-Stick", 60)]
HX_CHIPS = {  # the catalogue's active-ingredient lists (percentages only where the label prints them)
    "rheuma-salve-balm": [("Menthol", ""), ("Camphor", ""), ("Wintergreen", "")],
    "rheuma-salve-creme": [("Menthol", "13.8%"), ("Wintergreen", "12%"), ("Peppermint oil", "9.2%")],
    "rheuma-salve-liniment": [("Menthol", ""), ("Peppermint", ""), ("Wintergreen", "")],
    "rheuma-salve-pain-relief-patch-cool": [("Peppermint oil", "6%"), ("Menthol", "5.8%"), ("Centella asiatica", "3%")],
    "rheuma-salve-medi-stick": [("Wintergreen oil", "18%"), ("Menthol", "10%"), ("Eucalyptus", "8%")]}
CHEV_L = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="m14.5 6-6 6 6 6"/></svg>'
CHEV_R = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="m9.5 6 6 6-6 6"/></svg>'


HX_LEAF = '<svg class="hx-leaf hx-leaf-%s hx-par" style="--d:%dpx" viewBox="0 0 120 120" aria-hidden="true"><path d="M62 8C30 28 16 62 28 104c36-6 62-36 60-76-6-8-14-14-26-20z"/><path d="M28 104C42 76 56 50 78 22M44 76l-12-8M52 62l-14-6M62 48l-12-4M54 70l14 2M64 54l14 0"/></svg>'


def build_hero_cinema(root=""):
    words = lambda t, o=0, em=False: " ".join('<span class="w%s" style="--wi:%d"><span>%s</span></span>' % (" em" if em else "", o + k, esc(x)) for k, x in enumerate(t.split()))
    def title(l1, l2):
        n = len(l1.split())
        return '<span class="ln">%s</span><span class="ln">%s</span>' % (words(l1), words(l2, n, True))
    # scene 1: the Rheuma-Salve turntable (hero.js orbit engine; data in #hx-orbit-data)
    packs, odata = "", []
    for k, (slug, img, lab, hpct) in enumerate(HX_PACKS):
        p = BY_SLUG[slug]
        v = p["variants"][0]
        w, h = HERO_DIMS[img]
        size = p["size"].split(" (")[0]
        packs += (f'<a class="hx-pk{" is-front" if k == 0 else ""}" href="{root}products/{slug}/" data-k="{k}" style="--h:{hpct};--k:{k}" aria-label="{esc(p["name"])}, {esc(size)}, {esc(money(v["price"]))}">'
                  f'<span class="bob"><span class="tilt"><img src="{root}assets/img/hero/rs-{img}.webp" alt="" width="{w}" height="{h}" decoding="async"{" fetchpriority=\"high\"" if k == 0 else ""}>'
                  f'<i class="hx-sheen" aria-hidden="true" style="-webkit-mask-image:url({root}assets/img/hero/rs-{img}.webp);mask-image:url({root}assets/img/hero/rs-{img}.webp)"></i></span></span>'
                  f'<span class="hx-tag" aria-hidden="true"><b>{esc(lab)}</b><small>{esc(size)} · {esc(money(v["price"]))}</small></span></a>')
        odata.append({"label": lab, "name": p["name"], "meta": "%s · %s" % (size, money(v["price"])), "chips": ["%s%s" % (n, " " + q if q else "") for n, q in HX_CHIPS[slug]],
                      "add": {"id": slug, "name": p["name"], "price": v["price"], "variant": v["label"], "code": v["code"], "img": "assets/img/products/%s-thumb.webp" % p["image"], "url": "products/%s/" % slug}})
    p0 = BY_SLUG[HX_PACKS[0][0]]
    now = (f'<div class="hx-now"><button class="hx-spin" type="button" data-spin="-1" aria-label="Previous format">{CHEV_L}</button>'
           f'<span class="hx-now-t"><b data-now="label">{esc(HX_PACKS[0][2])}</b><small data-now="meta">{esc(odata[0]["meta"])}</small></span>'
           + add_btn(p0, root, cls="btn btn-sm hx-now-add", label="Add") +
           f'<button class="hx-spin" type="button" data-spin="1" aria-label="Next format">{CHEV_R}</button></div>')
    ingr = '<ul class="hx-ingr" aria-label="Key ingredients">%s</ul>' % "".join('<li style="--n:%d">%s</li>' % (n, esc(c)) for n, c in enumerate(odata[0]["chips"]))
    aroma = '<span class="hx-aroma" aria-hidden="true">%s</span>' % "".join('<i style="--n:%d"></i>' % n for n in range(7))
    orbit_json = json.dumps(odata, ensure_ascii=False).replace("</", "<\\/")
    # scene 2: the medicine cabinet (three rows of real packshots, each row doubled for a seamless pan)
    others = [p for p in PRODUCTS if not p["slug"].startswith("rheuma-salve")][:27]
    rows = ""
    for r in range(3):
        cells = "".join('<span class="hx-cell"><img data-src="%sassets/img/products/%s-thumb.webp" alt="" width="360" height="360" decoding="async"></span>' % (root, p["image"]) for p in others[r * 9:(r + 1) * 9])
        rows += '<div class="hx-row r%d"><div class="hx-track">%s%s</div></div>' % (r, cells, cells)
    L = {m["file"] for m in live_manifest()}
    medals = "".join('<img class="hx-medal m%d hx-par" style="--d:%dpx" data-src="%sassets/img/live/%s" alt="" width="200" height="200" decoding="async">' % (k, 18 + k * 8, root, f)
                     for k, f in enumerate(f for f in AWARD_TEXT if f in L))
    wd = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "where_data.json"), encoding="utf-8"))
    n_stores = sum(len(c.get("stores", [])) for c in wd["chains"])
    # scene 3: the people
    photo = "kowa-joined-signing.webp" if "kowa-joined-signing.webp" in L else ""
    roles = [("flask", "Pharmacists and TCM physicians formulate"), ("store", "Pharmacists dispense, at %d stores" % n_stores), ("kowa", "Part of the Kowa group since 2026")]
    role_html = "".join('<li class="hx-role r%d hx-par" style="--d:%dpx">%s<span>%s</span></li>' % (k, 14 + k * 10, AIC[i], esc(t)) for k, (i, t) in enumerate(roles))
    scenes = [
        ("Product", title("Deep relief,", "five ways."),
         "Rheuma-Salve® balm, crème, roll-on, patch and Medi-Stick: one formula, Singapore's pharmacy-shelf pain relief since 1994.",
         f'<a class="btn btn-light" href="{root}shop/pain-relief/">Shop Rheuma-Salve {IC["arrow"]}</a><a class="hx-link" href="#h-pain">Find my format {IC["arrow"]}</a>',
         f'<div class="hx-media m-product" data-orbit role="group" aria-roledescription="product turntable" aria-label="The five Rheuma-Salve formats. Drag, or use the arrows, to turn.">'
         f'<span class="hx-halo hx-par" style="--d:10px" aria-hidden="true"></span>{HX_LEAF % ("a", 14)}{HX_LEAF % ("b", 30)}<span class="hx-spot" aria-hidden="true"></span>'
         f'<span class="hx-floor" aria-hidden="true"></span>{aroma}<div class="hx-orbit">{packs}</div>{ingr}{now}'
         f'<script type="application/json" id="hx-orbit-data">{orbit_json}</script></div>'),
        ("Company", title("Singapore's medicine", "cabinet since 1994."),
         "51 remedies across %d ranges, from a 1930 medical hall to Guardian, Watsons and NHGP shelves today." % len(CAT_ORDER),
         f'<a class="btn btn-light" href="{root}shop/">Browse all 51 {IC["arrow"]}</a><a class="hx-link" href="{root}where-to-buy/">Where to buy {IC["arrow"]}</a>',
         f'<div class="hx-media m-company"><div class="hx-wall" aria-hidden="true">{rows}</div>'
         f'<p class="hx-stat hx-par" style="--d:22px"><b data-count="51">51</b><span>pharmacist-formulated remedies</span></p>'
         f'<ul class="hx-facts" aria-label="HST Medical in numbers"><li class="hx-par" style="--d:16px"><b>{len(CAT_ORDER)}</b> ranges</li><li class="hx-par" style="--d:28px"><b>{n_stores}</b> pharmacy stores</li><li class="hx-par" style="--d:20px"><b>1930</b> medical hall</li></ul>{medals}</div>'),
        ("People", title("The people behind", "every pack."),
         "Pharmacists and TCM physicians formulate every remedy. Since 29 May 2026, HST Medical is part of Kowa Pharmaceutical Asia.",
         f'<a class="btn btn-light" href="{root}about/">Our story {IC["arrow"]}</a><a class="hx-link" href="{root}contact/">Talk to our team {IC["arrow"]}</a>',
         f'<div class="hx-media m-people"><figure class="hx-photo hx-par" style="--d:12px">'
         + (f'<img data-src="{root}assets/img/live/{photo}" alt="HST Medical co-founder Simone Tan and Kowa\'s Shigeru Kimura shake hands at the signing ceremony" width="1400" height="933" decoding="async">' if photo else "")
         + f'<figcaption>Joining Kowa Pharmaceutical Asia, 29 May 2026</figcaption></figure><ul class="hx-roles">{role_html}</ul></div>'),
    ]
    out, chaps = [], []
    for n, (name, ttl, sub, ctas, media) in enumerate(scenes):
        on = n == 0
        out.append(f"""<article class="hx-scene s{n}{' is-on' if on else ''}" id="hx-s{n}" data-i="{n}" role="tabpanel" aria-roledescription="slide" aria-label="{n + 1} of 3: {name}"{'' if on else ' aria-hidden="true" inert'}>
        <div class="hx-copy">
          <h2 class="hx-title">{ttl}</h2>
          <p class="hx-sub">{esc(sub)}</p>
          <div class="hx-ctas">{ctas}</div>
        </div>
        {media}
      </article>""")
        chaps.append(f'<button class="hx-ch{" on" if on else ""}" type="button" role="tab" aria-controls="hx-s{n}" aria-selected="{"true" if on else "false"}"{"" if on else " tabindex=\"-1\""} data-go="{n}"{" style=\"--dur:11s\"" if n == 0 else ""}><span class="hx-p" aria-hidden="true"></span><span class="hx-n">0{n + 1}</span><span class="hx-t">{name}</span></button>')
    grain = "<i class=\"hx-grain\" aria-hidden=\"true\"></i>"
    return f"""<section class="hero hx" data-hero data-scene="0" style="--dur:6.5s" aria-roledescription="carousel" aria-label="HST Medical highlights">
  <div class="hx-stage">
    <div class="hx-skies" aria-hidden="true"><i class="hx-sky k0"></i><i class="hx-sky k1"></i><i class="hx-sky k2"></i><i class="hx-rays"></i></div>
    <h1 id="h1" class="sr-only">HST Medical Singapore: Rheuma-Salve® pain relief and 51 pharmacist-formulated remedies since 1994</h1>
    <div class="hx-scenes">{''.join(out)}</div>
    <div class="hx-bar"><div class="hx-chapters" role="tablist" aria-label="Highlights">{''.join(chaps)}</div><button class="hx-pause" type="button" aria-pressed="false"><svg class="ic i-pause" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6v12M15 6v12"/></svg><svg class="ic i-play" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l10-6.5z"/></svg><span class="sr-only">Pause the highlights</span></button></div>
    <i class="hx-wipe" aria-hidden="true"></i>{grain}
    <svg class="hx-wave" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true"><path d="M0 90V52C220 16 470 4 760 30s540 48 680 10v50z"/></svg>
  </div>
  {{{{FOOT}}}}
</section>"""


# ---------------------------------------------------------------- matcher (replaces the compare tables)
NEEDS = {
    "rheuma-salve-balm": "Deep joint pain", "rheuma-salve-creme": "Everyday aches", "rheuma-salve-liniment": "Headache, giddiness",
    "rheuma-salve-pain-relief-patch-cool": "Back and shoulders", "rheuma-salve-medi-stick": "Aches on the go",
    "alievaid-herbal-drops": "Sore throat", "cough-alievaid-herbal-lintus": "Cough with phlegm", "flu-gard": "Fever and body aches",
    "ivy-leaf-cough-syrup": "Dry or chesty cough", "ivy-leaf-drops": "Cough on the go", "sinus-clear-2-in-1": "Blocked nose",
}


# hand-drawn need pictograms (24px grid, 1.6 stroke) for the matcher chips and card tags
NEED_IC = {
    "joint": '<path d="M9 3v6.5a3 3 0 0 0 1 2.2l.5.5a3 3 0 0 1 0 4.2L9 18v3"/><path d="M15 3v6.5a3 3 0 0 1-1 2.2l-.5.5a3 3 0 0 0 0 4.2L15 18v3"/><path d="M5 12.5c1.2-.8 2.4-.8 3.5 0M15.5 12.5c1.1-.8 2.3-.8 3.5 0"/>',
    "muscle": '<path d="M4 15c1-5 4-8 7-8 1.5 0 2 1 2 2s-1 1.5-2 1.5"/><path d="M11 10.5c3 0 6 1 7.5 4 .8 1.6-.3 3.5-2.2 3.5H6.5C5 18 4 16.8 4 15"/><path d="M9 13.5c1.5.6 3.2.6 4.8 0"/>',
    "head": '<path d="M7 19v-2.5A6.5 6.5 0 1 1 17.5 11l1.5 3h-2v3a2 2 0 0 1-2 2h-2"/><path d="M10 6.5l1.2 2.5 1.6-2 .9 2.6"/>',
    "back": '<path d="M12 3v18"/><path d="M9.5 6h5M9 10h6M9 14h6M9.5 18h5"/><path d="M5 8c-1 2-1 6 0 8M19 8c1 2 1 6 0 8"/>',
    "walk": '<circle cx="13" cy="4.5" r="1.8"/><path d="M11 9.5l-2 4.5 2.5 2 1 5M11 9.5l3.5-.5 2 3M11.5 16l-3 5M8.5 11l-2.5 1"/>',
    "throat": '<path d="M8 3c0 4 1 5 4 5s4-1 4-5"/><path d="M10 8v4c0 3-3 4-3 9M14 8v4c0 3 3 4 3 9"/><path d="M12 13.5v2.5"/>',
    "cough": '<path d="M6 15a4 4 0 0 1 1-7.9A5 5 0 0 1 16.5 8 3.5 3.5 0 0 1 17 15z"/><path d="M8 18.5h.01M12 19.5h.01M16 18.5h.01"/>',
    "fever": '<path d="M12 4a2 2 0 0 1 2 2v8.3a3.5 3.5 0 1 1-4 0V6a2 2 0 0 1 2-2z"/><path d="M12 10v6"/><path d="M17 6h2M17 9h2"/>',
    "lungs": '<path d="M12 4v7"/><path d="M12 11c-1 0-2 .5-2.5 1.5M12 11c1 0 2 .5 2.5 1.5"/><path d="M9.5 7C6 8 4 12 4 16.5c0 2 1.5 3.5 3.5 3.5 1.5 0 2.5-1 2.5-2.5V9"/><path d="M14.5 7C18 8 20 12 20 16.5c0 2-1.5 3.5-3.5 3.5-1.5 0-2.5-1-2.5-2.5V9"/>',
    "lozenge": '<rect x="4" y="8" width="16" height="9" rx="4.5"/><path d="M9 8v9M15 8v9"/><path d="M7 5l1 2M17 5l-1 2"/>',
    "nose": '<path d="M12 4c-1 4-4 7-4 10.5A2.5 2.5 0 0 0 10.5 17h3a2.5 2.5 0 0 0 2.5-2.5C16 11 13 8 12 4z"/><path d="M9.5 17c0 1.5-1 2.5-2.5 3M14.5 17c0 1.5 1 2.5 2.5 3"/>',
}
NEED_ICON_FOR = {"rheuma-salve-balm": "joint", "rheuma-salve-creme": "muscle", "rheuma-salve-liniment": "head", "rheuma-salve-pain-relief-patch-cool": "back",
                 "rheuma-salve-medi-stick": "walk", "alievaid-herbal-drops": "throat", "cough-alievaid-herbal-lintus": "cough", "flu-gard": "fever",
                 "ivy-leaf-cough-syrup": "lungs", "ivy-leaf-drops": "lozenge", "sinus-clear-2-in-1": "nose"}


def need_ic(slug, cls="nic"):
    k = NEED_ICON_FOR.get(slug)
    return '<svg class="%s" viewBox="0 0 24 24" aria-hidden="true">%s</svg>' % (cls, NEED_IC[k]) if k else ""


def matcher(cid, root, title):
    items = cat_products(cid)
    chips, cards = "", ""
    for p in items:
        need = NEEDS.get(p["slug"], CATS[cid]["name"])
        usage = (p["usage"][0] if p["usage"] else "Use as directed on the label").split(". ")[0].rstrip(".")
        usage = re.sub(r"^(How To Use|Caution|Storage):\s*", "", usage)
        chips += '<button type="button" class="need" aria-pressed="false" data-need="%s">%s<span>%s</span></button>' % (p["slug"], need_ic(p["slug"]), esc(need))
        cards += f"""<article class="mcard" data-card="{p['slug']}">
  <a class="mimg" href="{root}products/{p['slug']}/" tabindex="-1" aria-hidden="true"><img src="{root}assets/img/products/{p['image']}-thumb.webp" alt="" width="360" height="360" loading="lazy" decoding="async"></a>
  <div class="mbody"><span class="mneed">{need_ic(p['slug'], 'nic nic-sm')}{esc(need)}</span>
  <h3><a href="{root}products/{p['slug']}/">{esc(p['name'])}</a></h3><p class="msize">{esc(p['size'])}</p>
  <p class="mfor">{esc(p['for'])}</p>
  <p class="muse"><b>How to use</b> {esc(usage)}</p></div>
  <div class="mfoot"><span class="price">{esc(money(p['price']))}<small>incl. GST</small></span>{add_btn(p, root, cls="btn btn-sm btn-card")}</div>
</article>"""
    return f"""<div class="matcher" data-matcher><div class="needs" role="group" aria-label="{esc(title)}"><span class="needs-l">What's bothering you?</span>{chips}<button type="button" class="need need-all" data-need="" hidden>Show all</button></div><div class="mcards">{cards}</div></div>"""


# ---------------------------------------------------------------- HOME
def build_home():
    root = ""
    counters = "".join(f"""<a href="shop/{cid + '/' if cid else ''}"><span class="tile"><img src="assets/img/products/{img}-thumb.webp" alt="" width="200" height="200" loading="lazy" decoding="async"></span><span>{esc(name)}</span><small>{esc(sub)}</small>{'<span class="stamp">Start here</span>' if i == 0 else ''}</a>""" for i, (cid, name, sub, img) in enumerate(COUNTERS))
    assure = "".join(f"""<li><span class="ai">{AIC[k]}</span><span><b>{esc(t)}</b><small>{esc(x)}</small></span></li>""" for k, t, x in ASSURE)
    best = [BY_SLUG[s] for s in ["rheuma-salve-balm", "alievaid-herbal-drops", "deep-sea-squalene", "pearl-powder", "crocodile-pure-skin-oil", "zoo-vite-multivitamin-gummies", "flu-gard", "melatonin-5mg"]]
    best_cards = "\n".join(product_label(p, root) for p in best)
    brands_row = "".join(f"<li>{b}</li>" for b in ["Rheuma-Salve®", "Heritage®", "HST Medical®", "Zoo-Vite®", "Kowa"])
    bento = "".join(f"""<a class="b-{i}" href="shop/{cid}/"><span class="bt"><b>{esc(CATS[cid]['name'])}</b>{'<span class="bb">%s</span>' % esc(CATS[cid]['blurb']) if i == 0 else ''}<small>{len(cat_products(cid))} products</small></span><span class="bimg"><img src="assets/img/products/{BENTO_IMG.get(cid, cat_products(cid)[0]['image'])}-thumb.webp" alt="" width="360" height="360" loading="lazy" decoding="async"></span><span class="bgo">{IC['arrow']}</span></a>""" for i, cid in enumerate(CAT_ORDER))
    fan = "".join('<img src="assets/img/products/%s-thumb.webp" alt="" width="360" height="360" loading="lazy" decoding="async" style="--f:%d">' % (i, k) for k, i in enumerate(("p23", "p13", "p03", "p27", "p43")))
    bento += f"""<a class="b-all" href="shop/"><span class="bt"><b><span class="ball-n">51</span> products, one store</b><small>Every shelf from balms to gummies. Browse them all</small></span><span class="ball-fan" aria-hidden="true">{fan}</span><span class="bgo">{IC['arrow']}</span></a>"""
    timeline = "".join(f"""<li><b>{y}</b><span>{esc(t)}</span></li>""" for y, t in TIMELINE)
    ctx = {"root": root, "PRODUCTS": PRODUCTS, "CATS": CATS, "BY_SLUG": BY_SLUG, "POSTS": POSTS, "IC": IC, "esc": esc, "money": money,
           "cat_products": cat_products, "brand_label": brand_label}
    journey = story_journey(root)
    proofs = "".join(f"""<li>{AIC[k]}<span>{esc(t)}</span></li>""" for k, t in [("flask", "Formulated by pharmacists and TCM physicians"), ("shield", "Made under GMP, ingredients tested for authenticity"), ("leaf", "Halal-certified and vegan options across the range")])
    notes = "".join(f"""<a href="blog/{s}/"><time datetime="{d}">{d}</time><span><b>{esc(t)}</b>{esc(x)}</span></a>""" for s, t, d, x, _ in POSTS)
    body = f"""
<main id="main">
{build_hero_cinema(root).replace("{{FOOT}}", '<div class="hero-foot"><nav class="counters" aria-label="Shop by need">' + counters + '</nav></div>')}
<section class="assure" aria-label="Why shop with HST Medical"><ul class="counter">{assure}</ul></section>

<section class="band" aria-labelledby="h-best">
  <div class="counter">
    <div class="band-head"><div><h2 id="h-best">Best sellers</h2><p>What Singapore buys most, with the real price for the real pack.</p></div><a class="btn btn-quiet" href="shop/">All 51 products {IC['arrow']}</a></div>
    <div class="labels">{best_cards}</div>
  </div>
</section>

<section class="band match-band" aria-labelledby="h-pain">
  <div class="counter">
    <div class="band-head"><div><h2 id="h-pain">Which pain relief do I need?</h2><p>{esc(GUIDES['pain-relief']['intro'])}</p></div><a class="btn btn-quiet" href="shop/pain-relief/">All pain relief {IC['arrow']}</a></div>
    {matcher('pain-relief', root, 'Match the pain')}
  </div>
</section>

<section class="band match-band" aria-labelledby="h-cough">
  <div class="counter">
    <div class="band-head"><div><h2 id="h-cough">Cough, cold or flu: match the symptom</h2><p>{esc(GUIDES['cough-cold-flu']['intro'])}</p></div><a class="btn btn-quiet" href="shop/cough-cold-flu/">All cough and cold {IC['arrow']}</a></div>
    {matcher('cough-cold-flu', root, 'Match the symptom')}
  </div>
</section>

<section class="band" aria-labelledby="h-shelf">
  <div class="counter">
    <div class="band-head"><div><h2 id="h-shelf">Shop by range</h2><p>Eleven ranges, one standard: developed by HST Medical's own pharmacists and TCM physicians, then tested for authenticity and safety before they reach the counter.</p></div></div>
    <nav class="bento" aria-label="Ranges">{bento}</nav>
    {catalogue_section(root)}
  </div>
</section>

{home_sections.marquee(ctx)}

<section class="band story" aria-labelledby="h-trust">
  <div class="counter">
    <div class="story-head">
      <h2 id="h-trust">Dispensed by pharmacists since 1994</h2>
      <p class="lead">From a Singapore medical hall to a Kowa company: nearly a century of formulating remedies people keep in the cabinet.</p>
    </div>
    <ol class="tline">{journey}</ol>
    <div class="story-foot">
      <ul class="proofs">{proofs}</ul>
      <div class="story-ctas"><a class="btn btn-stamp" href="about/">Our story {IC['arrow']}</a><a class="btn btn-quiet" href="where-to-buy/">Where to buy {IC['arrow']}</a></div>
    </div>
  </div>
</section>

{kowa_band(root)}

<section class="band visit" aria-labelledby="h-visit">
  <div class="counter visit-grid">
    <div class="visit-copy">
      <h2 id="h-visit">Where to buy</h2>
      <p>On the shelf at Singapore's pharmacy chains, or delivered from this store: free above S$30.</p>
      <ul class="where">{''.join('<li>%s</li>' % esc(r) for r in RETAILERS_CONFIRMED)}</ul>
      <div class="trade-card"><div><h3>Pharmacies, clinics and distributors</h3><p>Open a trade account, download the product sheets and order through your HST Medical territory manager.</p></div><a class="btn btn-quiet" href="resellers/">Trade enquiries {IC['arrow']}</a></div>
      <address class="hq"><b>HST Medical Pte Ltd</b>152 Paya Lebar Road #02-06, Citipoint Industrial Complex, Singapore 409020<a href="tel:+6565365108">+65 6536 5108 ext 816</a></address>
    </div>
    {map_embed('HST Medical head office, 152 Paya Lebar Road, Singapore')}
  </div>
</section>

{home_sections.brands(ctx)}

{home_sections.notes(ctx)}
</main>"""
    ld = jsonld({"@context": "https://schema.org", "@graph": [ORG, {"@type": "WebSite", "url": BASE, "name": "HST Medical", "publisher": {"@id": BASE + "#org"},
                 "potentialAction": {"@type": "SearchAction", "target": BASE + "shop/?q={search_term_string}", "query-input": "required name=search_term_string"}}]})
    page("index.html", "HST Medical Singapore — Rheuma-Salve® Pain Relief, Cough & Cold Remedies, Heritage® Tonics",
         "Pain, cough or cold? Start at the HST Medical counter: Rheuma-Salve®, Alievaid, Flu Gard and 51 pharmacist-formulated products from a Singapore company founded in 1994, now part of Kowa Pharmaceutical Asia. GMP, Halal options.",
         body, extra_head=ld + '<link rel="preload" as="image" href="assets/img/hero/rs-balm.webp" fetchpriority="high">\n<link rel="stylesheet" href="assets/css/home.css?v=%s">\n<script src="assets/js/hero.js?v=%s" defer></script>\n' % (V, V), body_class="home")
    add_sitemap(BASE, "1.0")

# ---------------------------------------------------------------- SHOP + CATEGORIES
def filters_html(root, active=None):
    """Range filter: one grid of tiles (transparent packshot, name, count); a swipeable rail on phones.
    Each tile is a real link to the range page; on /shop/ site.js turns them into in-page filters."""
    def tile(cid, name, count, img_html):
        on = (cid == active) or (cid == "all" and active is None)
        href = "%sshop/%s" % (root, "" if cid == "all" else cid + "/")
        return f'<a class="cat" role="button" aria-pressed="{"true" if on else "false"}" href="{href}" data-cat="{cid}"><span class="ct">{img_html}</span><span class="cn">{esc(name)}</span><span class="cc">{count}</span></a>'
    stack = "".join('<img src="%sassets/img/products/%s-thumb.webp" alt="" width="360" height="360" loading="lazy" decoding="async">' % (root, i) for i in ("p27", "p03", "p23"))
    tiles = tile("all", "All products", len(PRODUCTS), '<span class="stack">%s</span>' % stack)
    for cid in CAT_ORDER:
        im = BENTO_IMG.get(cid, cat_products(cid)[0]["image"])
        tiles += tile(cid, CATS[cid]["name"], len(cat_products(cid)), '<img src="%sassets/img/products/%s-thumb.webp" alt="" width="360" height="360" loading="lazy" decoding="async">' % (root, im))
    return '<nav class="filters" aria-label="Filter by range">%s</nav>' % tiles

def build_shop():
    root = "../"
    crumb, crumb_ld = crumbs(root, [("All products", None)])
    cards = "\n".join(product_label(p, root) for cid in CAT_ORDER for p in cat_products(cid))
    body = f"""
<main id="main"><div class="counter">{crumb}
<header class="page-head"><h1>All products</h1><p class="lead">{len(PRODUCTS)} products across {len(CAT_ORDER)} shelves. Prices in Singapore dollars including GST. Free Singapore delivery on orders above S$30; S$1.99 for orders of S$30 and below.</p></header>
<form class="search" role="search" action="" onsubmit="return false"><label class="sr-only" for="q">Search products</label><input id="q" type="search" name="q" placeholder="Search products: balm, ginseng…" autocomplete="off"><button class="btn" type="submit" aria-label="Search">{IC['search']}</button></form>
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
            guide = f"""<section aria-labelledby="h-guide" style="margin-bottom:2.5rem"><h2 id="h-guide" style="margin-bottom:.5rem">Which one do I need?</h2><p style="margin-bottom:1rem">{esc(g['intro'])}</p>{matcher(cid, root, 'Match the need')}</section>"""
            faqs = "".join(f"<details class='acc'><summary>{esc(q)}{IC['plus']}</summary><div class='body'><p>{esc(a)}</p></div></details>" for q, a in g["faq"])
            faq = f"""<section class="band faq" aria-labelledby="h-faq"><div class="counter faq-grid">
  <div class="faq-intro">
    <svg class="faq-art" viewBox="0 0 64 64" aria-hidden="true"><path d="M10 14h36a6 6 0 0 1 6 6v18a6 6 0 0 1-6 6H28l-10 8v-8h-8a6 6 0 0 1-6-6V20a6 6 0 0 1 6-6z"/><path d="M28 22v14M21 29h14"/></svg>
    <h2 id="h-faq">Ask the pharmacist</h2>
    <p class="lead">Common questions at the {esc(c['name'].lower())} counter.</p>
    <p class="caution"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16.5v.5"/></svg><span>General guidance only. Always read the label and follow directions for use. See a pharmacist or doctor if symptoms persist.</span></p>
    <a class="btn btn-quiet" href="{root}contact/">Ask us a question {IC['arrow']}</a>
  </div>
  <div class="faq-list">{faqs}</div>
</div></section>"""
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
        steps = "".join("<li><span>%d</span><p>%s</p></li>" % (k + 1, esc(u)) for k, u in enumerate(p["usage"])) or "<li><span>1</span><p>Use as directed on the label.</p></li>"
        ingr_items = "".join("<li>%s</li>" % esc(u) for u in p["ingredients"]) or "<li>See pack for the full ingredient list.</li>"
        use1 = (p["usage"][0] if p["usage"] else "As directed on the label").split(". ")[0].rstrip(".")
        facts = "".join(f"""<li>{ic}<span><b>{esc(k)}</b>{esc(v)}</span></li>""" for ic, k, v in [
            (need_ic(p["slug"], "ic") or AIC["leaf"], "For", p["for"]), (AIC["flask"], "How to use", use1), (AIC["store"], "Origin", (p["country"] or "See pack") + halal)])
        caution = 'External use only. Not for broken skin; ask a pharmacist before use in pregnancy or for young children.' if p['category'] in ('pain-relief', 'traditional-pain-relief') else 'A health supplement or herbal remedy, not a substitute for medical care. Ask a pharmacist if symptoms persist.'
        partners = "".join('<li><img src="%sassets/img/partners/%s.webp" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"></li>' % (root, f, n, w_, h_) for f, n, w_, h_ in (("guardian", "Guardian", 875, 226), ("nhg-polyclinics", "NHG Polyclinics", 834, 240))) + "".join("<li class=\"pt\">%s</li>" % n for n in ("Watsons", "Essentials Pharmacy"))
        body = f"""
<main id="main"><div class="counter">{crumb}
<article class="pdp2 {brand_class(p['brand'])}" data-pdp>
  <div class="pdp2-media">
    <figure class="pdp-pack"><span class="pdp-halo" aria-hidden="true"></span><span class="zoomer"><img src="{root}assets/img/products/{p['image']}.webp" alt="{esc(p['name'])}, {esc(p['size'])}" width="900" height="900" fetchpriority="high" decoding="async"><span class="zoom-hint" aria-hidden="true"><span class="h-hover">Click to zoom</span><span class="h-tap">Tap to zoom</span></span></span></figure>
  </div>
  <div class="pdp2-main">
    <p class="pdp-meta"><span class="pdp-brand">{esc(brand_label(p['brand']))}</span><a href="{root}shop/{p['category']}/">{esc(c['name'])}</a><span class="print" data-code-out>Item {v0['code'] or '—'}</span></p>
    <h1>{esc(p['name'])}</h1>
    <p class="pdp-tag">{esc(p['tagline'])}</p>
    <ul class="pdp-facts">{facts}</ul>
    <div class="price-line print"><span class="price" data-price-out>{esc(money(v0['price']))}</span><span class="meta">{AIC['truck']}incl. GST · free Singapore delivery above S$30</span></div>
    <fieldset class="pdp-packs"><legend>Pack size <span class="print" data-size-out>{esc(v0['label'])}</span></legend><div class="packs">{packs}</div>{other}</fieldset>
    <div class="buy">
      <div class="qty" aria-label="Quantity"><button type="button" data-step="-1" aria-label="Decrease quantity">−</button><input id="qty" type="number" min="1" max="99" value="1" inputmode="numeric" aria-label="Quantity"><button type="button" data-step="1" aria-label="Increase quantity">+</button></div>
      {add_btn(p, root, cls='btn btn-stamp pdp-add', from_pdp=True)}
      <a class="btn btn-quiet" href="{root}where-to-buy/" data-enquire{' hidden' if v0['price'] else ''}>Ask in store</a>
    </div>
    <ul class="pdp-benefits">{benefits}</ul>
  </div>
</article>
</div>
<div class="buybar" data-buybar hidden><img src="{root}assets/img/products/{p['image']}-thumb.webp" alt="" width="360" height="360" loading="lazy" decoding="async"><span class="bb-t"><b>{esc(p['name'])}</b><small data-price-out>{esc(money(v0['price']))}</small></span><button class="btn btn-stamp" type="button" data-buybar-add{' hidden' if not v0['price'] else ''}>{IC['bag']} Add</button></div>
<section class="band pdp-info" aria-label="Product information">
  <div class="counter">
    <div class="pdp-cards">
      <article class="pdp-card"><svg class="pc-ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/></svg><h2>What it is</h2><p>{esc(p['description'])}</p></article>
      <article class="pdp-card"><svg class="pc-ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4h6l-1 4h-4z"/><path d="M8 8h8l1 12H7z"/><path d="M10 13h4"/></svg><h2>How to use</h2><ol class="pdp-steps">{steps}</ol></article>
      <article class="pdp-card"><svg class="pc-ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19C5 10 10 5 20 4c0 10-5 15-14 15z"/><path d="M5 19c3-4 6-7 10-9"/></svg><h2>Active ingredients</h2><ul class="pdp-ingr">{ingr_items}</ul></article>
    </div>
    <p class="caution pdp-caution"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16.5v.5"/></svg><span>Always read the label and follow directions for use. {caution}</span></p>
    <div class="pdp-where"><div><h2>Also on the shelf at</h2><p>Singapore's pharmacy chains carry the core HST Medical® range.</p></div><ul>{partners}</ul><a class="btn btn-quiet" href="{root}where-to-buy/">Find a store {IC['arrow']}</a></div>
  </div>
</section>
<section class="band" aria-labelledby="h-rel"><div class="counter"><div class="band-head"><h2 id="h-rel">Also at the {esc(c['name'].lower())} counter</h2><a class="btn btn-quiet" href="{root}shop/{p['category']}/">The whole shelf {IC['arrow']}</a></div><div class="labels">{rel}</div></div></section>
</main>"""
        offers = [{"@type": "Offer", "name": v["label"], "priceCurrency": "SGD", "price": "%.2f" % v["price"], "availability": "https://schema.org/InStock", "sku": v["code"] or None, "url": BASE + "products/%s/" % p["slug"]} for v in p["variants"] if v["price"]]
        for o in offers:
            if o["sku"] is None: del o["sku"]
        ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "brand": {"@type": "Brand", "name": brand_label(p["brand"]).replace("®", "")},
              "image": BASE + "assets/img/products/%s-white.webp" % p["image"], "description": p["description"][:300], "category": c["name"],
              "manufacturer": {"@id": BASE + "#org"}, "url": BASE + "products/%s/" % p["slug"]}
        if offers:
            ld["offers"] = offers if len(offers) > 1 else offers[0]
        page("products/%s/index.html" % p["slug"], "%s (%s) — %s | HST Medical" % (p["name"], p["size"], brand_label(p["brand"])),
             ("%s. For %s. %s" % (p["tagline"], p["for"], p["description"]))[:158], body, active={"pain-relief": "pain", "cough-cold-flu": "cough"}.get(p["category"], "shop"),
             extra_head=crumb_ld + jsonld(ld), og_image=BASE + "assets/img/products/%s-white.webp" % p["image"])
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

def field(name, label, typ="text", req=False, err=None, **attrs):
    a = " ".join('%s="%s"' % (k.replace("_", "-"), esc(v)) for k, v in attrs.items())
    return f"""<label><span class="{'req' if req else ''}">{label}</span><input type="{typ}" name="{name}"{' required' if req else ''} {a}><span class="err">{err or (label + ' is needed.')}</span></label>"""

def build_static():
    build_about()

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
           "Four brands under one quality standard, part of Kowa Pharmaceutical Asia and the Japanese Kowa group behind Vantelin and Three Dimension Mask.",
           "Our brands", "Four brands, one standard, one parent: Kowa.",
           f"""<div class="labels" style="grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr))">{brand_rows}</div>
<div class="label" style="margin-top:var(--gutter)"><div class="label-body trade"><div><h2 style="font-size:1.4rem">Kowa: Japanese pharmaceutical heritage</h2><p style="margin-top:.5rem">Kowa Company, Ltd. (Nagoya, est. 1894) owns consumer brands such as Vantelin topical pain relief and Three Dimension Mask. HST Medical became part of Kowa Pharmaceutical Asia, the group's Singapore-based pharmaceutical arm, on 29 May 2026. Whether Kowa's Singapore range is listed here is still to be decided with the client.</p></div><a class="btn btn-quiet" href="../about/">Our story</a></div></div>""", active="about")

    build_where()

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
    <div class="lbl"><label class="check"><input type="checkbox" name="consent" required><span>I agree to be contacted about a trade account; my details are handled under the <a href="../privacy/">privacy policy</a>.</span></label><span class="err">Please tick the consent box so we can contact you.</span></div>
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
    <div><b>Customer service</b><p>Delivery, product and general questions.<br><a href="mailto:contact@hstmedical.com">contact@hstmedical.com</a><br>Orders: <a href="mailto:order@hstmedical.com">order@hstmedical.com</a></p></div>
    <div><b>Trade</b><p><a href="mailto:resellercontact@hstmedical.com">resellercontact@hstmedical.com</a><br>or your HST Medical territory manager.</p></div>
    <div><b>HST MEDICAL PTE LTD</b><p>Part of Kowa Pharmaceutical Asia · UEN 199405743E<br>152 Paya Lebar Road, #02-06 Citipoint Industrial Complex, Singapore 409020<br>Telephone <a href="tel:+6565365108">+65 6536 5108</a> ext. 816</p></div>
  </div></div>
  <form class="label form" style="grid-column:6 / span 7;padding:1.5rem" data-demo novalidate>
    <h2 style="font-size:1.3rem">Send a message</h2>
    <div class="row">{field('name', 'Name', req=True, autocomplete='name')}{field('email', 'Email', 'email', True, autocomplete='email')}</div>
    <label><span>Topic</span><select name="topic"><option>Order or delivery</option><option>Product question</option><option>Trade enquiry</option><option>Press</option><option>Other</option></select></label>
    <label><span class="req">Message</span><textarea name="message" required></textarea><span class="err">A message is needed.</span></label>
    <button class="btn btn-stamp" type="submit">Send {IC['arrow']}</button>
    <p class="ok">Thanks. We have your message and will reply within two working days.</p>
  </form>
</div>
<section class="visit-map" aria-label="Map">{map_embed("HST Medical Pte Ltd, 152 Paya Lebar Road, Singapore")}</section>""")

    trust = "".join('<li>%s<span>%s</span></li>' % (AIC[k], esc(t)) for k, t in [("shield", "Secure checkout, 100% genuine stock"), ("truck", "Free Singapore delivery above S$30"), ("store", "Also on the shelf at Guardian, Watsons and NHGP")])
    also = "\n".join(product_label(BY_SLUG[x], "../") for x in ["rheuma-salve-pain-relief-patch-cool", "alievaid-herbal-drops", "zoo-vite-multivitamin-gummies", "melatonin-5mg"])
    simple("cart/index.html", "Your bag — HST Medical", "Review your HST Medical order before checkout.", "Your bag", "",
           f"""
<div class="bag-grid">
  <section class="bag-list" aria-label="Items in your bag"><div class="lines" id="bag-lines" data-root="../"><div class="empty bag-empty"><svg class="ic bag-empty-ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5.5 8.5h13l-1 11.5h-11z"/><path d="M9 8.5V7a3 3 0 0 1 6 0v1.5"/></svg><b>Your bag is empty.</b><span>Start with what you need today.</span><span class="bag-empty-ctas"><a class="btn btn-stamp" href="../shop/pain-relief/">Pain relief</a><a class="btn btn-quiet" href="../shop/cough-cold-flu/">Cough and cold</a><a class="btn btn-quiet" href="../shop/">All products</a></span></div></div></section>
  <aside class="summary" aria-labelledby="h-sum">
    <h2 id="h-sum">Order summary</h2>
    <dl class="fields"><div class="field"><dt>Subtotal</dt><dd data-sub>S$0.00</dd></div><div class="field"><dt>Delivery</dt><dd data-ship>—</dd></div><div class="field total"><dt>Total <small>incl. GST</small></dt><dd data-total>S$0.00</dd></div></dl>
    <div class="meter" aria-hidden="true"><i></i></div><p class="small" data-free>Free Singapore delivery above S$30; S$1.99 for orders of S$30 and below.</p>
    <div class="sum-ctas"><a class="btn btn-stamp btn-block" href="../checkout/" data-needs-items aria-disabled="true">Checkout {IC['arrow']}</a><a class="btn btn-quiet btn-block" href="../shop/">Keep shopping</a></div>
    <ul class="sum-trust">{trust}</ul>
    <p class="note small">Prototype bag stored in your browser only. Production uses WP EasyCart's cart with this layout applied through CSS overrides.</p>
  </aside>
</div>
<section class="band bag-also" aria-labelledby="h-also">
  <div class="band-head"><div><h2 id="h-also">You might also need</h2><p>Popular with people who buy pain relief.</p></div><a class="btn btn-quiet" href="../shop/">All 51 products {IC['arrow']}</a></div>
  <div class="labels">{also}</div>
</section>""", active="")

    simple("checkout/index.html", "Checkout — HST Medical", "Secure checkout for HST Medical orders.", "Checkout", "",
           f"""
<div class="bag-grid">
  <form class="label form" style="padding:1.5rem" data-demo novalidate>
    <ol class="steps-bar" aria-label="Checkout steps"><li aria-current="step">1 · Contact</li><li>2 · Delivery</li><li>3 · Payment</li></ol>
    <section class="step"><h2>Who is this order for?</h2>
      <div class="row">{field('email', 'Email', 'email', True, autocomplete='email', inputmode='email')}{field('mobile', 'Mobile', 'tel', True, autocomplete='tel', inputmode='tel')}</div>
      <p class="note">We use these for the order confirmation and delivery updates only.</p>
      <div class="step-nav"><span></span><button class="btn btn-stamp" type="button" data-next>Continue to delivery {IC['arrow']}</button></div></section>
    <section class="step" hidden><h2>Where should we deliver?</h2>
      <div class="row">{field('first', 'First name', req=True, autocomplete='given-name')}{field('last', 'Last name', req=True, autocomplete='family-name')}</div>
      {field('address', 'Address', req=True, autocomplete='street-address')}
      <div class="row">{field('unit', 'Unit', autocomplete='address-line2')}{field('postal', 'Postal code', req=True, err='Enter the 6-digit postal code.', inputmode='numeric', autocomplete='postal-code', pattern='[0-9]{6}')}<label><span>Country</span><select name="country" autocomplete="country-name"><option>Singapore</option><option>Malaysia</option><option>Other</option></select></label></div>
      <div class="lbl"><span>Delivery method</span><label class="check"><input type="radio" name="ship" checked><span>Courier, 2 to 3 working days (free above S$30, otherwise S$1.99)</span></label><label class="check"><input type="radio" name="ship"><span>Self-collection, by appointment</span></label></div>
      <div class="step-nav"><button class="btn btn-quiet" type="button" data-prev>Back</button><button class="btn btn-stamp" type="button" data-next>Continue to payment {IC['arrow']}</button></div></section>
    <section class="step" hidden><h2>How would you like to pay?</h2>
      <div class="lbl"><span>Payment</span><label class="check"><input type="radio" name="pay" checked><span>Card (Visa, Mastercard, Amex)</span></label><label class="check"><input type="radio" name="pay"><span>PayNow</span></label><label class="check"><input type="radio" name="pay"><span>GrabPay, Apple Pay, Google Pay</span></label></div>
      <div class="lbl"><label class="check"><input type="checkbox" name="terms" required><span class="req">I accept the terms of sale and the <a href="../privacy/">privacy policy</a></span></label><span class="err">Please tick the box to accept the terms before placing the order.</span></div>
      <div class="step-nav"><button class="btn btn-quiet" type="button" data-prev>Back</button><button class="btn btn-stamp" type="submit" data-needs-items>Place order {IC['arrow']}</button></div>
      <div class="assure"><div><b>Secure payment</b>Card details are handled by the payment gateway, never stored here.</div><div><b>Delivery 2 to 3 working days</b>Island-wide courier; tracking by email.</div><div><b>Questions?</b><a href="../contact/">Contact us</a> before or after your order.</div></div>
      <p class="caution">Always read the label and follow directions for use.</p></section>
    <p class="note">Prototype: nothing is charged. Production checkout is WP EasyCart with the configured gateway; this layout is applied via CSS overrides on EasyCart's checkout wrapper.</p>
    <p class="ok">Order placed (demo). A confirmation email would follow with your order number.</p>
  </form>
  <aside class="label summary" aria-labelledby="h-sum"><div class="label-body"><h2 id="h-sum" style="font-size:1.3rem;margin-bottom:.75rem">Your bag</h2>
    <div id="bag-lines" data-root="../"></div>
    <dl class="fields" style="margin-top:.5rem"><div class="field"><dt>Subtotal</dt><dd data-sub>S$0.00</dd></div><div class="field"><dt>Delivery</dt><dd data-ship>—</dd></div><div class="field total"><dt>Total</dt><dd data-total>S$0.00</dd></div></dl>
    <p class="small" data-free>Free Singapore delivery above S$30; S$1.99 for orders of S$30 and below.</p>
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
    L = ["# HST Medical", "", "> HST Medical Pte Ltd (Singapore, incorporated 1994, rooted in the Heng Say Tong medical hall founded 1930; part of Kowa Pharmaceutical Asia since 29 May 2026) formulates and supplies health supplements and pain-relief remedies under the HST Medical®, Heritage®, Rheuma-Salve® and Zoo-Vite® brands. Products are GMP-manufactured, some Halal-certified, sold at Guardian, Watsons and NHGP pharmacies and shipped from this store in SGD.", "", "## Ranges"]
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
    chat_kb.build(OUT, BASE, FLIPBOOK, PRODUCTS, CATS, CAT_ORDER, GUIDES, NEEDS, NEED_ICON_FOR, POSTS, ASSURE, ORG, TIMELINE, AWARD_TEXT, brand_label, money)  # Ask HST knowledge base -> assets/data/chat-kb.json
    print("built %d sitemap URLs, %d products, prototype=%s" % (len(SITEMAP), len(PRODUCTS), PROTOTYPE))
    for s in ("rheuma-salve-balm", "rheuma-salve-creme", "alievaid-herbal-drops", "cordyceps-cs-4", "maxi-cal"):
        print(s, [(v["label"], v["price"], v["code"]) for v in BY_SLUG[s]["variants"]])
