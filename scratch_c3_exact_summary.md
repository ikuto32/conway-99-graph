# Exact fixed-point-free `C3` branch experiment

## Scope and exhaustive branch reduction

This is conditional on an `srg(99,14,1,2)` admitting a fixed-point-free
automorphism of order three.  Its 99 vertices then form 33 three-cycles.

If `t` of those cycles induce `K3`, the trace calculation gives
`t in {6,13,20,27}`.  The graph has `693/3 = 231` triangles.  A triangle
fixed setwise by the automorphism is exactly one of the `K3` vertex orbits;
all other triangles have orbit length three.  Hence `t = 0 mod 3`, leaving
the exhaustive values `t=6` and `t=27`.

For `t=27`, the multiplicity-two blocks form a simple 2-regular graph on the
six non-`K3` orbits.  Its exhaustive isomorphism types are `C6` and `2C3`.
Thus the three exact SAT branches are:

* `t6` (unrestricted 2-factor on 27 non-`K3` orbits),
* `t27_c6`, and
* `t27_2c3`.

## Exact encoding

The 1,617 primary variables are the `C3`-orbits of graph edges.  There are
528 quotient support variables and either 351 (`t=6`) or 15 (`t=27`)
double-block variables.  The encoding includes:

* exact support degree 12;
* exact double degree 2 at every non-`K3` orbit;
* all 528 off-diagonal equations of `M^2+M=12I+6J` as propagation-strong
  equalities in the `strong` artifacts;
* all 1,617 phase-level pair-orbit constraints
  `common(u,v)+adjacent(u,v) <= 2`.

The last constraints are collectively exact.  Quotient row constraints
force all 99 graph degrees to be 14, and therefore their left sides sum to

`99*C(14,2) + 99*14/2 = 9702 = 2*C(99,2)`.

Hence a SAT assignment would expand to the requested SRG.  The code also
expands and independently checks any SAT assignment before writing a witness
JSON.  It never writes `submission.txt`.

## Safe symmetry audit

Orbit 0 is a `K3`.  It meets exactly 12 other vertex orbits in simple
perfect matchings.  Independent phase rotations make every occupied matching
phase-preserving.

For `t=6`, orbit-0 support is prefix-sorted separately inside the freely
permutable `K3` and non-`K3` classes.

For `t=27`, the double-graph shape is fixed first.  **The six non-`K3`
support bits are not prefix-sorted under the full `S6`, which would be
unsafe.**  Instead, all 64 binary support words are reduced under the actual
automorphism group of the fixed shape:

* `Aut(C6)` has order 12 and 13 binary-word orbits;
* `Aut(2C3)` has order 72 and 10 binary-word orbits.

The encoding allows exactly one lexicographically least word from every one
of those orbits.  The remaining 26 `K3` support bits may still be safely
prefix-sorted.

The earlier CP-SAT `2C3` run used conflicting full-class prefix sorting and
is therefore **not** independent confirmation.  Only the safe CNF result
below should be used.

Repeated literals represent small positive weights in sequential counters.
`scratch_c3_exact_card_audit.py` exhaustively checked 9,570 counter instances
and 281,480 fixed input assignments for both equality and upper-bound
semantics; all passed.

## CaDiCaL 1.9.5 results

| branch | variables | clauses | bounded result |
|---|---:|---:|---|
| `t6` | 1,070,361 | 2,187,973 | `UNKNOWN` after 60 s |
| `t27_c6` | 695,490 | 1,408,409 | `UNKNOWN` after 60 s |
| `t27_2c3` | 695,490 | 1,408,412 | `UNSAT` in 1.515 solver s; 1,924 conflicts |

DIMACS line counts were audited as header plus exactly the listed number of
clauses.  No SAT witness was found.  The `2C3` result is a reproducible
computational UNSAT result, but no DRAT/LRAT proof certificate was produced;
it should not be presented as a formal machine-checkable nonexistence proof.

## SHA-256

* `scratch_c3_exact_sat.py`:
  `24D74E905C908A968AFDCF8D53516CB6CEEF0FC0FD5C8A84F7AAEC3247155D23`
* `scratch_c3_exact_card_audit.py`:
  `78CD0280FCEA4589628E69619C47273F8A88E2341E46077856E689DE3717A1A4`
* `scratch_c3_exact_card_audit.json`:
  `3FDF8847958DE96530A6BE59D40931BEE9DD7D90739B280B3EEB20F0BCA562B8`
* `scratch_c3_exact_strong_t6.cnf`:
  `0AFFE63C95B748FF11FDEEBBA494EA7FE4F692423939F44C0066A083E6D4671E`
* `scratch_c3_exact_strong_t27_c6.cnf`:
  `49B289CA31A9DE5F92407D0D4FC14B1AD482DF25201F8F13CBFBC5AB3505F927`
* `scratch_c3_exact_strong_t27_2c3.cnf`:
  `F3AD2D452BF8A6B0F5D51C522CECBFAFC6403057FE426CD120C18E3F2EF05CE0`

