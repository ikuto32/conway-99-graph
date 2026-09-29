# Unrestricted scaffold-only full99 encoding preflight

No solver was launched and no research CNF was built. The completed producer
preflight is `results/20260930_unrestricted_full99_preflight_v2/`; its manifest
pins source, exact commands, historical references and the current claim source
commit. The initial CRLF parsing failure is preserved separately and makes no
mathematical claim.

## Existing verified normalization

The authoritative current ledger already contains
`C-ROOT-SCAFFOLD-NORMALIZATION`, revision1, statusVERIFIED and review_stateCLEAR.
Its evidence is:

- `results/20260917_independent_review/ROOT_SCAFFOLD_DERIVATION.md`, SHA256
  `a45fa5c52f3b348e8fb41b347925a363bb79e4d6389f60f760ec85e6cfe8f077`;
- `results/20260917_independent_review/root_scaffold.json`, SHA256
  `e96941c2bc050aad65b67a4f22a8968d588ae4dbe3cd7b7f22bfe84972a963a8`.

The proof was read and every input hash in that historical audit was rechecked.
This is preservation/binding of a prior independent review, not a claim of a
new independent audit by this producer. A copy of the exact claim block from
the pinned current source commit is saved in the preflight output.

The theorem applies to every hypothetical target and every root. The root's
14neighbors induce7disjoint edges because adjacent vertices have one common
neighbor. Each outside vertex has exactly two root-neighbors, necessarily from
different matching pairs. Conversely, every nonmatched pair of root-neighbors
has exactly one common neighbor outside the root neighborhood. These arguments
give a bijection between the84outside vertices and the84nonmatched inner pairs.
The resulting189positive scaffold edges saturate the root and14inner degrees.
All other edges incident to those15vertices are absent, but **no outer pair is
prescribed present or absent**. This is labeling, with no target automorphism.

## Prospective exact scope and size

The saved `scope.json` has exactly the189fixed positive scaffold edges and one
free variable for every unordered pair of vertices15through98:3486variables,
including all126same-support outer pairs. There are no K-edge assumptions,
outer nonedge assumptions, branch units or extra cuts.

Applying the new fully equivalent prefix-threshold implementation to all99
degree equations and all4851common-neighbor caps would produce:

| Component | Count |
|---|---:|
| Free graph edges | 3486 |
| Exact AND product helpers | 285852 |
| Exact prefix helpers | 897162 |
| Total variables | 1186500 |
| Total clauses | 4136454 |

These counts were obtained from the full known/free matrix and complete row
histograms, instantiating only the small repeated threshold templates. They
remain producer engineering results pending independent checking. The complete
research instance was not built. Its scale is compatible with the previous
120-second/8GiB build envelope based on the completed conditional build, but no
runtime or memory guarantee for this larger build is claimed.

The direct model's degree14 equations plus all caps
`common(u,v)+A[u,v] <= 2` force equality by summing: common counts sum9009 and
edge counts sum693, totaling9702, exactly twice4851pairs. Thus a correctly
implemented version would enforce the exact target identity. Combining its
future independent encoding equivalence with the existing every-root theorem
would give unrestricted target coverage. The new scope and its code still need
their own independent binding review; the120-fixed-K encoding claim must not be
broadened silently.

## Prior unrestricted work and duplication boundary

`scratch_general_exact_sat.py` already builds an unrestricted rooted CNF with
3486edge variables,285852one-way wedge helpers,1176BP profile equalities and
3486outer-pair caps. Its raw `scratch_general_exact.cnf` has817278variables,
1622502clauses and30180695bytes, SHA256
`91d22e62625e1221dd46b819e89494db8141dd4ddc9a06f13b9abdb530b83242`.
The new direct model would be larger, with full bidirectional gates and direct
full99 rows that fit the newly independent clause-checking path. It is a new
implementation/verification experiment, not a new mathematical formulation.

The saved `scratch_general_exact_portfolio.json` records a600-second parallel
five-branch run: fourUNKNOWN and one rawUNSAT. It provides no complete checked
proof in that record; none is treated as a new exclusion. The base CNF itself
contains no selected branch units. This preflight did not rerun that portfolio.

The pinned archive also contains historical `C-ROOT-001` and `C-ENCODING-001`
in repository `https://github.com/YesterdaysLemon/conway-99-research`, commit
`85e705cc6c2a14d123120c93a847e30aaab1789e`, path `CLAIMS.yaml`. The associated
`attempts/2026-07-22-compact-sat-encoding.md` and
`verification/2026-07-22-first-wave-audit.md` describe the compact one-way-wedge
argument and historical audit. Their labels are retained as historical records,
not imported as fresh verification. The archive remains unchanged.

## Remaining gate

There is no newly identified gap in the stated every-root normalization.
Outstanding work is a new complete code/scope audit proving that the emitted
CNF actually uses all3486outer pairs without hidden restrictions and implements
the exact99degree/4851cap model. Only after this gate and calibrated solver/proof
paths would an unrestricted solve be warranted. A timeout or a proofless UNSAT
would remainUNKNOWN. No target graph or general nonexistence proof exists in
this preflight; overall search coverage remainsUNKNOWN.
