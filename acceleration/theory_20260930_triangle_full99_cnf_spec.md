# Fixed Wave154 triangle-root full99 completion: exact CNF build

Selection was made before this build: use the displayed Wave154 Q1 because the
saved exact propagation leaves1927unknown graph edges, versus1928for Wave151.
This is an input-size rule over the two recorded cases, not a runtime forecast,
symmetry coverage argument or exclusion of the unselected case.

Question: does the exact Wave154 triangle-root scaffold and Q1 incidence factor
extend to a complete target99graph when the residual60vertex blockD is included?
Archive waves151/154 searched the C-only extension; their negative solver reports
have no exported proofs, and Wave154's180-second CaDiCaL proof attempt timed out.
The new full99 problem includes all graph equations and residualD compatibility.

Freeze the input `results/20260930_triangle_partial99/wave154.json`, SHA256
e8581587313cf8207799dcf781d8469eb66a699687e023faf0a435000ab9f69b.
Use its final_adjacency only after preserving the initial matrix and all563
ordered forced-edge records. Independent scope/propagation review is mandatory
before any solver-based inference. This build may proceed while that audit runs.
The graph family fixes all three internal matchings, F01=F02=I, F12=shift6, and
the two incidence groups C0/C1; it is explicitly conditional. There is no claim
that an arbitrary target has this scaffold or Q1, and no target automorphism.

Assign lexicographic unordered-edge variable IDs to the1927remaining unknowns.
Encode all99degree equalities and all4851unordered-pair equalities
`sum_w A[u,w]A[w,v]+A[u,v]=2`. Constant-fold known entries. Introduce an exact
bidirectional AND variable for each remaining product. Use the existing frozen
exact bidirectional prefix-threshold recurrence throughk+1, asserting>=k and
not>=k+1. This directly specifies the full target identity, with no floating
arithmetic, relaxation, global-tight-count shortcut, or omitted pair equality.

Reuse only the disclosed generic producer mechanics from the earlier exact
encoder. Independently checking those helpers previously does not approve this
new scope/model/CNF; a separate complete reconstruction is still required.
Calibrate the graph validator and gate/counter truth tables before building.

Build limits:120seconds and8GiB working set. No SAT solver invocation. Save raw
DIMACS/model, full mappings, counter rows/states and clause ranges, exact source/
input/tool hashes, a resource receipt, and gzip parts smaller than10MiB with
decompression/hash replay. The no-file census predicts429476variables,
1486729clauses,104024ANDproducts; report any deviation without changing the input.

Future solver protocol is separate: first obtain independent propagation and
complete encoding gates and a dedicated conditional full99 SAT-object checker.
Only then consider one300-second native proof-enabled run with the already
calibrated ext4 path,4GiB address space and10GiB proof cap. SAT must decode to a
complete independently checked target graph. UNSAT requires a complete checked
trace and proves only this fixed family; it does not resolve unrestricted99.
