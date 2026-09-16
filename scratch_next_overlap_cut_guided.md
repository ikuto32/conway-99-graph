# One bounded cut-guided overlap experiment

The single authorized run returned **UNKNOWN after 45.047 seconds**.
It produced no candidate and was not extended. UNKNOWN proves neither
feasibility nor infeasibility.

The model retains the saved-C overlap totals, root-label quotas, and all
partial pair caps. It excludes the 640 sign images of the original and
four saved alternatives, and adds five unrelabeled no-gamma capacity
cuts using 4,881 exact-max constraints. The 65,520 existing one-way
product variables are retained; 24,492 occur in the cut bank.

For each affine coefficient w the model enforces z=max(0,-w) exactly.
Each cut is R+sum(z)>=0. Every product coefficient in R is negative:
replacing a true product by its one-way Boolean overestimate decreases R,
so it cannot allow a violating overlap assignment to pass a cut.

The solver used one worker and reached 449,059 branches, 51 conflicts,
and 47,930 LP iterations. Model validation passed. The compiled input SHA
is `f0f2a851b782f37ddd32e8d3af10da07c35f3ddd2b78a16448fd503fab13277d`.
The result audit confirms that hash and all 19 provenance leaf hashes.

Files: `scratch_next_overlap_cut_guided.py/.json`,
`scratch_next_overlap_cut_guided_model.json`, and
`scratch_next_overlap_cut_guided_audit.py/.json`.
The audit status is `CUT_GUIDED_NO_CANDIDATE_RETURNED`; no graph audit can
be claimed when no candidate was returned. No LP/dual follow-up, central
ledger change, or submission file was produced.
