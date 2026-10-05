#!/usr/bin/env python3
"""Normalise <head> SEO, site-wide schema and image dimensions on every page.

Usage:  python3 tools/seo.py      (also run automatically by tools/build_case_studies.py)

- Titles / descriptions for static pages come from PAGES below; case study pages keep
  the title/description written by tools/build_case_studies.py.
- Writes canonical, Open Graph, Twitter, lang="en-US", Organization + WebSite schema,
  BreadcrumbList (non-home) and Service schema (services hub).
- Adds width/height to every <img> from the image file itself.
See content-guide/on-page-seo.md.
"""
import glob, html, json, os, re, struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE_URL = "https://www.example.com"   # TODO: the live domain, no trailing slash
BRAND = "Renovo Studio"
SUFFIX = " | " + BRAND
OG_DEFAULT = "assets/img/og-default.png"
SAME_AS = ["https://www.linkedin.com/in/matthew-rissik/", "https://x.com/matthewrissik",
           "https://www.youtube.com/@MatthewRissik", "https://www.instagram.com/matthewrissik"]

# file: (title, meta description, primary keyword, breadcrumb name or None for home)
PAGES = {
    "index.html": ("Web Design, SEO & Outbound Lead Generation" + SUFFIX,
                   "Renovo Studio builds pipeline for B2B and service businesses: websites that convert, SEO that gets you found and outbound that books meetings.",
                   "web design seo and outbound lead generation", None),
    "services.html": ("Web Design, SEO & GTM Outbound Services" + SUFFIX,
                      "Web design, SEO and local SEO, GTM and outbound lead generation, or all of it as one Full Growth System. Book 15 minutes to see what we'd fix first.",
                      "web design, seo and gtm outbound services", "Services"),
    "work.html": ("Web Design & Lead Generation Case Studies" + SUFFIX,
                  "Lead generation, web design and SEO case studies for B2B and service businesses, plus live cold email campaign dashboards. $7.2M generated for clients.",
                  "web design and lead generation case studies", "Work"),
    "blog.html": ("Web Design, SEO & Cold Email Advice Blog" + SUFFIX,
                  "Plain-English advice on web design, SEO, local search and cold email for B2B and service businesses. One thing you can fix this week in every post.",
                  "web design and seo blog", "Blog"),
    "contact.html": ("Book a 15-Minute Pipeline Strategy Call" + SUFFIX,
                     "Book a free 15-minute call about web design, SEO or outbound. We'll look at how you win business today and tell you what we'd fix first, and the cost.",
                     "book a pipeline strategy call", "Contact"),
}

SERVICES = [
    ("Web Design", "web-design", "Fixed-scope websites, written and built to turn visitors into booked calls."),
    ("SEO & Local SEO", "seo", "Buyer-intent SEO, Google Business Profile and map pack work, with technical audits included."),
    ("GTM & Outbound", "gtm-outbound", "Done-for-you cold email and LinkedIn campaigns that book meetings with qualified buyers."),
    ("Full Growth System", "full-growth-system", "Website, SEO, outbound and CRM follow-up, run as one system."),
]


def url_for(path):
    path = path.replace(os.sep, "/")
    return SITE_URL if path == "index.html" else f"{SITE_URL}/{path}"


def org():
    return {"@context": "https://schema.org", "@type": "Organization", "@id": f"{SITE_URL}/#organization",
            "name": BRAND, "url": SITE_URL, "logo": f"{SITE_URL}/assets/img/renovo-logo.png",
            "description": "Web design, SEO and outbound lead generation for B2B and service businesses.",
            "founder": {"@type": "Person", "name": "Matthew Rissik", "jobTitle": "Founder", "sameAs": SAME_AS[:3]},
            "sameAs": SAME_AS,
            "knowsAbout": ["Web design", "Search engine optimization", "Local SEO", "Cold email outreach", "LinkedIn outreach", "Lead generation"]}


def website():
    return {"@context": "https://schema.org", "@type": "WebSite", "@id": f"{SITE_URL}/#website", "name": BRAND,
            "url": SITE_URL, "publisher": {"@id": f"{SITE_URL}/#organization"}, "inLanguage": "en-US"}


def breadcrumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": u} for i, (n, u) in enumerate(items, 1)]}


def services_schema():
    return [{"@context": "https://schema.org", "@type": "Service", "name": n, "description": d, "serviceType": n,
             "url": f"{SITE_URL}/services.html#{slug}", "provider": {"@id": f"{SITE_URL}/#organization"}}
            for n, slug, d in SERVICES]


# ------------------------------------------------------------------------- image sizes
def image_size(path):
    try:
        if path.endswith(".svg"):
            m = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', open(path).read())
            return (round(float(m.group(1))), round(float(m.group(2)))) if m else None
        with open(path, "rb") as f:
            head = f.read(64 * 1024)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", head[16:24])
        if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
            fmt = head[12:16]
            if fmt == b"VP8X":
                return (int.from_bytes(head[24:27], "little") + 1, int.from_bytes(head[27:30], "little") + 1)
            if fmt == b"VP8L":
                b = int.from_bytes(head[21:25], "little")
                return ((b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1)
            if fmt == b"VP8 ":
                return (struct.unpack("<H", head[26:28])[0] & 0x3FFF, struct.unpack("<H", head[28:30])[0] & 0x3FFF)
        if head[:2] == b"\xff\xd8":
            i = 2
            while i < len(head):
                if head[i] != 0xFF:
                    break
                mk, ln = head[i + 1], struct.unpack(">H", head[i + 2:i + 4])[0]
                if mk in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", head[i + 5:i + 9])
                    return (w, h)
                i += 2 + ln
    except (OSError, struct.error, AttributeError):
        pass
    return None


def size_images(doc, page_dir):
    def sub(m):
        tag = m.group(0)
        src = re.search(r'\ssrc="([^"]+)"', tag)
        if not src or src.group(1).startswith(("http", "data:")):
            return tag
        dims = image_size(os.path.normpath(os.path.join(page_dir, src.group(1))))
        if not dims:
            return tag
        tag = re.sub(r'\s(width|height)="[^"]*"', "", tag)
        return tag[:4] + f' width="{dims[0]}" height="{dims[1]}"' + tag[4:]
    return re.sub(r"<img\b[^>]*>", sub, doc)


# ------------------------------------------------------------------------- head
STRIP = [r'\s*<link rel="canonical"[^>]*>', r'\s*<meta property="og:[a-z_:]+"[^>]*>', r'\s*<meta name="twitter:[a-z]+"[^>]*>',
         r'\s*<meta name="description"[^>]*>', r"\s*<title>.*?</title>", r"\s*<!-- seo:head -->.*?<!-- /seo:head -->"]


def apply_page(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    doc = open(path).read()
    is_case = rel.startswith("case-studies/")
    if rel in PAGES:
        title, desc, _kw, crumb = PAGES[rel]
    else:
        title = html.unescape(re.search(r"<title>(.*?)</title>", doc, re.S).group(1))
        desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', doc).group(1))
        crumb = html.unescape(re.search(r'<nav class="crumbs[^"]*"[^>]*>.*?<b>(.*?)</b>', doc, re.S).group(1))
    og_img = OG_DEFAULT
    m = re.search(r'<meta property="og:image" content="([^"]+)"', doc)
    if is_case and m:
        og_img = m.group(1).replace(SITE_URL + "/", "")
    for pat in STRIP:
        doc = re.sub(pat, "", doc, flags=re.S)

    # schema: drop old site-wide/breadcrumb blocks (case studies keep their own Article + BreadcrumbList)
    def keep(m):
        try:
            t = json.loads(m.group(1)).get("@type")
        except json.JSONDecodeError:
            return m.group(0)
        if t in ("Organization", "WebSite", "ProfessionalService", "LocalBusiness", "Service") or (t == "BreadcrumbList" and not is_case):
            return ""
        return m.group(0)
    doc = re.sub(r'\s*<script type="application/ld\+json">(.*?)</script>', keep, doc, flags=re.S)

    ld = [org(), website()]
    if crumb and not is_case:
        ld.append(breadcrumbs([("Home", url_for("index.html")), (crumb, url_for(rel))]))
    if rel == "services.html":
        ld += services_schema()
    e = lambda s: html.escape(s, quote=True)
    block = f"""<!-- seo:head -->
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{url_for(rel)}">
  <meta property="og:type" content="{'article' if is_case else 'website'}">
  <meta property="og:site_name" content="{BRAND}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{url_for(rel)}">
  <meta property="og:image" content="{SITE_URL}/{og_img}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@matthewrissik">
  {"".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)}
  <!-- /seo:head -->"""
    doc = doc.replace('<meta name="viewport" content="width=device-width, initial-scale=1">',
                      '<meta name="viewport" content="width=device-width, initial-scale=1">\n  ' + block, 1)
    doc = re.sub(r'<html lang="[^"]*">', '<html lang="en-US">', doc, count=1)
    doc = size_images(doc, os.path.dirname(path))
    open(path, "w").write(doc)


def make_og_default():
    path = os.path.join(ROOT, OG_DEFAULT)
    if os.path.exists(path):
        return
    try:
        from PIL import Image
    except ImportError:
        return
    im = Image.new("RGB", (1200, 630), (236, 235, 230))
    logo = Image.open(os.path.join(ROOT, "assets/img/renovo-logo.png")).convert("RGBA")
    logo.thumbnail((720, 260))
    im.paste(logo, ((1200 - logo.width) // 2, (630 - logo.height) // 2), logo)
    im.save(path, optimize=True)


def apply_all():
    make_og_default()
    files = sorted(glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(os.path.join(ROOT, "case-studies/*.html"))
                   + glob.glob(os.path.join(ROOT, "blog/*.html")) + glob.glob(os.path.join(ROOT, "services/*.html")))
    for f in files:
        apply_page(f)
    return len(files)


if __name__ == "__main__":
    print(f"seo applied to {apply_all()} pages")
