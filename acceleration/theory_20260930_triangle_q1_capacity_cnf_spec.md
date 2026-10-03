# Exact component-capacity-aware Q1 projection

Freeze before build or solve. Same fixed Wave149 core only, with M_i=M,
identity01/02 matchings and shift6 cross12. No target automorphism or
unrestricted core containment. Preserve all old factors, CNFs and runs.

The five known Q1 factors have already verified component overflows. The
next question is whether ANY binary24x60 factor(C0;C1) satisfies its exact
Gram/margins and component partial-column counts<=2. This does not ask for
C2 or the residualD. A positive answer is a necessary first stage only.

Use the independently checked canonical C0 and600 unforced C1 entries from
the joint model. Require12row sums10,60column sums2,144linear C0-cross Gram
equations, and66 exact Gram equations between C1 rows. All C0 constants and
its within-block Gram are already fixed. Add180 upper bounds on known+free
C0/C1 incidence in each of the three core components and60 columns. The
upper bound2 follows from the separately checked component-kernel theorem,
since any full factor has exactly2 per component column and C2 is nonnegative.
These inequalities preserve every full fixed-core factor, but need not
suffice for extension. Both directions of this projected encoding require
independent checking; its full-core exclusion implication is only one-way.

Each quadratic product has a fully equivalent AND gate; exact row/Gram
equations and capacity inequalities use the frozen bidirectional prefix
counter. Save full fixed/free24x60 map, target24x24 Gram, every counter and
product clause interval, component rows and kernel premises. A decoded SAT
object must independently satisfy all raw clauses, margins,576Gram entries
and180capacity inequalities. Then each C1 column is a nonmatching pair,
and its60columns give a Q1 permutation; preserve both representations.

Cheap controls run before any research solver: exact counter truth-table
controls, literal replay of both known24row factors, and detection of their
capacity violations. A synthetic positive may calibrate the checker but
must never be called a factor of the frozen research Gram.

Build limit120seconds/8GiB, no solver calls, deterministic exact arithmetic.
If built and independently gated, proposed native pilot is at most300seconds
and1,000,000conflicts with existing calibrated4GiB/10GiB-proof controls.
Root must explicitly agree to a fresh gated launch. If the concurrently
running stronger joint-factor pilot resolves the fixed core first, do not
launch this projection on an already excluded family.

Command: `uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_q1_capacity_cnf.py --out acceleration/results/20260930_triangle_q1_capacity_cnf`, with `UV_PROJECT_ENVIRONMENT=build/research-venv`.
