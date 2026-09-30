# Independent review of the conditioned coarse60 arc fixed point

The exact claim concerns the frozen 18 local domains and 135 binary Gram
relations, after setting the six actual coordinate bits of column zero to
zero. It does not use a symmetry or normalization premise. Those explicit
conditions remove 68 values from each of six domains and none from the other
twelve: 408 removals from 2,448 values leave 2,040 values.

The checker reconstructs literal column sets from the authenticated local
domain masks and the raw coarse template. For domains (a,g) and (b,h) with
a different from b, their bit-one sets must intersect in one column if g=h,
and in two columns otherwise. It independently reconstructs every one of
the 2,496,960 forward relation coefficients by ordinary set intersection,
compares them to the frozen encoding metadata, and includes both directions.
Each domain has 15 neighboring domains, yielding 270 directed arcs.

For every conditioned value on every directed arc, the audit saves a live
neighboring value that meets this literal intersection equation. The separate
saved-certificate replay checks all 30,600 witnesses directly against the
raw column sets and six bit conditions, without consulting the reconstructed
relation tables. The support-count histogram is also recorded. Every value
therefore already has support in every neighboring domain. No first AC
revision can remove a value; hence no later removal or re-enqueue is possible,
and the producer's zero-removal fixed point follows without rerunning AC-3.
The original masks, fixed-bit deletion list, final masks and accounting are
checked against this independent reconstruction.

Calibration precedes research checking. A simultaneous-sweep routine is
checked on all 144 two-variable/two-value relations and nonempty initial-domain
combinations against exhaustive enumeration of every possible fixed-point
subset. Known propagating and contradictory cases are included. The two-color
triangle has a nonempty arc-consistent domain but no joint assignment, as
complete enumeration demonstrates. This explicitly tests the gap between
local support and feasibility. Missing arcs/values, invalid witnesses, wrong
units, malformed raw masks, false relation targets and corrupted research
traces must be rejected.

This is an independently checked finite engineering result, proposed as
`C-SIX-PRISM-COARSE60-UNIT-CONDITIONED-ARC-FIXEDPOINT`, revision 1, with the
earlier exact bit-lift encoding and complete local-domain claims as premises.
It omits all outside-column cap propagation. It gives no joint factor, target
graph, residual adjacency, exclusion or target-wide coverage percentage.
The producer's timing is preserved but not independently certified as a
performance result. No nontrivial automorphism of a hypothetical graph is
assumed.

The checking source imports only the Python standard library. Raw artifacts
and previously checked domain/encoding gates are shared trusted inputs; no
producer or previous checking algorithm is imported. Use a fresh directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_coarse60_arc.py --out build/coarse60-arc-review-new
```

The immutable report binds the exact claim revision, source, written audit,
all input/output hashes, controls and explicit limitations. It proposes
VERIFIED/CLEAR only for this finite fixed-point statement. Public availability
is a later publication action and is not inferred from successful checking.
