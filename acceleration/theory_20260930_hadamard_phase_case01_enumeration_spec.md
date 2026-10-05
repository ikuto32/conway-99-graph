# Exhaustive finite phase lift of parity batch case01

This protocol is frozen before enumerating any phase vector. Input is exactly case_01 of the new finite parity batch, not a chosen all-mixed branch. Saved metadata reports12 mixed groups,8 constant groups,172 homogeneous equations on120 phase variables, rank113 and nullity7. These numbers must be reconstructed before use. The raw batch remains subject to separate independent review.

Question: does any of the expected3^7=2187 vectors in this exact homogeneous kernel satisfy all local permutation multiplicities, all nonmatched-coordinate pair Gram conditions, and the full integer incidence-factor conditions including outside-column caps?

The producer rebuilds the general system from the raw fixed support and selected parity patterns, requires literal equality with the saved system, recomputes its RREF and complete nullspace, and checks the saved certificate. It shares the frozen exact producer RREF and discloses this. Independent verification must use a separate checking path; this run cannot approve its own exclusion or construction.

Enumerate all seven-coordinate coefficient tuples in lexicographic order over{0,1,2}. Record every tuple, its phase-vector hash, and its first failure or successful stage. The basis has identity free coordinates, so this is an exact nonoverlapping finite universe, not sampling. No nonzero-vector restriction or symmetry reduction is introduced. The zero vector is included. Stop after all2187 vectors or on a recorded error/resource limit, never after finding a promising factor. If all pass a stage, its full population is retained; pipeline-stage counts overlap and are not summed.

Stages, in order:

1. For a mixed group, phases on each sign class must be exactly{0,1,2}. For a constant group, the six phases must have multiplicities(2,2,2). Check literal affine maps also give exactly two coordinates in each fibre in each of the three group columns. No mixed-only condition is imposed on constant groups.
2. For every one of60 nonmatched coordinate pairs, reconstruct all five relative affine permutations from raw signs and phases. The literal3-by3 incidence sum must be `2J-I`, allnine entries. This enforces all odd/even phase multiplicities, not just their modular sums.
3. For every local survivor, reconstruct the binary36-by60 factor in the original raw support-column order: in group g's x-th column (x=0,1,2), coordinate a selects fibre `(s_a*x+t_a) mod3`, hence row12*fibre+a. Perform a separate full integer factor check. Save the complete raw factor and exact Gram/cap findings for every local survivor, even if the pair test fails, so no failure is omitted.
4. The literal checker computes every one of1296 Gram entries, row10 and per-fibre column2 margins, all1770 column intersections (required<=2), and all2160 entries of `(I+C)F` (required<=2). It compares coordinate sums with the exact saved L. A factor with correct Gram but failed caps is saved and labeled a weaker Gram-factor candidate. A factor satisfying all checks is still only a partial99 construction; residual D is absent.

All stage counts, first-failure category counts, and raw witnesses are retained. No full99 graph is claimed. Exhaustion can exclude only this one complete parity assignment inside the balanced fixed-support family, and only after independent certificate/enumeration review.

Controls run first: exact local mixed/constant positive profiles and changed multiplicities; all243 five-phase assignments for each of the0-odd and3-odd relative-sign cases; and the independently checked SRG243 nonempty factor as a generic integer Gram/margin/cap positive. SRG243 is not asserted to satisfy this fixed support or its balance restriction. Deliberately corrupted generic factors/caps must fail. No positive Conway99 factor is invented.

Limit120 seconds, exact integer arithmetic only, no native solver. Enumeration records are written incrementally as JSONL; an error preserves its completed prefix. The expected2187 cases are cheap enough for one complete run; no automatic resume/retry is authorized. The source commit, command, pinned environment, inputs, source/spec hashes, actual outcome and all output hashes are recorded.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_phase_case01_enumeration.py --out acceleration/results/20260930_hadamard_phase_case01_enumeration
```
