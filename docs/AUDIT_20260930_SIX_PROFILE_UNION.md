# Independent composition of the six-exception exclusions

This audit concerns only the literal support in `hadamard20_support/six_prism.json` (SHA256 `ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d`). Let F be binary36x60, have this coordinate support and its prescribed integer Gram, and have every two distinct outside columns overlap at most2. An identical-support group is unbalanced if any of its coordinate/fibre counts in its three columns is not1. No target automorphism is assumed.

The independently checked complete sextet census reduces every exactly-six-unbalanced F to one of nine literal sextets. The complete integer marginal census then reduces these to984 labelled profiles. Three sextets have no such profile. These are necessary reductions, not assumptions of feasibility. The local-domain gate binds every one of the984 profiles to complete local choices with within-group caps. The complete AC gate proves654 profiles impossible and identifies330 nonempty fixed points. A nonempty fixed point alone never proves feasibility.

For a permutation tau of the three fibres, permute F's rows accordingly. The fixed core and prescribed Gram are invariant under all six such permutations, as checked on all their entries. The coordinate support is unchanged. Sort each resulting triple inside its three identical-support columns (or apply the independently checked first-coordinate gauge for a balanced triple). This only permutes equal-support columns. Thus the transformed matrix still has the full Gram and every column cap. In matrix form it is P F Q, with P and Q permutation matrices; an arbitrary residual completion transforms to Q-transpose D Q. This is an isomorphism between labelled solution sets. It does not assert an automorphism of any hypothetical target.

The new checker reconstructs every literal profile image by directly permuting the three fibre slices and locates that exact array in the984-profile dictionary. It checks inverse actions, the previously recorded normalization orbits, and the independently established AC labels. There are164 disjoint six-member orbits. The330 nonempty profiles occupy55 whole orbits. A profile's groups and every coordinate/fibre deviation are retained, so a match is stronger than merely matching counts or rank.

The earlier profile0000 and the54 newly checked representatives each have an independently established exact full-Gram encoding and a complete accepted DRAT replay. Their formulas retain every initial local choice and within-group caps. They omit cross-group caps and residual D. Consequently every capped factor in a representative's profile would give a satisfying assignment of that representative's formula. UNSAT of these weaker necessary models excludes their respective capped profiles. The new audit binds all55 actual CNF/model/scope identities, the literal profile and raw support, complete proof bytes, accepted checker receipts and output hashes. It authenticates the proof artifacts; it does not rerun DRAT.

The literal set union is checked, not inferred by adding totals:654 distinct AC-excluded profile IDs, disjoint from330 IDs in55 distinct proof-excluded orbits, cover each of984 IDs exactly once. This proves the exactly-six exclusion. Combining it with the independently established at-most-five exclusion uses the disjoint integer cases0..5 and6 and implies at least seven unbalanced groups. Neither conclusion excludes the full fixed support, the core, other supports, or Conway99.

Positive controls include the actual partition, all inverse fibre actions, and a standalone known finite partition. Corruption controls remove or duplicate representatives, create overlaps/gaps, change an AC identity or universe ID, break a fibre bijection, reject an unaccepted replay or wrong CNF/proof hash, alter a literal deviation, and introduce an unreviewed scope restriction. This is a composition checker, not a factor validator; no feasible full factor is used or claimed.

Trusted components are explicitly the prior independent coverage, normalization, AC, encoding and complete proof gates and Python exact integer/set arithmetic. The checker imports no producer or previous checker code. The prior four-profile union informed the protocol, but this new implementation reconstructs the changed984-profile universe. The original root-written candidate derivation is preserved unchanged and authenticated; its historical pending-proof wording is not rewritten.

Replay with the existing locked environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_six_profile_union.py --out acceleration/results/20260930_independent_review/hadamard_six_profile_union
```

Use a fresh output directory for each replay. Missing raw CNFs/models/proofs must first be recovered from their authenticated packages; a recorded hash does not substitute for an available artifact. No solver, ledger or publication mutation is performed.
