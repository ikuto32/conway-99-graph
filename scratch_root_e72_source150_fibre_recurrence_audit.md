# E72 source150 fibre-recurrence independent audit

Status: **SOURCE150_FIBRE_RECURRENCE_AUDIT_PASS**.

The full 5,943-orbit / 2,244,608-mass input was replayed without importing the recurrence implementation. Exactly 1,008 orbits of mass 393,216 fail; these are the complete macro orbits `(0,2)` and `(3,2)`. The remaining 4,935 orbits of mass 1,851,392 pass and remain open.

All 190,176 exceptional pointwise degree rows are unique and recover both Gram-D margins of all twelve disjoint exceptional blocks. The thirteen ordinary fibres independently give option counts `1,1,1,3,3,3,11,3,3,11,3,11,11`.

One of the five PSD Gram matrices has rank two. Every recurrence difference is compared as `H*diff=0`; for PSD `H` this is exactly equality of represented Gram vectors and does not impose spurious coordinate equality. The ordinary--exceptional condition remains one-sided: exceptional degree one, ordinary degree 0 through 4.

The rejected target also has an independently reconstructed minimal three-coordinate obstruction at coordinates `(0,1,3)`: its projected Minkowski sum has 31,768 attainable states and omits the target.

Boundary: this is an exact executable finite-enumeration audit, not a proof-assistant certificate. It does not resolve the passing mass or construct an srg(99,14,1,2).
