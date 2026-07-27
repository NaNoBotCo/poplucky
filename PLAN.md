# Poplucky — a global, multilingual companion for Pop Mart collectors

*Plan drafted 2026-07-27. Name LOCKED: **Poplucky** — domain purchased 2026-07-27. "Lucky" is already a Thai-English loanword (ลัคกี้), so the name reads natively to the bilingual audience; luck + potluck = fortune and sharing, the hobby's two halves.*

## 1. Who these people are and what they uniquely want

Pop Mart enthusiasts are blind-box collectors (Labubu, Molly, Skullpanda, Crybaby, Hirono, Dimoo…). Their wants are genuinely odd:

- **They buy sealed mystery boxes on purpose.** The unit of joy is the reveal, and the unit of grief is the duplicate. Everyone has dupes; everyone wants trades.
- **They do probability math recreationally.** Chase/"secret" figures run ~1-in-72 or 1-in-144; a standard case of 12 guarantees no repeats *within the case*. "What will it cost me to complete this set?" is a real, daily question with a real expected-value answer nobody computes for them.
- **They fear fakes.** "Lafufu" counterfeits are an industry; verification ritual = QR scratch code + nine teeth + matte box. They want a calm reference, not a verdict machine.
- **They chase drops across borders.** Regional exclusives (Thailand's "Good Luck To You" Labubu, China-only collabs, US con exclusives) mean the same character exists in market-specific editions — and collectors track markets they don't live in.
- **They gift and display.** Wishlists exist so friends buy the *right* blind box; shelves are curated and photographed.
- **They speak three vocabularies at once.** Official Chinese names, official English names, and per-language fan slang (隐藏款 / secret / ซีเคร็ท; Lafufu; "chase"; "pull") — no existing surface holds all of them.

## 2. The gap and our edge

Existing surfaces: the official POP MART app (shop + ownership verification), Bubuspace (indie checklist tracker, ~900 items), TYPA (restock-tracker blog), and a sea of authentication blog posts. All are catalog-shallow, single-language-ish, and none treat the taxonomy as the product.

Our edge is the amulet playbook, re-aimed: **emic-term-primary, faceted, per-field provenance, folksonomy intake feeding a curated ontology.** Sale listings and shop apps destroy the axes collectors actually think in; we restore them.

## 3. The spine: the faceted catalog

Axes (each value a normalized node, multi-valued where reality is):

| Axis | Examples | Amulet analogue |
|---|---|---|
| **IP / character** | Labubu (The Monsters), Molly, Skullpanda, Crybaby, Hirono | the deity/master |
| **Series / release** | "Have a Seat" (2024), "Big into Energy", date + artist | รุ่น (batch) |
| **Variant / pull** | the 6–12 regulars + secret(s), with disclosed odds | พิมพ์ (mold) |
| **Form / material** | vinyl figure, plush pendant, MEGA 400%/1000%, accessory | เนื้อ (material) |
| **Edition scope** | global, regional exclusive (market), collab, con exclusive | wat-specific issue |

Every record carries per-field provenance (official page, disclosed odds sheet, community report — marked as such) and every name field is multilingual with register noted (official vs fan-vernacular). Fan slang enters as folksonomy tags and gets promoted into the ontology when it stabilizes — desire paths first, curbs later.

## 4. Multilingual strategy

Locale = **language × market**, not just translated UI. A Thai reader sees Thai fan names first, Thai-exclusive editions surfaced, THB context; a Chinese reader sees 官方 names first. Launch trio: **EN / TH / ZH** (the three vocabularies the hobby actually runs on), architecture ready for JA/KO/ES. Cross-language name search is a headline feature: paste any name in any register, land on the node.

## 5. Phases (narrow now, easy to widen)

**Phase 0 — the catalog spine. ✅ BUILT 2026-07-27.** 4 characters · 7 series · 64 figures · 77 pages · 75 open questions. Vault-canonical (`vault/`, Obsidian-editable) → `build.py` → `docs/`. Directory-genre nav with counts, EN/TH/ZH toggle, per-field provenance table on every page, share card per page, `/iso/` gap list. Verified in browser in all three languages. See README for what is and isn't verified.

*Built on stdlib Python → static HTML, not Astro+Tailwind as specified below — matching mot-dang/wichaa/defiant. One less toolchain; the vault-canonical pattern is unchanged.*

**Phase 1 — My Shelf. ✅ BUILT 2026-07-27.** localStorage `poplucky.shelf.v1`, no accounts, backup/restore JSON. Controls on every card and figure page; owning clears seeking (a trade card must never offer and request the same figure). `/shelf/` = tallies, per-set completion bars, doubles, seeking. Trade card drawn in canvas at 1200×630 — PNG or plain text — so **Thai and Chinese shape correctly**, unlike the Pillow og:images. Verified in EN/TH/ZH.

*Original wording:* Collection tracker: localStorage-first, zero accounts. Mark owned/wished/dupe per variant. The delight: marking a figure owned plays a box-opening reveal animation. Dupes auto-compose a **trade card** — a beautiful shareable ISO/FT image ("have these / seeking these", bilingual) for the FB groups and Discords where trading already happens. We host no marketplace; we make the flyer.

**Phase 2 — the odds toolkit.** Set-completion calculator (box price, case size, disclosed secret odds → expected cost to finish, dupe-count distribution), gift-wishlist links, series completion meters.

**Phase 3 — contributions + reference.** Cloudflare Worker moderation queue (the mueang-map-sync pattern) for community submissions: new releases, regional sightings, fan-name folksonomy. Calm authenticity *reference* pages per series (what official verification looks like, link to Pop Mart's own QR flow) — we describe the ritual, never issue verdicts.

**Later, if earned:** drop/restock calendar (needs data ops), secondary-market price observation as an analytical dashboard — analysis and discovery, never a storefront.

## 6. Tech shape

- **Authoring:** Obsidian vault as canonical source — one note per node with frontmatter facets, same pattern as wichaa-vault. Compiled to site by the build.
- **Build/site:** Astro + Tailwind v4 (hakfarang stack) → Cloudflare Pages. PWA offline for the catalog + shelf.
- **State:** localStorage until accounts are truly needed; when they are, Continue-with-Google first.
- **Interactive tier:** one Worker (+ D1) for the moderation queue and trade-card rendering, added only in Phase 3.
- **Cards:** make_card.py-style generator; every figure page ships its own og:image.
- **CSS:** full send — glassmorphism blind-box reveals, squishy hover on figure tiles, a magnetic shelf. The audience is *exactly* the audience for this.

## 7. Wording & delights

- Auspicious framing throughout: no "you failed the pull" — the shelf grows, the search continues, luck accumulates. The Thai exclusive is literally named "Good Luck To You"; that's the register.
- Hidden bells: a shake-the-box easter egg on series pages; the 1/144 chase figure gets a subtle shimmer wherever it appears; completing a set rings something.

## 8. Deliberately out of scope

- **No purchase automation / bots / restock sniping.** Half the "guides" online are bot tutorials; that lane is hostile to the community and to Pop Mart, and we don't drive in it.
- **No marketplace, payments, or escrow.** Trade cards yes; transactions never.
- **No authenticity verdicts.** Reference only; verdicts are liability plus false confidence.
- **No official product photography.** Pop Mart's images are theirs. Own photos, community-contributed CC photos with credit, or stylized silhouettes until then. Nominative use of names only; clear "fan project, not affiliated" footer. This is the one legal edge worth respecting from day one.

## 9. Risks, plainly

- **Catalog freshness is the treadmill.** Pop Mart releases constantly; the Worker intake queue is the long-term answer, an authoring cadence is the short-term one.
- **Bubuspace could deepen.** Our moat is the taxonomy + trilingual vocabulary + trade cards, not the checklist.
- **Trademark attention.** Fan catalogs generally live fine under nominative use; the no-official-images rule keeps us there.

## 10. Open questions

1. Name — Popluck? (folder renames trivially)
2. Beachhead — global-neutral launch, or lean Thai-first where the mania and the exclusives are richest?
3. wichaa crossover — Labubu-blessed-at-wats is a real phenomenon; a wichaa page on charm-ification of art toys could link here. Bridge, not merger: this app is its own global product.
