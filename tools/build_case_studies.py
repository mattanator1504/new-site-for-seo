#!/usr/bin/env python3
"""Build case study pages and project cards from _source/case-studies.json.

Usage:  python3 tools/build_case_studies.py

Generates:
  case-studies/<slug>.html        one page per case study (16)
  work.html                       project grid + campaign results   (between build markers)
  index.html                      homepage website + lead gen cards  (between build markers)
  sitemap.xml                     page list

Facts come only from the JSON. This file holds the site-specific layer: rewritten
titles/meta/keywords, lightly reworded `short`/`situation` copy in the agency "we"
voice, image/logo mapping and service filters. `internalSourceNote` is never output.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SITE_URL = "https://www.example.com"   # TODO: set the live domain (also in sitemap/robots)
TODAY = "2026-10-05"
BRAND = "Renovo Studio"
IMG = "assets/img/work"
ARROW = '<svg class="arrow" width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M2 8h12M9 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'

DATA = json.load(open("_source/case-studies.json"))
CASES = DATA["caseStudies"]
CARDS = DATA["projectCards"]
CAMPAIGNS = DATA["campaigns"]

# ---------------------------------------------------------------------------------------------
# Site-specific SEO: rewritten so nothing duplicates matthewrissik.com. Keywords are unique to
# this site; see content-guide/keyword-log.md.
SEO = {
    "b2b-saas-growth-system": ("SaaS Outbound Case Study: $2M to $7.2M ARR", "saas outbound lead generation",
        "How a cyber security SaaS company grew from about $2M to $7.2M ARR in 9 months with one niche, a rebuilt funnel and 142 enterprise demos booked."),
    "medspa-dr": ("Cold Email for Med Spa Software: 51 Calls, $250K", "med spa software cold email",
        "Cold email to med spa owners in Texas, Arizona and California: 51 qualified calls and $250K in pipeline in 60 days for the MedSpa DR CRM."),
    "all-med-search": ("Medical Staffing Lead Generation: 65 Meetings", "medical staffing lead generation",
        "Two cold email campaigns for a medical staffing firm, one to Canadian nurses and one to US facilities, booked 65 meetings from 60,000 emails."),
    "cj-stafford-construction": ("Construction Company Outbound: 25 Leads in 6 Weeks", "construction company outbound",
        "A 6-week outbound campaign plus a rebuilt website added 25 new leads to CJ Stafford Construction's pipeline in Phase 1."),
    "gabes-window-cleaning": ("Commercial Window Cleaning Leads: ~20 in 6 Weeks", "commercial window cleaning leads",
        "Outbound to Tucson property and facility managers brought Gabe's Window Cleaning about 20 quote-ready commercial leads in 6 weeks."),
    "monroy-sf-cleaning": ("Commercial Cleaning Leads: 20 Quote-Ready in 8 Weeks", "commercial cleaning leads",
        "50,000+ targeted emails plus SMS, LinkedIn and calls delivered 20 quote-ready leads to a San Francisco cleaning company in 8 weeks, without paid ads."),
    "pinnacle-real-estate": ("LA County Real Estate Leads: 30+ Vetted in 2 Months", "la county real estate leads",
        "A targeted campaign across LA County delivered 30+ vetted buyer and seller leads to Pinnacle Real Estate Group in 2 months, several of which closed."),
    "mike-k-realtor": ("Real Estate Agent Website and Outbound: ~60 Leads", "real estate agent website",
        "A brand-forward website and outbound for a new real estate agent produced about 60 hot leads and multiple closed deals."),
    "silver-solutions": ("Logistics Company Website Design: Silver Solutions", "logistics company website design",
        "A logistics website rebuilt to lead with capabilities, make services easy to find, add SEO foundations and simplify quote requests."),
    "fractional-ceo": ("Website and SEO for a Fractional CEO Firm", "fractional ceo website",
        "A launch website, niche keyword research, a content plan and analytics from day one for a new fractional executive firm."),
    "tengy": ("Event Food Ordering App UX Design: Tengy", "event food ordering app",
        "UX/UI for Tengy: order food and drinks from your seat at concerts and festivals, pay cashless, and give vendors a real-time order dashboard."),
    "kago-yama": ("Smallholder Farming App UX Design: Kago Yama", "smallholder farming app",
        "A ~25-screen Figma prototype for Limpopo smallholder farmers to manage plots, flag crop problems and sell produce, later used by a real farm."),
    "megalit-utility-app": ("Water Meter and Bill Payment App UX: MegaLit", "water meter app design",
        "UX/UI for MegaLit: real-time water meter readings, in-app bill payment and usage analytics for Johannesburg residents of every tech level."),
    "hlomo": ("Community SOS App Concept UX Design: Hlomo", "sos app design",
        "Hlomo, a one-tap SOS concept for South Africa that alerts trusted neighbors and responders together, designed to stay simple under stress."),
    "dress-me-up": ("AI Outfit and Tailor Chat App UX: Dress Me Up", "outfit app ux case study",
        "A 16-week fashion app prototype with a 60-second style quiz and in-app tailor chat, shaped by 100 survey responses and 8 interviews."),
    "syncd": ("Creative Community Platform UX Design: Sync'd", "creative community platform",
        "Sync'd, a web-first hub where South Africa's emerging artists, writers and podcasters could read, listen and connect."),
}

# Lightly reworded `short` and `situation` (same facts), in this site's agency voice.
COPY = {
    "b2b-saas-growth-system": dict(
        short="This B2B cyber security SaaS company had a strong product, an empty pipeline and revenue stuck at around $2M a year. We narrowed the focus to one niche, rebuilt the buyer funnel, rewrote the cold email positioning and automated demo booking. Nine months on: $7.2M in annual recurring revenue and 142 enterprise demos booked.",
        situation=["The company sold custom cyber security software to anyone who could cover the minimum yearly commitment, across healthcare, finance, manufacturing and telecom. Which meant going up against more than 30,000 competitors.",
                   "Then the sales team was let go, the pipeline was close to empty and revenue dropped to roughly $2M a year. Agencies and consultants had already been tried. The outbound copy was generic and landed in spam, and the website didn’t tell security buyers why this product was different."]),
    "medspa-dr": dict(
        short="MedSpa DR makes an all-in-one CRM for medical spas, covering scheduling, client records, marketing automation and reporting. The goal was more med spa owners on sales calls in Texas, Arizona and California. A targeted cold email campaign delivered 51 qualified calls and $250,000 in pipeline in 60 days.",
        situation=["MedSpa DR isn’t a med spa. It’s the software med spas run on, built by a team with over 20 years in the industry. The product was strong. The hard part was getting in front of busy owners who never go looking for new software.",
                   "The brief was simple: qualified conversations with med spa decision-makers in three states, and a pipeline that looked like real money."]),
    "all-med-search": dict(
        short="All Med Search places healthcare professionals in US hospitals, and needed more candidates and more facility clients without leaning on ads or job boards. We ran two cold email campaigns: one to Canadian nurses open to moving, one to US healthcare decision-makers. Between them they booked 65 meetings.",
        situation=["Recruiting is two sales problems at once: you need people to place, and you need places that want them. All Med Search wanted both, experienced nurses in Canada willing to relocate to the US and US healthcare facilities that needed staff.",
                   "And they wanted to get there through outbound, not by paying for more job board listings or advertising."]),
    "cj-stafford-construction": dict(
        short="CJ Stafford Construction ran on word of mouth and wanted a pipeline it could predict. We ran a focused 6-week outbound campaign aimed at decision-makers who need construction work, and rebuilt the website to back up every email. Phase 1 added 25 new leads.",
        situation=["Referrals are lovely until they stop. CJ Stafford needed new project leads that didn’t depend on who happened to mention them that month.",
                   "There was a second problem. Outbound sends people to your website, and the old one didn’t show the company’s work or credibility well enough to back up a cold email."]),
    "gabes-window-cleaning": dict(
        short="Gabe’s Window Cleaning in Tucson wanted steady commercial contracts, not sporadic one-off jobs. We built a tight list of property and facility managers, wrote short benefit-led emails that asked one question, “Want a quick quote?”, and followed up by SMS and LinkedIn. Six weeks in: about 20 quote-ready leads.",
        situation=["Sporadic bookings cost a cleaning crew money. Routes don’t line up, teams sit idle and planning next month is guesswork. Gabe wanted commercial clients on regular schedules: office blocks, retail centers and property managers.",
                   "Quality mattered more than volume. He wanted people ready to ask for a quote, not tire-kickers, and he didn’t want to burn money on broad advertising to find them."]),
    "monroy-sf-cleaning": dict(
        short="Monroy SF Cleaning, a commercial and residential cleaner in San Francisco, relied on referrals and organic search. Both worked, just slowly. We ran an outbound program built on cold email, with SMS, LinkedIn and warm calls on top. In 8 weeks it delivered 20 quote-ready leads, without paid ads.",
        situation=["Referrals and search were bringing in work, but not fast enough and not predictably. Monroy wanted two kinds of client: property managers and facility directors at offices, retail spaces and multi-tenant buildings, and higher-value homeowners.",
                   "They wanted results in weeks rather than the months SEO takes, and without the ongoing cost of paid advertising."]),
    "pinnacle-real-estate": dict(
        short="Pinnacle Real Estate Group works with buyers and sellers across Los Angeles County, and wanted a pipeline that didn’t rely only on referrals and ads. We ran a targeted campaign across key LA County neighborhoods and vetted every lead before handoff. In two months: 30+ hot leads, several of which closed.",
        situation=["Real estate teams live and die by their pipeline. Pinnacle had referrals and some advertising, but wanted a source they could scale and count on month after month.",
                   "Volume for its own sake wasn’t the goal. Agents’ time is the expensive part, so every lead had to be worth a call."]),
    "mike-k-realtor": dict(
        short="Mike K left pharmacy to sell real estate: a new agent with no track record, in a competitive market. We built a brand-forward website that turned his background into a reason to trust him, and ran outbound to buyers and sellers in his area. The result was about 60 hot leads and multiple closed deals.",
        situation=["New agents have a chicken-and-egg problem. You need deals to look credible, and you need to look credible to get deals.",
                   "Mike needed three things at once: a steady flow of qualified buyer and seller leads, credibility without a long track record, and a professional site that reflected his brand."]),
    "silver-solutions": dict(
        short="Silver Solutions is a logistics company covering warehousing, road transport and project management, with 35 years of combined expertise, and its old website showed none of it. We redesigned it to lead with impact, made the services easy to find, added SEO foundations and gave visitors a simple way to request a quote.",
        situation=["Decades of experience and a wide range of specialist services, undersold by the website. Visitors couldn’t quickly tell what Silver Solutions did, who it did it for or why it was better than the next logistics company."]),
    "fractional-ceo": dict(
        short="Fractional CEO offers executive expertise on demand. It was a new business with no website, in a competitive market. We built the site from scratch to explain the offer clearly and look the part, set up an SEO and content plan for the fractional executive niche, and put analytics in from day one.",
        situation=["New consulting firms have a credibility gap. Buyers are hiring senior judgement, so the website has to feel senior before anyone books a call.",
                   "Fractional CEO needed a site that explained a fairly new idea in plain language, and a way to be found by the people searching for it."]),
    "tengy": dict(
        short="Tengy set out to fix the worst part of big events: the food and drink queue. We designed an app that lets attendees order from their seats and pay cashless, plus a real-time dashboard for vendors to manage orders. Along the way, the role grew into product design and strategy.",
        situation=["At concerts and festivals, food and drink queues eat into the event people paid for, and vendors lose sales to everyone who gives up waiting.",
                   "The challenge: a smooth ordering flow for attendees and a dashboard vendors could run in a loud, busy, chaotic environment, without ignoring the technical and business constraints."]),
    "kago-yama": dict(
        short="Kago Yama is a farming app concept for smallholder farmers around Limpopo: manage plots, spot crop problems early and sell directly to buyers. We designed about 25 screens in Figma, from onboarding to a mini marketplace. It stayed a prototype until a real farm adopted the wireframes in 2025.",
        situation=["Smallholder farmers in Limpopo deal with unpredictable crop health and no easy way to spot pests early, operations tracked on paper, and buyers who are often hours away with no way to book digitally."]),
    "megalit-utility-app": dict(
        short="MegaLit was a utility app for Johannesburg residents tired of inaccurate water meter readings and painful bill payments. Leading the UX/UI design, we designed real-time meter readings, simple in-app payments and usage analytics that work for people with any level of tech confidence. It didn’t reach full launch.",
        situation=["Residents dealt with inaccurate, delayed water meter readings that led to billing disputes, and a payment process clunky enough to put people off paying on time.",
                   "Any fix also had to work for people with limited tech experience, not just confident app users."]),
    "hlomo": dict(
        short="Hlomo was a concept for rethinking emergency response in South Africa through trusted community networks. Our founder co-founded it over seven months at Sammi Studio, handling strategy, UX/UI design and front-end development. The idea: one tap alerts neighbors and professional responders at the same time, through a calm, simple interface.",
        situation=["Calling for help shouldn’t need a manual, and the existing call center system is hard to navigate in a high-stress moment.",
                   "Vulnerable groups, including older people, refugees and people with disabilities, often struggle with jargon or poor network coverage. And people need to trust that an SOS will actually reach someone, fast."]),
    "dress-me-up": dict(
        short="Dress Me Up began as a 16-week project during our founder’s business degree: a fashion app that suggests outfits to fit your style and lets you chat directly with tailors to adjust them. The team researched with real shoppers and tailors, then built a prototype that made a simulated AI feel personal. It never launched.",
        situation=["Shopping for clothes online means endless scrolling, decision fatigue and settling for “good enough.” Broad filters and “if you like X” suggestions weren’t cutting it, and nobody offered tailored advice plus an easy route to custom fittings.",
                   "There were 16 weeks, no real AI backend, and two very different users to design for: shoppers who want inspiration, and tailors who want clear custom orders."]),
    "syncd": dict(
        short="Sync'd was a passion project: a digital hub where South Africa’s emerging artists, writers and podcasters could show their work and meet each other. Our founder co-founded it and, as product lead, shaped everything from the editorial direction to the UX. When the app idea proved too heavy, the team moved to a web-first platform built on three pillars: Read, Listen, Connect.",
        situation=["Talent wasn’t in short supply. Attention was. Established names dominated galleries, airtime and search results, and new voices struggled to find an audience or collaborators."]),
}

# First-person phrases in the remaining exported copy, adapted to "we". Meaning unchanged.
PRONOUNS = [
    ("that’s the first thing I’d look at", "that’s the first thing we’d look at"),
    ("The lesson I keep coming back to", "The lesson we keep coming back to"),
    ("I used the pyramid principle", "We used the pyramid principle"),
    ("so I won’t invent any here", "so we won’t invent any here"),
    ("so I’ve left them out", "so we’ve left them out"),
    ("and I’m upfront about that", "and we’re upfront about that"),
]

# ---------------------------------------------------------------------------------------------
# Visuals. Extracted logos (on paper) keep the site's monochrome look; otherwise the exported
# card image is used (black and white, colour on hover). Screenshots enable hover-scroll.
LOGOS = {"mike-k-realtor": "mike-k-realtor", "cj-stafford-construction": "cj-stafford", "karpel-associates": "karpel-associates",
         "lloyds-global-logistics": "lloyds-global-logistics", "gabes-window-cleaning": "gabes-spotless", "pinnacle-real-estate": "pinnacle-real-estate",
         "monroy-sf-cleaning": "monroy-sf-cleaning", "medspa-dr": "med-spa-dr", "all-med-search": "all-med-search", "arvio-capital": "arvio-capital",
         "polish-and-prose": "polish-and-prose", "level-up-digital": "level-up-digital", "midnight-owl-group": "midnight-owl", "syncd": "syncd"}
DARK_LOGO = {"gabes-window-cleaning"}
WORDS = {"fractional-ceo": ("Fractional<br>/CEO", "Expertise on tap"), "silver-solutions": ("Silver Solutions", "Making the world a global village"),
         "ramjee-aesthetics": ("Ramjee<br>Aesthetics", "Cape Town, South Africa")}
SHOTS = {"mike-k-realtor": "mike-k-realtor", "cj-stafford-construction": "cj-stafford", "fractional-ceo": "fractional-ceo",
         "silver-solutions": "silver-solutions", "karpel-associates": "karpel-associates", "lloyds-global-logistics": "lloyds-global-logistics"}

# Projects supplied directly by the owner (full-page screenshots), not in the export.
EXTRAS = [
    dict(slug="fit-for-life", client="Fit For Life", category="Web Design & SEO", tags=["Personal training"], summary="", shot="fit-for-life"),
    dict(slug="wheels-to-wellness", client="Wheels to Wellness", category="Web Design & SEO", tags=["Massage therapy"], summary="", shot="wheels-to-wellness"),
    dict(slug="surface-solutions", client="Surface Solutions", category="Web Design & SEO", tags=["Surface restoration"], summary="", shot="surface-solutions"),
]

CAT_FILTER = {"Lead Generation": ["gtm-outbound"], "Web Design & SEO": ["web-design", "seo"], "UX/UI & Product Design": ["ux-ui"]}
SERVICE_FILTER = {"web-design": "web-design", "seo": "seo", "outbound-lead-generation": "gtm-outbound", "full-growth-system": "full-growth-system"}
SERVICE_PAGE = {"web-design": ("Web Design", "services.html#web-design"), "seo": ("SEO &amp; Local SEO", "services.html#seo"),
                "outbound-lead-generation": ("GTM &amp; Outbound", "services.html#gtm-outbound"),
                "full-growth-system": ("Full Growth System", "services.html#full-growth-system")}
FILTERS = [("all", "All"), ("web-design", "Web Design"), ("seo", "SEO &amp; Local SEO"), ("gtm-outbound", "Lead Generation"),
           ("full-growth-system", "Full Growth System"), ("ux-ui", "UX/UI")]


def esc(s):
    return html.escape(s, quote=True)


def fix(s):
    for a, b in PRONOUNS:
        s = s.replace(a, b)
    return s


def domain(u):
    return re.sub(r"^https?://(www\.)?", "", u).rstrip("/")


def img(path):
    """Export image path (images/...) -> site path."""
    return path.replace("images/projects/", f"{IMG}/projects/").replace("images/campaigns/", f"{IMG}/campaigns/")


def cats(p):
    out = list(CAT_FILTER.get(p["category"], []))
    for s in p.get("services", []):
        if SERVICE_FILTER.get(s) and SERVICE_FILTER[s] not in out:
            out.append(SERVICE_FILTER[s])
    return " ".join(out)


def tagline(p):
    cat = "" if p["category"] == "Recent work" else p["category"]
    first = p["tags"][0] if p.get("tags") else ""
    return esc(" · ".join(x for x in (cat, first) if x))


# ---------------------------------------------------------------------------------------------
def card(p, extra="", prefix=""):
    slug = p["slug"]
    page = f"{prefix}case-studies/{slug}.html" if p.get("hasPage") else None
    shot = p.get("shot") or SHOTS.get(slug)
    has_img = slug not in LOGOS and slug not in WORDS and p.get("images")
    cls = "proj" + (" has-screen" if shot else "") + (" has-img" if has_img else "") + (" " + extra if extra else "")
    name = esc(p["client"])
    if slug in LOGOS:
        inner = f'<img src="{prefix}{IMG}/logos/{LOGOS[slug]}.png" alt="{name} logo" loading="lazy">'
    elif slug in WORDS:
        inner = f'<span class="proj__word">{WORDS[slug][0]}<small>{WORDS[slug][1]}</small></span>'
    elif p.get("images"):
        inner = f'<img class="cover-img" src="{prefix}{img(p["images"]["card"])}" alt="{esc(p["imageAlt"])}" loading="lazy">'
    else:
        inner = None
    cover = ""
    if inner:
        dark = slug in DARK_LOGO
        dots = "" if has_img else f'<div class="dots{"" if dark else " dots--ink"}" aria-hidden="true"></div>'
        cover = f'\n              <div class="proj__cover{" proj__cover--dark" if dark else ""}">{dots}{inner}</div>'
    screen, attrs, tag = "", "", "div"
    if shot:
        site = p.get("website")
        screen = f'''
              <div class="proj__screen" aria-hidden="true">
                <div class="proj__bar"><i></i><i></i><i></i><span>{esc(domain(site)) if site else name}</span></div>
                <div class="proj__view"><img src="{prefix}{IMG}/source/shot-{shot}.jpg" alt="" loading="lazy"></div>
              </div>'''
        attrs = f' tabindex="0" role="button" aria-label="Preview the {name} website" data-cursor="Scroll"'
    elif page:
        tag, attrs = "a", f' href="{page}" data-cursor="Read" aria-label="{name} case study"'
    hint = ""
    if shot and cover:
        hint = '<span class="proj__hint" aria-hidden="true">Hover to scroll</span>'
    elif page and not shot:
        hint = '<span class="proj__hint" aria-hidden="true">Read case study</span>'
    title = f'<a href="{page}">{name}</a>' if page else name
    if page:
        right = f'<a class="chip visit" href="{page}">Case study →</a>'
    elif p.get("website"):
        right = f'<a class="chip visit" href="{esc(p["website"])}" target="_blank" rel="noopener">Visit site ↗</a>'
    else:
        right = f'<span class="label">{esc(p["category"] if p["category"] != "Recent work" else "Recent work")}</span>'
    summary = f'\n            <p>{esc(fix(p["summary"]))}</p>' if p.get("summary") else ""
    return f'''
          <article class="{cls}" data-cat="{cats(p)}">
            <{tag} class="proj__frame"{attrs}>{screen}{cover}
              <span class="proj__tag">{tagline(p)}</span>{hint}
            </{tag}>
            <div class="meta"><h3>{title}</h3>{right}</div>{summary}
          </article>'''


def campaign_card(c, prefix=""):
    full = img(c["images"]["full"])
    thumb = img(c["images"]["thumb"])
    have_full, have_thumb = os.path.exists(full), os.path.exists(thumb)
    shown = full if have_full else thumb if have_thumb else None
    link = full if have_full else shown
    shot = (f'<a class="camp__shot" href="{prefix}{link}" target="_blank" rel="noopener" data-cursor="Zoom">'
            f'<img src="{prefix}{shown}" alt="Cold email dashboard screenshot: {esc(c["title"])}" loading="lazy"></a>') if shown else ""
    if c.get("isTable"):
        body = f'<p class="camp__note">{esc(c["note"])}</p>'
    else:
        rows = [("Sent", c["sent"]), ("Replies", c["replies"]), ("Reply rate", c["replyRate"]),
                ("Positive replies", c["positive"]), ("Positive reply rate", c["positiveRate"])]
        key = ' class="is-key"'
        body = '<dl class="camp__nums">' + "".join(f'<div{key if k == "Positive reply rate" else ""}><dt>{k}</dt><dd>{esc(v)}</dd></div>' for k, v in rows) + "</dl>"
    return f'''
          <article class="camp reveal">
            <h3>{esc(c["title"])}</h3>
            {body}
            {shot}
          </article>'''


# ---------------------------------------------------------------------------------------------
def rel(markup, prefix):
    def sub(m):
        attr, q, url = m.group(1), m.group(2), m.group(3)
        if re.match(r"^(https?:|mailto:|tel:|#|data:|/)", url) or url.startswith(prefix + "assets/"):
            return m.group(0)
        return f"{attr}={q}{prefix}{url}"
    return re.sub(r'\b(href|src)=(["\'])([^"\']*)', sub, markup)


WORK = open("work.html").read()
HEADER = WORK[WORK.index("<body>"):WORK.index('<main id="main">')]
FOOTER = WORK[WORK.index("</main>") + len("</main>"):]


def head(title, desc, ld, prefix, og_image):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="robots" content="index, follow">
  <meta name="theme-color" content="#0b0b0b">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="{BRAND}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:image" content="{SITE_URL}/{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@matthewrissik">
  <link rel="icon" href="{prefix}assets/img/favicon-32.png" type="image/png" sizes="32x32">
  <link rel="icon" href="{prefix}assets/img/renovo-icon.png" type="image/png" sizes="512x512">
  <link rel="apple-touch-icon" href="{prefix}assets/img/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Condensed:wght@500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefix}assets/css/style.css">
  {"".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)}
</head>
"""


def case_page(i, c):
    slug, P = c["slug"], "../"
    title, kw, desc = SEO[slug]
    full_title = f"{title} | {BRAND}"
    url = f"{SITE_URL}/case-studies/{slug}.html"
    copy = COPY[slug]
    ld = [
        {"@context": "https://schema.org", "@type": "Article", "headline": c["h1"], "description": desc,
         "image": f"{SITE_URL}/{img(c['images']['full'])}", "datePublished": TODAY, "dateModified": TODAY,
         "keywords": kw, "about": c["client"], "mainEntityOfPage": url,
         "author": {"@type": "Organization", "name": BRAND},
         "publisher": {"@type": "Organization", "name": BRAND, "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/assets/img/renovo-logo.png"}}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Work", "item": f"{SITE_URL}/work.html"},
            {"@type": "ListItem", "position": 3, "name": c["client"], "item": url}]},
    ]
    facts = [("Client", esc(c["client"])), ("Category", esc(c["category"]))]
    if c.get("year"):
        facts.append(("Timeframe", esc(c["year"])))
    facts.append(("Role", esc(c["role"])))
    if c.get("website"):
        facts.append(("Website", f'<a class="link-u" href="{esc(c["website"])}" target="_blank" rel="noopener">{esc(domain(c["website"]))} ↗</a>'))
    facts_html = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in facts)
    stats = ""
    if c.get("stats"):
        stats = f'''
        <div class="stats cs-stats cs-stats--{len(c["stats"])}" data-stagger>''' + "".join(
            f'\n          <div class="stat reveal"><div class="n">{esc(s["value"])}</div><div class="l">{esc(s["label"])}</div></div>' for s in c["stats"]) + "\n        </div>"
    built = "".join(f'\n          <li class="reveal"><span class="n">{k:02d}</span><b>{esc(fix(b["title"]))}</b><span>{esc(fix(b["body"]))}</span></li>'
                    for k, b in enumerate(c["built"], 1))
    services = "".join(f'<a class="chip" href="{P}{SERVICE_PAGE[s][1]}">{SERVICE_PAGE[s][0]}</a>' for s in c.get("services", []) if s in SERVICE_PAGE)
    services_html = f'\n        <p class="svc-proof reveal"><span class="label">Services</span>{services}</p>' if services else ""
    nxt = CASES[(i + 1) % len(CASES)]
    body = f'''
  <main id="main">
    <article class="cs">
      <header class="cs-hero">
        <div class="container">
          <nav class="crumbs reveal" aria-label="Breadcrumb"><a href="{P}index.html">Home</a><span>/</span><a href="{P}work.html">Work</a><span>/</span><b>{esc(c["client"])}</b></nav>
          <span class="eyebrow reveal">{esc(c["category"])} · {esc(", ".join(c["tags"]))}</span>
          <h1 class="display cs-title" data-split>{esc(c["h1"])}</h1>
          <p class="lead reveal cs-short">{esc(copy["short"])}</p>
          <dl class="cs-facts reveal">{facts_html}</dl>{stats}
        </div>
      </header>

      <figure class="cs-image container clip-reveal">
        <img src="{P}{img(c["images"]["full"])}" alt="{esc(c["imageAlt"])}" width="1440" height="1080">
      </figure>

      <div class="container cs-body">
        <section class="cs-block" aria-labelledby="cs-situation">
          <span class="eyebrow reveal">01</span>
          <h2 class="display h-md" id="cs-situation" data-split>The situation</h2>
          <div class="prose reveal">{"".join(f"<p>{esc(x)}</p>" for x in copy["situation"])}</div>
        </section>

        <section class="cs-block" aria-labelledby="cs-built">
          <span class="eyebrow reveal">02</span>
          <h2 class="display h-md" id="cs-built" data-split>What we built</h2>
          <ol class="gtm-steps cs-built" data-stagger>{built}
          </ol>
        </section>

        <section class="cs-block" aria-labelledby="cs-happened">
          <span class="eyebrow reveal">03</span>
          <h2 class="display h-md" id="cs-happened" data-split>What happened</h2>
          <div class="prose reveal">{"".join(f"<p>{esc(fix(x))}</p>" for x in c["happened"])}</div>
        </section>

        <blockquote class="cs-quote reveal"><p>{esc(fix(c["differently"]))}</p><cite>What we’d tell you</cite></blockquote>{services_html}

        <nav class="cs-next reveal" aria-label="More case studies">
          <a class="btn btn--ghost" href="{P}work.html">All work {ARROW}</a>
          <a class="cs-next__link" href="{nxt["slug"]}.html"><span class="label">Next case study</span><b>{esc(nxt["client"])}</b></a>
        </nav>
      </div>
    </article>
'''
    cta = WORK[WORK.index('    <section class="cta"'):WORK.index("</section>", WORK.index('    <section class="cta"')) + len("</section>")]
    page = head(full_title, desc, ld, P, img(c["images"]["full"])) + rel(HEADER, P) + rel(body, P).replace(f'href="{P}{nxt["slug"]}.html"', f'href="{nxt["slug"]}.html"') + "\n" + rel(cta, P) + "\n  </main>" + rel(FOOTER, P)
    for bad in (c.get("internalSourceNote", "#none#"), "matthewrissik.com/case", "Matthew Rissik</title>"):
        assert bad not in page, (slug, bad)
    return page


def replace_block(doc, name, content, fallback):
    start, end = f"<!-- build:{name} -->", f"<!-- /build:{name} -->"
    block = f"{start}{content}\n{end}"
    if start in doc:
        return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda m: block, doc, count=1, flags=re.S)
    a, b = fallback(doc)
    return doc[:a] + block + doc[b:]


def main():
    by_slug = {p["slug"]: p for p in CASES + CARDS}
    for e in EXTRAS:
        by_slug[e["slug"]] = e

    # ---- case study pages
    os.makedirs("case-studies", exist_ok=True)
    for i, c in enumerate(CASES):
        open(f"case-studies/{c['slug']}.html", "w").write(case_page(i, c))

    # ---- work page grid + campaigns
    w = WORK
    order = [c["slug"] for c in CASES] + [p["slug"] for p in CARDS] + [e["slug"] for e in EXTRAS]
    grid = "".join(card(by_slug[s], "reveal") for s in order)
    fbtns = "".join(f'<button class="chip{" is-active" if k == "all" else ""}" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{v}</button>' for k, v in FILTERS)
    w = re.sub(r'(<div class="filters reveal" role="group" aria-label="Filter projects by service">\s*).*?(\s*</div>)', lambda m: m.group(1) + fbtns + m.group(2), w, count=1, flags=re.S)

    def grid_fallback(d):
        a = d.index('<div class="work-grid work-grid--flat">')
        return a, d.index("        </div>\n      </div>\n    </section>", a)
    w = replace_block(w, "work-grid", '<div class="work-grid work-grid--flat">' + grid, grid_fallback)

    camps = '\n        <h3 class="camp-head reveal">Live campaign dashboards</h3>\n        <p class="muted reveal camp-intro">Read straight off the sending dashboards, including the campaigns that didn’t fly. Reply rate is replies ÷ emails sent. Positive reply rate is interested replies ÷ all replies.</p>\n        <div class="camp-grid">' + "".join(campaign_card(c) for c in CAMPAIGNS) + "\n        </div>"

    def camp_fallback(d):
        a = d.index("<!-- Campaign screenshots go here")
        return a, d.index("-->", a) + 3
    w = replace_block(w, "campaigns", camps, camp_fallback)
    w = w.replace("Websites, lead generation and app design. Most projects cross more than one service",
                  "16 case studies and the rest of the portfolio. Most projects cross more than one service")
    open("work.html", "w").write(w)

    # ---- homepage: websites scroller + lead gen section
    s = open("index.html").read()

    def sites_fallback(d):
        a = d.index('<article class="proj', d.index("hscroll__intro"))
        a = d.rindex("\n", 0, a) + 1
        return a, d.index('          <article class="work-card ">', a)
    s = replace_block(s, "home-sites", "".join(card(by_slug[k]) for k in ["mike-k-realtor", "cj-stafford-construction", "fractional-ceo", "karpel-associates"]), sites_fallback)

    def lead_fallback(d):
        a = d.index('<div class="work-grid work-grid--flat">', d.index('id="leadgen-title"'))
        return a, d.index('\n        <div class="reveal" style="margin-top:56px">', a)
    s = replace_block(s, "home-leadgen", '<div class="work-grid work-grid--flat">' + "".join(card(by_slug[k], "reveal") for k in ["gabes-window-cleaning", "b2b-saas-growth-system"]) + "\n        </div>", lead_fallback)
    open("index.html", "w").write(s)

    # ---- sitemap
    pages = ["", "services.html", "work.html", "blog.html", "contact.html"] + [f"case-studies/{c['slug']}.html" for c in CASES]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<!-- TODO: replace https://www.example.com with your live domain -->\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{SITE_URL}/{p}</loc><lastmod>{TODAY}</lastmod></url>\n" for p in pages) + "</urlset>\n"
    open("sitemap.xml", "w").write(sm)
    print(f"built {len(CASES)} case studies, {len(order)} cards, {len(CAMPAIGNS)} campaigns")


if __name__ == "__main__":
    main()
