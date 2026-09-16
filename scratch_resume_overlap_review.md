# Independently checked failure of one prescribed overlap lift and C

The fixed overlap assignment cannot be completed with the prescribed
compression C. A smaller linear necessary-condition relaxation is already
UNSAT. Its proof has been checked by drat-trim and, on an extracted core,
by a separate standard-library-only Python RUP checker.

This excludes only the lift with SHA-256
`fb38e4c009e8c43d0bc043834695c59fff1b01819c3cae43a29353db866be887`
and compression with SHA-256
`7b7ac3ad4d9f36beadcc62589b76f0bf95a13656516d1c7bb2d4af3aec37ee1e`.
It excludes neither every lift of that C nor every E0=0 compression.

## Independent partial-graph and encoding review

The review reconstructs the 84 exact labels and the rooted skeleton
without importing producer code. The saved 168 overlap edges give 357
exposed edges, degrees 14 on fifteen vertices and 6 on the other 84,
and pass all 4,851 partial pair caps. Every overlap block total agrees
with C; all four own-group label quotas per outer vertex equal one.

The completion producer fixes every other overlapping-support edge and
every same-fiber edge absent, and has variables only for disjoint-support
edges. The input C has zero diagonal. Its label quota equalities imply
outer degree 12, hence full degree 14. Its one-way product auxiliaries
satisfy p>=ab, which is sufficient in common-neighbor upper bounds:
choosing p=ab proves equivalence after existentially eliminating p.

These bounds plus exact degrees imply the required equalities. For any
vertex, the sum of actual common-neighbor counts over the other vertices
is 14*13=182. The corresponding target sum is 14*1+84*2=182. Consequently
no individual common-neighbor deficit remains when all counts satisfy
their upper bounds. The producer's claimed exactness is therefore sound
within its explicitly fixed overlap assignment and compression.

## Smaller independently encoded relaxation

Let K be the fixed outer overlap adjacency, and e_uv a Boolean only when
the supports of u and v are disjoint. The independent encoder imposes
the fourteen label quotas at each outer vertex and all 105 disjoint
block totals of C. For each outer pair u,v it keeps only the linear terms
in the necessary cap:

```text
e_uv + sum_(w in K(u), vw variable) e_vw
     + sum_(w in K(v), uw variable) e_uw
 <= 2 - |label(u) intersect label(v)| - K_uv - |K(u) intersect K(v)|.
```

The first term is included only if uv is a variable. All omitted products
of two unknown edges are nonnegative, so dropping them is a relaxation.
Failure of this relaxation is sufficient to reject this fixed lift/C.
No propagated producer assignment is trusted or imported.

There are 1,680 edge variables, 40,161 total CNF variables including
cardinality auxiliaries, and 84,696 clauses. CaDiCaL found UNSAT with
69 conflicts. The hash-bound CNF and proof are preserved. A first Glucose
proof attempt was not accepted; the claimed certificate is the subsequently
generated CaDiCaL proof and its checked derivatives.

The extracted core contains 1,034 clauses, each checked to occur in the
full CNF, and 78 proof additions. The Python checker validates each
addition by assuming its negation and performing elementary unit
propagation to contradiction; the final addition is the empty clause.
It imports no solver, cardinality encoder, or DRAT code. It also checks
every proof literal lies in 1..40,161. It verifies the emitted CNF's
unsatisfiability; mathematical encoding semantics are the separate review
obligation described above.

All deletion lines are removed in separate addition-only proof files;
the original proofs remain preserved. The full addition-only proof
also passes drat-trim in RUP-only mode with no deletion warnings.

## Fast certificate replay

```text
& 'C:/Users/ikuto/.local/bin/python3.12.exe' -B scratch_resume_overlap_review_rup.py
& .\tools\drat-trim\drat-trim.exe scratch_resume_overlap_review.cnf scratch_resume_overlap_review_additions.drat -t 20 -U
```

The first returns `STDLIB_RUP_FIXED_OVERLAP_CORE_VERIFIED` and exit 0;
the second returns `s VERIFIED` and exit 0. The Python result records
all certificate hashes in `scratch_resume_overlap_review_rup.json`.

The discovery script completed its artifact generation and checks but
the tool reported native exit code 1 after its final JSON output. This
is not used as proof evidence. The independent certificate replays above
both completed normally with exit 0.

No submission file was created and no lower-layer exhaustive search was
performed. This finite fixed-choice rejection supplies no uniform
positive E0 bound or global Conway nonexistence result.
