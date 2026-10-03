# Independent six-facet completeness proof

Let Mx=r be the frozen independently reconstructed1445-row567-column rooted6
ordered-nonedge necessary system. Its previously independently checked rational
rank is564, so its nullspace has dimension3. Reparse the raw three integral
kernel vectors K0,K1,K2 and check MKq=0 exactly. Their entries at columns
(514,552,566) form the identity. Derive an affine origin o from the saved exact
primal p by o=p-p514K0-p552K1-p566K2; check Mo=r and all three free entries0.
Consequently every rational solution has the unique form
x=o+cK0+aK1+bK2, and c,a,b are the actual three flagged-count coordinates.
Because o and all Kq are integral, each integral(c,a,b) produces an integer
vector, and each integer vector has integral parameters. This uses the pinned
prior exact rank theorem, not a new rank computation.

Every coordinate is an affine form in(c,a,b). The literal forms include
c,a,b,2-c,20-a,18+c-2b (positive integer multiples are equivalent).
Therefore nonnegative vectors lie in
P={0<=c<=2,0<=a<=20,0<=b<=9+c/2}.
Conversely, check every one of567 affine forms at the eight points
(c,a,b) with c in{0,2}, a in{0,20}, and b in{0,9+c/2}. All are nonnegative.
For any point of P write X=c/2,Y=a/20,Z=b/(9+c/2).
Then0<=X,Y,Z<=1. At endpoint(i,j,k) assign weight
(X if i=1 else1-X)(Y if j=1 else1-Y)(Z if k=1 else1-Z).
These eight nonnegative weights sum1 and recover c,a,b exactly:
c=2X, a=20Y, b=Z((1-X)9+X10)=Z(9+c/2).
Thus P is exactly the convex hull of those eight points, and every affine
coordinate is nonnegative throughout P. The six witness forms prove the
reverse inclusion. This establishes the complete rational nonnegative domain
without trusting the discovery's enumeration of triples of tight planes.

Its integer parameters are precisely
c=0,1,2; a=0,...,20; b=0,...,floor(9+c/2).
The layer counts are21*10=210,21*10=210,21*11=231, total651.
The containing integer box has3*21*11=693 triples;42 are rejected. The checker
enumerates all693, independently constructs every accepted full567-coordinate
integer vector, checks every one of1445 exact equations, and preserves all
rejected negative-coordinate witnesses. The c=0 face matches the prior210
conditional-domain points exactly, but no zero-prism premise is used here.

The actual mask7100 is independently decoded: its vertices partition into
two disjoint triangles with a perfect matching between them; the ordered roots
are nonadjacent and free-label canonicalization fixes their order. Thus c is
the count of this rooted triangular-prism class, without assuming any target
automorphism. The other axes are raw rooted masks8024 and15540.

These651 objects are nonnegative solutions of necessary local identities.
The argument establishes no graph realization, local-profile exclusion beyond
this operator, unrestricted target nonexistence, or target-wide search coverage.
