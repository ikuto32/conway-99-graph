# Complete six-prism column model with target-necessary column caps

Producer status CANDIDATE. No solver is launched. The universal question whether
all complete abstract six-prism Gram factors already satisfy the column caps
remains UNKNOWN. A two-column partial witness and exact moment analysis below
only refute weaker local/moment implication arguments, not that universal claim.

## Cheap implication analysis

Every allowed column has six incidences, one in each prism component and two
in each fibre. In the fixed six-prism core, every row has within-component
degree3 and there are no edges between components. Thus for any allowed column
v and prescribed Gram G=12I-C-C²+2J-diag(J12,J12,J12), vᵀGv=114:
72 from12I,0 from-C,-18 from-C²,+72 from2J,-12 from blockJ.
If a full factor F exists and T=FᵀF, then Tyy=6, sum_z Tyz=60,
and sum_z Tyz²=114. Off diagonal sums are54 and78 respectively.
Both distributions (0:17,1:30,2:12) and (0:16,1:33,2:9,3:1) have59
entries and exactly these two sums. The moment equations alone therefore do
not force the cap. Neither distribution is asserted to be a realizable factor.

The saved first choice ID1 at canonical C0 edge(0,2) has rows
{0,2,16,18,32,34}. The allowed column at edge(0,4) with rows
{0,4,14,18,32,35} shares {0,18,32}, so its overlap is3. Fix all canonical C0
entries and these two complete columns; leave other C1/C2 entries unknown.
Every literal known Gram contribution is at most the prescribed entry, each
chosen column satisfies its full local domain, and the normalization unit holds.
This is a partial-domain obstruction only. It is not a full Gram factor or a
counterexample to automaticity in complete factors. All data are saved exactly.

## Exact encoding extension

Start from the independently audited first-choice normalized all96-choice
model,245880variables/874801clauses. Preserve the complete original body.
For r12..35,d0..59 add bit x[r,d], ID245881+(r-12)*60+d (1440bits).
For every choice, add four clauses choice⇒x for its selected unknown rows:
23040 binary clauses. For each x add x⇒OR(all choices in that column selecting
that row),1440 clauses;1200 have24 supporting choices and240 have none, giving
unit false bits. Together with the base exact-one choice rows these channels
are bidirectionally exact. They preserve all96 choices in every column.

Within each unknown fibre, every column has two rows, and the exact within-Gram
has off-diagonal entries0 or1. Two distinct columns cannot contain the same
two-row pair, since that pair would then have Gram entry≥2. Hence overlap in
each fibre is≤1. C0 also has unique two-subsets, so total column overlap≤3;
an overlap3 occurs exactly when C0 shares a row and C1 and C2 each share a row.
For every C0-sharing column pair d<e and local rows i,j in0..11, append

    ¬x[12+i,d] ∨ ¬x[12+i,e] ∨ ¬x[24+j,d] ∨ ¬x[24+j,e].

There are540 sharing pairs×144 row choices=77760 templates. Any template with
an empty-support incidence bit is true by its channel unit; these56640 templates
are omitted with exact support-empty witnesses recorded. The21120 remaining
four-literal clauses are retained, including clauses that might admit further
simplification; no additional argument or restriction is introduced.
The final exact counts are247320variables/920401clauses,45600 appended clauses.
This is equivalent to the normalized abstract factor model plus all1770
column-overlap caps. It is target-necessary in the fixed six-prism core family,
not an entailed strengthening of every abstract Gram factor. First-choice
relabeling preserves overlaps by row/column permutation, so its prior coverage
continues to apply when caps are added. No target automorphism is assumed.
Mixed caps, residual D and a full99 graph are still not asserted.

## Calibration and independent checking path

Before build: save the exact local witness, moment identities, input hashes,
scope and predicted counts. Deterministically verify every5760 choice and all
1440 bits under one selected choice per column, check all16 quartic truth
assignments and all eight possible per-fibre overlap triples, and reject altered
channel truth and partial-witness controls. Independently review raw catalogs,
literal core/Gram values, all channel supports and omitted templates; derive all
appended bytes independently and compare the unchanged base prefix. A later
SAT-object checker must check all247320 assignment bits and920401clauses,
decode raw F from choices and channels separately, validate the complete Gram
and margins, and directly check all1770 column overlaps. No fullF positive
fixture is invented and no solver may run before separate gates.

Resource limit120seconds, deterministic arithmetic, no random seed. Package
large raw artifacts in lossless gzip with exact raw/packed SHA256 and byte counts.
Use existing locked environment without dependency changes:

```
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_prism_column_caps.py --out acceleration/results/20260930_prism_column_caps
```
