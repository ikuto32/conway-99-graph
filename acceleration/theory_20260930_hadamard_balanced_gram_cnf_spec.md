# Complete balanced local-triple Gram encoding on one fixed support

This source/spec is frozen before the build. Build and finite calibration are authorized; no solver is invoked. The domain includes constant and mixed parity groups. It is not a continuation restricted to one sampled parity vector, to the all-mixed case, or to the cyclic construction.

## Exact construction class and equivalence

Fix the raw six-prism core and its saved12-by60 Hadamard coordinate-support matrix L. Its twenty distinct six-coordinate supports each occur in three columns. Impose the additional balance condition: within each group, every coordinate occupies each fibre exactly once across those three columns, while each column has two coordinates in each fibre. Balance is not asserted WLOG, nor is this support universally assumed. No target automorphism is assumed.

An ordered group's six coordinate functions are permutations of three letters. Relabel its three identical-support columns so the first coordinate function is identity. This normalization is a label change preserving the fixed L, all factor Gram entries, and all column intersections. It is not an automorphism assumption. Conversely any normalized object is an object in the unnormalized class. Enumerating all6^5 remaining permutation tuples and imposing the literal two-per-fibre column condition gives150 options:30 constant parity and120 mixed parity. No option is removed by a linear phase screen or prior branch exclusion.

Each option chooses eighteen factor entries in the group's three columns. For a nonmatched coordinate pair a<b, exactly five groups contain both coordinates. In each such group its contribution is the permutation matrix of `pi_b composed with inverse(pi_a)`. The full prescribed3-by3 cross-coordinate Gram block is `2J-I`: diagonal1, off-diagonal2. Enforcing these540 scalar entries gives the complete prescribed36-by36 Gram matrix: diagonal10 follows because each coordinate is in ten groups and contributes once to each fibre; entries for distinct rows of the same coordinate are zero; matched-coordinate rows have zero intersections; the remaining entries are precisely these60 blocks and their transposes.

Thus a complete SAT assignment is equivalent, after independently checked normalization and encoding, to a balanced binary36-by60 factor with this exact support and prescribed Gram. This is stronger than modular or necessary parity screens because it retains the actual150 local permutations and exact integer cell counts. **Outside-column caps are omitted initially.** The decoder computes all1770 intersections as diagnostics and distinguishes a Gram factor from one also passing these caps. The mixed `(I+C)F<=2` test is also reported. No residual D or complete99-vertex graph is encoded.

## Variables and full clauses

IDs1..3000 are group selectors: `150*g+choice_index+1`. Options are retained in lexicographic permutation-tuple order after fixing coordinate0 to identity.

There are2980 prefix auxiliaries,149 per group. Prefix p_i represents OR of the first i selectors (i=1..149). The first prefix is equivalent to its selector. Each intermediate prefix is equivalent to previous-prefix OR next-selector, with a clause forbidding both previous-prefix and next-selector. The last prefix and selector150 form an XOR. This is an exact-one relation with unique prefix extension and596 clauses per group (11,920 total).

Next come1800 relative-permutation indicators:60 coordinate pairs, five incident groups each, six permutations in lexicographic order. Each indicator is equivalent to the OR of exactly those group selectors inducing that permutation. All150 selectors occur in exactly one channel per pair/group. These full equivalences contribute46,800 clauses.

Finally come2700 cell flags:60 coordinate pairs, nine matrix cells, five incident groups. A flag is equivalent to OR of the two relative-permutation indicators mapping that cell's first fibre to its second fibre. All flags use full three-clause OR equivalences (8,100 clauses). A diagonal cell requires exactly one of its five flags; an off-diagonal cell requires exactly two. Direct subset clauses encode exact count: at-most k uses all(k+1)-subsets negative, at-least k uses all(5-k+1)-subsets positive. These contribute7,380 clauses.

Expected total:10,480 variables and74,200 clauses. The build derives and verifies actual counts, clause offsets and all channel populations. Compared with the earlier595,464-variable/3,336,642-clause ordered fixed-L formula, this is a different exact balanced-class formulation with a stronger balance restriction and initially omitted Ycaps. Size is not a performance comparison or a scope-equivalent speedup claim.

## Controls and artifacts

Before the build, exhaustively calibrate exact-one prefix semantics including unique auxiliary values for small sizes; full OR relations; and exact counts1/2 on five bits. Enumerate all7776 local permutation tuples and retain all150 without solver calls. Check relative-permutation orientation literally on all36 ordered permutation pairs and all three letters. Calibrate the generic integer factor checker on the independently checked nonempty SRG243 factor and deliberately corrupted entries. This is a validator control, not a positive instance of this fixed support or balance restriction.

`scope.json` saves exact L, core, prescribed Gram, original support-column mapping, normalization and omissions. `model.json` saves every local option, literal permutations, lifted rows, prefix state and clause range, all relative channels, all cell flags and exact-count rows. `instance.cnf` contains every clause. The decoder reads a complete10,480-signed-ID assignment, checks the actual CNF, reconstructs F in original column order, and checks all1296 Gram entries, margins, exact L, all1770 cap diagnostics and all2160 mixed-cap entries. It supplies a canonical C0 column permutation only after directly checking that its sixty column pairs are the complete nonmatching-pair catalogue.

Build allocation30 seconds, exact integer arithmetic, no solver. All source/input/output hashes, source commit, exact command, actual time and preserved failures are recorded. Every new mathematical/encoding claim remains CANDIDATE pending a separate independent derivation and full clause/object review. No green build constitutes mathematical verification.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_balanced_gram_cnf.py --out acceleration/results/20260930_hadamard_balanced_gram_cnf
```

Decoder API: `decode(assignment, model_path, scope_path, cnf_path)`. A raw Gram factor with failed caps is preserved by returning diagnostic failures; it is not rejected or silently upgraded to a capped factor. No native solve is authorized by this specification.
