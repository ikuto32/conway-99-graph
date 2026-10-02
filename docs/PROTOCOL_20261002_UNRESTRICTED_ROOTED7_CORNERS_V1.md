# Unrestricted rooted7 eight-corner screen v1

Producer /root/structural. Exact raw operator model SHA9f636889690071f69ad7a103b02abb2f43a5bbc2d2114c87a779da29c0f647a1,
2810 variables,11769 rows,89350 terms; independent necessary-encoding audit
e7631851f9cc5716c9d8a1bf5b30f9a4644d8e2170f116d1bb30378fbeb16d70.
These inherited audit results do not approve new producer certificates.

Question: Does the continuous nonnegative rooted7 necessary count model cut
the unrestricted exact local rooted6 parameter domain? Every variable represents
an actual integer count in a hypothetical graph, but this screen relaxes it to
a nonnegative rational value. No graph realization or target automorphism is
assumed. No prism-free premise or uniform secondary profile is imposed.

Freeze all8 vertices in lexicographic c,a,b order: c in{0,2},a in{0,20},
b in{0,9+c/2}. Freeze all651 integer triples c=0..2,a=0..20,
b=0..floor((18+c)/2). No omitted failures or favorable subset.

HiGHS1.15.1, locked root uv environment, simplex/presolve off/threads1/seed0,
primal/dual feasibility tolerance1e-10. Every original column is scaled by a
positive integer: rooted7 flag columns choose(97,5), aggregate/slack columns
1420. Every row is scaled by the maximum absolute scaled coefficient, absolute
integer RHS and1. Record these exact scales. Each of8 numerical solves receives
at most20 seconds, also bounded by the remaining shared invocation time divided
among remaining corners, retaining60 internal seconds for exact checks/save.
No implicit second numerical LP to request a missing ray: query getDualRayExist
and retrieve only a reported stored ray. Save every returned numeric vector,
status and valid basis. Time limits and floating infeasibility are UNKNOWN.

Rational lifts use individual maximum denominators1,10,1000,1000000, then take
their exact LCM. A primal passes only if every integer row times its common
denominator matches exactly and every numerator is nonnegative. A Farkas vector
passes only if all2810 original column products are nonnegative and its exact
affine RHS evaluated at the recorded point is strictly negative. Try both signs.
Calibrate actual tiny positive primal and stored negative ray, deliberately
wrong coefficient/primal and reversed-ray controls before scientific corners.
These are producer controls, not independent approval.

If all8 corner primals pass producer exact checking, reconstruct every651
profile with weights t=c/2,u=a/20,z=2b/(18+c), factors(t or1-t),(u or1-u),
(z or1-z) corresponding to the8 vertices. They sum to1 and reproduce all3
parameters exactly. Save complete numerator vectors/common denominators and
check every11769 literal row/nonnegative coordinate for every profile. Count
integer vectors only if every numerator is divisible by its denominator.
If any exact ray exists, evaluate that exact affine cut on all651 profiles.
Uncovered cases remain UNKNOWN; only8 numerical attempts, not651 solves.

Allocation300 outer/260 worker,60 internal reserve. Prior conditional4 LPs took
0.53 combined numerical seconds and210 exact convex checks24.2 total seconds;
this8-corner/651-profile model is only44 additional variables/20 additional rows.
The allowance is evidence based, not a historical cap. No automatic retry or
extension. Checkpoint every completed corner/basis and retain failed controls.
All meaningful raw vectors/relations and profile classifications need a different
author's exact checker bound to this raw model/source/protocol before promotion.
Literal continuous feasibility is not integer count feasibility or a graph.
