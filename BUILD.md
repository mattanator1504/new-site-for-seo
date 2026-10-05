# Build brief: case studies

This folder holds Matthew Rissik's client case studies, exported from matthewrissik.com on the date in `case-studies.json`. The job is to add them to **this** site, using this site's own stack, components, design and rules. Read this file in full before writing code.

## What's here

| Path | What it is |
|------|-----------|
| `case-studies.json` | The source of truth. Build pages from this file. |
| `case-studies/*.md` | The same 16 case studies as readable text, for checking only. |
| `images/projects/` | `<slug>.webp` = full/hero image, `<slug>-card.webp` = card thumbnail. |
| `images/campaigns/` | Cold email dashboard screenshots: `<slug>.webp` full size, `<slug>-thumb.webp` thumbnail. |

`case-studies.json` has three lists:

1. **`caseStudies`** (16): full case studies. Each one gets its own page plus a card on the work/portfolio index.
2. **`projectCards`** (11): card only. There's no case study source for these, so **no page**. Show the image, client, category, tags and `summary` (some have an empty summary; show the image and name only).
3. **`campaigns`** (19): real cold email campaign results, read off dashboard screenshots. Items with `isTable: true` are multi-campaign dashboards with a `note` instead of numbers.

## Case study fields

| Field | Use |
|-------|-----|
| `slug` | URL segment, e.g. `/case-studies/medspa-dr` (use this site's existing pattern for the path) |
| `client`, `category`, `tags` | Card and page header |
| `summary` | One line for the card |
| `h1` | Page heading |
| `year` | Timeframe (it's not always a year, e.g. "60 days") |
| `role` | What the work was |
| `website` | Client's live site, where present |
| `stats` | 2–4 headline results `{ value, label }`. Show them big, near the top |
| `short` | 40–60 word summary, directly under the H1 |
| `situation` | Paragraphs: the client's problem |
| `built` | `{ title, body }` items: what was done |
| `happened` | Paragraphs: the results |
| `differently` | One closing takeaway, shown as a pull quote |
| `services` | Service slugs **from matthewrissik.com** (`web-design`, `seo`, `outbound-lead-generation`, `full-growth-system`). Map them to this site's own service pages, or drop the links if there's no match |
| `title`, `metaDescription`, `primaryKeyword` | SEO from the original page. **Rewrite** the title and meta for this site so they don't duplicate matthewrissik.com. Check this site's keyword log first and don't reuse a keyword it already targets |
| `imageAlt`, `images.full`, `images.card` | Copy the images into this site's image folder and keep the alt text |
| `internalSourceNote` | Where the numbers came from. **Never publish this.** |
| `published`, `updated` | Original dates. Use today's date for this site's `published` |

## Campaign fields

`sent` = emails sent, `replies` = total replies, `replyRate` = replies ÷ sent, `positive` = interested replies, `positiveRate` = positive ÷ replies. Label `positiveRate` as **"positive reply rate"**, never just "reply rate". The two are different numbers.

## Rules

1. **Don't change any fact.** Every number, client name, result, timeframe and quote stays exactly as exported. Don't add results, testimonials, logos or clients that aren't in this folder. If something seems missing, leave it out; don't fill the gap.
2. **Voice.** The copy is written by Matthew in the first person ("I"). If this site speaks as an agency ("we"), adapt the pronouns and tone to fit this site's voice guide, but keep the meaning and every fact.
3. **No duplicate content.** These pages also live on matthewrissik.com. Rewrite titles and meta descriptions. Where this site's guidelines allow, lightly reword the `short` and `situation` text rather than pasting it word for word, and keep the facts identical.
4. **Use what this site already has.** Its components, page templates, schema helpers, sitemap and design tokens. Follow this repo's own `CLAUDE.md` or README over anything in this brief, except rule 1.
5. **Schema:** `Article` (or `CreativeWork`) per case study page, `BreadcrumbList`, and whatever this site already adds site-wide.
6. **Don't link to matthewrissik.com** unless this site's owner asks for it.

## Done means

- 16 case study pages and an index showing all 27 projects (16 linked, 11 card-only)
- Campaign results shown, if this site has a sensible place for them (ask if unsure)
- Every image loads, with alt text
- This site's build and checks pass
