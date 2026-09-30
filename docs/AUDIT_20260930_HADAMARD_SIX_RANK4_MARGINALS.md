# Independent integer marginal enumeration

The reviewed universe is the nine rank-four sextets remaining after the
complete six-exception kernel census. At every coordinate a and fibre f,
the six group deviations are integral, lie in[-1,2] on incident groups,
vanish on nonincident groups, and belong to the augmented global-incidence
kernel. The three fibre vectors sum to zero at each coordinate. Every
group/fibre quota sum over the twelve coordinates must vanish. A group is
active if any of its deviations is nonzero; all six must be active.

The independent checker enumerates all4^6 full group vectors and checks
literal matrix products and support conditions. It constructs every ordered
fibre triple by selecting two vectors and testing their negative sum in the
same complete domain. It does not use the producer's incident-only loops
or its two-coordinate kernel parametrization to construct the domains.

The domains are small enough to enumerate all121869 complete labelled
coordinate-profile sequences directly. A recursion visits every sequence
without merging equal states, maintaining all eighteen group/fibre quota
sums and the activity mask. Prefix visit counts are recorded at every
depth. Each producer four-sum projection is then proved injective on the
two-dimensional rational kernel by its nonzero2x2 determinant. The direct
full-quota counts are projected only for comparison with every saved DP
state, count and witness. This independently checks all108 layers and the
positive and zero terminal counts; the producer's DP recurrence is not
used to derive those counts.

The exact counts in saved sextet order are96,108,0,96,96,24,0,0,564. All984
positive labelled choice paths are saved by the independent checker.
Cases2,6,7 are excluded even by this necessary linear/count relaxation.
The other six cases remain open: feasible marginals need not be realizable
by local column triples, let alone satisfy the full quadratic Gram, outside
column caps or any residual graph equations. The984 units are labelled
marginal profiles, not graphs or a target-wide progress denominator.

A previously checked four-group circuit provides six nonzero and one
balanced feasible marginal profile as a positive control. Missing states,
wrong path counts, duplicate keys, corrupted choice paths and activity,
incomplete domains and violated integer bounds are rejected. No producer
code is imported and no native solver or numerical arithmetic is used.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_six_rank4_profiles.py --out acceleration/results/20260930_independent_review/hadamard_six_rank4_profiles
```
