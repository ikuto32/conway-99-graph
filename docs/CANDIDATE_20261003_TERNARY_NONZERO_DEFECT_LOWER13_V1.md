# Candidate: every nonzero ternary residual has at least thirteen defects

Discovery producer `/root`; source context
`63437c9b9fc2dd58b3bdfb51fc347b880b397503`. Status CANDIDATE, pending complete
different-author written dependency and implication review. This is outside
the frozen371-claim publication cutoff. No executed mathematical command,
graph fixture, formal proof, external review or novelty assertion is supplied.

## Precise revision-1 statement

For every symmetric binary integer 99-by-99 matrix A with zero diagonal and
every integer row sum14, define R=A^2+A-12I-2J over the integers, M=R modulo3
over GF(3), and F3 as the number of unordered off-diagonal entries of M that
are nonzero. Then F3=0 or13<=F3<=4851. This is an exact necessary bound in the
whole unrestricted degree14 adjacency domain. It does not force F3 to be
nonzero, establish sharpness, realize thirteen defects, assume an automorphism,
or construct/exclude the target SRG. In particular a target graph with F3=0
remains allowed.

## Four pinned material dependencies

All dependencies are revision1 and used with relation `uses_result` in the
same complete binary99/14 domain and with the same WHOLE residual support.

1. `C-UNRESTRICTED-DEGREE14-TERNARY-NONZERO-DEFECT-LOWER12`:
   F3=0 or F3>=12. Candidate
   `docs/CANDIDATE_20261003_TERNARY_NONZERO_DEFECT_LOWER12_V1.md`,
   SHA256 `8af2f38aeb004b5d485b8596f10d04caf1d3bb061d03885031641a9b8ebcdd25`;
   independent ROOT written audit
   `acceleration/audit_20261003_ternary_nonzero_defect_lower12_v1.md`,
   SHA256 `74fa37e72d3c2b44ee054933d06f887baf3bb2c4d9370fa1f09aa993973fb7a6`;
   report `acceleration/results/20261003_independent_review/ternary_nonzero_defect_lower12_01/summary.json`,
   SHA256 `b5cb1f515ff8f36dd9b18c57208c7b12540a6750e375ca932be3906ccaed5ea0`.
2. `C-UNRESTRICTED-DEGREE14-TERNARY-TWELVE-DEFECT-SUPPORT-CLASSIFICATION`:
   at F3=12 the whole support is K2,6 or K6 minus a perfect matching.
   Candidate `docs/CANDIDATE_20261003_TERNARY_TWELVE_DEFECT_SUPPORT_CLASSIFICATION_V1.md`,
   SHA256 `8a773e82bdd4bc7255f960deb93717c27c8ade0fab8a1fb4017e05a68e09384e`;
   independent ROOT audit
   `acceleration/audit_20261003_ternary_twelve_defect_support_classification_v1.md`,
   SHA256 `a53823f058201aca934349d79c049cea4762672d5d2574aa7327c4946205666b`;
   report `acceleration/results/20261003_independent_review/ternary_twelve_defect_support_classification01/summary.json`,
   SHA256 `a54c3eab6419ba0ce4e563c52444fd3d748d2e0687640b9bed81d1fe087da707`.
3. `C-UNRESTRICTED-DEGREE14-TERNARY-WHOLE-K2-6-SUPPORT-NONREALIZABILITY`:
   the whole K2,6 support has no actual integer adjacency-polynomial lift.
   ROOT candidate `docs/CANDIDATE_20261003_TERNARY_K2_6_INTEGER_LIFT_V1.md`,
   SHA256 `4efb2e1ffbcf4bf8c310c3521b175e570b93e1ed7ef18d20cbecaf05dea55260`;
   independent Structural audit
   `acceleration/audit_20261003_ternary_k2_6_integer_lift_v1.md`,
   SHA256 `2b8dad64a3d15443ddca45ddd4946ccc5aa215a7739a9d9f234b4c7f4873bd7d`;
   report `acceleration/results/20261003_independent_review/ternary_k2_6_integer_lift01/summary.json`,
   SHA256 `0301d9591b261b3cf1b29f1f51bd52b0233126ea2bf01dfa2e0721e2e9cd8832`.
4. `C-UNRESTRICTED-DEGREE14-TERNARY-WHOLE-OCTAHEDRAL-SUPPORT-NONREALIZABILITY`:
   the whole K6-minus-perfect-matching support has no actual integer lift.
   ROOT candidate `docs/CANDIDATE_20261003_TERNARY_OCTAHEDRAL_SUPPORT_V1.md`,
   SHA256 `4fe0d18e60d62af2b6c95a784b4bf4201168aa4cfdc141e1681f8561b9cbbd5a`;
   independent Structural audit
   `acceleration/audit_20261003_ternary_octahedral_support_v2.md`,
   SHA256 `812014ddb5aa877ab4a0ae83e5371a49f32adf40b22894f80b882c32fc8ce9fe`;
   report `acceleration/results/20261003_independent_review/ternary_octahedral_support01/summary.json`,
   SHA256 `7320feba0d6e86e6691fbef55daab95b561829d659fe9365242f8afbb9676a97`.

These are new internally reviewed written results, currently LOCAL_ONLY and not
asserted present in CLAIMS.yaml. ROOT authored two lift discoveries and verified
the other two discoveries; these roles are disclosed. ROOT does not independently
approve this new combined discovery. No historical ledger label is treated as
fresh mathematical verification, and no target graph or scientific run is read.

## Exact implication and review requirements

F3 is an integer between0 and binomial(99,2)=4851. If it is nonzero, dependency1
gives F3>=12. If it equals12, dependency2 exhausts its whole support into two
possibilities. Dependency3 rules out the first and dependency4 rules out the
second. Neither exclusion requires a support component to stand alone after
omitting any other defects: the classification already supplies the whole
support. Thus F3 cannot equal12. Integer discreteness gives F3>=13, proving
the candidate statement.

The independent reviewer should read all four exact discovery/audit/report
packages, check matching definitions, quantifiers, hypotheses, whole-support
coverage and pinned revisions, and try to falsify the boundary and implication.
The lower12 paper's field-level K2,6 nilpotent example remains algebraically
valid: the stronger separate integer-lift exclusion does not refute that example
or a sharpness statement, because no actual adjacency realization was claimed.
The classification's necessary survivors likewise need not be realizable.

The integer-lift exclusions provide no automorphism normalization and no graph
space denominator. No new heuristic zero, performance bound, incidence rank,
graph realization or general nonexistence is claimed. Overall search coverage:
UNKNOWN; no validated denominator. Artifact availability is LOCAL_ONLY; immutable
publication and external review remain separate. Creation/start timestamps are
unavailable; a verifier report must use its actual clock and final artifact hash.
No ledger, index, current notice, engine or frozen milestone is changed here.
