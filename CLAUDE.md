# Writing for this site

Before writing or editing any page copy or blog post, read the guides in `content-guide/`:

1. `humour.md`
2. `voice.md`
3. `opinions.md`
4. `stats.md` — the only numbers allowed
5. `stories.md` — the only anecdotes allowed

Brand: **Renovo Studio** (logo: `assets/img/renovo-logo.png`). Keep the existing design. These guides are for tone and content only.

**Voice override:** Renovo Studio is an agency, so site copy uses **"we"**, not "I" — this overrides the "I, not we" rule in `voice.md`. Matthew Rissik can be named as the founder.

Services (4): Web Design · SEO & Local SEO (technical audits + content live inside it) · GTM & Outbound (cold email + LinkedIn) · Full Growth System.
The $7.2M figure may be used as "generated for clients, collectively".
"32%+" is a **positive reply rate** (interested replies ÷ replies), never a plain reply rate.

## Case studies
- Source of truth: `_source/case-studies.json` (+ `_source/BUILD.md`). `_source/` is not published; it contains `internalSourceNote`, which must never appear on the site.
- Pages, the work grid, campaign results, homepage project cards and the sitemap are generated: edit the JSON (or the site-specific copy in `tools/build_case_studies.py`), then run `python3 tools/build_case_studies.py`.
- Never change a fact from the JSON. Keywords are tracked in `content-guide/keyword-log.md`.
