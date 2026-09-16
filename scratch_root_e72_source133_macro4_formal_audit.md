# E72 source133 macro-4 formal audit

Status: **FORMAL_AUDIT_PASS**.

The derived CNF is byte-for-byte the source133 aggregate CNF after its header, followed only by the four negative selector units in the prior UNSAT assumption core. The unique five-selector disjunction therefore forces macro 4. Its 3,128,709-line DRUP certificate was accepted by the pinned drat-trim checker, excluding 12,288 labelled completions.

Boundary: this certificate covers macro 4 only; it does not itself exclude the four regular source133 macros, and upstream semantic bridges remain separately audited.
