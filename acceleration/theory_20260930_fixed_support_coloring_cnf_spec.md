# Fixed connected_01 Hadamard-support coloring CNF

Freeze before build. Select the first case passing every cheap screen in the
already frozen order connected_00,01,02,03,six_prism. Thus connected_01 is the
input; connected_00 has empty domain41 and is not silently discarded from the
scout. The raw support scout remains candidate pending independent review;
building an encoding does not approve it. No solver until fresh independent
support, exact encoding and raw-object gates.

Scope: all binary36-by60 F whose coordinate projection is the one fixed12-by60
L, whose two-per-fibre column margins and exact prescribed1296 Gram entries
hold, and whose every distinct-column overlap is at most2. The chosen inner
core has identity cross matchings. Mixed caps are redundant by the separate
independent lemma. No D or full99 graph is encoded, no otherL/core coverage,
no target automorphism, no normalization beyond the fixed raw labels.

Start from all90 balanced fibre assignments of each fixed six-coordinate
support and discard any assignment selecting a pair with zero prescribed full
Gram entry, including cross-fibre zero entries. This is necessary for every
full factor; it is broader than only the within-fibre matching-pair filter.
Give every retained color choice one selector, ordered by column then frozen
option index. Each option chooses exactly six raw rows. Encode exact-one per
column. For all666upper-triangular Gram entries, count the selectors whose row
sets contain both rows and require the exact Gram target. Because only one
selector per column is true, these linear counts equal FF^T, without product
variables. For all1770column pairs, emit a binary negative clause for every
pair of choices overlapping in more than2rows. Save full row/count metadata
and per-column-pair forbidden-option bitmaps, cardinalities and clause ranges.

Reuse the frozen producer Encoder from theory_20260930_eight_full99_cnf.py:
full threshold recurrence t(i,j)=t(i-1,j) OR(x_i AND t(i-1,j-1)), exact gates,
constant folding, thresholds through k+1, final >=k and not>=k+1. Store every
state and fresh-variable interval. This is disclosed producer reuse, not an
independent check. Run its exhaustive small controls plus new option/count and
pair-cap truth controls; no known complete researchF is available as a positive.

Bound full build120seconds/8GiB sampled process memory. No RNG or solver. Use
tqdm for Gram and cap inventories; retain exact raw body/model and lossless
gzip parts eachunder9MiB. Save commands, versions, sourcecommit, all input/output
hashes and failures. A candidate decoder requires all IDs, exact-one choices,
then verifies raw F/L/Gram/caps and optionally derives the canonical C0 column
permutation; it must never claim independent verification or target discovery.
