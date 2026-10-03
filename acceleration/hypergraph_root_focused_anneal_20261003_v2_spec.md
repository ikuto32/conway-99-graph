# Root-focused native construction source V2

V1 source/build01 are preserved. V2 adds explicit braces/newline to the
Graph constructor degree-check loop to satisfy Werror misleading-indentation.
No native mathematical/state/objective/proposal/retention schema changes;
all V1 schema names remain format version1. Changed source/binary requires
a fresh independent engineering and saved-object gate with exact V2 pins.

Preparation only. Preserve weight60 engineV2, designc299 and independent
reviewdf46. No build, finite native controls or scientific optimization is
authorized by this source document. ROOT must review the exact frozen build
plan before a supported engineering invocation; science additionally needs
changed-source finite and pre-output saved-object gates, independently checked
exact start and a fresh frozen command/resource admission.

## Domain, objective and restricted moves

Target domain:99 labelled points,231 labelled ordered triples, every point
in seven triples, each unordered pair in at most one triple. The point graph
therefore has degree14. Generic controls have n9 or12 and hyperdegree2, and
must never enter the target99 certificate gate. Production root is11.

Objective SRG_ROOT_LOCAL_PAIR_RESIDUAL_V1 uses exact signed64-bit integers:
E_lambda=sum over adjacent unordered pairs(CN-1)^2;
E_mu=sum over nonadjacent unordered pairs(CN-2)^2;
R_root=sum over current nonneighbors of root(CN(root,v)-2)^2;
Froot=60E_lambda+R_root. E_mu is a separate diagnostic, not part of Froot.
This objective cannot be compared with globalF60 values. In these domains
CN<=14; integer intermediate sums fit64bits. No floating-point score is used.

Freeze every incident root triple with its original label and literal ordered
vertices. Derive sorted mutable indices by excluding those labels: exactly224
in target99. Each proposal samples two distinct mutable labels and two vertex
positions. Its exclusive selected points are exchanged, permitting one shared
point between lines. New pairs must be absent after the old pairs are removed.
Degree/linearity are checked again from complete raw triples at verification
intervals. Frozen rows and root adjacency are compared with original source
rows on resume, not merely a self-consistent serialized frozen list. This
restricted move space has no verified connectivity/exhaustive coverage.

## RNG, acceptance and explicit probe controls

Distribution MUTABLE_LABELLED_LINES_REJECTION_BOUNDED_XOSHIRO256SS_V1
reuses the disclosed prior splitmix64 expansion/xoshiro256** transition, but
changes bounded selection. For bound b, threshold=(-b) mod b in unsigned64;
draw until word>=threshold, then word mod b. Reject after1024 consecutive
rejections with a preserved error. Thus modulo bias is removed conditional on
uniform64-bit words; no claim that a deterministic PRNG is an independent
random source. Draw first mutable index in[0,M), second in[0,M-1) then skip
the first, and positions in[0,3). This is a new distribution gate.

Invalid proposals consume selection words only. Every admissible ordinary
proposal also consumes one acceptance word even if forced/mixing/downhill.
u=(word>>11)*2^-53; accept forced, during declared mixing, deltaF<=0, or
u<exp(-deltaF/T) for positive T. Linear temperature uses completed proposal
step after mix_steps, clamped at schedule_steps. Temperatures are bounded
finite0..1000; they guide search, not proof claims. Resume requires identical
seed/mix/schedule/T/forced/root/checkpoint interval/input/probe identities.

ROOT_FOCUSED_CONTROL_PROBES_V1 is a finite control-only tape: count, then
labelled ti tj pi pj rows, END. It explicitly tests all135 labelled proposals
for rook9 and prism9 including frozen labels. Frozen-root proposals are vetoed.
Valid probes compute full incremental candidate deltas and always roll back;
they consume no RNG, are never accepted and are not scientific optimization.
Ordinary proposals never draw frozen labels. Probe identity persists in state;
split tapes use absolute completed step. Wrapper run mode supplies no probe.

## Graph-only input and authentication boundary

ROOT_FOCUSED_GRAPH_INPUT_V1 has keyed lines n,degree,root,
source_matrix_sha256,source_triples_sha256,selection_report_sha256,triples count,
literal ordered rows and END. selection_report_sha256 identifies the producer's
selection.json, not an independent verification report. The wrapper hashes
the whole native input and passes graph-identity. Native validates hash syntax,
domain, rows and scores; it has no crypto library and does not authenticate
bytes itself. Trusted shared authentication is the wrapper/raw SHA256 checking
path plus ROOT's separately authored exact input check. On resume the original
frozen-reference input is required for imported states. Built-in fixtures use
explicit zero provenance hashes and original fixture literals instead.

Checkpoint candidate start export203e was chosen from two complete censuses
by ROOT's separate export producer. Its intended root11/L0/mu3484/R50 and
frozen labels15,18,22,57,61,82,154 remain input claims pending ROOT's direct
check. This engine preparation imports none of those bytes yet.

## State, trace and retained populations

State magic ROOT_FOCUSED_ANNEAL_STATE_V1. Exact keyed serialization order is
the frozen C++ write_state implementation: objective/weight/kernel/distribution,
n/degree/root/provenance,probe identity,seed/mix/schedule/T/forced/checkpoint
interval,step/admissible/accepted/best_updates/local_updates,current and best
Froot/E_lambda/E_mu/Rroot,RNG4words,frozen labelled literal rows,sorted mutable
indices,current/best_root triples,upper-triangle CN cache,first_localzero and
best_localzero_mu snapshots,END. Decimal RNG words are unsigned64 and all-zero
states are rejected. Complete current/best/snapshot graphs reconstruct exactly.

The three populations are distinct:

- best_root retains the first strict minimum Froot visited by the producer;
  ties retain the previous graph. Current and best are exported separately.
- first_localzero retains a complete first producer-observed current object
  with E_lambda=Rroot=0, including invocation initial state. The external
  earliest-attainment statement remains UNKNOWN across sparse unlogged history.
- best_localzero_mu retains the first local zero and every subsequently
  strictly lower E_mu localzero object immediately. Its public guarantee is
  minimum E_mu among actual retained localzero graph objects and inherited
  checked retained snapshots, not a global graph minimum or verified complete
  trajectory. Checkpoints/final/current objects also belong to the raw saved
  population; each accepted localzero object is compared before any checkpoint,
  so splitting cannot introduce an unexamined lower saved mu object.

Each snapshot stores full ordered triples,step/counters/RNG and selection
reason. Raw selected-object format ROOT_FOCUSED_SELECTED_OBJECT_V1 includes
provenance,frozen/mutable rows,root/full score components and snapshot. Immediate
retention files,final first/best-localzero objects and four adjacency exports
are independently checkable. Resume carries both snapshots and their counters.
Scheduled checkpoints use deterministic step intervals, not wall-clock events,
so whole/split final state and concatenated full finite traces can match bytes.
Cooperative deadline/signal stops save final current/best/selections. SIGKILL
can only leave earlier immutable checkpoints; absolute shutdown is not claimed.

Trace ROOT_FOCUSED_MOVE_V1 stores old/proposed triples,indices/root/probe flag,
frozen/exclusive/linearity diagnostics,selection draw count,admissible/accepted,
temperature/mixing,integer candidate deltas in all components,current/best
scores,local-selection flags,counters and exact before/after RNG words as
decimal strings. Full finite traces are replayed; sparse science traces support
only explicitly anchored segments, never bridged gaps.

Pair-cost controls enumerate172 exact CN/edge-category cases per successful
call, including root-pair status0/1. Root adjacency is frozen in production;
root-edge category arithmetic is still calibrated generically, rather than
silently assuming a cached outsider population. Rejected valid proposals roll
back all adjacency/CN/components and raw triples remain untouched.

Froot0 is a partial root condition. Support multiplicities need their own
literal audit before asserting an84-label scaffold. Every possible full target
zero additionally needs a separate full99 symmetric binary zero-diagonal
integer A^2=12I-A+2J validator. Rook9 controls are not99 certificates.
