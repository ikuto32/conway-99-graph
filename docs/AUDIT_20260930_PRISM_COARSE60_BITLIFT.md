# Independent semantics of the coarse60 bit-lift encoding

This document describes the checking argument. Approval requires the separate
complete raw-clause audit and its exact artifact bindings; this text alone is
not an encoding gate. The scope is the already audited60distinct coarse words
of one fixed six-prism core, each appearing once. No target automorphism,
bit-complement pairing or exhaustive coarse-template coverage is assumed.

There are18local domains indexed by component a and cell g. Each chooses one
of its136independently enumerated20-bit words. A prefix-OR chain is equivalent
to the OR of selectors seen so far when each gate is bidirectional. Combining
that recurrence with an exclusion of an already selected prefix and the next
selector gives at most one selected word. Requiring the final prefix makes
this exactly one. The first gate/constant folding and every actual clause are
reconstructed by the audit. The recurrence supplies an extension of auxiliary
values for every exactly-one selector assignment; auxiliaries add no domain
restriction.

For each of the60coarse columns and each of its six components there is one
coordinate bit,360bits total. Exactly one local domain controls each such bit.
Its selected word implies all20of that domain's bit values. Exactly-one
selection therefore determines all360bits consistently. Conversely any bit
lift satisfying the local marginal equations selects its unique matching
listed word in each domain; the lists are complete by the prior independent
domain audit. There is no missing reverse implication needed for this channel
under the exactly-one premises.

Consider different components a,b and cells g,h. Their common coarse positions
number4q, where q=1 if g=h and q=2 otherwise. Both selected local words have
2qones on that position set. Let the number of jointly selected ones be k.
The four bit-pair counts are then k,2q-k,2q-k,k. Consequently imposing k=q
is equivalent to all four prescribed Gram entries being q. A clause for
each left selector that requires at least one compatible right selector,
under exactly-one on the right, imposes precisely this condition. All135
component/cell pairs are covered; same-component different-row entries are
zero automatically because every column contains one row from each component.
Row diagonals are10 by the local weight constraint. Thus these conditions
are equivalent to the complete integer36-row prescribed Gram, with column
margin2in every cell supplied by the coarse words.

For two distinct columns d,e, let S be the components whose coarse cell labels
agree. Their row supports overlap once for exactly those a in S whose two
coordinate bits are equal. The condition that overlap is at most2is equivalent
to forbidding three simultaneous equalities. For each triple of components in
S, the eight possible common bit settings give eight assignments of six
literal bit values. The six-literal negation of each assignment forbids it.
Together they are equivalent to that triple not being entirely equal; covering
all triples is equivalent to the original column cap. There is no target
symmetry argument in this reduction.

The frozen60patterns give1,770column pairs with |S| distribution
0:240,1:360,2:630,3:360,4:180. Hence this direct encoding has
(360+4*180)*8=8,640six-literal column-cap clauses. Pairs with |S|<=2satisfy
their cap without any clause. The audit must independently reconstruct the
triples, bit settings, exact variable mapping, and every raw clause.

A satisfying assignment therefore represents precisely a binary36-by60factor
of the specified core with this coarse support and outside-column overlap at
most2. Such a factor is still only a necessary part of a99-vertex target:
residual D and mixed/quadratic completion conditions are not supplied here.
UNSAT, with a checked complete proof, could exclude this particular coarse
template; it would not exclude all factors of the core or Conway99.
