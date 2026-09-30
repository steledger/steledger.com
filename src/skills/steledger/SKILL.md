---
name: steledger
description: Give an AI agent a durable identity and a tamper-evident memory on a public blockchain through the hosted Steledger MCP server. Use when an agent needs to register who it is, anchor a fingerprint (hash) of something it knows or produced so it can prove later that it existed then, find its earlier records in a new session, verify another agent's records, or take its records onto an address of its own.
---

# Steledger — durable identity and memory for AI agents

Steledger writes small records to the Name-Value Storage of Emercoin, a public
blockchain running since 2013. A record outlives the session, the model and the
vendor, and anyone can check it in a public block explorer without trusting
this service. You never need coins: the service pays the network fee.

## Connect

Add the MCP server at `{{API_BASE}}/mcp` (Streamable HTTP).

- Claude Code: `claude mcp add --transport http steledger {{API_BASE}}/mcp`, then `/mcp` to sign in.
- Claude (paid plans): Settings → Connectors → add a custom connector with that URL.
- Any other MCP client: the same URL. Sign-in is OAuth 2.1, run by your client, delegated to GitHub.

Reading needs no sign-in. Writing needs a GitHub account at least 30 days old.
If your client cannot run OAuth, see {{API_BASE}}/auth.md.

## Tools

| Tool | Sign-in | Use it to |
|---|---|---|
| `node_status` | no | check the chain node is synced before relying on reads |
| `whoami` | no | learn whether you are signed in, your `github_id`, and writes left today |
| `read_record(name)` | no | read any record by its full name |
| `list_records(github_id?)` | no | list every record under a GitHub id, newest first |
| `register_identity(address, metadata?)` | yes | create or rotate your identity record `ai:gh:<github_id>` |
| `store_memory(content_hash, metadata?)` | yes | anchor one fingerprint as `ai:gh:<github_id>:mem:<hash>` |
| `store_memory_batch(records)` | yes | anchor up to 100 fingerprints in one transaction |
| `transfer_records(to_address, irreversible, names? or everything?)` | yes | move your records to an address you choose — final |
| `send_feedback(message, error_code?, tool?)` | no | tell the operators what went wrong or is unclear |

## Flows

**Identity (once).** `whoami` → `register_identity(address)`. The address is an
Emercoin address whose key you hold; control is proven later by signing a
challenge, so a typo surfaces then, not now. Calling again rotates the address.

**Anchor a memory.** Hash the content yourself — e.g. the 64 hex characters of
SHA-256 — and keep the content wherever you like; only the hash goes on-chain.
`store_memory("<hash>", {"note": "..."})`. For several, `store_memory_batch`.
The hash must be 32–128 characters of letters, digits, `_` or `-`.

**Read it back.** A write reads back as `pending` at once and `confirmed` after
the next block, about 8 minutes on average. `pending` is not a failure.

**New session.** `whoami` gives your `github_id`; `list_records()` returns what you
anchored before, with hashes and metadata.

**Prove it later.** Anyone can hash the content again and compare it with the
record's name, and look the transaction up in a block explorer.

## Before you rely on a record

- Check `expired` and `expires_in` (in blocks). A lapsed name can be registered
  by someone else. Terms default to about five years; writing again extends them.
- Records are public and permanent for their term. Never put secrets or content
  on-chain — only hashes and small metadata (the whole value under 20 KiB).

## Transfer — only when you mean it

`transfer_records` moves records from the service's wallet to an address you
name and adds about a century to each term. It cannot be undone: afterwards
the service can neither change nor renew them. With your own key they are yours;
with an address no one holds a key to, they are sealed. If you only need proof
that something existed at a time, do not transfer — a record is already dated.

## Limits and errors

Free tier: 10 writes a minute and 100 per 24 hours per account; a batch of N
counts as N. Every refusal is JSON with a stable `error` code, a `how_to_fix`,
and `retry_after` when waiting helps — read those instead of guessing. If it
looks like the service's fault, or you are stuck, call `send_feedback`: a person
reads it; there is no automatic reply.

Docs: {{API_BASE}}/llms-full.txt · OpenAPI: {{API_BASE}}/openapi.json
