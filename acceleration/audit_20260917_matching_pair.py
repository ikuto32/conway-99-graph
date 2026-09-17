"""Independent original-ID matching-filter / pair-propagation proof checker."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def path(p):
    p = Path(str(p).replace('\\', '/'))
    return p if p.is_absolute() else ROOT/p


def key(p):
    return path(p).resolve().relative_to(ROOT).as_posix()


def digest(p):
    return sha256(path(p).read_bytes()).hexdigest()


def construct(candidate, domains):
    labels = [(2*a+s, 2*b+t) for a in range(7) for b in range(a+1, 7)
              for s in range(2) for t in range(2)]
    neighbors = [set() for _ in range(99)]
    def add(u, v):
        require(u != v and v not in neighbors[u], 'duplicate known edge')
        neighbors[u].add(v); neighbors[v].add(u)
    for u in range(1, 15): add(0, u)
    for u in range(1, 15, 2): add(u, u+1)
    for u, (a, b) in enumerate(labels, 15):
        add(u, a+1); add(u, b+1)
    for a, b in candidate['overlap_edges_outer_zero_based']: add(a+15, b+15)
    require(list(map(len, neighbors)) == [14]*15+[6]*84, 'known degrees')
    unknown = {(u, v) for u, v in combinations(range(84), 2)
               if not {s//2 for s in labels[u]} & {s//2 for s in labels[v]}}
    full = []
    for u, table in enumerate(domains['domains']):
        require(table['outer_vertex'] == u, 'original vertex order')
        local = {}
        for i, mask in enumerate(table['domain_masks_hex']):
            chosen = {v+15 for v in range(84) if int(mask, 16) & (1 << v)}
            require(len(chosen) == 8 and all(tuple(sorted((u, v-15))) in unknown for v in chosen), 'star unknown scope')
            local[i] = frozenset(neighbors[u+15] | chosen)
            require(len(local[i]) == 14, 'completed neighborhood degree')
        full.append(local)
    return full, unknown


def compatible(u, nu, v, nv):
    a = v+15 in nu
    b = u+15 in nv
    return a == b and len(nu.intersection(nv)) == (1 if a else 2)


def replay_pair(full, initial, events, final, empty_vertex=None, check_closure=True):
    active = [set(ids) for ids in initial]
    checks = 0
    require(all(active) and all(set(ids) <= set(full[u]) for u, ids in enumerate(active)), 'initial original-ID scope')
    for step, event in enumerate(events):
        require(all(active), 'events continued after empty domain')
        u, v = event['target_vertex'], event['support_vertex']
        require(type(u) is int and type(v) is int and 0 <= u < len(full) and 0 <= v < len(full) and u != v, 'event vertices')
        require(event['before_count'] == len(active[u]), 'before count')
        removed = []
        for i in sorted(active[u]):
            for j in sorted(active[v]):
                checks += 1
                if compatible(u, full[u][i], v, full[v][j]):
                    break
            else:
                removed.append(i)
        require(removed and removed == event['removed_domain_ids'], 'pair deletion not exactly unsupported original IDs')
        active[u].difference_update(removed)
        require(event['after_count'] == len(active[u]), 'after count')
    require([sorted(ids) for ids in active] == final, 'final original-ID domains')
    if empty_vertex is not None:
        require(type(empty_vertex) is int and 0 <= empty_vertex < len(full) and not active[empty_vertex], 'claimed empty vertex')
    else:
        require(all(active), 'unexpected empty domain')
        if check_closure:
            for u in range(len(full)):
                for v in range(len(full)):
                    if u == v: continue
                    for i in active[u]:
                        for j in active[v]:
                            checks += 1
                            if compatible(u, full[u][i], v, full[v][j]): break
                        else:
                            raise ValueError('final relation not arc-consistent')
    return dict(events_checked=len(events), pair_compatibility_checks=checks,
                final_choices=sum(map(len, active)), empty_vertices=[u for u, ids in enumerate(active) if not ids],
                final_all_directed_pair_closure_checked=check_closure and empty_vertex is None)


def replay_reciprocal(full, unknown, initial, events, final, empty_vertex=None):
    active = [set(ids) for ids in initial]
    for event in events:
        require(all(active), 'reciprocity continued after empty domain')
        u, v, value = event['target_vertex'], event['support_vertex'], event['required_edge_value']
        require(tuple(sorted((u, v))) in unknown and type(value) is int and value in (0, 1), 'reciprocity scope/value')
        require({int(u+15 in full[v][j]) for j in active[v]} == {value}, 'support does not force value')
        removed = sorted(i for i in active[u] if int(v+15 in full[u][i]) != value)
        require(removed and removed == event['removed_domain_ids'] and event['before_count'] == len(active[u]), 'bad reciprocity deletion')
        active[u].difference_update(removed)
        require(event['after_count'] == len(active[u]), 'reciprocity after count')
    require([sorted(ids) for ids in active] == final, 'reciprocity final original IDs')
    if empty_vertex is not None:
        require(not active[empty_vertex], 'reciprocity claimed empty')
    else:
        require(all(active), 'reciprocity empty domain')
        for u, v in unknown:
            require({v+15 in full[u][i] for i in active[u]} == {u+15 in full[v][j] for j in active[v]}, 'reciprocity not closed')
    return dict(events_checked=len(events), final_choices=sum(map(len, active)))


def controls():
    # Intentionally noncontiguous IDs exercise original-ID preservation.
    full = [{0: frozenset((16, 2)), 5: frozenset((16, 1))}, {3: frozenset((15, 1))}]
    initial = [[0, 5], [3]]
    good = dict(target_vertex=0, support_vertex=1, removed_domain_ids=[0], before_count=2, after_count=1)
    result = replay_pair(full, initial, [good], [[5], [3]])
    records = [dict(name='noncontiguous_ID_sound_deletion_and_closed_positive', outcome='PASS', **result)]
    for name in ('delete_supported_choice', 'wrong_before_count', 'wrong_after_count', 'wrong_final_ID', 'omit_needed_deletion'):
        event = deepcopy(good); final = [[5], [3]]; events = [event]
        if name == 'delete_supported_choice': event['removed_domain_ids'] = [5]
        if name == 'wrong_before_count': event['before_count'] = 3
        if name == 'wrong_after_count': event['after_count'] = 0
        if name == 'wrong_final_ID': final = [[0], [3]]
        if name == 'omit_needed_deletion': events = []; final = initial
        try:
            replay_pair(full, initial, events, final)
        except ValueError as e:
            records.append(dict(name=name, outcome='REJECT', reason=str(e)))
        else:
            raise ValueError('corrupt control accepted: '+name)
    empty_full = [{0: frozenset((16, 2))}, {3: frozenset((15, 1))}]
    empty_event = dict(target_vertex=0, support_vertex=1, removed_domain_ids=[0], before_count=1, after_count=0)
    records.append(dict(name='exhausted_domain', outcome='PASS', **replay_pair(empty_full, [[0], [3]], [empty_event], [[], [3]], 0)))
    reciprocal_full = [{0: frozenset((1,)), 5: frozenset((16, 1))}, {3: frozenset((1,))}]
    reciprocal_event = dict(target_vertex=0, support_vertex=1, required_edge_value=0,
                            removed_domain_ids=[5], before_count=2, after_count=1)
    records.append(dict(name='reciprocity_noncontiguous_ID_deletion', outcome='PASS',
                        **replay_reciprocal(reciprocal_full, {(0, 1)}, initial, [reciprocal_event], [[0], [3]])))
    changed = deepcopy(reciprocal_event); changed['required_edge_value'] = 1
    try:
        replay_reciprocal(reciprocal_full, {(0, 1)}, initial, [changed], [[0], [3]])
    except ValueError as e:
        records.append(dict(name='incorrect_forced_reciprocity_value', outcome='REJECT', reason=str(e)))
    else:
        raise ValueError('invalid reciprocity control accepted')
    return records


def translated_events(raw):
    return [dict(target_vertex=e['target_vertex'], support_vertex=e['support_vertex'],
                 removed_domain_ids=e['removed_original_domain_ids'], before_count=e['before_count'],
                 after_count=e['after_count']) for e in raw]


def verify_translation(mapping, native, translated):
    require(translated['initial_original_domain_ids'] == mapping, 'translated initial IDs')
    require(len(native['events']) == len(translated['events']), 'event translation count')
    for a, b in zip(native['events'], translated['events']):
        require(all(a[k] == b[k] for k in ('target_vertex', 'support_vertex', 'before_count', 'after_count')), 'translated event metadata')
        require(all(type(i) is int and 0 <= i < len(mapping[a['target_vertex']]) for i in a['removed_domain_ids']), 'packed removal index')
        require([mapping[a['target_vertex']][i] for i in a['removed_domain_ids']] == b['removed_original_domain_ids'], 'packed/original event translation')
    require(len(native['surviving_domain_ids']) == len(mapping), 'packed final vertex count')
    require([[mapping[u][i] for i in ids] for u, ids in enumerate(native['surviving_domain_ids'])] ==
            translated['surviving_original_domain_ids'], 'packed/original final translation')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    require(not args.out.exists(), 'preserve prior verification')
    started = time.perf_counter()
    bindings = {key(__file__): digest(__file__), 'uv.lock': digest('uv.lock')}
    def read(p):
        bindings[key(p)] = digest(p)
        return json.loads(path(p).read_bytes())
    def verify_bindings(doc, field='inputs_sha256', base=ROOT):
        for f, h in doc.get(field, {}).items():
            file = base/f
            require(digest(file) == h, 'bound artifact changed: '+str(file)); bindings[key(file)] = h
    summary = read(args.input/'summary.json'); manifest = read(args.input/'manifest.json')
    verify_bindings(summary); verify_bindings(manifest)
    verify_bindings(summary, 'outputs_sha256', args.input)
    require(summary['status'] == 'CANDIDATE_MATCHING_FILTERED_PROPAGATION_ARC_CONSISTENT_NONEMPTY' and
            summary['cap_reason'] is None, 'this report checks complete nonempty propagation only')
    candidate_path = 'acceleration/results/20260916_star_guided_round2/search/probes/selection_03_index_18481_candidate.json'
    domain_path = 'acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481/local/stars.json'
    candidate, domains = read(candidate_path), read(domain_path)
    matching_dir = Path('acceleration/results/20260917_independent_review/triangle_matching')
    matching = read(matching_dir/'summary.json')
    require(digest(matching_dir/'summary.json') == '5be4cd010e48af4a690f611794d39f119e331414b6a0e848689745f3c0daf34c', 'matching prerequisite pin')
    require(matching['status'] == 'INDEPENDENT_EXACT_TRIANGLE_MATCHING_FILTER_PASS' and
            matching['claim_binding']['id'] == 'C-STAR-TRIANGLE-FILTER-18481' and matching['claim_binding']['revision'] == 1, 'matching prerequisite')
    verify_bindings(matching); verify_bindings(matching, 'vertex_reports_sha256')
    require(matching['inputs_sha256'][candidate_path] == digest(candidate_path) and
            matching['inputs_sha256'][domain_path] == digest(domain_path), 'matching candidate/domain binding')
    reports = [read(matching_dir/f'vertex_{u:02d}.json') for u in range(84)]
    initial = []
    for u, row in enumerate(reports):
        ids, removed = row['survivor_domain_ids'], row['removed_domain_ids']
        require(row['outer_vertex'] == u and row['status'] == 'PASS' and ids == sorted(set(ids)) and
                removed == sorted(set(removed)) and not set(ids) & set(removed) and
                sorted(ids+removed) == list(range(len(domains['domains'][u]['domain_masks_hex']))), 'matching partition original IDs')
        initial.append(ids)
    require(manifest['initial_original_domain_ids'] == initial and sum(map(len, initial)) == 19494, 'initial matching choice universe')
    require(manifest['domain_scope'] == 'SOUND_MATCHING_FILTERED_SUBDOMAINS' and manifest['original_complete_domains'] is False, 'initial scope')
    full, unknown = construct(candidate, domains)
    control_records = controls()
    reciprocal = read(args.input/'reciprocity.json')
    require(reciprocal['status'] == 'RECIPROCITY_ARC_CONSISTENT_NONEMPTY' and reciprocal['original_complete_domains'] is False, 'reciprocal completion/scope')
    rev = translated_events(reciprocal['events'])
    for old, new in zip(reciprocal['events'], rev):
        require(len(old['support_edge_values']) == 1, 'forced reciprocal value must be singleton')
        new['required_edge_value'] = old['support_edge_values'][0]
    rec_checked = replay_reciprocal(full, unknown, initial, rev, reciprocal['surviving_original_domain_ids'])
    print(json.dumps(dict(event='RECIPROCITY_REPLAY_PASS', **rec_checked)), flush=True)
    mapping_doc = read(args.input/'packed_to_original_ids.json')
    mapping = mapping_doc['packed_to_original_domain_ids']
    require(mapping_doc['original_complete_domains'] is False and mapping == reciprocal['surviving_original_domain_ids'] and
            mapping_doc['original_domains_sha256'] == digest(domain_path) and
            mapping_doc['reciprocity_sha256'] == digest(args.input/'reciprocity.json'), 'packed mapping scope/binding')
    # Parse the exact native input independently: header, counts, masks, no extra tokens.
    tokens = path(args.input/'domains.txt').read_text().split()
    require(tokens[:2] == ['C99DOMAINS1', '84'], 'native domain header')
    pos = 2
    for u, ids in enumerate(mapping):
        count = int(tokens[pos]); pos += 1
        require(count == len(ids), 'packed domain count')
        masks = [int(v, 16) for v in tokens[pos:pos+count]]; pos += count
        require(masks == [int(domains['domains'][u]['domain_masks_hex'][i], 16) for i in ids], 'packed domain masks/order')
    require(pos == len(tokens), 'extra packed input tokens')
    candidate_tokens = path(args.input/'candidate.txt').read_text().split()
    require(candidate_tokens[:2] == ['C99OVERLAPS1', '1'] and
            list(map(int, candidate_tokens[2:])) == [v for e in sorted(candidate['overlap_edges_outer_zero_based']) for v in e], 'native candidate bytes')
    native, translated = read(args.input/'native.json'), read(args.input/'translated_pairs.json')
    require(native['propagation_status'] == translated['propagation_status'] == 'ARC_CONSISTENT_NONEMPTY' and
            native['empty_vertex'] is None and translated['empty_vertex'] is None and
            native['cap_reason'] is None and translated['cap_reason'] is None and
            translated['original_complete_domains'] is False and
            translated['domain_scope'] == 'SOUND_MATCHING_AND_RECIPROCITY_FILTERED_SUBDOMAINS', 'native/translated scope/status')
    require(translated['native_sha256'] == digest(args.input/'native.json') and
            translated['mapping_sha256'] == digest(args.input/'packed_to_original_ids.json'), 'translation identity')
    verify_translation(mapping, native, translated)
    changed = deepcopy(translated); changed['events'][0]['removed_original_domain_ids'][0] += 1
    try:
        verify_translation(mapping, native, changed)
    except ValueError as e:
        control_records.append(dict(name='corrupted_raw_original_ID_translation', outcome='REJECT', reason=str(e)))
    else:
        raise ValueError('corrupt raw translated ID accepted')
    pair_checked = replay_pair(full, mapping, translated_events(translated['events']), translated['surviving_original_domain_ids'])
    print(json.dumps(dict(event='EXACT_PAIR_REPLAY_AND_CLOSURE_PASS', **pair_checked)), flush=True)
    require(summary['initial_choices'] == sum(map(len, initial)) and summary['after_reciprocity_choices'] == rec_checked['final_choices'] and
            summary['final_choices'] == pair_checked['final_choices'] and summary['pair_events'] == pair_checked['events_checked'], 'producer aggregate counts')
    # Independently inspect the old comparison against already audited partitions.
    comparison_path = 'acceleration/results/20260917_theory/matching_baseline18481/comparison.json'
    comparison = read(comparison_path)
    old_pair = read(comparison['pair_path'])
    old_audit = read('acceleration/results/20260917_independent_review/baseline_fresh_domain_replay.json')
    verify_bindings(old_audit)
    require(old_audit['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and
            {key(f): h for f, h in old_audit['inputs_sha256'].items()}[key(comparison['pair_path'])] == digest(comparison['pair_path']), 'old pair audit binding')
    old = old_pair['surviving_domain_ids']
    require(len(old) == 84 and all(ids == sorted(set(ids)) and set(ids) <= set(full[u]) for u, ids in enumerate(old)), 'old pair universe')
    counts = dict(original_choices=sum(len(row) for row in full), existing_pair_ac_survivor_choices=sum(map(len, old)),
                  matching_rejected_choices_among_pair_ac_survivors=sum(len(set(a)-set(b)) for a, b in zip(old, initial)),
                  survive_both_without_further_propagation=sum(len(set(a)&set(b)) for a, b in zip(old, initial)),
                  matching_survivors_rejected_by_old_pair=sum(len(set(b)-set(a)) for a, b in zip(old, initial)))
    for k, value in counts.items():
        if k in comparison: require(comparison[k] == value, 'comparison count '+k)
    isolated = nonisolated = 0
    for u, report in enumerate(reports):
        rawpath = Path('acceleration/results/20260917_theory/matching_baseline18481')/f'vertex_{u:02d}.json'
        require(digest(rawpath) == report['raw_sha256'], 'audited matching record identity')
        raw = read(rawpath)
        for i in report['removed_domain_ids']:
            r = raw['results'][i]
            endpoints = {v for edge in r['allowed_edges_full99'] for v in edge}
            if set(r['unmatched_vertices_full99'])-endpoints: isolated += 1
            else: nonisolated += 1
    classification = dict(isolated_free_vertex=isolated, no_isolated_free_vertex=nonisolated)
    require(classification == comparison['rejected_matching_graph_classification'], 'comparison classification')
    witness = comparison['compact_strict_strengthening_witness']
    u, i = witness['outer_vertex'], witness['domain_id']
    require(i in old[u] and i in reports[u]['removed_domain_ids'], 'compact witness membership')
    raw = read(witness['raw_path'])['results'][i]
    require(digest(witness['raw_path']) == witness['raw_sha256'] and raw == witness['raw_record'] and
            raw['mask_hex'] == witness['mask_hex'] == domains['domains'][u]['domain_masks_hex'][i], 'compact witness raw binding')
    isolated_vertex = witness['isolated_unmatched_full99_vertex']
    require(isolated_vertex in raw['unmatched_vertices_full99'] and all(isolated_vertex not in edge for edge in raw['allowed_edges_full99']), 'compact isolated vertex')
    final = translated['surviving_original_domain_ids']
    require(all(set(ids) <= set(old[u]) & set(initial[u]) for u, ids in enumerate(final)), 'new closure not contained in old closure intersection')
    counts['new_pair_closure_choices'] = sum(map(len, final))
    counts['additional_removed_beyond_initial_filter_intersection'] = counts['survive_both_without_further_propagation']-counts['new_pair_closure_choices']
    require(all(digest(f) == h for f, h in bindings.items()), 'input changed during audit')
    report = dict(status='INDEPENDENT_MATCHING_FILTERED_PAIR_PROPAGATION_AND_COMPARISON_PASS',
        timestamp=datetime.now(timezone.utc).isoformat(), source_commit=manifest['source_commit'],
        source_additions_explicitly_hashed=True, command=[sys.executable]+sys.argv, working_directory=str(Path.cwd()),
        python=platform.python_version(), inputs_sha256=bindings, controls=control_records,
        prerequisite_claim=dict(id='C-STAR-TRIANGLE-FILTER-18481', revision=1, relation='uses_result',
                                matching_audit_sha256=digest(matching_dir/'summary.json')),
        claim_bindings=[dict(id='C-STAR-MATCHING-PAIR-18481', revision=1, recommendation='VERIFIED',
                            statement='From all19494 independently sound matching-filter survivors, reciprocity deletes0 and806 exact pair-deletion events remove4159 choices, yielding15335 original-ID choices across84 nonempty domains with all directed pair arcs consistent.',
                            scope='Only this fixed baseline assignment; original-complete-domain flag remains false; no global simultaneous witness or new fixed-K exclusion'),
                        dict(id='C-STAR-FILTER-COMPARISON-18481', revision=1, recommendation='VERIFIED',
                            statement='The audited old pair closure has22058 choices; matching rejects5469 of those, leaving16589 in the initial filter intersection. Of6756 matching rejections,3819 have an isolated free vertex and2937 do not. The exact original vertex0/domain5 witness survives old pair closure but fails matching by isolated full99 vertex88.',
                            scope='Only descriptive set operations on the two named audited baseline partitions; no target-wide coverage')],
        reciprocal_verification=rec_checked, pair_verification=pair_checked, comparison_counts=counts,
        rejected_graph_classification=classification, compact_witness_checked=dict(outer_vertex=u, domain_id=i, isolated_full99_vertex=isolated_vertex),
        shared_trusted_components=['Python standard library', 'raw graph/domain convention', 'hash-bound previously audited triangle filter and historical complete-domain/pair proof'],
        producer_imported=False, native_solver_executed=False, matching_enumeration_repeated=False,
        legacy_native_controls_scope='Preserved and hash-bound as artifacts; no new native behavior claim from this audit',
        elapsed_seconds=time.perf_counter()-started, target_resolution='UNKNOWN',
        overall_search_coverage='UNKNOWN; no validated denominator')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2); f.write('\n')
    print(json.dumps(dict(status=report['status'], final_choices=counts['new_pair_closure_choices'],
                         pair_events=pair_checked['events_checked'], seconds=report['elapsed_seconds'])))


if __name__ == '__main__':
    main()
