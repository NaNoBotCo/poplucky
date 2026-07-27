#!/usr/bin/env python3
"""
build.py — Poplucky static site generator.

vault/ (Obsidian, canonical)  ->  docs/ (GitHub Pages / Cloudflare Pages)

Stdlib only, Python 3.9+. Run:  python3 build.py
"""
import html
import json
import os
import re
import shutil
import sys

import art as _art
import shelf as _shelf

ROOT = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.join(ROOT, "vault")
OUT = os.path.join(ROOT, "docs")

SITE = "https://poplucky.net"
LANGS = ["en", "th", "zh"]
LANG_LABEL = {"en": "EN", "th": "ไทย", "zh": "中文"}

# ---------------------------------------------------------------------------
# UI strings. Every visible chrome string lives here; nothing is hardcoded in
# a template. Missing translations fall back to English and are counted as gaps.
# ---------------------------------------------------------------------------
UI = {
    "tagline": {
        "en": "Every blind box, catalogued in the words collectors actually use.",
        "th": "ทุกกล่องสุ่ม จัดหมวดด้วยคำที่นักสะสมใช้จริง",
        "zh": "每一个盲盒，用收藏者真正使用的词语编目。",
    },
    "characters": {"en": "Characters", "th": "ตัวละคร", "zh": "角色"},
    "series": {"en": "Series", "th": "ซีรีส์", "zh": "系列"},
    "figures": {"en": "Figures", "th": "ตัว", "zh": "款"},
    "secret": {"en": "secret", "th": "ซีเคร็ท", "zh": "隐藏款"},
    "regular": {"en": "regular", "th": "ธรรมดา", "zh": "常规款"},
    "odds": {"en": "Odds", "th": "โอกาสได้", "zh": "抽中概率"},
    "artist": {"en": "Artist", "th": "ศิลปิน", "zh": "设计师"},
    "universe": {"en": "Universe", "th": "จักรวาล", "zh": "系列宇宙"},
    "form": {"en": "Form", "th": "รูปแบบ", "zh": "形式"},
    "scope": {"en": "Edition", "th": "รุ่นวางจำหน่าย", "zh": "发行范围"},
    "released": {"en": "Released", "th": "วางจำหน่าย", "zh": "发售"},
    "setsize": {"en": "Set size", "th": "จำนวนในชุด", "zh": "整套数量"},
    "where": {"en": "Where it sits", "th": "อยู่ตรงไหน", "zh": "所属"},
    "prov": {"en": "Where this comes from", "th": "ที่มาของข้อมูล",
             "zh": "资料来源"},
    "field": {"en": "Field", "th": "ข้อมูล", "zh": "字段"},
    "value": {"en": "Value", "th": "ค่า", "zh": "内容"},
    "source": {"en": "Source", "th": "แหล่งที่มา", "zh": "来源"},
    "iso": {"en": "In Search Of", "th": "ยังตามหาอยู่", "zh": "仍在寻找"},
    "iso_blurb": {
        "en": "What this catalogue does not know yet. Every line is an invitation.",
        "th": "สิ่งที่แคตตาล็อกนี้ยังไม่รู้ ทุกบรรทัดคือคำเชิญ",
        "zh": "本目录尚未收录的内容。每一条都是一份邀请。",
    },
    "iso_nav": {"en": "In Search Of", "th": "ยังตามหาอยู่", "zh": "仍在寻找"},
    "contested": {"en": "Sources disagree", "th": "แหล่งข้อมูลไม่ตรงกัน",
                  "zh": "资料来源有出入"},
    "unverified": {"en": "not yet verified", "th": "ยังไม่ได้ตรวจสอบ",
                   "zh": "尚未核实"},
    "roster_partial": {
        "en": "Roster incomplete — some figures in this set are not yet recorded.",
        "th": "รายชื่อยังไม่ครบ — บางตัวในชุดนี้ยังไม่ได้บันทึก",
        "zh": "名单尚不完整 — 本套中部分款式尚未收录。",
    },
    "colour": {"en": "Colour", "th": "สี", "zh": "颜色"},
    "naming": {"en": "Names", "th": "ชื่อ", "zh": "名称"},
    "home": {"en": "Home", "th": "หน้าแรก", "zh": "首页"},
    "notaffil": {
        "en": ("A collector's fan catalogue. Not affiliated with, endorsed by, or "
               "connected to POP MART. All character and series names belong to "
               "their creators and are used here to refer to the things they name."),
        "th": ("แคตตาล็อกของนักสะสม ไม่ได้มีส่วนเกี่ยวข้องหรือได้รับการรับรอง"
               "จาก POP MART ชื่อตัวละครและซีรีส์ทั้งหมดเป็นของผู้สร้าง "
               "ใช้ที่นี่เพื่ออ้างถึงสิ่งที่ชื่อนั้นเรียกเท่านั้น"),
        "zh": ("收藏者的同好目录。与 POP MART 无从属、认可或关联关系。"
               "所有角色与系列名称归其创作者所有，此处仅用于指称。"),
    },
}

UI.update(_shelf.SHELF_UI)
UI.update({
    "share": {"en": "Share", "th": "แชร์", "zh": "分享"},
    "copylink": {"en": "Copy link", "th": "คัดลอกลิงก์", "zh": "复制链接"},
    "linkcopied": {"en": "Link copied", "th": "คัดลอกลิงก์แล้ว", "zh": "链接已复制"},
    "odds_cap": {
        "en": "One lit box in %s. That is the chance, drawn to scale.",
        "th": "กล่องที่สว่าง 1 ใบ จาก %s นี่คือโอกาสจริง วาดตามสัดส่วน",
        "zh": "%s 里只有一个亮着。这就是概率，按比例画出来。",
    },
    "help_title": {"en": "Know this one?", "th": "รู้เรื่องนี้ไหม", "zh": "你知道吗？"},
    "help_contested": {
        "en": ("Sources disagree here and we would rather be corrected than "
               "confident. If you own one, you can settle it."),
        "th": ("ตรงนี้แหล่งข้อมูลไม่ตรงกัน เรายอมถูกแก้ดีกว่าเดาแล้วมั่นใจ "
               "ถ้าคุณมีตัวจริง คุณช่วยยืนยันได้"),
        "zh": "这里资料有出入，我们宁愿被纠正也不愿自信地写错。你要是有实物，就能定案。",
    },
    "help_gap": {
        "en": "This one is simply missing. If you know it, it is yours to add.",
        "th": "อันนี้ยังขาดอยู่ ถ้าคุณรู้ ก็เติมได้เลย",
        "zh": "这一条还缺着。你要是知道，就由你来补。",
    },
    "help_cta": {"en": "Tell us what you know", "th": "บอกสิ่งที่คุณรู้",
                 "zh": "告诉我们你知道的"},
    "fix": {"en": "help", "th": "ช่วย", "zh": "帮忙"},
})

FALLBACK_NOTE = {"en": "", "th": " ", "zh": " "}


def t(key, lang):
    d = UI.get(key, {})
    return d.get(lang) or d.get("en") or key


# ---------------------------------------------------------------------------
# Minimal frontmatter parser (flat key: value, YAML subset we author ourselves)
# ---------------------------------------------------------------------------
def parse_note(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    meta, body = {}, raw
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            head = raw[3:end]
            body = raw[end + 4:].lstrip("\n")
            for line in head.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or ":" not in line:
                    continue
                k, v = line.split(":", 1)
                v = v.strip()
                if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
                    v = v[1:-1].replace('\\"', '"')
                if v.lower() in ("true", "false"):
                    v = v.lower() == "true"
                elif re.match(r"^-?\d+$", v):
                    v = int(v)
                meta[k.strip()] = v
    return meta, body


def load(kind):
    d = os.path.join(VAULT, kind)
    out = []
    if not os.path.isdir(d):
        return out
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".md"):
            m, b = parse_note(os.path.join(d, fn))
            m["_body"] = b
            m["_kind"] = kind
            out.append(m)
    return out


# ---------------------------------------------------------------------------
# Markdown-lite for note bodies: **bold**, *em*, paragraphs
# ---------------------------------------------------------------------------
def md(text):
    if not text:
        return ""
    parts = []
    for para in re.split(r"\n\s*\n", text.strip()):
        p = html.escape(para.strip())
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", p)
        p = p.replace("\n", " ")
        parts.append("<p>%s</p>" % p)
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Names + provenance
# ---------------------------------------------------------------------------
def names(rec):
    """Return {lang: (text, is_fallback)}."""
    en = rec.get("name_en") or rec.get("id", "")
    out = {}
    for lg in LANGS:
        v = rec.get("name_%s" % lg)
        if v:
            out[lg] = (v, False)
        else:
            out[lg] = (en, lg != "en")
    return out


def name_span(rec, cls=""):
    n = names(rec)
    bits = []
    for lg in LANGS:
        txt, fb = n[lg]
        extra = " nm-fb" if fb else ""
        bits.append(
            '<span class="nm%s" data-lang="%s" title="%s">%s</span>'
            % (extra, lg, "no name recorded in this language" if fb else "",
               html.escape(txt))
        )
    return '<span class="%s">%s</span>' % (cls, "".join(bits))


SRC_LABEL = {
    "official": "POP MART",
    "community": "collector community",
    "inference": "unverified inference",
    "": "not recorded",
}


def src_cell(v):
    if not v:
        return '<span class="src src-none">not recorded</span>'
    if v.startswith("http"):
        pieces = []
        for u in [x.strip() for x in v.split("|")]:
            host = re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
            pieces.append('<a class="src src-url" href="%s" rel="nofollow noopener" '
                          'target="_blank">%s</a>' % (html.escape(u), html.escape(host)))
        return " · ".join(pieces)
    cls = "src-inf" if v == "inference" else "src-ok"
    return '<span class="src %s">%s</span>' % (cls, SRC_LABEL.get(v, html.escape(v)))


def ui_span_fmt(key, *a):
    """ui_span for UI strings that contain a %s placeholder."""
    return "".join(
        '<span data-i18n="%s">%s</span>' % (lg, html.escape(t(key, lg) % a))
        for lg in LANGS)


def ui_span(key):
    return "".join('<span data-i18n="%s">%s</span>' % (lg, html.escape(t(key, lg)))
                   for lg in LANGS)


FIELD_LABEL = {
    "name_en": "Name (EN)", "name_th": "Name (TH)", "name_zh": "Name (ZH)",
    "color": "Colour", "odds": "Odds", "note": "Note", "artist": "Artist",
    "universe_en": "Universe", "form": "Form", "edition_scope": "Edition",
    "released": "Released", "set_size": "Set size", "secret_odds": "Secret odds",
}
SKIP_FIELDS = {"id", "node", "ip", "series", "pull", "_body", "_kind",
               "roster_complete", "contested"}


def prov_table(rec, lang=None):
    rows = []
    for k in sorted(rec.keys()):
        if k in SKIP_FIELDS or k.endswith("_src") or k.startswith("_"):
            continue
        val = rec.get(k)
        if val == "" or val is None:
            continue
        label = FIELD_LABEL.get(k, k.replace("_", " ").title())
        rows.append(
            "<tr><th>%s</th><td>%s</td><td>%s</td></tr>"
            % (html.escape(label), html.escape(str(val)),
               src_cell(str(rec.get(k + "_src", "") or "")))
        )
    if not rows:
        return ""
    return (
        '<section class="prov"><h2>%s</h2><table><thead><tr>'
        '<th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody>'
        "</table></section>"
        % (ui_span("prov"), ui_span("field"), ui_span("value"), ui_span("source"),
           "".join(rows))
    )


# ---------------------------------------------------------------------------
# Gap detection — coverage is an object, not an afterthought
# ---------------------------------------------------------------------------
def collect_gaps(ips, series, figures):
    gaps = []

    def add(scope, url, what, why):
        gaps.append(dict(scope=scope, url=url, what=what, why=why))

    for s in series:
        nm = s.get("name_en", s["id"])
        if not s.get("roster_complete"):
            have = len([f for f in figures if f.get("series") == s["id"]])
            size = s.get("set_size") or 0
            add("series", "/series/%s/" % s["id"],
                "%s — roster incomplete" % nm,
                "%d of %s figures recorded" % (have, size or "?"))
        if not s.get("released"):
            add("series", "/series/%s/" % s["id"], "%s — no release date" % nm,
                "date not researched")
        for lg in ("th", "zh"):
            if not s.get("name_%s" % lg):
                add("series", "/series/%s/" % s["id"],
                    "%s — no %s name" % (nm, lg.upper()),
                    "series name not recorded in this language")

    for i in ips:
        nm = i.get("name_en", i["id"])
        for lg in ("th", "zh"):
            if not i.get("name_%s" % lg):
                add("ip", "/ip/%s/" % i["id"], "%s — no %s name" % (nm, lg.upper()),
                    "character name not recorded in this language")
        if i.get("artist_src") == "inference":
            add("ip", "/ip/%s/" % i["id"], "%s — artist unverified" % nm,
                "attributed by inference, needs an official source")
        if i.get("name_zh_src") == "inference":
            add("ip", "/ip/%s/" % i["id"], "%s — ZH name unverified" % nm,
                "transliteration by inference, needs an official source")

    for f in figures:
        nm = f.get("name_en", f["id"])
        if f.get("contested"):
            add("figure", "/figure/%s/" % f["id"], "%s — sources disagree" % nm,
                "recorded as contested; needs an official sheet")
        if f.get("odds_src") == "community":
            add("figure", "/figure/%s/" % f["id"], "%s — odds unconfirmed" % nm,
                "community-reported odds, no official disclosure seen")
        if f.get("pull") == "regular" and not f.get("color"):
            add("figure", "/figure/%s/" % f["id"], "%s — no colour recorded" % nm,
                "regular figures are identified by colour in conversation")
        if f.get("name_pairing_src") == "inference":
            add("figure", "/figure/%s/" % f["id"],
                "%s — EN/ZH pairing is inferred" % nm,
                "the phonetic pattern is exact, but no source lists both names "
                "together")
    for i in ips:
        nm = i.get("name_en", i["id"])
        if i.get("name_zh_register") == "nickname":
            add("ip", "/ip/%s/" % i["id"], "%s — ZH name is a nickname" % nm,
                "media usage, not a Pop Mart product name")
        if i.get("artist_zh_contested"):
            add("ip", "/ip/%s/" % i["id"], "%s — artist's ZH name varies" % nm,
                "sources give different characters for the same name")
    return gaps


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
CSS = """
:root{
  --bg:#fbf7f4; --ink:#241f2b; --dim:#6b6377; --line:#e6ddd6;
  --card:rgba(255,255,255,.62); --card-solid:#fffdfc;
  --pink:#ff6fa5; --grape:#7b5cff;
  --gold:#f7b32b; --mint:#3ecfae; --shadow:0 10px 30px rgba(60,40,80,.10);
  --r:18px;
}
@media (prefers-color-scheme:dark){
  :root{--bg:#17141d; --ink:#f3eef7; --dim:#a89fb6; --line:#2e2739;
        --card:rgba(44,38,56,.55); --card-solid:#241f2e;
        --shadow:0 10px 34px rgba(0,0,0,.45);}
}
*{box-sizing:border-box}
/* The wash lives on a fixed layer rather than on body: a background painted on
   body is sized to the content box, so short pages got a hard-edged blob. */
body::before{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;
  background:
   radial-gradient(120vw 90vh at 8% -14%, rgba(255,111,165,.20), transparent 70%),
   radial-gradient(110vw 85vh at 96% 6%, rgba(123,92,255,.19), transparent 70%),
   radial-gradient(100vw 70vh at 50% 108%, rgba(62,207,174,.13), transparent 70%);}
body{margin:0;min-height:100vh;background:var(--bg);
  color:var(--ink);font:17px/1.65 ui-rounded,"Hiragino Maru Gothic ProN",
  -apple-system,"Noto Sans Thai","Noto Sans SC",system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;}
.wrap{max-width:1040px;margin:0 auto;padding:0 22px 90px}
a{color:inherit}
header.top{display:flex;align-items:center;gap:14px;flex-wrap:wrap;
  padding:22px 0 10px}
.logo{font-weight:800;font-size:1.45rem;letter-spacing:-.02em;
  text-decoration:none;display:inline-flex;align-items:center;gap:9px}
.logo .b{display:inline-block;transition:transform .35s cubic-bezier(.34,1.8,.5,1)}
.logo:hover .b{transform:translateY(-4px) rotate(-9deg) scale(1.12)}
.langs{margin-left:auto;display:flex;gap:6px}
.langs button{font:inherit;font-size:.82rem;font-weight:700;cursor:pointer;
  border:1px solid var(--line);background:var(--card);color:var(--dim);
  padding:5px 12px;border-radius:999px;backdrop-filter:blur(8px);
  transition:transform .16s,color .16s,border-color .16s}
.langs button:hover{transform:translateY(-2px)}
.langs button[aria-pressed=true]{color:var(--ink);border-color:var(--pink);
  box-shadow:0 0 0 3px rgba(255,111,165,.16)}
.crumb{font-size:.83rem;color:var(--dim);padding:6px 0 0}
.crumb a{text-decoration:none;border-bottom:1px solid var(--line)}
h1{font-size:2.3rem;line-height:1.14;letter-spacing:-.025em;margin:.35em 0 .12em}
h2{font-size:1.06rem;letter-spacing:.09em;text-transform:uppercase;
  color:var(--dim);margin:2.4em 0 .7em;font-weight:750}
.tag{color:var(--dim);font-size:1.03rem;margin:.2em 0 1.3em;max-width:60ch}
/* directory-genre listing */
.dir{margin:0;padding:0;list-style:none;
  columns:2;column-gap:34px}
@media(max-width:640px){.dir{columns:1}}
.dir li{break-inside:avoid;padding:5px 0;font-size:1.04rem}
.dir a{text-decoration:none;border-bottom:1.5px solid transparent;
  transition:border-color .18s,color .18s}
.dir a:hover{border-bottom-color:var(--pink)}
.n{color:var(--dim);font-size:.86em}
.sub{margin:2px 0 8px 16px;padding:0;list-style:none;font-size:.94rem}
.sub li{padding:2px 0}
.sub a{color:var(--dim)}
.sub a:hover{color:var(--ink)}
/* cards */
.grid{display:grid;gap:15px;grid-template-columns:repeat(auto-fill,minmax(178px,1fr));
  margin:14px 0 0;padding:0;list-style:none}
.card{position:relative;display:block;text-decoration:none;padding:17px 16px 15px;
  border:1px solid var(--line);border-radius:var(--r);background:var(--card);
  backdrop-filter:blur(11px);box-shadow:var(--shadow);overflow:hidden;
  transition:transform .2s cubic-bezier(.34,1.6,.5,1),box-shadow .2s}
.card:hover{transform:translateY(-5px) scale(1.022);
  box-shadow:0 16px 40px rgba(60,40,80,.17)}
.card:active{transform:translateY(-1px) scale(.985)}
.card .fname{font-weight:750;font-size:1.1rem;display:block}
.card .meta{color:var(--dim);font-size:.83rem;margin-top:3px;display:block}
.swatch{position:absolute;inset:0 auto 0 0;width:5px}
/* secret = chase = holo foil. Opaque fill so the type stays legible;
   the iridescence lives in the border and a faint wash. */
.card.secret{border:2px solid transparent;
  background:linear-gradient(var(--card-solid),var(--card-solid)) padding-box,
    linear-gradient(115deg,var(--gold),var(--pink),var(--grape),var(--mint),var(--gold))
    border-box}
.card.secret::before{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(135deg,rgba(247,179,43,.16),rgba(255,111,165,.14) 34%,
    rgba(123,92,255,.14) 64%,rgba(62,207,174,.16));}
.card.secret::after{content:"";position:absolute;top:0;left:-130%;width:55%;
  height:100%;pointer-events:none;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.55),
  transparent);animation:sheen 4.6s ease-in-out infinite}
.card.secret .fname,.card.secret .meta,.card.secret .pill{position:relative;z-index:1}
@keyframes sheen{0%,72%{left:-130%}100%{left:170%}}
.pill{display:inline-block;font-size:.7rem;font-weight:800;letter-spacing:.07em;
  text-transform:uppercase;padding:2px 9px;border-radius:999px;
  background:rgba(247,179,43,.18);color:#a5730a;margin-top:8px}
@media (prefers-color-scheme:dark){.pill{color:var(--gold)}}
.pill.reg{background:rgba(123,92,255,.14);color:var(--grape)}
@media (prefers-color-scheme:dark){.pill.reg{color:#b9a5ff}}
/* notices */
.note{border:1px solid var(--line);border-left:4px solid var(--gold);
  border-radius:12px;padding:13px 16px;background:var(--card);margin:18px 0;
  font-size:.95rem}
.note.contested{border-left-color:var(--pink)}
.note b{letter-spacing:.02em}
/* provenance table */
.prov table{width:100%;border-collapse:collapse;font-size:.92rem;
  background:var(--card);border:1px solid var(--line);border-radius:12px;
  overflow:hidden}
.prov th,.prov td{text-align:left;padding:9px 13px;border-bottom:1px solid var(--line);
  vertical-align:top}
.prov thead th{font-size:.74rem;text-transform:uppercase;letter-spacing:.08em;
  color:var(--dim)}
.prov tbody th{font-weight:650;width:9.5em}
.prov tr:last-child th,.prov tr:last-child td{border-bottom:0}
.src{font-size:.85rem}
.src-url{color:var(--grape);text-decoration:none;border-bottom:1px dotted}
.src-none,.src-inf{color:var(--dim);font-style:italic}
.src-inf::before{content:"⚠ ";font-style:normal}
/* facts */
.facts{list-style:none;padding:0;margin:16px 0;display:grid;gap:9px;
  grid-template-columns:repeat(auto-fit,minmax(158px,1fr))}
.facts li{border:1px solid var(--line);border-radius:13px;padding:10px 13px;
  background:var(--card)}
.facts .k{display:block;font-size:.71rem;text-transform:uppercase;
  letter-spacing:.08em;color:var(--dim)}
.facts .v{font-weight:700}
/* ISO / gaps */
.iso{list-style:none;padding:0;margin:0}
.iso li{border-bottom:1px dashed var(--line);padding:11px 2px;display:flex;
  gap:12px;flex-wrap:wrap;align-items:baseline}
.iso a{font-weight:650;text-decoration:none;border-bottom:1px solid var(--line)}
.iso .why{color:var(--dim);font-size:.9rem}
.iso .sc{font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;
  color:var(--dim);border:1px solid var(--line);border-radius:999px;
  padding:1px 8px}
footer{margin-top:66px;padding-top:20px;border-top:1px solid var(--line);
  color:var(--dim);font-size:.85rem}
footer p{max-width:66ch}
.nm{display:none}
.nm-fb{opacity:.72;border-bottom:1px dotted var(--dim)}
html[lang=en] .nm[data-lang=en],
html[lang=th] .nm[data-lang=th],
html[lang=zh] .nm[data-lang=zh]{display:inline}
[data-i18n]{display:none}
html[lang=en] [data-i18n=en],
html[lang=th] [data-i18n=th],
html[lang=zh] [data-i18n=zh]{display:inline}
.ant{position:fixed;bottom:14px;left:-40px;font-size:20px;pointer-events:none;
  opacity:0}
"""

JS = """
(function(){
  var K='poplucky.lang';
  function set(l){
    document.documentElement.lang=l;
    try{localStorage.setItem(K,l)}catch(e){}
    var bs=document.querySelectorAll('.langs button');
    for(var i=0;i<bs.length;i++)
      bs[i].setAttribute('aria-pressed', bs[i].dataset.l===l?'true':'false');
  }
  var saved=null; try{saved=localStorage.getItem(K)}catch(e){}
  if(!saved){
    var n=(navigator.language||'en').toLowerCase();
    saved = n.indexOf('th')===0?'th' : (n.indexOf('zh')===0?'zh':'en');
  }
  document.addEventListener('click',function(e){
    var b=e.target.closest('.langs button'); if(b) set(b.dataset.l);
  });
  set(saved);

  /* copy link */
  document.addEventListener('click',function(e){
    var b=e.target.closest('[data-copylink]'); if(!b) return;
    var row=b.closest('.share'); if(!row) return;
    var url=row.dataset.shareUrl||location.href;
    function done(){
      var s=row.querySelector('.said');
      if(s){ s.classList.remove('hidden');
             setTimeout(function(){s.classList.add('hidden');},1800); }
    }
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(url).then(done,done);
    } else {
      var ta=document.createElement('textarea'); ta.value=url;
      ta.style.position='fixed'; ta.style.opacity='0';
      document.body.appendChild(ta); ta.select();
      try{document.execCommand('copy');}catch(err){}
      ta.remove(); done();
    }
  });

  /* hidden bell: shake a blind box and something rattles */
  var box=document.querySelector('.logo .b');
  if(box){
    var taps=0,timer=null;
    box.parentNode.addEventListener('click',function(ev){
      ev.preventDefault();
      taps++;
      box.animate([{transform:'rotate(0)'},{transform:'rotate(-16deg)'},
        {transform:'rotate(14deg)'},{transform:'rotate(0)'}],
        {duration:340,easing:'ease-in-out'});
      clearTimeout(timer);
      if(taps>=3){
        taps=0;
        box.textContent='\\u2728';
        setTimeout(function(){box.textContent='\\ud83c\\udf81'},1500);
      } else {
        timer=setTimeout(function(){taps=0;window.location=box.parentNode.href},420);
      }
    });
  }
})();
"""


REPO = "https://github.com/NaNoBotCo/poplucky"


def issue_link(title, body, labels="contribution"):
    """A pre-filled GitHub issue. No backend, no account for us to run --
    the same trick mot-dang uses for 'tell the ants'."""
    from urllib.parse import quote
    return ("%s/issues/new?title=%s&body=%s&labels=%s"
            % (REPO, quote(title), quote(body), quote(labels)))


def share_row(path, title):
    """LINE first: it is where Thai collectors actually talk."""
    from urllib.parse import quote
    url = quote(SITE + path, safe="")
    txt = quote(title, safe="")
    return (
        '<div class="share" data-share-url="%s%s">'
        '<span class="lbl">%s</span>'
        '<a class="line" href="https://social-plugins.line.me/lineit/share?url=%s" '
        'target="_blank" rel="noopener">LINE</a>'
        '<a href="https://www.facebook.com/sharer/sharer.php?u=%s" target="_blank" '
        'rel="noopener">Facebook</a>'
        '<a href="https://twitter.com/intent/tweet?url=%s&amp;text=%s" '
        'target="_blank" rel="noopener">X</a>'
        '<button data-copylink>%s</button>'
        '<span class="said hidden">%s</span>'
        "</div>"
        % (SITE, path, ui_span("share"), url, url, url, txt,
           ui_span("copylink"), ui_span("linkcopied"))
    )


def helpout(kind, what, prefill):
    return (
        '<div class="helpout"><p><strong>%s</strong> %s</p>'
        '<a href="%s" target="_blank" rel="noopener">%s</a></div>'
        % (ui_span("help_title"),
           ui_span("help_contested" if kind == "contested" else "help_gap"),
           issue_link("[%s] %s" % (kind, what), prefill), ui_span("help_cta"))
    )


def page(title, lang_neutral_title, body, desc, path, crumbs=None, extra_head="",
         card=None):
    """path is the site path like '/series/foo/'."""
    canon = SITE + path
    if card:
        extra_head += (
            '\n<meta property="og:image" content="%s/cards/%s">'
            '\n<meta property="og:image:width" content="1200">'
            '\n<meta property="og:image:height" content="630">'
            '\n<meta name="twitter:image" content="%s/cards/%s">'
            % (SITE, card, SITE, card)
        )
    crumb_html = ""
    if crumbs:
        bits = []
        for label_key, url in crumbs:
            lbl = "".join(
                '<span data-i18n="%s">%s</span>' % (lg, html.escape(t(label_key, lg)))
                for lg in LANGS)
            bits.append('<a href="%s">%s</a>' % (url, lbl))
        crumb_html = '<nav class="crumb">%s</nav>' % " › ".join(bits)

    langbar = "".join(
        '<button data-l="%s" aria-pressed="false">%s</button>' % (lg, LANG_LABEL[lg])
        for lg in LANGS)

    foot = "".join(
        '<p data-i18n="%s">%s</p>' % (lg, html.escape(t("notaffil", lg)))
        for lg in LANGS)

    doc = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Poplucky">
<meta name="twitter:card" content="summary_large_image">
{extra_head}
<style>{css}{shelfcss}{artcss}</style>
</head>
<body>
<div class="wrap">
<header class="top">
  <a class="logo" href="/"><span class="b">\U0001f381</span> Poplucky</a>
  <a class="shelfnav" href="/shelf/">{shelfword}<span class="badge"></span></a>
  <div class="langs">{langbar}</div>
</header>
{crumb}
<main>
{body}
{sharerow}
</main>
<footer>{foot}</footer>
</div>
<script>{js}</script>
<script>{shelfjs}</script>
</body>
</html>
""".format(title=html.escape(title), desc=html.escape(desc), canon=canon,
           ogtitle=html.escape(lang_neutral_title), css=CSS, js=JS,
           langbar=langbar, crumb=crumb_html, body=body, foot=foot,
           extra_head=extra_head, shelfcss=_shelf.SHELF_CSS,
           shelfjs=_shelf.SHELF_JS, shelfword=ui_span("shelf"),
           artcss=_art.ART_CSS,
           sharerow=share_row(path, lang_neutral_title))

    d = os.path.join(OUT, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)


COLOR_HEX = {
    "yellow": "#f7c948", "gray": "#9aa0ab", "grey": "#9aa0ab", "brown": "#a4714b",
    "blue": "#4f8ef7", "green": "#3ecfae", "pink": "#ff6fa5", "red": "#f2545b",
    "orange": "#ff9f43", "purple": "#7b5cff", "pink and yellow": "#ff6fa5",
}


def fig_card(f):
    cls = "card secret" if f.get("pull") == "secret" else "card"
    col = COLOR_HEX.get(str(f.get("color", "")).lower())
    sw = '<span class="swatch" style="background:%s"></span>' % col if col else ""
    pill_key = "secret" if f.get("pull") == "secret" else "regular"
    pill_cls = "pill" if f.get("pull") == "secret" else "pill reg"
    odds = f.get("odds")
    meta = html.escape(str(f.get("color", "") or ""))
    if odds:
        meta = (meta + " · " if meta else "") + html.escape(str(odds))
    ctl = (
        '<div class="ctl">'
        '<button data-act="dec" aria-label="one fewer">\u2212</button>'
        '<span class="cnt zero">0</span>'
        '<button data-act="inc" aria-label="one more">+</button>'
        '<button class="wish" data-act="wish" aria-pressed="false" '
        'aria-label="seeking">\u2661</button>'
        "</div>"
    )
    art = '<span class="boxwrap">%s</span>' % _art.box_svg(f, f.get("ip", ""))
    return (
        '<li class="%s shelf-item" data-id="%s">%s'
        '<a class="card-link" href="/figure/%s/">%s'
        '<span class="fname">%s</span>'
        '<span class="meta">%s</span></a>'
        '<span class="%s">%s</span>%s</li>'
        % (cls, f["id"], sw, f["id"], art, name_span(f), meta or "&nbsp;",
           pill_cls, ui_span(pill_key), ctl)
    )


def build():
    # Clear the CONTENTS of docs/, never docs/ itself — removing the directory
    # invalidates the cwd of any dev server serving it.
    os.makedirs(OUT, exist_ok=True)
    for entry in os.listdir(OUT):
        p = os.path.join(OUT, entry)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

    ips = load("ip")
    series = load("series")
    figures = load("figure")
    by_ip = {i["id"]: i for i in ips}
    by_series = {s["id"]: s for s in series}

    gaps = collect_gaps(ips, series, figures)

    # ---- home ------------------------------------------------------------
    items = []
    for i in ips:
        ss = [s for s in series if s.get("ip") == i["id"]]
        nfig = len([f for f in figures if f.get("ip") == i["id"]])
        sub = "".join(
            '<li><a href="/series/%s/">%s <span class="n">(%d)</span></a></li>'
            % (s["id"], name_span(s),
               len([f for f in figures if f.get("series") == s["id"]]))
            for s in ss)
        items.append(
            '<li><a href="/ip/%s/">%s</a> <span class="n">(%d)</span>'
            '<ul class="sub">%s</ul></li>'
            % (i["id"], name_span(i), nfig, sub))

    home = (
        "<h1>Poplucky</h1>"
        '<p class="tag">%s</p>'
        "<h2>%s</h2><ul class=\"dir\">%s</ul>"
        '<h2>%s</h2><p class="tag">%s <a href="/iso/">%s →</a></p>'
        % (ui_span("tagline"), ui_span("characters"), "".join(items),
           ui_span("iso_nav"), ui_span("iso_blurb"), ui_span("iso_nav"))
    )
    page("Poplucky — the Pop Mart collector's catalogue", "Poplucky", home,
         t("tagline", "en"), "/", card="home.png")

    # ---- IP pages --------------------------------------------------------
    for i in ips:
        ss = [s for s in series if s.get("ip") == i["id"]]
        facts = []
        if i.get("universe_en"):
            facts.append('<li><span class="k">%s</span><span class="v">%s</span></li>'
                         % (ui_span("universe"), html.escape(i["universe_en"])))
        if i.get("artist"):
            facts.append('<li><span class="k">%s</span><span class="v">%s</span></li>'
                         % (ui_span("artist"), html.escape(i["artist"])))
        lst = "".join(
            '<li><a href="/series/%s/">%s <span class="n">(%d)</span></a></li>'
            % (s["id"], name_span(s),
               len([f for f in figures if f.get("series") == s["id"]]))
            for s in ss)
        body = (
            "<h1>%s</h1>" % name_span(i)
            + ('<ul class="facts">%s</ul>' % "".join(facts) if facts else "")
            + md(i.get("_body", ""))
            + "<h2>%s</h2><ul class=\"dir\">%s</ul>" % (ui_span("series"), lst)
            + prov_table(i, "en")
        )
        page("%s — Poplucky" % i.get("name_en", i["id"]), i.get("name_en", i["id"]),
             body, "Series and figures for %s." % i.get("name_en", i["id"]),
             "/ip/%s/" % i["id"], crumbs=[("home", "/")],
             card="ip-%s.png" % i["id"])

    # ---- series pages ----------------------------------------------------
    for s in series:
        fs = [f for f in figures if f.get("series") == s["id"]]
        fs.sort(key=lambda f: (f.get("pull") == "secret", f.get("name_en", "")))
        facts = []
        for key, lbl in (("form", "form"), ("edition_scope", "scope"),
                         ("released", "released"), ("set_size", "setsize"),
                         ("secret_odds", "odds")):
            if s.get(key) not in (None, "", 0):
                facts.append(
                    '<li><span class="k">%s</span><span class="v">%s</span></li>'
                    % (ui_span(lbl), html.escape(str(s[key]))))
        notice = ""
        if not s.get("roster_complete"):
            notice = '<div class="note">%s</div>' % ui_span("roster_partial")
        swall = ""
        so = str(s.get("secret_odds", "") or "")
        if so and "\u00b7" not in so:
            swall = _art.odds_wall(so, s["id"])
            if swall:
                swall += ('<p class="oddscap">%s</p>'
                          % ui_span_fmt("odds_cap", html.escape(so)))
        body = (
            "<h1>%s</h1>" % name_span(s)
            + ('<ul class="facts">%s</ul>' % "".join(facts) if facts else "")
            + md(s.get("_body", ""))
            + swall
            + notice
            + '<h2>%s</h2><ul class="grid">%s</ul>'
              % (ui_span("figures"), "".join(fig_card(f) for f in fs))
            + prov_table(s, "en")
        )
        ip = by_ip.get(s.get("ip"), {})
        page("%s — %s — Poplucky" % (s.get("name_en"), ip.get("name_en", "")),
             s.get("name_en", s["id"]), body,
             "Every figure in %s, with odds and sources." % s.get("name_en", ""),
             "/series/%s/" % s["id"], crumbs=[("home", "/")],
             card="series-%s.png" % s["id"])

    # ---- figure pages ----------------------------------------------------
    for f in figures:
        s = by_series.get(f.get("series"), {})
        i = by_ip.get(f.get("ip"), {})
        facts = []
        if f.get("odds"):
            facts.append('<li><span class="k">%s</span><span class="v">%s</span></li>'
                         % (ui_span("odds"), html.escape(str(f["odds"]))))
        if f.get("color"):
            facts.append('<li><span class="k">%s</span><span class="v">%s</span></li>'
                         % (ui_span("colour"), html.escape(str(f["color"]))))
        notice = ""
        if f.get("contested"):
            notice = ('<div class="note contested"><b>%s.</b> %s</div>'
                      % (ui_span("contested"), html.escape(str(f.get("note", "")))))
        elif f.get("note"):
            notice = '<div class="note">%s</div>' % html.escape(str(f["note"]))
        solo = (
            '<div class="shelfsolo shelf-item" data-id="%s">'
            '<span class="lbl">%s</span>'
            '<div class="ctl">'
            '<button data-act="dec" aria-label="one fewer">\u2212</button>'
            '<span class="cnt zero">0</span>'
            '<button data-act="inc" aria-label="one more">+</button>'
            '<button class="wish" data-act="wish" aria-pressed="false" '
            'aria-label="seeking">\u2661</button>'
            "</div>"
            '<span class="mine">%s \u2713</span>'
            "</div>"
            % (f["id"], ui_span("have"), ui_span("on_shelf"))
        )
        where = (
            '<ul class="dir"><li><a href="/series/%s/">%s</a></li>'
            '<li><a href="/ip/%s/">%s</a></li></ul>'
            % (s.get("id", ""), name_span(s) if s else "",
               i.get("id", ""), name_span(i) if i else "")
        )
        wall = _art.odds_wall(f.get("odds", ""), f["id"])
        if wall:
            wall += ('<p class="oddscap">%s</p>'
                     % ui_span_fmt("odds_cap", html.escape(str(f["odds"]))))
        help_block = ""
        if f.get("contested"):
            help_block = helpout(
                "contested", "%s — %s" % (f.get("name_en", f["id"]),
                                          s.get("name_en", "")),
                "Page: %s/figure/%s/\n\nWhat the catalogue says now:\n%s\n\n"
                "What do you know? Anything helps -- what you own, what the box "
                "says, a link to an official listing."
                % (SITE, f["id"], str(f.get("note", "") or "sources disagree")))
        body = (
            '<div class="herobox"><span class="shelf-item boxwrap" data-id="%s">%s'
            "</span><span class=\"heroname\">" % (f["id"], _art.box_svg(f, f.get("ip", "")))
            + "<h1>%s</h1>" % name_span(f)
            + '<p class="tag">%s</p></span></div>' % ui_span(
                "secret" if f.get("pull") == "secret" else "regular")
            + ('<ul class="facts">%s</ul>' % "".join(facts) if facts else "")
            + wall
            + notice
            + solo
            + help_block
            + "<h2>%s</h2>%s" % (ui_span("where"), where)
            + prov_table(f, "en")
        )
        page("%s — %s — Poplucky" % (f.get("name_en"), s.get("name_en", "")),
             f.get("name_en", f["id"]), body,
             "%s, %s in %s." % (f.get("name_en", ""),
                                t(f.get("pull", "regular"), "en"),
                                s.get("name_en", "")),
             "/figure/%s/" % f["id"], crumbs=[("home", "/")],
             card="figure-%s.png" % f["id"])

    # ---- My Shelf --------------------------------------------------------
    page("My Shelf — Poplucky", "My Shelf", _shelf.shelf_body(ui_span),
         "Track what you have, what you are seeking, and make a trade card.",
         "/shelf/", crumbs=[("home", "/")], card="shelf.png")

    # ---- In Search Of ----------------------------------------------------
    rows = "".join(
        '<li><span class="sc">%s</span><a href="%s">%s</a>'
        '<span class="why">%s</span>'
        '<a class="fix" href="%s" target="_blank" rel="noopener">%s</a></li>'
        % (html.escape(g["scope"]), g["url"], html.escape(g["what"]),
           html.escape(g["why"]),
           issue_link("[gap] " + g["what"],
                      "Page: %s%s\n\nWhat is missing:\n%s\n\n"
                      "Anything you know helps -- a name, a photo of the box, "
                      "a link to an official listing."
                      % (SITE, g["url"], g["why"])),
           ui_span("fix"))
        for g in gaps)
    head = ('<h1>%s</h1><p class="tag">%s</p>'
            '<p class="tag"><strong>%d</strong> open questions.</p>'
            % (ui_span("iso"), ui_span("iso_blurb"), len(gaps)))
    invite = helpout(
        "gap", "the catalogue's open questions",
        "Page: %s/iso/\n\nWhich open question can you close, and what do you "
        "know about it?" % SITE)
    body = head + invite + ('<ul class="iso">%s</ul>' % rows)
    page("In Search Of — Poplucky", "In Search Of", body,
         "What the Poplucky catalogue does not know yet.", "/iso/",
         crumbs=[("home", "/")], card="iso.png")

    # ---- machine-readable + hygiene --------------------------------------
    with open(os.path.join(OUT, "catalog.json"), "w", encoding="utf-8") as f:
        json.dump(dict(ip=ips, series=series, figure=figures, gaps=gaps),
                  f, ensure_ascii=False, indent=1, default=str)
    urls = ["/", "/iso/", "/shelf/"] + ["/ip/%s/" % i["id"] for i in ips] + \
           ["/series/%s/" % s["id"] for s in series] + \
           ["/figure/%s/" % f["id"] for f in figures]
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u in urls:
            f.write("<url><loc>%s%s</loc></url>\n" % (SITE, u))
        f.write("</urlset>\n")
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE)
    # No trailing newline: GitHub writes CNAME this way when the custom domain
    # is set through its UI/API, and matching it stops the file flapping.
    with open(os.path.join(OUT, "CNAME"), "w", encoding="utf-8") as f:
        f.write("poplucky.net")
    with open(os.path.join(OUT, ".nojekyll"), "w") as f:
        f.write("")

    try:
        import make_cards
        ncards = make_cards.build_cards(ips, series, figures)
        print("wrote %d share cards -> docs/cards/" % ncards)
    except Exception as e:
        print("cards skipped: %s" % e)

    print("built %d pages -> docs/" % len(urls))
    print("  %d characters · %d series · %d figures · %d open questions"
          % (len(ips), len(series), len(figures), len(gaps)))
    return 0


if __name__ == "__main__":
    sys.exit(build())
