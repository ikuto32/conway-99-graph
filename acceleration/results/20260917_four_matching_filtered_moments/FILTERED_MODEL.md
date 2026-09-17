# Matching-filtered four-coordinate moment model

Model label: `PARTIAL_K_FOUR_COORDINATE_MATCHING_FILTERED_FULL_MOMENT_PHASE1_V1`. This is a distinct relaxation on the surviving original local-star choices. Scope is the same four-coordinate family with 144 fixed K edges, all prescribed absences, and 1,920 unknown edges.

The producer reads exactly the surviving original IDs in `../20260917_four_coordinate_matching_filter/run01/`. It removes 59,581 of the 290,460 original probability columns, retains 230,879, and leaves all 5,490 rows and all 6,972 residual slack columns unchanged. Every RHS, bound, slack coefficient and probability cost is preserved. Per-center original IDs and the complete original global column selection are saved in `model.json`.

The resulting matrix is 5,490 by 237,851 with 19,139,922 integer nonzeros. This is exact sparse integer column selection, not coefficient regeneration or a numerical approximation. Producer controls check positive column selection, unchanged slack columns, corrupted coefficients and invalid index lists.

The necessity argument has two parts: the original moment equations must hold for every completion, and each removed star cannot extend to the required matching in its center neighborhood. Both need independent proof within the same fixed-edge/allowed-edge scope. Agreement with the producer's retained-ID list alone is insufficient.

The complete matching-filter audit is recorded separately in `../20260917_independent_review/four_coordinate_matching_filter/summary.json`. The new filtered matrix still requires independent original-column selection and raw-neighborhood checks; later audit results must remain separate from this frozen build evidence.

One 2,400-second HiGHS IPM solve, one thread and crossover disabled, is preregistered in `build_manifest.json`. It may start only after independent filter and filtered-model PASS receipts bind the exact artifacts and the parent resource check approves RAM and disk availability. This duration is a cap, not a runtime prediction. The builder has no solver entry point; the separate gated runner is `acceleration/theory_20260917_four_matching_filtered_solve.py`.

A candidate exclusion requires a strictly positive exact support-function lower bound over all 230,879 surviving choices, plus the independent exclusion of all 59,581 removed choices. A numerical objective or numerical zero alone is not a certificate. There is no unrestricted target claim or assumed nontrivial automorphism.

The compressed raw matrix is 27,081,591 bytes, SHA-256 `4ec700a9605d721d4739cd1e79e0ceb950fac56afb2f479d797a84851d76a1db`. It stays LOCAL_ONLY. Four byte-exact companion parts are described in `chunk_manifest.json`: three parts of 8,388,608 bytes and one of 1,915,767 bytes. Verify each part, concatenate the listed order into a fresh file, and verify the full byte count and hash before replay. The large raw file must not be published by accident; no publication is performed by these tools.
