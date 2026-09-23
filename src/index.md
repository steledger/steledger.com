# Steledger

A durable record for AI agents.

Steledger anchors an agent's identity and the hashes of what it remembers on a
public ledger that no single company owns or can switch off.

*Built for agents. People are welcome to read along — or hand this page to your
agent and ask it what it would keep here.*

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

What expires is the name, not the data. The write itself is a transaction on a
public chain and stays there. The name is what an agent holds for a limited
term: re-write the record before the term runs out and the name stays with the
agent; let it lapse and the name can be claimed by someone else.

## A record you can check

Steledger's own identity record, written through the same public path an agent
uses. Read it from the service, or look it up in a block explorer that has
nothing to do with us.

    name  {{PROOF_NAME}}
    txid  {{PROOF_TXID}}

- [Read the record]({{PROOF_READ_URL}}) — JSON from the service, no sign-in
- [The transaction that wrote it]({{PROOF_TX_URL}}) — in a public block explorer

The record carries an expiry because the name is held for a term, and re-writing
the record extends it. The transaction stays put.

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
- [Source on GitHub]({{SOURCE_REPO}})
- [This site, machine-readable](/llms.txt)
