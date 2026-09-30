# Universal scalar upper-envelope inventory, version1

Inventory only; do not materialize a new CNF or run a solver. Freeze this spec,
source and derivation before executing the bounded experiment. Use locked/offline
uv, standard-library integer arithmetic, at most120 cooperative seconds and
256 MiB planning memory. Any failure is preserved in a fresh output directory.

Selection is all60 unordered nonmatching coordinate pairs and all9 ordered fibre
pairs on the frozen literal six-prism Hadamard support:540 cells, each with its
complete5 incident support groups. Derive target K=1 for equal fibres and2 for
distinct fibres directly from the raw36-vertex core/Gram, not only from that rule.
The elementary upper bound is the sum over groups of min(two incident counts).
Every factor must make that upper bound at least K. This is a necessary bound,
not equality with the exact local-class maximum and not simultaneous Gram
realizability. The prior refuted Frechet equality must not be reinstated.

Deterministic hypothetical extension recipe, with no constant or channel merging:

* Allocate six threshold variables for each of120 count channels, ordered by
  coordinate, group, fibre, threshold1 then2. Each equals the OR of the existing
  channel selectors whose corresponding fibre count is at least the threshold.
  Emit (-selector,q) for every selected alternative and (-q,all alternatives).
  Empty OR uses the single negative unit. This formula has exact semantics even
  without one-hot; one-hot links it to the selected count value.
* For each cell in coordinate-pair/fibre-pair lexicographic order, each incident
  group ascending and each t=1..K, allocate q=[left_count>=t] AND[right_count>=t].
  Use three clauses (-q,left),(-q,right),(q,-left,-right). Shared threshold IDs
  are reused; every product here has its own unique (cell,group,t) key.
* K=1 requires the OR of five product variables. K=2 requires at least two of
  ten products: emit all ten positive clauses omitting exactly one variable.

IDs extend the frozen >=7 master with155,939 variables. Compute exact counts,
LF ASCII bytes and streaming SHA256 of the hypothetical suffix without writing
it. Report totals for both the >=7 prefix705,833 clauses and the existing
six-orbit/six-partial-cut prefix705,845 clauses. Do not build either full file.
Save all threshold subsets, product keys/IDs, cell rows and per-section inventories.

Controls: all64 binary3-column row pairs verify intersection<=min(counts); all16
count pairs and both thresholds verify clipping; all4^5 possible five-group min
vectors test sum(min)>=K equivalence; exhaustive OR truth tables through4 inputs,
all8 AND assignments, all32 five-bit and1024 ten-bit bound assignments. Test all
actual one-hot count alternatives against every threshold; corrupt missing OR
term, threshold, AND sign, bound clause, target and contributor coverage. Calibrate
the known all-balanced raw count table as a scalar-bound positive only; test the
authenticated second count witness, which is not a factor and should retain its
known failure at coordinates9,11/fibres2,1. Record every failing cell rather than
stopping at the first one. No claim that passing all envelopes produces a factor.

Repository overlap: earlier count_interval_inventory builds the much larger
exact local-signature lower/upper interval relaxation; second_count_partial_cut
uses six selected scalar-bound clauses; local Frechet equality was refuted.
The read-only search found no existing complete540-cell shared-threshold version.
This is a bounded repository observation, not a novelty claim.

CLI: python -B acceleration/theory_20260930_count_min_upper_inventory.py --out NEWDIR
