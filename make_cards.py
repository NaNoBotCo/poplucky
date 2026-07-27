#!/usr/bin/env python3
"""
make_cards.py — og:image share cards, one per page.

Masters land in docs/cards/. Run before (or via) build.py.

Text shaping note: Pillow here has no raqm, so Thai will not shape correctly.
Cards therefore use the English name only, which is Latin for every figure in
the catalogue. Thai-script cards need a shaping engine — logged in the vault
as an open question rather than rendered badly.
"""
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed; skipping cards.")
    sys.exit(0)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs", "cards")

W, H = 1200, 630
INK = (36, 31, 43)
DIM = (120, 112, 134)
BG = (251, 247, 244)
PINK = (255, 111, 165)
GRAPE = (123, 92, 255)
GOLD = (247, 179, 43)
MINT = (62, 207, 174)

FONT_DIRS = ["/System/Library/Fonts/Supplemental", "/System/Library/Fonts",
             "/Library/Fonts"]
# rounded first: it matches the site's ui-rounded stack and the toy subject
BOLD_NAMES = ["Arial Rounded Bold.ttf", "Arial Bold.ttf", "Avenir Next.ttc",
              "HelveticaNeue.ttc", "Helvetica.ttc"]
REG_NAMES = ["Avenir Next.ttc", "Arial.ttf", "HelveticaNeue.ttc", "Helvetica.ttc"]


def find_font(names):
    for n in names:
        for d in FONT_DIRS:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    return None


BOLD_PATH = find_font(BOLD_NAMES)
REG_PATH = find_font(REG_NAMES)


def font(size, bold=False):
    p = BOLD_PATH if bold else REG_PATH
    if not p:
        return ImageFont.load_default()
    try:
        # index 1 in Avenir Next.ttc is a heavier cut
        return ImageFont.truetype(p, size, index=1 if (bold and p.endswith(".ttc"))
                                  else 0)
    except Exception:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def backdrop(secret=False):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # soft vertical wash
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=lerp(BG, (247, 240, 250), t))
    # corner blooms
    bloom = Image.new("RGB", (W, H), BG)
    bd = ImageDraw.Draw(bloom)
    bd.ellipse([-260, -320, 720, 400], fill=lerp(BG, PINK, .22))
    bd.ellipse([620, -260, 1500, 380], fill=lerp(BG, GRAPE, .18))
    img = Image.blend(img, bloom, 0.55)
    if secret:
        # holo ribbon along the top for chase figures
        d = ImageDraw.Draw(img)
        stops = [GOLD, PINK, GRAPE, MINT, GOLD]
        for x in range(W):
            t = x / W * (len(stops) - 1)
            i = min(int(t), len(stops) - 2)
            d.line([(x, 0), (x, 13)], fill=lerp(stops[i], stops[i + 1], t - i))
    return img


def fit(draw, text, size, bold, maxw):
    f = font(size, bold)
    while size > 26:
        if draw.textlength(text, font=f) <= maxw:
            return f
        size -= 4
        f = font(size, bold)
    return f


def card(path, title, kicker="", sub="", secret=False):
    img = backdrop(secret)
    d = ImageDraw.Draw(img)
    x, maxw = 84, W - 168

    if kicker:
        fk = font(30, True)
        d.text((x, 132), kicker.upper(), font=fk, fill=PINK if secret else GRAPE)

    ft = fit(d, title, 104, True, maxw)
    d.text((x, 196), title, font=ft, fill=INK)

    if sub:
        fs = fit(d, sub, 40, False, maxw)
        d.text((x, 348), sub, font=fs, fill=DIM)

    # wordmark
    fw = font(34, True)
    d.text((x, H - 96), "Poplucky", font=fw, fill=INK)
    fu = font(28, False)
    d.text((x + int(d.textlength("Poplucky", font=fw)) + 18, H - 92),
           "poplucky.com", font=fu, fill=DIM)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "PNG", optimize=True)


def build_cards(ips, series, figures):
    os.makedirs(OUT, exist_ok=True)
    by_ip = {i["id"]: i for i in ips}
    by_series = {s["id"]: s for s in series}
    n = 0

    card(os.path.join(OUT, "home.png"), "Poplucky", "",
         "Every blind box, catalogued in the words collectors use.")
    n += 1
    card(os.path.join(OUT, "iso.png"), "In Search Of", "open questions",
         "What this catalogue does not know yet.")
    n += 1
    card(os.path.join(OUT, "shelf.png"), "My Shelf", "collection",
         "What you have, what you seek, and a card to trade with.")
    n += 1

    for i in ips:
        card(os.path.join(OUT, "ip-%s.png" % i["id"]),
             i.get("name_en", i["id"]), "character",
             i.get("universe_en", "") or (i.get("artist", "") and
                                          "by " + i["artist"]))
        n += 1
    for s in series:
        ip = by_ip.get(s.get("ip"), {})
        bits = [x for x in [ip.get("name_en", ""), str(s.get("released", "") or "")]
                if x]
        card(os.path.join(OUT, "series-%s.png" % s["id"]),
             s.get("name_en", s["id"]), "series", " · ".join(bits))
        n += 1
    for f in figures:
        s = by_series.get(f.get("series"), {})
        sec = f.get("pull") == "secret"
        bits = [x for x in [s.get("name_en", ""), str(f.get("color", "") or ""),
                            str(f.get("odds", "") or "")] if x]
        card(os.path.join(OUT, "figure-%s.png" % f["id"]),
             f.get("name_en", f["id"]), "secret" if sec else "figure",
             " · ".join(bits), secret=sec)
        n += 1
    return n


if __name__ == "__main__":
    sys.path.insert(0, ROOT)
    import build as B
    cnt = build_cards(B.load("ip"), B.load("series"), B.load("figure"))
    print("wrote %d cards -> docs/cards/" % cnt)
