# Full point-graph hypergraph annealer v1

Objective SRG_SQUARED_PAIR_RESIDUAL_V1 is the exact integer sum over unordered
point pairs of (common(i,j)+Aij-2)^2, smaller is better. Target domain is 99
labelled points and 231 linear three-element triples, each point occurring in
seven triples; the binary point graph consequently has degree14. No triangle
core, Hadamard support, or target automorphism is required. This objective and
domain differ from old fixed-core permutation/factor Gram annealers. No connected
move-space, exhaustive coverage, success probability or novelty is claimed.

The initial target object is 33 triples {x,x+33,x+66} plus all99 translates
of {0,1,4} and {0,7,18}. Fourteen distinct connection differences guarantee
linearity and degree. This is merely a starting state: admissible trades may
break its cyclic symmetry. The control rook9 object consists of the three rows
and three columns of a labelled3x3 grid; pointdegree2 and graphdegree4, with E0.
Rook9 is never a target99 result.

A proposal selects two distinct labelled triples and one vertex of each using
the explicitly specified64-bit RNG. Modulo selection introduces finite bias;
no uniform trajectory assertion is made. Require the six vertices to be distinct
and all four new graph pairs absent. Swap x and y in {x,a,b},{y,c,d}. Remove
(x,a),(x,b),(y,c),(y,d), then add (y,a),(y,b),(x,c),(x,d). This preserves each
point's occurrence count and pair uniqueness. Other valid trades are not explored.

For a single edge uv toggled by delta, for each w other than u,v, CN(u,w)
changes by delta*A(v,w), and CN(v,w) by delta*A(u,w); CN(u,v) is unchanged.
Update each affected squared residual using 2*r*delta+delta^2, then the uv
adjacency residual. Sequential toggles handle interacting edge changes. Rejected
proposals roll back all eight toggles in reverse order. Engineering verification
reconstructs the whole graph and bitset-intersection CNs after every proposal;
an independent implementation must derive/recompute every saved delta using
adjacency sets from raw triples, and attempt to falsify these formulas.

Scores/deltas are signed64-bit integers. Floating temperature and exponential
acceptance guide search and certify nothing. Temperature is bounded in [0,1000],
linearly interpolated from t_start to t_end over schedule_steps after mix_steps
proposals, then held at t_end. Mixing accepts all admissible trades. Every valid
proposal consumes one64-bit acceptance draw even when forced or nonworsening;
invalid proposals consume only four proposal draws. Uniform threshold uses the
upper53 draw bits divided by2^53. RNG seed expansion and all transition operations
are explicit in the source; arithmetic wraps modulo2^64.

Raw controls preserve every proposed trade's indices/positions, old/proposed
triples, validity, acceptance, energy/delta, temperature, acceptance draw and
before/after RNG words. Current/best raw labelled triples, exact energies, full
CN cache, RNG and counters are in immutable HYPERGRAPH_ANNEAL_STATE_V1 text
checkpoints. Loading independently reconstructs domain, cache and energies and
rejects corrupted score/cache/domain/zero-RNG controls. Whole256 proposals must
match split73+183 byte for byte. Positive rook9E0, forced/greedy/annealed/mixed
target99 controls and five corrupted checkpoint controls precede research.

Compilation/controls use the pinned Linux g++13.3.0 binary, flags -std=c++17
-O3 -Wall -Wextra -Werror, minimal uv.lock environment with tqdm4.67.1, and
supervisor INSIDE Linux. Compiler and native child inherit the enclosing GNU
timeout group; native calls also get a foreground GNU guard and prlimit memory/
file bounds. All hashing/preparation/children share the producer CommandDeadline.
Observed receipts and enclosing supervisor cleanup describe containment only.

Build allocation is evidence-based180s outer/150s producer, a small C++ source
compared with previous similar parser build. Controls use300s outer/270s producer,
60s per tiny child as an explicit engineering limit for at most2048 checked
proposals, not a scientific solver default. Research native time must be supplied
explicitly from calibrated throughput/resource observations. External review is
mandatory by1800s of active computation; without a timely review the producer
stops children. No review extends the fixed command deadline.

Research requires a new INDEPENDENT_HYPERGRAPH_ANNEAL_V1_CONTROLS_PASS gate bound
to exact source/spec/wrapper/environment/binary/build identities. Declare the
seed, temperatures, proposal/mixing schedule, resource/time allocation and sparse
trace selection before launch. Save current/best/RNG checkpoints at most every
15seconds and periodic full cache checks; final state is always saved on orderly
stop. Time/resource stops prove no exclusion. Sparse scientific traces are sampled
and must not be called complete transition verification. A raw target E0 needs
a separate full99x99 integer SRG validator; discovery does not approve itself.

Locked invocation inside Linux: UV_PROJECT_ENVIRONMENT=/tmp/conway99-native-budget-v1-env
/root/.local/bin/uv run --project acceleration/native_budget_env_v1 --locked
python acceleration/run_compute_command.py ... -- /usr/bin/python3
acceleration/prepare_20261002_hypergraph_anneal_v1.py ... . Preserve original
receipts and create a new version/recheck whenever execution code changes.
