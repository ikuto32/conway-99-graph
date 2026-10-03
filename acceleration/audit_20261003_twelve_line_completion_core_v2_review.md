# Independent exact review of the twelve-line cap core and completion veto

Reviewer /root; discovery /root/structural. Review prepared 2026-10-03 UTC.
Exact candidate revision V1 SHA256 9ba6929ec3ac6273e0ce56f06bab4e0da0f3e706f1a4be22054733209eeed702, source context d0c0dd7db0d3de420b1d718b59122b069df01107.
Outcome: VERIFIED within the literal finite geometry and one specified non-induced configuration exclusion; ordinary ledger registration and public evidence remain pending. No target resolution, formal proof, external review or novelty claim.

## Independent finite implementation and controls

Root's new checker imports no producer code. It parses only the twelve numeric triples in the immutable configuration table, constructs an unordered edge set and all sixteen neighbor sets, and directly intersects the latter for every one of the120 unordered pairs. It separately enumerates actual triangles and sums the signed twelve incidence columns. The result reproduces36 edges, degrees6 at the four centers and4 at the twelve other points, exactly12 actual triangles, adjacent CN1/nonadjacent CN<=2, integer signed point sums (-3,-3,-3,-3,0,...,0) and column sum -4=2 mod3. Thus the exact finite graph refutes a universal balance assertion based only on these local caps and linear actual triangle geometry; it is not itself degree14 or a target.

Before enumeration, the actual V2 run passed three positive boundary controls (K3, two-triangle friendship graph, unfinished K2 edge permitted by caps but rejected by complete-triangle geometry) and four corrupted controls (duplicate pair, wrong incidence word, K4 adjacent CN2, forbidden added core edge). These controls test this implementation only, not every malformed input or every target.

The V1 implementation incorrectly required a newly added edge to have its unique triangle completion already inside the16 vertices. Its complete source/spec/plan/result are preserved. It reported only the unmodified core as locally compatible, but Root rejected this interpretation before approval. V2 has a separate cap-only mode for proposed supergraphs, preserving exact CN1 for the original core. This correction admits all49 locally cap-compatible matching cases and forbids16335 other subsets. No evidence from V1 is used as a valid exclusion.

V2 actual invocation871a9c0edd6840cca209bd0f695d31ba completed0.625 outer/0.422 worker seconds, exit0, reaped empty Windows Job PID27464. Source12397f32552910c315ab56d08785fa95dc071d6188f8bc95b1792982083e916c; raw report2f2ba24c9ccf5e1adde843a3effa241d94fbafcaa47490dc26db450873df803e; terminale7038b9de3951625163626100d38c9cd7f56c95187ef2f5300b2b755478b797c. Locked root uv environment/Python3.12.10/tqdm4.67.1, standard set/integer arithmetic, existing deadline and supported Windows Job supervisor are disclosed trusted components.

## Why the finite universe covers arbitrary extra edges

Any original nonedge uv with an original common neighbor w cannot be added: uw already has its original third triangle vertex q, different from v, and the added uv gives uw a second common neighbor v. Thus only the14 original CN-zero nonedges can be added. The finite run considers all2^14=16384 subsets, not just single-edge changes or sampled cases.

Independent paper elimination agrees: opposite x edges add a third common neighbor to a saturated center/x nonedge; y_i z_(i-1) does the same to a saturated center/z pair. The remaining eight edges are the two K2,2 possibilities between opposite-center leaf pairs. A leaf cannot take both opposite leaves since their original local edge already has its triangle completion. Therefore the added edges must form independent matchings in those two K2,2s. Each has1 empty,4 one-edge and2 two-edge matchings; their Cartesian product has49 cases, with f multiplicities1,8,20,16,4. Every one of these49 cases passes the local CN caps in the corrected exact enumeration. Newly added edges may have CN0 inside and obtain completion outside; this is deliberately allowed.

## Independent derivation of the target contradiction

Assume an arbitrary target contains the literal twelve triangles on16 distinct vertices; use the actual induced graph H, including all f permitted added edges. Its four center degrees stay6, its four x degrees stay4, and exactly2f leaf degrees increase4 to5. The degree14 cut is V=152-2f. Internal pair CN sums equal the sum of binomial vertex degrees,132+8f. Target CN totals on the120 pairs are (36+f)+2(84-f)=204-f. Thus the outside pair contribution is P=72-9f. This counts the missing external completion of any added edge correctly.

All center pairs are already CN-saturated; their outside neighborhoods are disjoint. Each center needs8 outside neighbors, so there are T=32 distinct anchored outside vertices. Saturated center/x pairs and center/local-or-neighbor-leaf pairs permit no other S-neighbor. Only the two opposite-center leaves can be further neighbors, and an anchored outside vertex cannot take both because their mutual edge is completed inside H.

The deficits of these center/opposite-leaf pairs total R=8-2f: each extra matching edge eliminates one deficit for each of its two opposite centers. Consequently R anchored outside vertices have two S-neighbors and32-R have one. They contribute T+R=40-2f cut edges and R pair completions. The remaining99-16-32=51 outside vertices therefore have exactly112 cut edges and64-7f pair completions. For every nonnegative integer t, choose(t,2)>=2t-3 because the difference is (t-2)(t-3)/2>=0, including t0/1. Summing over the51 vertices requires at least224-153=71 pairs, while64-7f<=64. Contradiction for every f0..4 and therefore every possible non-induced embedding.

The finite checker independently recomputes V,P,T,R,N,E,Q for all49 cases and checks these exact quantities. It does not enumerate83-vertex completions; the written counting inequality excludes all such completions.

## Optional exact interlacing check

Root independently checked the four Fourier blocks from the displayed neighbor sets. At shift1, y-z antisymmetry gives -2, and the remaining block has polynomial t^3-4t^2-4t+4. Endpoint values are f(-2)=-12,f(-1)=3,f(0)=4,f(1)=-3,f(4)=-12,f(5)=9. Its three real roots consequently lie in the three claimed intervals. At shift-1 the sum/difference blocks give -1+-sqrt3 and +-sqrt2. At shifti the diagonal is zero, squared trace16, cubic trace0: the four triangular products have real parts -1,-1,1,1. Paired-edge matching products sum6 and real four-cycle products sum-4, hence determinant6-2(-4)=14 and polynomial t^4-8t^2+14. Shift-i conjugates this block. All square-root comparisons are exact: sqrt3<2 and sqrt(4+sqrt2)<3. Thus exactly one eigenvalue exceeds3 and every eigenvalue is greater than-3. This passes the stated target principal-submatrix interlacing caps. No floating eigenvalues or completion sufficiency are claimed.

## Scope and falsification boundaries

The verified finite counterexample defeats the cap-only balance inference. The verified completion veto excludes just the twelve literal triangles, allowing arbitrary additional edges. It does not force those triangles in an arbitrary target, classify all twelve-line circuits, prove any unrestricted existence/nonexistence claim, or constrain a hypothetical automorphism.

The general anchor filter V1 is independently correct under both listed saturation conditions: T disjoint anchor-neighbors have Sdegree1/2, R counts the degree2 vertices with multiplicity, remaining N have exact E cut and Q pairs; the integer tangent inequality follows. It also handles C empty,m0,N0 and deficits2. Its distinct broader V2 candidate will require separate exact revision review; removing leaf saturation changes equal pair counts to an upper bound and invalidates R<=T. V1 verification must not silently approve V2.

No ledger/index change is performed by this review. Artifact availability LOCAL_ONLY until publication. The independent audit is bound to the candidate and exact V2 computation hashes above; repeated execution or agent agreement alone was not used as mathematical verification.
