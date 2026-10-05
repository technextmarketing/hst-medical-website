"""
Home hero cut-outs: the five Rheuma-Salve formats as transparent WebP packshots.

    python _src/hero_cutouts.py <path-to-catalogue.pdf>

Source is the client-supplied product-sheet catalogue PDF (Heyzine flipbook 1cbc07dcc6). The balm and the
Medi-Stick ship with their own alpha masks (smask) in the PDF; the creme, liniment and patch sit on white, so
their matte is a border flood fill that stops at near-white pixels AND at image edges (gradient barrier), which
keeps white tubes and caps intact. Writes assets/img/hero/rs-<format>.webp (long edge <= 760 px) plus a
120 px thumbnail and a provenance sidecar for each.
"""
import io, json, os, sys, datetime
from collections import deque
import numpy as np
import pymupdf
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "assets", "img", "hero")
# format -> (catalogue page, image xref, smask xref or 0)
JOBS = {"balm": (3, 11, 10), "creme": (4, 24, 0), "liniment": (5, 30, 0), "patch": (6, 39, 0), "stick": (7, 56, 55)}


def from_pdf(doc, xref, smask):
    pix = pymupdf.Pixmap(doc, xref)
    if pix.n - pix.alpha >= 4:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    if pix.alpha:
        pix = pymupdf.Pixmap(pix, 0)
    im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    if smask:
        m = Image.open(io.BytesIO(pymupdf.Pixmap(doc, smask).tobytes("png"))).convert("L").resize(im.size)
        im = im.convert("RGBA")
        im.putalpha(m)
    return im


def matte(im, thr=248, gthr=4.0):
    a = np.asarray(im.convert("RGB")).astype(float)
    g = a.mean(axis=2)
    gx = np.zeros_like(g); gy = np.zeros_like(g)
    gx[:, 1:-1] = g[:, 2:] - g[:, :-2]
    gy[1:-1, :] = g[2:, :] - g[:-2, :]
    ok = (a.min(axis=2) >= thr) & (np.hypot(gx, gy) < gthr)
    h, w = g.shape
    bg = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if ok[y, x] and not bg[y, x]:
                bg[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if ok[y, x] and not bg[y, x]:
                bg[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and ok[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True; q.append((ny, nx))
    alpha = Image.fromarray(np.where(bg, 0, 255).astype("uint8")).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out


def fit(im, edge):
    s = min(1.0, edge / max(im.size))
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS) if s < 1 else im


def main(pdf):
    os.makedirs(OUT, exist_ok=True)
    doc = pymupdf.open(pdf)
    for fmt, (page, xref, smask) in JOBS.items():
        im = from_pdf(doc, xref, smask)
        if not smask:
            im = matte(im)
        im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
        for suffix, edge, q in (("", 760, 86), ("-thumb", 120, 82)):
            o = fit(im, edge)
            name = "rs-%s%s.webp" % (fmt, suffix)
            o.save(os.path.join(OUT, name), "WEBP", quality=q, method=6, exact=True)
            how = "PDF alpha mask (smask)" if smask else "border flood-fill matte with a gradient barrier"
            with open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8") as f:
                json.dump({"prompt": "Origin: Rheuma-Salve %s packshot extracted from the client-supplied HST Medical product-sheet catalogue PDF (Heyzine flipbook 1cbc07dcc6), page %d; transparent background from the %s; long edge %d px max, WebP q%d. Not AI-generated." % (fmt, page, how, edge, q),
                           "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat()}, f, indent=2)
            print(name, o.size, os.path.getsize(os.path.join(OUT, name)))


if __name__ == "__main__":
    main(sys.argv[1])
