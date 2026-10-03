# Independent first-choice normalization for the fixed six-prism factor

The domain is precisely the previously audited complete six-prism factor
model, with60 canonical C0 columns and96 possibilities in each column. Its
first column has C0 support{0,2}; choice1 has support{0,2,16,18,32,34}.
The theorem is satisfiability equivalence between that base formula and the
same formula with primary literal1 required true. It concerns one fixed
core and does not assert that any target contains it.

Write an inner row as(g,a,b), where g is its cell, a its prism and b its bit.
A permutation of prisms2,3,4,5 and independent flips of their four bits,
applied identically in all three cells, fixes prisms0,1 pointwise. This gives
4!*2^4=384 distinct relabellings. It preserves every inner edge: within a
cell the paired bits remain paired, and cross-cell edges compare the same
prism and bit. Cells and hence root incidences remain fixed. Thus the full
raw39 core and prescribed Gram are invariant.

For each canonical C0 pair d={i,j}, relabel its outside-column index to the
canonical index of{rho(i),rho(j)}. This permutation pi restores canonical
C0. For every original factor define the transported one by
`F'[rho(r),pi(d)] = F[r,d]`. This is a bijection on binary factor arrays and
preserves the Gram, margins and all abstract counting equations. It is an
action on the space of labelled possible factors; it is not an assumption
that a factor or target is invariant under any nonidentity permutation.

The first column is fixed setwise. Its two selected cell1 prisms among2..5
can be sent to2,3 and the other two to4,5. Flip each selected bit to zero.
The transported first-column support is exactly choice1. This proves
transitivity on all96 choices. Within the explicit384 maps, four stabilize
choice1: independently permute the two cell1 and the two cell2 selected
prisms, with the selected bits unchanged. The finite audit checks the actual
orbit, stabilizer, all inverse IDs and all147456 ordered compositions.
No census of the full automorphism group is asserted.

Every base satisfying assignment selects exactly one of these96 first-column
choices. Applying its certified transport gives primary values satisfying
the same540 abstract equations and makes choice1 true. The audited prefix
counter semantics provide the unique auxiliary values for the transformed
primary assignment. The prefix auxiliaries are recomputed, not claimed to
undergo the same literal-variable permutation. Conversely any assignment
with the extra unit is a base assignment. Therefore satisfiability is
preserved in both directions.

The independent checker imports only its own previously audited raw-core,
complete-domain and equation constructor, not the normalization producer. It
reconstructs each supplied signed map from its explicit component data,
checks raw39/Gram invariance, every60-column image and5760 primary image,
and all540 equation images for each map. It checks all96 saved transports
against those independently reconstructed actions. The raw augmented CNF
must be exactly the old874800-clause body preceded by the new header and
followed by `1 0`. All245880 variables are unchanged.

Positive controls include identity, inverse actions, all valid transports
and exact file composition. Corrupted actions, incomplete coverage, wrong
transport direction, changed hashes, incorrect units and altered raw bytes
are rejected. No positive research factor is assumed or supplied by these
finite controls. No solver is invoked by this audit. The omitted column caps
and residual D remain omitted. Any later SAT object or UNSAT proof still
requires separate independent checking in this exact normalized scope.
