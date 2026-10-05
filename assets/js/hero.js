/* HST Medical home hero: the Rheuma-Salve format stage. No dependencies.
   Without JS the balm is shown, its price label works, and every format tab is a link to that product page.
   With JS the tabs become a tablist: each switch re-tones the plinth, swaps the cut-out pack (sheen pass),
   the headline phrase, the watermark word and the ingredient chips, and re-prints the price label.
   Autoplay advances on the tab's progress bar (CSS animationend), holds on hover, focus, hidden tab or
   off-screen, stops for good once the visitor picks a format, and never runs under reduced motion. */
(function () {
  'use strict';
  var d = document, hero = d.querySelector('[data-hero]');
  if (!hero) return;
  var data;
  try { data = JSON.parse(d.getElementById('hero-data').textContent); } catch (e) { return; }
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var $ = function (s, r) { return (r || hero).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || hero).querySelectorAll(s)); };
  var stage = $('.hs-stage'), packs = $$('.hs-pack'), phrases = $$('.hs-phrase'), words = $$('.hs-word span'),
      chipsBox = $('.hs-chips'), card = $('.hs-card'), print = $('.hs-print'), tabsBox = $('.hs-tabs'), tabs = $$('.fmt'),
      pause = $('.hs-pause'), add = $('[data-add]', card), priceEl = $('[data-f=price]', card), live = d.getElementById('live');
  var DEPTH = [18, 30, 22, 26, 14, 34], OUT = 'cubic-bezier(.16,1,.3,1)', IN = 'cubic-bezier(.55,0,.75,.2)';
  var SHADOW = ' drop-shadow(0 16px 16px rgba(24,48,38,.24))', SHADOW0 = ' drop-shadow(0 16px 16px rgba(24,48,38,0))';
  var cur = 0, token = 0, shown = data[0].price, stopped = reduce, holds = {};

  function money(n) { return n ? 'S$' + n.toFixed(2) : 'Price on request'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function say(t) { if (live) { live.textContent = ''; setTimeout(function () { live.textContent = t; }, 40); } }
  function anim(el, kf, o) {
    if (!el.animate) return { finished: Promise.resolve(), cancel: function () {} };
    var a = el.animate(kf, o); a.finished.catch(function () {}); return a;
  }
  function stopAnims(el) { if (el.getAnimations) el.getAnimations().forEach(function (a) { if (a.id === 'hs') a.cancel(); }); }
  function load(i) {
    var img = packs[i].querySelector('img');
    if (img.dataset.src) { img.src = img.dataset.src; img.removeAttribute('data-src'); img.alt = data[i].name.replace('®', '') + ', ' + data[i].size; }
    return img;
  }
  function sheen(i) {
    var p = packs[i], img = load(i);
    p.querySelector('.hs-sheen').style.setProperty('--m', 'url("' + img.src + '")');
    p.classList.remove('shine'); void p.offsetWidth; p.classList.add('shine');
  }

  /* the pack: outgoing swings away, incoming swings in from the travel direction */
  function swapPack(a, b, dir) {
    var A = packs[a], B = packs[b], ia = A.querySelector('img'), ib = load(b);
    packs.forEach(function (p) { stopAnims(p.querySelector('img')); if (p !== A) p.classList.remove('is-out'); });
    A.classList.remove('is-on', 'shine'); A.classList.add('is-out'); B.classList.add('is-on');
    var done = function () { if (!A.classList.contains('is-on')) A.classList.remove('is-out'); stopAnims(ia); };
    if (reduce) {
      anim(ia, [{ opacity: 1 }, { opacity: 0 }], { duration: 180, fill: 'forwards', id: 'hs' }).finished.then(done, done);
      anim(ib, [{ opacity: 0 }, { opacity: 1 }], { duration: 260, id: 'hs' });
      return;
    }
    anim(ia, [{ transform: 'none', opacity: 1, filter: 'blur(0px)' + SHADOW },
              { transform: 'translateX(' + (-dir * 36) + '%) rotate(' + (-dir * 10) + 'deg) scale(.8)', opacity: 0, filter: 'blur(8px)' + SHADOW0 }],
         { duration: 420, easing: IN, fill: 'forwards', id: 'hs' }).finished.then(done, done);
    anim(ib, [{ transform: 'translateX(' + (dir * 42) + '%) rotate(' + (dir * 12) + 'deg) scale(.78)', opacity: 0, filter: 'blur(10px)' + SHADOW0 },
              { transform: 'none', opacity: 1, filter: 'blur(0px)' + SHADOW }],
         { duration: 950, delay: 120, easing: OUT, fill: 'backwards', id: 'hs' });
    sheen(b);
  }

  /* stacked text (headline phrase, watermark word): the outgoing line lifts out of its mask, the next rises in */
  function swapStack(list, a, b, dist) {
    var A = list[a], B = list[b];
    if (!A || !B) return;
    list.forEach(function (el) { stopAnims(el); el.style.visibility = ''; });
    A.classList.remove('is-on'); B.classList.add('is-on');
    if (reduce) { anim(B, [{ opacity: 0 }, { opacity: 1 }], { duration: 300, id: 'hs' }); return; }
    A.style.visibility = 'visible';
    var clear = function () { A.style.visibility = ''; stopAnims(A); };
    anim(A, [{ transform: 'none', opacity: 1, filter: 'blur(0px)' }, { transform: 'translateY(-' + dist + ')', opacity: 0, filter: 'blur(6px)' }],
         { duration: 320, easing: IN, fill: 'forwards', id: 'hs' }).finished.then(clear, clear);
    anim(B, [{ transform: 'translateY(' + dist + ')', opacity: 0, filter: 'blur(6px)' }, { transform: 'none', opacity: 1, filter: 'blur(0px)' }],
         { duration: 800, delay: 140, easing: OUT, fill: 'backwards', id: 'hs' });
  }

  /* ingredient chips: old ones pop out, the new list pops in staggered (CSS hs-chip-in on insert) */
  function chip(c, k) {
    return '<li class="chip c' + k + '" data-k="' + c[2] + '" style="--d:' + DEPTH[k] + ';--fd:' + (k * 0.7).toFixed(1) + 's"><i></i>' +
      esc(c[0]) + (c[1] ? ' <small>' + esc(c[1]) + '</small>' : '') + '</li>';
  }
  function swapChips(list, t) {
    var outs = $$('.chip', chipsBox).map(function (el, k) {
      return anim(el, [{ opacity: 1, scale: 1 }, { opacity: 0, scale: 0.6, filter: 'blur(4px)' }],
                  { duration: reduce ? 120 : 220, delay: reduce ? 0 : k * 25, easing: IN, fill: 'forwards' }).finished.catch(function () {});
    });
    Promise.all(outs).then(function () { if (t === token) chipsBox.innerHTML = list.map(chip).join(''); });
  }

  /* the price label re-prints: content feeds out, fields update, the label feeds back in and the price rolls */
  function rollPrice(to) {
    var from = shown, t0 = performance.now();
    shown = to;
    if (reduce || !from || !to || from === to) { priceEl.textContent = money(to); return; }
    (function step(now) {
      if (shown !== to) return;
      var k = Math.min(1, (now - t0) / 480), e = 1 - Math.pow(1 - k, 3);
      priceEl.textContent = money(from + (to - from) * e);
      if (k < 1) requestAnimationFrame(step);
    })(t0);
  }
  function reprint(P, t) {
    stopAnims(print);
    anim(print, [{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'translateY(-8px)' }],
         { duration: reduce ? 90 : 170, easing: IN, fill: 'forwards', id: 'hs' }).finished.then(function () {
      if (t !== token) return;
      $('[data-f=fmt]', card).textContent = P.fmt;
      $('[data-f=size]', card).textContent = P.size;
      $('[data-f=origin]', card).textContent = P.origin;
      $('[data-f=for]', card).textContent = P.for;
      $('[data-f=packs]', card).textContent = P.packs;
      $('.hs-name a', card).textContent = P.name;
      $$('[data-f=url]', card).forEach(function (a) { a.setAttribute('href', P.url); });
      if (add) {
        var A = P.add;
        add.setAttribute('data-id', A.id); add.setAttribute('data-name', A.name); add.setAttribute('data-price', A.price);
        add.setAttribute('data-variant', A.variant); add.setAttribute('data-code', A.code); add.setAttribute('data-img', A.img); add.setAttribute('data-url', A.url);
      }
      stopAnims(print);
      if (!reduce) anim(print, [{ opacity: 0, transform: 'translateY(12px)', clipPath: 'inset(0 0 100% 0)' }, { opacity: 1, transform: 'none', clipPath: 'inset(0 0 0% 0)' }],
                        { duration: 560, easing: OUT, id: 'hs' });
      rollPrice(P.price);
    }, function () {});
  }

  function go(n, user, dir) {
    n = (n + data.length) % data.length;
    if (n === cur) return;
    var from = cur, P = data[n], t = ++token;
    dir = dir || (n > from ? 1 : -1);
    cur = n;
    tabs.forEach(function (tb, k) { tb.setAttribute('aria-selected', k === n ? 'true' : 'false'); tb.tabIndex = k === n ? 0 : -1; });
    hero.style.setProperty('--tone', P.tone);
    stage.setAttribute('aria-label', P.name.replace('®', '') + ', ' + P.size);
    swapPack(from, n, dir);
    swapStack(phrases, from, n, '60%');
    swapStack(words, from, n, '35%');
    swapChips(P.chips, t);
    reprint(P, t);
    if (user) say(P.name + ', ' + P.size + ', ' + money(P.price) + '.');
  }

  /* autoplay state */
  function sync() {
    hero.classList.toggle('auto', !stopped);
    hero.classList.toggle('hold', Object.keys(holds).length > 0);
    if (pause) {
      pause.setAttribute('aria-pressed', stopped ? 'true' : 'false');
      pause.querySelector('.sr-only').textContent = stopped ? 'Play the format showcase' : 'Pause the format showcase';
    }
  }
  function hold(key, on) { if (on) holds[key] = 1; else delete holds[key]; sync(); }
  function pick(k, dir) { stopped = true; sync(); go(k, true, dir); }

  tabsBox.setAttribute('role', 'tablist');
  stage.setAttribute('role', 'tabpanel');
  stage.setAttribute('aria-label', data[0].name.replace('®', '') + ', ' + data[0].size);
  tabs.forEach(function (tb, k) {
    tb.setAttribute('role', 'tab'); tb.setAttribute('aria-controls', 'hs-stage'); tb.removeAttribute('aria-current');
    tb.setAttribute('aria-selected', k === 0 ? 'true' : 'false'); tb.tabIndex = k === 0 ? 0 : -1;
    tb.addEventListener('click', function (e) { e.preventDefault(); pick(k); });
    tb.addEventListener('pointerenter', function () { load(k); });
  });
  tabsBox.addEventListener('keydown', function (e) {
    var k = { ArrowRight: cur + 1, ArrowDown: cur + 1, ArrowLeft: cur - 1, ArrowUp: cur - 1, Home: 0, End: data.length - 1 }[e.key];
    if (k === undefined) return;
    e.preventDefault();
    k = (k + data.length) % data.length;
    pick(k); tabs[k].focus();
  });
  tabsBox.addEventListener('animationend', function (e) {
    if (e.animationName === 'hs-bar' && !stopped) go(cur + 1, false, 1);
  });
  if (pause && !reduce) {
    pause.hidden = false;
    pause.addEventListener('click', function () { stopped = !stopped; sync(); });
  }
  var show = $('.hs-show');
  show.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') hold('hover', true); });
  show.addEventListener('pointerleave', function () { hold('hover', false); });
  hero.addEventListener('focusin', function () { hold('focus', true); });
  hero.addEventListener('focusout', function (e) { if (!hero.contains(e.relatedTarget)) hold('focus', false); });
  d.addEventListener('visibilitychange', function () { hold('hidden', d.hidden); });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      var off = !es[0].isIntersecting; hold('off', off); hero.classList.toggle('off', off);
    }, { threshold: 0.15 }).observe(hero);
  }

  /* swipe the stage on touch screens */
  var sx = null, sy = 0;
  stage.addEventListener('pointerdown', function (e) { if (e.pointerType !== 'mouse') { sx = e.clientX; sy = e.clientY; } });
  stage.addEventListener('pointercancel', function () { sx = null; });
  stage.addEventListener('pointerup', function (e) {
    if (sx === null) return;
    var dx = e.clientX - sx, dy = e.clientY - sy; sx = null;
    if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy) * 1.3) pick(cur + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1);
  });

  /* pointer light: the pack turns toward the pointer, chips and watermark drift at their own depth */
  if (fine && !reduce) {
    var tx = 0, ty = 0, x = 0, y = 0, raf = 0;
    var tick = function () {
      x += (tx - x) * 0.08; y += (ty - y) * 0.08;
      stage.style.setProperty('--rx', x.toFixed(4)); stage.style.setProperty('--ry', y.toFixed(4));
      raf = Math.abs(tx - x) > 0.002 || Math.abs(ty - y) > 0.002 ? requestAnimationFrame(tick) : 0;
    };
    var clamp = function (v) { return v < -1 ? -1 : v > 1 ? 1 : v; };
    hero.addEventListener('pointermove', function (e) {
      var r = stage.getBoundingClientRect();
      tx = clamp((e.clientX - r.left - r.width / 2) / (r.width / 2));
      ty = clamp((e.clientY - r.top - r.height / 2) / (r.height / 2));
      if (!raf) raf = requestAnimationFrame(tick);
    });
    hero.addEventListener('pointerleave', function () { tx = ty = 0; if (!raf) raf = requestAnimationFrame(tick); });
  }

  /* warm the other four packs once the page is idle */
  var warm = function () { for (var i = 1; i < packs.length; i++) load(i); };
  var later = function () { if (window.requestIdleCallback) requestIdleCallback(warm, { timeout: 1500 }); else setTimeout(warm, 600); };
  if (d.readyState === 'complete') later(); else addEventListener('load', later);
  sheen(0); packs[0].classList.remove('shine');
  setTimeout(function () { hero.classList.add('ready'); }, 1500);
  sync();
})();
