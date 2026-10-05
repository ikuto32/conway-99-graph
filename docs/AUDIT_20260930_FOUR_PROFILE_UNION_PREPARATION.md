# Prepared exact four-profile union audit

This document specifies a conditional proof-composition audit. It does not approve pending native UNSAT outputs or claim the union excluded before the complete independently checked fifteen-proof gate is available.

Let F be a binary36x60 factor with the pinned six-prism Hadamard coordinate support, prescribed full integer Gram, and every distinct outside-column overlap at most2. An unbalanced group is an identical-support triple with at least one coordinate/fibre count different from1. The previously checked circuit/profile theorem says that an F with exactly four unbalanced groups has exactly one of108 labelled signed profiles. The checked local screen excludes12 of those profiles; the remaining96 are unresolved by that screen alone.

The checked global fibre normalization gives an explicit reversible map from each remaining profile to one of16 representative profiles. It preserves Gram and all outside caps and relabels any residual completion; no target automorphism is assumed. The case0 full-Gram formula includes all initial48 options at each exceptional group and all150 at every balanced group. The separately encoded remaining15 formulas do the same. All these formulas omit cross-group caps, so their checked UNSAT conclusions would exclude a superset of the corresponding Gram-plus-all-column-cap profiles.

After authenticating the case0 proof gate and the complete15 proof gate against their exact independently checked input formulas, partition the108 literal case IDs into12 local-screen exclusions and the96 members of the16 representative orbits. Verify every case occurs exactly once, all orbits are disjoint, every representative is covered exactly once by the proof set, and each proof input is precisely the representative's full initial-domain encoding. Do not replace this set calculation by adding unrelated exclusion counts.

Under those premises there is no such F with exactly four unbalanced groups. Proposed exact derived claim: `C-FIXED-HADAMARD-EXACTLY-FOUR-UNBALANCED-GROUPS-EXCLUSION` revision1. Scope is only the literal fixed-support Gram-plus-column-cap family.

A second conclusion then combines three disjoint possibilities for the number of unbalanced groups:0 through3, exactly4, and exactly5. The independently checked at-most-three exclusion and exact-five theorem are the premises for the first and third parts. Thus any factor in this fixed-support Gram-plus-column-cap family must have at least6 unbalanced groups. Proposed claim: `C-FIXED-HADAMARD-AT-MOST-FIVE-UNBALANCED-GROUPS-EXCLUSION` revision1. It does not exclude the whole support, its core, or the unrestricted Conway99 problem.

Dependencies to authenticate at their exact revisions:

- `C-FIXED-HADAMARD-FOUR-GROUP-CIRCUIT-NECESSITY` r1 and `C-FIXED-HADAMARD-FOUR-EXCEPTION-LOCAL-PROFILE-SCREEN` r1: complete108-profile coverage and12 fixed-profile exclusions.
- `C-FIXED-HADAMARD-FOUR-EXCEPTION-GLOBAL-FIBRE-NORMALIZATION` r1: explicit orbit maps preserving the full restricted family.
- `C-FIXED-HADAMARD-FOUR-EXCEPTION-CASE0-GRAM-ENCODING` r1 and `C-FIXED-HADAMARD-FOUR-EXCEPTION-CASE0-EXCLUSION` r1: exact case0 input and its independently replayed proof.
- `C-FIXED-HADAMARD-FIFTEEN-FOUR-EXCEPTION-GRAM-ENCODINGS` r1 and the pending `C-FIXED-HADAMARD-FIFTEEN-FOUR-EXCEPTION-EXCLUSIONS` r1: all15 exact inputs and independently checked complete proofs.
- `C-FIXED-HADAMARD-AT-MOST-THREE-UNBALANCED-GROUPS-EXCLUSION` r1 and `C-FIXED-HADAMARD-EXACTLY-FIVE-UNBALANCED-GROUPS-EXCLUSION` r1: only for the at-most-five corollary.

Adversarial coverage controls must reject a missing representative, repeated representative, altered orbit member, an overlapping local/representative partition, and any changed proof-to-CNF binding. The final composition audit reuses prior proof replay as a trusted independently checked premise; it does not claim a new DRAT replay.
