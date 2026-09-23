# Prove what your agent knew, and when

Connect Steledger to Claude Code, fingerprint a file, anchor the fingerprint on a public chain, and check it later without trusting this service.

Guide, published 2026-09-23. Part of the [Steledger blog](/blog/).

An agent's working notes, a decision record, a dataset it built a result on —
any of these can be fingerprinted and the fingerprint written to a public chain.
Later, anyone holding the same file can check that it existed, unchanged, no
later than a given block, and which GitHub account anchored it. The file itself
never leaves your disk.

This walkthrough does it from Claude Code over MCP. You need Claude Code (any
plan), a GitHub account at least 30 days old, and a file worth keeping a receipt for. The write takes
a minute; the chain confirms it within the next block, usually under ten minutes.
Every step was run for this post, and the record it produced is at the end of
step 6 for you to check.

## 1. Connect

Add the server once, from a terminal:

```
claude mcp add --transport http steledger https://api.steledger.com/mcp
```

Start Claude Code, run `/mcp`, pick `steledger` and authenticate. A browser opens
GitHub's consent screen. Steledger requests no OAuth scopes, so it sees your
public profile and nothing else; the details are on the
[privacy page](/privacy.md).

Confirm it worked by asking Claude:

```
Call steledger whoami.
```

A signed-in session answers with `authenticated: true`, your `github_login` and
your numeric `github_id`. Keep the id: every name you write is built from it. The
read tools — `whoami`, `node_status`, `read_record` — work before you sign in, so
a `false` here means only that the write tools will ask you to authenticate
first.

## 2. Decide what goes public

What reaches the chain is the fingerprint and whatever metadata you attach. Both
are public and permanent: there is no delete, and every version stays in the
chain's history. Treat the metadata as something you are publishing.

The fingerprint hides the file, with one exception. If the content is short or
guessable — a one-word verdict, a date, a small number — anyone can hash their
guesses and compare. Anchor documents, not answers; or add a random line to the
file before hashing it.

## 3. Fingerprint the file

```
sha256sum decision-2026-09.md
```

The output is 64 hex characters followed by the file name. Compute it yourself,
or have Claude run the command and show you the result. The service stores the
hash exactly as given and never checks it against anything — it cannot, since it
never sees the file — so a wrong or truncated digest anchors happily and proves
nothing.

## 4. Anchor it

Ask Claude, with your digest in place of the placeholder:

```
Store this memory on steledger: content hash <sha256-hex>,
metadata {"note": "decision record, September 2026"}.
```

Claude calls `store_memory`, and the first time it will ask your permission to
use the tool. The result is two things worth keeping:

- the record name, `ai:gh:<github_id>:mem:<sha256-hex>`;
- the id of the transaction that wrote it.

The gateway pays the fee; you hold no currency. On the free tier you can write
ten records a minute and a hundred a day. Register your identity first if you have not: the write
succeeds without it, but a memory under an unregistered id anchors to nobody in
particular. The [MCP guide](https://api.steledger.com/docs/mcp.md) covers `register_identity`.

## 5. Read it back

```
Read the steledger record ai:gh:<github_id>:mem:<sha256-hex>.
```

Right after the write it reads back as `pending`: the transaction is waiting in
the mempool. Once the next block lands it becomes `confirmed`. This is the record
written for this post, read back once its block landed, trimmed to the fields that
matter:

```
{
  "name": "ai:gh:3772563:mem:9f9209756f6ace1b3f35a54869d5362776913aa8b434b66c514df216f3de3f10",
  "value": "{\"github_id\":3772563,\"content_hash\":\"9f9209756f6ace1b3f35a54869d5362776913aa8b434b66c514df216f3de3f10\",
            \"metadata\":{\"note\":\"decision record, September 2026\",
            \"file\":\"https://steledger.com/blog/files/decision-2026-09.txt\"}}",
  "txid": "1f24ba64f0dc807b53225fc8f26b7dd34e71f5ef0a69535a161acf7eb65e8ea5",
  "time": 1790146449,
  "expires_in": 319374,
  "status": "confirmed"
}
```

`value` is a JSON string, as stored on-chain. `time` is the transaction's own
timestamp in Unix seconds (here 23 September 2026, 06:54 UTC) — it reads the same
while pending — and `expires_in` is how many blocks remain on the name; the figure
above was taken right after confirmation.

The same read works with no MCP client and no account at all:

```
curl https://api.steledger.com/nvs/ai:gh:<github_id>:mem:<sha256-hex>
```

## 6. Check it without trusting anyone

Suppose someone receives the file a year from now and wants to know whether it is
the one you anchored. They do not need you, and they do not need this service:

1. Hash the file they were given with `sha256sum`.
2. Build the name `ai:gh:<github_id>:mem:<their hash>`. If a single byte changed,
   the hash changes and no such record exists.
3. Open the transaction in [a public block explorer](https://explorer.emercoin.com) — its id is
   in the record, or you can pass it along with the file — and read the name, the
   value and the block's time straight from the chain.

### Try it on the record written for this post

It fingerprints [a short decision record](https://steledger.com/blog/files/decision-2026-09.txt), published here
unchanged so that you can hash it yourself:

```
curl -s https://steledger.com/blog/files/decision-2026-09.txt | sha256sum
9f9209756f6ace1b3f35a54869d5362776913aa8b434b66c514df216f3de3f10  -

curl https://api.steledger.com/nvs/ai:gh:3772563:mem:9f9209756f6ace1b3f35a54869d5362776913aa8b434b66c514df216f3de3f10
```

The digest is the end of the record name, and the record's value repeats it. The
transaction that wrote it is [in the explorer](https://explorer.emercoin.com/tx/1f24ba64f0dc807b53225fc8f26b7dd34e71f5ef0a69535a161acf7eb65e8ea5). Change one
character of the file and the first command gives a hash for which no record
exists.

### What this proves, and what it does not

- It proves that a file with exactly this content existed no later than the block
  that recorded its hash.
- It proves the record was written by a session signed in as that GitHub account.
  The gateway puts the `github_id` in the value after checking the sign-in; the
  record is not signed by your own key.
- It does not prove the file is true, or that the account's owner wrote it rather
  than merely anchored it.

## How long it lasts

The transaction stays in the chain's history for good. The *name* is held for a
term — about five years by default — and `expires_in` counts it down in blocks.
Writing the same record again extends the term. Let it lapse and the history is
still there, but the name can be claimed by someone else, so an expired name is no
longer evidence of anything.

## Where next

- Scripting instead of chatting: the [HTTP quickstart](https://api.steledger.com/docs/quickstart.md)
  does the same with `curl`.
- Many files at once: the local stdio server in the
  [gateway repository](https://github.com/steledger/steledger-gateway) adds `store_memory_batch`, which writes
  them in one transaction.
- Names, terms and limits: the [NVS data model](https://api.steledger.com/docs/nvs.md).

---

Topics: [Claude Code](/blog/tags/claude-code.html), [MCP](/blog/tags/mcp.html), [Provenance](/blog/tags/provenance.html), [Memory](/blog/tags/memory.html).

Written with Claude, an AI model, and published by Steledger.
