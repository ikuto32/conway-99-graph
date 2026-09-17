# Six-coordinate CPU solve failure

The single authorized CPU solver attempt ended after 666.407 measured solver seconds with `HighsModelStatus.kSolveError`. HiGHS 1.15.1 reported that IPX's interior-point solve failed. It did not reach the preregistered 5400-second cap. The preserved log gives no more specific cause; the cause remains UNKNOWN.

Neither a valid primal nor a valid dual was returned. The reported objective is therefore null; any raw numerical zero is unusable as a feasibility result. Exact evaluation of the returned finite row weights gives 0/1048576, which provides no exclusion. This computational failure does not refute the model, the filter, or any graph family, and it does not invalidate their previously checked necessary-condition proofs.

The model remained the independently audited six-coordinate matching-filtered model: 132 fixed K edges and prescribed absences, 2040 unknown edges, 712721 surviving choices from 879449 original choices. The run used one HiGHS IPM thread with crossover disabled, with no automatic retry or GPU substitution.

The Python wrapper exited zero because it successfully preserved the solver's failed status and raw artifacts. This wrapper exit is not solver success. `execution_end.json` records no Python exception, while `numeric_lp.json` and `summary.json` explicitly record the solver error and invalid vectors.

Certificate diagnostic: `exact_support_bound.json`, SHA-256 `1965c055a6121f09bd097f0f4a7a23d532bce550bdb53931f7fe11acc7405bdc`. Raw vectors: `numeric_lp.json`, SHA-256 `290622fbbb0f224d894fcb4c0b60cbc9b7b2cc02d9e3c0c256522f56878f9eb5`. The solver log, every returned vector, chunk manifests where applicable, process start/end records, process-local heartbeats, actual execution-session observations and resource point observations are preserved.

Before this attempt, launcher version 1 failed before solver creation because it expected different resource-preflight field names. `../preflight_failure.json` and `../protocol_revision2.json` preserve that engineering failure and the narrow version-2 correction. It was not a solver attempt. This run was not restarted.

No process remains running after completion. No mathematical claim was established by this solve. A subsequent experiment needs a separate recorded selection and protocol; the original failed evidence must remain intact.
