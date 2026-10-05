# Unrestricted rooted8 content-divided GF2 screen V1

This is a new experiment. The conditional rooted8 sources, gates, checkpoints
and original experiments remain unchanged.

Frozen raw model:
`acceleration/results/20261003_rooted8_unrestricted_extension01/model.json`,
SHA256 `b143c129fce1f450b54a397d6d508ecb81a67870c2bafd2e9f50dee0bda83f1a`.
It has 23334 variables and 86434 equations with affine RHS order
`constant,c,a,b`. Full scientific execution additionally requires the separate
complete catalogue and necessary-model audit report paths/hashes and a new ROOT
pre-output scalar/content-checker calibration. Engineering controls do not
authorize full elimination.

## Frozen question and population

Do the appended unrestricted rooted8 marked/product equations create an exact
GF2 relation inconsistent with any of the 651 integer primary profiles
`0<=c<=2`, `0<=a<=20`, `0<=b<=floor((18+c)/2)`?
Use all profiles in lexicographic `(c,a,b)` order. No prism absence, common
secondary profile, graph automorphism, nonnegative sufficiency or target-wide
coverage assumption is introduced.

Combine duplicate column coefficients in each literal original row, remove
exact zero coefficients, and divide all coefficients and all four affine RHS
components by their positive greatest common divisor (zero row content becomes
one). This gives equivalent integer equations; consistency modulo two is only
necessary for integer solutions. Save every normalized original-index row and
its divisor. A divided-row XOR is not an undivided original-row mod2 relation.

Simultaneously reduce the coefficient and four-RHS bitsets, retaining exact
original-normalized-row XOR bitsets. Emit each discovered nonzero affine relation
with every selected original row index and its four RHS residues; independently
check all 23334 column sums. Classify all 651 profiles. If there is no such
relation, emit four complete 23334-coordinate binary primal vectors for the
individual RHS components. If some relations exist, emit a complete primal for
every compatible parameter parity class and map each surviving profile to it.
Neither a computed pivot count nor producer checks establish an independently
approved rank. Do not record a rank claim.

## Calibration and acceptance

Before science freeze this source/protocol and run finite controls in a separate
contained invocation. Test duplicate terms and content 2/4, zero rows, negative
coefficients, four independent RHS components, a relation excluding odd c only,
complete eight-parity brute-force truth-table agreement, full vector and relation
corruptions, coefficient/RHS/sign/divisor changes, and exact whole/split
checkpoint reconstruction. Distinguish producer calibration from mathematical
approval. The separate ROOT checker must be calibrated before full output exists.

Independent verification must recompute the complete normalization from the raw
integer model; verify every row of every full primal or every column and RHS of
each row relation; check every frozen outcome; and deliberately corrupt actual
full-width artifacts. No producer import or elimination algorithm is required
by that scalar checking path. Bind source, protocol, model, audit/calibration,
commands, versions and every raw artifact hash. A successful finite gate is
not a full endpoint check.

## Resources and stops

Proposed full allocation: 300 seconds outer, 260 worker, with 40 worker seconds
reserved for serializing useful progress and exact elimination checkpoints.
The prior root7 2810x11769 Python-int elimination took 0.77 worker seconds; old
conditional native root8 calculations took tens of seconds. Neither determines
the new Python fill-in cost. The uncompressed full-width bitset estimate for
23334 pivots is at most about 320 MB before Python/container overhead; raw and
normalized parsed JSON adds memory. Require at least 4 GiB actual available
physical memory when a Windows observation is supported; record unavailable
observation explicitly on other hosts. Reassess recorded progress and memory
diagnostics rather than extrapolating a guaranteed completion time.

Save prefix progress every 10000 processed rows. Stop checks occur at row
boundaries and during long reductions. If the internal reserve is reached, save
an exact compressed elimination checkpoint with source/input pins, the processed
row prefix, all pivot coefficient/RHS/origin bitsets, and all discovered relations.
Resume requires a separately declared invocation, unchanged source/input closure
and strict checkpoint bounds. No automatic retry or deadline extension. An
incomplete or partial checkpoint is preserved but is not accepted for restart.

Success means complete independently checked literal consistency or exact
profile exclusions, not graph existence. Timeout/error means “not completed
within the allocated budget”; no nonexistence inference is permitted. An
unrestricted target interpretation requires the independent necessary-model and
coverage gates; the literal row calculation itself is narrower.
