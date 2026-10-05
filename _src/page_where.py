"""
Where to buy page (owned separately from build.py). build.py calls render(ctx, crumb) and wraps the result with
the site header/footer; styles in assets/css/where.css (linked only on this page). ctx keys: see build.page_ctx.

Layout (2026-10-05 redesign): hero with partner logo tiles -> store finder (retailer tablist, one retailer's stores
at a time, search across all retailers) -> buy online panel + "beware of fakes" note -> one two-column block
(visit HST Medical with map | stock HST Medical with the to-be-confirmed stockists).

Facts come from _src/where_data.json (stockists, delivery, awards, head office and the "beware of fakes" line,
copied from hstmedical.com; see its _source). If that file is missing the page falls back to the WordPress build's
site.json, and if both are missing it still builds (logo tiles and online panel only). Partner logos live in
assets/img/partners/ with a provenance sidecar per file. Classes are prefixed wtb-.
"""
import json, os, re
from urllib.parse import quote_plus

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_JSON = r"C:\Users\leuss\ClaudeWork\hst-wp\wordpress\wp-content\plugins\hst-medical-core\data\site.json"

# chain id -> (logo file, logo alt, what is stocked) used only when where_data.json is missing
FALLBACK_META = {
    "Guardian": ("guardian", "Guardian", "guardian.webp", "Guardian", "Rheuma-Salve®, Heritage® tonics and selected HST Medical® supplements in most outlets island-wide."),
    "Watsons": ("watsons", "Watsons", "watsons.webp", "Watsons", "Pain relief, cough and cold and kids' ranges. Check in-store availability for tonics."),
    "NHGP pharmacies": ("nhgp", "NHGP pharmacies", "nhg-polyclinics.webp", "NHG Polyclinics", "National Healthcare Group polyclinic pharmacies carry the core pain-relief and cough range."),
    "Essentials Pharmacy 益生药房": ("essentials", "Essentials Pharmacy", "essentials-pharmacy.webp", "Essentials Pharmacy", ""),
    "FairPrice Online": ("fairprice", "FairPrice Online", "fairprice.webp", "FairPrice", ""),
}
LOGO_WH = {"guardian.webp": (875, 226), "watsons.webp": (159, 36), "nhg-polyclinics.webp": (834, 240),
           "essentials-pharmacy.webp": (158, 45), "fairprice.webp": (164, 40)}
SHORT = {"guardian": "Guardian", "watsons": "Watsons", "nhgp": "NHGP", "essentials": "Essentials", "fairprice": "FairPrice"}
UNIT = {"nhgp": ("polyclinic pharmacy", "polyclinic pharmacies")}      # long form (panel heading)
UNIT_SHORT = {"nhgp": ("pharmacy", "pharmacies")}                         # short form (tiles and tabs)
DEFAULT_DELIVERY = {"free_above": 30.0, "fee": 1.99,
                    "overseas": "Express shipping to most countries (3 to 7 working days); standard shipping to selected countries including Malaysia, the Philippines and Vietnam."}
DEFAULT_HQ = {"name": "HST Medical Pte Ltd", "address": "152 Paya Lebar Road #02-06, Citipoint Industrial Complex, Singapore 409020",
              "tel": "+65 6536 5108", "ext": "816"}

SVG = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">%s</svg>'
I = {
    "pin": SVG % '<path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
    "phone": SVG % '<path d="M6.5 3.5h3l1.6 4.4-2.1 1.3a11.5 11.5 0 0 0 5.8 5.8l1.3-2.1 4.4 1.6v3a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 4.5 5.7a2 2 0 0 1 2-2.2z"/>',
    "ext": SVG % '<path d="M7 17 17 7"/><path d="M8 7h9v9"/>',
    "down": SVG % '<path d="M12 5v14"/><path d="m6 13 6 6 6-6"/>',
    "nav": SVG % '<path d="M20 4 3.5 10.6l7 2.9 2.9 7z"/>',
    "truck": SVG % '<path d="M3 6.5h10.5v9H3z"/><path d="M13.5 9.5h3.8l2.7 3v3h-6.5"/><circle cx="7" cy="17" r="1.7"/><circle cx="16.5" cy="17" r="1.7"/>',
    "globe": SVG % '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17"/><path d="M12 3.5c2.4 2.4 3.6 5.2 3.6 8.5s-1.2 6.1-3.6 8.5c-2.4-2.4-3.6-5.2-3.6-8.5s1.2-6.1 3.6-8.5z"/>',
    "shield": SVG % '<path d="M12 3.5 19 6v5.5c0 4.2-2.9 7.6-7 9-4.1-1.4-7-4.8-7-9V6z"/><path d="m8.8 12 2.2 2.2 4.3-4.4"/>',
    "alert": SVG % '<path d="M12 3.5 19 6v5.5c0 4.2-2.9 7.6-7 9-4.1-1.4-7-4.8-7-9V6z"/><path d="M12 8.2v4.6"/><path d="M12 16.2v.1"/>',
    "clock": SVG % '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "box": SVG % '<path d="M3.5 7.5 12 3.5l8.5 4v9l-8.5 4-8.5-4z"/><path d="M3.5 7.5 12 11.5l8.5-4M12 11.5v9"/>',
    "search": SVG % '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "x": SVG % '<path d="M7 7l10 10M17 7 7 17"/>',
}


def load_data():
    try:
        with open(os.path.join(HERE, "where_data.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        pass
    try:  # fallback: the WordPress build's capture of hstmedical.com
        with open(SITE_JSON, encoding="utf-8") as f:
            s = json.load(f)
        chains = []
        for c in s.get("stockists", []):
            cid, name, logo, alt, note = FALLBACK_META.get(c["chain"], (re.sub(r"\W+", "-", c["chain"].lower()).strip("-"), c["chain"], "", c["chain"], ""))
            chains.append({"id": cid, "chain": c["chain"], "name": name, "logo": logo, "logo_alt": alt, "note": note, "online": c.get("online", ""),
                           "stores": c.get("stores", []), "hotline": c.get("hotline", ""), "hotline_hours": c.get("hotline_hours", "")})
        return {"delivery": s.get("delivery", DEFAULT_DELIVERY), "chains": chains,
                "award": next((a for a in s.get("awards", []) if a.get("award") == "Guardian Awards 2024"), None)}
    except Exception:
        return {"delivery": DEFAULT_DELIVERY, "chains": [
            {"id": cid, "name": name, "logo": logo, "logo_alt": alt, "note": note, "online": "", "stores": []}
            for cid, name, logo, alt, note in list(FALLBACK_META.values())[:3]]}


def dial(t):
    return re.sub(r"[^\d+]", "", t)


def tel_links(tel, esc):
    return "".join('<a class="wtb-tel" href="tel:%s">%s<span>%s</span></a>' % (dial(t), I["phone"], esc(t))
                   for t in [x.strip() for x in (tel or "").split("/") if x.strip()])


def unit(cid, n, short=False):
    one, many = (UNIT_SHORT if short else UNIT).get(cid, ("store", "stores"))
    return one if n == 1 else many


def render(ctx, crumb):
    esc, IC, root, map_embed, RETAILERS_TBC = ctx["esc"], ctx["IC"], ctx["root"], ctx["map_embed"], ctx["RETAILERS_TBC"]
    D = load_data()
    chains = D.get("chains", [])
    dl = D.get("delivery", DEFAULT_DELIVERY)
    hq = D.get("hq") or DEFAULT_HQ
    with_stores = [c for c in chains if c.get("stores")]
    total = sum(len(c["stores"]) for c in with_stores)
    first = next((c["id"] for c in with_stores if c["id"] == "guardian"), with_stores[0]["id"] if with_stores else "")
    P = root + "assets/img/partners/"

    def logo(c, alt=None):
        f = c.get("logo")
        if not f or not os.path.exists(os.path.join(os.path.dirname(HERE), "assets", "img", "partners", f)):
            return '<span class="wtb-word">%s</span>' % esc(c["name"])  # text wordmark fallback
        w, h = LOGO_WH.get(f, (240, 80))
        return '<img src="%s%s" alt="%s" width="%d" height="%d" decoding="async">' % (P, f, esc(c.get("logo_alt", c["name"]) if alt is None else alt), w, h)

    # ---------------------------------------------------------------- hero + partner logo tiles
    tiles = ""
    for i, c in enumerate(chains):
        n = len(c.get("stores", []))
        if n:
            href, meta, tab = "#" + c["id"], '<b>%d</b> %s' % (n, unit(c["id"], n, True)), ' data-tab="%s"' % c["id"]
        else:
            href, meta, tab = "#online", "Online shop", ""
        tiles += f"""<li style="--i:{i}"><a class="wtb-tile" href="{href}"{tab}>
        <span class="wtb-tile-logo wtb-l-{c['id']}">{logo(c)}</span>
        <span class="wtb-tile-n">{meta}</span>
      </a></li>"""

    hero = f"""<section class="wtb-hero" aria-labelledby="h-where">
  <div class="counter">{crumb}
    <div class="wtb-hero-copy">
      <h1 id="h-where">Where to buy</h1>
      <p class="lead">On the shelf at Singapore's pharmacy chains, and online with island-wide delivery.</p>
      <div class="wtb-hero-acts"><a class="btn btn-stamp" href="#stores">Find a store {I['down']}</a><a class="btn btn-quiet" href="{root}shop/">Shop online {IC['arrow']}</a></div>
    </div>
    <ul class="wtb-logos" aria-label="Pharmacy partners">{tiles}</ul>
  </div>
</section>"""

    # ---------------------------------------------------------------- store finder: tablist, one panel per retailer, search
    award = D.get("award")
    L = {m["file"]: m for m in (ctx.get("live_manifest") or (lambda: []))()}
    tabs, panels = "", ""
    for c in with_stores:
        cid, n = c["id"], len(c["stores"])
        on = cid == first
        tabs += f"""<button class="wtb-tab" type="button" role="tab" id="tab-{cid}" aria-controls="{cid}" aria-selected="{'true' if on else 'false'}" tabindex="{0 if on else -1}">
        <span class="wtb-tab-logo wtb-l-{cid}">{logo(c)}</span>
        <span class="wtb-tab-n"><b data-n>{n}</b> <span data-u data-one="{unit(cid, 1, True)}" data-many="{unit(cid, 2, True)}">{unit(cid, n, True)}</span></span>
      </button>"""
        cards = ""
        for k, s in enumerate(c["stores"]):
            q = quote_plus("%s %s, %s" % (c["name"], s["name"], s["address"]))
            hay = ("%s %s %s %s" % (c["name"], c.get("chain", ""), s["name"], s["address"])).lower()
            cards += f"""<li class="wtb-store" style="--i:{min(k, 11)}" data-q="{esc(hay)}">
          <h4>{esc(s['name'])}</h4>
          <p class="wtb-addr">{esc(s['address'])}</p>
          <div class="wtb-acts"><div class="wtb-tels">{tel_links(s.get('tel'), esc)}</div><a class="wtb-dir" href="https://www.google.com/maps/search/?api=1&amp;query={q}" target="_blank" rel="noopener">{I['nav']}Directions<span class="sr-only"> to {esc(c['name'])} {esc(s['name'])} (opens Google Maps)</span></a></div>
        </li>"""
        facts = ""
        if c.get("hours"):
            facts += f'<p class="wtb-fact">{I["clock"]}<span>{esc(c["hours"])}</span></p>'
        if c.get("hotline"):
            hrs = (", " + esc(c["hotline_hours"])) if c.get("hotline_hours") else ""
            facts += f'<p class="wtb-fact">{I["phone"]}<span>Hotline <a href="tel:{dial(c["hotline"])}">{esc(c["hotline"])}</a>{hrs}</span></p>'
        if cid == "guardian" and award and "award-guardian-2024.webp" in L:
            m = L["award-guardian-2024.webp"]
            cap = "%s: winner, The %s" % (award.get("product_name", "Rheuma-Salve®"), award.get("award", "Guardian Awards 2024"))
            facts += f'<p class="wtb-fact wtb-award"><img src="{root}assets/img/live/award-guardian-2024.webp" alt="" width="{m.get("width", 1024)}" height="{m.get("height", 1024)}" loading="lazy" decoding="async"><span>{esc(cap)}</span></p>'
        shop = ""
        if c.get("online"):
            host = re.sub(r"^https?://(www\.)?", "", c["online"]).rstrip("/")
            label = "Shop on Shopee" if "shopee" in host else "Shop %s online" % SHORT.get(cid, c["name"])
            shop = f'<a class="btn btn-quiet wtb-shop" href="{esc(c["online"])}" target="_blank" rel="noopener">{label} {I["ext"]}<span class="sr-only"> ({esc(host)}, opens in a new tab)</span></a>'
        zh = f' <span lang="zh-Hans" class="wtb-zh">{esc(c["name_zh"])}</span>' if c.get("name_zh") else ""
        note = f'<p class="wtb-stocked">{esc(c["note"])}</p>' if c.get("note") else ""
        facts = f'<div class="wtb-facts-row">{facts}</div>' if facts else ""
        panels += f"""<div class="wtb-panel{'' if on else ' wtb-off'}" role="tabpanel" id="{cid}" aria-labelledby="tab-{cid}" data-name="{esc(c['name'])}" data-one="{unit(cid, 1)}" data-many="{unit(cid, 2)}">
      <div class="wtb-panel-head">
        <div class="wtb-panel-copy"><h3>{esc(c['name'])}{zh} <span class="wtb-h-n">{n} {unit(cid, n)}</span></h3>{note}{facts}</div>
        {shop}
      </div>
      <ul class="wtb-stores">{cards}</ul>
    </div>"""

    finder = ""
    if with_stores:
        names = [SHORT.get(c["id"], c["name"]) for c in with_stores]
        names = ", ".join(names[:-1]) + " and " + names[-1] if len(names) > 1 else names[0]
        finder = f"""<section class="wtb-finder" id="stores" aria-labelledby="h-stores">
  <div class="counter">
    <div class="wtb-finder-head wtb-rv">
      <div class="wtb-finder-copy"><h2 id="h-stores">Find a store</h2><p>{total} pharmacies and stores across {esc(names)}. Opening hours vary by outlet, so please call ahead for a specific product.</p></div>
      <div class="wtb-search" hidden><label for="wtb-q" class="sr-only">Search all stores by mall, area or postcode</label>{I['search']}<input id="wtb-q" type="search" placeholder="Search a mall, area or postcode" autocomplete="off" enterkeyhint="search" aria-controls="wtb-results"><button class="wtb-clear" type="button" hidden aria-label="Clear search">{I['x']}</button></div>
    </div>
    <div class="wtb-tabs wtb-rv" role="tablist" aria-label="Retailers">{tabs}</div>
    <div class="wtb-panels wtb-rv">
      {panels}
      <div class="wtb-results" id="wtb-results" hidden>
        <p class="wtb-status" id="wtb-status" role="status" aria-live="polite"></p>
        <div class="wtb-groups"></div>
        <div class="wtb-empty" hidden>{I['search']}
          <div><h3>No store matches <span class="wtb-empty-q"></span></h3>
          <p>Try a mall, an area or a postcode, such as Orchard, Jurong or 238801. Or order online with island-wide delivery.</p>
          <div class="wtb-empty-acts"><a class="btn btn-stamp" href="{root}shop/">{IC['bag']} Shop online</a><button class="btn btn-quiet wtb-reset" type="button">Clear search</button></div></div>
        </div>
      </div>
    </div>
  </div>
</section>"""

    # ---------------------------------------------------------------- buy online + beware of fakes
    by = ctx.get("BY_SLUG") or {}
    packs = "".join(f'<img class="wtb-pack k{k}" src="{root}assets/img/products/{by[s]["image"]}-thumb.webp" alt="" width="360" height="360" loading="lazy" decoding="async">'
                    for k, s in enumerate(["cough-alievaid-herbal-lintus", "rheuma-salve-balm", "zoo-vite-multivitamin-gummies"]) if s in by)
    free, fee = dl.get("free_above", 30.0), dl.get("fee", 1.99)
    overseas = dl.get("overseas", DEFAULT_DELIVERY["overseas"])
    ex = re.search(r"\(([^)]*working days)\)", overseas)
    online_links = "".join(f'<li><a class="wtb-mini" href="{esc(c["online"])}" target="_blank" rel="noopener">{logo(c, alt=c["name"])}<span class="sr-only"> online (opens in a new tab)</span></a></li>'
                           for c in chains if c.get("online") and c["id"] in ("guardian", "watsons", "fairprice", "essentials"))
    elsewhere = f'<div class="wtb-elsewhere wtb-rv"><p>Also sold online by</p><ul>{online_links}</ul></div>' if online_links else ""
    fakes = esc(D.get('fakes', 'Please check the e-shop URL to make sure you buy from the right shop.').replace('Beware of fakes! ', ''))
    online = f"""<section class="wtb-online-sec" id="online" aria-labelledby="h-online">
  <div class="counter">
    <div class="wtb-online wtb-rv">
      <div class="wtb-online-copy">
        <h2 id="h-online">Buy online, delivered</h2>
        <p class="wtb-online-lead">Order direct from HST Medical. Every pack ships from us, island-wide or overseas.</p>
        <ul class="wtb-perks">
          <li>{I['truck']}<span><b>Free Singapore delivery above S${free:.0f}</b>S${fee:.2f} for orders of S${free:.0f} and below</span></li>
          <li>{I['globe']}<span><b>Express overseas in {esc(ex.group(1)) if ex else '3 to 7 working days'}</b>Standard shipping to selected countries including Malaysia, the Philippines and Vietnam</span></li>
          <li>{I['shield']}<span><b>100% genuine, sent direct</b>Everything in our store is genuine HST Medical product</span></li>
        </ul>
        <a class="btn btn-stamp wtb-online-cta" href="{root}shop/">{IC['bag']} Shop online {IC['arrow']}</a>
      </div>
      <div class="wtb-packs" aria-hidden="true">{packs}</div>
    </div>
    {elsewhere}
    <aside class="wtb-fakes wtb-rv" aria-labelledby="h-fakes">{I['alert']}
      <div><h2 id="h-fakes">Beware of fakes</h2>
      <p>{fakes} Buy only from hstmedical.com or the authorised stockists on this page.</p></div>
    </aside>
  </div>
</section>"""

    # ---------------------------------------------------------------- visit HST Medical | stock HST Medical
    ext = (' <span class="wtb-ext-n">ext %s</span>' % esc(hq["ext"])) if hq.get("ext") else ""
    tbc = "".join('<li>%s</li>' % esc(r.replace(' (to confirm)', '')) for r in RETAILERS_TBC)
    tbc_html = f"""<div class="wtb-tbc"><h3>To be confirmed</h3><p>Stockists reported but not yet verified with HST Medical.</p><ul>{tbc}</ul></div>""" if tbc else ""
    more = f"""<section class="wtb-more" aria-label="Visit or stock HST Medical">
  <div class="counter wtb-more-grid">
    <div class="wtb-visit wtb-rv">{I['pin']}
      <h2>Visit HST Medical</h2>
      <address><b>{esc(hq['name'])}</b>{esc(hq['address'])}</address>
      <a class="wtb-tel wtb-hq-tel" href="tel:{dial(hq['tel'])}">{I['phone']}<span>{esc(hq['tel'])}{ext}</span></a>
      {map_embed('HST Medical Pte Ltd, 152 Paya Lebar Road, Singapore')}
    </div>
    <div class="wtb-trade wtb-rv">{I['box']}
      <h2>Stock HST Medical</h2>
      <p>Retailers, clinics and distributors order direct from HST Medical.</p>
      <a class="btn btn-stamp" href="{root}resellers/">Trade enquiries {IC['arrow']}</a>
      {tbc_html}
    </div>
  </div>
</section>"""

    return f"""
<main id="main" class="wtb">
{hero}
{finder}
{online}
{more}
</main>
<script>{SCRIPT}</script>"""


# tabs (one retailer at a time, arrow keys), search across every retailer (grouped results + empty state),
# hero tiles that open a retailer, and entrance reveals. Motion is skipped under prefers-reduced-motion.
SCRIPT = r"""(function () {
  var d = document, root = d.querySelector('.wtb'); if (!root) return;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finder = d.getElementById('stores');
  var tabs = [].slice.call(d.querySelectorAll('.wtb-tab'));
  var panels = tabs.map(function (t) { return d.getElementById(t.getAttribute('aria-controls')); });
  var results = d.getElementById('wtb-results'), status = d.getElementById('wtb-status');
  var groups = results && results.querySelector('.wtb-groups'), empty = results && results.querySelector('.wtb-empty');
  var wrap = d.querySelector('.wtb-search'), box = d.getElementById('wtb-q'), clearBtn = d.querySelector('.wtb-clear');
  var cur = 0, lastKey = null;
  var plural = function (el, n) { return el.getAttribute(n === 1 ? 'data-one' : 'data-many'); };
  var searching = function () { return !!(box && box.value.trim()); };
  var play = function (el) { if (reduce || !el) return; el.classList.remove('wtb-enter'); void el.offsetWidth; el.classList.add('wtb-enter'); };
  var setCount = function (t, n, of) {
    var b = t.querySelector('[data-n]'), u = t.querySelector('[data-u]');
    b.textContent = of == null ? n : n + ' of ' + of; u.textContent = plural(u, of == null ? n : of);
    t.classList.toggle('is-zero', of != null && n === 0);
  };
  function select(i, focus, quiet) {
    if (!tabs[i]) return;
    var changed = i !== cur; cur = i;
    tabs.forEach(function (t, k) { var on = k === i; t.setAttribute('aria-selected', on ? 'true' : 'false'); t.tabIndex = on ? 0 : -1; });
    panels.forEach(function (p, k) { p.classList.remove('wtb-off'); p.hidden = k !== i || searching(); });
    if (focus) tabs[i].focus();
    if (changed && !quiet && !searching()) play(panels[i]);
  }
  function exitSearch() {
    if (!box || !searching()) return;
    box.value = ''; run(true);
  }
  function run(quiet) {
    if (!box) return;
    var raw = box.value.trim(), words = raw.toLowerCase().split(/\s+/).filter(Boolean);
    if (clearBtn) clearBtn.hidden = !words.length;
    if (!words.length) {
      if (finder) finder.classList.remove('is-search');
      results.hidden = true; groups.innerHTML = ''; status.textContent = ''; lastKey = null;
      tabs.forEach(function (t, k) { setCount(t, panels[k].querySelectorAll('.wtb-store').length); });
      select(cur, false, true); if (!quiet) play(panels[cur]);
      return;
    }
    if (finder) finder.classList.add('is-search');
    panels.forEach(function (p) { p.hidden = true; });
    var total = 0, hit = [], key = [], frag = d.createDocumentFragment();
    panels.forEach(function (p, k) {
      var cards = [].slice.call(p.querySelectorAll('.wtb-store'));
      var m = cards.filter(function (s) { var h = s.getAttribute('data-q'); return words.every(function (w) { return h.indexOf(w) > -1; }); });
      setCount(tabs[k], m.length, cards.length);
      if (!m.length) return;
      total += m.length; hit.push(p.getAttribute('data-name'));
      var g = d.createElement('div'); g.className = 'wtb-group';
      g.innerHTML = '<div class="wtb-group-head"><h3></h3><span></span></div><ul class="wtb-stores"></ul>';
      g.querySelector('h3').textContent = p.getAttribute('data-name');
      g.querySelector('span').textContent = m.length + ' of ' + cards.length + ' ' + plural(p, cards.length);
      var ul = g.querySelector('ul');
      m.forEach(function (s, j) { var c = s.cloneNode(true); c.style.setProperty('--i', Math.min(j, 11)); ul.appendChild(c); key.push(k + ':' + cards.indexOf(s)); });
      frag.appendChild(g);
    });
    var q = '\u201c' + raw + '\u201d';
    if (total) {
      var at = hit.length > 1 ? hit.slice(0, -1).join(', ') + ' and ' + hit[hit.length - 1] : hit[0];
      status.textContent = total + (total === 1 ? ' store matches ' : ' stores match ') + q + ' at ' + at + '.';
    } else {
      status.textContent = 'No store matches ' + q + '.';
      empty.querySelector('.wtb-empty-q').textContent = q;
    }
    results.hidden = false;
    var k2 = key.join('|');
    if (k2 === lastKey) return;            // same matches: keep the cards still while typing
    lastKey = k2;
    groups.innerHTML = ''; groups.appendChild(frag);
    empty.hidden = total > 0;
    play(results);
  }
  if (tabs.length) {
    tabs.forEach(function (t, k) {
      t.addEventListener('click', function () { exitSearch(); select(k); });
      t.addEventListener('keydown', function (e) {
        var n = tabs.length, j = null;
        if (e.key === 'ArrowRight') j = (k + 1) % n; else if (e.key === 'ArrowLeft') j = (k - 1 + n) % n;
        else if (e.key === 'Home') j = 0; else if (e.key === 'End') j = n - 1;
        if (j === null) return;
        e.preventDefault(); exitSearch(); select(j, true);
      });
    });
    var h = (location.hash || '').slice(1), hi = panels.map(function (p) { return p.id; }).indexOf(h);
    cur = Math.max(0, tabs.map(function (t) { return t.getAttribute('aria-selected'); }).indexOf('true'));
    select(hi > -1 ? hi : cur, false, true);
    [].forEach.call(d.querySelectorAll('.wtb-tile[data-tab]'), function (a) {
      a.addEventListener('click', function (e) {
        var k = panels.map(function (p) { return p.id; }).indexOf(a.getAttribute('data-tab')); if (k < 0) return;
        e.preventDefault(); exitSearch(); select(k);
        finder.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
        try { tabs[k].focus({ preventScroll: true }); } catch (x) {}
        if (history.replaceState) history.replaceState(null, '', '#' + panels[k].id);
      });
    });
  }
  if (wrap && box && results) {
    wrap.hidden = false;
    box.addEventListener('input', function () { run(); });
    box.addEventListener('search', function () { run(); });
    if (clearBtn) clearBtn.addEventListener('click', function () { box.value = ''; run(); box.focus(); });
    var reset = results.querySelector('.wtb-reset');
    if (reset) reset.addEventListener('click', function () { box.value = ''; run(); box.focus(); });
  }
  if (!reduce && 'IntersectionObserver' in window) {
    var vh = innerHeight;
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        io.unobserve(e.target); e.target.classList.remove('wtb-pre'); e.target.classList.add('wtb-go');
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
    [].forEach.call(d.querySelectorAll('.wtb-rv'), function (el) {
      if (el.getBoundingClientRect().top > vh * 0.92) { el.classList.add('wtb-pre'); io.observe(el); }
    });
  }
})();"""
