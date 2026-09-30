# Independent identity-cross aggregate and Hadamard support review

Write T=[I I I], let M0,M1,M2 be the three 12-coordinate perfect-matching
matrices, and put S=M0+M1+M2. The identity-cross core C has diagonal blocks Mg
and off-diagonal blocks I. Its exact prescribed factor Gram is
G=12I-C-C²+2J-B, where B has three diagonal J12 blocks. Direct multiplication
gives TCTᵀ=S+6I and TC²Tᵀ=15I+4S: the three blocks of TC are Mg+2I and each
Mg²=I. Also TTᵀ=3I, TJTᵀ=9J and TBTᵀ=3J. Hence

    TGTᵀ = 15I + 15J - 5S.

For a binary factor F with FFᵀ=G and the target margins, the same-coordinate
cross-fibre Gram zeros force at most one of the three entries at any
coordinate in a column. Thus L=TF is binary, has row sums 30 and column sums
six, and LLᵀ=TGTᵀ. For X=2L-J, the row margins give
XXᵀ=4LLᵀ-120J+60J=20(3I-S). These are necessary aggregate conditions in the
identity-cross family, not sufficient conditions for F or a target graph.
No target automorphism or unrestricted identity-cross normalization is used.

The raw 20-by-20 Hadamard matrix is checked literally over the integers in
both row and column directions, with constant first column and balanced other
columns. No Hadamard-existence theorem is trusted. For each matching, assign
six distinct balanced orthogonal sign columns to its six edges and put opposite
signs at the two endpoints. The resulting 12-by-20 block Yg has
YgYgᵀ=20(I-Mg), row sums zero and column sums zero. Concatenating the three
blocks gives X; L=(X+J)/2 is binary with the required margins and aggregate
Gram. This proof works for every triple of perfect matchings on 12 coordinates.
It constructs only the aggregate, not a colouring into three fibres.

The checker reconstructs the exact saved choice of columns, edge ordering and
endpoint signs in all five cases: connected00–03 and the standard six-prism
control. Each of their 60 supports has six coordinates. A separate choose-two,
choose-two enumeration considers all 90 balanced fibre assignments per support
and retains exactly those avoiding every zero prescribed-Gram pair. It checks
all saved raw choices and masks, all 1,296 independent column contribution
capacities, all 1,770 column-pair outcomes, and three complete column-to-pair
bipartite projections per case. Perfect-match witnesses are checked literally;
Hall obstructions include the entire neighbor union. No producer matching or
colour-enumeration code is imported, and no complete-factor search is run.

Connected00 has an exact short obstruction. Its column 41 support is
{2,3,4,5,10,11}, containing three whole pairs of M0=M1. For either endpoint
placement in fibres zero and one, the two rows of such a pair have prescribed
Gram zero. Each pair therefore needs at least one endpoint in fibre two.
Three pairs need three such endpoints, but the fibre has only two slots.
The audit also records a zero-Gram witness for every one of the 90 balanced
colourings. Consequently no full factor can have this particular saved L.
This excludes neither connected00 itself nor other aggregate/Hadamard choices.

The other four saved supports pass these separate projections. Their projection
witnesses are not asserted jointly compatible. No full F, residual adjacency
D, target graph, exhaustive support classification or target-wide search
percentage follows.

Independent controls precede the finite research checks. They include a
literal Sylvester matrix, correct bipartite and Hall witnesses, and the already
independently checked non-target SRG(243,22,1,2) factor with identity cross
matchings. At general fibre size n the same calculation gives
TGTᵀ=(3n-21)I+15J-5S. The 243 control uses n=20, 180 outside columns, aggregate
row sum 54 and column sum six; its full factor and aggregate identities are
checked directly. Its existence supplies no evidence for SRG99. Corruptions
change signs, factors, support bits, matchings, Gram entries, colouring lists,
capacities, overlaps and projection witnesses.

The checking source imports only Python standard-library components. Shared
raw artifacts and earlier independent core/243 premise reports are disclosed.
The saved producer search is only a bounded archive keyword search; no novelty
or comprehensive literature claim is adopted. The four separate proposed
claim bindings distinguish necessity, universal aggregate construction, the
five finite projection outcomes and the one fixed-support exclusion.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard20_support_v2.py --out build/hadamard20-support-review-new
```

Version 1 stopped before research checking because the independently saved
SRG243 gate hash was transcribed with an extra letter f. Version 2 corrects
that exact hash only; the original failed source, report and written audit
are preserved and bound. Producer artifacts and mathematical scope are unchanged.
