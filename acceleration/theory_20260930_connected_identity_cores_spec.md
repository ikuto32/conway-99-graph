# Four connected identity-P construction domains

Preparation only; zero native solver/GPU/search calls. Results are CANDIDATE
until a separate validator checks the exact raw cores and selection coverage.
Existing engine, wrappers, gates, uv.lock and ledger remain unchanged.

The deterministic rule is frozen before any enumeration: traverse the eleven
M1 stages in increasing stage index and their second-orbit representatives in
the frozen census order. For each stage, identify its first M2 representative
whose36-vertex cubic core with P=I is connected. Select the first four distinct
M1 stages having such a representative. If fewer than four stages qualify,
report the actual number. Scan all3580 candidates to retain complete eligibility
and per-stage counts; no ranking by Gram objective, heuristic score or search
success is performed. Connectivity is computed on the36 core vertices, not
on the39 graph (the distinguished triangle would trivially connect fibres).

M0 is coordinate xor1; internal M1,M2 are the exact saved representatives.
All three cross-fibre matchings, including P, are identity. The independently
verified identity-P local-construction theorem supplies context; P=I is a
chosen domain restriction, never asserted without loss of generality for a
target. Every candidate receives a direct positive39-graph pair-cap check.
The four selected raw artifacts contain M0/M1/M2/P coordinate maps, full39
adjacency, raw36 core, component memberships, canonical C0 nonmatching pairs,
three nonmatching-edge catalogs and exact prescribed Gram coefficients.
Each selected Gram is checked both against literal full39 common counts and
12I-C-C²+2J-diag(J12,J12,J12). Within-fibre Grams equal the incidence Gram of
the corresponding full60-edge catalog, and every catalog has row degree10.

These are four local construction domains only. No36×60 full factor, residual
D, target graph, target automorphism or general nonexistence is claimed.
Independent review must separately reconstruct rawgraphs, localcaps,
connectivity, catalog andGram coefficients and the complete deterministic
selection from the authenticated3580 census. Later generic-core GPU admission
requires that new gate; this preparation does not change existing admission.

Controls precede the catalog scan: an actual9-vertex rook graph produced at
n2 satisfies its complete exact SRG identity; a connectedn4 localconstruction
passes all paircaps; an extra root-to-foreign-fibre edge and a malformedmatching
must be rejected. A corrupted selected Gram coefficient is rejected.
Resource cap60seconds; deterministic standard-library arithmetic; tqdm stages.

```
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_connected_identity_cores.py --out acceleration/results/20260930_connected_identity_cores
```
