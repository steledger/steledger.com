#!/usr/bin/env python3
"""Assemble dist/ from src/ + partials/ + assets/. Stdlib only, no template engine."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PARTIALS = ROOT / "partials"
ASSETS = ROOT / "assets"
DIST = ROOT / "dist"

SITE_URL = "https://steledger.com"
# The canonical service host since the gateway migration of 2026-09-22.
# ai.emercoin.com still answers reads, but its OAuth metadata now points here, so
# it is no longer a working sign-in target. This is the ONLY place a service
# hostname is hard-coded.
API_BASE = "https://api.steledger.com"

EXPLORER = "https://explorer.emercoin.com"

# The one live record the site offers as evidence. Re-write it on-chain before its
# term lapses, then update the txid here and rebuild — a lapsed record on a page
# about durability is worse than no record at all. Nothing else references these.
PROOF = {
    "name": "ai:gh:3772563",
    "txid": "1a41f6f7d12733b35cf14769811ee3b6ead87be663aa083a708c57d45dc3b169",
}

# Site-wide substitutions for every source fragment and markdown twin.
TOKENS = {
    "API_BASE": API_BASE,
    "PROOF_NAME": PROOF["name"],
    "PROOF_TXID": PROOF["txid"],
    "PROOF_READ_URL": f"{API_BASE}/nvs/{PROOF['name']}",
    "PROOF_TX_URL": f"{EXPLORER}/tx/{PROOF['txid']}",
}

PAGES = {
    "index": {
        "html_path": "/",
        "md_path": "/index.md",
        "title": "Identity and memory for AI agents",
        "description": (
            "Durable identity and memory for AI agents, anchored on the "
            "Emercoin blockchain's Name-Value Storage."
        ),
        "jsonld": {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "WebSite",
                    "name": "Steledger",
                    "url": SITE_URL + "/",
                    "description": (
                        "Durable identity and memory for AI agents, anchored "
                        "on the Emercoin blockchain."
                    ),
                },
                {
                    "@type": "WebAPI",
                    "name": "Steledger agent gateway",
                    "url": API_BASE,
                    "documentation": API_BASE + "/openapi.json",
                    "description": (
                        "HTTP API and MCP server for AI agent identity and "
                        "memory, anchored on Emercoin NVS."
                    ),
                },
            ],
        },
    },
}


def fill(text: str, tokens: dict) -> str:
    for key, value in tokens.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def render_page(slug: str, meta: dict) -> str:
    body = fill((SRC / f"{slug}.html").read_text(), TOKENS)
    header = fill((PARTIALS / "header.html").read_text(), TOKENS)
    footer = fill((PARTIALS / "footer.html").read_text(), TOKENS)

    tokens = {
        "TITLE": meta["title"],
        "DESCRIPTION": meta["description"],
        "CANONICAL": SITE_URL + meta["html_path"],
        "SITE_URL": SITE_URL,
        "JSONLD": json.dumps(meta["jsonld"], ensure_ascii=False),
    }
    head = fill((PARTIALS / "head.html").read_text(), tokens)

    lines = ["<!doctype html><html lang=\"en\">", "<head>", head.rstrip()]
    lines.append(f'  <title>{meta["title"]} — Steledger</title>')
    if meta.get("md_path"):
        lines.append(f'  <link rel="alternate" type="text/markdown" href="{meta["md_path"]}">')
    lines += [
        "</head>",
        "<body>",
        header.strip(),
        '<main id="content">',
        body.strip(),
        "</main>",
        footer.strip(),
        "</body></html>",
    ]
    return "\n".join(lines) + "\n"


def build_robots() -> str:
    bots = ["*", "GPTBot", "ClaudeBot", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "CCBot"]
    blocks = "\n\n".join(f"User-agent: {b}\nAllow: /" for b in bots)
    return blocks + f"\n\nSitemap: {SITE_URL}/sitemap.xml\n"


def build_llms() -> str:
    return f"""# Steledger

> Durable identity and memory for AI agents, anchored on the Emercoin blockchain's
> Name-Value Storage (NVS). This site is the front door; the live service — API,
> MCP server, OAuth, and full documentation — runs at {API_BASE}.

## Service

- [Quickstart]({API_BASE}/docs/quickstart.md): raw HTTP walkthrough
- [MCP guide]({API_BASE}/docs/mcp.md): connect Claude, Claude Code, or any MCP client
- [NVS data model]({API_BASE}/docs/nvs.md): record names, ownership, expiry
- [OpenAPI spec]({API_BASE}/openapi.json): full machine-readable contract
- [Full documentation corpus]({API_BASE}/llms-full.txt)

## This site

- [Home]({SITE_URL}/): what Steledger is, how to connect, how it works
- [Home as Markdown]({SITE_URL}/index.md)
"""


def build_sitemap() -> str:
    urls = []
    for meta in PAGES.values():
        urls.append(SITE_URL + meta["html_path"])
        urls.append(SITE_URL + meta["md_path"])
    items = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{items}\n"
        "</urlset>\n"
    )


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    for slug, meta in PAGES.items():
        (DIST / f"{slug}.html").write_text(render_page(slug, meta))
        md_src = SRC / f"{slug}.md"
        if md_src.exists():
            md_text = fill(md_src.read_text(), TOKENS)
            (DIST / f"{slug}.md").write_text(md_text)

    # 404 is generated but is not a content page: no markdown twin, not in sitemap/llms.txt.
    not_found_meta = {
        "html_path": "/404.html",
        "title": "Not found",
        "description": "This page does not exist on steledger.com.",
        "jsonld": {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Steledger",
            "url": SITE_URL + "/",
        },
    }
    (DIST / "404.html").write_text(render_page("404", not_found_meta))

    shutil.copytree(ASSETS, DIST / "assets")

    (DIST / "robots.txt").write_text(build_robots())
    (DIST / "llms.txt").write_text(build_llms())
    (DIST / "sitemap.xml").write_text(build_sitemap())
    (DIST / "CNAME").write_text("steledger.com\n")
    (DIST / ".nojekyll").write_text("")

    print(f"Built {len(PAGES)} page(s) + 404 into {DIST}")


if __name__ == "__main__":
    main()
