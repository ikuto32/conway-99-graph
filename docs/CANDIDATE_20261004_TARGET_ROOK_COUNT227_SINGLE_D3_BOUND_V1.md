# Candidate: one deficiency-three triangle at R227 permits at most two d2 triangles

This separate written follow-up preserves the sixteen-row R227 population
candidate unchanged. It is not independently approved and lies outside the
current publication cutoff. No mathematical program, enumeration, import,
backend or worker ran. Root received the argument before freeze; shared
agreement is not verification.

## Exact statement

For every complete finite simple SRG(99,14,1,2) with exactly227 actual
induced rook-nine vertex subsets counted once, define d_T=6-r_T for each
actual triangle, where r_T counts those subsets containing T. Suppose
exactly one actual triangle has deficiency three. Then every deficiency
is zero, one, two or three, the number b of deficiency-two triangles is
zero, one or two, and the number a of deficiency-one triangles is21-2b.

This does not exclude R227 or construct any listed population. It does
not assume deficiency-one-only parity, equitability, automorphisms, a
codeword beyond the derived odd-deficiency family, or an induced positive
support. The induced support used at the contradiction boundary is proved.

## Inputs and local geometry reconstructed

The only inherited result is
C-UNRESTRICTED-TARGET-ROOK-DEFICIENCY-STRICT-SECOND-NEIGHBOR-BOUND r1.
It gives d_T<=3 when total deficiency D=6(231-227)=24. The weaker R227
population table is comparison evidence, not a required verified premise.

Every vertex is in seven actual triangles, each edge has its unique
triangle partner, distinct triangles meet at most once, and three triangles
cannot meet pairwise at three different points. At each point v the simple
defect graph D_v joins its incident triangles exactly when no induced rook
contains both. The degree of its triangle T is d_T. Double counting gives
D24. With c=1, a+2b=21 and the positive triangle count is P=22-b.
The local handshake says r_1+r_3 is even; this is the odd-family parity.

For any point fan of positive triangles the actual outer-point incidence
argument gives

    P>=3r_1+5r_2+7r_3.                            (1)

Indeed a fan triangle of deficiency d has d external defect partners at
each of its two outer points. An external triangle can meet only one outer
point of the whole fan: two in one triangle violate linearity and two in
different fan triangles create the forbidden distinct-intersection triple.

Let T be the sole deficiency-three triangle. Assume b>=3. Then P<=19.
At each point of T, r_3=1 and r_1 is odd. If r_1=1 a degree-three node
needs r_2>=2, whose fan weight is20. If r_1>=5 its fan weight is at least22.
If r_1=3 and r_2>=1 its weight is at least21. Thus precisely three
deficiency-one triangles and no deficiency-two triangle occur at each
point of T. Each local defect graph is the (3,1,1,1) star.

These nine distinct deficiency-one partners C form three central buckets.
Their eighteen outer points are distinct. A same-bucket identification
violates linearity; an identification between different buckets creates
three triangles meeting pairwise at distinct points, with T the third.

## Odd parity already removes b>=4

No outer point of C lies on T or on another member of C. At each such point
C has odd deficiency one, and the sole deficiency-three triangle T is absent.
Odd-family parity therefore requires at least one further deficiency-one
triangle at that point. Deficiency-two triangles cannot correct this parity.

There are s=a-9=12-2b deficiency-one triangles outside C. They have only3s
point incidences in total, so covering the eighteen distinct outer C points
requires3s>=18. Consequently b<=3. This counts actual incidences even if
several triangles meet at a point; it does not impose multiplicity two.

## The b=3 equality support and its full Gram implication

Suppose b=3. Then a=15 and s=6. Equality3s=18 means all six external
deficiency-one triangles V lie on the eighteen outer C points, every such
point lies on exactly one V, and no V point occurs elsewhere. An external
triangle meets at most one C outer point per central bucket, by the same
distinct-intersection prohibition. Each V therefore has one point in each
of the three buckets. The support S consists of the three points of T and
these eighteen outer points. All sixteen odd-deficiency triangles are
exactly T, the nine C and the six V, wholly inside S.

Give the three points of T weight three, the eighteen outer points weight
one, and all other points weight zero. This vector w has

    sum w=27,  ||w||^2=45.

The known triangle edges have total endpoint-product weight108:
T contributes3*9=27; each of the nine C contributes3+3+1=7; each
of the six V contributes1+1+1=3. All these edges are distinct by unique
triangle partners. Thus their total is27+63+18=108.

The exact target spectrum makes Q=3I-A+J/9 positive semidefinite.
On the specified triangle-edge union the quadratic value is

    w^T Q w = 3*45-2*108+27^2/9 = 0.

Any additional target edge inside S would decrease this value by twice
the strictly positive product of its endpoint weights, contradicting
positivity. Hence that known edge union is exactly the induced graph on S.
This is a consequence of target PSD, not an inducedness assumption.

Every internal edge of S is in one of T,C,V, with its unique triangle
completion in S. A different actual triangle meets S in at most one point:
if it had two, their edge would be an internal edge and uniqueness would
make it one of the known odd triangles. In particular each of the three
remaining deficiency-two triangles has at least two points outside S.

At an outside point of one of them, the only possible positive triangles
are those same three deficiency-two triangles, because every odd triangle
is wholly in S and no other positive deficiency occurs. A degree-two node
in the simple local defect graph requires the other two distinct positive
nodes to be incident at that point. Thus all three deficiency-two triangles
must pass through each such outside point. Taking the at least two outside
points of one triangle makes the other two meet it twice, contradicting
linearity. This rejects b=3 and proves b<=2.

## Falsification boundaries, failed shortcuts and overlap

The common-point star (3,1,1,1) has three deficiency-one triangles, an odd
number, yet its four odd-deficiency nodes satisfy parity. Applying
deficiency-one-only parity there would refute a valid local graph and is
not part of this proof.

At b=2 the locally permissible sequence (3,2,2,1) has fan weight20,
equal to P20. It is the graph obtained by joining the degree-three node
to all others and joining the degree-two pair. The star conclusion is
used only under b>=3; this exception and b0/b1 remain open.

Odd parity alone gives b<=3. It does not reject the equality, whose eighteen
outer incidences and six external triples fit exactly. Rejecting that case
needs the weighted target Gram and the actual outside local degree-two rule.

The weighted support is the m=3 matching-support geometry appearing in the
preserved strict second-neighbor paper. The difference here is that its
six external degree-one triangles are forced by odd parity while three
additional degree-two triangles still exist. The contradiction prevents
those extra positive triangles from supplying their outside local degrees.
No previous equality proof or mathematical approval is transferred.

The support's three matchings need not coincide. No rook-count conclusion
is deduced merely from the matching choices or from an ordinary collapsed
defect four-cycle. Arbitrary other target edges are retained until PSD
proves this particular support induced.

The general upper Gram alone does not exclude a twenty-one-point local
triangle union outside a target extension. The completed target spectrum
and the global positive-deficiency roster are essential. This is a new
conditional restriction, not a global target contradiction or scientific
coverage result. A different author must challenge the parity cover,
all108 weighted edges, induced-support step and outside two-point argument.
