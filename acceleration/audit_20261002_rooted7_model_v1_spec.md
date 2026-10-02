# Independent rooted7 marked/reroot model audit v1

Question: does the frozen 11,749-row, 2,766-variable model correctly encode the
stated necessary rooted7 counts for a hypothetical prism-free srg(99,14,1,2)?
The prism-free premise remains UNKNOWN. No graph automorphism is assumed.

Use exact previously independently checked rooted7 catalogue/rooted6 count
artifacts, with pinned independent reports. Independently reconstruct every
marked six-to-seven deletion/degree/pair extension coefficient. For each free
deletion enumerate every root-fixing lower isomorphism and check that the orbit
coefficient is invariant. Mark orbits are finite induced-flag coordinate
normalizations only. Independently enumerate all reroot choices: if the other
primary root belongs to a rerooted-six subset, its union is a primary six-set;
otherwise its union is a primary seven-set. These disjoint collision/union
contributions exhaust each sum. Four new-root partitions have cardinalities
(71,12,12,2), obtained directly from n=99,k=14,lambda=1,mu=2.

For each actual edge new-root use the separately checked conditional universal
six-count vector. For each nonedge new-root use its independently checked affine
six-profile with actual coordinate counts a_w in[0,20], b_w in[0,9]. Their sums
are separate aggregate variables for each anchor/partition. The aggregate
rectangle bounds follow by summing individual bounds, with nonnegative slacks.
There is no assumption that distinct actual roots have equal nonedge profiles.
Substitute the primary six-profile exactly and compare every raw integer row,
variable descriptor, known term, aggregate coefficient and affine right side.

Calibration: independently construct Petersen as the disjoint-pair Kneser graph
KG(5,2), check its exact srg(10,3,0,1) identities and prism-free property, count
all 90 ordered six-root profiles and all 60 primary nonedge seven-root profiles,
and check every unspecialized extension/reroot relation. Reject changed counts,
coefficients, RHS, aggregate upper bound and missing row controls. No numerical
solver or producer code is imported. Shared components are the earlier independent
small-graph matrix/bit/DSU helpers, Python arithmetic, SHA-256 and policy runtime.

Declare600seconds outer/570seconds inner; dictionary orbit maps cover fewer than
2^21 labelled seven-graphs and the sparse model, expected under1GiB memory.
Previous six-audits took under7seconds and catalogue exhaustion3seconds, while
all rooted7 coefficient/reroot operations may take several minutes. Reserve30
seconds inside for diagnostics/checkpoint. Success means complete exact necessary
model reconstruction and all calibrated controls, without new exclusion or
claim of graph realization. Save failure on any missing/mismatched artifact or
unfinished budget. Raw discovery artifacts are never rewritten.
