/* HST Medical home hero v6: one Rheuma-Salve format in the spotlight. No dependencies.
   Without JS the balm slide shows, its Add to bag works, and every format tab is a link to that product page.
   With JS the tabs become a tablist with a springy indicator. Each hand-off swings the old pack out and the new one
   in on a re-toned halo, lifts the old copy away and raises the new headline word by word, then swaps the
   ingredient chips. Autoplay: every 3 s, driven by the indicator's progress bar (CSS animationend); it holds on
   hover, focus, a hidden tab or off-screen, pauses for 6 s after the visitor picks a format, stops for good with
   the pause button, and never runs under reduced motion. */
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
  var stage = $('.hs-stage'), packs = $$('.hs-pack'), slides = $$('.hs-slide'), chipsBox = $('.hs-chips'),
      tabsBox = $('.hs-tabs'), tabs = $$('.fmt'), ind = $('.hs-ind'), pause = $('.hs-pause'), live = d.getElementById('live');
  var N = data.length, DEPTH = [18, 30, 22], OUT = 'cubic-bezier(.16,1,.3,1)', IN = 'cubic-bezier(.55,0,.75,.2)';
  var cur = 0, token = 0, stopped = reduce, holds = {}, resumeT = 0;
  hero.style.setProperty('--dwell', '3s');

  function money(n) { return n ? 'S$' + n.toFixed(2) : 'Price on request'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function say(t) { if (live) { live.textContent = ''; setTimeout(function () { live.textContent = t; }, 40); } }
  function anim(el, kf, o) {
    if (!el.animate) return { finished: Promise.resolve(), cancel: function () {} };
    var a = el.animate(kf, o); a.finished.catch(function () {}); return a;
  }
  function stop(el) { if (el.getAnimations) el.getAnimations().forEach(function (a) { if (a.id === 'hs') a.cancel(); }); }

  /* indicator: slides under the chosen tab with a little overshoot, and carries the autoplay progress */
  function moveInd(n, instant) {
    if (!ind) return;
    var t = tabs[n], box = tabsBox.getBoundingClientRect(), r = t.getBoundingClientRect();
    if (instant) ind.style.transition = 'none';
    ind.style.width = r.width + 'px';
    ind.style.transform = 'translateX(' + (r.left - box.left) + 'px)';
    if (instant) { void ind.offsetWidth; ind.style.transition = ''; }
    ind.classList.remove('run'); void ind.offsetWidth; ind.classList.add('run');
  }

  /* the pack hand-off */
  function swapPack(a, b, dir) {
    var A = packs[a], B = packs[b], ia = A.querySelector('img'), ib = B.querySelector('img');
    packs.forEach(function (p) { stop(p); if (p !== A && p !== B) p.classList.remove('is-on', 'is-out', 'shine'); });
    A.classList.remove('is-on', 'shine'); A.classList.add('is-out'); B.classList.remove('is-out'); B.classList.add('is-on');
    ia.alt = ''; ib.alt = data[b].name + ', ' + data[b].size;
    var done = function () { if (!A.classList.contains('is-on')) A.classList.remove('is-out'); stop(A); };
    setTimeout(done, reduce ? 320 : 700); /* never rely on finish events alone: stalled frames must not leave two packs on stage */
    if (reduce) {
      anim(A, [{ opacity: 1 }, { opacity: 0 }], { duration: 200, fill: 'forwards', id: 'hs' }).finished.then(done, done);
      anim(B, [{ opacity: 0 }, { opacity: 1 }], { duration: 260, id: 'hs' });
      return;
    }
    anim(A, [{ transform: 'none', opacity: 1 }, { transform: 'translateX(' + (-dir * 14) + '%) scale(.86) rotate(' + (-dir * 5) + 'deg)', opacity: 0 }],
         { duration: 380, easing: IN, fill: 'forwards', id: 'hs' }).finished.then(done, done);
    anim(B, [{ transform: 'translateX(' + (dir * 16) + '%) scale(.86) rotate(' + (dir * 5) + 'deg)', opacity: 0 }, { transform: 'none', opacity: 1 }],
         { duration: 820, delay: 140, easing: OUT, fill: 'backwards', id: 'hs' });
    var sh = B.querySelector('.hs-sheen');
    sh.style.setProperty('--m', 'url("' + ib.src + '")');
    B.classList.remove('shine'); void B.offsetWidth; B.classList.add('shine');
  }

  /* the copy: old slide lifts away, new headline rises word by word, details follow */
  function focusables(sl, on) {
    $$('a,button', sl).forEach(function (el) { if (on) el.removeAttribute('tabindex'); else el.setAttribute('tabindex', '-1'); });
    sl.setAttribute('aria-hidden', on ? 'false' : 'true');
  }
  function swapSlide(a, b) {
    var A = slides[a], B = slides[b];
    slides.forEach(function (sl) { stop(sl); $$('*', sl).forEach(stop); sl.style.visibility = ''; });
    A.classList.remove('is-on'); B.classList.add('is-on');
    focusables(A, false); focusables(B, true);
    if (reduce) { anim(B, [{ opacity: 0 }, { opacity: 1 }], { duration: 260, id: 'hs' }); return; }
    A.style.visibility = 'visible';
    var clear = function () { if (!A.classList.contains('is-on')) A.style.visibility = ''; stop(A); };
    setTimeout(clear, 600);
    anim(A, [{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'translateY(-12px)' }], { duration: 240, easing: IN, fill: 'forwards', id: 'hs' }).finished.then(clear, clear);
    $$('.hs-title .w>span', B).forEach(function (w, k) {
      anim(w, [{ transform: 'translateY(105%)' }, { transform: 'none' }], { duration: 760, delay: 200 + k * 55, easing: OUT, fill: 'backwards', id: 'hs' });
    });
    $$('.hs-name,.hs-desc,.hs-origin,.hs-buy', B).forEach(function (el, k) {
      anim(el, [{ opacity: 0, transform: 'translateY(12px)' }, { opacity: 1, transform: 'none' }], { duration: 620, delay: 340 + k * 70, easing: OUT, fill: 'backwards', id: 'hs' });
    });
  }

  /* ingredient chips */
  function chip(c, k) {
    return '<li class="chip c' + k + '" data-k="' + c[2] + '" style="--d:' + DEPTH[k] + ';--fd:' + (k * 0.8).toFixed(1) + 's"><i></i>' +
      esc(c[0]) + (c[1] ? ' <small>' + esc(c[1]) + '</small>' : '') + '</li>';
  }
  function swapChips(list, t) {
    var outs = $$('.chip', chipsBox).map(function (el, k) {
      return anim(el, [{ opacity: 1, scale: 1 }, { opacity: 0, scale: 0.7 }], { duration: reduce ? 100 : 200, delay: reduce ? 0 : k * 30, easing: IN, fill: 'forwards' }).finished.catch(function () {});
    });
    Promise.all(outs).then(function () { if (t === token) chipsBox.innerHTML = list.map(chip).join(''); });
  }

  function go(n, user, dir) {
    n = (n % N + N) % N;
    if (n === cur) return;
    var from = cur, t = ++token;
    dir = dir || (n > from || (from === N - 1 && n === 0) ? 1 : -1);
    cur = n;
    tabs.forEach(function (tb, k) { tb.setAttribute('aria-selected', k === n ? 'true' : 'false'); tb.tabIndex = k === n ? 0 : -1; });
    moveInd(n);
    hero.style.setProperty('--tone', data[n].tone);
    stage.setAttribute('aria-label', data[n].name + ', ' + data[n].size);
    swapPack(from, n, dir);
    swapSlide(from, n);
    swapChips(data[n].chips, t);
    if (user) say(data[n].name + ', ' + data[n].size + ', ' + money(data[n].price) + '.');
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
  function pick(k, dir) {
    go(k, true, dir);
    hold('picked', true); clearTimeout(resumeT);
    resumeT = setTimeout(function () { hold('picked', false); }, 6000);
  }

  tabsBox.setAttribute('role', 'tablist');
  stage.setAttribute('role', 'tabpanel');
  stage.setAttribute('aria-label', data[0].name + ', ' + data[0].size);
  tabs.forEach(function (tb, k) {
    tb.setAttribute('role', 'tab'); tb.setAttribute('aria-controls', 'hs-stage'); tb.removeAttribute('aria-current');
    tb.setAttribute('aria-selected', k === 0 ? 'true' : 'false'); tb.tabIndex = k === 0 ? 0 : -1;
    tb.addEventListener('click', function (e) { e.preventDefault(); pick(k); });
  });
  tabsBox.addEventListener('keydown', function (e) {
    var k = { ArrowRight: cur + 1, ArrowDown: cur + 1, ArrowLeft: cur - 1, ArrowUp: cur - 1, Home: 0, End: N - 1 }[e.key];
    if (k === undefined) return;
    e.preventDefault();
    k = (k % N + N) % N;
    pick(k); tabs[k].focus();
  });
  if (ind) ind.addEventListener('animationend', function (e) { if (e.animationName === 'hs-bar' && !stopped) go(cur + 1, false, 1); });
  if (pause && !reduce) {
    pause.hidden = false;
    pause.addEventListener('click', function () { stopped = !stopped; sync(); if (!stopped) moveInd(cur); });
  }
  var show = $('.hs-show'), copy = $('.hs-copy');
  [show, copy].forEach(function (el) {
    el.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') hold('hover', true); });
    el.addEventListener('pointerleave', function () { hold('hover', false); });
  });
  hero.addEventListener('focusin', function () { hold('focus', true); });
  hero.addEventListener('focusout', function (e) { if (!hero.contains(e.relatedTarget)) hold('focus', false); });
  d.addEventListener('visibilitychange', function () { hold('hidden', d.hidden); });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      var off = !es[0].isIntersecting; hold('off', off); hero.classList.toggle('off', off);
    }, { threshold: 0.2 }).observe(hero);
  }
  addEventListener('resize', function () { moveInd(cur, true); });

  /* swipe the stage on touch screens */
  var sx = null, sy = 0;
  stage.addEventListener('pointerdown', function (e) { if (e.pointerType !== 'mouse') { sx = e.clientX; sy = e.clientY; } });
  stage.addEventListener('pointercancel', function () { sx = null; });
  stage.addEventListener('pointerup', function (e) {
    if (sx === null) return;
    var dx = e.clientX - sx, dy = e.clientY - sy; sx = null;
    if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy) * 1.3) pick(cur + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1);
  });

  /* pointer light: the pack turns toward the pointer, the halo's highlight and the chips follow */
  if (fine && !reduce) {
    var tx = 0, ty = 0, x = 0, y = 0, raf = 0;
    var tick = function () {
      x += (tx - x) * 0.08; y += (ty - y) * 0.08;
      hero.style.setProperty('--rx', x.toFixed(4)); hero.style.setProperty('--ry', y.toFixed(4));
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

  slides.forEach(function (sl, k) { focusables(sl, k === 0); });
  var start = function () { moveInd(0, true); };
  if (d.fonts && d.fonts.ready) d.fonts.ready.then(start); else start();
  setTimeout(function () { hero.classList.add('ready'); }, 1400);
  sync();
})();
