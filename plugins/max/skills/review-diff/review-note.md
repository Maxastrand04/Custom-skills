# Review note

Shared contract. The shape of the note `review-diff` leaves on the ticket PR, and the marker `pr-ticket` looks for when a ticket's effort level asks for a review.

## Finding it

The note's first line is always `## review-diff note`, exactly. A comment starting with that line is a review note, and no other comment starts with it. When a branch has more than one, the newest is the current one.

## Template

```md
## review-diff note

Ticket #<N>, branch `<branch>`, pre-review commit `<short hash>`

Suite: <green, 142 passed | none in repo, check each fix by hand>

**Drift**

| Spec line | Verdict | Change |
|---|---|---|
| refunds partial orders | fixed | refund path added, `src/refund.ts` |
| emails on every refund | amended | [amendment](<comment URL>) |

**Fixes**

| File | Issue | Fix |
|---|---|---|
| `src/pricing.ts:42` | duplicated code (6.4) | extracted `applyDiscount` |
| `src/order.ts:17` | ADR-0004, no DB in handlers | query moved to `OrderRepository` |

**Reconciled tests**

| Test | Cause | Change |
|---|---|---|
| `test_cart_items` | structure-sensitive | rewritten to `total()` |
| `test_refund_full` | drift fix | asserts partial refund |

**Records**

| Record | Action | Decision |
|---|---|---|
| ADR-0009 | written | repositories own SQL |
| ADR-0010 | found | no batching in `sync.ts` |
| ADR-0003 | amended | handlers may read config |

**Found, not fixed**

| File | Issue | Why |
|---|---|---|
| `src/tax.ts:60` | PCR-0002, no ORM imports | run `$max:challenge-pcr` |
| `src/cart.ts:12` | feature envy (6.4) | breaks `test_cart_total` |

Left untracked: `notes.txt`, `scratch.py`
```

## Rules

- **Findings only.** No hit, no row. A table with no rows becomes one line, `**Fixes** none`.
- **Cap every cell.** Middle column 6 words, last column 8. No sentences, no trailing periods. Truncate a deep path from the left, `.../handlers/order.ts:17`.
- **No suite.** The Suite line says so, and every row in Fixes and Drift is one the user should check by hand.
- **Amended drift** links its amendment note on the ticket PR instead of restating it.
- **Left untracked** names the files the user chose to leave out. Drop the line when there are none.
