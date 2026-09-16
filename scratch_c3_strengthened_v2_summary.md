# Strengthened fixed-point-free C3 branch (v2)

## Exact model

`scratch_c3_strengthened_cpsat_v2.py` combines the 33-orbit quotient and
the full Z/3 phase lift in one CP-SAT model.  It uses only the remaining
trace cases `t=6,27`, enforces off-diagonal multiplicities in `{0,1,2}`, a
12-regular support, a 2-regular multiplicity-two graph on the non-K3
orbits, and every off-diagonal entry of

`M^2 + M = 12 I + 6 J`.

The phase lift has all 1,617 unordered-pair orbits.  It imposes
`common(u,v) + adjacent(u,v) <= 2`; degree 14 and the global wedge count
make every one of these inequalities exact.  The current revision also
links each nine-term phase convolution exactly to the corresponding
quotient product `m_ik*m_kj` (16,368 links), and links each three-term
internal convolution to the appropriate double-edge bit (1,056 links).
Thus the implication-only AND helpers cannot introduce spurious models.

Any feasible assignment is expanded to 99 vertices and independently
checks all 4,851 vertex pairs, all degrees, and the 693-edge count before a
witness JSON is written.

## Safe symmetry coverage

The double-edge 2-factor is canonicalized completely and without loss:

* for `t=6`, all 191 nondecreasing partitions of 27 into cycle lengths at
  least 3 are selectable, and each selected partition is represented by
  consecutive canonical cycles;
* for `t=27`, the two shapes are `C6` and `2C3` and are separate modes.

After fixing this 2-factor, the model deliberately places **no sorting or
canonical-word constraint** on the independent-orbit word
`(x(0,j))_{j>=t}`.  Therefore every root-support word is retained (usually
with residual duplicates); exact coverage does not depend on computing
orbits under the 2-factor automorphism group.  Only the K3-orbit incidences
`x(0,1),...,x(0,t-1)` are sorted, since that disjoint class remains freely
permutable.  Per-orbit phase rotations set the possible orbit-0 matching to
shift zero and do not change support or the double 2-factor.

## Bounded results

Safe integrated runs gave:

* `t=27`, double shape `2C3`: **INFEASIBLE**, independently repeated after
  adding the exact convolution links in 28.791 s (159,880 branches, 610
  conflicts).  Result:
  `scratch_c3_strengthened_v2_t27_2c3_linked_result.json`.
* `t=27`, double shape `C6`: **UNKNOWN** after 300.536 s (831,102 branches,
  3,980 conflicts).  Result:
  `scratch_c3_strengthened_v2_t27_c6_result.json`.
* `t=6`, all 191 double-2-factor shapes: **UNKNOWN** after 300.899 s
  (2,162,066 branches, 273,659 conflicts).  Result:
  `scratch_c3_strengthened_v2_t6_result.json`.

The two 300-second records were produced immediately before the final
convolution-link strengthening.  Linked reruns for those two open branches
were stopped on request and produced no terminal result.  Consequently the
statuses remain UNKNOWN, not evidence of infeasibility.

## Important audit note about the older quotient script

The earlier `scratch_c3_quotient_cpsat.py` simultaneously fixed a `C6` or
`2C3` labelling and prefix-sorted the orbit-0 support over all six
non-K3 vertices.  Once the 2-factor labelling is fixed, only its residual
automorphism group is available; arbitrary prefix sorting is not generally
valid.  Its shape-specific statuses, especially the old `2C3` INFEASIBLE
record, must not be used as a proof.  The fresh v2 `2C3` result above avoids
that incompatible symmetry break and is the safe computational result.

No feasible lift was found, so no `submission.txt` was created.
