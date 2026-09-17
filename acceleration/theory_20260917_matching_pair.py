"""Bounded reciprocity and exact pair AC on sound matching-filtered subdomains.

Preserves historical original IDs and existing native output unchanged.
All new propagation results require independent review.
"""
import argparse
from collections import deque
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT/'acceleration/results/20260916_star_guided_round2/search/probes/selection_03_index_18481_candidate.json'
DOMAINS = ROOT/'acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481/local/stars.json'
FILTER = ROOT/'acceleration/results/20260917_theory/matching_baseline18481/summary.json'
AUDIT = ROOT/'acceleration/results/20260917_independent_review/triangle_matching/summary.json'
NATIVE = ROOT/'acceleration/build/pair_domains.exe'
SOURCE = ROOT/'acceleration/pair_domains.rs'


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def key(p):
    return p.relative_to(ROOT).as_posix()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(p, value):
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def reciprocity(masks, original_ids, unordered_pairs, seconds):
    started = time.perf_counter()
    current = [set(row) for row in original_ids]
    neighbors = [[] for _ in current]
    for u, v in unordered_pairs:
        neighbors[u].append(v)
        neighbors[v].append(u)
    queue = deque((u, v) for a, b in unordered_pairs for u, v in ((a, b), (b, a)))
    queued = set(queue)
    events = []
    visits = 0
    status = 'RECIPROCITY_ARC_CONSISTENT_NONEMPTY'
    empty = None
    while queue:
        if time.perf_counter()-started >= seconds:
            status = 'INCOMPLETE'
            break
        u, v = queue.popleft()
        queued.remove((u, v))
        visits += 1
        supported_bits = {(masks[v][j] >> u) & 1 for j in current[v]}
        removed = sorted(i for i in current[u] if ((masks[u][i] >> v) & 1) not in supported_bits)
        if not removed:
            continue
        before = len(current[u])
        current[u].difference_update(removed)
        events.append(dict(target_vertex=u, support_vertex=v,
            removed_original_domain_ids=removed, before_count=before, after_count=len(current[u]),
            support_edge_values=sorted(supported_bits)))
        if not current[u]:
            status, empty = 'EMPTY_DOMAIN', u
            break
        for w in neighbors[u]:
            if (w, u) not in queued:
                queue.append((w, u))
                queued.add((w, u))
    return dict(status=status, events=events,
        surviving_original_domain_ids=[sorted(row) for row in current], empty_vertex=empty,
        queue_visits=visits, pending_arcs=list(queue), elapsed_seconds=time.perf_counter()-started,
        original_complete_domains=False, input_scope='SOUND_MATCHING_FILTERED_SUBDOMAINS',
        cap_seconds=seconds, independently_verified=False)


def controls():
    keep = reciprocity([[2], [1]], [[0], [0]], [(0, 1)], 1)
    assert keep['status'] == 'RECIPROCITY_ARC_CONSISTENT_NONEMPTY' and not keep['events']
    remove = reciprocity([[0, 2], [0]], [[0, 1], [0]], [(0, 1)], 1)
    assert remove['surviving_original_domain_ids'] == [[0], [0]]
    bad = reciprocity([[2], [0]], [[0], [0]], [(0, 1)], 1)
    assert bad['status'] == 'EMPTY_DOMAIN'
    capped = reciprocity([[2], [1]], [[0], [0]], [(0, 1)], 0)
    assert capped['status'] == 'INCOMPLETE' and not capped['events']
    return dict(status='PRODUCER_RECIPROCITY_CONTROLS_PASS', independently_verified=False,
                reciprocal_singletons=keep, forced_removal=remove,
                corrupted_nonreciprocal_singletons=bad, zero_time_cap=capped)


def native_run(out, name, candidate_path, domain_path, seconds, pair_cap):
    result_path = out/(name+'.json')
    command = [str(NATIVE), str(candidate_path), str(domain_path), str(result_path), str(seconds), str(pair_cap)]
    begun = stamp()
    with (out/(name+'.log')).open('x', encoding='utf-8') as log:
        try:
            run = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                 timeout=seconds+30, check=False)
            code, timeout = run.returncode, False
        except subprocess.TimeoutExpired:
            code, timeout = None, True
    receipt = dict(command=command, cwd=str(ROOT), started_at=begun, finished_at=stamp(),
        returncode=code, subprocess_timeout=timeout, result_exists=result_path.exists(),
        result_sha256=digest(result_path) if result_path.exists() else None,
        result_missing_reason=None if result_path.exists() else 'Native command returned no result artifact',
        log_sha256=digest(out/(name+'.log')))
    save(out/(name+'_receipt.json'), receipt)
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--seconds', type=float, default=60)
    p.add_argument('--pair-cap', type=int, default=500000000)
    args = p.parse_args()
    assert 0 < args.seconds <= 3600 and 0 < args.pair_cap <= 1000000000
    args.out.mkdir(parents=True, exist_ok=False)
    audit, filtered, data, candidate = (json.loads(path.read_bytes()) for path in (AUDIT, FILTER, DOMAINS, CANDIDATE))
    assert audit['status'] == 'INDEPENDENT_EXACT_TRIANGLE_MATCHING_FILTER_PASS'
    assert audit['claim_binding']['id'] == 'C-STAR-TRIANGLE-FILTER-18481' and audit['claim_binding']['revision'] == 1
    for path in (FILTER, DOMAINS, CANDIDATE):
        assert audit['inputs_sha256'][key(path)] == digest(path)
    assert digest(NATIVE) == '7031a0a9d32075fb8f32777149ff5f54466c930726a2777709aa5278779eb976'
    masks = [[int(mask, 16) for mask in row['domain_masks_hex']] for row in data['domains']]
    selected = [row['survivor_domain_ids'] for row in filtered['vertices']]
    assert len(masks) == len(selected) == 84
    assert sum(map(len, selected)) == 19494
    assert all(ids == sorted(set(ids)) and ids and all(0 <= i < len(masks[u]) for i in ids)
               for u, ids in enumerate(selected))
    bindings = {key(path):digest(path) for path in (CANDIDATE, DOMAINS, FILTER, AUDIT, NATIVE, SOURCE,
                                                  Path(__file__), ROOT/'uv.lock', ROOT/'pyproject.toml')}
    manifest = dict(schema_version=1, created_at=stamp(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'],cwd=ROOT,text=True).strip(),
        command=['uv','run','--locked','--offline','--cache-dir','.uv-cache-20260917','python','-B']+sys.argv,
        environment={'UV_PROJECT_ENVIRONMENT':'build/research-venv'}, cwd=str(ROOT), python=sys.version,
        platform=platform.platform(), source_bytes_uncommitted_and_explicitly_hashed=True,
        inputs_sha256=bindings, prerequisite={'id':'C-STAR-TRIANGLE-FILTER-18481','revision':1,
                                            'relation':'uses_result','audit_sha256':digest(AUDIT)},
        question='Does exact reciprocity and full completed-neighborhood pair propagation empty a matching-filtered baseline18481 domain?',
        selection_rule='All19494 matching survivors at all84 vertices; no historical pair-AC survivors used as initial restrictions.',
        domain_scope='SOUND_MATCHING_FILTERED_SUBDOMAINS', original_complete_domains=False,
        initial_original_domain_ids=selected, caps={'reciprocity_seconds':args.seconds,
            'pair_seconds':args.seconds,'pair_comparisons':args.pair_cap,'subprocess_extra_seconds':30},
        success='Empty domain with complete independently checked prerequisite and deletion trace excludes this fixed K only.',
        secondary_outcome='Nonempty final closure measures only the exact resulting local relaxation and further deletions.',
        numerical_acceptance='Exact integer/set conditions; no floating-point mathematical threshold',
        rule='Edge decisions reciprocate, and full neighborhoods have exactly2-adjacency common neighbors for each outer pair.',
        random_seed=None, random_seed_reason='Deterministic propagation',
        limitations='Already excluded baselineK; no unrestricted coverage, no new original complete enumeration, no global joint-star selection.',
        restart='Frozen candidate.txt and domains.txt plus packed_to_original_ids.json permit a fresh capped native run into a NEW filename. Partial survivor/deletion records are checkpoints; independent replay required before using prior deletions as a premise.')
    save(args.out/'manifest.json', manifest)
    save(args.out/'reciprocity_controls.json', controls())
    supports = [set(pair) for pair in combinations(range(7), 2) for _ in range(4)]
    variable_pairs = [(u,v) for u,v in combinations(range(84),2) if not supports[u]&supports[v]]
    assert len(variable_pairs) == 1680
    reciprocal = reciprocity(masks, selected, variable_pairs, args.seconds)
    save(args.out/'reciprocity.json', reciprocal)
    if reciprocal['status'] != 'RECIPROCITY_ARC_CONSISTENT_NONEMPTY':
        save(args.out/'summary.json', dict(status='CANDIDATE_RECIPROCITY_'+reciprocal['status'],
            original_complete_domains=False, initial_choices=19494,
            final_choices=sum(map(len, reciprocal['surviving_original_domain_ids'])),
            empty_vertex=reciprocal['empty_vertex'], pair_phase='NOT_STARTED', independently_verified=False,
            inputs_sha256=bindings, outputs_sha256={'reciprocity.json':digest(args.out/'reciprocity.json')}))
        return
    ids = reciprocal['surviving_original_domain_ids']
    save(args.out/'packed_to_original_ids.json', dict(domain_scope='SOUND_MATCHING_AND_RECIPROCITY_FILTERED_SUBDOMAINS',
        original_complete_domains=False, packed_to_original_domain_ids=ids,
        original_domains_sha256=digest(DOMAINS), reciprocity_sha256=digest(args.out/'reciprocity.json')))
    candidate_path, domain_path = args.out/'candidate.txt', args.out/'domains.txt'
    with candidate_path.open('x', encoding='ascii', newline='\n') as f:
        f.write('C99OVERLAPS1 1\n'+' '.join(str(v) for e in sorted(candidate['overlap_edges_outer_zero_based']) for v in e)+'\n')
    with domain_path.open('x', encoding='ascii', newline='\n') as f:
        f.write('C99DOMAINS1 84\n')
        for u,row in enumerate(ids):
            f.write(str(len(row))+' '+' '.join(hex(masks[u][i]) for i in row)+'\n')
    cap = native_run(args.out,'control_pair_cap',candidate_path,domain_path,args.seconds,1)
    assert cap['returncode'] == 0
    cap_data = json.loads((args.out/'control_pair_cap.json').read_bytes())
    assert cap_data['propagation_status'] == 'INCOMPLETE' and cap_data['cap_reason'] == 'DOMAIN_PAIR_CAP'
    corrupt_path = args.out/'control_corrupted_domains.txt'
    parts = domain_path.read_text().split()
    parts[3] = '0x0'
    with corrupt_path.open('x', encoding='ascii') as f:
        f.write(' '.join(parts)+'\n')
    corrupt = native_run(args.out,'control_corrupt',candidate_path,corrupt_path,args.seconds,args.pair_cap)
    assert corrupt['returncode'] != 0 and not corrupt['result_exists']
    save(args.out/'native_controls.json', dict(status='PRODUCER_NATIVE_CONTROLS_PASS',
        cap_returns_incomplete=True, corrupted_zero_star_rejected=True, independently_verified=False))
    receipt = native_run(args.out,'native',candidate_path,domain_path,args.seconds,args.pair_cap)
    if receipt['returncode'] != 0:
        save(args.out/'summary.json', dict(status='INCOMPLETE_NATIVE_EXECUTION', native_receipt=receipt,
            initial_choices=19494, after_reciprocity_choices=sum(map(len,ids)), independently_verified=False))
        return
    native = json.loads((args.out/'native.json').read_bytes())
    translated = dict(status='CANDIDATE_EXACT_MATCHING_FILTERED_PAIR_'+native['propagation_status'],
        domain_scope='SOUND_MATCHING_AND_RECIPROCITY_FILTERED_SUBDOMAINS', original_complete_domains=False,
        propagation_status=native['propagation_status'], cap_reason=native['cap_reason'], empty_vertex=native['empty_vertex'],
        initial_original_domain_ids=ids, events=[dict(target_vertex=e['target_vertex'],support_vertex=e['support_vertex'],
            removed_original_domain_ids=[ids[e['target_vertex']][i] for i in e['removed_domain_ids']],
            before_count=e['before_count'],after_count=e['after_count']) for e in native['events']],
        surviving_original_domain_ids=[[ids[u][i] for i in row] for u,row in enumerate(native['surviving_domain_ids'])],
        native_sha256=digest(args.out/'native.json'), mapping_sha256=digest(args.out/'packed_to_original_ids.json'),
        independently_verified=False)
    save(args.out/'translated_pairs.json', translated)
    assert all(digest(ROOT/path) == h for path,h in bindings.items())
    summary = dict(status='CANDIDATE_MATCHING_FILTERED_PROPAGATION_'+native['propagation_status'],
        created_at=stamp(), source_commit=manifest['source_commit'],
        original_complete_domains=False, initial_choices=19494,
        after_reciprocity_choices=sum(map(len,ids)),
        final_choices=sum(map(len,translated['surviving_original_domain_ids'])),
        reciprocity_events=len(reciprocal['events']), pair_events=len(native['events']),
        pair_choice_comparisons=native['domain_pairs_evaluated'], pair_relations=native['vertex_pair_relations_built'],
        empty_vertex=native['empty_vertex'], cap_reason=native['cap_reason'],
        pair_seconds=native['elapsed_seconds'], reciprocity_seconds=reciprocal['elapsed_seconds'],
        independently_verified=False, target_resolution='UNKNOWN', overall_search_coverage='UNKNOWN; no validated denominator',
        inputs_sha256=bindings, outputs_sha256={p.name:digest(p) for p in args.out.iterdir() if p.is_file()},
        limitations='Nonempty closure is not a graph or global CSP witness. Empty domain would only exclude the fixed baselineK, pending independent replay.')
    save(args.out/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','outputs_sha256')}))


if __name__ == '__main__':
    main()
