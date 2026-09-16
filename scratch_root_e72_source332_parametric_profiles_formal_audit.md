# E72 source 332: three-profile formal exclusion

Source row 332 has one canonical `Q=6` macro with labelled coverage `131,072`.
Its Gram system has one free parameter `t`.  The exact integrality, block-range,
and PSD audit leaves precisely `t=-1,0,1`; an independent principal-minor audit
reaches the same list.

The full-SRG CNF contains one selector for each case and an explicit exactly-one
constraint.  Under each selector it fixes all 126 internal four-vertex fibre
edges and all 210 cross-fibre 4-by-4 block cardinalities.  The three profiles
assign different exact totals to parametric disjoint exceptional blocks, so
their graph sets are pairwise disjoint.

Each profile was isolated by appending its positive selector as one unit clause
to a byte-identical copy of the common CNF payload.  Proof-producing CaDiCaL
returned UNSAT in all three cases, and pinned `drat-trim` accepted every DRUP
trace.  The machine audit verifies the hashes, payload-plus-unit construction,
selector tail, profile completeness, and checker results.

The three selectors partition one macro.  Therefore the formally excluded
coverage is `131,072` once, **not** `3 * 131,072`.

Machine-readable result:
`scratch_root_e72_source332_parametric_profiles_formal_audit.json`, status
`FORMAL_AUDIT_PASS`.
