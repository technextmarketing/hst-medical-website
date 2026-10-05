"""
Hero v6 pack compositions (box + product, like the balm and creme shots), from the catalogue PDF.

    python _src/hero_compose.py <catalogue.pdf>

liniment = blister card (p5 x28) + roll-on bottle (p5 x32); patch = the pouch only (p6 x39, loose sheets cropped);
stick = carton (p7 x52) + stick (p7 x56, own alpha). Mattes via hero_cutouts.matte. Overwrites
assets/img/hero/rs-{liniment,patch,stick}.webp (+ -thumb) and their provenance sidecars.
"""
import os, sys, json, datetime
import pymupdf
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hero_cutouts import from_pdf, matte, fit

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "img", "hero")


def cut(doc, xref, smask=0):
    im = from_pdf(doc, xref, smask)
    if not smask:
        im = matte(im)
    return im.crop(im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())


def pair(back, front, front_h=0.78, overlap=0.30, drop=0.0):
    fh = round(back.height * front_h)
    front = front.resize((round(front.width * fh / front.height), fh), Image.LANCZOS)
    W = back.width + front.width - round(front.width * overlap)
    H = max(back.height, fh + round(back.height * drop))
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c.alpha_composite(back, (0, H - back.height))
    c.alpha_composite(front, (W - front.width, H - fh))
    return c


PRODUCT = {"liniment": "p05", "patch": "p06", "stick": "p07"}  # the same compositions become the product images


def save(name, im, how):
    from product_cutouts import square
    pid = PRODUCT.get(name)
    if pid:
        sq = square(im)
        for suffix, edge, q in (("", 900, 86), ("-thumb", 360, 82)):
            s_ = min(1.0, edge / sq.width)
            o = sq.resize((round(sq.width * s_), round(sq.height * s_)), Image.LANCZOS) if s_ < 1 else sq
            fn = os.path.join(os.path.dirname(OUT), "products", "%s%s.webp" % (pid, suffix))
            o.save(fn, "WEBP", quality=q, method=6, exact=True)
            json.dump({"prompt": "Origin: Rheuma-Salve %s pack composition from packshots in the client-supplied HST Medical product-sheet catalogue PDF (Heyzine flipbook 1cbc07dcc6): %s; transparent background, centred on a square transparent canvas (5%% margin), %d px max, WebP q%d. Not AI-generated." % (name, how, edge, q),
                       "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat()}, open(fn + ".json", "w", encoding="utf-8"), indent=2)
            print(os.path.basename(fn), o.size)
    for suffix, edge, q in (("", 760, 86), ("-thumb", 120, 82)):
        o = fit(im, edge)
        fn = os.path.join(OUT, "rs-%s%s.webp" % (name, suffix))
        o.save(fn, "WEBP", quality=q, method=6, exact=True)
        json.dump({"prompt": "Origin: Rheuma-Salve %s pack composition from packshots in the client-supplied HST Medical product-sheet catalogue PDF (Heyzine flipbook 1cbc07dcc6): %s; transparent background; long edge %d px max, WebP q%d. Not AI-generated." % (name, how, edge, q),
                   "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat()}, open(fn + ".json", "w", encoding="utf-8"), indent=2)
        print(os.path.basename(fn), o.size)


def main(pdf):
    doc = pymupdf.open(pdf)
    save("liniment", pair(cut(doc, 28), cut(doc, 32), front_h=0.74, overlap=0.15), "page 5 blister card + roll-on bottle")
    p = cut(doc, 39)
    p = p.crop((0, 0, p.width, round(p.height * 0.60)))
    p = p.crop(p.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
    save("patch", p, "page 6 pouch, loose patches cropped out")
    save("stick", pair(cut(doc, 52), cut(doc, 56, 55), front_h=0.80, overlap=0.06), "page 7 carton + Medi-Stick")


if __name__ == "__main__":
    main(sys.argv[1])
