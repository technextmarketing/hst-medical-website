"""
About page (owned separately from build.py). build.py calls render(ctx, crumb); styles in assets/css/about.css
(linked only on this page; base about styles still live in style.css under "about page"). ctx keys: see build.page_ctx.

Motion: a two-line inline script. The first (top of <main>) adds .ab-js only when motion is allowed and
IntersectionObserver exists; every hidden/entrance state in about.css is scoped to .ab-js, so the page is fully
visible without JS or with prefers-reduced-motion. The second (end of <main>) runs reveals, count-ups, the
scroll-drawn timeline and the card tilt.
"""
import re

# line-art icons: plain brand-coloured strokes (no plates). pathLength=1 lets about.css draw them in.
_ICONS = {
    "higher": '<path d="M2.5 20 9 9.5l3.2 5.2L15 10.5 21.5 20z"/><path d="M15 8V3.5M12.8 5.6 15 3.5l2.2 2.1"/>',
    "stronger": '<path d="M12 20.5s-7.5-4.6-7.5-10.4A4.3 4.3 0 0 1 12 7.3a4.3 4.3 0 0 1 7.5 2.8c0 5.8-7.5 10.4-7.5 10.4z"/><path d="M7.6 12.3h2.6l1.3-2.4 2 4.6 1.3-2.2h1.6"/>',
    "together": '<circle cx="12" cy="7.5" r="2.8"/><path d="M6.5 19.5c.6-3.4 2.7-5.2 5.5-5.2s4.9 1.8 5.5 5.2"/><circle cx="5" cy="10.2" r="2"/><path d="M1.8 18c.4-2.3 1.6-3.5 3.4-3.6"/><circle cx="19" cy="10.2" r="2"/><path d="M22.2 18c-.4-2.3-1.6-3.5-3.4-3.6"/>',
    "hall": '<path d="M3 10.5 12 4l9 6.5"/><path d="M5 9.5V20h14V9.5"/><path d="M10 20v-5.5h4V20"/><path d="M2.5 20h19"/>',
    "doc": '<path d="M6.5 3h7.5l4 4v14H6.5z"/><path d="M14 3v4h4"/><path d="M9.5 12h5M9.5 15.5h5"/>',
    "ribbon": '<circle cx="12" cy="9" r="5.5"/><path d="m8.6 13.3-1.6 7.2 5-2.6 5 2.6-1.6-7.2"/><path d="m9.8 9 1.5 1.5 2.9-2.9"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17"/><path d="M12 3.5c2.4 2.5 3.6 5.3 3.6 8.5s-1.2 6-3.6 8.5c-2.4-2.5-3.6-5.3-3.6-8.5s1.2-6 3.6-8.5z"/>',
    "leaf": '<path d="M5 19C5 10 10 5 20 4c0 10-5 15-14 15z"/><path d="M5 19c3-4 6-7 10-9"/>',
    "flask": '<path d="M9 3h6M10 3v6L5 18a2 2 0 0 0 1.8 3h10.4A2 2 0 0 0 19 18l-5-9V3"/><path d="M7.5 14h9"/>',
    "pin": '<path d="M12 21s-6.5-6.2-6.5-11.2a6.5 6.5 0 0 1 13 0C18.5 14.8 12 21 12 21z"/><circle cx="12" cy="9.8" r="2.4"/>',
    "phone": '<path d="M5.2 3.5h3l1.6 4.1-2.1 1.4a11.5 11.5 0 0 0 5.3 5.3l1.4-2.1 4.1 1.6v3a2.3 2.3 0 0 1-2.5 2.3C9.4 18.6 5.4 14.6 4.9 6a2.3 2.3 0 0 1 .3-2.5z"/>',
    "mail": '<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="m3.5 7 8.5 6 8.5-6"/>',
}


def icon(name, cls="ic"):
    body = re.sub(r"<(path|circle|rect) ", r'<\1 pathLength="1" ', _ICONS[name])
    return '<svg class="%s" viewBox="0 0 24 24" aria-hidden="true">%s</svg>' % (cls, body)


SHORT = {"pain-relief": "Pain relief", "cough-cold-flu": "Cough and cold", "traditional-pain-relief": "Traditional oils",
         "immunity-energy": "Tonics", "beauty-wellness": "Beauty", "kids": "Kids", "bones-joints": "Bones and joints",
         "alertness-memory-vision": "Memory and vision", "stress-sleep": "Sleep", "immunity-allergy": "Immunity",
         "heart-liver-vitality": "Heart and liver"}

# the four brands. Rheuma-Salve = the pain-relief shelf (Heritage-marked packs); Heritage = the rest of that mark.
BRANDS = [
    ("rs", "Rheuma-Salve®", "Balm, crème, liniment, cooling patch and Medi-Stick for joint and muscle pain, with travel packs too.",
     ["rheuma-salve-pain-relief-patch-cool", "rheuma-salve-balm", "rheuma-salve-medi-stick"], "shop/pain-relief/"),
    ("her", "Heritage®", "Ginseng, cordyceps and lingzhi tonics, pearl powder and squalene, and traditional medicated oils.",
     ["pearl-powder", "korean-red-ginseng", "gold-lion-rheumatic-oil"], "shop/?q=heritage"),
    ("hst", "HST Medical®", "Cough and cold remedies, with support for joints, sleep, immunity, eyes, memory, heart and liver.",
     ["shou-wu-hair-plus", "boost-immune", "sleep-aid-melatonin-10mg"], "shop/?q=hst+medical"),
    ("zoo", "Zoo-Vite®", "Kids' gummies and jelly sticks for immunity, eyes and brain (DHA).",
     ["zoo-vite-immune-jelly", "zoo-vite-multivitamin-gummies", "zoo-vite-dha-jelly"], "shop/kids/"),
]

TL_ICON = {"1930": "hall", "1994": "doc", "2024": "ribbon", "2026": "globe"}
TL_SUB = {"1930": "Established by the family of HST Medical's co-founders.",
          "1994": "The name is a tribute to Heng Say Tong.",
          "2024": "Shou Wu Hair Plus, Sleep Aid and The Guardian Awards 2024.",
          "2026": "Part of the Japanese Kowa group."}

# award file -> (h3, honour line, product slug for the CTA, CTA label)
AWARDS = [
    ("award-beauty-insider-2024-shou-wu.webp", "Beauty Insider Health & Wellness Awards 2024",
     "Best Hair Supplements (Beauty Insiders' Choice): HST Medical Shou Wu Hair Plus", "shou-wu-hair-plus", "View Shou Wu Hair Plus"),
    ("award-beauty-insider-2024-sleep-aid.webp", "Beauty Insider Health & Wellness Awards 2024",
     "Best Wellness Supplement (Readers' Choice): HST Medical Sleep Aid", "sleep-aid-melatonin-10mg", "View Sleep Aid"),
    ("award-guardian-2024.webp", "The Guardian Awards 2024", "Winner", "rheuma-salve-balm", "View Rheuma-Salve® Balm"),
]

MAP_DIR = "https://www.google.com/maps/dir/?api=1&amp;destination=HST+Medical+Pte+Ltd,+152+Paya+Lebar+Road,+Singapore+409020"
KOWA_NEWS = "https://hstmedical.com/hst-medical-joins-kowa-pharmaceutical-asia/"
SASSY = "https://www.sassymamasg.com/health-picky-eaters-multivitamins-zoo-vite/"

HEAD_JS = "<script>(function(m){try{if(m&&'IntersectionObserver' in window&&!matchMedia('(prefers-reduced-motion: reduce)').matches)m.classList.add('ab-js')}catch(e){}})(document.currentScript&&document.currentScript.parentNode)</script>"

TAIL_JS = """<script>
(function(){
  var m=document.getElementById('main');
  if(!m||!m.classList.contains('ab-js'))return;
  function count(el){
    var to=+el.getAttribute('data-to'),from=+(el.getAttribute('data-from')||0),t0=0,dur=1500;
    function step(t){if(!t0)t0=t;var k=Math.min(1,(t-t0)/dur),e=1-Math.pow(1-k,4);el.textContent=Math.round(from+(to-from)*e);if(k<1)requestAnimationFrame(step);}
    requestAnimationFrame(step);
  }
  m.querySelectorAll('[data-to]').forEach(function(el){el.textContent=el.getAttribute('data-from')||'0';});
  var ob=new IntersectionObserver(function(es){es.forEach(function(e){
    if(!e.isIntersecting)return;var el=e.target;ob.unobserve(el);el.classList.add('is-in');
    el.querySelectorAll('[data-to]').forEach(count);
  });},{rootMargin:'0px 0px -8% 0px',threshold:0.12});
  m.querySelectorAll('[data-rv]').forEach(function(el){ob.observe(el);});

  var tl=m.querySelector('[data-tl]');
  if(tl){
    var track=tl.querySelector('.ab-tl-track'),dots=[].slice.call(tl.querySelectorAll('.ab-tl-dot')),stops=[].slice.call(tl.querySelectorAll('.ab-tl-stop')),fr=[],vert=false,a0=0,len=1,busy=false,best=0;
    var update=function(){
      busy=false;var r=tl.getBoundingClientRect(),vh=innerHeight,p;
      p=vert?(vh*0.7-(r.top+a0))/len:(vh*0.92-r.top)/(vh*0.45);
      p=Math.max(best,Math.min(1,p));best=p;
      tl.style.setProperty('--p',p.toFixed(4));
      stops.forEach(function(s,i){s.classList.toggle('on',p>0.001&&p>=fr[i]-0.002);});
    };
    var layout=function(){
      if(!dots.length)return;
      var r=tl.getBoundingClientRect(),a=dots[0].getBoundingClientRect(),b=dots[dots.length-1].getBoundingClientRect();
      var ax=a.left+a.width/2-r.left,ay=a.top+a.height/2-r.top,bx=b.left+b.width/2-r.left,by=b.top+b.height/2-r.top;
      vert=Math.abs(bx-ax)<4;
      if(vert){a0=ay;len=Math.max(1,by-ay);track.style.cssText='left:'+(ax-1.5)+'px;top:'+ay+'px;width:3px;height:'+len+'px;right:auto;bottom:auto';}
      else{len=Math.max(1,bx-ax);track.style.cssText='left:'+ax+'px;top:'+(ay-1.5)+'px;width:'+len+'px;height:3px;right:auto;bottom:auto';}
      fr=dots.map(function(d){var q=d.getBoundingClientRect();return vert?(q.top+q.height/2-r.top-ay)/len:(q.left+q.width/2-r.left-ax)/len;});
      update();
    };
    addEventListener('scroll',function(){if(!busy){busy=true;requestAnimationFrame(update);}},{passive:true});
    addEventListener('resize',layout);addEventListener('load',layout);
    if(document.fonts&&document.fonts.ready)document.fonts.ready.then(layout);
    layout();
  }

  if(matchMedia('(hover: hover) and (pointer: fine)').matches){
    m.querySelectorAll('[data-tilt]').forEach(function(el){
      var raf=0,x=0,y=0;
      el.addEventListener('pointermove',function(e){var r=el.getBoundingClientRect();x=(e.clientX-r.left)/r.width-0.5;y=(e.clientY-r.top)/r.height-0.5;
        if(!raf)raf=requestAnimationFrame(function(){raf=0;el.style.setProperty('--rx',(x*7).toFixed(2)+'deg');el.style.setProperty('--ry',(-y*7).toFixed(2)+'deg');});});
      el.addEventListener('pointerleave',function(){el.style.removeProperty('--rx');el.style.removeProperty('--ry');});
    });
  }
})();
</script>"""


def render(ctx, crumb):
    esc, IC, root, map_embed = ctx["esc"], ctx["IC"], ctx["root"], ctx["map_embed"]
    PRODUCTS, CATS, BY_SLUG = ctx["PRODUCTS"], ctx["CATS"], ctx["BY_SLUG"]
    L = {m["file"]: m for m in ctx["live_manifest"]()}
    AWARD_TEXT, TIMELINE = ctx["AWARD_TEXT"], ctx["TIMELINE"]
    arrow = IC["arrow"]

    def img(f, cls="", lazy=True, alt=None):
        m = L.get(f)
        if not m:
            return ""
        return '<img%s src="%sassets/img/live/%s" alt="%s" width="%s" height="%s"%s decoding="async">' % (
            ' class="%s"' % cls if cls else "", root, f, esc(alt if alt is not None else (m.get("alt") or "")), m.get("width", 1200), m.get("height", 800), ' loading="lazy"' if lazy else ' fetchpriority="high"')

    def cut(slug, cls=""):
        p = BY_SLUG.get(slug)
        if not p:
            return ""
        return '<img%s src="%sassets/img/products/%s-thumb.webp" alt="" width="360" height="360" loading="lazy" decoding="async">' % (
            ' class="%s"' % cls if cls else "", root, p["image"])

    n_products, n_ranges = len(PRODUCTS), len(CATS)

    # ---- facts row (count-up on reveal; the final values are in the markup)
    facts = [("1930", "1900", "Heng Say Tong medical hall founded"), ("1994", "1960", "HST Medical Pte Ltd incorporated"),
             (str(n_products), "0", "products"), (str(n_ranges), "0", "health ranges"),
             ("3", "0", "pharmacy chains: Guardian, Watsons and NHGP")]
    facts_html = "".join(
        '<div class="ab-fact" data-rv style="--d:%dms"><dt>%s</dt><dd><span class="ab-num" aria-hidden="true" data-to="%s" data-from="%s" style="--w:%d">%s</span><span class="sr-only">%s</span></dd></div>'
        % (i * 90, esc(label), v, f, len(v), v, v) for i, (v, f, label) in enumerate(facts))

    # ---- Higher, Stronger, Together
    values = [("H", "higher", "Higher", "Everyone's aspiration to go higher, and it all starts with one's holistic health."),
              ("S", "stronger", "Stronger", "The best of East and West in integrative supplements, to help everyone be stronger on their journey of health."),
              ("T", "together", "Together", "Professionals from Traditional Chinese Medicine and Western pharmacology, working together to do great things for the world.")]
    values_html = "".join(
        '<article class="ab-value ab-lift" data-rv data-tilt style="--d:%dms"><span class="ab-letter" aria-hidden="true">%s</span>%s<h3>%s</h3><p>%s</p></article>'
        % (i * 110, L_, icon(ic, "ic ab-draw"), t, esc(x)) for i, (L_, ic, t, x) in enumerate(values))

    # ---- what we make: four brands, cut-outs from the catalogue
    def group(p):
        if p["brand"] == "Heritage" and p["category"] == "pain-relief":
            return "rs"
        return {"Heritage": "her", "HST Medical": "hst", "Zoo-Vite": "zoo"}.get(p["brand"], "hst")
    order = list(CATS.keys())
    brands_html = ""
    for i, (gid, name, line, picks, href) in enumerate(BRANDS):
        prods = [p for p in PRODUCTS if group(p) == gid]
        cats = sorted({p["category"] for p in prods}, key=lambda c: (-sum(1 for p in prods if p["category"] == c), order.index(c)))
        shown = cats[:3]
        chips = "".join('<li><a href="%sshop/%s/" title="%s">%s</a></li>' % (root, c, esc(CATS[c]["name"]), esc(SHORT.get(c, CATS[c]["name"]))) for c in shown)
        if len(cats) > 3:
            chips += '<li><a href="%s%s">+%d more</a></li>' % (root, href, len(cats) - 3)
        stage = "".join(cut(s, "c%d" % (k + 1)) for k, s in enumerate(picks))
        brands_html += f"""<article class="ab-brand ab-lift ab-b-{gid}" data-rv data-tilt style="--d:{i * 100}ms">
  <div class="ab-stage" aria-hidden="true">{stage}</div>
  <div class="ab-brand-body">
    <h3>{esc(name)}</h3>
    <p>{esc(line)}</p>
    <p class="ab-bcount"><b>{len(prods)}</b> products in <b>{len(cats)}</b> {'range' if len(cats) == 1 else 'ranges'}</p>
    <ul class="ab-ranges" aria-label="{esc(name)} ranges">{chips}</ul>
    <a class="btn btn-quiet btn-sm" href="{root}{href}">Shop {esc(name)} {arrow}</a>
  </div>
</article>"""

    # ---- timeline
    tl_html = "".join(
        f"""<li class="ab-tl-stop on" data-rv style="--d:{i * 120}ms">
  <span class="ab-tl-icon">{icon(TL_ICON.get(y, 'ribbon'), 'ic ab-draw')}</span>
  <span class="ab-tl-dot" aria-hidden="true"></span>
  <span class="ab-tl-body"><span class="ab-tl-year">{esc(y)}</span><b>{esc(t)}</b>{'<span class="ab-tl-sub">%s</span>' % esc(TL_SUB[y]) if y in TL_SUB else ''}</span>
</li>""" for i, (y, t) in enumerate(TIMELINE))

    # ---- Rheuma-Salve formats (all five, from the pain-relief shelf)
    fmt_names = {"rheuma-salve-balm": "Balm", "rheuma-salve-creme": "Crème", "rheuma-salve-liniment": "Liniment",
                 "rheuma-salve-pain-relief-patch-cool": "Cooling patch", "rheuma-salve-medi-stick": "Medi-Stick"}
    formats = "".join('<li><a href="%sproducts/%s/" style="--k:%d">%s<span>%s</span></a></li>' % (root, p["slug"], k, cut(p["slug"]), esc(fmt_names.get(p["slug"], p["name"])))
                      for k, p in enumerate([p for p in PRODUCTS if p["category"] == "pain-relief"]))

    # ---- awards
    awards_html = ""
    for i, (f, h, line, slug, cta) in enumerate(AWARDS):
        if f not in L:
            continue
        awards_html += f"""<article class="ab-aw ab-lift" data-rv data-tilt style="--d:{i * 110}ms">
  <div class="ab-aw-art">{img(f, alt=AWARD_TEXT.get(f, h))}</div>
  <div class="ab-aw-body">
    <h3>{icon('ribbon')}<span>{esc(h)}</span></h3>
    <p>{esc(line)}</p>
    <a class="btn btn-quiet btn-sm" href="{root}products/{slug}/">{esc(cta)} {arrow}</a>
  </div>
</article>"""

    seal = ('<svg class="ab-seal" viewBox="0 0 120 120" aria-hidden="true"><defs><path id="ab-seal-c" d="M60,60 m-45,0 a45,45 0 1,1 90,0 a45,45 0 1,1 -90,0"/></defs>'
            '<circle cx="60" cy="60" r="58" class="ab-seal-bg"/><circle cx="60" cy="60" r="33" class="ab-seal-in"/>'
            '<g class="ab-seal-ring"><text><textPath href="#ab-seal-c" textLength="280" lengthAdjust="spacing">HENG SAY TONG · SINCE 1930 · HIGHER · STRONGER · TOGETHER ·</textPath></text></g>'
            '<text x="60" y="58" text-anchor="middle" class="ab-seal-s">SINCE</text><text x="60" y="76" text-anchor="middle" class="ab-seal-y">1930</text></svg>')

    return f"""
<main id="main" class="ab-page">{HEAD_JS}
<div class="counter">{crumb}</div>
<section class="ab-hero" aria-labelledby="h-about">
  <div class="counter ab-hero-grid">
    <div class="ab-hero-copy">
      <h1 id="h-about">About <span class="ab-grad">HST Medical</span></h1>
      <p class="lead">HST Medical (博诚药业) is a Singapore health supplements and pain-relief company, home of the Rheuma-Salve® Pain Relief Balm and the Zoo-Vite® kids' vitamins, and part of Kowa Pharmaceutical Asia since 29 May 2026.</p>
      <div class="ab-ctas"><a class="btn btn-stamp" href="{root}shop/">Shop all {n_products} products {arrow}</a><a class="btn btn-quiet" href="{root}where-to-buy/">Where to buy</a></div>
    </div>
    <div class="ab-hero-visual">
      {seal}
      <figure class="ab-hero-photo">{img('kowa-joined-signing.webp', lazy=False)}</figure>
      <p class="ab-hero-cap"><b>We have joined Kowa Pharmaceutical Asia</b>Mr. Shigeru Kimura, Vice-Chairman of Kowa's Board of Directors, with HST Medical co-founder Simone Tan at the signing ceremony.</p>
    </div>
  </div>
</section>

<section class="ab-facts" aria-label="HST Medical in numbers">
  <dl class="counter">{facts_html}</dl>
</section>

<section class="ab-hstwrap" aria-labelledby="h-hst">
  <div class="ab-hst" style="background-image:linear-gradient(160deg,rgba(221,24,96,.88),rgba(179,18,76,.9)),url('{root}assets/img/live/about-og-summit-sunrise.webp')">
    <div class="counter">
      <h2 id="h-hst"><span class="ab-w">HST =</span> <span class="ab-w"><b>H</b>igher,</span> <span class="ab-w"><b>S</b>tronger,</span> <span class="ab-w"><b>T</b>ogether</span></h2>
      <p>HST Medical's philosophy has evolved through the years. Today it stands for Higher, Stronger, Together: everyone's aspiration to go higher, be stronger and get together to do great things for the world.</p>
    </div>
  </div>
  <div class="counter ab-values">{values_html}</div>
</section>

<section class="band ab-pursuit" aria-labelledby="h-pursuit">
  <div class="counter ab-split">
    <div class="ab-text" data-rv>
      <h2 id="h-pursuit">The pursuit of health</h2>
      <p>Health is a universal pursuit, and HST Medical grew from the aspiration to provide the best of East and West in integrative supplements for everyone's journey of health.</p>
      <div class="ab-duo">
        <span class="ab-duo-i">{icon('leaf', 'ic ab-draw')}<b>Traditional Chinese Medicine</b></span>
        <span class="ab-duo-plus" aria-hidden="true">+</span>
        <span class="ab-duo-i">{icon('flask', 'ic ab-draw')}<b>Western pharmacology</b></span>
      </div>
      <p>The company brings these professionals together to formulate health products that are easy and affordable to reach, anywhere in the world: pain relief balm, kids' vitamins, immunity support for colds and flu, joint support, beauty support and much more.</p>
      <ul class="ab-points">
        <li>{IC['tick']}<span>Ingredients tested for authenticity, finished products verified for safety</span></li>
        <li>{IC['tick']}<span>Made under GMP, with Halal-certified and vegan options</span></li>
        <li>{IC['tick']}<span>On the shelf at Guardian, Watsons and NHGP pharmacies</span></li>
      </ul>
    </div>
    <figure class="ab-collage" data-rv style="--d:120ms">{img('about-what-is-hst-products.webp')}</figure>
  </div>
</section>

<section class="band ab-make" aria-labelledby="h-make">
  <div class="counter">
    <div class="ab-head"><h2 id="h-make">What we make</h2><p>Four brands, {n_products} products across {n_ranges} ranges, formulated by pharmacists and TCM physicians and made under GMP.</p></div>
    <div class="ab-brands">{brands_html}</div>
  </div>
</section>

<section class="band ab-heritage2" aria-labelledby="h-heritage">
  <div class="counter">
    <div class="ab-her-head">
      <h2 id="h-heritage">A heritage that began in 1930</h2>
      <p>The name is a tribute to Heng Say Tong, the medical hall established by the family of the company's co-founders. HST Medical Pte Ltd was incorporated in 1994 and draws on nearly a century of heritage in healthcare.</p>
    </div>
    <ol class="tline ab-journey">{ctx['story_journey'](root)}</ol>
  </div>
</section>

<section class="band ab-kowa" aria-labelledby="h-kowa">
  <div class="counter ab-kowa-grid">
    <figure class="ab-kowa-photo" data-rv>
      <div class="ab-kowa-frame">{img('kowa-joined-banner.webp')}</div>
      <figcaption>Management and staff from Kowa and HST Medical commemorate the acquisition signing ceremony.</figcaption>
    </figure>
    <div class="ab-kowa-copy" data-rv style="--d:140ms">
      <h2 id="h-kowa">Part of Kowa Pharmaceutical Asia</h2>
      <p>Since 29 May 2026 HST Medical has been part of Kowa Pharmaceutical Asia Pte. Ltd., within the Japanese Kowa group, whose consumer brands include Vantelin and Three Dimension Mask.</p>
      <ol class="ab-tree" aria-label="Group structure">
        <li><b>Kowa group</b><span>Japan</span></li>
        <li><b>Kowa Pharmaceutical Asia Pte. Ltd.</b><span>Parent company since 29 May 2026</span></li>
        <li><b>HST Medical Pte Ltd</b><span>Incorporated 1994, heritage since 1930</span></li>
      </ol>
      <a class="btn btn-quiet" href="{KOWA_NEWS}" target="_blank" rel="noopener">Read the announcement {arrow}</a>
    </div>
  </div>
</section>

<section class="band ab-homeband" aria-labelledby="h-home">
  <div class="counter">
    <div class="ab-head"><h2 id="h-home">Home of <span class="ab-nw">Rheuma-Salve®</span> and <span class="ab-nw">Zoo-Vite®</span></h2></div>
    <div class="ab-spots">
      <article class="ab-spot ab-spot-rs ab-lift" data-rv>
        <ul class="ab-formats" aria-label="Rheuma-Salve formats">{formats}</ul>
        <h3>Rheuma-Salve®: a format for each pain</h3>
        <p>Backache, sprains and strains, arthritis, rheumatism or other joint pain: the Rheuma-Salve® range has a format for each, from the balm, liniment and crème to the cooling patch, with travel packs too.</p>
        <a class="btn btn-quiet" href="{root}shop/pain-relief/">Rheuma-Salve® range {arrow}</a>
      </article>
      <article class="ab-spot ab-spot-zoo ab-lift" data-rv style="--d:120ms">
        <div class="ab-zoo-vis">
          <a class="ab-sassy" href="{SASSY}" target="_blank" rel="noopener" aria-label="Read the Sassy Mama feature (opens in a new tab)">{img('about-sassy-mama-badge-2020.webp')}</a>
          <span class="ab-zoo-packs" aria-hidden="true">{cut('zoo-vite-lutein-jelly', 'z1')}{cut('zoo-vite-elderberry-gummies', 'z2')}</span>
        </div>
        <h3>Zoo-Vite®: featured by Sassy Mama</h3>
        <p>Zoo-Vite® kids' vitamins were featured by Sassy Mama in 2020: <a href="{SASSY}" target="_blank" rel="noopener">Picky eaters? Why multivitamins can help fill your kid's nutrient gap</a>.</p>
        <a class="btn btn-quiet" href="{root}shop/kids/">Zoo-Vite® for kids {arrow}</a>
      </article>
    </div>
  </div>
</section>

<section class="band ab-awardsx-band" aria-labelledby="h-awards">
  <div class="counter">
    <div class="ab-head"><h2 id="h-awards">Award-winning</h2><p>Recognised by Beauty Insider readers and by Guardian in 2024.</p></div>
    <div class="ab-awardsx">{awards_html}</div>
    <p class="small ab-note">Award artwork as published on hstmedical.com.</p>
  </div>
</section>

<section class="band ab-resell" aria-labelledby="h-resell">
  <div class="counter">
    <div class="ab-cta-card" data-rv>
      <div class="ab-cta-copy">
        <h2 id="h-resell">Be an entrepreneur. Join us as a reseller.</h2>
        <p>Sell HST Medical products and buy from us in bulk: pharmacies, clinics, TCM halls and online sellers are welcome.</p>
        <div class="ab-ctas"><a class="btn btn-light" href="{root}resellers/">Become a reseller {arrow}</a></div>
      </div>
      <div class="ab-cta-packs" aria-hidden="true">{cut('rheuma-salve-balm', 'k1')}{cut('boost-immune', 'k2')}{cut('zoo-vite-multivitamin-gummies', 'k3')}</div>
    </div>
  </div>
</section>

<section class="band ab-visit" aria-labelledby="h-find">
  <div class="counter ab-visit-grid">
    <div class="ab-visit-copy" data-rv>
      <h2 id="h-find">Find us</h2>
      <address class="ab-contact">
        <span class="ab-ci">{icon('pin')}<span><b>HST Medical Pte Ltd</b>152 Paya Lebar Road #02-06, Citipoint Industrial Complex, Singapore 409020</span></span>
        <span class="ab-ci">{icon('phone')}<a href="tel:+6565365108">+65 6536 5108 ext 816</a></span>
        <span class="ab-ci">{icon('mail')}<a href="mailto:contact@hstmedical.com">contact@hstmedical.com</a></span>
      </address>
      <div class="ab-ctas"><a class="btn btn-stamp" href="{MAP_DIR}" target="_blank" rel="noopener">Get directions {arrow}</a><a class="btn btn-quiet" href="tel:+6565365108">Call us</a></div>
    </div>
    {map_embed('HST Medical Pte Ltd, 152 Paya Lebar Road, Singapore')}
  </div>
</section>
{TAIL_JS}
</main>"""
