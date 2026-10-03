# Fixed six-prism Hadamard support: all ordered colourings

Freeze before build; future wave 17, excluded from the frozen sixteenth
catalogue. Choose the exact six_prism L in the independently checked five-case
Hadamard support scout. The connected-01/02/03 supports have exact exclusions;
the later cyclic-colouring subclass exclusion does not exclude all colourings
of this L. This build covers all 90 balanced colour options per column, with
no cyclic restriction, bit complement restriction or target automorphism.

Scope: binary 36-by-60 F projecting to this fixed binary 12-by-60 L, with two
entries per fibre per column, the entire prescribed Gram FF^T, and overlap
at most two for each of the 1,770 distinct column pairs. Identity cross-fibre
core matchings are fixed. Mixed caps follow from the independently checked
identity-P lemma and are also explicitly tested by the candidate decoder.
No residual D or 99-vertex graph is encoded. Only this support and core are
covered. The exact SAT object remains subject to independent raw validation.

Use the independent identical-support order gate
0ce1be9ca11a3e860aa97791cfb4f42c1660d937a69ac7a9b7d96ca37640c9d2.
It supplies 20 size-three groups and their 40 adjacent column pairs. Each
group has the identical saved 90-option order. Equal selected options are
already impossible by within-fibre Gram entries or column overlap; permuting
these outside columns permits strictly increasing option ranks. This is
relabelling of possible factors (and of a possible D), not assuming their
automorphisms. The ordered model is existentially equivalent to the full
fixed-support model under those column permutations, not literally all of
its labelled assignments.

Assign 5,400 selectors by increasing raw column then option rank. Reconstruct
all balanced six-coordinate colourings and check the saved lists exactly.
The generic rule excludes choices containing a zero prescribed Gram pair;
for this six-prism L all 90 options survive in every column. Emit 60 exact-one
counters and 666 upper-triangular exact Gram counters, including the 36
diagonals. A row-pair contribution equals the selector count because one
choice per column is true. Reuse the unchanged fully equivalent prefix
threshold Encoder from theory_20260930_eight_full99_cnf.py, thresholds through
k+1, constant folding, exact bidirectional gates and final lower/upper units.
Record every counter and fresh-variable interval. No CardEnc or solver.

For each of 1,770 column pairs test all 90-by-90 choice pairs, 14,337,000 in
total; emit a two-negative-selector clause exactly when overlap exceeds two.
Save the complete forbidden-choice bitmaps, counts and clause intervals.
Then append for every adjacent ordered pair (d,e), every left rank a=0..89
and right rank b=0..a the clause -s[d,a] -s[e,b]. This is 4,095 clauses per
pair, 163,800 overall; no new auxiliary variables. Preserve the base-clause
cutoff and exact suffix metadata to permit independent byte reconstruction.

Success at this stage means complete deterministic formula/model construction,
controls and lossless public packages. It is a CANDIDATE encoding until a
separate complete audit. Failure means recording the exception and retaining
all partial output. Preregistered resource limits are 120 seconds and 8 GiB
sampled process peak working set, checked throughout encoding/packaging.
No automatic retry, RNG or research SAT call. Progress uses tqdm. Save source
commit, exact command, Python/uv versions, all source/input/output hashes and
resource observations. Gzip parts are each at most 9 MiB; raw files retained.

Controls: existing exhaustive prefix-counter controls, one-hot Gram identity
truth cases, column-cap clause truth cases, strict-order clause truth cases
on sizes 2..8, all small distinct-triple sorting controls, explicit duplicate
and reversed-rank rejection. These are encoding controls, not a known full
research factor. The candidate decoder requires a complete unique assignment,
then checks every raw Gram entry, L projection, margins, both cap types and
all 40 rank comparisons. It emits raw F, selected selectors/ranks and an
explicit canonical-C0 column permutation; independent native/object gates
must check the complete assignment and every actual CNF clause before any
SAT output can be promoted. UNSAT requires a full independent proof replay
and the exact encoding/ordering coverage gates.
