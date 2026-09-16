# Independent fixed-local exact SAT portfolio for `E0=76`

## Outcome

All 311 exhaustive local representatives are computationally UNSAT in an
independently rebuilt fixed-local CaDiCaL model.  The final counts are:

```
UNSAT  = 311
SAT    = 0
UNKNOWN= 0
```

No UNSAT proof certificates were emitted, so this is a finite-computational
elimination of `E0=76`, not a formally certified theorem.

## Exhaustive branch catalog

[`scratch_e76_fixed_exact_catalog.json`](scratch_e76_fixed_exact_catalog.json)
maps branches `0..310` bijectively to the 311 explicit canonical local graphs
in `scratch_e76_independent_local.json`.  Their local orbit-size weights sum
to all 68,864 labelled survivors on the ten support branches.  Each source
representative occurs exactly once.

## Independent exact model

[`scratch_e76_fixed_exact_sat.py`](scratch_e76_fixed_exact_sat.py) rebuilds a
fresh CNF from the explicit local constants for every branch.  It does not
read or import the separate shared/incremental E76 implementation.  Every
branch has:

- all 105 disjoint-support blocks and all 1,680 associated edge variables;
- 65,520 exact Boolean conjunction variables;
- all 1,176 `BP=PA0` equalities;
- all 3,486 outer-pair common-neighbour equalities;
- the ordinary-`C4` exact-one block constraints, applied on two sides only
  for ordinary--ordinary blocks and one side for ordinary--exceptional
  blocks;
- no redundant support-aggregate rows.

Depending on fixed constants, the sequential-cardinality CNFs contain
279,948--281,456 variables and 651,740--655,088 clauses.  A SAT response would
be expanded to all 99 vertices and independently verified before being
accepted.  No SAT response occurred.

## Bounded portfolio

Every result was checkpointed immediately in
[`scratch_e76_fixed_exact_checkpoint.json`](scratch_e76_fixed_exact_checkpoint.json).

The first pass used 20,000 conflicts per branch, four workers, and a
15-second four-branch batch limit:

```
UNSAT   188
UNKNOWN 123
SAT       0
```

All 123 UNKNOWN results were conflict-budget terminations, not wall-time
terminations.  The second pass retried exactly those branches with 200,000
conflicts and a 60-second batch limit; all 123 returned UNSAT.  Thus 188
branches have one attempt and 123 have two, for 434 recorded attempts.  The
largest successful solve used 122,809 conflicts and 47.125 seconds.

| partition/support orbit | branches | labelled local graphs | first-pass UNSAT | first-pass UNKNOWN | final UNSAT |
|---|---:|---:|---:|---:|---:|
| `2+2+2+2`, 1 | 58 | 1,792 | 53 | 5 | 58 |
| `2+2+1+1+1+1`, 20 | 52 | 2,048 | 45 | 7 | 52 |
| `2+1+1+1+1+1+1`, 6 | 16 | 768 | 10 | 6 | 16 |
| `2+1+1+1+1+1+1`, 87 | 6 | 768 | 2 | 4 | 6 |
| `1^8`, 1 | 40 | 8,192 | 28 | 12 | 40 |
| `1^8`, 13 | 74 | 43,008 | 18 | 56 | 74 |
| `1^8`, 15 | 12 | 1,024 | 6 | 6 | 12 |
| `1^8`, 20 | 28 | 8,192 | 8 | 20 | 28 |
| `1^8`, 88 | 13 | 1,024 | 6 | 7 | 13 |
| `1^8`, 89 | 12 | 2,048 | 12 | 0 | 12 |
| **total** | **311** | **68,864** | **188** | **123** | **311** |

The last invocation log is
[`scratch_e76_fixed_exact_portfolio.json`](scratch_e76_fixed_exact_portfolio.json);
the checkpoint is authoritative for both attempts.

## Independent audit and claim boundary

[`scratch_e76_fixed_exact_audit.py`](scratch_e76_fixed_exact_audit.py)
independently re-joins the local source, catalog, checkpoint, and latest
portfolio.  It verifies:

- complete branch indices `0..310` and exact 68,864-orbit-weight coverage;
- one attempt on 188 branches and two attempts on the other 123;
- every first-pass UNKNOWN followed by a second-pass UNSAT;
- `SAT=UNKNOWN=0` in the latest state;
- all model counts and the safe ordinary-`C4` block rule on every branch;
- absence of purported solution files.

[`scratch_e76_fixed_exact_audit.json`](scratch_e76_fixed_exact_audit.json)
has `"ok": true`.  This eliminates the `E0=76` branch only conditional on
the finite compression/local enumeration and the solver computations.  It
does not provide a proof certificate for the 311 UNSAT conclusions and does
not construct an `srg(99,14,1,2)`.

