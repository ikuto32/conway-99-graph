# Rooted8 explicit weaker product subset diagnostic, version 2

Input full model SHA256:
`a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b`.
Select zero-based original row indices `0..11749` inclusive and
`82046..85873` inclusive. This is 15,578 rows: all 11,749 prior root7 rows,
the root8 total row, and every 3,828 universal5 product row. Omit only the
70,296 remaining marked7-to8 rows. Preserve all 23,019 original variables and
their nonnegative domain. Save the complete original-row map, and bind it in
the manifest/output hashes. This subset is frozen before guide outcomes.

The population remains all 210 profiles `a=0..20,b=0..9`, no omission. Guide
the four rectangle corners `(0,0),(20,0),(0,9),(20,9)`. Test every population
point against any exact affine Farkas inequality. If all four corners have
exact primals, construct and replay all 210 convex integer-numerator vectors.
Partial corner success certifies only those corners; all other points remain
UNKNOWN unless individually excluded by an exact inequality.

A positive primal proves only this **weaker** literal relaxation. It does not
certify the omitted marked constraints, integer counts or graph feasibility.
A Farkas multiplier on the subset can be zero-extended to all original rows:
all original variable products must be nonnegative and the selected affine RHS
strictly negative. A separate agent must check the full original row mapping,
zero extension and every column/RHS. Target-relevant conditional exclusion also
requires independently checked catalogue/model necessity. No global prism-free
premise or target-level resolution is inferred.

V2 uses the measured full-wave cost to remove 70,296 redundant equality rows
for this diagnostic. HiGHS guides use one thread, seed zero, simplex,
presolve OFF, tolerance `1e-9`, integer column/row scales recorded explicitly.
Only exact replay accepts a result. Grid denominators are frozen at
`1,10,1000,1000000`. Primal numerators are rounded guide values times the common
denominator; every exact integer row must equal RHS times that denominator,
and every numerator must be nonnegative. Farkas multipliers are integer-rounded
normalized ray values on the same grids, tested with both signs on every raw
column and affine RHS. Failed rounding is UNKNOWN, not a refutation.

Every native phase records actual elapsed time and basic solver diagnostics.
Preserve numerical solutions at every status. Save valid bases; a resume
requires identical source/spec/model/environment pins and the same point's
basis. A basis is only a numerical warm-start, never an exact certificate.
Query `getDualRayExist` first. Retrieve `getDualRay` only if a stored ray exists,
so an implicit additional LP is never deliberately requested. Missing rays
remain UNKNOWN. The outer supported supervisor bounds all preprocessing,
native phases, exact checks, basis transfers and retries in one invocation.

Before scientific launch, separately execute `--controls-only` from the frozen
source. Require exact positive/corrupt primal/Farkas checks, an actual stored
infeasibility ray with presolve OFF, basis save/reload plus exact replay, and a
deliberately malformed basis rejection. These controls are producer calibration,
not independent mathematical approval.

First diagnostic allocation is outer 600 / worker 540 seconds, with 60 seconds
of worker time reserved for exact checks/checkpoints/shutdown. Four native
guides share the remaining actual worker time. The full 85,874-row wave consumed
hundreds of seconds per unresolved native phase; the reduced row count is a
new experiment, not an assumed speedup. Save each completed corner and basis.
If incomplete, preserve failure and exact restart procedure. Reassess upon
significant evidence and before any new allocation; never extend an existing
invocation. No automatic resume is authorized.

Target resolution: UNKNOWN. Overall search coverage: UNKNOWN; no validated
denominator. Neither subset completion nor fewer rows measures graph coverage.
