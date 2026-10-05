#!/usr/bin/env python3
"""Performance pass for every page (run by tools/seo.py, so by the build too).

- Inlines a minified copy of assets/css/style.css (no render-blocking stylesheet request).
  Edit assets/css/style.css, never the inlined <style> block.
- Preloads the two fonts needed above the fold; removes any Google Fonts requests.
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = os.path.join(ROOT, "assets/css/style.css")
PRELOAD = ["assets/fonts/anton-400.woff2", "assets/fonts/space-mono-400.woff2", "assets/fonts/barlow-condensed-600.woff2"]


def minify(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>~])\s*", r"\1", css)
    css = css.replace(";}", "}")
    # restore spaces that matter inside selectors/values
    css = re.sub(r"(\d)(and|or)\(", r"\1 \2 (", css)
    css = css.replace(")and(", ") and (").replace("@media(", "@media (")
    return css.strip()


def lazy_images(doc):
    """Lazy-load every image except the header logo and the homepage hero art (above the fold)."""
    def sub(m):
        tag = m.group(0)
        if "loading=" in tag or "brand-logo" in tag or "data-depth=" in tag:
            return tag
        return tag[:4] + ' loading="lazy" decoding="async"' + tag[4:]
    return re.sub(r"<img\b[^>]*>", sub, doc)


def optimise(doc, prefix):
    doc = lazy_images(doc)
    css = minify(open(CSS).read()).replace("url(../", f"url({prefix}assets/")
    doc = re.sub(r'\s*<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"[^>]*>', "", doc)
    doc = re.sub(r'\s*<link href="https://fonts\.googleapis\.com/[^"]*" rel="stylesheet">', "", doc)
    doc = re.sub(r'\s*<link rel="preload" as="font"[^>]*>', "", doc)
    preload = "".join(f'\n  <link rel="preload" as="font" type="font/woff2" href="{prefix}{f}" crossorigin>' for f in PRELOAD)
    block = f'{preload}\n  <style data-src="assets/css/style.css">{css}</style>'
    if "<style data-src=" in doc:
        doc = re.sub(r'\s*<style data-src="assets/css/style\.css">.*?</style>', lambda m: block, doc, count=1, flags=re.S)
    else:
        doc, n = re.subn(r'\s*<link rel="stylesheet" href="[^"]*assets/css/style\.css">', lambda m: block, doc, count=1)
        assert n, "stylesheet link not found"
    return doc
