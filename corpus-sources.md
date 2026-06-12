# Dharma AI — Source Text Corpus

> Research-backed list of the scripture/commentary sources for the Dharma AI corpus, with **copyright status flagged per source**. Compiled from a multi-source, fact-checked deep-research pass (June 2026).
>
> **Legend:** ✅ safe to use · ⚠️ usable with conditions · ⛔ copyrighted — do **not** use without a license

---

## 0. The Golden Rule (read this first)

Two court rulings (Delhi High Court; Bombay High Court, *Bhaktivedanta Book Trust* cases) set the legal frame we must build inside:

1. **The ancient scriptures themselves are public domain.** "There can be no copyright claimed in the Scriptures." The original Gita, Ramayana, Upanishads, etc. are free to use.
2. **Translations, commentaries, summaries, and interpretations are NOT.** They are "transformative works" and carry their **own independent copyright** owned by the translator/author. A translation of a public-domain text can itself be fully copyrighted.

**Therefore our rule:** we may only ingest text that is *either*
- an **old public-domain translation** (author died 100+ years ago / published before ~1929), **or**
- the **original Sanskrit** (always public domain), **or**
- a dataset under an **open license** (Unlicense / CC0 / CC-BY / public-domain dedication).

⚠️ **Dataset license ≠ text copyright.** A GitHub repo can be GPL/CC-BY on the *files* while bundling *copyrighted translations* inside. Always check both layers.

---

## 1. MVP Corpus — Recommended Starting Set (Hindu)

| Text | Recommended public-domain source | Where | Citation-ready? |
|---|---|---|---|
| **Bhagavad Gita** | `gita/gita` JSON dataset (Unlicense) for structure + K.T. Telang prose (SBE 8, 1882) for scholarly English | GitHub / sacred-texts.com | ✅ Yes — verse-keyed (BG ch:verse) |
| **Ramayana** | Ralph T. H. Griffith verse translation (1870–74) | sacred-texts.com | ⚠️ Verse, needs parsing |
| **Mahabharata** | Kisari Mohan Ganguli, complete 18-parva prose (1896) | sacred-texts.com (w/ Gutenberg) | ⚠️ Prose, parva/section structured |
| **Principal Upanishads** | Max Müller, SBE Vol. 1 (1879) + Vol. 15 (1884) | sacred-texts.com | ⚠️ Per-upanishad sections |
| **Yoga Sutras (Patanjali)** | Charles Johnston (1912) + Vivekananda's *Raja-Yoga* | sacred-texts.com | ✅ Sutra-numbered |
| **Vedas (selected)** | GRETIL Sanskrit originals + SBE *Vedic Hymns* (Müller) | Zenodo / sacred-texts.com | ⚠️ Selective |
| **Sanskrit originals (all)** | **GRETIL** plain-text corpus | **Zenodo, CC-BY-4.0** | ✅ IAST .txt |
| **Saint/commentary** | Swami Vivekananda, *Complete Works* (9 vols) | Wikisource + Archive.org | ✅ PD worldwide |

---

## 2. Per-Text Detail

### 2.1 Bhagavad Gita
- ✅ **`gita/gita` (GitHub)** — **Unlicense (public-domain dedication)** — the cleanest option. Structured JSON: `verse.json`, `chapters.json`, `translation.json`, `commentary.json`, `authors.json`, `languages.json`. Each verse has `chapter_number`, `verse_number`, `verse_order`, Devanagari Sanskrit, romanized transliteration, `word_meanings`. This is the data backend for **BhagavadGita.io**. ⚠️ `translation.json`/`commentary.json` bundle *multiple authors* — verify each author's license before using their text (some are modern/copyrighted).
- ✅ **K. T. Telang, "The Bhagavadgîtâ" (SBE Vol. 8, 1882)** — scholarly **prose**, public domain, numbered → good for citation. (sacred-texts.com)
- ✅ **Swami Swarupananda (1909)** — prose with commentary, public domain.
- ✅ **Edwin Arnold, "The Song Celestial"** — Project Gutenberg **#2388**, public domain. ⚠️ Rendered as *dramatic verse*, **not numbered verses** → poor for exact ch:verse citation. Use for flavor, not as the citation backbone.
- ⚠️ **`vedicscriptures/bhagavad-gita` + its REST API** — GPL-3.0 on code; verses keyed `BG1.1` with Sanskrit + transliteration + Hindi. Bundles copyrighted 20th-c. commentators → don't ship those commentaries.
- ⛔ **Prabhupada / ISKCON "Bhagavad-Gita As It Is" (Bhaktivedanta Book Trust)** — copyrighted and **actively litigated** (Bombay HC injunction vs Thomson Press). Do not use.
- ⛔ **Eknath Easwaran (Nilgiri Press, ISBN 9781586380199)** — commercial, copyrighted.

### 2.2 Ramayana
- ✅ **Ralph T. H. Griffith, verse translation (1870–1874)** — "the first complete public-domain Ramayana online." (sacred-texts.com) Also Sanskrit Ramayana available there.
- ✅ R. Dutt (1899) abridgment also listed (public domain) — condensed.

### 2.3 Mahabharata
- ✅ **Kisari Mohan Ganguli, complete unabridged English prose, all 18 parvas (1896)** — public domain by age. Best acquired from **sacred-texts.com** (digitized jointly with Project Gutenberg).
- ⚠️ **Archive.org compiled edition** has a handy 14.5 MB plain-text `.txt`, **BUT that specific upload is CC BY-NoDerivatives 4.0** (restricts derivatives of *that edition*). Prefer the sacred-texts/Gutenberg source text to avoid the ND restriction.

### 2.4 Principal Upanishads
- ✅ **Max Müller, Sacred Books of the East — Part I = Vol. 1 (1879), Part II = Vol. 15 (1884)** — the canonical public-domain English set. Covers Chandogya, Kena, Aitareya, Kaushitaki, Isha (Part I) and Katha, Mundaka, Taittiriya, Brihadaranyaka, Svetasvatara, Prasna, Maitrayana (Part II). (sacred-texts.com)

### 2.5 Vedas (selected portions)
- ✅ **GRETIL** has all four Vedas in Sanskrit (machine-readable).
- ✅ **SBE "Vedic Hymns" (Müller)** — public-domain English selections.
- ⚠️ **Gutenberg #12894 "Sacred Books of the East"** (Epiphanius Wilson, ed., 1900) — a *selections anthology*, not the full series; mixes Vedic Hymns + Upanishads with non-Hindu texts. Partial coverage only.

### 2.6 Yoga Sutras of Patanjali
- ✅ **Charles Johnston (1912)** — public domain (sacred-texts.com). *(Note: the spec named James Haughton Woods' edition; Woods' 1914 translation is also public domain and more literal/scholarly — both are options.)*
- ✅ **Swami Vivekananda, *Raja-Yoga*** — his rendering + commentary on Patanjali (public domain).

### 2.7 Saints & Commentary (public-domain)
- ✅ **Swami Vivekananda — *Complete Works* (9 vols + misc.)** — **public domain worldwide** (died 1902; published before 1931). Includes Karma-Yoga, Raja-Yoga, Bhakti-Yoga, Jnana-Yoga, Practical Vedanta. ⚠️ Wikisource transcription is **incomplete** → supplement from **Archive.org** (Advaita Ashrama editions) for full text.
- ⚠️ **Adi Shankaracharya's commentaries (bhashyas)** — the *original Sanskrit* is public domain, but specific *modern English translations* of them are usually copyrighted. Use Sanskrit originals (GRETIL) or pre-1929 translations only.
- ⛔ **Sivananda, Chinmayananda, Tejomayananda, Prabhupada and other 20th-c. commentators** — copyrighted.

---

## 3. Structured / Machine-Readable Datasets (license comparison)

For exact verse-reference citation, prefer these — but mind the license column.

| Dataset | License | Contents | Verdict |
|---|---|---|---|
| **`gita/gita`** (GitHub) | **Unlicense (PD)** ✅ | Gita: verse/chapter/translation/commentary JSON, ch+verse numbering, Sanskrit+translit | **Best for Gita** |
| **GRETIL on Zenodo** (rec. 6466333, DOI 10.5281/zenodo.6466333) | **CC-BY-4.0** ✅ | Sanskrit originals of Mahabharata, Gita, Ramayana, Upanishads, all Vedas, Yoga texts; plain-text IAST `.txt` | **Best for Sanskrit** (attribution only) |
| **SuttaCentral `bilara-data`** | **CC0** ✅ | Buddhist Pali Canon root + translations, segmented JSON keyed `mn1:1.1` | **Best for future Buddhist** |
| **GRETIL GitHub mirror** | No explicit license ⚠️ | TEI/XML + Unicode; Mahabharata absent from TEI dir | Use the Zenodo CC-BY version instead |
| **`vedicscriptures/bhagavad-gita(-api)`** | GPL-3.0 (code) ⚠️ | Gita JSON / REST API, `/slok/:ch/:sl`, 700 verses | OK for structure; don't ship bundled copyrighted commentaries |
| **DharmicData** | **ODbL** ⚠️ | Sanskrit + Hindi only, hierarchical (kaand/mandala/sukta/mantra); **no English**; provenance unverified | Share-alike obligations; caution |
| **`gita/Datasets`** | **No license disclosed** ⛔ | Charak Samhita, Chanakya Niti, Srimad Bhagavatam JSON (not the Gita itself) | Unsafe — undetermined rights |

---

## 4. Future-Phase Texts (Phase 2+)

- **Buddhist** — ✅ **SuttaCentral `bilara-data`** (CC0): Pali Canon root texts + parallel EN/DE translations, segment-level IDs. Plus ✅ **SBE Vol. 10 — Dhammapada** (Müller, from Pali) + Sutta Nipata.
- **Jain** — ✅ **SBE Vols. 22 & 45 — Jaina Sutras** (public domain).
- **Sikh** — *not covered by this research pass; flagged as a TODO (Guru Granth Sahib public-domain English translations need a dedicated check).*

---

## 5. Recommended Acquisition Plan (MVP)

1. **Gita first** — ingest `gita/gita` (Unlicense) as the structured, verse-citable backbone; layer Telang (SBE 8) prose English. This alone powers the PRD's flagship "What would the Gita say?" demo.
2. **Sanskrit layer** — pull **GRETIL from Zenodo (CC-BY-4.0)** for original-language grounding + transliteration across all priority texts.
3. **Epics + Upanishads** — Ganguli Mahabharata, Griffith Ramayana, Müller Upanishads (all from sacred-texts.com).
4. **Voice/persona color** — Vivekananda *Complete Works* (Archive.org) for the "Vivekananda guide" persona, public domain.
5. **Attribution file** — since GRETIL is CC-BY, maintain a `CREDITS.md` listing each source + translator + license. (Good practice anyway for the PRD's "every answer traceable to source" promise.)

---

## 6. Compliance Checklist (per source, before ingest)

- [ ] Is the **underlying text** public domain? (ancient scripture → yes)
- [ ] Is the **translation** pre-~1929 / author died 100+ yrs ago, OR openly licensed?
- [ ] What is the **dataset/file license** (Unlicense/CC0/CC-BY/GPL/ODbL/ND/none)?
- [ ] If CC-BY/ODbL → record attribution in `CREDITS.md`.
- [ ] If a dataset **bundles multiple translators** → verify each author individually.
- [ ] ⛔ Confirmed it is **not** Prabhupada/BBT, Easwaran, or other modern copyrighted commentary.

---

*Sources: Delhi High Court & Bombay High Court rulings on scripture copyright; sacred-texts.com; Project Gutenberg (#2388, #12894); Archive.org; Wikisource; GRETIL (Göttingen / Zenodo); GitHub (`gita/gita`, `vedicscriptures/*`, SuttaCentral `bilara-data`, DharmicData). Each claim was independently fact-checked (3-vote adversarial verification) during research.*
