# Independent normalization of the seven-exception profiles

This is a new finite audit of the1608 exactly-seven-exception profiles on the literal six-prism Hadamard support. It imports only the pinned independently authored six-profile checker helpers for dense bitmap parsing, exact reindexing and calibrated covariance controls. No normalization, local-domain or AC producer is imported. The prior diagnostic orbit count is unused. Complete initial domains, every actual checkpoint relation path (including reused run01 files) and the separately reviewed complete AC report are authenticated.

Write a core row as (f,a), with f in three fibres and a in twelve coordinates. For any permutation tau, let P map (f,a) to (tau(f),a). Every internal matching is the same, and every cross-fibre matching is the identity. Therefore P C P-transpose=C. The literal check also verifies P G P-transpose=G for the prescribed factor Gram. The three root-triangle vertices are relabelled by tau as well, preserving the39-vertex core.

For any binary factor F, the coordinate support L[a,d]=sum_f F[(f,a),d] is invariant under P. Reorder the three columns in each identical-support group as needed after relabelling; their column permutation Q preserves L. Then F'=P F Q has F'F'-transpose=P G P-transpose=G. Every column overlap is permuted, and (I+C)F'=P(I+C)FQ preserves all mixed upper bounds. Row margins and each profile deviation transform by the same fibre permutation. The exceptional group identities and number remain unchanged.

For any residual completion D, put D'=Q-transpose D Q. Binary, symmetry, diagonal and degree conditions are preserved. The exact identities transform as

```
F'D' = P(FD)Q = 2J - F' - C F',
D'^2 + F'^T F' = Q^T(D^2 + F^T F)Q = 12I - D' + 2J.
```

Thus this is a reversible relabelling of full factors and completions. It is not an assumption of a nontrivial automorphism of any hypothetical target. Sorting local columns is only a canonical representative choice inside equal-support triples; inverse relabelling recovers the original solution up to that explicitly allowed column order.

For all90 balanced six-coordinate words and31110 cap-compatible local triples, the checker reconstructs the transformed literal words, sorted triple and old-column order, checks every map is bijective and all36 group compositions agree. Every complete endpoint domain is mapped by its literal triple set. Both pair predicates are invariant because their summed Gram is conjugated by P and their column intersections are permuted by the two within-group column permutations.

The implementation uses dense Boolean matrices rather than the producer's bit-transport loop. It compares every entry for both predicates under all six actions:37,784,232 option pairs times two predicates times six actions. All2016 endpoint maps, all1608 profile actions, all final-domain elements and every one of42 directed arcs per profile/action are checked. Reverse arcs are the transposes of the already completely checked forward relations; their endpoint images and relation identities are explicitly verified. This implication is complete, not a sample or a second AC search.

The direct raw profile actions determine268 disjoint size-six orbits. The separate exact AC audit supplies the classifications:276 first-predicate-empty profiles form46 orbits;312 combined-empty profiles form52 orbits;1296 combined-nonempty profiles form216 orbits. Both predicates begin with within-group-cap-filtered domains. The first count is therefore not an abstract Gram-only exclusion. Nonempty AC is not simultaneous compatibility, a factor or a residual completion.

Known-positive controls include an authenticated SRG(243,22,1,2) factor with a nonempty residual: exact Gram, mixed and residual equations are checked before and after independent row/column relabelling. This is a different parameter set, not Conway99 evidence. Dense rectangular-matrix controls and actual changed relation entries, invalid bijections, changed fixed core/residual, changed final-domain elements and wrong directed arcs are rejected. Empty and nonempty first-survivor selection controls are included.

The new audit depends explicitly on the independently checked local-domain population and AC correctness. It does not repeat those exhaustive algorithms. No native solver, ledger or publication operation is performed.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_seven_fibre_orbits.py --out acceleration/results/20260930_independent_review/hadamard_seven_fibre_orbits
```

Use a new output directory for every replay; outputs retain exact input/source hashes, local availability, actual commands and environment versions.
