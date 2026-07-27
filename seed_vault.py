#!/usr/bin/env python3
"""
seed_vault.py — one-time initial import for the Poplucky vault.

Same role as mot-dang's importers: this folds researched records into the
vault ONCE. After seeding, vault/ is canonical and is edited in Obsidian.
Re-running refuses unless --force is passed.

Provenance rule: every fact field may carry a sibling `<field>_src`.
  - a URL            -> sourced from that page
  - "official"       -> from popmart.com itself
  - "community"      -> collector catalog / community consensus
  - "inference"      -> model inference, NOT verified. Counts as a gap.
  - absent           -> unknown / not yet researched. Counts as a gap.

STANDING CAVEAT, recorded here because it colours every record below:
popmart.com is JavaScript-rendered and defeated every attempt to read a
product page's BODY. So no roster and no odds figure in this seed is
confirmed against Pop Mart's own pages — those rest on third-party
catalogs, chiefly thetoypool.com and toysez.com, which independently agree.
Closing that gap needs a real browser session against popmart.com.

Chinese SERIES names are the exception and are genuinely official: Pop
Mart's HK/MO/TH storefronts encode the Chinese title in the product URL
itself, and the same numeric product ID serves both the Chinese and English
titles. That ID match is what proves 眼泪工厂系列 == "Crying Again".
"""
import argparse
import os
import sys

VAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vault")

# --- sources -----------------------------------------------------------------
S_SEAT = "https://blindboxradar.com/dada-labubu-have-a-seat/"
S_SEAT2 = "https://www.feltify.com/blogs/all-about-labubu/what-is-the-secret-labubu-have-a-seat"
S_CITY_SEAT = "https://labubu.city/blog/have-a-seat-labubu"
S_BIE = "https://labubukeychain.co.uk/blogs/news/labubu-big-into-energy-guide"
S_TZ_BIE = "https://toysez.com/collections/labubu-the-monsters-big-into-energy-series-vinyl-plush-pendant"
S_TZ_BIE_ID = "https://toysez.com/products/labubu-the-monsters-big-into-energy-series-vinyl-plush-pendant-secret-id1-72"
S_POOL_SOUND = "https://thetoypool.com/pop-mart/series/skullpanda/the-sound-series/"
S_TZ_SOUND = "https://toysez.com/collections/skullpanda-the-sound-series"
S_POOL_CRY = "https://thetoypool.com/pop-mart/series/crybaby/crying-again-series/"
S_TZ_CRY = "https://toysez.com/collections/crybaby-crying-again-series"
S_POOL_PLUSH = "https://thetoypool.com/pop-mart/series/crybaby/crying-again-vinyl-face-plush-series/"
S_POOL_CARB = "https://thetoypool.com/pop-mart/series/molly/carb+lover-series/"
S_TZ_CARB = "https://toysez.com/collections/molly-carb-lover-baking-time-series"
S_GLTY = "https://www.kickscrew.com/products/pop-mart-the-monsters-labubu-good-luck-to-you-pendant-ppmt-2412-0042"
S_ZH_LABUBU = "https://zh.wikipedia.org/wiki/%E6%8B%89%E5%B8%83%E5%B8%83"
S_ZH_MOLLY = "https://zh.wikipedia.org/zh-tw/%E8%8C%89%E8%8E%89_(%E8%97%9D%E8%A1%93%E4%BA%BA%E5%81%B6)"
S_ZH_CRY = "https://stcn.com/article/detail/2163016.html"
# Pop Mart's OWN Chinese-language storefronts. These are official.
S_PM_SEAT_ZH = "https://www.popmart.com/hk/products/1001/the-monsters-%E5%9D%90%E5%9D%90%E6%B4%BE%E5%B0%8D%E6%90%AA%E8%86%A0%E6%AF%9B%E7%B5%A8%E7%9B%B2%E7%9B%92"
S_PM_BIE_ZH = "https://www.popmart.com/mo/products/1990/the-monsters-%E5%89%8D%E6%96%B9%E9%AB%98%E8%83%BD%E7%B3%BB%E5%88%97-%E6%90%AA%E8%86%A0%E6%AF%9B%E7%B5%A8%E6%8E%9B%E4%BB%B6%E7%9B%B2%E7%9B%92"
S_PM_SOUND_ZH = "https://www.popmart.com/hk/products/991/skullpanda%E8%81%B2%E9%9F%B3%E7%B3%BB%E5%88%97"
S_PM_CRY_ZH = "https://www.popmart.com/hk/products/1131/crybaby-%E7%9C%BC%E6%B7%9A%E5%B7%A5%E5%BB%A0%E7%B3%BB%E5%88%97%E6%89%8B%E8%BE%A6"
S_PM_CRYP_ZH = "https://www.popmart.com/hk/products/1234/crybaby%E7%9C%BC%E6%B7%9A%E5%B7%A5%E5%BB%A0%E7%B3%BB%E5%88%97-%E6%90%AA%E8%86%A0%E8%87%89%E6%AF%9B%E7%B5%A8%E7%9B%B2%E7%9B%92"
S_PM_GLTY = "https://www.popmart.com/th/products/1844/labubu-good-luck-to-you-vinyl-plush-doll-pendant"
S_PM_GLTY_BAG = "https://www.popmart.com/th/products/1846/labubu-good-luck-to-you-canvas-bag"
S_MOFCOM = "https://ipr.mofcom.gov.cn/article/gjxw/zfxd/mz/202511/1993778.html"
S_HUPU = "https://m.hupu.com/score-list/common_first/2097984"
S_WUYAW = "https://miniapp.wuyaw.com/goods/_dmesoh0evoLgLiT4RabpMpNWDHMJOvysNcrcOLw"

TWO_CATALOGS = "collector catalogs (thetoypool + toysez, in agreement)"

# --- IP nodes ----------------------------------------------------------------
IPS = [
    dict(
        id="labubu", name_en="Labubu", name_en_src="official",
        name_zh="拉布布", name_zh_src=S_ZH_LABUBU,
        name_th="ลาบูบู้", name_th_src="community",
        universe_en="The Monsters", universe_src=S_SEAT,
        universe_zh="精灵天团", universe_zh_src=S_ZH_LABUBU,
        artist="Kasing Lung", artist_src=S_SEAT,
        artist_zh="龙家升", artist_zh_src=S_MOFCOM, artist_zh_contested=True,
        body=(
            "Elf-like creature with a serrated grin, from Kasing Lung's THE MONSTERS "
            "universe (精灵天团). The teeth are the collector's tell: authentic figures "
            "are consistently described as having exactly nine, evenly gapped.\n\n"
            "*Vernacular* — counterfeits are called **Lafufu** across every language "
            "community, English included. The word is affectionate as often as it is "
            "scornful; plenty of collectors keep a Lafufu on the shelf on purpose.\n\n"
            "*Naming* — 拉布布 is the standard Chinese rendering in media, encyclopedic "
            "and even Chinese government usage, but **Pop Mart itself brands the "
            "character in Latin letters** even on its Chinese storefronts. The artist's "
            "given name appears as both 龙家升 and 龙家昇 depending on source; the "
            "simplified 升 is used here on the strength of the ministry citation."
        ),
    ),
    dict(
        id="skullpanda", name_en="SKULLPANDA", name_en_src="official",
        name_zh="", name_th="",
        artist="Xiong Miao", artist_src="community",
        artist_zh="熊喵", artist_zh_src="community",
        body=(
            "Pop Mart house IP. Series lean conceptual, each release built around one "
            "theme rather than a cast of named friends.\n\n"
            "*Naming note* — no official Chinese rendering of the character name was "
            "found; Pop Mart appears to use the Latin \"SKULLPANDA\" even in "
            "Chinese-market materials. 熊喵 is the **artist**, not the character. "
            "Left blank rather than guessed."
        ),
    ),
    dict(
        id="crybaby", name_en="CRYBABY", name_en_src="official",
        name_zh="哭娃", name_zh_src=S_ZH_CRY, name_zh_register="nickname",
        artist="Molly Yllom", artist_src="community",
        body=(
            "Created by a **Thai** artist working as Molly Yllom — not to be confused "
            "with Pop Mart's separate MOLLY character. Crying is the whole premise: the "
            "figures weep and are cheerful about it.\n\n"
            "*Regional note* — CRYBABY's Thai origin makes it the natural doorway for "
            "Thai-language readers, and Thai-market releases around this IP deserve "
            "close tracking.\n\n"
            "*Naming* — 哭娃 is what Chinese media and Taiwanese retailers call this "
            "character, introduced with \"also known as\" rather than as a product "
            "name. Pop Mart keeps CRYBABY in Latin on its own Chinese pages. Recorded "
            "as a nickname, which is what it is."
        ),
    ),
    dict(
        id="molly", name_en="MOLLY", name_en_src="official",
        name_zh="茉莉", name_zh_src=S_ZH_MOLLY, name_th="",
        artist="Kenny Wong", artist_src=S_ZH_MOLLY,
        artist_zh="王信明", artist_zh_src=S_ZH_MOLLY,
        body=("Pop Mart's longest-running flagship character.\n\n"
              "*Naming* — 茉莉 is encyclopedic and media usage; Pop Mart brands the IP "
              "as MOLLY in Latin on its own storefronts."),
    ),
]

# --- series nodes ------------------------------------------------------------
SERIES = [
    dict(
        id="labubu-have-a-seat", ip="labubu",
        name_en="Have a Seat", name_en_src="official",
        name_zh="坐坐派对", name_zh_src=S_PM_SEAT_ZH, name_th="",
        form="vinyl-plush", form_src=S_SEAT,
        edition_scope="global", edition_scope_src=S_SEAT,
        released="2024-07-12", released_src=S_CITY_SEAT,
        set_size=6, set_size_src=S_SEAT,
        secret_odds="1/72", secret_odds_src=S_SEAT2,
        roster_complete=True,
        body=(
            "Six seated figures plus one secret. The line that took Labubu from "
            "art-toy shelves to airport queues.\n\n"
            "Each regular is identified primarily by colour, which is how collectors "
            "actually call them in conversation — \"the green one\" long before "
            "\"Ququ\".\n\n"
            "*Naming* — the Chinese names came first and the English ones are simply "
            "their doubled final syllable: 眼巴巴 becomes Baba, 羞答答 becomes Dada. "
            "Read in Chinese they are little emotional states — 委屈屈 is sulky, "
            "甜丝丝 is sweet — and the English names keep the sound while dropping "
            "every bit of that meaning. Recording only the English would throw away "
            "what the set is actually about."
        ),
    ),
    dict(
        id="labubu-big-into-energy", ip="labubu",
        name_en="Big into Energy", name_en_src="official",
        name_zh="前方高能系列", name_zh_src=S_PM_BIE_ZH, name_th="",
        form="vinyl-plush-pendant", form_src=S_TZ_BIE,
        edition_scope="global", edition_scope_src=S_TZ_BIE,
        released="2025-04-24", released_src=S_TZ_BIE,
        set_size=6, set_size_src=S_TZ_BIE,
        secret_odds="1/72", secret_odds_src=S_TZ_BIE_ID,
        roster_complete=True,
        body=(
            "Third mainline Labubu blind-box pendant series, often called **V3**. "
            "17cm, tie-dye colourways, one positive quality per figure.\n\n"
            "**Colour is deliberately not recorded here.** Sources actively disagree "
            "on which emotion wears which colour — one catalog calls Luck yellow, "
            "another purple. Because the figures are tie-dyed and no two pulls are "
            "identical, colour is a poor identifier for this set. Recording nothing "
            "beats recording a coin-flip.\n\n"
            "*Source hygiene* — at least one widely-circulated guide to this series "
            "lists a figure called \"Courage\", which does not exist in it, and gives "
            "the wrong odds. Treat single-source rosters for this set with suspicion."
        ),
    ),
    dict(
        id="labubu-good-luck-to-you", ip="labubu",
        name_en="Good Luck To You", name_en_src=S_PM_GLTY,
        name_zh="", name_th="",
        form="vinyl-plush-pendant", form_src=S_PM_GLTY,
        edition_scope="Thailand exclusive", edition_scope_src=S_PM_GLTY,
        released="2024-12-20", released_src=S_GLTY,
        set_size=1, set_size_src=S_PM_GLTY,
        price_thb="1050", price_thb_src=S_GLTY,
        roster_complete=True,
        body=(
            "A **Thailand-exclusive** release, roughly 17cm, sold at 1,050 baht. Not a "
            "blind box — you know what you are buying.\n\n"
            "This is the edition-scope axis doing its work: the same character, bound "
            "to one market. A collector in Bangkok and a collector in Berlin are not "
            "shopping the same catalogue, and a catalogue that flattens them into one "
            "global list is lying to both.\n\n"
            "Labubu wears Thai traditional dress with gold ornaments, and it is a "
            "**line rather than a single item** — the pendant has a matching canvas "
            "bag on the same store.\n\n"
            "*No Chinese name exists.* Pop Mart hosts this only on its Thai store. A "
            "plausible-looking 祝你好运 circulates in search summaries but appears on "
            "no actual page, so it is deliberately absent here.\n\n"
            "*Open question* — a separately-titled \"Good Luck To You King Labubu\" "
            "appears at some retailers. Whether that is a distinct SKU or a reseller "
            "renaming this one is unresolved."
        ),
    ),
    dict(
        id="skullpanda-the-sound", ip="skullpanda",
        name_en="The Sound", name_en_src="official",
        name_zh="声音系列", name_zh_src=S_PM_SOUND_ZH, name_th="",
        form="figure", form_src=S_POOL_SOUND,
        edition_scope="global", edition_scope_src=S_POOL_SOUND,
        released="2024-06-28", released_src=S_POOL_SOUND,
        set_size=12, set_size_src=S_POOL_SOUND,
        secret_odds="1/144", secret_odds_src=S_TZ_SOUND,
        roster_complete=True,
        body=(
            "Twelve figures, each an emotional register. A full case of twelve contains "
            "no repeats, which makes this set unusually tractable to complete by the "
            "case rather than by the box.\n\n"
            "*Structure* — the roster maps cleanly onto Plutchik's wheel of emotions, "
            "eight primaries and their intensities. That is a useful integrity check: a "
            "roster claiming an emotion outside the wheel is probably wrong."
        ),
    ),
    dict(
        id="crybaby-crying-again", ip="crybaby",
        name_en="Crying Again", name_en_src="official",
        name_zh="眼泪工厂系列", name_zh_src=S_PM_CRY_ZH, name_th="",
        form="figure", form_src=S_POOL_CRY,
        edition_scope="global", edition_scope_src=S_POOL_CRY,
        released="2024-09-27", released_src=S_POOL_CRY,
        set_size=12, set_size_src=S_POOL_CRY,
        secret_odds="1/144 · 1/144 · 1/288", secret_odds_src=S_TZ_CRY,
        roster_complete=True,
        body=(
            "Twelve regulars and — unusually — **three** secrets, tiered: two at 1/144 "
            "and one \"super secret\" at 1/288.\n\n"
            "**Do not confuse this with the plush.** There is a separate *Crying Again "
            "Vinyl Face Plush* line sharing the name, with a different and smaller "
            "roster. Two figures, Baby Blonde and Baby Brown, are ordinary regulars "
            "here and **secrets** over there. A collector who checks the wrong list "
            "will think they pulled a chase, or fail to realise they did.\n\n"
            "*Naming* — the Chinese name is a **renaming, not a translation**: "
            "眼泪工厂系列, \"Tear Factory\". Anyone translating \"Crying Again\" "
            "into Chinese lands on a name that no Chinese collector uses. The mapping "
            "is provable because Pop Mart serves both titles under the same product ID."
        ),
    ),
    dict(
        id="crybaby-crying-again-plush", ip="crybaby",
        name_en="Crying Again Vinyl Face Plush", name_en_src=S_POOL_PLUSH,
        name_zh="眼泪工厂系列", name_zh_src=S_PM_CRYP_ZH, name_th="",
        form="vinyl-face-plush", form_src=S_POOL_PLUSH,
        edition_scope="global", edition_scope_src=S_POOL_PLUSH,
        released="", released_src="",
        set_size=6, set_size_src=S_POOL_PLUSH,
        roster_complete=True,
        body=(
            "The plush cousin of *Crying Again*, and the sharpest argument in this "
            "catalogue for keeping **form** as its own axis.\n\n"
            "Same IP, same series name, six regulars instead of twelve — and the two "
            "secrets here, Baby Blonde and Baby Brown, are plain regulars in the figures "
            "line. Rarity is a property of a figure *within a form*, never of a name."
        ),
    ),
    dict(
        id="molly-carb-lover", ip="molly",
        name_en="Carb-Lover", name_en_src=S_POOL_CARB,
        name_zh="", name_th="",
        form="figure", form_src=S_POOL_CARB,
        edition_scope="global", edition_scope_src=S_POOL_CARB,
        released="2024-10-16", released_src=S_POOL_CARB,
        set_size=12, set_size_src=S_POOL_CARB,
        secret_odds="1/144", secret_odds_src=S_TZ_CARB,
        roster_complete=True,
        body=(
            "Twelve bakery figures plus one secret. MOLLY dressed as bread, essentially, "
            "and the better for it.\n\n"
            "*Naming note* — at least one retailer renders three of these differently "
            "(\"Baker or Guard\", \"Balaclava Crescent\"). Two independent catalogs back "
            "the spellings used here; the outlier is recorded as an outlier."
        ),
    ),
]


# --- figure nodes ------------------------------------------------------------
def fig(id, series, ip, name_en, name_en_src, pull="regular", **kw):
    d = dict(id=id, series=series, ip=ip, name_en=name_en,
             name_en_src=name_en_src, pull=pull)
    d.update(kw)
    return d


def regulars(prefix, series, ip, names, src):
    """Bulk-make regular figures with no colour recorded."""
    out = []
    for n in names:
        slug = n.lower().replace("'", "").replace(".", "")
        slug = "".join(c if c.isalnum() else "-" for c in slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        out.append(fig("%s-%s" % (prefix, slug), series, ip, n, src))
    return out


import re  # noqa: E402  (used by regulars())

FIGURES = []

# Have a Seat -- roster verified by two independent catalogs
# The Chinese names are the ORIGINAL; the English ones are the doubled final
# syllable of each (眼巴巴 -> Baba). The pattern holds for all seven, but no
# single page lists both languages side by side, so the PAIRING is inference.
_SEAT = [
    ("Sisi", "甜丝丝", "yellow", "cream-yellow"),
    ("Hehe", "乐呵呵", "gray", "grey"),
    ("Baba", "眼巴巴", "brown", "golden-brown"),
    ("Zizi", "美滋滋", "blue", "purple"),
    ("Ququ", "委屈屈", "green", "green"),
    ("Dada", "羞答答", "pink", "pink"),
]
for _en, _zh, _c_en, _c_zh in _SEAT:
    _rec = dict(color=_c_en, color_src=S_SEAT,
                name_zh=_zh, name_zh_src=S_HUPU,
                name_pairing_src="inference")
    if _c_en != _c_zh and not (_c_en == "gray" and _c_zh == "grey"):
        _rec["contested"] = True
        _rec["note"] = ("Colour is contested: English sources say %s, the Chinese "
                        "listing says %s. Unresolved." % (_c_en, _c_zh))
        _rec["note_src"] = S_SEAT + " | " + S_WUYAW
    FIGURES.append(fig("hs-" + _en.lower(), "labubu-have-a-seat", "labubu",
                       _en, S_SEAT, **_rec))
FIGURES.append(fig("hs-duoduo", "labubu-have-a-seat", "labubu", "Duoduo",
                   S_SEAT2, pull="secret", odds="1/72", odds_src=S_SEAT2,
                   name_zh="趣多多", name_zh_src=S_HUPU,
                   name_pairing_src="inference",
                   color="chestnut", color_src=S_WUYAW,
                   note="Red nose and an extra sparkle in the finish. Stated as "
                        "1.4% per box. The 1/72 figure is retailer-disclosed (JD "
                        "and collector catalogs agree); Pop Mart's own page says "
                        "only that odds vary by set.",
                   note_src=S_SEAT2))

# Big into Energy -- colour deliberately omitted, sources conflict
FIGURES += regulars("bie", "labubu-big-into-energy", "labubu",
                    ["Hope", "Happiness", "Love", "Serenity", "Luck", "Loyalty"],
                    S_TZ_BIE)
FIGURES.append(fig("bie-id", "labubu-big-into-energy", "labubu", "ID",
                   S_TZ_BIE_ID, pull="secret", odds="1/72",
                   odds_src=S_TZ_BIE_ID,
                   note="Grey-furred, with rainbow-gradient glitter eyes and rainbow "
                        "teeth. Earlier reports of a \"rainbow-eyed\" secret and a "
                        "\"grey edition\" describe this one figure, not two.",
                   note_src=S_TZ_BIE_ID))

# Good Luck To You -- Thailand exclusive, single figure
FIGURES.append(fig("glty-labubu", "labubu-good-luck-to-you", "labubu",
                   "Good Luck To You", S_GLTY, pull="regular",
                   note="Sold openly, not as a blind box.", note_src=S_GLTY))

# The Sound -- full 12 + secret
FIGURES += regulars("sound", "skullpanda-the-sound", "skullpanda",
                    ["The Joy", "The Serenity", "The Ecstasy", "The Trust",
                     "The Admiration", "The Terror", "The Vigilance", "The Awe",
                     "The Anger", "The Disgust", "The Grief", "The Pensiveness"],
                    S_POOL_SOUND)
FIGURES.append(fig("sound-equilibrium", "skullpanda-the-sound", "skullpanda",
                   "The Equilibrium", S_POOL_SOUND, pull="secret", odds="1/144",
                   odds_src=S_TZ_SOUND))

# Crying Again -- 12 regulars + 3 tiered secrets
FIGURES += regulars("cry", "crybaby-crying-again", "crybaby",
                    ["Baby Brown", "Baby Blonde", "Heartless Girl", "Star Boy",
                     "Love is Love", "Love Makes Us Cry", "The Robber",
                     "She's Alice", "I'll Give You All My Love",
                     "I'll Bring You A Flower", "What A Frog", "Duck You"],
                    S_POOL_CRY)
FIGURES.append(fig("cry-shes-alice-halloween", "crybaby-crying-again", "crybaby",
                   "She's Alice Halloween Ver.", S_POOL_CRY, pull="secret",
                   odds="1/144", odds_src=S_TZ_CRY))
FIGURES.append(fig("cry-robber-red", "crybaby-crying-again", "crybaby",
                   "The Robber Red Ver.", S_POOL_CRY, pull="secret",
                   odds="1/144", odds_src=S_TZ_CRY,
                   note="Earlier community reports put this at 1/288. That number "
                        "belongs to The Queen of Broken Heart, the set's third and "
                        "rarest secret.", note_src=S_TZ_CRY))
FIGURES.append(fig("cry-queen-broken-heart", "crybaby-crying-again", "crybaby",
                   "The Queen of Broken Heart", S_POOL_CRY, pull="secret",
                   odds="1/288", odds_src=S_TZ_CRY,
                   note="The set's super secret — twice as rare as its two siblings.",
                   note_src=S_TZ_CRY))

# Crying Again plush -- same names, different rarity
FIGURES += regulars("cryp", "crybaby-crying-again-plush", "crybaby",
                    ["Duck You", "I'll Bring You A Flower",
                     "I'll Give You All My Love", "Love Makes Us Cry",
                     "She's Alice", "What A Frog"],
                    S_POOL_PLUSH)
for _n in ["Baby Blonde", "Baby Brown"]:
    FIGURES.append(fig("cryp-" + _n.lower().replace(" ", "-"),
                       "crybaby-crying-again-plush", "crybaby", _n, S_POOL_PLUSH,
                       pull="secret",
                       note="A secret in the plush line, but an ordinary regular in "
                            "the figures line of the same name.",
                       note_src=S_POOL_PLUSH))

# MOLLY Carb-Lover
FIGURES += regulars("carb", "molly-carb-lover", "molly",
                    ["Afternoon Tea", "Baker or Gardener", "Crocodile Bread",
                     "Croissant Balaclava", "Elegant Waffle", "Heart to Heart Toast",
                     "Let's Go Hot Dog", "Pick-a-Boo Burger", "Soft Punch",
                     "Sweet Ballet", "Taiyaki Princess", "Yummy Bread Shoes"],
                    S_POOL_CARB)
FIGURES.append(fig("carb-pretend-bear-bread", "molly-carb-lover", "molly",
                   "Pretend Bear Bread", S_POOL_CARB, pull="secret",
                   odds="1/144", odds_src=S_TZ_CARB))

FM_ORDER = ["node", "id", "ip", "series", "pull", "name_en", "name_en_src",
            "name_th", "name_th_src", "name_zh", "name_zh_src"]


def esc(v):
    s = str(v)
    if s == "":
        return '""'
    if any(c in s for c in ':#\n"') or s.strip() != s:
        return '"' + s.replace('"', '\\"') + '"'
    return s


def write_note(kind, rec):
    rec = dict(rec)
    body = rec.pop("body", "")
    rec["node"] = kind
    keys = [k for k in FM_ORDER if k in rec] + \
           sorted(k for k in rec if k not in FM_ORDER)
    lines = ["---"]
    for k in keys:
        lines.append("%s: %s" % (k, esc(rec[k])))
    lines.append("---")
    lines.append("")
    if body:
        lines.append(body)
        lines.append("")
    path = os.path.join(VAULT, kind, rec["id"] + ".md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing vault")
    a = ap.parse_args()

    existing = []
    for kind in ("ip", "series", "figure"):
        d = os.path.join(VAULT, kind)
        if os.path.isdir(d):
            existing += [x for x in os.listdir(d) if x.endswith(".md")]
    if existing and not a.force:
        print("vault already seeded (%d notes). vault/ is canonical — edit in "
              "Obsidian.\nRe-run with --force only to discard it." % len(existing))
        return 1

    for kind in ("ip", "series", "figure"):
        d = os.path.join(VAULT, kind)
        os.makedirs(d, exist_ok=True)
        for fn in os.listdir(d):
            if fn.endswith(".md"):
                os.remove(os.path.join(d, fn))

    ids = [f["id"] for f in FIGURES]
    dupes = set(x for x in ids if ids.count(x) > 1)
    if dupes:
        print("ERROR: duplicate figure ids: %s" % ", ".join(sorted(dupes)))
        return 2

    n = 0
    for r in IPS:
        write_note("ip", r); n += 1
    for r in SERIES:
        write_note("series", r); n += 1
    for r in FIGURES:
        write_note("figure", r); n += 1
    print("seeded %d notes into %s" % (n, VAULT))
    print("vault/ is now canonical. Edit in Obsidian; run build.py to publish.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
