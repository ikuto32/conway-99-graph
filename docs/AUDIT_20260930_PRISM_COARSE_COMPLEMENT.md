# Independent audit of the60-distinct coarse-pattern scout

The claim concerns a selected coarse template for the fixed six-prism core.
It supplies complete single-row bit domains, not jointly compatible bits.

Choose the two component positions of cell0 and then the two positions of cell1.
This gives C(6,2)C(4,2)=90 balanced six-entry words, each cell appearing twice.
Their same-cell component pairs define one of the15 perfect matchings ofK6,
with six assignments of its edges to the three cells. The five old round-robin
matchings are independently identified overF5 plus infinity: infinity pairs
with t, and the other endpoints sum to2t modulo5. Removing those five matchings'
30words leaves ten matchings'60words, each used once. The audit compares this
set with the immutable prior raw30pattern convention without importing its code
or its exclusion theorem.

For fixed different components a,b and a cell g, the complete90word population
contains6words with both in g; the old30 contribute2. For ordered distinct cells
g,h, the counts are12 and4. The remaining60therefore have counts4and8. Each
component occurs20times in each cell. These are also reconstructed directly
from the raw39-vertex adjacency and the target identity, summing the prescribed
36-row Gram over both endpoint bits. All135coarse pair conditions and18margins
are checked literally.

For component a in cell g, there are20local bit positions. Row margin10 fixes
the bit1 weight. Summing Gram requirements with the two bits of another
component b in cell h requires bit1 count2 on the four same-cell positions,
or4 on the eight different-cell positions. There are15such conditions. They
are necessary projections of any actual lift; they omit joint bit counts.

The producer enumerated weight10 combinations. The independent checker uses
every one of the1,024left10-bit masks and1,024right10-bit masks. A mask receives
an integer signature of its weight and its15subset sums. Matching complementary
signatures reconstructs every admissible20-bit mask uniquely. This is an exact
coverage bijection, not a sample. Prefix-signature joins also count the number
passing the first j equations. Consecutive differences independently reproduce
the producer's entire first-failure histogram. All18domains have136survivors;
their exact lists, metadata, ordering and counts are compared.

Because every required subset count is half its population, complementing all
20bits preserves a local domain; all68complement pairs per domain are checked.
This arithmetic involution imposes no global pairing between columns, no
automorphism of a target, and no extension of the old30×2 exclusion.

Controls compare the independent half-join with explicit Boolean enumeration
for every single-subset/weight/quota system up to five coordinates, plus a
two-constraint positive and impossible domains. Changed geometry, quotas,
multiplicities, labels, survivor lists, masks, constraints, denominators and
failure histograms are rejected. No producer module is imported.

The complete population18×184,756 consists of local row words, not full factors.
The2,448local survivors and1,224local complement pairs are overlapping views of
those domains and must not be summed as distinct factors. There is no justified
target-wide denominator. No solver is run and no global feasibility or exclusion
is claimed. Future joint-domain/CSP or CNF work needs a new independent audit.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/audit_20260930_prism_coarse_complement.py --out acceleration/results/20260930_independent_review/prism_coarse_complement
```
