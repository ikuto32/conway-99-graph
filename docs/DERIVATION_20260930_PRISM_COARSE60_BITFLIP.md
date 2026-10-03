# Candidate six-bit normalization for the fixed coarse60 model

Status: CANDIDATE pending independent review. The frozen base encoding is
C-SIX-PRISM-COARSE60-EXACT-BITLIFT-CNF r1. All statements below concern that
fixed 60-distinct-pattern six-prism family, not unrestricted target coverage.

Write a core row as `(g,a,b)`, with fibre `g` in {0,1,2}, component `a` in
{0,...,5}, and coordinate bit `b` in {0,1}. A coarse column fixes the fibre for
each component and selects exactly one bit in that fibre. For any vector
`e` in {0,1}^6, relabel rows by `(g,a,b) -> (g,a,b xor e[a])`. This preserves
matching edges and the three-fibre coordinate triangles, hence the core and
its prescribed Gram. It preserves every coarse column and all row margins.
Left multiplication of F by this row permutation preserves column overlaps,
so the required outside-column caps are invariant as well.

For a local component/fibre domain the action either keeps its 20-bit mask or
complements all twenty bits. Complementation preserves weight ten and changes
each required subtotal half-of-its-domain-size to itself. Thus it permutes the
complete 136-mask domain. Compatibility of two selected domains is transported
accordingly. This follows already from row relabelling; the accompanying exact
table checks also evaluate every one of the 2,496,960 selector pairs under all
four endpoint-flip choices. All 18 domain choices and all 360 bit channels are
therefore preserved.

The 64 actions form the elementary abelian group under bitwise XOR. On any
given six-bit first-column word x, the unique action e=x makes every first
column bit zero. This establishes coverage of every satisfying factor by the
normalized formula. The converse is inclusion, since the new formula merely
adds units. This is relabelling a possible object; no nontrivial automorphism
of that object is assumed.

The original formula's exact-one prefix auxiliary variables need not transform
by a permutation. After selecting the transported domain masks, set each
prefix variable to the OR of all selectors up to its recorded position.
Exactly one selected mask gives the unique satisfying prefix assignment.
The base encoding equivalence therefore lifts each transported raw factor
back to a complete assignment. The six appended unit literals are looked up
from column-zero bit metadata, rather than assumed from an ID convention.

There is no solver result in this package. SAT would produce a factor only;
the residual 60-vertex graph D remains absent. UNSAT would exclude only this
fixed coarse template, after a complete independently checked proof trace.
