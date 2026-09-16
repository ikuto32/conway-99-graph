# Integral compression covariance and the next fibre-incidence condition

This bounded lane studies E0=0 without enumerating lower E0 layers. It does
not prove a positive E0 bound and does not construct a Conway graph.
The parent lane supplies an exact symmetric integral compression C with
tr(C^2)=2772. Its independent matrix audit verifies all support equations
and the spectral interval. The question here is whether four actual binary
neighbour rows can realize its fibre totals.

## A necessary condition lost by averaged degree moments

Fix a four-point fibre F and order its signed corners 00,01,10,11. Let X_F
be the 4-by-80 binary matrix of its neighbours outside F. At E0=0 there are
no edges inside F. All four vertices have twelve outer neighbours. A side
pair of corners already has one common first-layer neighbour and therefore
has one outer common neighbour; a diagonal pair has no common first-layer
neighbour and therefore has two outer common neighbours. Consequently

```text
X_F X_F^T = [12  1  1  2]
            [ 1 12  2  1]
            [ 1  2 12  1]
            [ 2  1  1 12].                         (1)
```

This retains the six particular pair intersections that the averaged
degree-row population does not assign. The ordinary Hadamard characters
diagonalize (1), with eigenvalues 16,10,10,12. Thus the four integer signed
column-load vectors obtained from X_F are pairwise orthogonal, with squared
norms 64,40,40,48. Each of their 80 coordinate tuples must be the Hadamard
transform of a binary four-tuple; separate PSD tests omit this alphabet.

The constant-character consequence is

```text
sum_y load_F(y) = 48,  sum_y load_F(y)^2 = 64.        (2)
```

The second expression is an incoming column-load moment. It is not the sum
of the four outgoing fibre-degree row square norms. Our controls separately
require each outgoing row to have square norm16; that extra choice is a
property of the controls, not a claimed universal graph identity.

The necessary model also imposes all fourteen exact root-label quotas per
source corner, the twenty prescribed block totals C[F,G], and every
known-edge/nonedge common-neighbour upper cap in the exposed partial graph.
It uses only one fibre at a time. It does not require the 21 choices to
agree on their shared edge variables.

## Why the old 30-template control cannot supply four rows

The old averaged degree control uses thirty rows for each source. On the
five external support groups, each such row is a hub star with weights1
plus a doubled matching on the other four groups. Modulo two it is exactly
the hub star. A sum of any four of these rows therefore has its odd
disjoint-fibre entries equal to a cut of K5: retain the groups occurring an
odd number of times as hubs. K5 cuts have 0,4, or6 edges.

Equality tr(C^2)=2772 at E0=0, on the other hand, requires every source row
to have eight disjoint entries3 and two disjoint entries4. Its odd-entry
support has size8. It cannot be a K5 cut. Therefore no quartet of the old
thirty templates realizes any sharp compression row.

The pair-sum probe independently finds zero such quartets in each of the
21 rows of the new compression. This is an obstruction to combining those
two particular controls. It is not an exclusion of C or E0=0, because the
thirty templates are an incomplete row family.

## Broader binary-incidence controls

The binary model admits all labelled neighbour subsets, while separately
retaining the convenient outgoing q=16 condition. For F={0,1}, it found a
witness in5.7 seconds. The independent standard-library audit checks its
four twelve-element neighbour sets directly, without importing the
producer or using a solver. The partial graph has237 exposed edges,
all4,851 pair caps pass, and all56 label quotas and six exact source-pair
intersections pass. This proves the old quartet failure comes from its
narrow template orbit.

The sequential all-fibre runner used one solver worker, a15-second cap per
fibre, and saved each result separately. Every one of the21 fibres now has
an independently checked positive witness. Across them the audit checks
101,871 partial pair caps,1,176 exact label quotas,126 exact source-pair
intersections, and all21 signed incidence Grams diag(64,40,40,48).

Combining the separately chosen rows gives852 unordered pairs violating
edge reciprocity, and203 of231 upper-triangular entries violate the full
degree-Gram equation D^T D=48I+32J-C-8LL^T. Thus these controls explicitly
stop before global shared-edge or degree-Gram compatibility. The existence
of a different synchronized selection is neither proved nor disproved.

The independent audit initially rejected four producer witnesses because
the first model omitted incoming first-layer-label/target-vertex caps.
Those four outputs are preserved as `_preincoming_invalid.json` diagnostics.
The model was corrected, just those four cases were rerun, and the final
complete audit passed. No positive claim depends on the rejected outputs.

Files:

- `scratch_resume_uniform_quartet_probe.py/.json`: the restricted
  thirty-template pair-sum check, with no exclusion claim.
- `scratch_resume_uniform_fibre_incidence.py`: bounded labelled binary model.
- `scratch_resume_uniform_fibre_incidence_f0_q16.json`: first exact witness.
- `scratch_resume_uniform_fibre_incidence_audit.py/.json`: independent
  first-witness and universal K5 parity audit.
- `scratch_resume_uniform_fibre_incidence_all.py/.json`: sequential local
  controls and per-file hashes.
- `scratch_resume_uniform_fibre_incidence_all_audit.json`: completed
  independent all-fibre replay and explicit synchronization discrepancies.

No sealed historical artifact, root inventory, or submission.txt is changed.
