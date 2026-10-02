/* HST Medical prototype — progressive enhancement only (~3 KB, no dependencies).
   Everything works without JS: category pages are real URLs, accordions are <details>,
   forms post nowhere in the prototype. JS adds: mobile nav, scroll reveal, shop filter/search,
   and a localStorage demo cart so the EasyCart flow can be reviewed end to end. */
(function () {
  'use strict';
  var d = document, root = d.documentElement;

  /* mobile nav */
  var tg = d.querySelector('.nav-toggle'), nav = d.getElementById('site-nav');
  if (tg && nav) tg.addEventListener('click', function () {
    var open = nav.classList.toggle('open'); tg.setAttribute('aria-expanded', open);
  });

  /* reveal on scroll */
  var items = d.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && items.length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
  } else items.forEach(function (el) { el.classList.add('in'); });

  /* demo cart (localStorage) */
  var KEY = 'hst-demo-cart';
  function load() { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; } }
  function save(c) { try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) {} paint(); }
  function paint() {
    var n = load().reduce(function (s, i) { return s + i.qty; }, 0);
    d.querySelectorAll('.cart .count').forEach(function (el) { el.textContent = n; el.hidden = !n; });
  }
  paint();
  d.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-add]'); if (!b) return;
    ev.preventDefault();
    var c = load(), id = b.getAttribute('data-add'), q = 1, qi = d.getElementById('qty');
    if (qi && b.hasAttribute('data-pdp')) q = Math.max(1, parseInt(qi.value, 10) || 1);
    var hit = c.filter(function (i) { return i.id === id; })[0];
    if (hit) hit.qty += q; else c.push({ id: id, name: b.getAttribute('data-name'), price: +b.getAttribute('data-price') || 0, img: b.getAttribute('data-img'), url: b.getAttribute('data-url'), qty: q });
    save(c);
    var t = b.textContent; b.setAttribute('data-added', ''); b.textContent = 'Added ✓';
    setTimeout(function () { b.removeAttribute('data-added'); b.textContent = t; }, 1400);
  });
  var cartEl = d.getElementById('cart-lines');
  function money(n) { return 'S$' + n.toFixed(2); }
  function renderCart() {
    if (!cartEl) return;
    var c = load(), sub = 0, root = cartEl.getAttribute('data-root') || '';
    if (!c.length) { cartEl.innerHTML = '<div class="empty">Your cart is empty. <a href="' + root + 'shop/">Browse the store</a>.</div>'; d.querySelectorAll('[data-sub],[data-total]').forEach(function (e) { e.textContent = money(0); }); return; }
    var h = '<table class="cart-table"><thead><tr><th>Product</th><th>Qty</th><th>Price</th><th></th></tr></thead><tbody>';
    c.forEach(function (i) {
      sub += i.price * i.qty;
      h += '<tr><td><div style="display:flex;gap:.8rem;align-items:center"><img src="' + root + i.img + '" alt=""><a href="' + root + i.url + '">' + i.name + '</a></div></td><td>' + i.qty + '</td><td>' + money(i.price * i.qty) + '</td><td><button class="remove" data-rm="' + i.id + '">Remove</button></td></tr>';
    });
    cartEl.innerHTML = h + '</tbody></table>';
    d.querySelectorAll('[data-sub]').forEach(function (e) { e.textContent = money(sub); });
    d.querySelectorAll('[data-total]').forEach(function (e) { e.textContent = money(sub + (sub >= 60 || !sub ? 0 : 4.5)); });
    d.querySelectorAll('[data-ship]').forEach(function (e) { e.textContent = sub >= 60 ? 'Free' : money(4.5); });
  }
  renderCart();
  d.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-rm]'); if (!b) return;
    save(load().filter(function (i) { return i.id !== b.getAttribute('data-rm'); })); renderCart();
  });

  /* shop filter + search (category pages exist as real URLs too) */
  var grid = d.getElementById('shop-grid');
  if (grid) {
    var chips = d.querySelectorAll('.filters .chip'), q = d.getElementById('q'), cnt = d.getElementById('result-count'), cat = 'all';
    function apply() {
      var term = (q && q.value || '').toLowerCase().trim(), n = 0;
      grid.querySelectorAll('.product').forEach(function (p) {
        var ok = (cat === 'all' || p.getAttribute('data-cat') === cat) && (!term || p.getAttribute('data-search').indexOf(term) > -1);
        p.hidden = !ok; if (ok) n++;
      });
      if (cnt) cnt.textContent = n + ' product' + (n === 1 ? '' : 's');
    }
    chips.forEach(function (c) { c.addEventListener('click', function (e) {
      e.preventDefault(); chips.forEach(function (x) { x.classList.remove('active'); }); c.classList.add('active'); cat = c.getAttribute('data-cat'); apply();
      if (history.replaceState) history.replaceState(null, '', cat === 'all' ? location.pathname : '?cat=' + cat);
    }); });
    if (q) q.addEventListener('input', apply);
    var m = location.search.match(/cat=([\w-]+)/);
    if (m) { chips.forEach(function (c) { if (c.getAttribute('data-cat') === m[1]) c.click(); }); }
    apply();
  }

  /* forms: prototype success state only */
  d.querySelectorAll('form[data-demo]').forEach(function (f) {
    f.addEventListener('submit', function (e) { e.preventDefault(); f.classList.add('sent'); f.querySelector('.ok').scrollIntoView({ block: 'nearest' }); });
  });
})();
