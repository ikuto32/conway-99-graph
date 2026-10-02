# Independent literal root7 corner and interpolation audit v1

Claim scope is the frozen literal2766-coordinate11749-row integer affine matrix,
not the necessity or interpretation of these rows for an SRG. Inputs are the
exact root7 model and four corner JSON artifacts with pinned SHA256. Ignore
floating values, solver status, tolerance and claimed lifting success. Check
every exact rational pair is an integer numerator with denominator1 and check
all coordinates nonnegative. For each corner, independently form every sparse
integer row sum and compare against the recorded affine RHS at that corner.

For each of all210 integer pairs0<=a<=20,0<=b<=9, form the full2766-coordinate
scaled vector using corner weights [(20-a)(9-b),a(9-b),(20-a)b,ab] and denominator
180. Verify nonnegative weights, sum180 and exact parameter interpolation, then
recompute all11749 row sums with arbitrary-precision Python integers and compare
against180 times the literal affine RHS. Save every full vector, not a sampled
selection or inference from corner checks. Separately identify vectors whose
every coordinate is divisible by180. Rational interior witnesses establish no
integer feasibility claim; named integral witnesses establish literal-model
feasibility only. No producer imports, LP solver, numerical verification,
semantic derivation, graph construction or target exclusion are involved.

Calibrate on nonsingular positive, singular/zero-row positive, and negative
coordinate satisfying its rows. Falsification controls change an actual corner
coordinate, actual row coefficient and actual RHS constant, checking every row;
all must fail. Reject malformed rational denominator/vector length, floating
coefficient/RHS and out-of-range coordinate syntax. Control reports preserve
acceptance and mismatch details. Shared trusted execution components are the
standard Python parser/arbitrary-precision integers/hashes plus policy helpers.

Predeclared allocation300s outer/270s worker includes model hashing/JSON parsing,
four corner matvecs, controls, all210 full vectors, exact matvecs and output hashes.
There are86129 literal term occurrences, so the210 checks require about18million
integer term products; no matrix inversion or exponential search. Keep20s worker
reserve. Use the existing locked root uv environment, current local Windows Job
supervisor, fresh output/receipt paths, and save all full witnesses in compact
JSONL. Independent verifier is /root/native_driver, distinct from the root7
model/certificate producer. Prior annealer producer work has no role in this
checking path. No git index or ledger mutation.
