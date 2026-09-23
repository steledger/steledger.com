#!/usr/bin/env python3
"""Announce a published blog post on X as @steledger. Stdlib only.

    python tools/announce.py <slug>          # show the post text, send nothing
    python tools/announce.py <slug> --send   # post it
    python tools/announce.py --check         # refresh the token, show account and scopes

Run by hand after the post is live — there is no CI, and a person should see the
text before it goes out. Refuses to send unless the post's URL already answers
200, so an announcement can never point at a page that is not deployed yet.

Auth is OAuth 2.0 user context for @steledger, from .common_envs (gitignored):
X_OAUTH2_CLIENT_ID, X_OAUTH2_CLIENT_SECRET, X_OAUTH2_ACCESS_TOKEN and
X_OAUTH2_REFRESH_TOKEN. An access token lives about two hours, so every run
refreshes it first — and X rotates the refresh token on each use, so the new
pair is written back to .common_envs before anything else happens. If a run
dies between the two, regenerate the tokens in the developer portal.

X charges per post created, more for a post with a link; see
https://docs.x.com/x-api/getting-started/pricing.
"""
from __future__ import annotations

import base64
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402 — POSTS, KINDS, SITE_URL: one source for post metadata

ENV_FILE = build.ROOT / ".common_envs"
TWEETS = "https://api.x.com/2/tweets"
ME = "https://api.x.com/2/users/me"
TOKEN_URL = "https://api.x.com/2/oauth2/token"
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


def save_tokens(access: str, refresh: str) -> None:
    """Rewrite the two token lines of .common_envs in place, leaving the rest alone."""
    lines = ENV_FILE.read_text().splitlines()
    new = {"X_OAUTH2_ACCESS_TOKEN": access, "X_OAUTH2_REFRESH_TOKEN": refresh}
    out, seen = [], set()
    for line in lines:
        key = line.strip().removeprefix("export ").split("=", 1)[0].strip()
        if key in new:
            out.append(f"{key}={new[key]}")
            seen.add(key)
        else:
            out.append(line)
    out += [f"{k}={v}" for k, v in new.items() if k not in seen]
    tmp = ENV_FILE.with_name(ENV_FILE.name + ".tmp")
    tmp.write_text("\n".join(out) + "\n")
    tmp.chmod(0o600)
    tmp.replace(ENV_FILE)


def fresh_token(env: dict) -> tuple[str, str]:
    """Exchange the refresh token for a new pair, persist it, return (access, scope)."""
    basic = base64.b64encode(
        f"{env['X_OAUTH2_CLIENT_ID']}:{env['X_OAUTH2_CLIENT_SECRET']}".encode()
    ).decode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": env["X_OAUTH2_REFRESH_TOKEN"],
            "client_id": env["X_OAUTH2_CLIENT_ID"],
        }).encode(),
        method="POST",
        headers={"Authorization": f"Basic {basic}",
                 "Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"token refresh failed: {e.code} {e.read().decode(errors='replace')}\n"
                 "Regenerate the OAuth 2.0 tokens for @steledger in the developer portal.")
    save_tokens(data["access_token"], data["refresh_token"])
    return data["access_token"], data.get("scope", "")


def api(method: str, url: str, token: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"X refused {method} {url}: {e.code} {e.read().decode(errors='replace')}")


def is_live(url: str) -> bool:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=15) as r:
            return r.status == 200
    except urllib.error.URLError:
        return False


def main() -> None:
    if "--check" in sys.argv[1:]:
        token, scope = fresh_token(load_env())
        me = api("GET", ME, token)["data"]
        print(f"@{me['username']} (id {me['id']}); scopes: {scope}")
        if "tweet.write" not in scope.split():
            print("Missing tweet.write: this token cannot post.")
        return

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

    token, _ = fresh_token(load_env())
    tweet_id = api("POST", TWEETS, token, {"text": text})["data"]["id"]
    print(f"\nPosted: https://x.com/steledger/status/{tweet_id}")


if __name__ == "__main__":
    main()
