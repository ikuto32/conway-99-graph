"""Select a bounded new-graph cohort from an independently audited cross CP run.

The first64 are the best refined edge upper scores; the next64 alternate
between root-group/cycle-size strata. Scores select work and prove nothing.
"""
import argparse
from collections import Counter, defaultdict, deque
from hashlib import sha256, file_digest
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITOR_SHA = '3a3e0c93d540982248254d87a3de753d8171be0081b6a7c82a4a7b89187721c8'


def path(p):
    return (ROOT/str(p).replace('\\', '/')).resolve()


def key(p):
    return path(p).relative_to(ROOT).as_posix()


def digest(p):
    with path(p).open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def signature(edges):
    require(type(edges) is list and len(edges) == 168 and all(type(e) is list and len(e) == 2 and
            all(type(x) is int for x in e) and 0 <= e[0] < e[1] < 84 for e in edges), 'Bad graph edges')
    sig = tuple(sorted(map(tuple, edges)))
    require(len(set(sig)) == 168, 'Repeated edge')
    return sig


def edge_hash(sig):
    return sha256(json.dumps(sig, separators=(',', ':')).encode('ascii')).hexdigest()


def choose(scores, moves, excluded):
    ordered = sorted((i for i in scores if i not in excluded), key=lambda i: (scores[i], i))
    require(len(ordered) >= 128, 'Insufficient new refined candidates')
    selected = ordered[:64]
    roles = {i: ['global_refined_upper'] for i in selected}
    buckets = defaultdict(deque)
    for i in ordered[64:]:
        buckets[moves[i]['root_group'], moves[i]['cycle_size']].append(i)
    while len(selected) < 128:
        changed = False
        for bucket in sorted(buckets):
            if buckets[bucket]:
                i = buckets[bucket].popleft()
                selected.append(i)
                roles[i] = ['round_robin_root_group_cycle_size']
                changed = True
                if len(selected) == 128:
                    break
        require(changed, 'Round-robin selection exhausted')
    return selected, roles, ordered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    parser.add_argument('--recovery', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    require(not path(args.out).exists(), 'Fresh request required')
    bindings = {}
    def bind(p, expected=None):
        name = key(p)
        if name not in bindings:
            bindings[name] = digest(p)
        require(expected is None or bindings[name] == expected, 'Changed input '+name)
        return bindings[name]
    def read(p):
        bind(p)
        return json.loads(path(p).read_bytes())
    run, recovery = path(args.run), path(args.recovery)
    audit = read(recovery/'audit.json')
    require(audit['status'] == 'INDEPENDENT_CP_CROSS_REPAIRED_LP_AUDIT_PASS' and
            audit['audited_producer_version'] == 'cross1' and audit['independent_LP_audit_tolerance'] == 1e-7,
            'Independently recovered cross audit required')
    for p, h in audit['inputs_sha256'].items():
        bind(p, h)
    require(audit['inputs_sha256'].get('acceleration/audit_cp_cross_recovery.py') == AUDITOR_SHA,
            'Unexpected recovery auditor')
    view = read(recovery/'summary.json')
    require(key(audit['effective_summary_path']) == key(recovery/'summary.json') and
            audit['effective_summary_sha256'] == bind(recovery/'summary.json'), 'Unbound effective summary')
    original = read(run/'summary.json')
    require(key(audit['original_summary_path']) == key(run/'summary.json') and
            audit['original_summary_sha256'] == bind(run/'summary.json') and
            original['status'] == 'BOUNDED_CP_MATCHING_SEARCH_FINISHED', 'Unbound original search')
    require([r['proposal_index'] for r in original['records']] == [r['proposal_index'] for r in view['records']] and
            len(original['records']) == 64, 'CP inventory differs')
    manifest = read(run/'manifest.json')
    family_path, family_audit_path = original['paths']['native'], original['paths']['family_audit']
    family, family_audit = read(family_path), read(family_audit_path)
    require(family['status'] == 'COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION' and
            family['selector'] == 'cross_3_4' and family_audit['status'] == 'INDEPENDENT_COMPLETE_CROSS_ATOMIC_CYCLE_EXTRACTION_PASS',
            'Wrong family')
    require(audit['family_association']['native_sha256'] == bind(family_path) and
            family_audit['inputs_sha256'].get(key(family_path)) == bind(family_path), 'Family byte association differs')
    options, moves = family['overlap_candidates'], family['moves']
    require(len(options) == len(moves) == family['legal_count'] == family_audit['legal_count'], 'Family inventory differs')
    sigs = [signature(edges) for edges in options]
    require(len(set(sigs)) == len(sigs), 'Repeated family graph')
    excluded_signatures = {signature(read(family['candidate_path'])['overlap_edges_outer_zero_based'])}
    for row in manifest['previous_candidates']:
        bind(row['candidate_path'], row['candidate_sha256'])
        sig = signature(read(row['candidate_path'])['overlap_edges_outer_zero_based'])
        require(edge_hash(sig) == row['overlap_edges_sha256'], 'Previous graph identity differs')
        excluded_signatures.add(sig)
    for row in original['records']:
        bind(row['candidate_path'], row['candidate_sha256'])
        sig = signature(read(row['candidate_path'])['overlap_edges_outer_zero_based'])
        require(sig == sigs[row['proposal_index']], 'Current CP graph association differs')
        excluded_signatures.add(sig)
    stage = read(run/'refined_stage.json')
    gpu = read(stage['gpu_output_path'])
    bind(stage['gpu_output_path'], stage['gpu_output_sha256'])
    require(audit['inputs_sha256'].get(key(run/'refined_stage.json')) == bind(run/'refined_stage.json') and
            audit['inputs_sha256'].get(key(stage['gpu_output_path'])) == stage['gpu_output_sha256'], 'Unbound refined stage')
    indices = stage['proposal_indices']
    require(stage['stage'] == 'refined' and stage['steps'] == 2000 and indices[0] is None and
            len(indices) == len(gpu['results']) == 2049 and len(set(indices[1:])) == 2048,
            'Wrong refined stage shape')
    scores = {}
    for j, (index, result) in enumerate(zip(indices, gpu['results'])):
        require(result['candidate_index'] == j and len(result['checkpoints']) == 1, 'Refined GPU order differs')
        checkpoint = result['checkpoints'][0]
        values = [result['initial']['primal_upper'], checkpoint['last']['primal_upper'], checkpoint['average']['primal_upper']]
        require(checkpoint['iterations'] == 2000 and all(type(x) in (int, float) and math.isfinite(x) for x in values) and
                math.isfinite(checkpoint['best_upper']) and abs(checkpoint['best_upper']-min(values)) < 1e-10,
                'Invalid refined upper score')
        if index is not None:
            require(type(index) is int and 0 <= index < len(options), 'Invalid family index')
            scores[index] = min(values)
    excluded = {i for i, sig in enumerate(sigs) if sig in excluded_signatures}
    selected, roles, eligible = choose(scores, moves, excluded)
    records = [dict(proposal_index=i, roles=roles[i], refined_upper=scores[i], root_group=moves[i]['root_group'],
                    cycle_size=moves[i]['cycle_size'], original_native_index=family['original_native_indices'][i],
                    overlap_edges_sha256=edge_hash(sigs[i])) for i in selected]
    bind(__file__)
    output = dict(status='EXPLICIT_FRESH_STAR_COHORT_REQUEST', family_path=key(family_path), family_sha256=bind(family_path),
        family_audit_path=key(family_audit_path), family_audit_sha256=bind(family_audit_path), indices=selected,
        selection_policy=dict(name='64_GLOBAL_REFINED_UPPER_THEN64_ROUND_ROBIN_ROOT_SIZE', global_count=64,
                              stratified_count=64, ordering='score,index; strata sorted(root_group,cycle_size)'),
        records=records, inputs_sha256=bindings, original_search_path=key(run/'summary.json'),
        recovery_audit_path=key(recovery/'audit.json'), refined_stage_path=key(run/'refined_stage.json'),
        previous_or_CP_graphs_excluded=True, eligible_refined_count=len(eligible), excluded_family_indices=sorted(excluded),
        count_by_root_group={str(k): v for k, v in sorted(Counter(moves[i]['root_group'] for i in selected).items())},
        LP_or_domain_or_GPU_runs=0, graph_exclusions_claimed=0, exhaustive_family_evaluation_claimed=False,
        scope='A new128-graph sampled cohort, outside prior CP graphs. Old edge upper scores choose numerical ranking work only.')
    with path(args.out).open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(output, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(status=output['status'], count=len(selected), eligible=len(eligible), sha256=digest(args.out))))


if __name__ == '__main__':
    main()
