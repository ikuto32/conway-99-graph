# Eight-coordinate exact moment model build

Freeze before execution. Require completed independent audits of all 84 local
domains and every matching-filter decision. Family: exactly 120 fixed K edges,
2160 unknown outer edges, root scaffold and prescribed absences fixed. No
automorphism assumption. The full-domain population is 2,290,122 choices.

Build one simplex for each center, exact reciprocity for each unknown edge,
and exact common-neighbor equations for all 3486 outer pairs, including the
direct adjacency term allocated at the smaller endpoint. Retain every audited
matching survivor by original ID. Add positive and negative residual slacks
only to the common-neighbor equations, with L1 objective equal to their sum.
The model is a necessary relaxation; zero objective is not a graph certificate.

Use the disclosed frozen direct-column assembler, calibrated on 18 exact rook9
witnesses and 36 coefficient/RHS corruptions. Allocate exact int8 coefficients
and int32 sparse indices. Record the typed-array memory projection first; this
does not measure peak memory. New build limit 900 seconds; inherited exception
labels mention the historical 400-second cap but actual deadline is 900 seconds.
All raw inputs and sources are hashed; output large files have 8 MiB byte-part
companions. Completed in-memory columns alone are not a resumable matrix.

Success requires a complete matrix/model followed by independent rederivation
of every retained column, every RHS, all bounds, costs, and6972slack columns.
No LP or GPU solve is authorized by the build program. A later solver wave
needs its own protocol, numerical thresholds, resource limits and exact
raw-neighborhood certificate checking. Failure or any cap preserves partial
artifacts and supplies no mathematical exclusion.
