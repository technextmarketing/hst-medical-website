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

  /* mobile nav */
  var tg = d.querySelector('.nav-toggle'), nav = d.getElementById('site-nav');
  if (tg && nav) tg.addEventListener('click', function () {
    var open = nav.classList.toggle('open'); tg.setAttribute('aria-expanded', open);
  });

  /* bag storage */
  function load() { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; } }
  function save(c) { try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) { say('Your browser blocks storage, so the bag cannot be kept between pages.'); } paint(); }
  function paint() {
    var n = load().reduce(function (s, i) { return s + i.qty; }, 0);
    d.querySelectorAll('.bag .count').forEach(function (el) { el.textContent = n; el.hidden = !n; });
    d.querySelectorAll('.bag').forEach(function (el) { el.setAttribute('aria-label', 'Bag, ' + n + ' item' + (n === 1 ? '' : 's')); });
  }
  paint();

  /* pack size → reprint the label */
  var pdp = d.querySelector('[data-pdp]');
  if (pdp) {
    var price = pdp.querySelector('[data-price-out]'), code = pdp.querySelector('[data-code-out]'), size = pdp.querySelector('[data-size-out]');
    var add = pdp.querySelector('[data-add]'), enquire = pdp.querySelector('[data-enquire]');
    function reprint(r) {
      var p = parseFloat(r.getAttribute('data-price')), has = !isNaN(p) && p > 0;
      pdp.classList.remove('printing'); void pdp.offsetWidth; if (!reduce) pdp.classList.add('printing');
      if (price) price.textContent = has ? money(p) : 'Price on request';
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
    save(c);
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
    var c = load(), sub = 0, FREE = 60, SHIP = 4.5;
    if (!c.length) {
      lines.innerHTML = '<div class="empty"><b>Your bag is empty.</b>Start at the counter: <a href="' + root + 'shop/pain-relief/">pain relief</a>, <a href="' + root + 'shop/cough-cold-flu/">cough and cold</a>, or <a href="' + root + 'shop/">all products</a>.</div>';
    } else {
      lines.innerHTML = c.map(function (i) {
        sub += i.price * i.qty;
        return '<div class="line"><img src="' + root + i.img + '" alt="" width="72" height="72"><div><a class="name" href="' + root + i.url + '">' + i.name + '</a><span class="meta">' + (i.variant ? i.variant + ' · ' : '') + money(i.price) + ' each' + (i.code ? ' · Item ' + i.code : '') + '</span><button class="rm" data-rm="' + i.id + '">Remove</button></div>' +
          '<div class="qty" aria-label="Quantity for ' + i.name + '"><button type="button" data-step="-1" aria-label="Decrease">−</button><input type="number" min="1" max="99" value="' + i.qty + '" data-line="' + i.id + '" aria-label="Quantity"><button type="button" data-step="1" aria-label="Increase">+</button></div><span class="sum">' + money(i.price * i.qty) + '</span></div>';
      }).join('');
    }
    var ship = sub && sub < FREE ? SHIP : 0;
    d.querySelectorAll('[data-sub]').forEach(function (e) { e.textContent = money(sub); });
    d.querySelectorAll('[data-ship]').forEach(function (e) { e.textContent = sub ? (ship ? money(ship) : 'Free') : '—'; });
    d.querySelectorAll('[data-total]').forEach(function (e) { e.textContent = money(sub + ship); });
    d.querySelectorAll('[data-free]').forEach(function (e) { e.textContent = !sub ? 'Free delivery on orders over ' + money(FREE) + '.' : (sub >= FREE ? 'You have free island-wide delivery.' : 'Add ' + money(FREE - sub) + ' more for free delivery.'); });
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
})();
