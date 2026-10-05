/* HST Medical — Dispensing Counter. Progressive enhancement, no dependencies (~6 KB).
   Without JS: every category is a real URL, pack sizes are native radios, accordions are <details>.
   With JS: mobile nav, pack-size → label reprint, bag (localStorage demo of the EasyCart cart),
   steppers, undo, store filter/search with empty state, gated checkout, inline validation, aria-live. */
(function () {
  'use strict';
  var d = document, KEY = 'hst-bag', live = d.getElementById('live');
  function say(t) { if (live) { live.textContent = ''; setTimeout(function () { live.textContent = t; }, 30); } }
  function money(n) { return 'S$' + n.toFixed(2); }
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* header stuck state (style it via .scrolled .site-header; never change its height) */
  var root_ = d.documentElement, onScroll = function () { root_.classList.toggle('scrolled', window.scrollY > 10); };
  onScroll(); addEventListener('scroll', onScroll, { passive: true });

  /* mobile nav */
  var tg = d.querySelector('.nav-toggle'), nav = d.getElementById('site-nav');
  if (tg && nav) d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && nav.classList.contains('open')) { nav.classList.remove('open'); tg.setAttribute('aria-expanded', 'false'); tg.focus(); } });
  if (tg && nav) tg.addEventListener('click', function () {
    var open = nav.classList.toggle('open'); tg.setAttribute('aria-expanded', open);
  });
  /* the page behind an open menu is dimmed: a tap there closes the menu instead of following whatever link lies underneath */
  if (tg && nav) d.addEventListener('click', function (e) {
    if (!nav.classList.contains('open') || e.target.closest('.site-header, .mbar')) return;
    nav.classList.remove('open'); tg.setAttribute('aria-expanded', 'false'); e.preventDefault(); e.stopPropagation();
  }, true);

  /* bag storage */
  function load() { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; } }
  function save(c) { try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) { say('Your browser blocks storage, so the bag cannot be kept between pages.'); } paint(); }
  function paint() {
    var n = load().reduce(function (s, i) { return s + i.qty; }, 0);
    d.querySelectorAll('.bag .count, .mbar-bag .count').forEach(function (el) { el.textContent = n; el.hidden = !n; });
    d.querySelectorAll('.bag').forEach(function (el) { el.setAttribute('aria-label', 'Bag, ' + n + ' item' + (n === 1 ? '' : 's')); });
  }
  paint();
  window.HSTBag = { load: load, save: save, paint: paint, say: say };

  /* pack size → reprint the label */
  var pdp = d.querySelector('[data-pdp]');
  if (pdp) {
    var price = pdp.querySelector('[data-price-out]'), code = pdp.querySelector('[data-code-out]'), size = pdp.querySelector('[data-size-out]');
    var add = pdp.querySelector('[data-add]'), enquire = pdp.querySelector('[data-enquire]');
    function reprint(r) {
      var p = parseFloat(r.getAttribute('data-price')), has = !isNaN(p) && p > 0;
      pdp.classList.remove('printing'); void pdp.offsetWidth; if (!reduce) pdp.classList.add('printing');
      d.querySelectorAll('[data-price-out]').forEach(function (el) { el.textContent = has ? money(p) : 'Price on request'; });
      if (code) code.textContent = 'Item ' + r.getAttribute('data-code');
      if (size) size.textContent = r.getAttribute('data-size');
      if (add) {
        add.setAttribute('data-price', has ? p : 0); add.setAttribute('data-variant', r.getAttribute('data-size')); add.setAttribute('data-code', r.getAttribute('data-code'));
        add.hidden = !has;
      }
      if (enquire) enquire.hidden = has;
      say(r.getAttribute('data-size') + ' selected, ' + (has ? money(p) : 'price on request'));
    }
    pdp.querySelectorAll('.pack input').forEach(function (r) { r.addEventListener('change', function () { reprint(r); }); });
    var checked = pdp.querySelector('.pack input:checked'); if (checked) { /* sync without animation */ var c = pdp.classList.contains('printing'); reprint(checked); pdp.classList.remove('printing'); if (c) pdp.classList.add('printing'); }
  }

  /* steppers */
  d.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-step]'); if (!b) return;
    var box = b.closest('.qty'), inp = box && box.querySelector('input'); if (!inp) return;
    var v = Math.max(1, Math.min(99, (parseInt(inp.value, 10) || 1) + (+b.getAttribute('data-step'))));
    inp.value = v; inp.dispatchEvent(new Event('change', { bubbles: true }));
  });
  d.addEventListener('change', function (ev) {
    var inp = ev.target; if (!inp.matches('.qty input')) return;
    var v = Math.max(1, Math.min(99, parseInt(inp.value, 10) || 1)); inp.value = v;
    var id = inp.getAttribute('data-line'); if (!id) return;
    var c = load(); c.forEach(function (i) { if (i.id === id) i.qty = v; }); save(c); renderBag();
  });

  /* add to bag */
  d.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-add]'); if (!b || b.hidden) return;
    ev.preventDefault();
    var p = parseFloat(b.getAttribute('data-price')) || 0; if (!p) { say('This pack size is price on request.'); return; }
    var q = 1, qi = d.getElementById('qty'); if (qi && b.hasAttribute('data-from-pdp')) q = Math.max(1, parseInt(qi.value, 10) || 1);
    var variant = b.getAttribute('data-variant') || '', id = b.getAttribute('data-id') + (variant ? '|' + variant : ''), c = load();
    var hit = c.filter(function (i) { return i.id === id; })[0];
    if (hit) hit.qty += q; else c.push({ id: id, name: b.getAttribute('data-name'), variant: variant, code: b.getAttribute('data-code') || '', price: p, img: b.getAttribute('data-img'), url: b.getAttribute('data-url'), qty: q });
    save(c); fly(b);
    var t = b.innerHTML; b.classList.add('is-added'); b.innerHTML = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg> In your bag';
    setTimeout(function () { b.classList.remove('is-added'); b.innerHTML = t; }, 1600);
    var n = c.reduce(function (s, i) { return s + i.qty; }, 0);
    say(b.getAttribute('data-name') + (variant ? ', ' + variant : '') + ' added. ' + n + ' item' + (n === 1 ? '' : 's') + ' in your bag.');
  });

  /* bag page */
  var lines = d.getElementById('bag-lines'), root = lines ? (lines.getAttribute('data-root') || '') : '';
  var undo = null;
  function renderBag() {
    if (!lines) return;
    var c = load(), sub = 0, FREE = 30, SHIP = 1.99; /* live store: free above S$30, S$1.99 at S$30 and below */
    if (!c.length) {
      lines.innerHTML = '<div class="empty bag-empty"><svg class="ic bag-empty-ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5.5 8.5h13l-1 11.5h-11z"/><path d="M9 8.5V7a3 3 0 0 1 6 0v1.5"/></svg><b>Your bag is empty.</b><span>Start with what you need today.</span><span class="bag-empty-ctas"><a class="btn btn-stamp" href="' + root + 'shop/pain-relief/">Pain relief</a><a class="btn btn-quiet" href="' + root + 'shop/cough-cold-flu/">Cough and cold</a><a class="btn btn-quiet" href="' + root + 'shop/">All products</a></span></div>';
    } else {
      lines.innerHTML = c.map(function (i) {
        sub += i.price * i.qty;
        return '<div class="line"><img src="' + root + i.img + '" alt="" width="72" height="72"><div><a class="name" href="' + root + i.url + '">' + i.name + '</a><span class="meta">' + (i.variant ? i.variant + ' · ' : '') + money(i.price) + ' each' + (i.code ? ' · Item ' + i.code : '') + '</span><button class="rm" data-rm="' + i.id + '"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 7h14M10 7V5h4v2M7 7l1 12h8l1-12"/></svg>Remove</button></div>' +
          '<div class="qty" aria-label="Quantity for ' + i.name + '"><button type="button" data-step="-1" aria-label="Decrease">−</button><input type="number" min="1" max="99" value="' + i.qty + '" data-line="' + i.id + '" aria-label="Quantity"><button type="button" data-step="1" aria-label="Increase">+</button></div><span class="sum">' + money(i.price * i.qty) + '</span></div>';
      }).join('');
    }
    var ship = sub && sub <= FREE ? SHIP : 0;
    d.querySelectorAll('[data-sub]').forEach(function (e) { e.textContent = money(sub); });
    d.querySelectorAll('[data-ship]').forEach(function (e) { e.textContent = sub ? (ship ? money(ship) : 'Free') : '—'; });
    d.querySelectorAll('[data-total]').forEach(function (e) { e.textContent = money(sub + ship); });
    d.querySelectorAll('[data-free]').forEach(function (e) { e.textContent = !sub ? 'Free delivery on orders above ' + money(FREE) + '.' : (sub > FREE ? 'You have free island-wide delivery.' : 'Add ' + money(Math.max(0.01, FREE - sub + 0.01)) + ' more for free delivery.'); });
    d.querySelectorAll('.meter i').forEach(function (e) { e.style.transform = 'scaleX(' + Math.min(1, sub / FREE) + ')'; });
    d.querySelectorAll('[data-needs-items]').forEach(function (e) { e.toggleAttribute('disabled', !c.length); e.setAttribute('aria-disabled', !c.length); });
  }
  renderBag();
  d.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-rm]'); if (!b) return;
    var c = load(), id = b.getAttribute('data-rm'), removed = c.filter(function (i) { return i.id === id; })[0];
    save(c.filter(function (i) { return i.id !== id; })); renderBag();
    var toast = d.getElementById('toast'); if (!toast || !removed) return;
    toast.querySelector('span').textContent = removed.name + ' removed.'; toast.hidden = false; say(removed.name + ' removed. Undo available.');
    clearTimeout(undo); undo = setTimeout(function () { toast.hidden = true; }, 6000);
    toast.querySelector('button').onclick = function () { var c2 = load(); c2.push(removed); save(c2); renderBag(); toast.hidden = true; say(removed.name + ' restored.'); };
  });

  /* store filter + search */
  var grid = d.getElementById('shop-grid');
  if (grid) {
    var tabs = d.querySelectorAll('.filters [data-cat]'), q = d.getElementById('q'), out = d.getElementById('result'), emptyEl = d.getElementById('shop-empty'), cat = 'all';
    function fold(s) { return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
    function apply() {
      var term = fold(q && q.value || '').trim(), n = 0;
      grid.querySelectorAll('.plabel').forEach(function (p) {
        var ok = (cat === 'all' || p.getAttribute('data-cat') === cat) && (!term || fold(p.getAttribute('data-search')).indexOf(term) > -1);
        p.hidden = !ok; if (ok) n++;
      });
      var total = grid.querySelectorAll('.plabel').length;
      if (out) out.textContent = 'Showing ' + n + ' of ' + total + ' products' + (term ? ' for “' + (q.value) + '”' : '');
      if (emptyEl) { emptyEl.hidden = n > 0; if (!n) emptyEl.querySelector('b').textContent = 'No match for “' + q.value + '”.'; }
    }
    tabs.forEach(function (t) { t.addEventListener('click', function (e) {
      e.preventDefault(); tabs.forEach(function (x) { x.setAttribute('aria-pressed', 'false'); }); t.setAttribute('aria-pressed', 'true'); cat = t.getAttribute('data-cat'); apply();
      if (history.replaceState) history.replaceState(null, '', cat === 'all' ? location.pathname : '?cat=' + cat);
    }); });
    if (q) q.addEventListener('input', apply);
    var m = location.search.match(/cat=([\w-]+)/); if (m) tabs.forEach(function (t) { if (t.getAttribute('data-cat') === m[1]) t.click(); });
    var qs = location.search.match(/q=([^&]+)/); if (qs && q) { q.value = decodeURIComponent(qs[1].replace(/\+/g, ' ')); }
    apply();
  }

  /* forms: inline validation + demo success; checkout: gated steps */
  function validate(scope) {
    var ok = true;
    scope.querySelectorAll('input,select,textarea').forEach(function (f) {
      if (f.closest('[hidden]')) return;
      var bad = !f.checkValidity();
      f.setAttribute('aria-invalid', bad ? 'true' : 'false');
      var wrap = f.closest('.lbl') || f.closest('label'); if (wrap) wrap.classList.toggle('is-error', bad);
      if (bad && ok) { ok = false; f.focus(); }
    });
    return ok;
  }
  d.querySelectorAll('form[data-demo]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!validate(f)) { say('Please complete the highlighted fields.'); return; }
      f.classList.add('sent'); var okEl = f.querySelector('.ok'); if (okEl) { okEl.scrollIntoView({ block: 'nearest' }); say(okEl.textContent); }
    });
    f.addEventListener('input', function (e) { var t = e.target; if (t.getAttribute('aria-invalid') === 'true' && t.checkValidity()) { t.setAttribute('aria-invalid', 'false'); var w = t.closest('.lbl') || t.closest('label'); if (w) w.classList.remove('is-error'); } });
  });
  var steps = d.querySelectorAll('.step');
  if (steps.length) {
    var bar = d.querySelectorAll('.steps-bar li');
    function show(i) {
      steps.forEach(function (s, k) { s.hidden = k !== i; });
      bar.forEach(function (b, k) { b.classList.toggle('done', k < i); if (k === i) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current'); });
      if (i > 0 || show.ran) { steps[i].querySelector('h2').setAttribute('tabindex', '-1'); steps[i].querySelector('h2').focus(); say('Step ' + (i + 1) + ' of ' + steps.length + ': ' + steps[i].querySelector('h2').textContent); }
      show.ran = true;
    }
    d.addEventListener('click', function (ev) {
      var n = ev.target.closest('[data-next]'), p = ev.target.closest('[data-prev]');
      if (n) { var cur = [].indexOf.call(steps, n.closest('.step')); if (validate(steps[cur])) show(cur + 1); else say('Please complete the highlighted fields before continuing.'); }
      if (p) { show([].indexOf.call(steps, p.closest('.step')) - 1); }
    });
    show(0);
  }

  /* ---- image motion layer ----
     fly(): the pack you added flies to the Bag on an arc and the count pops (reduced motion: count pop only).
     Reveal: product lists below the fold rise in and their packshots develop from a blur, staggered per batch.
     Tilt: packshots in cards and shop-by-need tiles turn toward the pointer. Zoom: product page lens. */
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  function fly(b) {
    var bag = d.querySelector('.bag'); if (!bag) return;
    bag.classList.remove('bump'); void bag.offsetWidth; bag.classList.add('bump');
    var host = b.closest('.hs-card, .plabel, tr, .pdp, .line'), src = null;
    if (host && host.classList.contains('hs-card')) src = d.querySelector('.hs-pack.is-on img');
    else if (host) src = host.querySelector('.img img, .thumb, .pdp-pack img, img');
    if (reduce || !src || !src.animate) return;
    var r = src.getBoundingClientRect(), t = bag.getBoundingClientRect();
    if (!r.width || r.bottom < 0 || r.top > innerHeight) return;
    var s = Math.min(120, Math.max(r.width, r.height)), im = d.createElement('img');
    im.src = src.currentSrc || src.src; im.alt = ''; im.className = 'fly';
    im.style.width = im.style.height = s + 'px';
    d.body.appendChild(im);
    var x0 = r.left + r.width / 2 - s / 2, y0 = r.top + r.height / 2 - s / 2, x1 = t.left + t.width / 2 - s / 2, y1 = t.top + t.height / 2 - s / 2;
    var lift = Math.min(160, Math.abs(y0 - y1) * 0.35 + 60);
    im.animate([
      { transform: 'translate(' + x0 + 'px,' + y0 + 'px) scale(1) rotate(0deg)', opacity: 1 },
      { transform: 'translate(' + (x0 + (x1 - x0) * 0.45) + 'px,' + (Math.min(y0, y1) - lift) + 'px) scale(.7) rotate(-14deg)', opacity: 1, offset: 0.45 },
      { transform: 'translate(' + x1 + 'px,' + y1 + 'px) scale(.12) rotate(8deg)', opacity: 0.2 }
    ], { duration: 820, easing: 'cubic-bezier(.45,0,.2,1)' }).finished.then(function () {
      im.remove();
      bag.animate([{ transform: 'scale(1)' }, { transform: 'scale(1.12)' }, { transform: 'scale(1)' }], { duration: 380, easing: 'cubic-bezier(.16,1,.3,1)' });
    }, function () { im.remove(); });
  }

  if (!reduce && 'IntersectionObserver' in window) {
    var vh = innerHeight, targets = d.querySelectorAll('.labels > .plabel, .compare tbody tr, .counters > a, .shelf > a, .notes > a, #bag-lines > .line, .mcard, .bento > a, .assure li, .award, .kowa-card, .kowa-media, .kowa-copy, .map, .filters .cat, .cat-stage');
    var io = new IntersectionObserver(function (es) {
      var k = 0;
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target; io.unobserve(el);
        el.style.setProperty('--rv', Math.min(k++ * 70, 420) + 'ms');
        el.classList.add('in');
        setTimeout(function () { el.classList.remove('rv', 'in'); el.style.removeProperty('--rv'); }, 1700);
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.1 });
    targets.forEach(function (el) {
      var r = el.getBoundingClientRect();
      /* items parked off-screen to the right (filter rail, matcher cards, swipe rows) are never hidden: nothing would reveal them until the swipe, and the rail would look like it had two items */
      if (r.top > vh * 0.94 && r.left < innerWidth - 4 && r.right > 4 && !el.closest('[hidden]')) { el.classList.add('rv'); io.observe(el); }
    });
  }

  if (fine && !reduce) {
    d.querySelectorAll('.plabel .img, .counters .tile').forEach(function (el) {
      var raf = 0, ex = 0, ey = 0;
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect(); ex = (e.clientX - r.left) / r.width * 2 - 1; ey = (e.clientY - r.top) / r.height * 2 - 1;
        if (!raf) raf = requestAnimationFrame(function () { raf = 0; el.style.setProperty('--tx', ex.toFixed(3)); el.style.setProperty('--ty', ey.toFixed(3)); });
      });
      el.addEventListener('pointerleave', function () { el.style.removeProperty('--tx'); el.style.removeProperty('--ty'); });
    });
  }

  /* symptom matcher: pick a need, the matching card lifts and the rest step back */
  d.querySelectorAll('[data-matcher]').forEach(function (m) {
    var all = m.querySelector('.need-all'), box = m.querySelector('.mcards');
    function pickNeed(slug) {
      m.querySelectorAll('.need:not(.need-all)').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-need') === slug ? 'true' : 'false'); });
      m.classList.toggle('has-pick', !!slug); if (all) all.hidden = !slug;
      var hit = null;
      m.querySelectorAll('.mcard').forEach(function (c) { var on = c.getAttribute('data-card') === slug; c.classList.toggle('is-match', on); if (on) hit = c; });
      if (hit && box && box.scrollWidth > box.clientWidth + 4) box.scrollTo({ left: hit.offsetLeft - box.offsetLeft - parseFloat(getComputedStyle(box).paddingLeft || 0), behavior: reduce ? 'auto' : 'smooth' });
      if (hit) say('Best match: ' + hit.querySelector('h3').textContent + '.');
    }
    m.addEventListener('click', function (e) {
      var b = e.target.closest('.need'); if (!b) return;
      var slug = b.getAttribute('data-need');
      pickNeed(b.getAttribute('aria-pressed') === 'true' ? '' : slug);
    });
  });

  /* phones: bottom tab bar marks the current section; the product page buy bar appears once the real button scrolls away */
  var here = location.pathname.replace(/index\.html$/, '');
  d.querySelectorAll('.mbar a').forEach(function (a) {
    var k = a.getAttribute('data-mb'), p = a.pathname.replace(/index\.html$/, '');
    var on = k === 'search' ? false : (k === 'home' ? here === p : here.indexOf(p) === 0 && p !== '/' && !(k === 'shop' && /\/cart\//.test(here)));
    if (k === 'home' && here === p) on = true;
    if (on) a.setAttribute('aria-current', 'page');
  });
  if (/[?&]focus=search\b/.test(location.search)) { var qf = d.getElementById('q'); if (qf) setTimeout(function () { qf.focus(); }, 300); }
  var bb = d.querySelector('[data-buybar]'), mainBuy = d.querySelector('.pdp2 .buy');
  if (bb && mainBuy && 'IntersectionObserver' in window) {
    bb.hidden = false;
    /* shown once the real buy row has scrolled off the top, hidden again at the top of the page (a jump such as the footer's "Top" link
       never crossed the row, so the old observer left the bar up) and once the footer reaches it, so it never sits on the legal rows */
    var foot = d.querySelector('.site-footer'), bbRaf = 0;
    var bbUpdate = function () {
      bbRaf = 0;
      var past = mainBuy.getBoundingClientRect().bottom < 0, atFoot = foot && foot.getBoundingClientRect().top < innerHeight - 130;
      bb.classList.toggle('show', past && !atFoot);
    };
    addEventListener('scroll', function () { if (!bbRaf) bbRaf = requestAnimationFrame(bbUpdate); }, { passive: true });
    addEventListener('resize', bbUpdate); bbUpdate();
    var bba = bb.querySelector('[data-buybar-add]'); if (bba) bba.addEventListener('click', function () { var real = d.querySelector('.pdp-add'); if (real) real.click(); });
  }

  var pk = d.querySelector('.pdp-pack'), zm = pk && pk.querySelector('.zoomer');
  if (zm) {
    var at = function (e) {
      var r = zm.getBoundingClientRect();
      pk.style.setProperty('--ox', Math.max(0, Math.min(100, (e.clientX - r.left) / r.width * 100)).toFixed(1) + '%');
      pk.style.setProperty('--oy', Math.max(0, Math.min(100, (e.clientY - r.top) / r.height * 100)).toFixed(1) + '%');
    };
    if (fine) {
      /* not zoomed: the pack tilts toward the pointer (components.css reads --tx/--ty); click zooms and the lens
         follows the pointer; click again or leave to go back to the tilt */
      var tilt = function (e) {
        var r = zm.getBoundingClientRect();
        pk.style.setProperty('--tx', Math.max(-1, Math.min(1, (e.clientX - r.left) / r.width * 2 - 1)).toFixed(3));
        pk.style.setProperty('--ty', Math.max(-1, Math.min(1, (e.clientY - r.top) / r.height * 2 - 1)).toFixed(3));
      };
      zm.addEventListener('pointerenter', function (e) { if (!reduce) { tilt(e); pk.classList.add('tilt'); } });
      zm.addEventListener('pointermove', function (e) { if (pk.classList.contains('zoom')) at(e); else if (!reduce) tilt(e); });
      zm.addEventListener('pointerleave', function () { pk.classList.remove('zoom', 'tilt'); pk.style.removeProperty('--tx'); pk.style.removeProperty('--ty'); });
      zm.addEventListener('click', function (e) { at(e); pk.classList.toggle('zoom'); });
    } else {
      zm.addEventListener('click', function (e) { at(e); pk.classList.toggle('zoom'); });
    }
  }
})();
