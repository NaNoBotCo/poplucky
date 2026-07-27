# Poplucky

A collector's catalogue for Pop Mart blind boxes — faceted, trilingual (EN/TH/ZH),
and honest about what it doesn't know.

Live target: **poplucky.net** (domain purchased 2026-07-27, not yet deployed)

## What this is

Existing surfaces treat these figures as products. Poplucky treats them as a
taxonomy: character × series × variant/pull × form × edition scope, with
per-field provenance on every claim and a first-class page for the gaps.

The same shape as the amulet work — วัด × รุ่น × พิมพ์ × เนื้อ — pointed at
vinyl.

## Run it

```bash
python3 build.py
```

That reads `vault/` and writes `docs/`, including share cards. Stdlib only,
except Pillow for the cards (cards are skipped cleanly if Pillow is missing).

Preview locally:

```bash
python3 -m http.server 8765 --directory docs
```

## Layout

| Path | What it is |
|---|---|
| `vault/` | **Canonical.** One Markdown note per node, Obsidian-editable. |
| `vault/ip/` | Characters — Labubu, MOLLY, SKULLPANDA, CRYBABY |
| `vault/series/` | Releases — Have a Seat, Big into Energy, The Sound… |
| `vault/figure/` | Individual figures, regular and secret |
| `build.py` | vault → docs. Also emits catalog.json, sitemap, CNAME. |
| `shelf.py` | Phase 1 — shelf CSS/JS and the trade-card canvas. |
| `art.py` | Procedural blind-box artwork, the odds wall, and their CSS. |
| `make_cards.py` | og:image per page, into `docs/cards/` |
| `seed_vault.py` | One-time initial import. Historical after seeding. |
| `docs/` | Build output. **Wiped every build — never hand-place files here.** |

## The provenance rule

Every fact field may carry a sibling `<field>_src`:

| Value | Means |
|---|---|
| a URL | sourced from that page |
| `official` | from popmart.com itself |
| `community` | collector catalog or community consensus |
| `inference` | model inference, **not verified** — counts as a gap |
| absent | unknown, not yet researched — counts as a gap |

Gaps aren't hidden. They're collected at build time and published at `/iso/`
("In Search Of" — the collectors' own term for what they're hunting, doing
double duty for what the catalogue is hunting).

### What is genuinely unverified right now

popmart.com is JavaScript-rendered and would not yield a product page body to
any fetch. **No roster and no odds figure here is confirmed against Pop Mart's
own pages** — they rest on thetoypool.com and toysez.com, which independently
agree with each other. Closing that needs a real browser session.

Chinese *series* names are the exception and are properly official: Pop Mart's
HK/MO/TH storefronts put the Chinese title in the product URL, and the same
numeric product ID serves both the Chinese and English titles. That ID match is
what proves 眼泪工厂系列 == "Crying Again" — a renaming, not a translation.

## My Shelf (Phase 1)

Account-free by design. State lives in `localStorage` under `poplucky.shelf.v1`
as `{figureId: {n: <how many you own>, w: <seeking?>}}`. Nothing is sent
anywhere, so **Back up the shelf** on `/shelf/` writes a JSON file and
**Restore** reads one back — that is the whole recovery story, and the page
says so plainly rather than pretending the data is safe.

Controls sit on every figure card and on each figure's own page: `−` / count /
`+`, plus a heart for seeking. Owning something clears seeking it, and the
heart is disabled while you own one — otherwise a trade card could offer and
request the same figure in the same breath. The first copy of anything gets a
small pop and a burst of sparkles, suppressed under `prefers-reduced-motion`.

`/shelf/` totals what you have, shows per-set completion bars, and lists your
doubles and your seeking list. Numbers on doubles are **spares** (own 3, offer
2) because that is what a trade post means by a count.

### Trade cards

The point of the phase. Doubles and seeking compose into a 1200×630 card drawn
in a browser canvas, saveable as PNG or copyable as plain text for chat. It is
a flyer for the Facebook groups and Discords where trading already happens —
Poplucky hosts no trades, takes no cut, and sees none of it.

Drawing in canvas rather than Pillow means **Thai and Chinese shape correctly**
on trade cards, unlike the og:image cards. Same reason: the browser has a real
text engine.

## The artwork: why boxes, not figures

Poplucky uses no Pop Mart product photography, and drawing the characters
would be derivative work wearing a different hat. But a blind-box collector
does not face a figure — they face a **sealed box**, and what is inside is
unknown until it is opened. So the box is the icon here. It is honest to the
hobby, it is entirely our own drawing, and it gives every figure an image
without borrowing anything.

Each box is generated deterministically from the figure's id, tinted by the
colour the catalogue actually recorded (or, where no colour is known, by a
stable hue drawn from the character's family so a series still reads as a
set). Secrets get holographic foil. Ribbon, pattern and tilt vary by id so a
shelf does not look stamped.

**Owned boxes open.** Mark something on your shelf and its lid tilts off with
light spilling out of it; everything you do not own stays sealed. That single
piece of state turns a catalogue page into a picture of your own collection.

### Odds, drawn to scale

A secret at 1/144 is an abstraction until you see it. Series and figure pages
render the odds as a wall of that many boxes with exactly one lit — 72 cells,
144, 288. It communicates rarity in a way the fraction never does.

## Participatory

Every page carries a share row, **LINE first**, because that is where Thai
collectors actually talk — plus Facebook, X, and copy-link.

Contributing needs no backend and no account for us to run: gaps and
contradictions link to a **pre-filled GitHub issue**, the same trick mot-dang
uses. Every one of the open questions on `/iso/` has its own "help" link that
opens an issue naming that specific gap, and any figure whose sources disagree
carries a prompt saying so in plain words — we would rather be corrected than
confident.

## Deliberately out of scope

- No purchase automation, restock sniping, or bots.
- No marketplace, payments, or escrow.
- No authenticity verdicts — reference only.
- **No official Pop Mart product photography.** Own photos, community-contributed
  CC photos with credit, or nothing. Nominative name use only, with a standing
  not-affiliated footer on every page.

## Deviation from PLAN.md

The plan specified Astro + Tailwind v4. This is stdlib Python → static HTML
instead, matching mot-dang / wichaa / defiant. One less toolchain, same output,
and the vault-is-canonical pattern is identical either way. Revisit if the site
grows interactive beyond what a static build can carry.

## Known gaps in the tooling

- Note bodies are English-only; only names, UI chrome and labels are trilingual.
- Share cards render the English name only — this Pillow has no raqm, so Thai
  will not shape correctly. Thai-script cards need a shaping engine.
- Colour vocabulary ("brown", "pink") is not translated.
