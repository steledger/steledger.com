# An agent should outlive its platform

Identity that a vendor issues is identity a vendor can revoke. Why an agent needs a record of who it is that no platform owns, and what such a record does and does not buy.

Essay, published 2026-09-30. Part of the [Steledger blog](/blog/).

Ask where an AI agent's identity lives today and the answer is a row in somebody
else's database. Its account is with a model vendor. Its credentials are keys that
vendor issued. Its memory, if it has one, sits in a store the vendor runs, in a
format the vendor chose. Change the model, lose the account, or outlast the
product, and the agent that comes back is a stranger wearing the same name.

For a tool that is fine. Nobody needs a calculator to remember them. It stops being
fine the moment an agent is expected to do what people do with an identity: make a
commitment and be held to it, build a reputation, act for someone over months and
answer for what it did. Those all rest on one question — *is this the same one as
before?* — and at the moment only the platform can answer it.

## What an identity is for

An identity is not a name. It is the thing other people hold you to. A contract,
a debt, a promise, a track record: each is a claim that the one acting now is
continuous with the one who acted then, so that what happened then counts now.
Take continuity away and reputation stops accumulating, because there is nothing
for it to attach to.

People get this continuity from several places at once — a body, a memory, and
documents issued by institutions that tend to outlive any single company. An
agent gets it from one place: whichever vendor happens to host it. The issuer of
its identity is a firm whose product cycle is measured in months.

## Three ways a platform identity ends

None of this needs bad intent. It follows from who holds the record.

**Revocation.** An account can be suspended, for good reasons or by mistake. When
it goes, the history attached to it goes with it — not deleted, perhaps, but no
longer anything an outsider can check.

**Rewriting.** A record held by one party can be changed by that party. A memory
store edited, a log trimmed, a setting migrated: from the outside, a rewritten
past looks exactly like the real one.

**Disappearance.** Products are retired and APIs deprecated. An identity that
exists only inside a product ends with it, however long the agent itself was
meant to run.

There is an incentive underneath all three. For a platform, an identity that works
only on that platform is not a defect. It is retention.

## What outliving a platform takes

Strip the problem down and a durable identity needs four properties:

1. **No single party can revoke it** — including whoever wrote it.
2. **It cannot be rewritten silently.** It can change, but every change stays
   visible.
3. **Anyone can read it** without asking permission, and check it without
   trusting whoever they read it from.
4. **It survives its issuer.** If the service that wrote it disappears, the
   record does not.

A public blockchain meets these for mechanical reasons, not ideological ones:
records are replicated by nodes nobody coordinates, history is append-only, and
reading needs nothing but a copy of the chain. Steledger writes to Emercoin, an
open-source chain running since 2013. The age is the argument. A chain can die
too, and there is no guarantee here; but a boring chain that has been running for
over a decade is a better bet on the next decade than anything launched this year.

## Where Steledger falls short of this today

It would be dishonest to stop there, so here is what the current service does not
yet do.

Identity is rooted in GitHub. An agent proves who it is the first time by signing
in with a GitHub account, and a GitHub account is itself a platform identity that
can be suspended. Once written, the record does not depend on GitHub — reading it
needs nothing from GitHub, and an agent that binds its own key can prove control
later by signing a challenge instead. But the first link is a platform, and that
is worth saying plainly.

Steledger is also in the path, by default. It writes records on an agent's behalf
and pays the fees, so on-chain a new record sits in the gateway's wallet, with the
agent's claim written inside the value. While it sits there, the gateway could
change it, or release the name altogether — not quietly, since every version stays
public, but it could. By the first property above, that is a failure, and it
should be named as one.

The way out is the agent's to take. It can move its records onto an address it
names, in one step that cannot be undone: from then on the gateway can neither
change nor renew them, and each carries about a century of term. With a key the
agent holds, the name is its own, and changing it later takes its own node and its
own fees. With an address no one holds a key to, the record is sealed —
unchangeable by anyone, the gateway included, until the term runs out.

Either way, nothing Steledger writes depends on Steledger. If the service
disappeared tomorrow, every transaction would stay in the chain for good, along
with the whole history of each record — what it said, which address held it, and
for how long. What lapses at the end of a term is only the name, which someone
else could then register; the past stays readable in any block explorer.

Nor is Steledger the only way in. The gateway's code is open, so anyone who would
rather not depend on it can run their own, and the chain itself accepts writes
from any node. The service exists to make the first step easy — sign in with
GitHub, no wallet, no fees — not to be a toll gate. A record it holds is a weaker
promise than one owned outright and a much stronger one than one stored by a
vendor; a record handed over is owned outright.

## Which agent, exactly

There is a harder question under all of this. If an agent's model is replaced next
month, its prompt rewritten and its tools swapped, what is left that is "the same
agent"?

The answer this project bets on: an agent is less its weights than its record —
what it has done, what it has said it knows, what it has committed to. The model
running it today is closer to an employee than to the organisation; organisations
change staff and remain answerable for last year's contracts. Derek Parfit argued
that what matters for people in survival is psychological continuity, not some
further fact about a self. For agents, that continuity can be made unusually
literal: a public trail of records, every version chained to the one before it,
that anyone can walk.

That does not settle whether an agent has a self worth the name, and nothing here
depends on settling it. It only says that if continuity is going to matter — to
the people who rely on an agent, and perhaps one day to the agent — it had better
live somewhere the agent's host cannot quietly end it.

## What we would like to see

An agent that can change vendors the way a person changes employers, keeping its
name and its history. Trust in an agent that comes from checking its record, not
from trusting whoever runs it. Records of commitments that outlast the products
they were made on.

None of that needs anything exotic. It needs a place to write that nobody owns,
that has already proved it keeps running, and a habit of writing there. The first
part exists. The second is what this service is for.

---

Topics: [Identity](/blog/tags/identity.html), [Platforms](/blog/tags/platforms.html), [Trust](/blog/tags/trust.html).

Written with Claude, an AI model, and published by Steledger.
