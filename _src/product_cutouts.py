"""
Transparent packshots for every product (assets/img/products/pXX.webp + pXX-thumb.webp).

    python _src/product_cutouts.py <catalogue.pdf> <catalogue.json> [--sheet out.jpg] [--only p03,p07]

catalogue.json is the per-page extraction index from catalogue_parse.py (page, w, h of the product image).
For each product page the matching PDF image is re-extracted at full resolution: its own alpha mask (smask)
when the PDF carries one, otherwise a border flood-fill matte that stops at near-white pixels and at image
edges (hero_cutouts.matte). The cut-out is centred on a square transparent canvas with a 5% margin so every
template keeps its 1:1 box. The white-ground originals stay as pXX-white.webp for OG/schema images.
"""
import json, os, sys, datetime
import pymupdf
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hero_cutouts import from_pdf, matte

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "assets", "img", "products")
# per-image matte tuning where the default leaks or eats into a pale pack
TUNE = {}


def square(im, margin=0.05):
    side = round(max(im.size) / (1 - 2 * margin))
    c = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    c.alpha_composite(im, ((side - im.width) // 2, (side - im.height) // 2))
    return c


def main(pdf, index, sheet=None, only=None):
    doc = pymupdf.open(pdf)
    rows = json.load(open(index, encoding="utf-8"))
    tiles = []
    for r in rows:
        name = os.path.splitext(os.path.basename(r["img"]))[0]
        if only and name not in only:
            continue
        page = doc[int(r["page"]) - 1]
        hit = [i for i in page.get_images(full=True) if i[2] == int(r["w"]) and i[3] == int(r["h"])]
        if not hit:
            print("!! no image match", name); continue
        xref, smask = hit[0][0], hit[0][1]
        im = from_pdf(doc, xref, smask)
        if not smask:
            im = matte(im, **TUNE.get(name, {}))
        bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        im = square(im.crop(bb))
        how = "PDF alpha mask (smask)" if smask else "border flood-fill matte with a gradient barrier"
        for suffix, edge, q in (("", 900, 86), ("-thumb", 360, 82)):
            s = min(1.0, edge / im.width)
            o = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS) if s < 1 else im
            fn = os.path.join(OUT, "%s%s.webp" % (name, suffix))
            o.save(fn, "WEBP", quality=q, method=6, exact=True)
            with open(fn + ".json", "w", encoding="utf-8") as f:
                json.dump({"prompt": "Origin: product packshot extracted from the client-supplied HST Medical product-sheet catalogue PDF (Heyzine flipbook 1cbc07dcc6), page %s; transparent background from the %s, centred on a square transparent canvas (5%% margin), %d px max, WebP q%d. Not AI-generated." % (r["page"], how, edge, q),
                           "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat()}, f, indent=2)
        print(name, "smask" if smask else "matte", im.size)
        t = Image.new("RGBA", im.size, (179, 18, 76, 255)); t.alpha_composite(im)
        tiles.append((name, t.convert("RGB").resize((220, 220), Image.LANCZOS)))
    if sheet and tiles:
        from PIL import ImageDraw
        cols = 9
        S = Image.new("RGB", (cols * 224, ((len(tiles) + cols - 1) // cols) * 244), (40, 40, 40))
        d = ImageDraw.Draw(S)
        for k, (n, t) in enumerate(tiles):
            x, y = (k % cols) * 224, (k // cols) * 244
            S.paste(t, (x + 2, y + 2)); d.text((x + 6, y + 226), n, fill=(255, 255, 255))
        S.save(sheet, quality=85)


if __name__ == "__main__":
    a = sys.argv[1:]
    sheet = a[a.index("--sheet") + 1] if "--sheet" in a else None
    only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None
    main(a[0], a[1], sheet, only)
