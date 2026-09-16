# General exact SAT v2 report

## Outcome

No satisfying assignment was found.  No unrestricted branch was proved
UNSAT, and no `submission.txt` was created.  All solver results called
`UNKNOWN` below are conflict-budget terminations, never inferred UNSATs.

## Three independently auditable exact encodings

`scratch_general_sat_v2.py` builds the strongest direct encoding.  It uses
the same 3,486 outer-edge variables as the rooted reduction, but each of the
285,852 wedge helpers is a full Tseitin AND.  Every outer-pair equation is an
explicit equality: the at-most side uses a sequential counter and the
at-least-two side uses a linear exact prefix-threshold circuit.  It repeats
the following BP consequences as redundant constraints:

* outer degree 12, split into 2 exact-symbol and 10 exact-symbol-disjoint
  neighbours;
* degree 2 into each incident support group and degree 4 into each other
  support group;
* a same-fibre diagonal excludes all four square sides.

The resulting CNF has 1,554,294 variables and 4,299,582 clauses, SHA-256
`A8F13D204400C41D4724EC97EA98D84CA616939A9F878C42D5219553664E0A81`.

`scratch_general_sat_hybrid.py` isolates full-AND propagation while retaining
the baseline globally exact upper-bound argument.  It has 817,278 variables
and 2,194,374 clauses, SHA-256
`EB136D336F3894B946896DADC24A4706E804A33AB003ED55CAE65E81320B9D65`.

`scratch_general_sat_triangles.py` instead retains the lean baseline wedge
encoding and adds the exact outer-triangle decomposition.  It enumerates
35,560 possible pairwise exact-symbol-disjoint triples, forbids the other
59,724 triples, and links each of the 2,562 disjoint-label pairs to exactly
one triangle iff its edge is selected.  It has 956,956 variables and
2,136,988 clauses, SHA-256
`ADFB986AE53AFF930237997F23341CCAD5418FF702122F3D32BF5D8030293456`.

The audit in `scratch_general_sat_v2_audit.py/json` independently checks the
three DIMACS headers and hashes, exhaustively checks the custom threshold
circuit for input sizes 2 through 6, and recomputes all triangle counts.

## Propagation benchmark

On the same live branch `a0__w1_5` with 20,000 conflicts:

| encoding / solver | seconds | decisions | propagations | result |
|---|---:|---:|---:|---|
| baseline / CaDiCaL 1.9.5 | 15.547 | 257,179 | 27,507,104 | UNKNOWN |
| full-AND hybrid / CaDiCaL 1.9.5 | 51.437 | 353,628 | 81,483,167 | UNKNOWN |
| explicit-equality v2 / CaDiCaL 1.9.5 | 79.437 | 231,869 | 316,758,476 | UNKNOWN |
| baseline / CaDiCaL 3.0 | 12.375 | 490,242 | 29,693,374 | UNKNOWN |
| triangle decomposition / CaDiCaL 3.0 | 26.203 | 122,386 | 60,512,435 | UNKNOWN |

Thus all strengthenings reduce some decision counts but cost substantially
more propagation per conflict.  The explicit-equality v2 portfolio ran all
17 live normalized-triangle branches for 1,000 conflicts each; all remained
UNKNOWN (mean 7.835 seconds and about 28.8 million propagations per branch).
The exact records are in `scratch_general_sat_v2_portfolio.json`.

## Safe deeper symmetry decomposition

For each of the 17 live triangle branches, let `w` be the fixed third vertex.
BP makes the labels containing either exact symbol of `w` induce a perfect
matching, so the matching partner of `w` for a fixed symbol is unique.

`scratch_general_sat_deep_branches.py/json` fixes one such partner and
enumerates its orbits under the subgroup preserving the existing branch,
`w`, and that symbol.  This gives 98 exhaustive orbit branches.  Unit
propagation on the triangle CNF proves 7 UNSAT and leaves 91 live; coverage
and every representative are stored in
`scratch_general_sat_deep_screen.json`.

`scratch_general_sat_two_matchings.py/json` fixes both coordinate partners
simultaneously and allows their swap under the full residual stabilizer.  Its
121 labelled possibilities per parent collapse to 559 exhaustive orbit
branches.  Unit propagation proves 114 UNSAT and leaves 445 live.  The
per-parent split and propagated-literal counts are in
`scratch_general_sat_two_matchings_screen.json`.

Bounded follow-up results were:

* baseline exact CNF on the 91 one-partner branches, 2,000 conflicts each:
  all UNKNOWN (`scratch_general_sat_deep_portfolio.json`);
* triangle CNF on the same 91 branches, 1,000 conflicts each: all UNKNOWN
  (`scratch_general_sat_deep_triangles_portfolio.json`);
* persistent two-worker baseline portfolio on the 445 two-partner branches,
  first 100 and then 500 conflicts each: all UNKNOWN
  (`scratch_general_sat_two_matchings_portfolio.json` and
  `scratch_general_sat_two_matchings_portfolio_c500.json`).

The 500-conflict run took about 94 seconds wall time and 181 seconds summed
solve time.  It produced neither SAT nor an additional nontrivial UNSAT
branch.

## Structural-bound safety note

The rigorous fibre-compression result available during this work is
`E0 not in {81,82,83}`, equivalently `E0 <= 80 or E0 = 84`.  The `E0=84`
case is the separately tested all-C4 canonical class.  An early suggestion
to add unconditional `E0<=80` (and later `E0<=79`) was rejected after audit:
the first would silently depend on the certificate-free canonical
computation, and the second relied on an overconstrained E0=80 compact model.
Neither unsafe bound appears in these general CNFs.

## Reproduction entry points

* Build strongest CNF: `scratch_general_sat_v2.py --build`
* Run its 17-branch portfolio: `scratch_general_sat_v2.py --portfolio-conflicts N`
* Build triangle CNF: `scratch_general_sat_triangles.py --build`
* Recompute one-partner orbits/screen: `scratch_general_sat_deep_branches.py`
* Recompute two-partner orbits/screen: `scratch_general_sat_two_matchings.py`
* Run persistent deep portfolio: `scratch_general_sat_two_matchings_portfolio.py`
* Audit artifacts: `scratch_general_sat_v2_audit.py`
