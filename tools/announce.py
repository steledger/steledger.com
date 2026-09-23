#!/usr/bin/env python3
"""Announce a published blog post on X as @steledger. Stdlib only.

    python tools/announce.py <slug>          # show the post text, send nothing
    python tools/announce.py <slug> --send   # post it

Run by hand after the post is live — there is no CI, and a person should see the
text before it goes out. Refuses to send unless the post's URL already answers
200, so an announcement can never point at a page that is not deployed yet.

Credentials come from .common_envs (gitignored): X_OAUTH_CONSUMER_KEY,
X_OAUTH_CONSUMER_KEY_SECRET, X_OAUTH_ACCESS_TOKEN, X_OAUTH_ACCESS_TOKEN_SECRET.
The access token must be generated for @steledger after the app was given
Read and Write permission, or X will refuse the write.

X charges per post created, more for a post with a link; see
https://docs.x.com/x-api/getting-started/pricing.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402 — POSTS, KINDS, SITE_URL: one source for post metadata

ENV_FILE = build.ROOT / ".common_envs"
TWEETS = "https://api.x.com/2/tweets"
LIMIT = 280
URL_WEIGHT = 23  # X counts every link as 23 characters, whatever its length


def load_env() -> dict:
    env = {}
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[len("export "):]
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip("'\"")
    return env


def compose(post: dict) -> tuple[str, str]:
    """The announcement text and the URL it links to, within X's length limit."""
    url = build.SITE_URL + build.post_url(post)
    head = f"{build.KINDS[post['kind']]}: {post['title']}"
    body = post["description"]
    room = LIMIT - URL_WEIGHT - len(head) - 4  # two blank-line separators
    if len(body) > room:
        body = body[: room - 1].rsplit(" ", 1)[0].rstrip(",;:—- ") + "…"
    return f"{head}\n\n{body}\n\n{url}", url


def _pct(s: str) -> str:
    return urllib.parse.quote(s, safe="~")


def oauth1_header(method: str, url: str, env: dict) -> str:
    """OAuth 1.0a HMAC-SHA1. A JSON body is not part of the signature base string."""
    params = {
        "oauth_consumer_key": env["X_OAUTH_CONSUMER_KEY"],
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": env["X_OAUTH_ACCESS_TOKEN"],
        "oauth_version": "1.0",
    }
    param_str = "&".join(f"{_pct(k)}={_pct(v)}" for k, v in sorted(params.items()))
    base = "&".join([method.upper(), _pct(url), _pct(param_str)])
    key = f"{_pct(env['X_OAUTH_CONSUMER_KEY_SECRET'])}&{_pct(env['X_OAUTH_ACCESS_TOKEN_SECRET'])}"
    digest = hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()
    params["oauth_signature"] = base64.b64encode(digest).decode()
    return "OAuth " + ", ".join(f'{_pct(k)}="{_pct(v)}"' for k, v in sorted(params.items()))


def is_live(url: str) -> bool:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=15) as r:
            return r.status == 200
    except urllib.error.URLError:
        return False


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    posts = {p["slug"]: p for p in build.POSTS}
    if args[0] not in posts:
        sys.exit(f"no published post {args[0]!r}; drafts cannot be announced")
    text, url = compose(posts[args[0]])
    print(text, f"\n\n[{len(text) - len(url) + URL_WEIGHT}/{LIMIT} characters as X counts them]")

    if "--send" not in sys.argv[1:]:
        print("\nDry run. Add --send to post it.")
        return
    if not is_live(url):
        sys.exit(f"\n{url} is not live yet — push and let the site sync first.")

    env = load_env()
    req = urllib.request.Request(
        TWEETS,
        data=json.dumps({"text": text}).encode(),
        method="POST",
        headers={
            "Authorization": oauth1_header("POST", TWEETS, env),
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            tweet_id = json.load(resp)["data"]["id"]
    except urllib.error.HTTPError as e:
        sys.exit(f"\nX refused the post: {e.code} {e.read().decode(errors='replace')}")
    print(f"\nPosted: https://x.com/steledger/status/{tweet_id}")


if __name__ == "__main__":
    main()
