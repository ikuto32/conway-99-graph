# Four-coordinate full moment build

Model label: `PARTIAL_K_FOUR_SAME_SIGN_COORDINATES_FULL_MOMENT_PHASE1_V1`. Status at build: CANDIDATE necessary encoding pending independent reconstruction. This tool has no solver entry point and ran no LP.

The model keeps all 290,460 original domain choices from the four-coordinate pilot, with no matching or pair filter. Exactly 144 baseline K edges and the prescribed absences remain fixed. Only 240 legal same-sign matching-coordinate edges at root groups 0 and 1, plus 1,680 disjoint-support edges, may vary.

For every outer pair v<w, the necessary moment equality remains

    sum_(t,S) 1[{v,w} subset N_B,outer(t) union S] z(t,S) + x(v,w)
      = 2 - |support(v) intersect support(w)| - B(v,w).

Here x is the smaller endpoint's local marginal for an unknown edge and zero otherwise. All selected full outer neighborhoods have twelve vertices, contributing 66 co-neighbor pairs each. Every actual graph completion yields one local star per center and satisfies the moment equations. Fractional domain mixtures are only a relaxation.

The complete augmented integer matrix has 5,490 rows, 297,432 columns and 24,085,997 nonzeros. Its rows are 84 hard simplex equations, 1,920 hard reciprocity equations and 3,486 full moment equalities with two L1 slack columns per equation. Exact RHS, costs, bounds, supports, fixed and unknown edge identities, pair order and original domain offsets are in `model.json`.

The build took 12.093 measured seconds. All 18 exact rook-graph witness controls and 36 coefficient/RHS corruption controls passed. These producer checks do not replace independent new-domain completeness and all-column model verification.

The preceding two-coordinate certificate was tested through one preregistered raw-neighborhood transfer, preserving y and mapping q by edge identity with 120 new zero weights. Evaluation of every new star gave -1823266244/1048576, which supplies no exclusion. Its full failed evidence is in `../20260917_four_matching_transferred_certificate/`.

The raw compressed sparse matrix `integer_augmented_csr.npz` is 34,329,990 bytes, SHA-256 `c6226a5c7d00b61c87bb2ef49a219d518ffaf71d871169be4fc9b2511c922591`. It remains local. `chunk_manifest.json` specifies five byte-exact publication companion parts: four of 8,388,608 bytes and one of 775,558 bytes. To restore into a fresh file, verify every part's recorded byte count and SHA-256, concatenate the five parts in the listed order, then verify the recovered total byte count and full SHA-256. A part hash is not a substitute for the corresponding file. No publication was performed by this tool.

Independent reviewers may use the local raw matrix, or verify the part concatenation before checking its integer contents. The parts, manifest, exact model metadata and source must be preserved together for public replay. Large raw files should not be added to the publication commit.

No solver budget or configuration has been chosen for this larger model. Independent domain/model gates and a later resource decision are required first; the parent research wave is examining matching-filter reductions before that decision. No process remains active after this build, and no broader-family exclusion or unrestricted target resolution is claimed.
