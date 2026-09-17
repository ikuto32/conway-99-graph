# Six-coordinate matching-filtered moment build

Model: `PARTIAL_K_SIX_COORDINATE_MATCHING_FILTERED_FULL_MOMENT_PHASE1_V1`. Status at production: CANDIDATE encoding pending independent matching-filter and all-column model checks. No LP was launched.

Both same-sign coordinates at root groups 0, 1 and 2 are free. The family retains 132 baseline K edges, including all seven cross matchings and the eight other same-sign matchings. All same-fibre and unlisted other-coordinate absences remain fixed. The unknown set contains 360 legal edges in the six freed coordinates plus 1,680 disjoint-support edges, totaling 2,040.

The complete original domain universe has 879,449 choices. The producer filter removes 166,728 and retains 712,721. This build reads all recorded surviving original IDs and builds their moment columns directly; it does not allocate or silently substitute an unfiltered matrix. Original-ID lists and original/filtered offsets are preserved in `model.json`.

For each outer pair v<w, the necessary equality is the full outer co-neighbor count plus the projected unknown edge marginal, equal to 2 minus the root-support intersection and fixed adjacency. Every selected full outer neighborhood has twelve members and contributes 66 unordered pairs. The matrix has 84 hard simplex rows, 2,040 hard reciprocity rows and 3,486 moment rows with L1 residual slacks.

The complete augmented matrix is 5,610 by 719,693 with 59,380,799 nonzeros. This producer uses a new direct CSC-column construction, then converts to CSR. Coefficients are stored exactly as int8 values +1 or -1, with integer indices; storage width does not introduce numerical rounding. Eighteen known-valid rook-graph witnesses and thirty-six coefficient/RHS corruptions calibrate this new construction, rather than testing only the older builder. Independent reconstruction of all new columns remains required.

The build completed in 26.843 measured seconds under the preregistered 400-second cap. The saved resource projection is 302,661,547 bytes for the allocated CSC arrays and 599,610,430 bytes for combined CSC/CSR arrays. These are array-size calculations, not measured peak RAM; Python data and conversion overhead are additional. They are not estimates for a later LP solve.

The raw sparse matrix is 85,616,258 bytes, SHA-256 `118707aa109ed5195a38b7a0edda7ea6b3514669e50b9493094d8563097e8b55`. Raw `model.json` is 15,477,067 bytes, SHA-256 `22ff4fbce2f9659877fe115483300bedfb603d60bf96d761a90ffd48a2a0d3c7`. Both remain LOCAL_ONLY. The chunk manifest describes eleven matrix parts and two metadata parts, each at most eight MiB. Both artifacts were restored into `build/six-filtered-model-chunk-replay-20260917/` using the existing separate restoration implementation, checking every part and both full identities; `chunk_replay_receipt.json` records the exact command and result. Original raw files were not overwritten.

Before this build, one exact raw-neighborhood weight transfer from the four-coordinate positive certificate assigned zero to the 120 newly unknown reciprocity multipliers and retained all other integer weights. The resulting bound over all 712,721 retained stars was -2378749843/1048576, giving no exclusion. All weights, original-ID maps and maxima are preserved separately in `../20260917_six_filtered_transferred_certificate/`.

The six-coordinate family is not excluded by the earlier four-coordinate proof. A new positive exact certificate would require independently sound filtering and a fresh raw-neighborhood bound check. A future solver needs separate authorization and a fresh resource preflight. No target-wide existence/nonexistence result or coverage denominator is claimed.
