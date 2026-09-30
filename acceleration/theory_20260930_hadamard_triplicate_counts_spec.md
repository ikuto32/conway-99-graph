# Exact triplicate-support projection experiment

Frozen before execution. This is a new candidate investigation, not an audit of
its own conclusions and not a SAT retry.

Input: the hash-bound `20260930_hadamard20_support/six_prism.json` and its
independent support and ordering audits. Scope: the one saved aggregate L with
20 distinct six-coordinate supports, each repeated three times. No cyclic
colouring, graph automorphism, residual D, or target existence is assumed.

Questions and selection rules:

1. Derive the exact necessary equations for each coordinate a and fibre g:
   its ten group counts t_p are in {0,1,2,3}, sum to10, and sum to5 on the five
   groups containing each nonmatching coordinate b. Form their integer matrix
   directly from raw supports and save exact rational row reduction.
2. For every a in ascending order, enumerate vectors v in {-1,0,1}^10 in
   lexicographic order until the first nonzero kernel vector. Save counts
   (1+v,1-v,1), which test only the marginal projection. A nonconstant witness
   refutes uniqueness in this projection, not the proposed implication from
   the full Gram system.
3. Exhaust all 117,480 increasing triples of the 90 balanced colour words in
   one six-coordinate support. Keep exactly those satisfying every literal
   within-triple Gram upper bound and all three outside-column overlap caps.
   Count colour-count profiles, coordinatewise (1,1,1) cases, and cyclic cases.
   Preserve the first lexicographic unbalanced survivor and first balanced
   noncyclic survivor if either exists. These are local witnesses, not factors.
4. Compare the marginal witnesses against local triple count profiles. Seek a
   projected joint assignment only if the preceding exact records expose a
   cheap deterministic check; any additional experiment needs a separate
   protocol rather than a retroactive selection change.

Limits: 60 seconds total computation, no native SAT/MIP or LP solve, no GPU;
the two enumerations have the exact finite universes above. Exact integer or
Fraction arithmetic only. A complete table is claimed only after all cases
are processed; incomplete work saves its stopping reason and counters.

Controls precede research enumeration: small matrices with known rational
rank/kernel; positive and corrupted kernel vectors; valid balanced words and
malformed words; an explicitly cyclic local triple; deliberate duplicate
word and repeated pair violations. Save exact source/input hashes, commands,
tool versions, controls, raw witnesses and limitations. Outputs remain
CANDIDATE pending independent review. No claim ledger changes.
