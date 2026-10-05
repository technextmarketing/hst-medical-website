"""
Home page sections owned separately from build.py: the range marquee, the brands section and the health notes.
build.py calls marquee(ctx), brands(ctx) and notes(ctx) with ctx = {root, PRODUCTS, CATS, BY_SLUG, POSTS, IC, esc,
money, cat_products, brand_label}. Styles live in assets/css/sections.css (class prefixes rg-, bp-, hn-).
Every motion is progressive: the markup is complete and usable without the small inline scripts.
"""
import datetime
import re

IMG = "assets/img/products/"
PAUSE = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6v12M15 6v12"/></svg>'
PLAY = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l10.5-6.5z"/></svg>'


# ---------------------------------------------------------------- Explore the range (two-row marquee)
def _mix(products):
    """Round-robin across categories so neighbours in a row come from different shelves."""
    groups, order = {}, []
    for p in products:
        if p["category"] not in groups:
            groups[p["category"]] = []
            order.append(p["category"])
        groups[p["category"]].append(p)
    out = []
    while any(groups.values()):
        for c in order:
            if groups[c]:
                out.append(groups[c].pop(0))
    return out


def marquee(ctx):
    root, esc, IC, money = ctx["root"], ctx["esc"], ctx["IC"], ctx["money"]
    seq = _mix(ctx["PRODUCTS"])
    rows = [seq[0::2], seq[1::2]]
    total = len(ctx["PRODUCTS"])

    def item(p, dup):
        tab = ' tabindex="-1"' if dup else ""
        price = money(p.get("price"))
        pcls = "rg-price" if p.get("price") else "rg-price rg-ask"
        return (f'<li><a class="rg-item" href="{root}products/{p["slug"]}/"{tab}>'
                f'<span class="rg-img"><img src="{root}{IMG}{p["image"]}-thumb.webp" alt="" width="360" height="360" loading="lazy" decoding="async"></span>'
                f'<span class="rg-name">{esc(p["name"])}</span><span class="{pcls}">{esc(price)}</span></a></li>')

    html_rows = []
    for i, r in enumerate(rows):
        a = "".join(item(p, False) for p in r)
        b = "".join(item(p, True) for p in r)
        html_rows.append(f'<div class="rg-row{" rev" if i else ""}" style="--n:{len(r)}">'
                         f'<ul class="rg-track" aria-label="Products, row {i + 1} of 2">{a}</ul>'
                         f'<ul class="rg-track" aria-hidden="true">{b}</ul></div>')
    return f"""<section class="band rg" aria-labelledby="h-range">
  <div class="counter">
    <div class="band-head"><div><h2 id="h-range">Explore the range</h2><p>{total} remedies and supplements, from Rheuma-Salve® balm to Zoo-Vite® gummies.</p></div><div class="rg-acts"><button class="btn btn-quiet rg-toggle" type="button" hidden><span class="rg-ip">{PAUSE}</span><span class="rg-ipl">{PLAY}</span><span class="rg-tl">Pause</span></button><a class="btn btn-quiet" href="{root}shop/">Shop all {total} products {IC['arrow']}</a></div></div>
  </div>
  <div class="rg-view">{''.join(html_rows)}</div>
  <script>(function(){{var s=document.currentScript.closest('section'),b=s.querySelector('.rg-toggle'),t=b.querySelector('.rg-tl');
if(!matchMedia('(prefers-reduced-motion: reduce)').matches){{b.hidden=false;b.addEventListener('click',function(){{var p=s.classList.toggle('paused');t.textContent=p?'Play':'Pause';b.setAttribute('aria-label',p?'Play the product carousel':'Pause the product carousel');}});b.setAttribute('aria-label','Pause the product carousel');}}
if('IntersectionObserver' in window)new IntersectionObserver(function(es){{s.classList.toggle('off',!es[0].isIntersecting);}},{{rootMargin:'60px 0px'}}).observe(s);}})();</script>
</section>"""


# ---------------------------------------------------------------- Our brands (five tinted panels)
BRANDS = [
    {"key": "rs", "name": "Rheuma-Salve®", "href": "shop/pain-relief/", "cta": "Shop Rheuma-Salve®",
     "desc": "Singapore's extra-strength pain relief since 1994, in five formats.",
     "picks": ["rheuma-salve-creme", "rheuma-salve-balm", "rheuma-salve-pain-relief-patch-cool"],
     "match": lambda p: p["category"] == "pain-relief"},
    {"key": "her", "name": "Heritage®", "href": "shop/immunity-energy/", "cta": "Heritage® tonics",
     "desc": "Traditional Asian remedies, prepared to modern GMP standards.",
     "picks": ["american-ginseng", "korean-red-ginseng", "lingzhi-cracked-spores"],
     "match": lambda p: p["brand"] == "Heritage" and p["category"] != "pain-relief"},
    {"key": "hst", "name": "HST Medical®", "href": "shop/cough-cold-flu/", "cta": "Cough and cold",
     "desc": "Pharmaceutical-grade supplements and herbal remedies.",
     "picks": ["alievaid-herbal-drops", "cough-alievaid-herbal-lintus", "ivy-leaf-cough-syrup"],
     "match": lambda p: p["brand"] == "HST Medical"},
    {"key": "zoo", "name": "Zoo-Vite®", "href": "shop/kids/", "cta": "Zoo-Vite® for kids",
     "desc": "Kids' gummies and jelly sticks for immunity, eyes, brain and daily vitamins.",
     "picks": ["zoo-vite-elderberry-gummies", "zoo-vite-multivitamin-gummies", "zoo-vite-immune-jelly"],
     "match": lambda p: p["brand"] == "Zoo-Vite"},
    {"key": "kowa", "name": "Kowa", "href": "about/", "cta": "Our story",
     "desc": "HST Medical has been part of Kowa Pharmaceutical Asia since 29 May 2026, within the Japanese Kowa group behind Vantelin."},
]
RS_FORMATS = [("rheuma-salve-balm", "Balm"), ("rheuma-salve-creme", "Crème"), ("rheuma-salve-liniment", "Liniment"),
              ("rheuma-salve-pain-relief-patch-cool", "Patch"), ("rheuma-salve-medi-stick", "Medi-Stick")]


def _picks(ctx, b):
    by = ctx["BY_SLUG"]
    got = [by[s] for s in b["picks"] if s in by]
    for p in ctx["PRODUCTS"]:
        if len(got) >= 3:
            break
        if b["match"](p) and p not in got:
            got.append(p)
    return got[:3]


def brands(ctx):
    root, esc, IC = ctx["root"], ctx["esc"], ctx["IC"]
    panels = []
    for b in BRANDS:
        hid = "bp-h-" + b["key"]
        extra = ""
        if b["key"] == "rs":
            extra = '<ul class="bp-formats" aria-label="Rheuma-Salve® formats">' + "".join(
                f'<li><a href="{root}products/{s}/">{esc(l)}</a></li>' for s, l in RS_FORMATS if s in ctx["BY_SLUG"]) + "</ul>"
        if b["key"] == "kowa":
            art = """<div class="bp-chain" aria-hidden="true"><span class="bp-word">Kowa</span><ol>
<li><b>Kowa group</b><small>Japan, the makers of Vantelin</small></li>
<li><b>Kowa Pharmaceutical Asia</b><small>Since 29 May 2026</small></li>
<li class="me"><b>HST Medical</b><small>Singapore, since 1994</small></li></ol></div>"""
        else:
            size = "" if b["key"] == "rs" else "-thumb"
            imgs = "".join(f'<img class="f{i + 1}" src="{root}{IMG}{p["image"]}{size}.webp" alt="" width="{510 if not size else 360}" height="{510 if not size else 360}" loading="lazy" decoding="async">'
                           for i, p in enumerate(_picks(ctx, b)))
            art = f'<div class="bp-fan" aria-hidden="true">{imgs}</div>'
        panels.append(f"""<article class="bp bp-{b['key']}" aria-labelledby="{hid}">
  <div class="bp-copy"><h3 id="{hid}">{esc(b['name'])}</h3><p>{esc(b['desc'])}</p>{extra}<a class="bp-cta" href="{root}{b['href']}">{esc(b['cta'])} {IC['arrow']}</a></div>
  {art}
</article>""")
    return f"""<section class="band bp-band" aria-labelledby="h-brands">
  <div class="counter">
    <div class="band-head"><div><h2 id="h-brands">Our brands</h2><p>Four ranges from HST Medical, a Singapore company since 1994 and now part of Japan's Kowa group.</p></div><a class="btn btn-quiet" href="{root}brands/">About the brands {IC['arrow']}</a></div>
    <div class="bp-grid">
{chr(10).join(panels)}
    </div>
  </div>
  <script>(function(){{var g=document.currentScript.closest('section').querySelector('.bp-grid');
if(matchMedia('(prefers-reduced-motion: reduce)').matches||!('IntersectionObserver' in window)||g.getBoundingClientRect().top<innerHeight*.85)return;
g.classList.add('pre');var io=new IntersectionObserver(function(es){{if(!es[0].isIntersecting)return;io.disconnect();g.classList.add('go');requestAnimationFrame(function(){{g.classList.remove('pre');}});setTimeout(function(){{g.classList.remove('go');}},2000);}},{{threshold:.12}});io.observe(g);}})();</script>
</section>"""


# ---------------------------------------------------------------- Health notes (editorial cards)
ART = {
    # jar of balm with a mint leaf and a cooling sparkle
    "jar": """<svg viewBox="0 0 120 120" aria-hidden="true"><rect pathLength="1" x="33" y="40" width="44" height="12" rx="4"/><path pathLength="1" d="M29 52h52v28a14 14 0 0 1-14 14H43a14 14 0 0 1-14-14z"/><path pathLength="1" d="M38 66h34M38 74h20"/><path pathLength="1" d="M74 41c0-15 11-25 28-25 0 16-10 26-28 25z"/><path pathLength="1" d="M75 40 94 23"/><path pathLength="1" d="M18 26v10M13 31h10"/><circle pathLength="1" cx="20" cy="56" r="2.5"/></svg>""",
    # droplet with breath lines: cough, cold and flu
    "drop": """<svg viewBox="0 0 120 120" aria-hidden="true"><path pathLength="1" d="M60 16C52 30 36 46 36 64a24 24 0 0 0 48 0c0-18-16-34-24-48z"/><path pathLength="1" d="M48 66a12 12 0 0 0 12 12"/><path pathLength="1" d="M90 50h16a6 6 0 1 0-6-6"/><path pathLength="1" d="M92 64h20"/><path pathLength="1" d="M88 78h12a6 6 0 1 1-6 6"/><path pathLength="1" d="M10 58h16M14 72h12"/></svg>""",
    # shield with a tick: GMP and Halal
    "shield": """<svg viewBox="0 0 120 120" aria-hidden="true"><path pathLength="1" d="M60 14 92 26v26c0 24-14 40-32 50C42 92 28 76 28 52V26z"/><path pathLength="1" d="M60 24 84 33v19c0 18-10 31-24 39-14-8-24-21-24-39V33z"/><path pathLength="1" d="m47 58 9 9 18-20"/><path pathLength="1" d="M104 20v10M99 25h10"/><path pathLength="1" d="M15 78v8M11 82h8"/></svg>""",
}
NOTE_ART = {"balm-creme-liniment-or-patch": "jar", "cough-cold-or-flu-which-remedy": "drop", "what-gmp-and-halal-mean": "shield"}


def _date(d):
    try:
        x = datetime.date.fromisoformat(d)
        return f"{x.day} {x.strftime('%b')} {x.year}"
    except ValueError:
        return d


def notes(ctx):
    root, esc, IC = ctx["root"], ctx["esc"], ctx["IC"]
    keys = list(ART)
    cards = []
    for i, (s, t, d, x, body) in enumerate(ctx["POSTS"][:3]):
        art = ART[NOTE_ART.get(s, keys[i % len(keys)])]
        mins = max(1, round(len(re.sub(r"<[^>]+>", " ", body).split()) / 200))
        cards.append(f"""<article class="hn-card">
  <div class="hn-art hn-a{i % 3 + 1}" aria-hidden="true">{art}</div>
  <div class="hn-body"><h3><a href="{root}blog/{s}/">{esc(t)}</a></h3><p>{esc(x)}</p>
    <p class="hn-foot"><span><time datetime="{d}">{_date(d)}</time><span class="hn-rt"> · {mins} min read</span></span><span class="hn-read" aria-hidden="true">Read {IC['arrow']}</span></p></div>
</article>""")
    return f"""<section class="band hn-band" aria-labelledby="h-notes">
  <div class="counter">
    <div class="band-head"><div><h2 id="h-notes">Health notes</h2><p>Short, practical reading written with HST Medical's pharmacists.</p></div><a class="btn btn-quiet" href="{root}blog/">All notes {IC['arrow']}</a></div>
    <div class="hn-grid">
{chr(10).join(cards)}
    </div>
  </div>
  <script>(function(){{var g=document.currentScript.closest('section').querySelector('.hn-grid');
if(matchMedia('(prefers-reduced-motion: reduce)').matches||!('IntersectionObserver' in window)||g.getBoundingClientRect().top<innerHeight*.85)return;
g.classList.add('pre');var io=new IntersectionObserver(function(es){{if(!es[0].isIntersecting)return;io.disconnect();g.classList.add('go');requestAnimationFrame(function(){{requestAnimationFrame(function(){{g.classList.remove('pre');}});}});setTimeout(function(){{g.classList.remove('go');}},2600);}},{{threshold:.2}});io.observe(g);}})();</script>
</section>"""
