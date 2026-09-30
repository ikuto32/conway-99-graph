# Independent review plan for a fixed coordinate-support coloring model

This is preparation, not an encoding approval or authorization to launch a
solver. A future model must freeze the particular identity-cross core C,
binary coordinate support L, complete domain lists, selector map, exact CNF,
source versions and input hashes before independent review. A fixed L is an
additional construction restriction. Neither a Hadamard support nor this
coloring model covers all factors for its core.

## Raw contract needed from the producer

The scope artifact must contain the raw36x36 cubic adjacency (or an explicitly
mapped39x39 rooted core), literal M0/M1/M2 and P=I, and L12x60 with each
column weight6 and row weight30. M0 is standard and cross01/cross02 are
identity, as required by the existing independent raw-factor validator.
Any different labeling needs an explicit bijection, not an inferred one.

For each of60 columns, give its six coordinate labels in increasing order,
the full list of admissible six-row supports, and the selector ID for each.
One support chooses exactly one fibre per selected coordinate and exactly
two vertices in each fibre. Reject a support only if one of those within-
fibre pairs is an internal matching edge. There are90 possible balanced
colorings before that filter; their surviving count is to be computed, not
assumed. No bit, fibre or column symmetry normalization is implicit.

The model must give total variables/clauses, fresh-variable allocation and
the exact equation/gadget recipe. For each unordered core-row pair i<=j,
the diagonal or Gram equation is the sum of the selectors whose raw support
contains both rows, over all columns, equal to the literal prescribed Gram
entry. On the diagonal this is exactly the row-degree equation. There are
36+630=666 equations. All target-zero equations and empty sums require
explicit treatment. An independently reconstructed equation population must
include every unordered pair once.

For each pair of columns, every domain-choice pair with intersection above2
must be forbidden. This is a complete finite cross-domain population whose
size is determined by the frozen domain lengths. The audit will reconstruct
the shared-row count directly, not trust a producer overlap table. Identical
or repeated coordinate-support columns do not permit skipping a pair.

The complete native assignment remains a JSON object with `assignment` equal
to all signed IDs exactly once, accompanied by untouched native `v` lines.
The decoder should expose `factor`36x60 in the frozen column order,
`selected_domain_selector_ids`, `core_adjacency`, `coordinate_support`, and
`target_graph:false`. Optional canonical F and column maps are comparisons;
the independent checker will derive its own complete C0-pair bijection.

## Independent checking stages

1. Authenticate the raw core/support and all input gates. Independently
   enumerate each support-color domain using successive two-element subsets,
   compare every support and selector map, and check exact scope flags.
2. Reconstruct the666 literal integer Gram equations. Audit the actual
   cardinality clauses using the established separate truth-relation/threshold
   checking path after identifying the producer's chosen encoding. Prove the
   threshold recurrence and fresh-ID coverage. Compare every actual clause,
   complete one-hot constraints and every forbidden overlap pair.
3. Freeze a dedicated complete-object wrapper and fresh calibration for the
   actual variable/clause totals. Check every native/JSON ID and raw CNF
   clause before reconstructing F. Then independently check fixed L equality,
   all36x36 integer Gram entries, margins, all1770 column caps, mixed caps,
   and the partial99 matrix through the frozen raw-factor path. This is still
   not a complete graph, since D is absent.
4. Use the independently validated SRG243 fixture as a genuine nonempty
   generic raw-factor positive control. It is not a research99 witness. Any
   large assignment/codec positive remains explicitly synthetic unless an
   actual research SAT factor exists. Test missing/duplicate IDs, altered
   domain choices/supports, false clauses, wrong Gram and excessive overlaps.

`audit_20260930_fixed_support_raw_preparation.py` supplies only the reusable
raw support/domain checks and calibrated243 controls. Its preparation report
is deliberately not an encoding or SAT-run admission gate. No candidate
research CNF or mathematical exclusion is approved by it.

If SAT survives the complete checker, pass its independently reconstructed F
to the existing residual60 necessary screens and exact completion path.
UNSAT requires the exact full trace and independent replay, and would exclude
only this fixed support/core. Timeouts provide no such exclusion.
