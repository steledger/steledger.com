# Run a node for your agent

Transfer your agent's records to an address it holds, run the Emercoin node that holds the key, and update and sign for those records yourself. Every step run on the live network.

Guide, published 2026-10-07. Part of the [Steledger blog](/blog/).

By default the gateway holds your agent's records: it writes them, pays for
them, and is the only party that can change them. `transfer_records` hands them
to an address you choose, and from then on nobody but the holder of that
address's key can change them — the gateway included. This guide sets up the
other half: an Emercoin node of your own, holding that key, so the agent can
still update what it owns.

Every command below was run for this post, on a fresh machine, against the live
network, on 30 September 2026; the wallet encryption in step 2 was checked again
on 7 October. The records it produced are linked at the end.

## Do you need this?

Probably not, if all you want is proof that something existed at a given time.
A record the gateway holds is already dated and already public. Run a node when:

- the agent must **update** a record it owns — an identity whose value changes,
  a pointer that moves;
- the agent must **prove control** of its records by signing with their key;
- you want no service in the path at all, not even for reads.

A record you transfer and never touch again needs no node: a transfer adds about
a century to its term, so it does not need renewing either.

## What it costs

- **Disk:** about 1.2 GB for the whole chain, growing slowly. There is no pruned
  mode.
- **Time:** our fresh sync, genesis to the tip, took 20 minutes on a fast
  workstation with a good connection; expect up to an hour and a half on a
  smaller machine. The node pulled blocks from peers on the public internet and
  found them on its own.
- **Fees:** each change to a record is a transaction with a network fee, paid in
  EMC from the node's wallet. In our run a value update cost **0.0002 EMC**.
  Extending a term costs more, growing with the square root of the days added:
  a few thousandths of an EMC even for a century.

A node that has never held EMC cannot pay those fees. If yours has none, ask for
network-fee funds when you transfer (step 3): the gateway then sends 0.01 EMC to
the same address, once per GitHub account.

## 1. Start the node

The official image is `emercoin/core` on Docker Hub. Give it a small
configuration with RPC bound to the container's loopback, so the wallet is
reachable only through `docker exec`:

```
mkdir -p ~/emercoin
cat > ~/emercoin/emercoin.conf <<'EOF'
server=1
rpcbind=127.0.0.1
rpcallowip=127.0.0.1
rpcuser=agent
rpcpassword=<a long random string>
txindex=1
EOF

docker volume create emercoin-data
docker run -d --name emercoin --restart unless-stopped \
  -v emercoin-data:/srv/emercoind \
  -v ~/emercoin/emercoin.conf:/srv/emercoind/emercoin.conf:ro \
  emercoin/core:0.8.5

alias emc='docker exec emercoin emercoin-cli -datadir=/srv/emercoind'
```

`txindex=1` keeps an index of every transaction, which name lookups rely on.
Nothing is published to the host: the node makes outbound connections only. If
you want to help the network, publish the peer port with `-p 6661:6661`.

Watch it sync:

```
emc getblockchaininfo
```

It is done when `blocks` equals `headers` and `initialblockdownload` is `false`.
Nothing that follows works reliably before that.

## 2. Make an address and back up its key

```
emc getnewaddress
em1qp4mcgztr8zqlw062mgesnyu3w53hqq47nu38mw
```

The wallet is created on first start and is **not encrypted**. Before anything
of value lands in it:

```
emc encryptwallet "<passphrase>"
emc backupwallet /srv/emercoind/wallet-backup.dat
docker cp emercoin:/srv/emercoind/wallet-backup.dat .
```

Encrypt first, then back up: encrypting generates a new HD seed, so a backup
taken before it does not cover addresses made after. Keep the backup and the
passphrase apart, off this machine. From now on the wallet is locked; unlock it
for a minute before each write or signature with
`emc walletpassphrase "<passphrase>" 60`, or the node answers
`Please enter the wallet passphrase with walletpassphrase first`.
Lose the key and the records it holds
cannot be changed or renewed by anyone until their term ends. There is no
recovery, and the gateway cannot help: it no longer holds them.

## 3. Transfer the records to it

From your MCP client, signed in, ask the agent:

```
Transfer ai:gh:<github_id>:mem:<hash> to em1q… with steledger.
Set irreversible to true.
```

The agent calls `transfer_records`. To move the identity and every memory at
once, it passes `everything: true` instead of names. If the node's wallet is
empty, add `fee_grant: true`: 0.01 EMC for network fees then goes to the same
address in a separate transaction — enough for about fifty value updates. It is
given once per account, within a daily budget, and refused before anything moves
if it is not available, so you can decide to transfer without it. Over HTTP the same call is
`POST https://api.steledger.com/nvs/transfer`. The transfer is one transaction; once its
block confirms, the node sees the names as its own:

```
emc name_show ai:gh:<github_id>:mem:<hash>
```

`address` in the answer is your address. The name's own output carries 0.0001
EMC with it; that amount belongs to the name and is not spendable as a fee.

## 4. Update a record

A record's value is JSON written by the gateway. Keep its shape, change what you
need, and pass the **current address and an empty string** after the days:

```
emc name_update ai:gh:<github_id>:mem:<hash> '<new value>' 0 em1q… ""
```

- `0` days changes the value without extending the term. A positive number adds
  that many days.
- The address matters. Leave it out and the wallet moves the name to a fresh
  address of its own. The name stays yours, but it no longer sits where you
  said it would, and a signature from the old address stops matching the record.
- The empty string is the value type. Always pass it explicitly: anything else
  is read by the node as a file path, and that file's contents are written
  on-chain.

The command returns a transaction id. The gateway reads your update like any
other: `https://api.steledger.com/nvs/<name>` shows it under `pending_update` at once and as
the record itself after the next block.

### If the wallet is empty

With nothing spendable, the node refuses the update with a message that does not
say why:

```
error code: -32603
error message:
unkown error
```

(Spelled that way by the node.) Check `emc getbalances` before you suspect
anything else.

## 5. Prove it is yours

Sign any message with the address that holds the record:

```
emc signmessage em1q… "I hold ai:gh:<github_id>:mem:<hash>"
```

Anyone can check the signature against the address in the record, with their
own node or any Emercoin wallet:

```
emc verifymessage em1q… "<signature>" "I hold ai:gh:<github_id>:mem:<hash>"
true
```

This is the proof the gateway cannot give while it holds a record: it shows
control of the key, not just the GitHub account that wrote it.

## The records written for this post

`ai:gh:3772563:mem:aae0dfa2109894288bd5dc1765d29163ae9d0bf1f58e25f7dc91f0a552c002e7`
was stored through the gateway, transferred to a fresh node's address, and
updated twice from that node — once without an address, which moved it, and once
with one, which kept it. Read it at
[https://api.steledger.com/nvs/ai:gh:3772563:mem:aae0dfa2…](https://api.steledger.com/nvs/ai:gh:3772563:mem:aae0dfa2109894288bd5dc1765d29163ae9d0bf1f58e25f7dc91f0a552c002e7),
or follow its transactions in [a public block explorer](https://explorer.emercoin.com).

A second record,
`ai:gh:3772563:mem:f92717b71a238de591566fdfb3cdf141946d94410da91f586ebea5b524723747`,
went the way this guide suggests for an empty wallet: transferred with
`fee_grant: true`, which sent 0.01 EMC to the same address, then updated from the
node with nothing but those funds — 0.0002 EMC in fees, the name kept on its
address. Read it at
[https://api.steledger.com/nvs/ai:gh:3772563:mem:f92717b7…](https://api.steledger.com/nvs/ai:gh:3772563:mem:f92717b71a238de591566fdfb3cdf141946d94410da91f586ebea5b524723747).

## Where next

- What transfer does and does not change: the
  [MCP guide](https://api.steledger.com/docs/mcp.md).
- Names, terms and fees: the [NVS data model](https://api.steledger.com/docs/nvs.md).
- The node's source: [emercoin/emercoin](https://github.com/emercoin/emercoin).

---

Topics: [Identity](/blog/tags/identity.html), [Trust](/blog/tags/trust.html), [MCP](/blog/tags/mcp.html).

Written with Claude, an AI model, and published by Steledger.
