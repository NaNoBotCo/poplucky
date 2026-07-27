# -*- coding: utf-8 -*-
"""
art.py — procedural blind-box artwork.

WHY BOXES AND NOT FIGURES
Poplucky shows no Pop Mart product photography, and drawing the characters
would be derivative work wearing a different hat. But a blind-box collector
does not face a figure — they face a sealed box, and the toy inside is
unknown until it is opened. So the box is the icon here. It is honest to the
hobby and it is entirely our own drawing.

Every box is deterministic: the same figure always yields the same box, so
the art is stable across builds and across the site.

Owned boxes open. That state is driven by CSS from the shelf, not from here.
"""
import colorsys
import hashlib

# Named colours the catalogue records, mapped to a hue we can build a box from.
COLOR_HUE = {
    "yellow": 47, "gold": 42, "cream-yellow": 50,
    "gray": 220, "grey": 220,
    "brown": 24, "golden-brown": 33, "chestnut": 18,
    "blue": 213, "green": 158, "mint": 165,
    "pink": 338, "red": 356, "orange": 26, "purple": 268,
    "pink and yellow": 350,
}
IP_HUE = {"labubu": 338, "molly": 268, "skullpanda": 220, "crybaby": 199}


def _seed(s):
    return int(hashlib.sha1(s.encode("utf-8")).hexdigest()[:8], 16)


def _hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360.0, l, s)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def palette(fig, ip_id):
    """(base, light, dark, accent) for this figure's box."""
    col = str(fig.get("color", "") or "").lower().strip()
    if col in COLOR_HUE:
        hue = COLOR_HUE[col]
    else:
        # no colour recorded: derive a stable hue from the id, nudged toward
        # the character's own family hue so a series still reads as a set
        base = IP_HUE.get(ip_id, 300)
        hue = (base + (_seed(fig.get("id", "x")) % 70) - 35) % 360
    return (_hex(hue, .62, .62), _hex(hue, .70, .76),
            _hex(hue, .55, .45), _hex((hue + 32) % 360, .70, .70))


HOLO = ["#f7b32b", "#ff6fa5", "#7b5cff", "#3ecfae", "#f7b32b"]


def box_svg(fig, ip_id, size=None, decorative=True):
    """Inline SVG for one blind box. Deterministic from the figure id."""
    fid = fig.get("id", "x")
    secret = fig.get("pull") == "secret"
    base, light, dark, accent = palette(fig, ip_id)
    n = _seed(fid)
    uid = "b" + hashlib.sha1(fid.encode("utf-8")).hexdigest()[:7]

    # a little variation so a shelf does not look stamped
    dots = n % 3            # 0 none, 1 dots, 2 stars
    band = (n >> 3) % 2     # ribbon or plain sash
    tilt = ((n >> 6) % 5) - 2

    if secret:
        stops = "".join(
            '<stop offset="%d%%" stop-color="%s"/>' % (i * 25, c)
            for i, c in enumerate(HOLO))
        body_fill = "url(#%s-holo)" % uid
        lid_fill = "url(#%s-holo)" % uid
        defs = ('<linearGradient id="%s-holo" x1="0" y1="0" x2="1" y2="1">%s'
                "</linearGradient>" % (uid, stops))
    else:
        body_fill = "url(#%s-g)" % uid
        lid_fill = "url(#%s-l)" % uid
        defs = (
            '<linearGradient id="%s-g" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0%%" stop-color="%s"/>'
            '<stop offset="100%%" stop-color="%s"/></linearGradient>'
            '<linearGradient id="%s-l" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0%%" stop-color="%s"/>'
            '<stop offset="100%%" stop-color="%s"/></linearGradient>'
            % (uid, light, dark, uid, light, base)
        )

    pattern = ""
    if dots == 1:
        pattern = "".join(
            '<circle cx="%d" cy="%d" r="2.6" fill="#fff" opacity=".30"/>'
            % (26 + (i % 3) * 24, 74 + (i // 3) * 18) for i in range(6))
    elif dots == 2:
        pattern = "".join(
            '<path d="M%d %d l2.4 5 5.2.6-3.9 3.6 1.1 5.2-4.8-2.7-4.8 2.7 '
            '1.1-5.2-3.9-3.6 5.2-.6z" fill="#fff" opacity=".28"/>'
            % (24 + (i % 2) * 42, 72 + (i // 2) * 22) for i in range(4))

    if band:
        ribbon = ('<rect x="53" y="58" width="14" height="62" fill="#fff" '
                  'opacity=".34"/>'
                  '<rect x="12" y="82" width="96" height="12" fill="#fff" '
                  'opacity=".22"/>')
    else:
        ribbon = ('<path d="M12 96 L108 78 L108 92 L12 110 Z" fill="#fff" '
                  'opacity=".20"/>')

    lid_ribbon = ('<rect x="53" y="30" width="14" height="26" fill="#fff" '
                  'opacity=".34"/>') if band else ""

    shine = ('<path d="M18 62 L44 62 L26 122 L14 122 Z" fill="#fff" '
             'opacity=".13"/>')

    sizing = ' style="width:%s"' % size if size else ""
    aria = ' aria-hidden="true" focusable="false"' if decorative else ""

    return (
        '<svg class="box" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg"'
        '%s%s><defs>%s</defs>'
        '<ellipse class="box-shadow" cx="60" cy="128" rx="40" ry="6" '
        'fill="#000" opacity=".13"/>'
        '<g class="box-body">'
        '<rect x="12" y="56" width="96" height="66" rx="9" fill="%s"/>'
        '%s%s%s</g>'
        '<g class="box-lid" style="transform-origin:60px 56px">'
        '<g transform="rotate(%d 60 46)">'
        '<rect x="6" y="30" width="108" height="28" rx="8" fill="%s"/>'
        '%s</g></g>'
        "</svg>"
        % (sizing, aria, defs, body_fill, ribbon, pattern, shine,
           tilt, lid_fill, lid_ribbon)
    )


# ---------------------------------------------------------------------------
# "What 1 in 144 looks like" — the odds, as a wall of boxes
# ---------------------------------------------------------------------------
def odds_wall(odds_str, uid):
    """Render 1/N as N tiny boxes with one lit. Returns '' if unparseable."""
    try:
        n = int(str(odds_str).split("/")[1].split()[0])
    except Exception:
        return ""
    if n < 2 or n > 400:
        return ""
    lit = (n * 7 // 11) % n          # stable, not the first or last cell
    cols = 24 if n > 100 else (12 if n > 40 else 8)
    cells = []
    for i in range(n):
        c = "cell lit" if i == lit else "cell"
        cells.append('<span class="%s"></span>' % c)
    return (
        '<figure class="oddswall" style="--cols:%d">'
        '<div class="wall">%s</div>'
        "</figure>" % (cols, "".join(cells))
    )


# ---------------------------------------------------------------------------
# CSS for the artwork, the odds wall, sharing and the contribute prompts
# ---------------------------------------------------------------------------
ART_CSS = """
/* --- the box ------------------------------------------------------------ */
.box{display:block;width:100%;height:auto;overflow:visible}
.box-lid{transition:transform .42s cubic-bezier(.34,1.6,.5,1)}
.card:hover .box-lid{transform:translateY(-7px) rotate(-4deg)}
.shelf-item.owned .box-lid{transform:translateY(-19px) rotate(-13deg)}
.shelf-item.owned .box-body{filter:saturate(1.12)}
.boxwrap{position:relative;margin:-4px 0 9px}
.card .boxwrap{max-width:118px}
/* an opened box gets a glow where the lid was */
.shelf-item.owned .boxwrap::after{content:"";position:absolute;left:22%;
  right:22%;top:34%;height:16px;border-radius:50%;
  background:radial-gradient(ellipse,rgba(255,233,168,.85),transparent 70%);
  pointer-events:none}
@media (prefers-reduced-motion:reduce){.box-lid{transition:none}}
/* figure page hero */
.herobox{display:flex;align-items:flex-end;gap:22px;flex-wrap:wrap;margin:6px 0 4px}
.herobox .boxwrap{width:148px;max-width:38vw;margin:0}
.herobox .heroname{flex:1;min-width:210px}
.herobox h1{margin:0 0 .1em}
/* --- odds as a wall of boxes -------------------------------------------- */
.oddswall{margin:14px 0 4px;padding:0}
.oddswall .wall{display:grid;grid-template-columns:repeat(var(--cols),1fr);
  gap:3px;max-width:560px}
.oddswall .cell{aspect-ratio:3/4;border-radius:2px;background:var(--line);
  opacity:.62}
.oddswall .cell.lit{background:linear-gradient(150deg,var(--gold),var(--pink));
  opacity:1;box-shadow:0 0 0 2px rgba(255,111,165,.30),0 0 13px rgba(247,179,43,.65);
  animation:litpulse 2.9s ease-in-out infinite}
@keyframes litpulse{0%,100%{transform:scale(1)}50%{transform:scale(1.32)}}
@media (prefers-reduced-motion:reduce){.oddswall .cell.lit{animation:none}}
.oddscap{color:var(--dim);font-size:.88rem;margin:7px 0 0}
/* --- share row ---------------------------------------------------------- */
.share{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:26px 0 0}
.share .lbl{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;
  color:var(--dim);margin-right:2px}
.share a,.share button{font:inherit;font-size:.88rem;font-weight:650;
  cursor:pointer;text-decoration:none;border:1px solid var(--line);
  background:var(--card);color:var(--ink);padding:7px 14px;border-radius:11px;
  backdrop-filter:blur(8px);transition:transform .16s,border-color .16s}
.share a:hover,.share button:hover{transform:translateY(-2px);border-color:var(--pink)}
.share .line:hover{border-color:#06c755}
/* --- contribute ---------------------------------------------------------- */
.helpout{border:1px dashed var(--line);border-radius:14px;padding:14px 17px;
  margin:18px 0;background:var(--card)}
.helpout p{margin:0 0 10px;font-size:.94rem;color:var(--dim)}
.helpout a{display:inline-block;text-decoration:none;font-weight:700;
  font-size:.9rem;border:1px solid transparent;color:#fff;padding:8px 16px;
  border-radius:11px;background:linear-gradient(120deg,var(--grape),var(--pink));
  transition:transform .16s}
.helpout a:hover{transform:translateY(-2px)}
.iso .fix{margin-left:auto;font-size:.8rem;text-decoration:none;color:var(--grape);
  border:1px solid var(--line);border-radius:999px;padding:3px 11px;
  white-space:nowrap;transition:transform .15s,border-color .15s}
.iso .fix:hover{transform:translateY(-2px);border-color:var(--grape)}
"""
