# No Cayley Conway 99-graph

The exact audit `scratch_root_abelian_cayley_independent.py` excludes every
Cayley realization of an `srg(99,14,1,2)` without using a SAT-negative.

Every group of order `99=9*11` is abelian.  Indeed, the Sylow counts satisfy

```
n_11 | 9,   n_11 = 1 (mod 11),
n_3  | 11,  n_3  = 1 (mod 3),
```

so both Sylow subgroups are normal.  The only group types are therefore
`Z99` and `Z3 x Z3 x Z11`.

Let `D=-D` be the 14-element connection set of a hypothetical undirected
Cayley graph.  For every nonzero `t`, the partial-difference-set equation is

```
#{(a,b) in D^2 : a-b=t} = 1  if t in D,
                           2  otherwise.
```

When `t` belongs to `D`, the involution `(a,b) -> (-b,-a)` acts on the unique
ordered representation.  Its fixed point obeys `a=-b`, hence `t=2a` with
`a in D`.  Thus `D` is invariant under multiplication by two.

On the 49 inverse pairs, the doubling-orbit sizes are

```
Z99:                 1,3,5,5,5,15,15
Z3 x Z3 x Z11:       1,1,1,1,5,5,5,5,5,5,5,5,5
```

No union in the cyclic case has size seven.  In the noncyclic case there are
exactly `9 * binom(4,2) = 54` such unions.  Direct integer convolution checks
all 54 and none has the required difference multiplicities.  The independent
SAT encoding reaches the same two UNSAT decisions.

This only excludes the Cayley subclass; it does not exclude an arbitrary
Conway 99-graph.
