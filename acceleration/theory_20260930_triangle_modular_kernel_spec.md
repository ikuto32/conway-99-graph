# Bounded modular mixed-equation exploration

Status: producer protocol, not independent approval. No target automorphism,
prism-free assumption, binary field lift or novelty is assumed.

Question: does a modular incidence Gram equality, even with row/fibre margins,
automatically imply modular consistency of FD = 2J - (I+C)F? The previously
audited global target ranks and universal real core PSD/rank identities are
read first and are not rerun as new research.

Frozen cheap experiment: check the known exact SRG243 triangle F/D and the
degenerate rook9 triangle. Over each of GF(2) and GF(3), compute exact kernels
and test at most 128 deterministic perturbations F' = F + u v^T of the known
243 factor. Require Fv=0, sum(v)=0, v.v=0, and zero sum of u in each fibre;
these preserve the modular Gram and all stated modular margins. Search for
a left-kernel vector w with wF'=0 but w[2J-(I+C)F'] nonzero. Such a witness
refutes automatic consistency only in this explicit modular, generalized
parameter setting; it is not a binary factor, Conway99 factor or exclusion.
The modular dimensions/ranks are experiment telemetry unless independently
checked. Save every attempt count and any raw counterexample. Seed 20260930,
120-second wall cap, unchanged uv lock, no solver or floating point.

Controls: actual243 F/D must satisfy all exact integer equations; rook9 has
empty residual. Exact finite-field nullspace vectors are checked by original
matrix multiplication. A changed mixed RHS must fail its supplied exact D.
Corrupted kernel certificates must be rejected. If no witness is found, save
that finite failed route and do not infer universal redundancy.
