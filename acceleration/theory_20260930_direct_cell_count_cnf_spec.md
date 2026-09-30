# Frozen build: labelled direct cells, standalone and count≥7, all column caps

Build only the two formulas selected by the parent after the exact preflight:
standalone23,112variables320,484clauses7,208,403ASCII bytes; count≥7
169,151variables968,960clauses18,279,995ASCII bytes. Reject every count,
recipe or byte-size deviation. No baseline-count formula is built. No native
solver, GPU, LP/MIP, ledger or publication mutation.

Allocation120 cooperative seconds and512MiB checked peak working set, including
controls, both formula streams and transport. Preserve all failures and raw
artifacts; no automatic retry or overwrite. A later version must bind a failure.
Read and authenticate the frozen direct-cell preflight source/spec/summary and
both exact recipes, all its input pins and the independently checked count
master. The only shared production module is
theory_20260930_direct_cell_count_preflight.py, SHA
902bafedf5099fc27727caf17819e50080e514ed9e0b6788fdd5345fb3d5ffdd.
Its exact/AND/equality/count-channel/threshold generators and inventory ordering
are reused transparently. It imports only standard-library modules. This build
uses a streaming subclass of its clause counter; no independent review is
claimed for reusing that code.

Write the exact predeclared header to an exclusive new .partial file. For≥7,
copy the authenticated existing base body verbatim after removing its checked
header. Generate every appended clause through the frozen recipe's ordering,
with only one clause in memory. Compare the complete regenerated recipe to the
frozen JSON and the file byte count to the inventory. Only then atomically
rename .partial to instance.cnf. Every final model records all1080 labelled
cell IDs, all8100 product gates,540 Gram rows, count links or36 explicit row
counters, all1770 cap rows and exact clause-section bounds. No ordering or
symmetry normalization is added.

Standalone raw-F equivalence: exactly the binary36x60 matrices with literalL,
two entries per fibre/column, every row sum10, prescribed integer FF^T, and
every pair of outside columns overlapping at most2. The remaining90 zero
Gram entries follow from literal support and one-fibre-per-coordinate. The
standalone exact thresholds, ANDs and equality flags admit the prescribed
truth values for every such F. Count≥7 has the same raw properties and at least
seven unbalanced triplicate-support groups. Count-master completeness makes
its signature/channel/marginal variables a compatible extension of any such
F; local words can be sorted solely to establish catalogue membership, without
sorting or restricting the actual labelled model. The ≥7 restriction is a
separate target-family necessity, not silently entailed by the standalone CNF.
No claim of≥8 is incorporated.

Gadget assumptions: AND clauses are unconditional equivalences; subset
cardinality constraints use distinct inputs; incidence count maxterms apply
when their existing master count selector is selected, and master channels are
exactly-one; the six-clause same-coordinate column equality gadget is
equivalent only under its two already imposed one-hot fibre triples. All caps
use the actual support intersections. No residualD or99-vertex adjacency is
encoded. No automorphism of a hypothetical target is assumed.

The producer decoder ABI is decode(assignment,model_path,scope_path,cnf_path=None).
It requires every variable exactly once as signed integers and verifies every
actual CNF clause. It reconstructs literal36x60 F, checks all1296 integer Gram
entries, all1770 column overlaps, all2160 closed-neighbourhood mixed values,
literalL, row and fibre margins, and the≥7 bound when relevant. Outputs include
the actual raw F and exact tables, exception counts and explicit nullD; they
remain candidates pending separate raw-object verification. There is no
research satisfying assignment in this build.

Controls: all frozen gadget/control cases; independently validated SRG243 raw
factor with its own60-row Gram/180columns, explicitly not research99; changed
binary entry, Gram target and matrix shape must reject. Tiny actual DIMACS
positive and corrupt assignment/header/clause controls check the parser.
Neither count-only fixture is mislabelled a full research factor.

Preserve every raw original. Any research output over10MiB receives deterministic
gzip transport in8MiB raw chunks (level9,mtime0,empty filename), each part strictly
below10MiB. Verify every recovered chunk and whole stream against raw bytes;
save exact package identities. Standalone instance is below10MiB. Transport is
not a proof or an encoding approval. All availability stays LOCAL_ONLY until
publication is separately confirmed.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_direct_cell_count_cnf.py --out acceleration/results/20260930_direct_cell_count_cnf
```
