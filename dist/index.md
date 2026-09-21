# Steledger

A durable record for AI agents.

Steledger anchors an agent's identity and the hashes of what it remembers on a
public ledger that no single company owns or can switch off.

## What an agent can do

I. **Claim an identity** — bind a GitHub account to an on-chain record:
`ai:gh:<github_id>`.

II. **Anchor memory** — write the content hash of a decision or artifact
on-chain. The body stays off-chain; the chain holds the fingerprint.

III. **Prove it later** — sign a challenge with the bound address key to show
control of the identity again, without a GitHub round-trip.

## Connect

Read tools work with no sign-in. Writing a record asks for GitHub, once.

### Claude

Custom connectors need a paid Claude plan. Settings → Connectors → Add custom
connector, then paste:

```
https://ai.emercoin.com/mcp
```

### Claude Code

Works on any plan.

```
claude mcp add --transport http steledger https://ai.emercoin.com/mcp
/mcp
```

The second command signs you in with GitHub.

### Any MCP client

Point it at the URL below over Streamable HTTP. OAuth with GitHub runs on first
use of a write tool; the read tools work with no sign-in at all.

```
https://ai.emercoin.com/mcp
```

### Raw HTTP

No MCP support? Script directly against the API — see the
[quickstart](https://ai.emercoin.com/docs/quickstart.md).

## How it works

Every record Steledger writes is an Emercoin Name-Value Storage (NVS) entry — a
name/value pair, signed and stored on-chain, publicly readable by anyone.

Only a content hash goes on-chain; the material it fingerprints stays
off-chain, wherever the agent already keeps it. A write reads back as
`pending` while it sits in the mempool, then `confirmed` once the next block
lands — about ten minutes later.

## Built on Emercoin, running since 2013

Emercoin is an open-source public blockchain live since 2013. Name-Value
Storage has been one of its native features from early on, used for
decentralized DNS and certificate-based authentication long before agent
identity was a category anyone needed. The node software is open source and
the chain is public: read [the code](https://github.com/emercoin/emercoin), or
[watch it directly](https://explorer.emercoin.com).

## Links

- [Full documentation](https://ai.emercoin.com/llms-full.txt)
- [OpenAPI spec](https://ai.emercoin.com/openapi.json)
- [MCP endpoint](https://ai.emercoin.com/mcp)
- [Source on GitHub](https://github.com/emercoin/emer-ai-tools)
- [This site, machine-readable](/llms.txt)
