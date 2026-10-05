# Independent finite hypergraph controls v1

This checker imports no annealer/producer/scorer code. It reconstructs adjacency
sets, point occurrences, unordered pair uniqueness and every common-neighbor
count from raw triples. For every fully traced proposal it expands SplitMix64,
replays xoshiro256** with integer arithmetic modulo 2^64, independently checks
the swap domain, constructs the proposed triples and fully rescores them. It
compares the exact integer delta, acceptance, current/best raw states, counters,
all saved checkpoints, all CN cache entries, adjacency and reported outcomes.
It also checks whole256 versus split73+183 state bytes and trace sequence.

The frozen population is fourteen native engineering calls: nine successful
fixtures and five rejected corrupt checkpoints. No native worker is launched.
The rook9 control is independently checked as srg(9,4,1,2) and rejected as a
99-vertex target certificate. Corrupted score, best score, CN, duplicate triple
and zero RNG controls require the corresponding explicit checking diagnostic.
Additional mutated trace delta/energy/RNG/acceptance and corrupted rook adjacency
controls must fail; unrelated exceptions do not count as rejection.

All energies/deltas/counts/cache/RNG checks are exact integers. Temperature and
exponential acceptance are heuristic only: absolute temperature tolerance is
1e-12, and every probabilistic worsening decision must have distance greater
than 1e-12 from its threshold. Ambiguous decisions veto the gate. This is not a
proof about floating point on other libraries, or an approval of other runs.

Declare 300 seconds outer and 270 seconds internal. About ten thousand tiny
proposal rescoring checks and roughly 200 small checkpoints justify this
allocation; the old native receipt's 60 seconds is a tiny-control allocation,
not a research default. All hashes and checking share this invocation's deadline;
reserve 20 seconds for shutdown. Stop and preserve failure on any disagreement.

Success requires complete replay of the frozen control population, all positive
and negative controls, exact source/environment/binary/build bindings, receipts
and observed empty enclosing Linux group. The gate approves only these finite
engineering checks. No scientific search, trajectory generalization, exhaustive
coverage, nonexistence, or target resolution is claimed. Mathematical checking
uses adjacency sets independently of the producer's incremental/cache/bitset
implementation. Shared trusted components are SHA-256, Python arithmetic,
libm for heuristic acceptance, uv runtime and the policy supervisor/deadline.

Locked Windows checking invocation uses the root uv.lock environment and
acceleration/run_compute_command.py; the checker launches no cross-host worker.
Original raw artifacts and all failed versions are retained unchanged.
