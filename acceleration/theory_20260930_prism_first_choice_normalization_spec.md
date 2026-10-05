# Six-prism first-column normalization, version 1

Question: can the complete fixed-six-prism column-factor encoding be restricted
to choice ID 1 in its canonical C0 column (0,2) without losing satisfiability?
The proposed answer is a relabelling equivalence, not an assertion that any
factor or target graph has a nontrivial automorphism.

The fixed core has rows (g,a,b), with fibre g in {0,1,2}, prism component a in
{0,...,5}, and bit b in {0,1}; row index is 12g+2a+b. Edges are the bit flip
within one fibre and equality of (a,b) between distinct fibres. Consider all
384 maps (g,a,b) -> (g,p(a),b xor e(a)), where p fixes components 0 and 1,
permutes components 2,...,5 freely, e(0)=e(1)=0, and the remaining four flips
are arbitrary. These maps preserve the core, its Gram matrix, and fibres.
They fix the two C0 coordinates 0 and 2. On every other canonical C0 column
{i,j}, simultaneously relabel the column to {sigma(i),sigma(j)}. This is a
bijection of the 60 nonmatching coordinate pairs, and restores canonical C0.

Each of the 96 choices in column (0,2) assigns two of components 2,...,5 to
fibre 1 and the other two to fibre 2, with four arbitrary bits. Map those two
fibre-1 components to components 2,3, and the other two to components 4,5;
flip each selected bit to zero. The resulting choice is exactly ID 1.
Thus the orbit has all 96 choices. The subgroup stabilizing ID 1 has size 4.
The build will enumerate the complete 384-element action, verify closure and
inverse existence, and retain one explicit transport to ID 1 for each choice.

For each map the build checks every raw core/Gram entry, all 60 C0 columns,
all 5,760 primary choice supports and all 540 abstract counting equations.
The proof is about the represented factor and counting equations. It does not
assert that a primary-variable map extends to a literal permutation of the
prefix-counter auxiliaries: those are recomputed from transformed choices,
using the already audited exact prefix semantics. Every base solution selects
one of the 96 first-column choices, so one of the retained transports sends
it to a solution with ID 1 true. The reverse implication is inclusion.

The new CNF must contain the byte-identical original clause body, with its
header clause count increased by one, followed by the exact unit `1 0`.
Variable IDs and all base files remain unchanged. The new model is a small
recipe referencing the immutable original model rather than duplicating it.
Fresh independent normalization, byte and object gates are required before
any solver launch. This producer does not approve its own claim.

Scope: all abstract 36x60 Gram factors for this specified six-prism core,
after canonical C0 relabelling. A target graph containing this fixed core
would provide such a factor. This supplies no unrestricted core containment,
no residual D, and no target graph. Base column-overlap caps remain absent.

Predeclared limits: 120 seconds, 8 GiB process working set, deterministic exact
integer/finite-set calculations, zero solver calls. Success requires complete
group and equation checks, all 96 transports, exact one-unit file assembly,
and controls rejecting corrupted maps/transports/unit recipes. Any failure is
preserved and no incomplete enumeration is called a coverage result.
Oversized raw records and CNF receive lossless gzip companions below 10 MiB.

Locked execution from the repository root, with a fresh output directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_prism_first_choice_normalization.py --out acceleration/results/20260930_prism_first_choice_normalization
```
