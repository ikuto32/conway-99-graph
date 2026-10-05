# Candidate normalized triangle matching-pair census

Frozen before execution on 2026-09-30 JST. This is a discovery protocol, not independent verification.

## Scope and question

Fix labelled triangle T and pull the A1 and A2 labels through their perfect
matchings to A0. Let M0 be the standard perfect matching on twelve labels.
The remaining internal matchings M1,M2 and the A1--A2 bijection P are arbitrary.
The simultaneous coordinate group H=Cent(M0), of order 2^6*6!=46080, acts
by conjugation. This changes labels; it does not assume an automorphism of
a completed graph. No interchange of the named fibres is imposed.

The experiment completely classifies ordered pairs (M1,M2) under H, without
constraining P or the sixty outside vertices. First classify M1 under H;
then classify M2 under the actual stabilizer of the selected M1. Do not
independently normalize both matchings under all of H.

Success means explicit orbit partitions cover all 10395 choices at both
stages, with generated subgroups checked against independently enumerated
centralizers in this producer, and exact orbit/stabilizer/count identities.
This is not a complete 39-vertex core census: P remains unclassified.
No common-neighbour, Gram, or extension pruning is used in this first census.
No SAT solver is launched. All classifications remain CANDIDATE until a
separate implementation audits the emitted partitions and coverage.

## Limits and controls

Use pinned root uv.lock, standard library only, deterministic order, no seed.
Hard cooperative wall limit 120 seconds and memory cap 8 GiB, checked during
group and orbit traversals. If reached, retain the manifest and completed
stage records, report incomplete, and do not infer coverage.
Small cases n=4 and n=6 compare generator-BFS partitions with direct images
under every full stabilizer element. A deliberately corrupt non-permutation
is rejected. Main n=12 uses explicit full group enumeration as well as
generator-BFS; these share code and are producer controls, not independent
review. Every emitted group generator must preserve M0 and the named M1.

## Prior work and why this is a different experiment

Archive repository https://github.com/YesterdaysLemon/conway-99-research at
85e705cc6c2a14d123120c93a847e30aaab1789e:

* attempts/2026-07-22-eleven-branch-cover.md and its first-wave/wave2 audits
  classify one matching into eleven H-orbits, not an ordered pair.
* attempts/wave40-exact-coupling-model/README.md normalizes M1 and derives
  a complete lower-rank projection bound. Its full-block scout samples 512
  (P,M2) pairs per type and explicitly denies complete pair coverage.
* attempts/wave42-rank26-equality/proof.md implicitly covers P and M2 only
  to exclude rank-26 residuals; it does not emit all core orbits.
* verification/wave41-allquotient-lifts/audit.md classifies the all-222,
  rank_F3=12 quotient/lift case, a conditional subset.
* verification/wave34-rootless-global/audit.md scans triples from a fixed
  one-factorization and a fixed holonomy, not arbitrary internal matchings.
* attempts/wave153-alternative-compatibility/README.md concerns eighteen
  component types at the prism-free kappa=3 endpoint only.
* Wave149/151/154 fix all three internal matchings and P=shift6, then study
  incidence factors. Their Q1 orbit counts are not core counts.

This scoped source search found no released complete arbitrary (M1,M2,P)
canonical census. Absence from this inspected set is not a claim that no
such result exists anywhere in the archive or literature. Historical VERIFIED
labels are not fresh independent verification.

## Next use

Each ordered matching-pair representative leaves P arbitrary up to the
joint stabilizer Cent(M0,M1,M2), whose exact size is recorded. Subsequent
work may search P with exact principal common-neighbour and Gram filters,
then Q1 incidence feasibility, but must prove pruning and coverage separately.
The unrestricted labelled triple population is 10395^2*12!, not the number
of representatives produced here. No target-wide coverage fraction is defined.

Command: `uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_matching_pair_census.py --out acceleration/results/20260930_triangle_matching_pair_census` with `UV_PROJECT_ENVIRONMENT=build/research-venv`.
