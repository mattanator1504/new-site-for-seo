# Level Up Digital — Web Design & SEO agency site

Static site (plain HTML/CSS/JS, no build step). Open `index.html` or serve the folder:

```sh
python3 -m http.server 8000
```

## Pages
| File | Page |
| --- | --- |
| `index.html` | Home — hero, marquee, scroll-lit manifesto, stats, services, horizontal-scroll work, process, founder, CTA |
| `services.html` | All services with anchors (`#web-design`, `#seo`, `#local-seo`, `#technical-seo`, `#copywriting`, `#lead-generation`) + FAQ |
| `work.html` | Featured case study + filterable project grid |
| `blog.html` | Featured article + upcoming posts + newsletter |
| `contact.html` | Contact form (accepts `?service=<slug>` to pre-select a service) |

The **Services** item in the header is a dropdown listing every service. Right now each item links to its
section on `services.html`; when the dedicated service pages are built, change those links to e.g. `services/web-design.html`.
The header and footer are repeated in every HTML file, so update all five when changing navigation.

## Motion
All in `assets/js/main.js` (no libraries): page-transition curtain, split-letter headline reveals, scroll reveals,
parallax (`data-speed`), mouse parallax in the hero (`data-depth`), velocity-reactive marquees, a pinned horizontal-scroll
work section, a scroll-scrubbed manifesto, number counters, magnetic buttons and a custom orbit cursor.
Everything respects `prefers-reduced-motion`.

## Before going live
- [ ] Replace `hello@example.com` on `contact.html` with your business email.
- [ ] Set the contact form `action` (Formspree, Netlify Forms, Basin…) — with `action="#"` it validates but doesn't send.
- [ ] Set the newsletter form `action` on `blog.html`.
- [ ] Replace `https://www.example.com` in `sitemap.xml` and `robots.txt`; add `<link rel="canonical">` and `og:image` per page.
- [ ] Swap illustrations for real project screenshots in `work.html` / `index.html` (`<img class="shot" ...>` fills the card)
      and add a photo to the founder section (`<img class="photo" ...>`).
- [ ] Replace the placeholder project cards (marked "Case study soon") with real portfolio projects, and the "Coming soon" blog cards with real posts.
