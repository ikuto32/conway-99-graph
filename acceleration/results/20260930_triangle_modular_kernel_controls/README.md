This separate, explicitly post-run calibration leaves the original experiment
and report bytes unchanged. The imported producer nullspace routine was
tested against direct enumeration of every field vector for all64 binary
and729 ternary2-by3 matrices. All kernels matched;63 binary and728 ternary
deliberately false kernel vectors were rejected. This calibrates code only,
does not supply independent review, and does not turn the finite failed
exploration into a theorem.

Report SHA256: c3f17ead26ee9f0533f1dca8a58d651f39af67273a7e23522a33766302406f01.

Replay with the locked environment using
`python -B acceleration/control_20260930_triangle_modular_kernel.py --out NEW_DIRECTORY`.
