#!/usr/bin/env python3
"""Static checks for dist/. Stdlib only. Run before every commit."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SITE_URL = "https://steledger.com"

ERRORS = []


def fail(msg: str):
    ERRORS.append(msg)


class PageScan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.styles = []
        self.stylesheets = []
        self.jsonld = []
        self._in_jsonld = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "style" in attrs:
            self.styles.append(tag)
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.stylesheets.append(attrs.get("href"))
        for a in ("href", "src"):
            if a in attrs and attrs[a]:
                self.links.append(attrs[a])
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._in_jsonld = True
            self.jsonld.append("")

    def handle_data(self, data):
        if self._in_jsonld:
            self.jsonld[-1] += data

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_jsonld = False


def resolve_internal(href: str):
    """dist/ file an href points to, or None if it's external/not a file link."""
    if href.startswith("#") or href.startswith("mailto:"):
        return None
    if href.startswith(SITE_URL):
        href = href[len(SITE_URL):] or "/"
    elif href.startswith("http://") or href.startswith("https://"):
        return None
    if not href.startswith("/"):
        return None
    path = href.split("#")[0].split("?")[0]
    if path in ("", "/"):
        path = "/index.html"
    return DIST / path.lstrip("/")


def check_pages():
    html_files = sorted(DIST.glob("*.html"))
    if not html_files:
        fail("No .html files found in dist/")
        return

    sitemap_path = DIST / "sitemap.xml"
    sitemap_text = sitemap_path.read_text() if sitemap_path.exists() else ""

    for f in html_files:
        scan = PageScan()
        scan.feed(f.read_text())

        if scan.styles:
            fail(f"{f.name}: style= attribute found on <{scan.styles[0]}>")
        if len(scan.stylesheets) != 1:
            fail(f"{f.name}: expected exactly one stylesheet link, found {len(scan.stylesheets)}")

        for block in scan.jsonld:
            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                fail(f"{f.name}: invalid JSON-LD ({e})")

        for href in scan.links:
            target = resolve_internal(href)
            if target is not None and not target.exists():
                fail(f"{f.name}: broken internal link {href!r} -> {target}")

        if f.name == "404.html":
            continue  # error page: no markdown twin, not part of the sitemap

        twin = f.with_suffix(".md")
        if not twin.exists():
            fail(f"{f.name}: missing markdown twin {twin.name}")

        html_url = SITE_URL + ("/" if f.name == "index.html" else f"/{f.name}")
        md_url = SITE_URL + f"/{twin.name}"
        if html_url not in sitemap_text:
            fail(f"sitemap.xml: missing {html_url}")
        if md_url not in sitemap_text:
            fail(f"sitemap.xml: missing {md_url}")


def check_llms_txt():
    path = DIST / "llms.txt"
    if not path.exists():
        fail("llms.txt missing")
        return
    text = path.read_text()
    for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
        href = match.group(1)
        if not href.startswith("https://"):
            fail(f"llms.txt: link is not an absolute https URL: {href}")
            continue
        if href.startswith(SITE_URL):
            target = resolve_internal(href)
            if target is not None and not target.exists():
                fail(f"llms.txt: broken internal link {href}")


def main():
    if not DIST.exists():
        fail("dist/ does not exist — run tools/build.py first")
    else:
        check_pages()
        check_llms_txt()

    if ERRORS:
        print(f"{len(ERRORS)} check(s) failed:\n")
        for e in ERRORS:
            print(f"  - {e}")
        sys.exit(1)

    print("All checks passed.")


if __name__ == "__main__":
    main()
