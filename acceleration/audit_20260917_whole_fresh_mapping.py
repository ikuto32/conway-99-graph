"""Independent whole-family128 preparation/selection mapping check; no producer imports."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from math import isfinite
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
LABELS = [(2*a+s, 2*b+t) for a in range(7) for b in range(a+1, 7) for s in range(2) for t in range(2)]


def require(ok, msg):
    if not ok: raise ValueError(msg)


def path(p):
    p = Path(str(p).replace('\\', '/'))
    return p.resolve() if p.is_absolute() else (ROOT/p).resolve()


def key(p): return path(p).relative_to(ROOT).as_posix()


def digest(p):
    h = sha256()
    with path(p).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()


def graph(edges):
    require(type(edges) is list and len(edges) == 168 and all(type(e) is list and len(e) == 2 and
            all(type(v) is int for v in e) and 0 <= e[0] < e[1] < 84 for e in edges), 'graph format')
    result = tuple(tuple(e) for e in edges)
    require(result == tuple(sorted(set(result))), 'graph canonical/unique')
    return result


def graph_digest(edges): return sha256(json.dumps(edges, separators=(',', ':')).encode()).hexdigest()


def partial_caps(edges):
    rows = [0]*99
    def add(u, v): rows[u] |= 1 << v; rows[v] |= 1 << u
    for v in range(1, 15): add(0, v)
    for v in range(1, 15, 2): add(v, v+1)
    for v, pair in enumerate(LABELS, 15):
        for s in pair: add(v, s+1)
    for u, v in edges: add(u+15, v+15)
    require(list(map(int.bit_count, rows)) == [14]*15+[6]*84, 'partial degrees')
    require(all((rows[u]&rows[v]).bit_count() <= 2-int(bool(rows[u]&(1 << v)))
                for u, v in combinations(range(99), 2)), 'full99 partial cap')


def move_shape(move, base, final):
    """Derive connected cycle components from changed edges, not cycle metadata."""
    old, new = set(map(tuple, move['removed'])), set(map(tuple, move['added']))
    require(old <= base and not new & base and not old & new and final == (base-old)|new, 'exact replacement identity')
    require(2 <= len(old) <= 6 and len(old) == len(new) == move['changed_edges'], 'changed-edge population')
    degree_old = Counter(v for e in old for v in e); degree_new = Counter(v for e in new for v in e)
    require(degree_old == degree_new and all(n == 1 for n in degree_old.values()), 'changed matching endpoint coverage')
    group, kind = move['root_group'], move['matching_class']
    require(type(group) is int and 0 <= group < 7 and kind in ('same_0', 'same_1'), 'whole coordinate')
    symbol = 2*group+int(kind[-1])
    require(all(symbol in LABELS[v] for v in degree_old), 'coordinate literal-label cohort')
    require(all({s//2 for s in LABELS[u]} & {s//2 for s in LABELS[v]} == {group} for u, v in old|new), 'same-sign support domain')
    adjacency = {v: set() for v in degree_old}
    for a, b in old|new: adjacency[a].add(b); adjacency[b].add(a)
    require(all(len(ns) == 2 for ns in adjacency.values()), 'alternating graph not2regular')
    unused = set(adjacency); components = []
    while unused:
        todo = [min(unused)]; component = set()
        while todo:
            v = todo.pop()
            if v in component: continue
            component.add(v); todo.extend(adjacency[v]-component)
        require(len(component) % 2 == 0 and len(component) >= 4, 'alternating component parity')
        components.append(frozenset(component)); unused -= component
    advertised = move['alternating_cycles']
    require({frozenset(c) for c in advertised} == set(components) and len(advertised) == len(components), 'cycle metadata components')
    for cycle in advertised:
        require(len(cycle) == len(set(cycle)), 'cycle repeats vertex')
        for k, a in enumerate(cycle):
            edge = tuple(sorted((a, cycle[(k+1)%len(cycle)])))
            require(edge in (old if k % 2 == 0 else new), 'cycle parity/edge metadata')
    return group, kind, tuple(sorted(len(c)//2 for c in components))


def choose_independently(scores, strata, excluded):
    ordered = sorted(set(scores)-excluded, key=lambda i: (scores[i], i))
    require(len(ordered) >= 128, 'eligible cohort too small')
    first = ordered[:64]
    buckets = {}
    for i in ordered[64:]: buckets.setdefault(strata[i], []).append(i)
    extra = []
    depth = 0
    while len(extra) < 64:
        for stratum in sorted(buckets):
            if len(buckets[stratum]) > depth:
                extra.append(buckets[stratum][depth])
                if len(extra) == 64: break
        depth += 1
    return first+extra, ordered


def validate_request(request, selected, scores, positions, strata, family):
    require(request['status'] == 'EXPLICIT_WHOLE_FRESH_STAR_COHORT_REQUEST_V2' and
            request['objective_id'] == 'ORIGINAL_STAR_SIMPLEX_PDHG_V1' and request['indices'] == selected and
            request['requested_count'] == 128 and request['iterations'] == 500, 'request population/objective')
    require(request['domain_source'] == 'ORIGINAL_NATIVE_DOMAIN_TABLES_NOT_PROPAGATION_SURVIVORS' and
            request['LP_runs'] == request['native_domain_processes'] == request['GPU_processes'] == 0, 'request domain/process scope')
    require(len(request['records']) == 128, 'request record count')
    for position, (i, row) in enumerate(zip(selected, request['records'])):
        group, kind, sizes = strata[i]
        require(row['proposal_index'] == row['whole_family_index'] == row['original_native_index'] == i and
                row['native_index_convention'] == 'ZERO_BASED_COMPLETE_WHOLE_FAMILY_ROW', 'whole/native index conflation')
        require(row['root_group'] == group and row['matching_class'] == kind and row['alternating_cycle_sizes'] == list(sizes) and
                row['changed_edges'] == sum(sizes), 'whole cycle stratum')
        expected_role = 'global_refined_upper64' if position < 64 else 'round_robin_coordinate_cycle_shape64'
        require(row['roles'] == [expected_role], 'selection role')
        require(row['refined_upper'] == scores[i] and row['refined_gpu_result_index'] == positions[i], 'score/row mapping')
        require(row['overlap_edges_sha256'] == graph_digest(family['overlap_candidates'][i]), 'graph identity hash')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--request', type=Path, required=True)
    p.add_argument('--preflight', type=Path, required=True)
    p.add_argument('--producer-controls', type=Path, required=True)
    p.add_argument('--preregistration', type=Path, default=Path('docs/NEXT_20260917_WHOLE_FRESH.md'))
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    require(not args.out.exists(), 'preserve prior review')
    started = time.perf_counter(); bindings = {}
    def bind(p, h=None):
        k = key(p)
        if k not in bindings: bindings[k] = digest(p)
        require(h is None or bindings[k] == h, 'artifact identity mismatch '+k)
        return bindings[k]
    def read(p):
        bind(p); d = json.loads(path(p).read_bytes())
        for f, h in d.get('inputs_sha256', {}).items(): bind(f, h)
        return d
    for f in (__file__, 'acceleration/rank_fresh_whole_v2.py', 'acceleration/rank_fresh_star_pdhg.py', args.preregistration, 'uv.lock'): bind(f)
    request = read(args.request); preflight = read(args.preflight); producer_controls = read(args.producer_controls)
    family = read(request['family_path']); family_audit = read(request['family_audit_path'])
    search = read(request['original_search_path']); search_audit = read(request['search_audit_path'])
    search_dir = path(request['original_search_path']).parent
    search_manifest = read(search_dir/'manifest.json'); stage = read(request['refined_stage_path'])
    gpu = read(stage['gpu_output_path'])
    require(family['legal_count'] == family_audit['legal_count'] == len(family['overlap_candidates']) == len(family['moves']) == 81000 and
            family_audit['status'] == 'INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS', 'audited whole-family count')
    require(family['selector'] == family_audit['selector'] == 'all' and family['coordinate_count'] == 14, 'whole family coordinates')
    require(search_audit['status'] == 'INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS' and
            stage['stage'] == 'refined' and stage['steps'] == 2000, 'audited refined score stage')
    require(search['family_association']['native_sha256'] == bind(request['family_path']) and
            stage['gpu_output_sha256'] == bind(stage['gpu_output_path']), 'scored family identity')
    audited = {key(f): h for f, h in search_audit['inputs_sha256'].items()}
    for f in (request['family_path'], request['family_audit_path'], request['refined_stage_path'], stage['gpu_output_path'], search_dir/'manifest.json'):
        require(audited[key(f)] == bind(f), 'input outside prior independent search audit')
    base_path = search['family_association']['initial_path']
    base = graph(read(base_path)['overlap_edges_outer_zero_based'])
    bind(base_path, search['family_association']['initial_sha256'])
    excluded_graphs = {base}; current_ids = []
    for row in search['records']:
        g = graph(read(row['candidate_path'])['overlap_edges_outer_zero_based']); bind(row['candidate_path'], row['candidate_sha256'])
        require(g == graph(family['overlap_candidates'][row['proposal_index']]), 'current64 family index identity')
        excluded_graphs.add(g); current_ids.append(row['proposal_index'])
    require(len(current_ids) == len(set(current_ids)) == 64, 'current64 distinct indices')
    previous = search_manifest['previous_candidates']
    for row in previous:
        doc = read(row['candidate_path']); bind(row['candidate_path'], row['candidate_sha256'])
        g = graph(doc['overlap_edges_outer_zero_based'])
        require(graph_digest(doc['overlap_edges_outer_zero_based']) == row['overlap_edges_sha256'], 'previous canonical graph binding')
        excluded_graphs.add(g)
    ids = stage['proposal_indices']
    require(len(ids) == len(gpu['results']) == 2049 and ids[0] is None and len(set(ids[1:])) == 2048, 'refined index population')
    scores, positions, strata, graphs = {}, {}, {}, {}
    for pos, (i, row) in enumerate(zip(ids, gpu['results'])):
        require(row['candidate_index'] == pos and len(row['checkpoints']) == 1, 'refined GPU row position')
        checkpoint = row['checkpoints'][0]
        vals = [row['initial']['primal_upper'], checkpoint['last']['primal_upper'], checkpoint['average']['primal_upper']]
        require(checkpoint['iterations'] == 2000 and all(type(v) in (int, float) and isfinite(v) for v in vals), 'refined finite upper values')
        require(isfinite(checkpoint['best_upper']) and abs(checkpoint['best_upper']-min(vals)) < 1e-10, 'saved best-upper consistency')
        if i is None: continue
        require(type(i) is int and 0 <= i < 81000, 'refined native index range')
        scores[i] = min(vals); positions[i] = pos
        graphs[i] = graph(family['overlap_candidates'][i])
        strata[i] = move_shape(family['moves'][i], set(base), set(graphs[i]))
    require(len(set(graphs.values())) == 2048, 'distinct scored graph population')
    excluded = {i for i, g in graphs.items() if g in excluded_graphs}
    require(set(current_ids) <= excluded, 'current64 not excluded')
    selected, ordered = choose_independently(scores, strata, excluded)
    validate_request(request, selected, scores, positions, strata, family)
    require(request['excluded_refined_indices'] == sorted(excluded) and request['excluded_current64_indices'] == sorted(current_ids) and
            request['eligible_unused_refined_count'] == len(ordered) and request['refined_scored_population'] == 2048 and
            request['bound_previous_candidate_record_count'] == len(previous), 'exclusion population metadata')
    require(len(set(selected)) == 128 and len({graphs[i] for i in selected}) == 128 and not set(selected) & excluded, 'selected unique fresh graphs')
    for row in request['records']:
        doc = read(row['prepared_candidate_path']); bind(row['prepared_candidate_path'], row['prepared_candidate_sha256'])
        i = row['proposal_index']
        require(graph(doc['overlap_edges_outer_zero_based']) == graphs[i] and doc['proposal_index'] == doc['original_native_index'] == i and
                doc['native_index_convention'] == 'ZERO_BASED_COMPLETE_WHOLE_FAMILY_ROW' and
                doc['family_sha256'] == bind(request['family_path']) and key(doc['family_path']) == key(request['family_path']), 'prepared raw candidate identity')
        require(doc['root_group'] == strata[i][0] and doc['matching_class'] == strata[i][1] and
                doc['alternating_cycle_sizes'] == list(strata[i][2]), 'prepared move geometry')
        partial_caps(graphs[i])
    controls = [dict(name='real128_materializations_independently_reconstructed', outcome='PASS')]
    for name in ('off_by_one_native_index', 'wrong_cycle_shape', 'wrong_refined_row', 'duplicate_selected_index', 'wrong_selection_role', 'swapped_ranked_diverse_order'):
        bad = deepcopy(request)
        if name == 'off_by_one_native_index': bad['records'][0]['original_native_index'] += 1
        if name == 'wrong_cycle_shape': bad['records'][0]['alternating_cycle_sizes'] = [6]
        if name == 'wrong_refined_row': bad['records'][0]['refined_gpu_result_index'] += 1
        if name == 'duplicate_selected_index': bad['indices'][1] = bad['indices'][0]
        if name == 'wrong_selection_role': bad['records'][0]['roles'] = ['round_robin_coordinate_cycle_shape64']
        if name == 'swapped_ranked_diverse_order': bad['indices'][0], bad['indices'][64] = bad['indices'][64], bad['indices'][0]
        try: validate_request(bad, selected, scores, positions, strata, family)
        except ValueError as e: controls.append(dict(name=name, outcome='REJECT', reason=str(e)))
        else: raise ValueError('corrupted mapping accepted: '+name)
    require(preflight['status'] == 'WHOLE_FRESH_V2_PREFLIGHT_PASS' and preflight['selected_indices'] == selected and
            preflight['iterations'] == 500 and preflight['request_sha256'] == bind(args.request) and
            preflight['native_processes'] == preflight['GPU_processes'] == preflight['LP_runs'] == 0, 'saved preflight state')
    require(all(digest(f) == h for f, h in bindings.items()), 'source/input changed during audit')
    report = dict(status='INDEPENDENT_WHOLE_FRESH_V2_MAPPING_PASS', timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=request['source_commit'], source_additions_explicitly_hashed=True, command=[sys.executable]+sys.argv,
        working_directory=str(Path.cwd()), python=platform.python_version(), inputs_sha256=bindings,
        selected_indices=selected, GPU_processes=0, native_domain_processes=0, LP_runs=0,
        family_population=81000, refined_scored_population=2048, excluded_refined_indices=sorted(excluded),
        current_LP_excluded_count=64, prior_candidate_records=len(previous), eligible_unused_refined_count=len(ordered),
        ranked_selected=64, diverse_selected=64, distinct_selected_graphs=128,
        selected_cycle_strata=[dict(root_group=stratum[0], matching_class=stratum[1], changed_edges_per_cycle=list(stratum[2]),
                                    count=sum(strata[i] == stratum for i in selected)) for stratum in sorted({strata[i] for i in selected})],
        exact_graph_identity_comparison_used=True, full99_selected_partial_caps_checked=128*4851,
        cycle_shapes_derived_from_changed_edge_connected_components=True, controls=controls,
        producer_controls_artifact_path=key(args.producer_controls), producer_controls_reexecuted=False,
        preregistration_path=key(args.preregistration), selection='64 smallest refined upper then64 round-robin lexicographic coordinate/cycle-component strata, with exact graph duplicate exclusions',
        scope='Engineering verification of this128-case whole-family preparation, materialization, selection and frozen preflight only; no domain enumeration, GPU ranking, exclusion or global coverage claim',
        score_scope='Historical2000-iteration old-edge numerical scores choose a future original-star500-iteration cohort; neither numerical score is a certificate',
        shared_trusted_components=['Python standard library','raw whole-family graph convention','hash-bound prior independent family/search audits'],
        producer_imported=False, elapsed_seconds=time.perf_counter()-started,
        target_resolution='UNKNOWN', overall_search_coverage='UNKNOWN; no validated denominator')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f: json.dump(report, f, indent=2); f.write('\n')
    print(json.dumps(dict(status=report['status'], eligible=len(ordered), excluded=len(excluded), selected=128)))


if __name__ == '__main__': main()
