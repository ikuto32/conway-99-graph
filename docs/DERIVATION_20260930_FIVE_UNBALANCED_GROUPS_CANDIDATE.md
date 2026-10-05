# Candidate exclusion of exactly five unbalanced groups

Status: CANDIDATE, awaiting a separate independent derivation and falsification.
This statement concerns binary factors with the literal six-prism support and
prescribed full integer Gram. It does not assume column-overlap caps, balance,
or an automorphism of any target.

Use the separately checked marginal identity: for every coordinate a and fibre f,
the vector delta_g(a,f)=n_g(a,f)-L_ag lies in the kernel of the augmented support
matrix H whose columns are (1,L_.g). Here n counts that fibre among the three
columns of group g. The vector vanishes outside groups incident to a.
For every a,g, the sum over the three fibres of delta_g(a,f) is zero.
On an incident group, -1 <= delta_g(a,f) <= 2.

Suppose exactly five groups E are unbalanced. Their five support columns are
distinct binary vectors. An affine subspace of dimension d contains at most
2^d binary vectors: select d coordinate functionals giving an injective
projection on its direction space, and count possible binary images.
Consequently the five augmented columns have rank at least four over Q.

If the rank is five, every deviation vanishes. Otherwise the kernel is one
dimensional. Choose its primitive nonzero integer generator sigma.
Every integer deviation vector on E is t sigma with integer t, by Bezout
applied to the relatively prime coordinates of sigma.

If sigma has a zero coordinate, that group has zero deviation at every a,f,
contradicting exactly five unbalanced groups. Otherwise all five entries are
nonzero. The augmented leading row gives sum sigma_g=0. Five entries all
equal to +1 or -1 cannot sum to zero. Some |sigma_g| is therefore at least two.

Fix such a group g. If it is absent from coordinate a, t(a,f)=0 because its
deviation is zero and sigma_g is nonzero. If it is present and sigma_g>=2,
the lower bound t(a,f)*sigma_g>=-1 forces the integer t(a,f)>=0.
If sigma_g<=-2, the same bound forces t(a,f)<=0.
But sum_f t(a,f)=0, from the fibre-sum identity and any nonzero sigma entry.
Thus all three coefficients vanish in either case. This holds for every a.
Every group is balanced, a contradiction.

Proposed exact statement: no factor on this fixed support with prescribed
integer Gram has exactly five unbalanced triplicate-support groups.
The argument does not exclude exactly four or six or more, and does not
exclude the support or target. Independent review must verify the marginal
premise, affine-cube rank bound, primitive-lattice step and one-sided
integer argument. No finite census, solver result or external review is
claimed by this written candidate.

