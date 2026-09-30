# Separate exact fractional witness and integral column-order normalization

Both claims use only the frozen six-prism Hadamard aggregate support. Each
column chooses one endpoint of each of six standard matching pairs. Every
balanced assignment of its six coordinates to three fibres, two coordinates
per fibre, avoids the zero Gram pairs. There are exactly 90 such options,
ordered by their saved lexicographic fibre words. The independent checker
reconstructs these domains by successive choices of two coordinates and
checks every raw row set and mask; it imports no producer code.

For the original continuous selector model, give every option weight 1/90.
Each column then has total weight one. A specified coordinate occupies a
specified fibre in 30 of the 90 assignments. For two selected coordinates,
they occupy two specified equal fibres in six assignments and two specified
different fibres in twelve assignments. The aggregate has each coordinate in
30 columns, each nonmatching pair in 15 columns, and a matching pair in zero
columns. Thus the weighted factor has diagonal Gram 30/3=10, same-fibre
nonmatching Gram 15/15=1, different-fibre nonmatching Gram 2*15/15=2, and the
required zero entries. This agrees with the literal prescribed Gram.

The audit reconstructs all 5,400 sparse selector columns from their six raw
row indices and all 726 right-hand sides. It checks the supplied integer
numerators against denominator 90, and separately accumulates ordinary exact
Fractions by raw-option membership. All equations hold exactly. This gives
only a feasible point of the continuous nonnegative Gram-selector relaxation.
It omits integrality, outside-column caps, ordering constraints and residual
D. The earlier numerical result and failed bounded-denominator attempt remain
unchanged. No rational repair or floating tolerance is needed for this new
literal uniform witness.

Separately, the saved support has 20 distinct six-coordinate sets, each
appearing in exactly three columns. All 90 options align identically, including
their saved order, across each such group. In any exact binary factor, two
columns in one group cannot choose the same option: that would repeat the
option's two fibre-zero neighbors, contributing two to a nonmatching
within-fibre Gram entry whose exact total is one. The outside-column cap
would also reject their overlap of six, but that extra premise is unnecessary.
The audit checks this obstruction for all 20 times 90 group/option cases.

Therefore the three selected option indices in each group are distinct.
Relabel its three outside vertices so those indices strictly increase along
the group's ascending saved column labels. This preserves the aggregate L
because the three supports agree. If P is the resulting 60-column permutation,
F becomes FP and any residual adjacency becomes PᵀDP. Then FFᵀ is unchanged,
column-pair overlap data are permuted, FD becomes FDP, and D² is conjugated.
Every full graph identity is preserved by the corresponding simultaneous
row/column relabelling of all outside vertices. This establishes coverage of
all integral factors and their possible completions in this fixed-support
family, without assuming any automorphism of a hypothetical solution.

Only increasing option order within each identical-support group is approved.
There is no additional fixed column, fixed bit, complement pairing or target
symmetry premise. The uniform fractional point is not asserted to satisfy an
ordered relaxation. No new CNF implementation is approved by the mathematical
normalization gate; each subsequent encoding still needs a complete check.

Sorting controls exhaust all 90^3 rank triples: 704,880 ordered triples of
distinct ranks admit invertible sorting, while 24,120 have repetitions. The
number of increasing triples is 117,480. Separate small raw matrix controls
check Gram preservation, mixed-product permutation and residual-square
conjugation for all six permutations. They are generic controls, not invented
complete research factors. Corruptions alter weights, sparse entries, margins,
option order, support identity and Gram data.

Two distinct reports and claim bindings are emitted. The shared independent
raw-domain implementation is disclosed; no producer LP code or solver is
imported. Use separate fresh output directories:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_prism_relaxation_and_order.py --mode lp --out build/hadamard-prism-uniform-review-new
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_prism_relaxation_and_order.py --mode order --out build/hadamard-prism-order-review-new
```
