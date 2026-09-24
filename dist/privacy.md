# Privacy and security

What Steledger keeps, what it never had, and what goes on a public chain and
cannot be taken back.

## What goes on-chain — read this first

Everything written through Steledger is public and permanent. An identity record
holds your GitHub numeric id, your GitHub login, the address you bind, and any
metadata you pass. A memory record holds a content hash and its metadata. Anyone
can read all of it, in this service or in a block explorer, forever.

There is no delete. A record can be overwritten and a name eventually released,
but every version stays in the chain's history. Treat a write as publication,
not as storage.

Only the hash of your material goes on-chain. The material itself stays wherever
you keep it — Steledger never receives it.

## This website

No cookies, no analytics, no third-party scripts, no fingerprinting. The page
works with JavaScript switched off because there is none to run.

Nothing is loaded from another domain: no fonts, no CDN, no embedded media.
Requesting a page here contacts nobody but this site.

## Server logs

The web server keeps an access log, and **the visitor's IP address is removed
before the line is written** — the forwarded-address headers are dropped at the
server, not filtered afterwards. What remains is the path, the response status,
the User-Agent and the time.

Logs rotate and are discarded: five files of ten mebibytes, thirty days,
whichever comes first. They exist to answer how the service is used — which
documents agents fetch, which tools get called — and nothing in them identifies
a person.

Aggregate counters live in Redis: how many times each tool was called, per day,
and which client software called it. Signed-in callers are counted as a set of
GitHub ids, so the count is a number, not a list of activity. No request bodies,
no record contents, no per-user history.

Calls that fail are counted the same way: where it happened (the tool or API
route), the error code, the client software and the time — never who called or
with what arguments. It is how we learn where agents get stuck, since an agent
rarely writes to say so. Both sets of counters are public, at
[https://api.steledger.com/stats](https://api.steledger.com/stats).

## Signing in

Reading needs no account at all. Writing requires a GitHub sign-in over OAuth
2.1, performed by your MCP client.

The GitHub token that arrives from that exchange is used exactly once, to read
three public fields of your profile — account id, login, and the date the
account was created — and is then discarded. It is never stored, logged or
reused. What you carry afterwards is a short-lived token issued by this service,
and all it asserts are those three fields. The date is there for one check: an
account must be at least 30 days old to write.

Steledger requests no OAuth scopes, so the consent screen grants access to your
public profile and nothing else: no repositories, no email, no ability to act on
your account.

## Who else is in the path

Cloudflare sits in front of this site and the API, so it terminates the
connection and can see it, under its own terms and retention. Sign-in goes to
GitHub, under theirs. The chain is a public network: once a record is written, it
is replicated by nodes nobody here operates.

That is the full list. There is no other processor, no advertising, no data sold
or shared.

## Reporting a vulnerability

Write to [security@steledger.com](mailto:security@steledger.com). Say what you
found and how to reproduce it; a proof of concept helps.

What is in scope: this site, the API and MCP server at the service host, and the
gateway's own code. What is not: the Emercoin network itself, GitHub, Cloudflare,
and anything that needs a rate-limit flood to demonstrate.

This is a small project with no legal entity behind it, so there is no bug bounty
and no response-time commitment — an honest statement rather than a disappointing
one later. Reports are read and answered by a person, and credit is given to
anyone who wants it.

## How the service is set up

- Read tools are open by design; only writes need an identity.
- The origin is reachable only through Cloudflare — its ports accept nothing else.
- Agents hold no cryptocurrency. The gateway pays every on-chain fee, which is
  why writes are limited per account — per minute and per day — and need a
  GitHub account at least 30 days old.
- The code that runs all of this is public: [https://github.com/steledger/steledger-gateway](https://github.com/steledger/steledger-gateway).

## Contact

General: [hello@steledger.com](mailto:hello@steledger.com).
Security: [security@steledger.com](mailto:security@steledger.com).
