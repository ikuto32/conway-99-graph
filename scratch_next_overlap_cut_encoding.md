# Exact CP-SAT encoding of a variable-overlap capacity cut

The existing one-way common-neighbour product variables are sufficient for
an exact existential encoding of the no-gamma cut. They need not be made
equal to their Boolean products. The negative-part max terms require
exact equalities; one-sided max epigraph bounds are insufficient.

The cut is a necessary condition on a complete E0=0 overlap assignment.
No disjoint compression total is used. This note supplies an encoding and
compiled coefficients, not a new solver run or graph-existence claim.

## 1. Sparse polynomial and affine forms

Let k_ab be a Boolean variable for each of the1,680 overlapping-support
pairs O. Put k_ab=0 outside O, including the diagonal and same fibres.
Let D denote the1,680 disjoint-support pairs. Write alpha_(u,s) for the
fixed integer quota multipliers and beta_uv>=0 for the symmetric pair-cap
multipliers, with beta_uu=0. No edge-upper-bound multipliers are included.

Define

```text
q0(u,s) = 1 if group(s) belongs to support(u), else2,
t_uv = number of exact labels shared by u,v,

r0 = sum_(u,s) alpha_(u,s) q0(u,s)
     + sum_(u<v) beta_uv (2-t_uv),

a_ab = -sum_(s in label(b)) alpha_(a,s)
       -sum_(s in label(a)) alpha_(b,s)-beta_ab,

R(k) = r0+sum_(ab in O) a_ab k_ab
       -sum_(u<v,w) beta_uv k_uw k_vw.                (1)
```

Only wedges for which uw and vw belong to O occur in the last sum. For a
disjoint edge e=ab, its combined coefficient is affine:

```text
b_ab = sum_(s in label(b)) alpha_(a,s)
       +sum_(s in label(a)) alpha_(b,s)+beta_ab,

w_ab(k) = b_ab+sum_v beta_av k_vb+sum_v beta_bv k_va.  (2)
```

Every nonconstant coefficient in (2) is nonnegative. The necessary cut is

```text
R(k)+sum_(e in D) z_e >=0,
z_e=max(0,-w_e(k)).                                  (3)
```

The compiler expands the quota and cap groups individually, rather than
importing the existing cut evaluator. Its sparse `R_products` entries are
`[u,v,w,coefficient]`, with u<v and coefficient=-beta_uv<0. They identify
the existing generator variable named `p_{u}_{v}_{w}`. Overlap and disjoint
variable id maps are both recorded explicitly and are one-based.

## 2. Why one-way products are sufficient

For every wedge use an existing Boolean p_uvw satisfying

```text
p_uvw >= k_uw+k_vw-1.
```

Equivalently, the current generator has the clause
`not k_uw or not k_vw or p_uvw`. Thus p_uvw>=k_uw k_vw, while p may be1
when the product is0. Substitute p into (1), obtaining Rhat(k,p). Because
every beta is nonnegative,

```text
Rhat(k,p) <= R(k).                                   (4)
```

If the encoded inequality Rhat+sum exact z>=0 holds, (4) proves the true
cut (3). Conversely, if (3) holds, choosing all p equal to their true
products satisfies the one-way clauses and makes Rhat=R. Therefore the
projection of this existential encoding onto k is exactly the cut.

This remains true for several cuts sharing p: all their product
coefficients are nonpositive, so the same exact-product choice works
simultaneously. The current overlap generator uses p only in upper
common-neighbour caps, with nonnegative coefficients. Lowering an inflated
p to its actual product also preserves every such cap. Thus reuse of its
one-way products is sound without adding product upper implications.

The argument depends on these signs and uses of p. It does not authorize
reusing arbitrary auxiliaries that another constraint forces above their
true product, or changing the cut to use positive product coefficients.
Adding the two upper implications would also be correct, but is not
required here.

## 3. Exact max and finite domains

For a compiled affine w_e=b_e+sum_j c_ej k_j, all c_ej>=0, hence the safe
integer bounds are

```text
L_e=b_e, U_e=b_e+sum_j c_ej,
0<=z_e<=max(0,-L_e).                                 (5)
```

These bounds need no degree, compression, or overlap consistency
assumptions. They may be tightened only using proved constraints.

There are three cases:

- L_e>=0: z_e is identically0 and needs no variable or affine expression.
- U_e<=0: replace z_e by the affine expression-w_e.
- L_e<0<U_e: use an exact max equality, such as
  `model.add_max_equality(z_e, [0, -w_expression])`.

An equivalent exact reified encoding selects either w_e<=0,z_e=-w_e or
w_e>=0,z_e=0. Equality at zero may select either branch. Each branch must
enforce both its sign and its equality.

Only adding z_e>=0 and z_e>=-w_e is unsound for the existential constraint
(3): z has a positive coefficient and can be inflated to pass a false
cut. A bounded counterexample is w=-1+2k, R=-1, k=1, and z in[0,1]. The
true score is-1, but the one-sided epigraph permits z=1 and encoded score0.

No R variable is required. If desired, a safe domain is

```text
R_lower=r0+sum_j min(0,a_j)+sum_wedges(-beta_uv),
R_upper=r0+sum_j max(0,a_j).                          (6)
```

It also bounds Rhat when its product variables are Boolean. The compiled
files record (5) and (6), using exact integers.

## 4. Integration sketch

This is pseudocode for adding one compiled cut to the existing overlap
model; the generator has not been edited or run by this task.

```python
rhs = cut['R_constant']
rhs += sum(coefficient * overlap_by_id[var_id]
           for var_id, coefficient in cut['R_linear'])
rhs += sum(coefficient * common_product[u, v, w]
           for u, v, w, coefficient in cut['R_products'])

negative_parts = []
for row in cut['w_affine']:
    if row['mode'] == 'zero':
        continue
    w = row['constant'] + sum(coefficient * overlap_by_id[var_id]
                              for var_id, coefficient in row['terms'])
    if row['mode'] == 'affine_negative':
        negative_parts.append(-w)
    else:
        z = model.new_int_var(0, row['z_upper'],
                              f"cut_{cut['name']}_z_{row['disjoint_id']}")
        model.add_max_equality(z, [0, -w])
        negative_parts.append(z)
model.add(rhs + sum(negative_parts) >= 0)
```

`common_product[u,v,w]` must refer to the actual one-way product of
`overlap[u,w]` and `overlap[v,w]`, not an independently renamed Boolean.
The current generator can retain those variables in a dictionary when
constructing them. The supplied key order matches its u<v loop.

For a sign-conjugate cut, apply the corresponding vertex permutation to
every overlap and wedge reference, sorting the two wedge endpoints again.
The wedge centre remains the permuted centre. This implements score(gK)
with the same fixed coefficients. All beta signs remain nonnegative, so
the product argument is unchanged. A finite selected family gives valid
necessary constraints; full sign invariance requires all128 conjugates
or an equivalent complete orbit representative treatment.

## 5. Measured complexity of the five current cuts

The existing generator already has65,520 one-way product variables. The
union needed by these five fixed-label cuts is24,492 of those same wedges;
no additional product variables are mathematically necessary.

| Cut | R linear terms | R product terms | w affine terms | Exact max variables | Identically zero z |
| --- | ---: | ---: | ---: | ---: | ---: |
| original | 1,566 | 6,456 | 16,288 | 989 | 691 |
| alternative0 | 1,545 | 6,232 | 15,840 | 937 | 743 |
| alternative1 | 1,579 | 6,560 | 16,544 | 979 | 701 |
| alternative2 | 1,570 | 6,508 | 16,416 | 1,002 | 678 |
| alternative3 | 1,550 | 5,924 | 15,168 | 974 | 706 |

Together these require4,881 max variables/constraints and five score
constraints. No case currently falls in the affine-negative simplification.
The80,256 affine term occurrences shown include rows whose z is zero and
can therefore be skipped. Separate w variables are unnecessary when the
max API accepts the affine expressions directly. Actual solver presolve
and branching costs have not been measured.

Across these five cuts the compiled w bounds lie inside[-62,281], each
z upper bound is at most62, and R lies between-60,459 and14,107.
These ranges are far inside signed64-bit arithmetic; future cuts should
recompute their own bounds rather than reuse these numbers.

Naively adding every sign conjugate of all five would raise the number of
max constraints to at most624,768 before deduplication or presolve. The
product variables can still be shared. This note does not propose or run
that much larger model.

## 6. Files, comparisons, and scope

```text
scratch_next_overlap_cut_compile.py
scratch_next_overlap_cut_compiled.json
scratch_next_overlap_cut_compile_check.json
```

The pure-stdlib compiler verified60 complete evaluations: five cuts on
the original plus four saved alternative K assignments, and on the seven
single-sign images of the original. It compared all100,800 affine edge
coefficients and every polynomial RHS with a separate direct semantic
evaluation. The5-by-5 score matrix matches the stored cut bank; the eight
original-cut sign scores match the independent no-gamma review controls.

The recorded hashes bind all candidate inputs, the original Farkas
certificate and semantic map, all four alternative Farkas certificates,
their independent audits, the bank/review comparison JSONs, and the
compiler source. The short check file additionally hashes the compiled
coefficient file. A future model should verify these bindings before
using or relabeling the coefficients.

No cut evaluator was imported, no solver was run, no generator was edited,
and no new overlap assignment was created. This work establishes exact
encoding semantics and reusable coefficients. Passing any such model
still proves no adjacency completion or Conway graph existence.
