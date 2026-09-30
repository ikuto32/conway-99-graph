# Candidate complete scalar upper-envelope CNF build

Freeze source, this spec and the design before execution. New output only:
`results/20260930_count_min_upper_cnf`. Bound120 cooperative seconds and512MiB
planning memory. No native calls, solver, ledger, index or wave25 changes. Failure
leaves all partial artifacts, never changes old input/results. Build exact current
12-cut prefix155939/705845 plus the already inventoried720 OR/4500 AND variables
and20640clauses. Expected161159/726485,11834633 ASCII bytes. Any deviation rejects.

The input prefix is pinned CNFbaca89a7014e10e1fea9fd1873ef5dde4a090ab02dfe1791b4734a196677880b.
Read the original master channels and literal raw support, reconstruct every
threshold subset and all60nonmatching pairs ×9fibre pairs ×5groups. Match the old
inventory's raw recipe as data; import none of its code. Retain six malformed
recipe controls and three dropped-clause truth witnesses; enumerate all local
OR/AND/cardinality truth tables and all actual one-hot threshold alternatives.

Allocate thresholds in (coordinate,group,fibre,t=1,2) order, then products in
(coordinatepair,fibrepair,group,t=1..target) order. Emit all OR clauses first and
then each cell's products followed by its bound. OR clauses: (-x,q) and
(-q,x1,...). AND clauses: (-q,a),(-q,b),(q,-a,-b). Target1 uses one disjunction
of5; target2 uses10disjunctions each omitting one of10products. No merging.
Require exact suffix571440bytes and priorSHAa99c2118364159e9035e0353e21cd8e1e12fead8c0b82df7b16f826e52937845.

Preserve prefix body exactly. Write newheader+body+suffix to fresh .partial then
rename after count/byte checks. Save separate suffix/model/scope/manifest and
deterministic8MiB-raw gzip parts each under10MiB, checking literal recovery.

Candidate object ABI `decode(assignment, model_path)` checks every signed ID,
every actual clause, coordinate/group/channel agreement, marginal equations,
group/fibre quotas, inherited≥7 and all540 scalar inequalities. It returns only
count data, selectedIDs/localranklists, envelope records, no F/D/target. Extend
the existing checked third native count assignment with deterministically defined
new auxiliaries as a same-count positive calibration. Save it as CANDIDATE;
no new native SAT claim and no independent approval. Check malformed length,
duplicate/noninteger/range IDs, flipped new auxiliaries, header/count/terminator.
All producer checks remain distinct from later independent review.

CLI: locked/offline python -B acceleration/theory_20260930_count_min_upper_cnf.py --out acceleration/results/20260930_count_min_upper_cnf
