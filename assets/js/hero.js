/* HST Medical home hero v7: three cinematic scenes (Product, Company, People).
   Markup: build.py build_hero_cinema(); look: home.css section 2.
   - Chapters: the active tab's progress bar runs for --dur (CSS); its animationend moves to the next scene.
   - Holds pause the bar (CSS .hold) and block advancing: hovering a link/pack/chapter, keyboard focus inside the hero,
     a recent pick (9 s), a hidden tab, the hero off-screen, and the entry intro (html.intro).
   - Pointer parallax (fine pointers): .hx-par layers read --mx/--my, eased in rAF. Swipe changes scenes on touch.
   - Images of scenes 2 and 3 load on first use (data-src), the next scene is warmed 1.5 s after each cut.
   - Reduced motion: no autoplay, no parallax, plain cut (CSS removes the animation). */
(function () {
  var d = document, hero = d.querySelector('.hx[data-hero]');
  if (!hero) return;
  var stage = hero.querySelector('.hx-stage'), scenes = [].slice.call(hero.querySelectorAll('.hx-scene')), tabs = [].slice.call(hero.querySelectorAll('.hx-ch'));
  var pause = hero.querySelector('.hx-pause'), live = d.getElementById('live');
  var N = scenes.length, cur = 0, holds = {}, pickT = 0;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches, fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var stopped = reduce;
  if (!N || !tabs.length) return;

  function held() { return Object.keys(holds).length > 0; }
  function sync() {
    hero.classList.toggle('auto', !stopped);
    hero.classList.toggle('hold', held());
    if (pause) {
      pause.setAttribute('aria-pressed', stopped ? 'true' : 'false');
      var s = pause.querySelector('.sr-only'); if (s) s.textContent = stopped ? 'Play the highlights' : 'Pause the highlights';
    }
  }
  function hold(k, on) { if (on) holds[k] = 1; else delete holds[k]; sync(); }
  function wake(s) {
    if (!s) return;
    s.querySelectorAll('img[data-src]').forEach(function (im) { im.src = im.getAttribute('data-src'); im.removeAttribute('data-src'); });
  }
  function count(s) {
    s.querySelectorAll('[data-count]').forEach(function (el) {
      var to = +el.getAttribute('data-count'), t0 = 0;
      if (reduce) { el.textContent = to; return; }
      el.textContent = '0';
      var step = function (t) { if (!t0) t0 = t; var k = Math.min(1, (t - t0) / 1300); el.textContent = Math.round(to * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(step); };
      setTimeout(function () { requestAnimationFrame(step); }, 600);
    });
  }
  function say(t) { if (!live) return; live.textContent = ''; setTimeout(function () { live.textContent = t; }, 30); }

  function go(n, user) {
    n = (n % N + N) % N;
    if (n === cur) return;
    var from = scenes[cur], to = scenes[n];
    wake(to);
    from.classList.remove('is-on'); from.classList.add('is-out');
    from.setAttribute('aria-hidden', 'true'); from.inert = true;
    clearTimeout(from._t); from._t = setTimeout(function () { from.classList.remove('is-out'); }, reduce ? 0 : 950);
    to.classList.remove('is-out'); void to.offsetWidth; to.classList.add('is-on');
    to.removeAttribute('aria-hidden'); to.inert = false;
    tabs.forEach(function (t, k) {
      t.classList.toggle('on', k === n); t.classList.toggle('done', k < n);
      t.setAttribute('aria-selected', k === n ? 'true' : 'false'); t.tabIndex = k === n ? 0 : -1;
    });
    hero.setAttribute('data-scene', n);
    if (!reduce) { hero.classList.remove('wiping'); void hero.offsetWidth; hero.classList.add('wiping'); }
    cur = n;
    count(to);
    if (user) say(to.getAttribute('aria-label'));
    setTimeout(function () { wake(scenes[(n + 1) % N]); }, 1500);
  }
  function pick(n) {
    go(n, true);
    hold('picked', true); clearTimeout(pickT);
    pickT = setTimeout(function () { hold('picked', false); }, 9000);
  }

  tabs.forEach(function (t, k) {
    t.addEventListener('click', function () { if (k !== cur) pick(k); });
    t.addEventListener('animationend', function (e) {
      if (e.animationName === 'hx-prog' && k === cur && !stopped && !held()) go(cur + 1, false);
    });
  });
  var bar = hero.querySelector('.hx-chapters');
  if (bar) bar.addEventListener('keydown', function (e) {
    var k = { ArrowRight: cur + 1, ArrowLeft: cur - 1, Home: 0, End: N - 1 }[e.key];
    if (k === undefined) return;
    e.preventDefault(); k = (k % N + N) % N; pick(k); tabs[k].focus();
  });
  if (pause) {
    if (reduce) pause.hidden = true;
    pause.addEventListener('click', function () { stopped = !stopped; sync(); });
  }

  /* holds */
  hero.querySelectorAll('.hx-ctas, [data-orbit], .hx-bar, .hx-photo, .hx-stat').forEach(function (el) {
    el.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') hold('hover', true); });
    el.addEventListener('pointerleave', function () { hold('hover', false); });
  });
  hero.addEventListener('focusin', function (e) { if (e.target.matches(':focus-visible')) hold('focus', true); });
  hero.addEventListener('focusout', function (e) { if (!hero.contains(e.relatedTarget)) hold('focus', false); });
  d.addEventListener('visibilitychange', function () { hold('hidden', d.hidden); });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { var off = !es[0].isIntersecting; hold('off', off); hero.classList.toggle('off', off); }, { threshold: 0.15 }).observe(hero);
  }
  if (d.documentElement.classList.contains('intro')) {
    hold('intro', true);
    var mo = new MutationObserver(function () {
      if (d.documentElement.classList.contains('intro')) return;
      mo.disconnect(); hold('intro', false);
      var t = tabs[cur]; t.classList.remove('on'); void t.offsetWidth; t.classList.add('on');
    });
    mo.observe(d.documentElement, { attributes: true, attributeFilter: ['class'] });
  }

  /* swipe (touch / pen) */
  var sx = 0, sy = 0, sid = null;
  stage.addEventListener('pointerdown', function (e) { if (e.pointerType === 'mouse' || e.target.closest('[data-orbit]')) return; sid = e.pointerId; sx = e.clientX; sy = e.clientY; }, { passive: true });
  stage.addEventListener('pointerup', function (e) {
    if (e.pointerId !== sid) return; sid = null;
    var dx = e.clientX - sx, dy = e.clientY - sy;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.4) pick(cur + (dx < 0 ? 1 : -1));
  }, { passive: true });
  stage.addEventListener('pointercancel', function () { sid = null; });

  /* pointer parallax, eased */
  if (fine && !reduce) {
    var tx = 0, ty = 0, mx = 0, my = 0, raf = 0;
    var tick = function () {
      mx += (tx - mx) * 0.07; my += (ty - my) * 0.07;
      hero.style.setProperty('--mx', mx.toFixed(4)); hero.style.setProperty('--my', my.toFixed(4));
      raf = (Math.abs(tx - mx) > 0.001 || Math.abs(ty - my) > 0.001) ? requestAnimationFrame(tick) : 0;
    };
    stage.addEventListener('pointermove', function (e) {
      var r = stage.getBoundingClientRect();
      tx = (e.clientX - r.left) / r.width * 2 - 1; ty = (e.clientY - r.top) / r.height * 2 - 1;
      if (!raf) raf = requestAnimationFrame(tick);
    });
    stage.addEventListener('pointerleave', function () { tx = 0; ty = 0; if (!raf) raf = requestAnimationFrame(tick); });
  }

  setTimeout(function () { wake(scenes[1]); }, 2500);
  sync();
})();

/* Product turntable (hero scene 1): the five Rheuma-Salve formats on an ellipse.
   - Positions are computed per frame (transform/opacity only) and spring toward the target stop.
   - Drag or flick to spin (pointer capture starts after 6px, so plain clicks still work); a click on a back pack
     brings it forward, a click on the front pack opens its page; arrows in the "now" card step it.
   - The front pack drives the "now" card (name, size, price, Add to bag for THAT pack), its ingredient chips and the
     spotlight. The light sweep (.lit) plays only when the visitor picks a pack (click, arrows, drag, keyboard), once
     the spin settles; automatic turns (every 2.6 s while scene 1 shows and the hero is not held) never light it.
   - Reduced motion: no auto-turn, stops jump instead of spring. */
(function () {
  var d = document, box = d.querySelector('[data-orbit]');
  if (!box) return;
  var hero = box.closest('.hx'), orbit = box.querySelector('.hx-orbit'), items = [].slice.call(box.querySelectorAll('.hx-pk')), N = items.length, data = [];
  try { data = JSON.parse(d.getElementById('hx-orbit-data').textContent); } catch (e) { return; }
  if (!N || data.length !== N) return;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches, fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var STEP = 360 / N, angle = 0, target = 0, vel = 0, raf = 0, front = 0, W = 0, H = 0, picked = false, quietUntil = 0;
  var label = box.querySelector('[data-now="label"]'), meta = box.querySelector('[data-now="meta"]'), card = box.querySelector('.hx-now');
  var add = box.querySelector('.hx-now-add'), ingr = box.querySelector('.hx-ingr'), spot = box.querySelector('.hx-spot'), live = d.getElementById('live');
  var esc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var say = function (t) { if (!live) return; live.textContent = ''; setTimeout(function () { live.textContent = t; }, 30); };
  var restart = function (el, c) { if (!el) return; el.classList.remove(c); void el.offsetWidth; el.classList.add(c); };
  var nearest = function (a) { return ((Math.round(a / STEP) % N) + N) % N; };

  function measure() { W = box.clientWidth; H = box.clientHeight; }
  function layout() {
    var narrow = W < 520;
    for (var i = 0; i < N; i++) {
      var el = items[i], th = (i * STEP - angle) * Math.PI / 180, x = Math.sin(th), f = (Math.cos(th) + 1) / 2;
      var s = .5 + .5 * Math.pow(f, 1.6), tx = x * W * (narrow ? .36 : .41), ty = -(1 - f) * H * (narrow ? .11 : .15);
      el.style.transform = 'translate3d(' + tx.toFixed(1) + 'px,' + ty.toFixed(1) + 'px,0) scale(' + s.toFixed(3) + ')';
      el.style.zIndex = String(10 + Math.round(f * 40));
      el.style.opacity = (.5 + .5 * f).toFixed(3);
      el.style.setProperty('--fog', (1 - f).toFixed(3));
    }
  }
  function setFront(i) {
    if (i === front) return;
    front = i;
    var o = data[i];
    items.forEach(function (el, k) { el.classList.toggle('is-front', k === i); });
    if (label) label.textContent = o.label;
    if (meta) meta.textContent = o.meta;
    if (add) {
      var a = o.add;
      add.setAttribute('data-id', a.id); add.setAttribute('data-name', a.name); add.setAttribute('data-price', a.price);
      add.setAttribute('data-variant', a.variant); add.setAttribute('data-code', a.code); add.setAttribute('data-img', a.img); add.setAttribute('data-url', a.url);
      add.setAttribute('aria-label', 'Add ' + a.name + ' to bag');
    }
    if (ingr) ingr.innerHTML = o.chips.map(function (c, n) { return '<li style="--n:' + n + '">' + esc(c) + '</li>'; }).join('');
    restart(ingr, 'swap'); restart(card, 'swap'); restart(spot, 'flash');
  }
  function tick() {
    if (!drag) {
      var dA = target - angle;
      vel = vel * .78 + dA * .085; angle += vel;
      if (Math.abs(dA) < .03 && Math.abs(vel) < .03) { angle = target; vel = 0; }
    }
    layout();
    setFront(nearest(angle));
    if (!drag && angle === target && picked) { picked = false; light(); }
    raf = (drag || angle !== target) ? requestAnimationFrame(tick) : 0;
  }
  function go(t) {
    target = t;
    if (reduce) { angle = t; vel = 0; layout(); setFront(nearest(angle)); if (picked) { picked = false; light(); } return; }
    if (!raf) raf = requestAnimationFrame(tick);
  }
  function light() { quietUntil = Date.now() + 8000; items.forEach(function (el) { el.classList.remove('lit'); }); var el = items[front]; void el.offsetWidth; el.classList.add('lit'); }
  function pick() { picked = true; items.forEach(function (el) { el.classList.remove('lit'); }); if (angle === target && !raf) { picked = false; light(); } }
  function stepBy(n) { go(Math.round(target / STEP) * STEP + n * STEP); }
  function bring(i) { var diff = ((i * STEP - target) % 360 + 540) % 360 - 180; go(target + diff); }
  function announce() { var o = data[nearest(target)]; say(o.name + ', ' + o.meta); }

  /* drag / flick */
  var drag = false, pid = null, sx = 0, lx = 0, lt = 0, v = 0, moved = 0;
  box.addEventListener('pointerdown', function (e) {
    if (e.button || e.target.closest('.hx-now')) return;
    pid = e.pointerId; sx = lx = e.clientX; lt = performance.now(); v = 0; moved = 0;
  });
  box.addEventListener('pointermove', function (e) {
    if (pid !== null && e.pointerId === pid) {
      var dx = e.clientX - lx; lx = e.clientX; moved += Math.abs(dx);
      if (!drag && Math.abs(e.clientX - sx) > 6) { drag = true; box.classList.add('grabbing'); try { box.setPointerCapture(pid); } catch (er) {} }
      if (drag) {
        var k = 360 / (W * 1.35), now = performance.now();
        angle -= dx * k; target = angle;
        v = (-dx * k) / Math.max(8, now - lt) * 16; lt = now;
        if (!raf) raf = requestAnimationFrame(tick);
      }
      return;
    }
    if (fine && !reduce) {
      var r = box.getBoundingClientRect();
      box.style.setProperty('--ox', ((e.clientX - r.left) / r.width * 2 - 1).toFixed(3));
      box.style.setProperty('--oy', ((e.clientY - r.top) / r.height * 2 - 1).toFixed(3));
    }
  });
  function end(e) {
    if (e.pointerId !== pid) return;
    pid = null;
    if (drag) { drag = false; box.classList.remove('grabbing'); picked = true; go(Math.round((angle + v * 9) / STEP) * STEP); announce(); }
  }
  box.addEventListener('pointerup', end);
  box.addEventListener('pointercancel', end);
  box.addEventListener('pointerleave', function () { box.style.setProperty('--ox', 0); box.style.setProperty('--oy', 0); });
  orbit.addEventListener('click', function (e) {
    var a = e.target.closest('.hx-pk'); if (!a) return;
    if (moved > 6) { e.preventDefault(); moved = 0; return; }
    var i = +a.getAttribute('data-k');
    if (i !== nearest(target)) { e.preventDefault(); picked = true; bring(i); announce(); } else if (moved <= 6) { pick(); }
  });
  items.forEach(function (el) {
    el.addEventListener('focus', function () { if (!el.matches(':focus-visible')) return; picked = true; if (+el.getAttribute('data-k') !== nearest(target)) bring(+el.getAttribute('data-k')); else pick(); });
    el.addEventListener('dragstart', function (e) { e.preventDefault(); });
  });
  box.querySelectorAll('[data-spin]').forEach(function (b) {
    b.addEventListener('click', function () { picked = true; stepBy(+b.getAttribute('data-spin')); announce(); });
  });

  /* auto-turn while the product scene is showing */
  (function loop() {
    setTimeout(function () {
      var showing = hero && hero.getAttribute('data-scene') === '0' && hero.classList.contains('auto');
      var paused = picked || Date.now() < quietUntil || !hero || hero.classList.contains('hold') || hero.classList.contains('off') || d.documentElement.classList.contains('intro') || d.hidden || drag || pid !== null;
      if (showing && !paused && !reduce) { items.forEach(function (el) { el.classList.remove('lit'); }); stepBy(1); }
      loop();
    }, 2600);
  })();

  measure(); layout(); orbit.classList.add('ready');
  addEventListener('resize', function () { measure(); layout(); });
})();

/* Catalogue index (home, end of "Shop by range"): hovering or focusing a chapter row turns the book to that chapter's
   first sheet; leaving the index turns back to the cover. Images are warmed on first approach. Rows are plain links to
   the flipbook, so nothing depends on this script. */
(function () {
  var d = document, box = d.querySelector('[data-cbk]');
  if (!box) return;
  var vol = box.querySelector('.cbk-vol'), page = box.querySelector('.cbk-page'), rows = [].slice.call(box.querySelectorAll('.cbk-toc a'));
  if (!vol || !page || !rows.length) return;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cover = page.getAttribute('src'), cur = cover, curN = 1, warm = false, t = 0, busy = null;
  function warmUp() { if (warm) return; warm = true; rows.forEach(function (a) { var i = new Image(); i.decoding = 'async'; i.src = a.getAttribute('data-img'); }); }
  function turn(src, n, row) {
    rows.forEach(function (a) { a.classList.toggle('on', a === row); });
    if (src === cur) return;
    var back = n < curN, from = cur;
    cur = src; curN = n;
    var im = new Image(); im.src = src;
    (im.decode ? im.decode() : Promise.resolve()).catch(function () {}).then(function () {
      if (cur !== src) return;
      if (reduce) { page.src = src; return; }
      if (busy && busy.parentNode) busy.parentNode.removeChild(busy);
      var leaf = d.createElement('span');
      leaf.className = 'cbk-leaf' + (back ? ' back' : '');
      leaf.innerHTML = '<img alt="" src="' + (back ? src : from) + '">';
      vol.appendChild(leaf); busy = leaf;
      if (!back) page.src = src;
      var done = function () { if (back && cur === src) page.src = src; if (leaf.parentNode) leaf.parentNode.removeChild(leaf); };
      leaf.addEventListener('animationend', done, { once: true });
      setTimeout(done, 900);
    });
  }
  box.addEventListener('pointerenter', warmUp, { once: true });
  box.addEventListener('focusin', warmUp, { once: true });
  rows.forEach(function (a) {
    var go = function () { clearTimeout(t); t = setTimeout(function () { turn(a.getAttribute('data-img'), +a.getAttribute('data-page'), a); }, 70); };
    a.addEventListener('pointerenter', go);
    a.addEventListener('focus', go);
  });
  var idx = box.querySelector('.cbk-index');
  idx.addEventListener('pointerleave', function () { clearTimeout(t); t = setTimeout(function () { turn(cover, 1, null); }, 450); });
  idx.addEventListener('focusout', function (e) { if (!idx.contains(e.relatedTarget)) { clearTimeout(t); t = setTimeout(function () { turn(cover, 1, null); }, 450); } });
})();
