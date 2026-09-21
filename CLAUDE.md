# steledger.com — Engineering Guide for Claude Code

> Read fully at the start of every session. Also read `CLAUDE.local.md` if present
> (gitignored: project strategy and the current session plan).
> This repo is PUBLIC. Nothing in committed files may contain strategy, holdings,
> people, or internal policy numbers.

## 1. What this repo is

The static front door for **Steledger** — durable identity and memory for AI agents,
anchored on the Emercoin blockchain's Name-Value Storage (NVS).

- The live service (API, MCP server, OAuth, docs) is moving to its own host,
  **api.steledger.com**. Until that host serves traffic, the service runs at
  **ai.emercoin.com**. This site does NOT host the API and does NOT duplicate the
  docs — it links to them.
- The API host appears in pages ONLY through the `API_BASE` constant in
  `tools/build.py`. Never hard-code a service hostname in `src/` — switching hosts
  must be a one-line change plus a rebuild.
- Audience priority: **AI agents > developers > humans browsing.** Build machine-first;
  human readability follows from clean structure.

## 2. Source of truth for product facts

Never invent product behavior. Before writing or changing copy, read the current
docs at `{API_BASE}/llms-full.txt` and `{API_BASE}/openapi.json`.
If the site and those docs disagree, the docs win — fix the site.

Stable facts (re-verify before relying on them):
- MCP endpoint: `{API_BASE}/mcp` (Streamable HTTP).
- Sign-in: OAuth 2.1 handled by the MCP client, delegated to GitHub. Read tools are
  open without sign-in; write tools require it.
- Claude (paid plans): Settings → Connectors → add custom connector with the URL above.
- Claude Code: `claude mcp add --transport http steledger {API_BASE}/mcp`,
  then `/mcp` to sign in.
- Records: identity `ai:gh:<github_id>`, memory `ai:gh:<github_id>:mem:<hash>`.
  Only a content hash goes on-chain; the body stays off-chain.
- A write reads back as `pending`, then `confirmed` after the next block (~10 min).

## 3. Hosting and deploy

- GitHub Pages, deployed by GitHub Actions from the committed `dist/` folder
  (`.github/workflows/pages.yml`, upload-pages-artifact → deploy-pages).
- **No build runs in CI.** Pages are generated locally (by Claude Code), reviewed,
  then `dist/` is committed. CI only uploads it.
- Custom domain `steledger.com` via `dist/CNAME`; `dist/.nojekyll` so `.md` and
  `.txt` files are served as-is.

## 4. Layout

```
src/            page sources: one .html body fragment + one .md per page
partials/       head.html, header.html, footer.html
assets/         styles.css (the ONE stylesheet), favicon.svg, minimal JS if any
tools/build.py  stdlib-only assembler: src + partials + assets -> dist/
tools/check.py  stdlib-only checks (see section 7)
dist/           build output — committed, served by Pages
```

`build.py` is deliberately tiny: wrap each `src/<page>.html` fragment with the
partials, copy the matching `.md`, copy assets, and write `llms.txt`, `robots.txt`,
`sitemap.xml`, `CNAME`, `.nojekyll`, `404.html`. No template engine, no dependencies.

## 5. Page conventions (follow exactly — do not improvise layout)

Every generated page:
```html
<!doctype html><html lang="en">
<head> {head partial: charset, viewport, description, canonical, OG, favicon,
        stylesheet, JSON-LD}
  <title>PAGE_TITLE — Steledger</title>
  <link rel="alternate" type="text/markdown" href="/PAGE.md">
</head>
<body> {header partial} <main>…</main> {footer partial} </body></html>
```

- One stylesheet. No inline styles, no CSS frameworks, no CDN scripts.
- Semantic HTML5, headings in order. Works fully without JavaScript.
- Every page has a Markdown twin at the same path + `.md` with the same content.
- JSON-LD on every page (`WebSite` + `SoftwareApplication`/`WebAPI` on the home page).
- Light and dark themes via `prefers-color-scheme`; responsive; fast (no web fonts
  unless one is clearly worth it).
- Aesthetic: minimal, technical, archival — think a carved record, not a startup.
  Reference points: Linear, Stripe docs, a well-set technical paper.

## 6. Copy rules

- Plain, technical English. No hype, no "revolutionary", no emoji headlines.
- Never use coin/crypto/DeFi/Web3/NFT/token-price language. The blockchain is named
  honestly as the substrate — "built on Emercoin, running since 2013" — not sold.
- Do not claim listing, approval, or endorsement by Anthropic or anyone else.
  "Works with Claude and any MCP client" is a factual compatibility statement.
- Do not describe features that are not live. Unreleased work is omitted, not teased.
- Do not name individuals or the legacy Emercoin team/community.
- Emercoin is named as the substrate, but do not link to emercoin.com (a frozen
  legacy site). For evidence that the chain is alive, link to the Emercoin node
  source repository on GitHub and a public block explorer (verify both URLs first).
- Contact: `hello@steledger.com`; security reports: `security@steledger.com`.

## 7. Checks (`python tools/check.py`, must pass before commit)

- Every internal link resolves to a file in `dist/`.
- Every `dist/*.html` has its `.md` twin, and both are listed in `sitemap.xml`.
- JSON-LD blocks parse as JSON.
- `llms.txt` links resolve (internal) or are absolute https URLs (external).
- No `style=` attributes; exactly one stylesheet link per page.

## 8. Do not

- Do not add a framework, CMS, bundler, or npm toolchain.
- Do not copy the service docs into this repo — link to them via `API_BASE`.
- Do not add analytics, cookies, or third-party trackers (agents don't run JS
  anyway; usage metrics come from the service's own server-side stats).
- Do not commit `CLAUDE.local.md`.
