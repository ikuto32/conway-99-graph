# Conway 99-graph search: general progress v3

## Outcome boundary

No `srg(99,14,1,2)` witness was found.  In particular, no `submission.txt`
was created.  Every heuristic candidate mentioned below has 693 distinct
edges and degree 14 at all 99 vertices, but fails the common-neighbour test.

## Independently checked heuristic records

- Best unrestricted regular rooted candidate:
  `scratch_general_lns_v2_best.json`, energy 2042, 1,871 bad pairs,
  maximum absolute residual 2.
- Best candidate satisfying all 1,176 exact rooted BP incidence equations:
  `scratch_bp_linearized_v2_best.json`, energy 4268, inner--outer energy 0,
  2,262 bad pairs, maximum absolute residual 4.

The second record was reached by two new exact-BP move mechanisms.  A
balanced 4-by-4 block trade changes eight old and eight new outer edges while
preserving every BP row.  There are 2,121 balanced label-pair identities; the
4512-energy seed had eight available trades, and direct trade descent reached
4424.  A sequential CP-SAT LNS then minimized a linearization of the true
quadratic objective over BP-feasible moves of up to 24 deleted/added edges.
Every proposed point was rescored with the exact 99-vertex objective; this
reached 4268.  A 120-second full quadratic CP-SAT run in a 16-deletion
neighbourhood did not improve 4424, and later tabu runs did not improve 4268.

The diagnostic `scratch_bp_minmove_result.json` found a BP-preserving move
with eight deletions and eight additions (Hamming distance 16) in 0.42 s.  Its
120-second run did not prove minimality: overlap 496 was feasible while the
upper bound was 502.

## High-fibre-edge restrictions

Let `E0` be the number of outer edges whose endpoints have the same two-group
support.

- The fibre-compression calculation rigorously excludes
  `E0 in {81,82,83}` and leaves `E0 <= 80` or `E0=84`.
- The corrected exact `E0=80` computation exhausts 5 local orbits.  All five
  are UNSAT in CaDiCaL and independently INFEASIBLE in CP-SAT.  The corrected
  block inventory is 67 C4--C4 permutation blocks, 36 one-sided C4--P4
  blocks, and 2 fixed P4--P4 blocks.  This is computational elimination, not
  a proof-certificate result.
- The earlier E0=80 compact files imposed an invalid extra row-one condition
  on C4--P4 blocks.  They are prominently labelled `RESTRICTED_SUBCASE` and
  are not evidence for the full branch.
- The separate exact canonical all-C4 computation computationally eliminates
  `E0=84`.  Combining the two computational results with the analytic gap
  conditionally restricts a witness to `E0 <= 79`.

At `E0=79`, an independent exact compression audit enumerated all 53,109
labelled deficit placements as 59 S7 orbits.  Exactly 12 compression orbits
survive, and every survivor has sixteen C4 fibres and five P4 fibres.  This
classifies a necessary high-edge boundary case but does not eliminate it or
construct an 84-vertex lift.

## General exact SAT status

The unrestricted rooted CNF was safely refined without using an E0 bound.
The 17 live triangle parents become 98 exhaustive one-coordinate partner
orbits, of which 7 fail unit propagation.  Refining both coordinate partners
gives 559 exhaustive orbits: 114 fail propagation and 445 remain.  Each of
the 445 was explored to 500 conflicts and remained UNKNOWN.  Larger explicit
equality/full-AND and triangle encodings propagated more slowly and found no
SAT witness.

## Intermediate exact layer

A model containing BP plus all 126 same-support outer-pair equations was
tested independently in overlap-optimization and pure-satisfaction CP-SAT
modes for 120 seconds each.  Both terminated UNKNOWN with no feasible point;
this is not an infeasibility result.  A separate full-AND CaDiCaL CNF has
27,510 variables and 287,616 clauses.  Its exhaustive five safe local fibre
branches gave one propagation UNSAT branch (`a2_mixed`) and four UNKNOWN
branches after 60 seconds each.  Hence the independent cross-check agrees on
the status but does not settle this intermediate layer.

## Principal artifacts

- `scratch_general_e80_exact_summary.md`
- `scratch_general_e80_coverage_audit.json`
- `scratch_general_e80_corrected_sat_portfolio.json`
- `scratch_general_e80_corrected_cpsat.json`
- `scratch_general_e79_summary.md`
- `scratch_general_e79_compression_audit.json`
- `scratch_general_sat_v2_summary.md`
- `scratch_general_sat_v2_audit.json`
- `scratch_bp_trade_search.rs`
- `scratch_bp_linearized_lns.py`
- `scratch_bp_linearized_v2_best.json`
- `scratch_fibre_layer_project_cpsat.py`
- `scratch_fibre_layer_project_best.json`
- `scratch_fibre_layer_sat_result.json`
- `scratch_fibre_layer_sat_summary.md`
- `scratch_fibre_layer_sat_audit.json`
