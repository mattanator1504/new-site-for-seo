#!/usr/bin/env python3
"""Check every page against the ⚙ items in content-guide/on-page-seo.md.

Usage:  python3 tools/seo_check.py          (exit code 1 if anything fails)
Standard library only.
"""
import glob, json, os, re, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from seo import SITE_URL, url_for  # noqa: E402

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
VAGUE = {"click here", "here", "read more", "more", "learn more", "this", "link"}
BANNED_SCHEMA = {"LocalBusiness", "ProfessionalService", "Review", "AggregateRating"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags, self.stack, self.headings, self.links, self.jsonld = [], [], [], [], []
        self.title, self._in, self._buf = "", None, []
        self.first_body_child = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append((tag, a))
        if self.first_body_child is None and self.stack and self.stack[-1] == "body":
            self.first_body_child = (tag, a)
        if tag in ("title", "h1", "h2", "h3", "h4", "h5", "h6", "a", "script") and self._in is None:
            if tag != "script" or a.get("type") == "application/ld+json":
                self._in, self._attrs, self._buf = tag, a, []
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if self._in == tag:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if tag == "title":
                self.title = text
            elif tag == "a":
                self.links.append((self._attrs, text))
            elif tag == "script":
                self.jsonld.append("".join(self._buf))
            else:
                self.headings.append((int(tag[1]), text, self._attrs))
            self._in = None
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass

    def handle_data(self, data):
        if self._in:
            self._buf.append(data)


def types_in(obj):
    out = []
    if isinstance(obj, dict):
        t = obj.get("@type")
        out += t if isinstance(t, list) else [t] if t else []
        for v in obj.values():
            out += types_in(v)
    elif isinstance(obj, list):
        for v in obj:
            out += types_in(v)
    return out


def check(path):
    errs = []
    src = open(path).read()
    p = Page()
    p.feed(src)
    tags = p.tags
    metas = {(a.get("name") or a.get("property")): a.get("content", "") for t, a in tags if t == "meta"}
    is_home = path == "index.html"
    rel = path

    # 1. Head
    if not 50 <= len(p.title) <= 60: errs.append(f"title {len(p.title)} chars (50–60): {p.title}")
    d = metas.get("description", "")
    if not 140 <= len(d) <= 160: errs.append(f"meta description {len(d)} chars (140–160)")
    canon = [a.get("href") for t, a in tags if t == "link" and a.get("rel") == "canonical"]
    if canon != [url_for(rel)]: errs.append(f"canonical {canon} != {url_for(rel)}")
    for k in ("og:title", "og:description", "og:image", "og:url", "og:type"):
        if not metas.get(k): errs.append(f"missing {k}")
    if metas.get("og:url") and metas["og:url"] != url_for(rel): errs.append("og:url differs from canonical")
    if metas.get("twitter:card") != "summary_large_image": errs.append("twitter:card")
    html_tag = next((a for t, a in tags if t == "html"), {})
    if html_tag.get("lang") != "en-US": errs.append('lang is not "en-US"')
    if not any(t == "meta" and "charset" in a for t, a in tags): errs.append("charset")
    if "viewport" not in metas: errs.append("viewport")
    if "noindex" in metas.get("robots", ""): errs.append("noindex on a ranking page")

    # 2. URL
    if not re.fullmatch(r"[a-z0-9\-/]+\.html", rel): errs.append("URL not lowercase-hyphen")

    # 3. Headings
    h1s = [h for h in p.headings if h[0] == 1]
    if len(h1s) != 1: errs.append(f"{len(h1s)} H1s")
    prev = 0
    for lvl, text, _ in p.headings:
        if prev and lvl > prev + 1: errs.append(f"skipped heading level h{prev}→h{lvl} ({text[:40]})")
        prev = lvl

    # 5/9. Schema
    blocks = []
    for raw in p.jsonld:
        try:
            blocks.append(json.loads(raw))
        except json.JSONDecodeError as e:
            errs.append(f"JSON-LD does not parse: {e}")
    types = [t for b in blocks for t in types_in(b)]
    for need in ("Organization", "WebSite"):
        if need not in types: errs.append(f"missing {need} schema")
    for bad in BANNED_SCHEMA & set(types): errs.append(f"banned schema type {bad}")
    if not is_home and "BreadcrumbList" not in types: errs.append("missing BreadcrumbList schema")
    visible = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", "", src, flags=re.S)))
    import html as H
    visible = H.unescape(visible)
    for b in blocks:
        if b.get("@type") == "FAQPage":
            for q in b["mainEntity"]:
                for txt in (q["name"], q["acceptedAnswer"]["text"]):
                    if txt not in visible: errs.append(f"FAQ text not visible: {txt[:50]}")

    # 6. Images
    for t, a in tags:
        if t == "img":
            if "alt" not in a: errs.append(f"img without alt: {a.get('src')}")
            if not (a.get("width") and a.get("height")): errs.append(f"img without width/height: {a.get('src')}")

    # 7/8. Links
    if not is_home and not any(t == "nav" and a.get("aria-label") == "Breadcrumb" for t, a in tags): errs.append("no visible breadcrumbs")
    for a, text in p.links:
        if a.get("target") == "_blank" and "noopener" not in (a.get("rel") or ""): errs.append(f"_blank without noopener: {a.get('href')}")
        label = (a.get("aria-label") or text).strip().lower().rstrip(" →↗")
        if label in VAGUE: errs.append(f"vague link text: {text}")
        if "matthewrissik.com" in (a.get("href") or "") and "mailto:" not in a.get("href"): errs.append(f"link to matthewrissik.com: {a.get('href')}")

    # 11. Accessibility
    names = [t for t, a in tags]
    for lm in ("header", "nav", "main", "footer"):
        if lm not in names: errs.append(f"missing <{lm}>")
    if rel.startswith(("case-studies/", "blog/")) and "article" not in names: errs.append("missing <article>")
    fb = p.first_body_child
    if not (fb and fb[0] == "a" and "skip-link" in fb[1].get("class", "")): errs.append("skip link is not first in <body>")
    for t, a in tags:
        if "data-filter" in a and (t != "button" or "aria-pressed" not in a): errs.append("filter control not a <button> with aria-pressed")

    # 13. Conversion
    if not any(t == "a" and "nav-cta" in a.get("class", "") and a.get("href", "").endswith("contact.html") for t, a in tags):
        errs.append("no Book a call CTA in the header")

    # 15. H2 ids on long-form
    words = len(visible.split())
    if rel.startswith("blog/") and words > 1500:
        for lvl, text, a in p.headings:
            if lvl == 2 and not a.get("id"): errs.append(f"long-form H2 without id: {text[:40]}")
    return errs


def pages():
    return sorted(f for f in glob.glob("*.html") + glob.glob("case-studies/*.html") + glob.glob("blog/*.html") + glob.glob("services/*.html") + glob.glob("for/*.html"))


def main():
    total = 0
    for f in pages():
        e = check(f)
        total += len(e)
        print(("✔ " if not e else "✘ ") + f)
        for x in e:
            print("    - " + x)
    # sitemap: no orphan pages
    sm = open("sitemap.xml").read()
    for f in pages():
        if url_for(f) not in sm:
            print(f"✘ sitemap missing {f}"); total += 1
    print(f"\n{total} problem(s)")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
