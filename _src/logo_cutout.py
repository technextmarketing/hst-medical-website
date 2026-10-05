"""
Transparent HST Medical logo from the live site's white-ground PNG (assets/img/logo-hst-kowa.png).

    python _src/logo_cutout.py

The magenta roundel is found geometrically (its horizontal extent gives the radius; its lowest point the
centre). Inside the roundel everything stays opaque, so the white figure survives. Outside it every pixel is
un-multiplied from white (colour-to-alpha), so the wordmark, the swirl and the letter counters come out clean,
anti-aliased and fringe-free on any ground.
Writes assets/img/logo-hst.png (full size), logo-hst.webp (240 px tall) and logo-hst-white.webp (an all-white
silhouette for coloured grounds, 240 px tall).
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(os.path.dirname(HERE), "assets", "img")


def main():
    im = Image.open(os.path.join(IMG, "logo-hst-kowa.png")).convert("RGB")
    a = np.asarray(im).astype(float)
    h, w, _ = a.shape
    mag = (a[..., 0] > 150) & (a[..., 1] < 120) & (a[..., 2] < 170)
    left = mag[:, : int(w * 0.45)]
    ys, xs = np.nonzero(left)
    r = (xs.max() - xs.min()) / 2.0
    cx = (xs.max() + xs.min()) / 2.0
    cy = ys.max() - r
    yy, xx = np.mgrid[0:h, 0:w]
    inside = np.hypot(xx - cx, yy - cy) < r - 1.0
    alpha = np.clip((255 - a).max(axis=2) / 255.0 * 1.12, 0, 1)
    alpha[inside] = 1.0
    rgb = a.copy()
    m = (~inside) & (alpha > 0.01)
    for c in range(3):
        ch = rgb[..., c]
        ch[m] = np.clip((ch[m] - 255 * (1 - alpha[m])) / alpha[m], 0, 255)
    out = Image.fromarray(np.dstack([rgb, alpha * 255]).astype("uint8"), "RGBA")
    out = out.crop(out.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox())
    out.save(os.path.join(IMG, "logo-hst.png"), optimize=True)
    s = out.resize((round(out.width * 240 / out.height), 240), Image.LANCZOS)
    s.save(os.path.join(IMG, "logo-hst.webp"), "WEBP", quality=92, exact=True)
    white = Image.new("RGBA", s.size, (255, 255, 255, 255))
    white.putalpha(s.getchannel("A"))
    white.save(os.path.join(IMG, "logo-hst-white.webp"), "WEBP", quality=92, exact=True)
    print("roundel r=%.1f c=(%.1f,%.1f)" % (r, cx, cy), out.size, s.size)


if __name__ == "__main__":
    main()


def reversed_logo():
    """White-on-colour lock-up for the transparent header over the magenta hero: roundel, wordmark and Kowa line
    in white; the figure inside the roundel is knocked out so the hero colour shows through it."""
    src = Image.open(os.path.join(IMG, "logo-hst.png")).convert("RGBA")
    a = np.asarray(src).astype(float)
    h, w, _ = a.shape
    mag = (a[..., 0] > 150) & (a[..., 1] < 120) & (a[..., 2] < 170) & (a[..., 3] > 200)
    ys, xs = np.nonzero(mag[:, : int(w * 0.45)])
    r = (xs.max() - xs.min()) / 2.0
    cx, cy = (xs.max() + xs.min()) / 2.0, ys.max() - r
    yy, xx = np.mgrid[0:h, 0:w]
    inside = np.hypot(xx - cx, yy - cy) < r - 0.5
    white = a[..., :3].min(axis=2) / 255.0
    alpha = a[..., 3] / 255.0
    alpha = np.where(inside, np.clip(1.0 - (white - 0.35) / 0.55, 0, 1) * alpha, alpha)
    out = np.dstack([np.full((h, w), 255.0), np.full((h, w), 255.0), np.full((h, w), 255.0), alpha * 255]).astype("uint8")
    o = Image.fromarray(out, "RGBA")
    o = o.resize((round(o.width * 240 / o.height), 240), Image.LANCZOS)
    o.save(os.path.join(IMG, "logo-hst-rev.webp"), "WEBP", quality=92, exact=True)
    print("reversed", o.size)


if __name__ == "__main__" and os.environ.get("HST_REV"):
    reversed_logo()


def intro_slices():
    """Full-resolution reversed logo cut into exact, padded parts for the entry animation (no sprite maths)."""
    src = Image.open(os.path.join(IMG, "logo-hst.png")).convert("RGBA")
    a = np.asarray(src).astype(float)
    h, w, _ = a.shape
    mag = (a[..., 0] > 150) & (a[..., 1] < 120) & (a[..., 2] < 170) & (a[..., 3] > 200)
    ys, xs = np.nonzero(mag[:, : int(w * 0.45)])
    r = (xs.max() - xs.min()) / 2.0
    cx, cy = (xs.max() + xs.min()) / 2.0, ys.max() - r
    yy, xx = np.mgrid[0:h, 0:w]
    inside = np.hypot(xx - cx, yy - cy) < r - 0.5
    white = a[..., :3].min(axis=2) / 255.0
    alpha = a[..., 3] / 255.0
    alpha = np.where(inside, np.clip(1.0 - (white - 0.35) / 0.55, 0, 1) * alpha, alpha)
    rev = Image.fromarray(np.dstack([np.full((h, w), 255.0)] * 3 + [alpha * 255]).astype("uint8"), "RGBA")
    al = np.asarray(rev.getchannel("A")) > 30
    cols = al.sum(axis=0)
    gap = next(x for x in range(int(w * 0.3), w) if cols[x] == 0)          # first empty column after the roundel
    start = next(x for x in range(gap, w) if cols[x] > 0)                   # wordmark starts
    rows = al[:, start:].sum(axis=1)
    bands, on = [], False
    for y, v in enumerate(rows):
        if v and not on:
            y0, on = y, True
        if not v and on:
            bands.append((y0, y)); on = False
    if on:
        bands.append((y0, h))
    bands = [bd for bd in bands if bd[1] - bd[0] > 6][:3]
    out = os.path.join(IMG, "intro")
    os.makedirs(out, exist_ok=True)
    pad = 6
    parts = {"mark": (0, 0, gap, h)}
    for name, (y0, y1) in zip(("hst", "med", "kowa"), bands):
        parts[name] = (start - pad, max(0, y0 - pad), w, min(h, y1 + pad))
    lay = {}
    for name, (x0, y0, x1, y1) in parts.items():
        rev.crop((x0, y0, x1, y1)).save(os.path.join(out, "ix-%s.webp" % name), "WEBP", quality=94, exact=True)
        lay[name] = (round(x0 / w * 100, 3), round(y0 / h * 100, 3), round((x1 - x0) / w * 100, 3), round((y1 - y0) / h * 100, 3))
    rev.save(os.path.join(out, "ix-full.webp"), "WEBP", quality=94, exact=True)
    print("logo", w, h, "layout % (left, top, width, height):", lay)
    return lay


def intro_letters():
    """Split the reversed lock-up into the roundel, the letters H S T, the seven letters of MEDICAL and the Kowa line
    (column gaps inside each text row), save each as its own image and return CSS boxes in % of the lock-up."""
    full = Image.open(os.path.join(IMG, "intro", "ix-full.webp")).convert("RGBA")
    al = np.asarray(full.getchannel("A")) > 30
    h, w = al.shape
    cols = al.sum(axis=0)
    gap = next(x for x in range(int(w * 0.3), w) if cols[x] == 0)
    start = next(x for x in range(gap, w) if cols[x] > 0)
    rows = al[:, start:].sum(axis=1)
    bands, on = [], False
    for y, v in enumerate(rows):
        if v and not on:
            y0, on = y, True
        if not v and on:
            bands.append((y0, y)); on = False
    if on:
        bands.append((y0, h))
    bands = [b for b in bands if b[1] - b[0] > 6][:3]
    out = os.path.join(IMG, "intro")
    boxes = {"mark": (0, 0, gap, h)}

    def letters(y0, y1, minw):
        c = al[y0:y1, start:].sum(axis=0)
        segs, on = [], False
        for x, v in enumerate(c):
            if v and not on:
                x0, on = x, True
            if not v and on:
                segs.append((x0 + start, x + start)); on = False
        if on:
            segs.append((x0 + start, w))
        merged = []
        for s in segs:   # glue fragments narrower than minw to their neighbour
            if merged and (s[0] - merged[-1][1] < 3 or s[1] - s[0] < minw):
                merged[-1] = (merged[-1][0], s[1])
            else:
                merged.append(s)
        return merged

    (h0, h1), (m0, m1), (k0, k1) = bands
    for i, (x0, x1) in enumerate(letters(h0, h1, 8)):
        boxes["h%d" % i] = (x0, h0, x1, h1)
    for i, (x0, x1) in enumerate(letters(m0, m1, 4)):
        boxes["m%d" % i] = (x0, m0, x1, m1)
    boxes["kowa"] = (start, k0, w, k1)
    pad = 4
    css = []
    for name, (x0, y0, x1, y1) in boxes.items():
        x0p, y0p, x1p, y1p = max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)
        full.crop((x0p, y0p, x1p, y1p)).save(os.path.join(out, "ix-%s.webp" % name), "WEBP", quality=95, exact=True)
        css.append(".ix-%s{left:%.3f%%;top:%.3f%%;width:%.3f%%}" % (name, x0p / w * 100, y0p / h * 100, (x1p - x0p) / w * 100))
    print(" ".join(sorted(boxes)))
    return "\n".join(css)


def roundel_anchor():
    """Where the magenta roundel sits inside the lock-up, in % of the lock-up box. The entry intro's ripple, rings (phones) and aroma
    leaves are anchored to it (assets/css/intro.css: .ix-ripple, .ix-aroma, the phone .ix-ring). Measured on logo-hst.png:
    centre x 21.49%, centre y 44.36% (not 50%: the Kowa line hangs below the roundel), diameter 41.8% of the width.
    Re-check after re-cutting the logo:  python -c "import sys; sys.path.insert(0,'_src'); import logo_cutout; logo_cutout.roundel_anchor()" """
    src = Image.open(os.path.join(IMG, "logo-hst.png")).convert("RGBA")
    a = np.asarray(src).astype(float)
    h, w, _ = a.shape
    mag = (a[..., 0] > 150) & (a[..., 1] < 120) & (a[..., 2] < 170) & (a[..., 3] > 200)
    ys, xs = np.nonzero(mag[:, : int(w * 0.45)])
    r = (xs.max() - xs.min()) / 2.0
    cx, cy = (xs.max() + xs.min()) / 2.0, ys.max() - r
    out = {"cx": round(float(cx / w * 100), 2), "cy": round(float(cy / h * 100), 2), "diameter": round(float(2 * r / w * 100), 1)}
    print("roundel anchor, % of the lock-up:", out)
    return out
