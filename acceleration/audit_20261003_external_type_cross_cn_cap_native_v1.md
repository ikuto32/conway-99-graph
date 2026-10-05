# Independent written cross-common-neighbor cap derivation

Author and verifier: /root/native_driver. Method: independent_derivation from the target common-neighbor equations and literal geometry. ROOT proposed this filter and the mask44 example; Checkpoint is preparing its separate producer. Those shared origins are disclosed. No enumerator, producer, checker, LP, native executable or mathematical program was imported or run for this written audit. This is a necessary-type lemma, not an actual finite filtering gate or target exclusion.

Let G be a finite simple graph in which adjacent vertices have exactly one common neighbor and nonadjacent distinct vertices have exactly two. Let S be a vertex subset, H=G[S] its induced graph, x outside S, and T=N_G(x) intersect S. For each u in S define h(u,T)=|N_H(u) intersect T|.

Every v counted in h(u,T) is in S, is adjacent to u in H and hence G, and is adjacent to x by membership in T. It is therefore a distinct common neighbor of u and x in G. The map from those counted vertices to common neighbors is the identity and is injective. Since x is outside S, u and x are distinct. They are adjacent precisely when u belongs to T. Consequently

```
h(u,T) <= 1  for u in T,
h(u,T) <= 2  for u outside T.
```

There is no equality assertion: additional common neighbors can lie outside S. No degree, regularity, connectedness, construction triples or symmetry assumption is needed for this implication. For Conway99 the hypothesis is supplied by lambda1/mu2. The cap is necessary for every exterior vertex's type separately; retaining a type does not prove that it can occur or be combined with any other types.

The first inequality restates maximum degree at most1 in H[T], already present in the original matching filter. The new restriction is the second inequality at support vertices outside T. It can therefore remove old matching-eligible types without refuting the original weaker necessary relaxation. It imposes no new equality row or changed total/vertex/pair moment right-hand side. Any complete target still induces a nonnegative integer solution of the same154 equations over only types passing the new cap. Feasibility of that further necessary system remains insufficient for graph completion.

For the exact fixed17 base, independently decode the twelve literal triples:

```
(0,1,2), (0,3,4), (0,5,6), (1,7,9), (1,8,10), (15,11,14),
(16,12,13), (2,15,16), (3,7,11), (4,8,12), (5,9,13), (6,10,14).
```

Their source is docs/CANDIDATE_20261003_SEVENTEEN_POINT_EXTERNAL_NEIGHBOR_MOMENTS_V1.md, SHA70ef6392e86c6b9a3c9c6eac9b5d72abb9ea25741d3649282f66ac200bb93349. The original independently checked fixed model is modeld5f1/types4799 and full reportaf6b. This written calculation uses the literal triples rather than producer type eligibility.

Mask44 is 2^2+2^3+2^5, so T={2,3,5}. The complete neighbor sets relevant to its old eligibility are

```
N_H(2)={0,1,15,16}, N_H(3)={0,4,7,11}, N_H(5)={0,6,9,13}.
```

Each pair in T is nonadjacent and its two neighbor sets intersect exactly in {0}. Thus each pair has H common-neighbor count1 and delta=2-0-1=1>0. H[T] has no edges, |T|=3<=14 and |T|-edges=3<=7. This proves the old pair/matching/size eligibility by hand. But N_H(0)={1,2,3,4,5,6}; u0 is outside T and h(0,T)=3>2. A hypothetical exterior vertex adjacent to all three would give the nonedge0x at least three common neighbors, contradicting mu2. Mask44 must be rejected by the new necessary filter. This example alone does not count how many of the534 old masks will be removed.

Known-valid controls use the3-by3 rook graph, with vertex i=(floor(i/3),i mod3) and edges joining distinct points in the same row or column. An adjacent pair has exactly the third point of its common row/column as its single common neighbor. A nonadjacent pair (r,c),(s,d) has exactly (r,d),(s,c) as its two common neighbors. Thus these fixtures independently satisfy the same lambda1/mu2 hypotheses despite their different order/degree.

Take S={0,1,3,4}. Its induced graph is the4-cycle with edges01,03,14,34. The five actual exterior vertices yield these complete h vectors in support order(0,1,3,4):

| exterior x | actual T | h vector | cap result |
|---|---|---|---|
|2|{0,1}|(1,1,1,1)|passes|
|5|{3,4}|(1,1,1,1)|passes|
|6|{0,3}|(1,1,1,1)|passes|
|7|{1,4}|(1,1,1,1)|passes|
|8|empty|(0,0,0,0)|passes|

These test the empty type and show that the outside bound is an inequality: outside support vertices can have h=0 or1. To test equality at the outside bound, take S={0,1,2,3,4,5,6,7} and actual exterior x8. Its type T={2,5,6,7} induces exactly edges25 and67. Its complete h vector in support order0..7 is (2,2,1,2,2,1,1,1). Every inside-T count is1 and every outside-T count is2. An erroneous uniform cap1 would reject this known-valid type.

Deliberate bad fixtures are separate from known-valid exterior types. In the4-cycle support above, T={0,1,3} gives h(0,T)=2 and must fail the inside cap1; the original matching filter already rejects it. The fixed17 mask44 gives h(0,T)=3 outside T and must fail the new cap2, despite passing the old filters. A Boolean or float h/mask entry is not a mathematical type and should fail typed runtime controls in any future producer/checker. This written audit executes none of those runtime controls and approves no future code or count.

The exact necessary statement survives independent reconstruction. No all534-mask enumeration, feasible/infeasible strengthened model, rational primal, target existence/nonexistence, external review or formal proof has been obtained here. Future artifact checking must derive every h vector from actual H and mask bits, preserve all534 original labels and first veto evidence, bind the unchanged154-row coefficients, and independently check any new rational certificate.
