# CONTEXT.md format

## Structure

```md
# {Context name}

{One or two sentences on what this context is and why it exists.}

## Language

**Order**:
{A short description of the term}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account

## Relationships

- An **Order** produces one or more **Invoices**
- An **Invoice** belongs to exactly one **Customer**

## Example dialogue

> **Dev:** "When a **Customer** places an **Order**, do we create the **Invoice** immediately?"
> **Domain expert:** "No. An **Invoice** is only generated once a **Fulfillment** is confirmed."

## Flagged ambiguities

- "account" was used to mean both **Customer** and **User**. Resolved: these are distinct concepts.
```

## Rules

- **Pick one word.** When several words exist for one concept, choose the best and list the others under _Avoid_.
- **Flag conflicts.** A term used two ways goes in Flagged ambiguities with its resolution.
- **Keep definitions tight.** Say what the term is, not what it does. One sentence when it fits.
- **Show relationships.** Bold the term names and give cardinality where it's obvious.
- **Only project terms.** General programming concepts such as timeouts, error types, or utility patterns stay out, however much the project uses them. Before adding a term, ask whether it is specific to this context.
- **Group under subheadings** when clusters emerge. A flat list is fine for one cohesive area.
- **Write an example dialogue** between a dev and a domain expert that shows the terms working together and where related concepts end.

## One context or several

Most repos have one `CONTEXT.md` at the root.

A repo with several contexts has a `CONTEXT-MAP.md` at the root instead, listing each context, where its file lives, and how the contexts relate:

```md
# Context map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md): receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md): generates invoices and processes payments

## Relationships

- **Ordering → Billing**: Ordering emits `OrderPlaced` events; Billing consumes them to generate invoices
```

Each context may also keep its own `docs/adr/` for decisions that bind only that context. Project-wide records stay in the root `docs/`.

How to tell which applies:

- `CONTEXT-MAP.md` exists: read it to find the contexts, and work out which one the topic belongs to. Ask if it isn't clear.
- Only a root `CONTEXT.md` exists: one context.
- Neither exists: create a root `CONTEXT.md` when the first term resolves.
