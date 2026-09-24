#!/usr/bin/env python3
"""Assemble dist/ from src/ + partials/ + assets/. Stdlib only, no template engine."""
import json
import shutil
import sys
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PARTIALS = ROOT / "partials"
ASSETS = ROOT / "assets"
DIST = ROOT / "dist"
DRAFTS = ROOT / "drafts"

SITE_URL = "https://steledger.com"
# The canonical service host since the gateway migration of 2026-09-22.
# ai.emercoin.com still answers reads, but its OAuth metadata now points here, so
# it is no longer a working sign-in target. This is the ONLY place a service
# hostname is hard-coded.
API_BASE = "https://api.steledger.com"

EXPLORER = "https://explorer.emercoin.com"

# The gateway source. Moved to the steledger org on 2026-09-22; GitHub redirects
# the old URL, but a published link should name where the code actually lives.
SOURCE_REPO = "https://github.com/steledger/steledger-gateway"

# The one live record the site offers as evidence. Re-write it on-chain before its
# term lapses, then update the txid here and rebuild — a lapsed record on a page
# about durability is worse than no record at all. Nothing else references these.
PROOF = {
    "name": "ai:gh:3772563",
    "txid": "1a41f6f7d12733b35cf14769811ee3b6ead87be663aa083a708c57d45dc3b169",
}

# The memory record written for the Claude Code walkthrough, and the file it
# fingerprints (src/blog/files/, published byte for byte). Same rule as PROOF:
# re-write before the term lapses. Never edit the file — its hash is the record.
EXAMPLE = {
    "file": "/blog/files/decision-2026-09.txt",
    "hash": "9f9209756f6ace1b3f35a54869d5362776913aa8b434b66c514df216f3de3f10",
    "txid": "1f24ba64f0dc807b53225fc8f26b7dd34e71f5ef0a69535a161acf7eb65e8ea5",
}
EXAMPLE["name"] = f"{PROOF['name']}:mem:{EXAMPLE['hash']}"

# Site-wide substitutions for every source fragment and markdown twin.
TOKENS = {
    "API_BASE": API_BASE,
    "SOURCE_REPO": SOURCE_REPO,
    "PROOF_NAME": PROOF["name"],
    "PROOF_TXID": PROOF["txid"],
    "PROOF_READ_URL": f"{API_BASE}/nvs/{PROOF['name']}",
    "PROOF_TX_URL": f"{EXPLORER}/tx/{PROOF['txid']}",
    "EXPLORER": EXPLORER,
    "EXAMPLE_FILE_URL": SITE_URL + EXAMPLE["file"],
    "EXAMPLE_HASH": EXAMPLE["hash"],
    "EXAMPLE_NAME": EXAMPLE["name"],
    "EXAMPLE_TXID": EXAMPLE["txid"],
    "EXAMPLE_READ_URL": f"{API_BASE}/nvs/{EXAMPLE['name']}",
    "EXAMPLE_TX_URL": f"{EXPLORER}/tx/{EXAMPLE['txid']}",
}

# Blog posts, newest first. Each is src/blog/<slug>.html (the article body, no
# title) plus src/blog/<slug>.md (same, as Markdown). Title, date and standfirst
# live here only, so the page, its twin, the index, the feed and the sitemap
# cannot disagree. Set "updated" when a post changes in substance.
BLOG_TITLE = "Blog"
BLOG_DESCRIPTION = (
    "Notes on identity, memory and trust between people and AI agents — how to "
    "use Steledger, why it is built this way, and what we think should come next."
)

# Every post is one kind (its section) and any number of tags. Both vocabularies
# are closed: a post naming anything not listed here fails the build, so a typo
# cannot quietly mint a new topic page. Add a tag here when a post needs it.
KINDS = {"guide": "Guide", "essay": "Essay"}
TAGS = {
    "identity": ("Identity", "Who an agent is, and what lets others recognise it again."),
    "memory": ("Memory", "What an agent keeps, and how it can show later what it kept."),
    "trust": ("Trust", "Why anyone should rely on an agent, and what that reliance rests on."),
    "provenance": ("Provenance", "Showing later that something existed, unchanged, and who anchored it."),
    "platforms": ("Platforms", "Vendors, lock-in, and what outlives them."),
    "claude-code": ("Claude Code", "Using Steledger from Claude Code."),
    "mcp": ("MCP", "The Model Context Protocol, and connecting to Steledger through it."),
}

# Posts, newest first. Drafts live in drafts/ (gitignored: this repo is public,
# and a draft's title is already a publication): drafts/posts.json holds their
# entries, drafts/<slug>.html and .md their bodies. `build.py --drafts` renders
# them with everything else into preview/, which nothing deploys. Publishing a
# draft = move its files to src/blog/ and its entry here.
# "written_with" names the AI model a post was written with — said on the post
# itself, because a blog about trust between people and agents should not hide it.
POSTS = [
    {
        "slug": "anchor-from-claude-code",
        "title": "Prove what your agent knew, and when",
        "description": (
            "Connect Steledger to Claude Code, fingerprint a file, anchor the "
            "fingerprint on a public chain, and check it later without trusting "
            "this service."
        ),
        "published": "2026-09-23",
        "kind": "guide",
        "tags": ["claude-code", "mcp", "provenance", "memory"],
        "written_with": "Claude",
    },
]

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
    "privacy": {
        "html_path": "/privacy.html",
        "md_path": "/privacy.md",
        "title": "Privacy and security",
        "description": (
            "What Steledger keeps, what it never had, and what goes on a public "
            "chain and cannot be taken back."
        ),
        "jsonld": {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": "Privacy and security — Steledger",
            "url": SITE_URL + "/privacy.html",
            "description": (
                "No cookies or analytics; access logs with the client address "
                "stripped; what a write puts on a public chain, permanently."
            ),
        },
    },
}


def fill(text: str, tokens: dict) -> str:
    for key, value in tokens.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def render_page(body: str, meta: dict) -> str:
    # MD_PATH is per-page: the footer offers "this page as Markdown", which on any
    # page but the home page used to be a link to a different page.
    page_tokens = {**TOKENS, "MD_PATH": meta.get("md_path", "/index.md")}
    body = fill(body, page_tokens)
    header = fill((PARTIALS / "header.html").read_text(), page_tokens)
    footer = fill((PARTIALS / "footer.html").read_text(), page_tokens)

    tokens = {
        "TITLE": meta["title"],
        "DESCRIPTION": meta["description"],
        "CANONICAL": SITE_URL + meta["html_path"],
        "OG_TYPE": meta.get("og_type", "website"),
        "SITE_URL": SITE_URL,
        "JSONLD": json.dumps(meta["jsonld"], ensure_ascii=False),
    }
    head = fill((PARTIALS / "head.html").read_text(), tokens)

    lines = ["<!doctype html><html lang=\"en\">", "<head>", head.rstrip()]
    lines.append(f'  <title>{meta["title"]} — Steledger</title>')
    if meta.get("md_path"):
        lines.append(f'  <link rel="alternate" type="text/markdown" href="{meta["md_path"]}">')
    lines += [f"  {line}" for line in meta.get("head_extra", [])]
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


def human_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B %Y')}"


def post_url(post: dict) -> str:
    return f"/blog/{post['slug']}.html"


def tag_url(tag: str) -> str:
    return f"/blog/tags/{tag}.html"


def check_posts(posts: list) -> None:
    for p in posts:
        if p["kind"] not in KINDS:
            sys.exit(f"{p['slug']}: unknown kind {p['kind']!r}; add it to KINDS")
        for t in p["tags"]:
            if t not in TAGS:
                sys.exit(f"{p['slug']}: unknown tag {t!r}; add it to TAGS")


def used_tags() -> list:
    """Tags carried by at least one built post, in TAGS order."""
    used = {t for p in POSTS for t in p["tags"]}
    return [t for t in TAGS if t in used]


def tag_links(tags: list) -> str:
    return ", ".join(f'<a href="{tag_url(t)}">{TAGS[t][0]}</a>' for t in tags)


def tag_links_md(tags: list) -> str:
    return ", ".join(f"[{TAGS[t][0]}]({tag_url(t)})" for t in tags)


BLOG_REF = {"@type": "Blog", "name": f"Steledger {BLOG_TITLE}", "url": SITE_URL + "/blog/"}
# The project, not a company: there is no legal entity behind the site.
PUBLISHER = {"@type": "Organization", "name": "Steledger", "url": SITE_URL + "/"}


def post_meta(post: dict) -> dict:
    url = SITE_URL + post_url(post)
    return {
        "html_path": post_url(post),
        "md_path": f"/blog/{post['slug']}.md",
        "title": post["title"],
        "description": post["description"],
        "og_type": "article",
        "head_extra": [
            f'<meta property="article:published_time" content="{post["published"]}">',
            f'<meta property="article:section" content="{KINDS[post["kind"]]}">',
            *(f'<meta property="article:tag" content="{TAGS[t][0]}">' for t in post["tags"]),
        ],
        "jsonld": {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post["title"],
            "description": post["description"],
            "url": url,
            "mainEntityOfPage": url,
            "datePublished": post["published"],
            "dateModified": post.get("updated", post["published"]),
            "inLanguage": "en",
            "articleSection": KINDS[post["kind"]],
            "keywords": [TAGS[t][0] for t in post["tags"]],
            "author": PUBLISHER,
            "publisher": PUBLISHER,
            "isPartOf": BLOG_REF,
        },
    }


def post_dateline(post: dict) -> str:
    line = f'{KINDS[post["kind"]]} · <time datetime="{post["published"]}">{human_date(post["published"])}</time>'
    if post.get("updated"):
        line += f' · updated <time datetime="{post["updated"]}">{human_date(post["updated"])}</time>'
    return line


def authorship(post: dict) -> str:
    if post.get("written_with"):
        return f"Written with {post['written_with']}, an AI model, and published by Steledger."
    return "Published by Steledger."


def post_source(post: dict, ext: str) -> Path:
    return (DRAFTS if post.get("draft") else SRC / "blog") / f"{post['slug']}.{ext}"


def render_post_body(post: dict) -> str:
    article = post_source(post, "html").read_text().strip()
    return (
        '<article class="post">\n'
        '<header class="post-header">\n'
        f'  <p class="post-meta"><a href="/blog/">{BLOG_TITLE}</a> · {post_dateline(post)}</p>\n'
        f'  <h1>{escape(post["title"])}</h1>\n'
        f'  <p class="lead">{escape(post["description"])}</p>\n'
        "</header>\n"
        f"{article}\n"
        '<footer class="post-footer">\n'
        f"  <p>Topics: {tag_links(post['tags'])}.</p>\n"
        f"  <p>{authorship(post)}</p>\n"
        "</footer>\n"
        "</article>"
    )


def render_post_md(post: dict) -> str:
    dateline = f"{KINDS[post['kind']]}, published {post['published']}"
    if post.get("updated"):
        dateline += f", updated {post['updated']}"
    body = post_source(post, "md").read_text().strip()
    return fill(
        f"# {post['title']}\n\n{post['description']}\n\n"
        f"{dateline}. Part of the [Steledger blog](/blog/).\n\n{body}\n\n---\n\n"
        f"Topics: {tag_links_md(post['tags'])}.\n\n{authorship(post)}\n",
        TOKENS,
    )


def blog_index_meta() -> dict:
    return {
        "html_path": "/blog/",
        "md_path": "/blog/index.md",
        "title": BLOG_TITLE,
        "description": BLOG_DESCRIPTION,
        "jsonld": {
            "@context": "https://schema.org",
            **BLOG_REF,
            "description": BLOG_DESCRIPTION,
            "publisher": PUBLISHER,
            "blogPost": [
                {
                    "@type": "BlogPosting",
                    "headline": p["title"],
                    "url": SITE_URL + post_url(p),
                    "datePublished": p["published"],
                }
                for p in POSTS
            ],
        },
    }


def render_post_list(posts: list) -> str:
    items = "\n".join(
        "  <li>\n"
        f'    <p class="post-meta">{KINDS[p["kind"]]} · <time datetime="{p["published"]}">{human_date(p["published"])}</time></p>\n'
        f'    <h2><a href="{post_url(p)}">{escape(p["title"])}</a></h2>\n'
        f'    <p>{escape(p["description"])}</p>\n'
        "  </li>"
        for p in posts
    )
    return f'<ol class="post-list">\n{items}\n</ol>'


def render_post_list_md(posts: list) -> str:
    return "\n\n".join(
        f"## [{p['title']}]({post_url(p)})\n\n"
        f"{KINDS[p['kind']]}, {p['published']} — {p['description']}"
        for p in posts
    )


def render_blog_index() -> str:
    return (
        '<section class="hero">\n'
        f"  <h1>{BLOG_TITLE}</h1>\n"
        f'  <p class="lead">{escape(BLOG_DESCRIPTION)}</p>\n'
        f'  <p class="caption">Topics: {tag_links(used_tags())}. '
        'Subscribe: <a href="/feed.xml">Atom feed</a>.</p>\n'
        "</section>\n\n"
        + render_post_list(POSTS)
    )


def render_blog_index_md() -> str:
    return (
        f"# {BLOG_TITLE}\n\n{BLOG_DESCRIPTION}\n\n"
        f"Topics: {tag_links_md(used_tags())}.\n\n"
        f"Subscribe: [Atom feed](/feed.xml).\n\n{render_post_list_md(POSTS)}\n"
    )


def tagged(tag: str) -> list:
    return [p for p in POSTS if tag in p["tags"]]


def tag_meta(tag: str) -> dict:
    label, blurb = TAGS[tag]
    url = SITE_URL + tag_url(tag)
    return {
        "html_path": tag_url(tag),
        "md_path": f"/blog/tags/{tag}.md",
        "title": f"{label} — {BLOG_TITLE}",
        "description": blurb,
        "jsonld": {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": f"{label} — Steledger {BLOG_TITLE}",
            "url": url,
            "description": blurb,
            "about": label,
            "isPartOf": BLOG_REF,
            "hasPart": [
                {"@type": "BlogPosting", "headline": p["title"], "url": SITE_URL + post_url(p)}
                for p in tagged(tag)
            ],
        },
    }


def render_tag_page(tag: str) -> str:
    label, blurb = TAGS[tag]
    others = [t for t in used_tags() if t != tag]
    return (
        '<section class="hero">\n'
        f'  <p class="post-meta"><a href="/blog/">{BLOG_TITLE}</a> · Topic</p>\n'
        f"  <h1>{label}</h1>\n"
        f'  <p class="lead">{escape(blurb)}</p>\n'
        + (f'  <p class="caption">Other topics: {tag_links(others)}.</p>\n' if others else "")
        + "</section>\n\n"
        + render_post_list(tagged(tag))
    )


def render_tag_page_md(tag: str) -> str:
    label, blurb = TAGS[tag]
    return (
        f"# {label}\n\nA topic on the [Steledger blog](/blog/). {blurb}\n\n"
        f"{render_post_list_md(tagged(tag))}\n"
    )


def build_feed() -> str:
    """Atom 1.0, full content. Every timestamp comes from POSTS, never the clock,
    so rebuilding an unchanged site leaves the feed byte-identical."""

    def stamp(iso: str) -> str:
        return f"{iso}T00:00:00Z"

    def updated(p: dict) -> str:
        return p.get("updated", p["published"])

    entries = []
    for p in POSTS:
        url = SITE_URL + post_url(p)
        content = fill(post_source(p, "html").read_text().strip(), TOKENS)
        entries.append(
            "  <entry>\n"
            f"    <title>{escape(p['title'])}</title>\n"
            f'    <link rel="alternate" type="text/html" href="{url}"/>\n'
            f'    <link rel="alternate" type="text/markdown" href="{SITE_URL}/blog/{p["slug"]}.md"/>\n'
            f"    <id>{url}</id>\n"
            f"    <published>{stamp(p['published'])}</published>\n"
            f"    <updated>{stamp(updated(p))}</updated>\n"
            f"    <summary>{escape(p['description'])}</summary>\n"
            f'    <category term="{p["kind"]}" label="{KINDS[p["kind"]]}"/>\n'
            + "".join(
                f'    <category term="{t}" label="{TAGS[t][0]}" scheme="{SITE_URL}/blog/tags/"/>\n'
                for t in p["tags"]
            )
            + 
            f'    <content type="html">{escape(content)}</content>\n'
            "  </entry>"
        )
    feed_updated = max((updated(p) for p in POSTS), default="2026-09-23")
    # xml:base resolves the root-relative links inside each entry's content.
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<feed xmlns="http://www.w3.org/2005/Atom" xml:base="{SITE_URL}/" xml:lang="en">\n'
        f"  <title>Steledger {BLOG_TITLE}</title>\n"
        f"  <subtitle>{escape(BLOG_DESCRIPTION)}</subtitle>\n"
        f'  <link rel="self" type="application/atom+xml" href="{SITE_URL}/feed.xml"/>\n'
        f'  <link rel="alternate" type="text/html" href="{SITE_URL}/blog/"/>\n'
        f"  <id>{SITE_URL}/blog/</id>\n"
        f"  <updated>{stamp(feed_updated)}</updated>\n"
        f"  <author><name>Steledger</name><uri>{SITE_URL}/</uri></author>\n"
        f'  <icon>{SITE_URL}/assets/favicon.svg</icon>\n'
        + "\n".join(entries)
        + "\n</feed>\n"
    )


def build_robots() -> str:
    bots = ["*", "GPTBot", "ClaudeBot", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "CCBot"]
    blocks = "\n\n".join(f"User-agent: {b}\nAllow: /" for b in bots)
    return blocks + f"\n\nSitemap: {SITE_URL}/sitemap.xml\n"


def build_llms() -> str:
    # Posts are listed by their Markdown twin: that is the copy an agent wants.
    posts = "\n".join(
        f"- [{p['title']}]({SITE_URL}/blog/{p['slug']}.md): {KINDS[p['kind']]}. {p['description']}"
        for p in POSTS
    )
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
- [Privacy and security]({SITE_URL}/privacy.html): what is kept, what is public
  and permanent, how to report a vulnerability
- [Privacy and security as Markdown]({SITE_URL}/privacy.md)

## Blog

- [Blog index]({SITE_URL}/blog/index.md): {BLOG_DESCRIPTION}
- [Atom feed]({SITE_URL}/feed.xml): every post, full text
{posts}
"""


def build_sitemap() -> str:
    urls = []  # (loc, lastmod or None)
    for meta in PAGES.values():
        urls += [(SITE_URL + meta["html_path"], None), (SITE_URL + meta["md_path"], None)]
    urls += [(SITE_URL + "/blog/", None), (SITE_URL + "/blog/index.md", None)]
    for t in used_tags():
        urls += [(SITE_URL + tag_url(t), None), (f"{SITE_URL}/blog/tags/{t}.md", None)]
    for p in POSTS:
        lastmod = p.get("updated", p["published"])
        urls += [
            (SITE_URL + post_url(p), lastmod),
            (f"{SITE_URL}/blog/{p['slug']}.md", lastmod),
        ]
    items = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{m}</lastmod></url>" if m else f"  <url><loc>{u}</loc></url>"
        for u, m in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{items}\n"
        "</urlset>\n"
    )


def main():
    global DIST, POSTS
    if "--drafts" in sys.argv[1:]:
        # Everything, drafts included, into a gitignored directory that nothing
        # deploys. dist/ is committed and served, so a draft must never land there.
        DIST = ROOT / "preview"
        drafts_index = DRAFTS / "posts.json"
        if drafts_index.exists():
            drafts = [{**d, "draft": True} for d in json.loads(drafts_index.read_text())]
            POSTS = sorted(drafts + POSTS, key=lambda p: p["published"], reverse=True)
    check_posts(POSTS)
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    for slug, meta in PAGES.items():
        (DIST / f"{slug}.html").write_text(render_page((SRC / f"{slug}.html").read_text(), meta))
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
    (DIST / "404.html").write_text(render_page((SRC / "404.html").read_text(), not_found_meta))

    blog = DIST / "blog"
    # Files that posts anchor on-chain: copied byte for byte, never templated.
    shutil.copytree(SRC / "blog" / "files", blog / "files")
    (blog / "index.html").write_text(render_page(render_blog_index(), blog_index_meta()))
    (blog / "index.md").write_text(render_blog_index_md())
    for p in POSTS:
        (blog / f"{p['slug']}.html").write_text(render_page(render_post_body(p), post_meta(p)))
        (blog / f"{p['slug']}.md").write_text(render_post_md(p))
    tags_dir = blog / "tags"
    tags_dir.mkdir()
    for t in used_tags():
        (tags_dir / f"{t}.html").write_text(render_page(render_tag_page(t), tag_meta(t)))
        (tags_dir / f"{t}.md").write_text(render_tag_page_md(t))
    (DIST / "feed.xml").write_text(build_feed())

    shutil.copytree(ASSETS, DIST / "assets")
    # crawlers and favicon services ask for /favicon.ico whatever the page declares
    shutil.copy(ASSETS / "favicon.ico", DIST / "favicon.ico")

    (DIST / "robots.txt").write_text(build_robots())
    (DIST / "llms.txt").write_text(build_llms())
    (DIST / "sitemap.xml").write_text(build_sitemap())

    print(
        f"Built {len(PAGES)} page(s), blog with {len(POSTS)} post(s) and "
        f"{len(used_tags())} topic(s), 404 into {DIST}"
    )


if __name__ == "__main__":
    main()
