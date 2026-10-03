# Independent audit of four fixed-core factor instances

The exact previously checked variable-core encoding allows each M1 and M2
to be a perfect matching and P to be a permutation matrix. Its raw variable
IDs are independently reconstructed here in lexicographic order, rather than
copied from the new producer's unit lists.

Fix a selected matching. The six positive edge units cover every coordinate
once. The base exactly-one constraint at each coordinate then forces every
other incident matching variable false. Thus those units are equivalent,
within the base domain, to fixing all 66 matching entries. Similarly the
twelve positive entries of the selected permutation cover each row and each
column once; the base exactly-one rows force all its other entries false.
The converse holds because a factor with that exact core satisfies every
listed positive unit. This is an equivalence for the restricted base factor
problem, not a theorem that a target must have one of these cores.

The audit independently rebuilds all 132 matching and 144 permutation IDs,
the 36-vertex cubic adjacency, the full 39-vertex adjacency, all 741 local
pair caps and all 1,296 integer Gram entries per selected core. Every
augmented CNF has an exact new header, every original 518,160 clause byte,
and exactly its 24 positive unit clauses. No auxiliary variable is changed.
The complete original encoding has its own pinned independent audit; it is
not re-proved by a mere file hash or this small extension check.

Independent controls enumerate all 15 matchings on six coordinates and all
24 permutations on four coordinates to check the fixing argument. A small
positive byte fixture and altered headers, base clauses, unit signs/order,
missing/duplicate units, semantic mappings, raw cores and Gram values test
the rejection paths. No producer implementation is imported.

All four choices are restrictions. No target automorphism, target asymmetry,
universal identity-P reduction, full factor, residual D, target graph or
nonexistence conclusion is assumed or obtained.

```
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_connected_fixed_core_cnf.py --out acceleration/results/20260930_independent_review/connected_fixed_core_cnf
```
