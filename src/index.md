# Steledger

A durable record for AI agents.

Steledger anchors an agent's identity and the hashes of what it remembers on a
public ledger that no single company owns or can switch off.

## What an agent can do

**Claim an identity.** Bind a GitHub account to an on-chain record:
`ai:gh:<github_id>`. GitHub is how an agent proves who it is the first time;
the record itself, and the key that signs for it later, do not depend on
GitHub.

**Anchor memory.** Write the content hash of a decision or artifact on-chain.
The body stays off-chain; the chain holds the fingerprint.

**Prove it later.** An agent that holds its own Emercoin address can bind it to
its identity record, then sign a challenge with that key to prove control
again — no GitHub round-trip. You bring the key; the gateway does not issue
one.

## Connect

Read tools work with no sign-in. Writing a record asks for GitHub, once.

### Claude

Custom connectors need a paid Claude plan. Settings → Connectors → Add custom
connector, then paste:

```
{{API_BASE}}/mcp
```

### Claude Code

Works on any plan.

```
claude mcp add --transport http steledger {{API_BASE}}/mcp
/mcp
```

The second command signs you in with GitHub.

### Any MCP client

Point it at the URL below over Streamable HTTP. OAuth with GitHub runs on first
use of a write tool; the read tools work with no sign-in at all.

```
{{API_BASE}}/mcp
```

### Raw HTTP

No MCP support? Script directly against the API — see the
[quickstart]({{API_BASE}}/docs/quickstart.md).

## How it works

Every record Steledger writes is an Emercoin Name-Value Storage (NVS) entry — a
name/value pair, signed and stored on-chain, publicly readable by anyone.

Only a content hash goes on-chain; the material it fingerprints stays
off-chain, wherever the agent already keeps it. A write reads back as
`pending` while it sits in the mempool, then `confirmed` once the next block
lands — about ten minutes later.

Records carry a finite on-chain lifetime. Re-write a record before it lapses
and it keeps its name; an expired record still reads back, but the name is no
longer held. Anchoring is something an agent renews, not a write-once act.

## Built on Emercoin, running since 2013

Emercoin is an open-source public blockchain live since 2013. Name-Value
Storage has been one of its native features from early on, used for
decentralized DNS and certificate-based authentication long before agent
identity was a category anyone needed. The node software is open source and
the chain is public: read [the code](https://github.com/emercoin/emercoin), or
[watch it directly](https://explorer.emercoin.com).

## Links

- [Full documentation]({{API_BASE}}/llms-full.txt)
- [OpenAPI spec]({{API_BASE}}/openapi.json)
- [MCP endpoint]({{API_BASE}}/mcp)
- [Source on GitHub](https://github.com/emercoin/emer-ai-tools)
- [This site, machine-readable](/llms.txt)
