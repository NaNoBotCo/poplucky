# Poplucky

A collector's catalogue for Pop Mart blind boxes — faceted, trilingual (EN/TH/ZH),
and honest about what it doesn't know.

Live target: **poplucky.com** (domain purchased 2026-07-27, not yet deployed)

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
