"""
Builds _src/products.json from the HST Medical product-sheet catalogue (Heyzine flipbook PDF, 54 pages).

Inputs (session scratchpad, produced once from cat.pdf):
  ext/catalogue.json  — per-page text + extracted image
  ext/store.json      — live hstmedical.com store list (title, SGD price, URL)

Each product sheet follows one layout: category header, description paragraph, "For orders…" block,
"Always read the label…", product name lines + tagline, then BENEFITS / SUGGESTED USAGE /
ACTIVE INGREDIENTS / COUNTRY / PRODUCTS (item codes). We split on those headings.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get("TEMP", ""), "hst-scratch")

CATS = {
    "pain-relief":        ("Premium Pain Relief",        "Rheuma-Salve® balms, creams, liniments and patches for joint pain, muscle aches, sprains and strains."),
    "cough-cold-flu":     ("Cough, Cold & Flu",           "Herbal lozenges, syrups, remedies and inhalers for cough, sore throat, flu and blocked noses."),
    "traditional-pain-relief": ("Traditional Pain Relief", "Time-tested Heritage® medicated oils for rheumatic pain, bruises and muscle strain."),
    "immunity-energy":    ("Immunity & Energy",           "Heritage® ginseng, cordyceps, deer antler and lingzhi tonics in vegicaps."),
    "beauty-wellness":    ("Beauty & Wellness",           "Squalene, pearl powder, crocodile oil, NMN and hair support from Heritage® and HST Medical®."),
    "kids":               ("Kids Supplements",            "Zoo-Vite® gummies and jelly sticks for immunity, eyes, brain and daily vitamins."),
    "bones-joints":       ("Bones & Joints",              "Joint, cartilage, calcium and vitamin D3+K2 support."),
    "alertness-memory-vision": ("Alertness, Memory & Vision", "Omega-3, DHA, eye health and ginkgo formulas."),
    "stress-sleep":       ("Stress, Anxiety & Sleep",     "Magnesium glycinate and pharmaceutical-grade melatonin."),
    "immunity-allergy":   ("Immunity & Allergy",          "Vitamin C, multivitamins and probiotics for daily defence."),
    "heart-liver-vitality": ("Heart, Liver, Urinary & Vitality", "Men's vitality, liver, urinary and women's health formulas."),
}

# page, slug, display name, brand, category, pack size, store-title keyword (for price), focus flag
PRODUCTS = [
    (3,  "rheuma-salve-balm",            "Rheuma-Salve® Pain Relief Balm",            "Heritage", "pain-relief", "50g (also 20g, value & travel packs)", "Pain Relief Balm (50g)", True),
    (4,  "rheuma-salve-creme",           "Rheuma-Salve® Crème",                        "Heritage", "pain-relief", "50g", "Crème (Single Pack)", True),
    (5,  "rheuma-salve-liniment",        "Rheuma-Salve® Liniment",                     "Heritage", "pain-relief", "10ml", "Liniment (10ml Single Bottle)", True),
    (6,  "rheuma-salve-pain-relief-patch-cool", "Rheuma-Salve® Pain Relief Patch (Cool)", "Heritage", "pain-relief", "8 patches, 10 × 7 cm", "Pain Relief Patch Cool", True),
    (7,  "rheuma-salve-medi-stick",      "Rheuma-Salve® On-the-Go Medi-Stick",         "Heritage", "pain-relief", "15g", "Medi-Stick 15g", True),
    (8,  "american-ginseng",             "American Ginseng",                           "Heritage", "immunity-energy", "60 vegicaps", "American Ginseng (Single Pack)", False),
    (9,  "cordyceps-cs-4",               "Cordyceps CS-4",                             "Heritage", "immunity-energy", "60 vegicaps", "Cordyceps CS-4 (Single Pack)", False),
    (10, "deer-antler",                  "Deer Antler",                                "Heritage", "immunity-energy", "60 vegicaps", "Deer Antler (Single Pack)", False),
    (11, "korean-red-ginseng",           "Korean Red Ginseng",                         "Heritage", "immunity-energy", "60 vegicaps", "Korean Red Ginseng (Single Pack)", False),
    (12, "lingzhi-cracked-spores",       "Lingzhi Cracked Spores Plus",                "Heritage", "immunity-energy", "60 vegicaps", "Lingzhi Cracked Spores Plus (Single Pack)", False),
    (13, "deep-sea-squalene",            "Deep Sea Squalene",                          "Heritage", "beauty-wellness", "200 softgels", "Deep Sea Squalene (Single Pack)", False),
    (14, "pearl-powder",                 "Pure Medicinal Pearl Powder",                "Heritage", "beauty-wellness", "60 vegicaps", "Pearl Powder (Single Pack)", False),
    (15, "shou-wu-hair-plus",            "Shou Wu Hair Plus",                          "HST Medical", "beauty-wellness", "80 vegicaps", "Shou Wu Hair Plus (Single Pack)", False),
    (16, "crocodile-pure-skin-oil",      "Crocodile Pure Skin Oil",                    "Heritage", "beauty-wellness", "50ml", "Crocodile Pure Skin Oil (50ml)", False),
    (17, "age-defying-nmn",              "Age-Defying NMN Pearl & Collagen",           "Heritage", "beauty-wellness", "30 sachets", "Age-Defying NMN", False),
    (18, "gold-lion-rheumatic-oil",      "Gold Lion Rheumatic Oil",                    "Heritage", "traditional-pain-relief", "60ml", "Gold Lion Rheumatic Oil (Single Pack)", False),
    (19, "safflower-red-flower-oil",     "Safflower Red Flower Oil (Hung Far Oil)",    "Heritage", "traditional-pain-relief", "60ml", "Hung Far (Safflower Red Flower) Oil (Single Pack)", False),
    (20, "qian-li-zhui-feng-oil",        "Qian Li Zhui Feng Oil",                      "Heritage", "traditional-pain-relief", "60ml", "Qian Li Zhui Feng Oil (Single)", False),
    (21, "zoo-vite-elderberry-gummies",  "Zoo-Vite® “Perky Penguin” Elderberry Gummies", "Zoo-Vite", "kids", "60 gummies", "Perky Penguin Gummies (Single Pack)", False),
    (22, "zoo-vite-lutein-jelly",        "Zoo-Vite® “Inspector Charley” Lutein Jelly", "Zoo-Vite", "kids", "30 sticks", "Inspector Charly Lutein Jelly", False),
    (23, "zoo-vite-multivitamin-gummies","Zoo-Vite® “Safari Buddies” Multivitamin Gummies", "Zoo-Vite", "kids", "60 gummies", "Safari Buddies Gummies (Single Pack)", False),
    (24, "zoo-vite-immune-jelly",        "Zoo-Vite® “Super Panda” Immune Jelly",       "Zoo-Vite", "kids", "30 sticks", "Immune Jelly Sticks", False),
    (25, "zoo-vite-dha-jelly",           "Zoo-Vite® “Professor Skippy” DHA Jelly",     "Zoo-Vite", "kids", "30 sticks", "DHA Jelly Sticks", False),
    (26, "alievaid-herbal-drops",        "Alievaid Herbal Drops",                      "HST Medical", "cough-cold-flu", "12 lozenges", "Alievaid Herbal Drops", True),
    (27, "cough-alievaid-herbal-lintus", "Cough Alievaid Herbal Lintus",               "HST Medical", "cough-cold-flu", "120ml", "Cough Alievaid", True),
    (28, "flu-gard",                     "Flu Gard Herbal Remedy",                     "HST Medical", "cough-cold-flu", "30 vegicaps", "Flu Gard", True),
    (29, "ivy-leaf-cough-syrup",         "Ivy Leaf Cough Syrup",                       "HST Medical", "cough-cold-flu", "12 sachets × 10ml", "Ivy Leaf Cough Syrup", True),
    (30, "ivy-leaf-drops",               "Ivy Leaf Drops",                             "HST Medical", "cough-cold-flu", "12 lozenges", "Ivy Leaf Drops", True),
    (31, "sinus-clear-2-in-1",           "Sinus Clear 2-in-1 Nasal Inhaler",           "HST Medical", "cough-cold-flu", "2ml", "2-in-1 Sinus Clear", True),
    (32, "arthro-gard",                  "Arthro Gard Advanced Formula",               "HST Medical", "bones-joints", "90 capsules", "Arthro Gard (Single Pack)", False),
    (33, "curqmax",                      "CurQmax Turmeric-Boswellia Complex",         "HST Medical", "bones-joints", "60 vegicaps", "CurQmax (Single Pack)", False),
    (34, "maxi-cal",                     "Maxi-Cal",                                   "HST Medical", "bones-joints", "180 vegi softgels", None, False),
    (35, "vitamin-d3-k2",                "Vitamin D3 + K2",                            "HST Medical", "bones-joints", "100 capsules", "Vitamin D3 + K2", False),
    (36, "algaomega",                    "AlgaOmega",                                  "HST Medical", "alertness-memory-vision", "60 mini softgels", "AlgaOmega (Buy 1", False),
    (37, "clear-eyes-plus",              "Clear Eyes Plus",                            "HST Medical", "alertness-memory-vision", "60 vegicaps", "Clear Eye Plus (Single Pack)", False),
    (38, "dha-600",                      "DHA 600",                                    "HST Medical", "alertness-memory-vision", "90 mini softgels", "DHA 600 Fish Oil (Single Pack)", False),
    (39, "fish-oil-minigels",            "Fish Oil Minigels High Strength Omega-3",    "HST Medical", "alertness-memory-vision", "320 mini softgels", "Fish Oil Minigels", False),
    (40, "max-omega",                    "Max-Omega High Potency Omega-3 with D3",     "HST Medical", "alertness-memory-vision", "120 mini softgels", "Max-Omega Fish Oil (Single Pack)", False),
    (41, "neuro-gard",                   "Neuro Gard Ginkgo Biloba + B Vitamins",      "HST Medical", "alertness-memory-vision", "60 vegicaps", "Neuro Gard (Single Pack)", False),
    (42, "magnesium-glycinate",          "Magnesium Glycinate",                        "HST Medical", "stress-sleep", "60 vegicaps", "Magnesium Glycinate", False),
    (43, "melatonin-5mg",                "Melatonin 5mg",                              "HST Medical", "stress-sleep", "30 vegicaps", "Melatonin 5mg", False),
    (44, "sleep-aid-melatonin-10mg",     "Sleep Aid Melatonin 10mg",                   "HST Medical", "stress-sleep", "30 vegicaps", "Sleep Aid (Melatonin 10mg) (Single Pack)", False),
    (45, "sleep-fast-melatonin-gummies", "Sleep Fast Melatonin Gummies 5mg",           "HST Medical", "stress-sleep", "60 gummies", None, False),
    (46, "boost-immune",                 "Boost Immune C1000mg + Bs + D3 + Zinc",      "HST Medical", "immunity-allergy", "48 effervescent tablets", "Boost Immune (48 Effervescent", False),
    (47, "c-rosehips",                   "C+ Rosehips Time Release",                   "HST Medical", "immunity-allergy", "90 time-released tablets", "C+Rosehips (Single Pack)", False),
    (48, "therra-m",                     "Therra-M Multi-Vitamin with Minerals",       "HST Medical", "immunity-allergy", "90 tablets", "Therra-M", False),
    (49, "synbioten",                    "Synbioten Probiotics + Prebiotics + Enzyme", "HST Medical", "immunity-allergy", "30 vegicaps", "Synbioten (Single Pack)", False),
    (50, "libi-max",                     "Libi-Max",                                   "HST Medical", "heart-liver-vitality", "90 tablets", None, False),
    (51, "liver-gard-forte",             "Liver Gard Forte",                           "HST Medical", "heart-liver-vitality", "60 vegicaps", "Liver Gard Forte (Single Pack)", False),
    (52, "uri-gard",                     "Uri Gard Herbal Formula",                    "HST Medical", "heart-liver-vitality", "80 vegicaps", "Uri Gard", False),
    (53, "womens-choice",                "Women’s Choice",                             "HST Medical", "heart-liver-vitality", "60 vegicaps", "Women's Choice", False),
]

HEADINGS = ["BENEFITS", "SUGGESTED USAGE", "USAGE & SAFETY", "ACTIVE INGREDIENTS", "HERBAL FORMULA",
            "COUNTRY", "PRODUCTS", "PRODUCT SPECIFICATIONS", "KEY INGREDIENTS", "INGREDIENTS", "DIRECTIONS",
            "RECOMMENDED USAGE", "DOSAGE", "WARNING", "CAUTION", "STORAGE", "NOTE", "SERVING"]
BAD_LINES = re.compile(r"^(For orders please contact:|.*territory manager|.*resellercontact@|Always read the label|follow directions for use|Halal \(Malaysia\)|MS1500.*|Certified ISO.*|ITEM CODE.*|P|R|O|D|U|C|T|S|I|N|G|A|E|B|F)$")


def clean(s):
    s = s.replace("�", "•").replace("•\t", "• ").replace("\t", " ")
    s = re.sub(r"[ ]{2,}", " ", s)
    return s.strip()


def bullets(block):
    """Split a heading block into bullet items (lines starting with •) or sentences."""
    items, cur = [], ""
    for ln in block.splitlines():
        ln = clean(ln)
        if not ln or BAD_LINES.match(ln):
            continue
        if ln.startswith("•"):
            if cur: items.append(cur.strip())
            cur = ln.lstrip("• ").strip()
        else:
            cur = (cur + " " + ln).strip() if cur else ln
    if cur: items.append(cur.strip())
    return items


def parse_page(text):
    lines = [l for l in text.splitlines()]
    # 1) category header = first line(s) with spaced capitals; description = following paragraph until "For orders"
    i = 0
    while i < len(lines) and re.match(r"^[A-Z ,&]+$", lines[i].strip()) and len(lines[i].strip()) > 3:
        i += 1
    if i < len(lines) and lines[i].strip() in ("Proprietary Formula",):
        i += 1
    desc = []
    while i < len(lines) and not lines[i].startswith("For orders") and not lines[i].strip().startswith("Always read"):
        if lines[i].strip() and not re.match(r"^[A-Z &,]{6,}$", lines[i].strip()):
            desc.append(lines[i].strip())
        i += 1
    description = clean(" ".join(desc))
    # 2) section blocks
    body = "\n".join(lines)
    pat = re.compile(r"^(%s)\s*$" % "|".join(re.escape(h) for h in HEADINGS), re.M)
    parts = pat.split(body)
    sections = {}
    for k in range(1, len(parts) - 1, 2):
        sections.setdefault(parts[k], "")
        sections[parts[k]] += parts[k + 1]
    # 3) tagline: block between "follow directions for use" and first heading = name lines + tagline
    m = re.search(r"follow directions for use\n(.*?)(?=\n(?:%s)\s*\n)" % "|".join(re.escape(h) for h in HEADINGS), body, re.S)
    tagline = ""
    if m:
        nl = [clean(x) for x in m.group(1).splitlines() if clean(x)]
        if nl:
            tagline = nl[-1]
    # 4) item codes
    skus = []
    for mm in re.finditer(r"•\s*([^\n•]+?)\s*\n?\s*([\w ×xX\d.()-]+?)\s*\n?\s*ITEM CODE\s*:\s*(\d+)", sections.get("PRODUCTS", ""), re.S):
        name, size, code = clean(mm.group(1)), clean(mm.group(2)), mm.group(3)
        skus.append({"name": name, "size": size, "code": code})
    country = ""
    if "COUNTRY" in sections:
        c = [clean(x) for x in sections["COUNTRY"].splitlines() if clean(x)]
        country = c[0] if c else ""
    usage = bullets(sections.get("SUGGESTED USAGE", "") or sections.get("USAGE & SAFETY", "") or sections.get("DIRECTIONS", "") or sections.get("RECOMMENDED USAGE", ""))
    ingredients = bullets(sections.get("ACTIVE INGREDIENTS", "") or sections.get("HERBAL FORMULA", "") or sections.get("KEY INGREDIENTS", "") or sections.get("INGREDIENTS", ""))
    benefits = bullets(sections.get("BENEFITS", ""))
    return {"description": description, "tagline": tagline, "benefits": benefits, "usage": usage,
            "ingredients": ingredients, "country": country, "skus": skus}


def main():
    cat = {p["page"]: p for p in json.load(open(os.path.join(SCRATCH, "ext", "catalogue.json"), encoding="utf-8"))}
    store = json.load(open(os.path.join(SCRATCH, "ext", "store.json"), encoding="utf-8"))
    out = []
    for page, slug, name, brand, cat_id, size, key, focus in PRODUCTS:
        d = parse_page(cat[page]["text"])
        price, url = None, None
        if key:
            for s in store:
                if key.lower() in s["title"].lower():
                    price, url = s["price"], s["url"]; break
        # fall back to the first SKU code's name if tagline empty
        out.append({
            "slug": slug, "name": name, "brand": brand, "category": cat_id, "size": size, "focus": focus,
            "price": price, "live_url": url, "image": f"p{page:02d}",
            **d,
        })
    json.dump({"categories": {k: {"name": v[0], "blurb": v[1]} for k, v in CATS.items()}, "products": out},
              open(os.path.join(HERE, "products.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    missing = [p["name"] for p in out if not p["description"] or not p["benefits"]]
    print("products:", len(out), "| no price:", sum(1 for p in out if p["price"] is None), "| weak parse:", missing)


if __name__ == "__main__":
    main()
