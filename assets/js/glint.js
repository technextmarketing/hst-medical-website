/* HST Medical: the hero's light sweep on every product image, site-wide (cards, matcher, ranges, shop-by-need tiles,
   marquee, brand fans, about page, product pages, bag, chat). Light only: no reflections.
   - Each product image gets a sibling overlay <i class="glint"> masked by the image itself, so the light only ever
     touches the pack, never the background (components.css section 4).
   - It plays once when the image first scrolls into view (staggered), again on hover, and every few seconds on the
     product page's main image. While it plays, the overlay copies the image's live transform each frame, so lifts,
     tilts and fans stay aligned.
   - New images (filters, bag lines, chat cards) are picked up by a MutationObserver. Reduced motion: off. */
(function () {
  if (!window.matchMedia || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var d = document, SEL = 'img[src*="assets/img/products/"],img[src*="assets/img/hero/rs-"]';
  var SKIP = '.hx, .hx-cell, .cbk, .glint-off, [data-no-glint]';
  var HOST = '.plabel, .mcard, .bento a, .counters a, .rg-item, .bp, .line, .pdp-pack, .ab-formats li, a, figure, li';
  var done = typeof WeakSet === 'function' ? new WeakSet() : null, queue = [], qt = 0;

  function place(img, g) {
    g.style.left = img.offsetLeft + 'px'; g.style.top = img.offsetTop + 'px';
    g.style.width = img.offsetWidth + 'px'; g.style.height = img.offsetHeight + 'px';
  }
  function copy(img, g) {
    var cs = getComputedStyle(img);
    g.style.transform = cs.transform === 'none' ? '' : cs.transform;
    g.style.translate = cs.translate && cs.translate !== 'none' ? cs.translate : '';
    g.style.rotate = cs.rotate && cs.rotate !== 'none' ? cs.rotate : '';
    g.style.scale = cs.scale && cs.scale !== 'none' ? cs.scale : '';
    g.style.transformOrigin = cs.transformOrigin;
  }
  function play(img) {
    var g = img._glint;
    if (!g || !g._ready || !img.offsetWidth) return;
    place(img, g);
    g.classList.remove('go'); void g.offsetWidth; g.classList.add('go');
    var t0 = performance.now();
    (function follow() { copy(img, g); if (performance.now() - t0 < 1250) requestAnimationFrame(follow); })();
  }
  function flush() {
    qt = 0;
    var img = queue.shift();
    if (img) play(img);
    if (queue.length) qt = setTimeout(flush, 90);
  }
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.unobserve(e.target); queue.push(e.target);
      if (!qt) qt = setTimeout(flush, 260);
    });
  }, { threshold: 0.4 }) : null;
  var ro = 'ResizeObserver' in window ? new ResizeObserver(function (es) {
    es.forEach(function (e) { if (e.target._glint) place(e.target, e.target._glint); });
  }) : null;

  function make(img) {
    if ((done && done.has(img)) || img._glint || img.closest(SKIP)) return;
    if (done) done.add(img);
    var g = d.createElement('i');
    g.className = 'glint'; g.setAttribute('aria-hidden', 'true');
    img.insertAdjacentElement('afterend', g);
    img._glint = g;
    var ready = function () {
      var u = 'url("' + (img.currentSrc || img.src) + '")';
      g.style.webkitMaskImage = u; g.style.maskImage = u; g._ready = true; place(img, g);
    };
    if (img.complete && img.naturalWidth) ready(); else img.addEventListener('load', ready, { once: true });
    if (ro) ro.observe(img);
    if (io) io.observe(img);
    var host = img.closest(HOST) || img.parentElement;
    if (host && !host._glintHover) {
      host._glintHover = true;
      host.addEventListener('pointerenter', function (e) {
        if (e.pointerType !== 'mouse') return;
        clearTimeout(host._gt);
        host._gt = setTimeout(function () { host.querySelectorAll(SEL).forEach(function (im) { if (im._glint) play(im); }); }, 240);
      });
      host.addEventListener('pointerleave', function () { clearTimeout(host._gt); });
    }
  }
  function scan(root) { (root || d).querySelectorAll(SEL).forEach(make); }

  scan();
  var mt = 0;
  new MutationObserver(function (ms) {
    var hit = false;
    for (var i = 0; i < ms.length && !hit; i++) for (var j = 0; j < ms[i].addedNodes.length; j++) { var n = ms[i].addedNodes[j]; if (n.nodeType === 1 && n.className !== 'glint') { hit = true; break; } }
    if (hit) { clearTimeout(mt); mt = setTimeout(scan, 150); }
  }).observe(d.body, { childList: true, subtree: true });

  /* product page: a showroom light across the main pack every few seconds while it is on screen */
  var pk = d.querySelector('.pdp-pack'), main = pk && pk.querySelector('.zoomer img');
  if (main) {
    var vis = true;
    if (io) new IntersectionObserver(function (es) { vis = es[0].isIntersecting; }).observe(main);
    setInterval(function () { if (vis && !d.hidden && !pk.classList.contains('zoom')) play(main); }, 6500);
  }
})();
