"""Independent conditional composition of seven-profile coverage and proof gates.

Preparation is not an exclusion. Final mode additionally authenticates every complete
proof and its separate independent replay. No producer imports or solver calls.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from itertools import permutations
from pathlib import Path
import argparse, gzip, hashlib, json, platform, subprocess, sys, time, traceback

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'
GATES = {
 'hadamard_seven_exception_census': ('0baaa10f59840dc2ca02676cf9d0f56a6dc0fd6f227edfeecabd0e94b3ff6c91', 'INDEPENDENT_HADAMARD_SEVEN_EXCEPTION_KERNEL_CENSUS_PASS'),
 'hadamard_seven_rank5_profiles': ('a5d5ac4d966077ceda4b19382bc4ddc5f85b7b812ab3bf01352260c74b2cb93d', 'INDEPENDENT_SEVEN_RANK5_INTEGER_MARGINAL_CENSUS_PASS'),
 'hadamard_seven_profile_local_domains': ('764918cdb953f10f378304db4448000a8eee9b8e721e750fc62870df98fdbe2d', 'INDEPENDENT_SEVEN_EXCEPTION_LOCAL_DOMAIN_FILTER_PASS'),
 'hadamard_seven_profile_arc': ('eeb0a947e6dde99c65578c6de323951f6c6654fdafeb31b22d053e117e84467d', 'INDEPENDENT_SEVEN_EXCEPTION_PROFILE_ARC_SCREEN_PASS'),
 'hadamard_seven_fibre_orbits': ('930f8d9a6e6b5986a61627cf21208c65691254c50fb2a71f6ddc0c4504b94e6f', 'INDEPENDENT_HADAMARD_SEVEN_EXCEPTION_FIBRE_NORMALIZATION_PASS'),
 'hadamard_seven_profile_cnf': ('3d000917a2c0e9fedd2cd5ca8df9a81502f3cb511df3b97a24b679e06c4955d1', 'INDEPENDENT_HADAMARD_SEVEN_PROFILE_ENCODING_PASS'),
 'hadamard_seven_profile_unsat': ('ff0ce1b606f0fd8c96ba4b4d892943b86abf09c9bb3c32ed3db02702a9e516a2', 'INDEPENDENT_FIXED_HADAMARD_SEVEN_PROFILE0001_UNSAT_PASS'),
 'hadamard_twohundredfifteen_profile_cnfs_v2': ('8b05dd0827fcebed9258566077720f890abea150dfdae7198c29bf97428f7b66', 'INDEPENDENT_HADAMARD_TWOHUNDREDFIFTEEN_PROFILE_ENCODING_PASS'),
 'hadamard_six_profile_union': ('6a7b34f7feaf7d9330ce07f4c615f4198e8cdc0c8ac22dd7fb5e673ba59311df', 'INDEPENDENT_FIXED_HADAMARD_SIX_PROFILE_UNION_PASS'),
}
RAW = B + 'hadamard20_support/six_prism.json'
RAW_HASH = 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'
UNIVERSE = B + 'hadamard_seven_profile_local_domains/profiles.jsonl.gz'
UNIVERSE_HASH = '88d5e572fe280a70b51e0dd2785378d73300e6873a7db788072bcbca8ef256ae'
SELECTION = B + 'hadamard_seven_remaining_selection/selection.json'
SELECTION_HASH = '9b949349900b586716ff15065350a8eedbbd87bac6f2fe78841ac940675f731e'
BATCH = B + 'hadamard_seven_remaining_cnfs/run02/summary.json'
BATCH_HASH = 'eabd989bd427c6fcfc57564d62b907d80630f1b5c7b7d56df17fa09f2df16119'
PRIOR_ID = 'rank5_07_profile_0001'
PROOF_STATUS = 'INDEPENDENT_FIXED_HADAMARD_TWOHUNDREDFIFTEEN_PROFILE_UNSAT_PASS'
PROOF_CLAIM = 'C-FIXED-HADAMARD-TWOHUNDREDFIFTEEN-SEVEN-EXCEPTION-PROFILE-EXCLUSIONS'
DOC = 'docs/AUDIT_20260930_SEVEN_PROFILE_UNION.md'
SPEC = 'acceleration/audit_20260930_hadamard_seven_profile_union_spec.md'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def key(path):
    path = Path(path)
    return (path if path.is_absolute() else ROOT / path).resolve().relative_to(ROOT).as_posix()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def save(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def literal_key(groups, delta):
    return tuple(groups), tuple(tuple(tuple(v) for v in a) for a in delta)


def image(delta, pullback):
    need(sorted(pullback) == [0, 1, 2], 'fibre bijection')
    return [[a[pullback[f]][:] for f in range(3)] for a in delta]


def cover(universe, excluded, orbits, representatives):
    need(len(universe) == len(set(universe)) == 1608, '1608 distinct profiles')
    need(len(excluded) == len(set(excluded)) == 312, '312 distinct AC exclusions')
    need(len(representatives) == len(set(representatives)) == 216,
         '216 distinct representative identities')
    need(set(representatives) == set(orbits), 'representative set exactly matches nonempty orbits')
    members = [x for r in representatives for x in orbits[r]]
    need(len(members) == len(set(members)) == 1296, '1296 disjoint orbit members')
    need(all(len(orbits[r]) == 6 and r in orbits[r] for r in representatives),
         'six-element identity-containing orbits')
    need(not set(excluded).intersection(members), 'AC and proof-orbit sets are disjoint')
    need(set(excluded).union(members) == set(universe), 'exact literal coverage without gaps')


def replay_binding(replay, cnf_hash, proof_hash):
    need(replay['accepted'] is True and replay['actual_exit_code'] == 0
         and replay['expected_acceptance'] is True, 'accepted independent complete replay')
    need(replay['cnf_sha256'] == cnf_hash and replay['proof_sha256'] == proof_hash,
         'exact replay CNF/proof pair')


def completed_proof_batch(gate, expected):
    records = gate['profile_records']
    need(gate['status'] == PROOF_STATUS, 'complete independent proof gate status')
    need(gate['completed_proof_replays'] == len(records) == 215, '215 complete proof replays')
    need(gate['UNKNOWN'] == gate['SAT_pending_separate_review'] == 0
         and gate['unattempted_profiles'] == [], 'no unknown, SAT or pending case in exclusion')
    need(gate['selected_profiles'] == [r['profile_id'] for r in records] == expected,
         'exact ordered 215-profile proof population')
    need(all(r['outcome'] == 'UNSAT_VERIFIED' for r in records), 'each literal outcome proof-verified')
    return records


def support_groups(raw):
    columns = {}
    for d in range(60):
        support = tuple(a for a in range(12) if raw['L'][a][d] == 1)
        columns.setdefault(support, []).append(d)
    need(len(columns) == 20 and all(len(s) == 6 and len(ds) == 3 for s, ds in columns.items()),
         'twenty literal six-coordinate triplicate supports')
    return [list(s) for s in columns], list(columns.values())


def profile_marginals(profile, groups):
    gs = profile['group_ids']
    d = profile['coordinate_fibre_deviations']
    need(len(gs) == 7 and gs == sorted(set(gs)) and all(0 <= g < 20 for g in gs),
         'seven literal exceptional groups')
    need(len(d) == 12 and all(len(a) == 3 and all(len(v) == 7 for v in a) for a in d),
         '12 by 3 by 7 deviation shape')
    need(all(type(x) is int and -1 <= x <= 2 for a in d for v in a for x in v),
         'integer local count bounds')
    for a in range(12):
        for j, g in enumerate(gs):
            need(sum(d[a][f][j] for f in range(3)) == 0, 'coordinate colour count total')
            if a not in groups[g]:
                need(all(d[a][f][j] == 0 for f in range(3)), 'absent coordinate has zero deviation')
        for f in range(3):
            need(sum(d[a][f]) == 0, 'row margin cancellation')
            for b in range(12):
                need(sum(d[a][f][j] for j, g in enumerate(gs) if b in groups[g]) == 0,
                     'literal support incidence marginal')
    for j, g in enumerate(gs):
        need(any(d[a][f][j] for a in range(12) for f in range(3)), 'each selected group unbalanced')
        for f in range(3):
            need(sum(d[a][f][j] for a in groups[g]) == 0, 'six entries per group and fibre')


def scope_binding(scope, profile, raw, groups, columns):
    need(scope['selected_profile_id'] == profile['id']
         and scope['selected_profile_sha256'] == profile['profile_sha256'], 'literal profile identity')
    need(scope['exceptional_groups'] == profile['group_ids']
         and scope['coordinate_fibre_deviations'] == profile['coordinate_fibre_deviations'],
         'literal profile values')
    need(scope['balanced_groups'] == [g for g in range(20) if g not in profile['group_ids']],
         'exact balanced complement')
    need(scope['core_adjacency36'] == raw['core_adjacency']
         and scope['prescribed_Gram36'] == raw['prescribed_Gram36']
         and scope['L12x60'] == raw['L'], 'literal core, Gram and support')
    need(scope['groups'] == groups and scope['group_columns'] == columns, 'literal support group order')
    need(scope['raw_support_path'] == RAW and scope['raw_support_sha256'] == RAW_HASH
         and scope['profile_universe_path'] == UNIVERSE
         and scope['profile_universe_sha256'] == UNIVERSE_HASH, 'immutable scope input identities')
    need(scope['initial_domain_references'] == profile['local_domains'], 'complete initial domains')
    need(scope['within_group_column_caps_encoded'] is True
         and scope['cross_group_column_caps_encoded'] is False
         and scope['residual_D_encoded'] is False, 'weaker necessary full-Gram formula')
    need(scope['arc_pruning_used'] is False and scope['orbit_coverage_used'] is False
         and scope['balance_WLOG'] is False and scope['assumed_target_automorphism'] is None,
         'no hidden scope reduction')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['prepare', 'final'])
    ap.add_argument('--proof-gate')
    ap.add_argument('--proof-gate-sha256')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    need((args.mode == 'final') == bool(args.proof_gate and args.proof_gate_sha256),
         'final requires both explicit proof gate arguments; prepare accepts neither')
    need(args.mode != 'prepare' or not (args.proof_gate or args.proof_gate_sha256),
         'preparation cannot consume proof gate arguments')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    pins, gates, gate_paths, bindings = {}, {}, {}, {}
    started = time.perf_counter()

    def pin(path, digest):
        path = key(path)
        need(isinstance(digest, str) and len(digest) == 64, 'required hash ' + path)
        if path not in pins:
            pins[path] = sha(ROOT / path)
        need(pins[path] == digest, 'input identity ' + path)
        return path

    def gate_output(name, path):
        path = key(path)
        pin(path, gates[name]['outputs_sha256'][path])
        return read(path)

    def add_binding(name, filename='claim_binding.json'):
        path = (Path(gate_paths[name]).parent / filename).as_posix()
        value = gate_output(name, path)
        for claim in value if isinstance(value, list) else [value]:
            need(claim['revision'] == 1 and claim['status'] == 'VERIFIED'
                 and claim['review_state'] == 'CLEAR', 'exact independently reviewed claim revision')
            bindings[claim['id']] = dict(path=path, sha256=pins[path], revision=1)

    def receipt(name, replay, cnf_hash, proof_hash):
        replay_binding(replay, cnf_hash, proof_hash)
        folder = Path(gate_paths[name]).parent
        path = (folder / (replay['name'] + '.receipt.json')).as_posix()
        need(gate_output(name, path) == replay, 'literal independent replay receipt')
        for suffix in ['stdout', 'stderr']:
            path = (folder / (replay['name'] + '.' + suffix + '.log')).as_posix()
            pin(path, gates[name]['outputs_sha256'][path])
            need(pins[path] == replay[suffix + '_sha256'], 'replay output hash')
            if suffix == 'stdout':
                need('s VERIFIED' in (ROOT / path).read_text(), 'independent checker acceptance output')

    try:
        for name, (digest, status) in GATES.items():
            path = I + name + '/summary.json'
            pin(path, digest)
            gates[name], gate_paths[name] = read(path), path
            need(gates[name]['status'] == status, 'approved exact premise ' + name)
            add_binding(name, 'claim_bindings.json' if name == 'hadamard_six_profile_union' else 'claim_binding.json')
        if args.mode == 'final':
            path = pin(args.proof_gate, args.proof_gate_sha256)
            gates['new_proofs'], gate_paths['new_proofs'] = read(path), path
            need(gates['new_proofs']['status'] == PROOF_STATUS, 'complete proof gate before promotion')
            add_binding('new_proofs')
            need(PROOF_CLAIM in bindings, 'exact expected literal215 exclusion claim')

        pin(RAW, RAW_HASH)
        raw = read(RAW)
        groups, columns = support_groups(raw)
        pin(UNIVERSE, UNIVERSE_HASH)
        with gzip.open(ROOT / UNIVERSE, 'rt', encoding='utf-8') as stream:
            profiles = [json.loads(line) for line in stream]
        ids = [p['id'] for p in profiles]
        by_id = {p['id']: p for p in profiles}
        lookup = {literal_key(p['group_ids'], p['coordinate_fibre_deviations']): p['id'] for p in profiles}
        need(len(ids) == len(set(ids)) == len(lookup) == 1608, 'unique complete literal population')
        for name in ['hadamard_seven_profile_local_domains', 'hadamard_seven_profile_arc',
                     'hadamard_seven_fibre_orbits', 'hadamard_seven_profile_cnf',
                     'hadamard_twohundredfifteen_profile_cnfs_v2']:
            need(gates[name]['inputs_sha256'][RAW] == RAW_HASH
                 and gates[name]['inputs_sha256'][UNIVERSE] == UNIVERSE_HASH,
                 'premises use identical fixed support and literal universe')

        retained = gate_output('hadamard_seven_exception_census',
                               I + 'hadamard_seven_exception_census/independent_remaining.json')['records']
        marginal = gate_output('hadamard_seven_rank5_profiles',
                               I + 'hadamard_seven_rank5_profiles/all_positive_marginal_profiles.json')['records']
        need(len(retained) == len(marginal) == 200
             and [r['groups'] for r in retained] == [r['groups'] for r in marginal]
             and [r['case'] for r in marginal] == list(range(200)), 'all200 rank-census outputs enter the DP')
        paths = {(r['case'], tuple(r['groups']), tuple(p)) for r in marginal for p in r['ordered_choice_paths']}
        need(len(paths) == 1608 and paths == {(p['rank5_case'], tuple(p['group_ids']), tuple(p['choice_path'])) for p in profiles},
             'every complete marginal path maps to one literal profile, without omissions')
        for profile in profiles:
            profile_marginals(profile, groups)
            need([d['group'] for d in profile['local_domains']] == profile['group_ids'], 'all seven initial domains')
            for domain in profile['local_domains']:
                pin(domain['path'], domain['sha256'])
                need(gates['hadamard_seven_profile_local_domains']['inputs_sha256'][domain['path']] == domain['sha256'],
                     'same complete independently checked local domain')

        outcomes = gate_output('hadamard_seven_profile_arc',
                               I + 'hadamard_seven_profile_arc/profile_outcomes.json')['records']
        need([r['id'] for r in outcomes] == ids and [r['index'] for r in outcomes] == list(range(1608)),
             'AC exact population ordering')
        empty = {r['id']: r['combined_empty'] for r in outcomes}
        need(all(type(v) is bool for v in empty.values()), 'literal AC classifications')
        excluded = [pid for pid in ids if empty[pid]]
        all_orbits, orbits, maps = {}, {}, []
        actions = list(permutations(range(3)))
        for profile in profiles:
            images = []
            for tau in actions:
                changed = image(profile['coordinate_fibre_deviations'], tau)
                destination = lookup[literal_key(profile['group_ids'], changed)]
                need(image(changed, [tau.index(f) for f in range(3)]) == profile['coordinate_fibre_deviations'],
                     'literal inverse fibre action')
                images.append(destination)
            members, rep = sorted(images), min(images)
            need(len(set(members)) == 6 and all(empty[x] == empty[profile['id']] for x in members),
                 'six distinct images and AC label covariance')
            all_orbits[rep] = members
            if not empty[profile['id']]:
                orbits[rep] = members
            maps.append(dict(profile_id=profile['id'], representative=rep, images=images,
                             AC_excluded=empty[profile['id']]))
        need(len(all_orbits) == 268, 'all268 literal orbits')
        saved = gate_output('hadamard_seven_fibre_orbits',
                            I + 'hadamard_seven_fibre_orbits/independent_orbits.json')['orbits']
        need({r['representative_id']: sorted(r['member_ids']) for r in saved} == all_orbits,
             'independent literal actions reproduce authenticated normalization')
        need({r['representative_id'] for r in saved if not r['Gram_caps_empty']} == set(orbits),
             'exact nonempty orbit labels')
        for tau in actions:
            rows = [12 * tau[f] + a for f in range(3) for a in range(12)]
            for matrix in [raw['core_adjacency'], raw['prescribed_Gram36']]:
                need(all(matrix[rows[i]][rows[j]] == matrix[i][j] for i in range(36) for j in range(36)),
                     'literal core and prescribed Gram invariant under every global fibre map')

        pin(SELECTION, SELECTION_HASH)
        selection = read(SELECTION)
        pin(BATCH, BATCH_HASH)
        batch = read(BATCH)
        enc = gates['hadamard_twohundredfifteen_profile_cnfs_v2']
        for path in [SELECTION, BATCH]:
            need(enc['inputs_sha256'][path] == pins[path], 'audited exact finite formula selection')
        expected = selection['remaining_profile_ids']
        representatives = [PRIOR_ID, *expected]
        need(selection['omitted_previously_proved_profile'] == PRIOR_ID, 'sole prior literal omitted for bookkeeping')
        need([r['profile_id'] for r in batch['records']] == expected and len(expected) == 215,
             'complete selected formula order')
        cover(ids, excluded, orbits, representatives)
        enc_records = gate_output('hadamard_twohundredfifteen_profile_cnfs_v2',
                                  I + 'hadamard_twohundredfifteen_profile_cnfs_v2/records.json')
        need([r['profile_id'] for r in enc_records] == expected, 'independent formula records match selection')
        bound_formulas, scopes = {}, {}
        for record, checked in zip(batch['records'], enc_records):
            pid = record['profile_id']
            for field in ['cnf', 'model', 'scope']:
                path, digest = record[field + '_path'], record[field + '_sha256']
                pin(path, digest)
                need(enc['inputs_sha256'][path] == digest and checked[field + '_path'] == path
                     and checked[field + '_sha256'] == digest, 'same independently encoded literal formula')
            scope = read(record['scope_path'])
            scope_binding(scope, by_id[pid], raw, groups, columns)
            selected = (Path(record['scope_path']).parent / 'selected_profile.json').as_posix()
            pin(selected, scope['selected_profile_artifact_sha256'])
            need(read(selected) == by_id[pid], 'complete selected profile artifact identity')
            bound_formulas[pid], scopes[pid] = record, scope
        old_paths = {field: B + 'hadamard_seven_profile_cnf/profile_0001/' + file
                     for field, file in [('cnf', 'instance.cnf'), ('model', 'model.json'), ('scope', 'scope.json')]}
        for path in old_paths.values():
            pin(path, gates['hadamard_seven_profile_cnf']['inputs_sha256'][path])
            need(gates['hadamard_seven_profile_unsat']['inputs_sha256'][path] == pins[path], 'prior encoding/proof input')
        prior_scope = read(old_paths['scope'])
        scope_binding(prior_scope, by_id[PRIOR_ID], raw, groups, columns)
        prior = gates['hadamard_seven_profile_unsat']
        trace = prior['proof']
        need(trace['complete_independent_replay'] is True, 'prior complete proof')
        pin(trace['path'], trace['sha256'])
        need((ROOT / trace['path']).stat().st_size == trace['bytes'], 'prior complete proof byte length')
        old_replay = next(r for r in prior['replays'] if r['name'] == 'complete_profile0001_proof')
        receipt('hadamard_seven_profile_unsat', old_replay, pins[old_paths['cnf']], trace['sha256'])
        proof_bytes = trace['bytes']
        proof_records = [dict(profile_id=PRIOR_ID, cnf_sha256=pins[old_paths['cnf']],
                              scope_sha256=pins[old_paths['scope']], proof_sha256=trace['sha256'],
                              proof_bytes=trace['bytes'], orbit_members=orbits[PRIOR_ID])]

        if args.mode == 'final':
            proof_gate = gates['new_proofs']
            records = completed_proof_batch(proof_gate, expected)
            for record in records:
                pid = record['profile_id']
                for field in ['cnf', 'model', 'scope']:
                    need(record[field + '_path'] == bound_formulas[pid][field + '_path']
                         and record[field + '_sha256'] == bound_formulas[pid][field + '_sha256'],
                         'proof uses the exact selected independently encoded formula')
                scope = scopes[pid]
                need(record['literal_profile'] == {k: scope[k] for k in record['literal_profile']},
                     'proof report literal scope matches full checked scope')
                trace = record['trace']
                pin(trace['path'], trace['sha256'])
                need((ROOT / trace['path']).stat().st_size == trace['bytes'], 'full available proof byte length')
                receipt('new_proofs', record['replay'], record['cnf_sha256'], trace['sha256'])
                for field in ['run_summary', 'native_receipt']:
                    pin(record[field + '_path'], record[field + '_sha256'])
                proof_bytes += trace['bytes']
                proof_records.append(dict(profile_id=pid, scope_sha256=record['scope_sha256'],
                                          cnf_sha256=record['cnf_sha256'], proof_sha256=trace['sha256'],
                                          proof_bytes=trace['bytes'], orbit_members=orbits[pid]))

        controls = []
        def reject(name, function):
            try:
                function()
            except (ValueError, KeyError):
                controls.append(name)
                return
            raise ValueError('corruption accepted: ' + name)
        reject('missing_representative', lambda: cover(ids, excluded, orbits, representatives[:-1]))
        reject('duplicate_representative', lambda: cover(ids, excluded, orbits, representatives[:-1] + [PRIOR_ID]))
        bad = deepcopy(orbits)
        bad[representatives[0]][0] = bad[representatives[1]][0]
        reject('orbit_overlap_and_gap', lambda: cover(ids, excluded, bad, representatives))
        reject('wrong_AC_identity', lambda: cover(ids, [PRIOR_ID, *excluded[1:]], orbits, representatives))
        reject('unknown_universe_ID', lambda: cover(ids[:-1] + ['absent'], excluded, orbits, representatives))
        reject('nonbijective_fibre_action', lambda: image(profiles[0]['coordinate_fibre_deviations'], [0, 0, 2]))
        bad_replay = deepcopy(old_replay)
        bad_replay['accepted'] = False
        reject('unaccepted_complete_replay', lambda: replay_binding(bad_replay, old_replay['cnf_sha256'], old_replay['proof_sha256']))
        reject('wrong_CNF_hash', lambda: replay_binding(old_replay, '0' * 64, old_replay['proof_sha256']))
        reject('wrong_proof_hash', lambda: replay_binding(old_replay, old_replay['cnf_sha256'], '0' * 64))
        bad_scope = deepcopy(prior_scope)
        bad_scope['coordinate_fibre_deviations'][0][0][0] += 1
        reject('changed_literal_scope', lambda: scope_binding(bad_scope, by_id[PRIOR_ID], raw, groups, columns))
        bad_scope = deepcopy(prior_scope)
        bad_scope['arc_pruning_used'] = True
        reject('unreviewed_local_pruning', lambda: scope_binding(bad_scope, by_id[PRIOR_ID], raw, groups, columns))
        bad_profile = deepcopy(by_id[PRIOR_ID])
        bad_profile['coordinate_fibre_deviations'][0][0][0] = 3
        reject('invalid_local_count_bound', lambda: profile_marginals(bad_profile, groups))
        toy_gate = dict(status=PROOF_STATUS, completed_proof_replays=215, UNKNOWN=0,
                        SAT_pending_separate_review=0, unattempted_profiles=[], selected_profiles=expected,
                        profile_records=[dict(profile_id=p, outcome='UNSAT_VERIFIED') for p in expected])
        completed_proof_batch(toy_gate, expected)
        for field, value in [('UNKNOWN', 1), ('SAT_pending_separate_review', 1),
                             ('unattempted_profiles', [expected[-1]]), ('completed_proof_replays', 214),
                             ('status', 'UNCHECKED_UNSAT')]:
            bad_gate = deepcopy(toy_gate)
            bad_gate[field] = value
            reject('terminal_gate_' + field, lambda q=bad_gate: completed_proof_batch(q, expected))
        toy = [list(range(i, i + 6)) for i in range(0, 18, 6)]
        need(Counter(x for block in toy for x in block) == Counter(range(18)), 'small known disjoint partition')
        need(set(range(7)).isdisjoint({7}) and set(range(7)).union({7}) == set(range(8)),
             'disjoint integer cases zero through six and seven')
        save(out / 'controls.json', dict(rejected_corruptions=controls, positive_actual_partition=True,
             small_partition_positive=toy, synthetic_complete_receipt_metadata_positive=True,
             synthetic_receipt_is_not_a_research_proof=True, integer_exception_partition=[list(range(7)), [7]],
             full_factor_positive_fixture=None, full_factor_positive_fixture_null_reason='Coverage composition, not a factor validator.'))
        save(out / 'coverage.json', dict(profile_population=ids, AC_excluded=excluded, all_orbits=all_orbits,
             expected_proof_representatives=representatives, nonempty_orbits=orbits, profile_maps=maps,
             covered_once=dict(Counter(excluded + [x for r in representatives for x in orbits[r]])),
             authenticated_proof_records=proof_records, new_proof_batch_checked=args.mode == 'final'))
        for path in [key(__file__), SPEC, DOC, 'docs/AUDIT_20260930_HADAMARD_SEVEN_FIBRE_ORBITS.md',
                     'acceleration/audit_20260930_hadamard_six_profile_union.py', 'uv.lock', 'pyproject.toml']:
            pin(path, sha(ROOT / path))
        now = datetime.now(timezone.utc).isoformat()
        claim_ids = []
        if args.mode == 'final':
            base = dict(revision=1, kind='exclusion', basis=['DERIVED', 'COMPUTED'], status='VERIFIED',
                review_state='CLEAR', verifier='/root/eight_domain_audit', created_at=now, updated_at=now,
                checking_method='Independent complete literal1608-profile action/partition, 216 exact scope/encoding/proof-identity composition, and written implication proof; no solver or DRAT rerun.',
                trusted_components=['Pinned independently reviewed rank/DP coverage, complete local domains, AC soundness, global-fibre normalization, exact encodings and complete DRAT replays.',
                                    'Python standard-library exact integer, set, JSON and SHA256 operations; no producer or checker imports.'],
                assumptions=['Binary36x60 factor on exactly the pinned six-prism Hadamard support, with its prescribed full integer Gram.',
                             'Every pair of distinct outside columns has overlap at most2, including within identical-support groups.'],
                limitations=['Only this fixed-support family; no exclusion of all supports, the core or unrestricted Conway99.',
                             'Eight or more unbalanced groups remain unresolved by these statements.',
                             'No automorphism of a hypothetical target is assumed.',
                             'Prior exhaustive mathematical and DRAT gates are explicit premises, not rerun by this composition.'],
                artifact_availability='LOCAL_ONLY', availability_reason='Awaiting parent publication.',
                external_review=None, external_review_null_reason='Internal independent composition only.',
                inputs_sha256=pins, premise_bindings=bindings)
            first = dict(base, id='C-FIXED-HADAMARD-EXACTLY-SEVEN-UNBALANCED-GROUPS-EXCLUSION',
                statement='No binary36x60 factor on the pinned six-prism Hadamard support can have the prescribed full integer Gram, every outside-column overlap at most2, and exactly seven unbalanced identical-support triplicate groups.',
                scope='All exactly-seven-unbalanced factors on this one fixed support;1608 necessary literal profiles are covered exactly once by312 AC exclusions and1296 members of216 proof-excluded fibre orbits.',
                dependencies=[dict(id=cid, revision=1, relation=relation) for cid, relation in [
                    ('C-FIXED-HADAMARD-SEVEN-EXCEPTION-KERNEL-CENSUS', 'coverage'),
                    ('C-FIXED-HADAMARD-SEVEN-EXCEPTION-INTEGER-MARGINAL-CENSUS', 'coverage'),
                    ('C-FIXED-HADAMARD-SEVEN-EXCEPTION-LOCAL-DOMAIN-FILTER', 'coverage'),
                    ('C-FIXED-HADAMARD-SEVEN-EXCEPTION-PAIRWISE-PROFILE-SCREEN', 'uses_result'),
                    ('C-FIXED-HADAMARD-SEVEN-EXCEPTION-FIBRE-NORMALIZATION', 'normalization'),
                    ('C-FIXED-HADAMARD-SEVEN-EXCEPTION-PROFILE0001-GRAM-ENCODING', 'encoding_equivalence'),
                    ('C-FIXED-HADAMARD-SEVEN-EXCEPTION-PROFILE0001-EXCLUSION', 'uses_result'),
                    ('C-FIXED-HADAMARD-TWOHUNDREDFIFTEEN-SEVEN-EXCEPTION-GRAM-ENCODINGS', 'encoding_equivalence'),
                    (PROOF_CLAIM, 'uses_result')]])
            second = dict(base, id='C-FIXED-HADAMARD-AT-MOST-SEVEN-UNBALANCED-GROUPS-EXCLUSION',
                statement='Every binary36x60 factor on the pinned six-prism Hadamard support with the prescribed full integer Gram and all outside-column overlaps at most2 has at least eight unbalanced identical-support triplicate groups.',
                scope='At-most-seven-unbalanced subfamily excluded by disjoint integer cases0..6 and7; no existence assertion for eight or more.',
                dependencies=[dict(id=cid, revision=1, relation='uses_result') for cid in [
                    'C-FIXED-HADAMARD-AT-MOST-SIX-UNBALANCED-GROUPS-EXCLUSION', first['id']]])
            for claim in [first, second]:
                for dep in claim['dependencies']:
                    need(dep['id'] in bindings or dep['id'] == first['id'], 'every exact dependency bound')
            save(out / 'claim_bindings.json', [first, second])
            claim_ids = [first['id'], second['id']]
        result = dict(status='INDEPENDENT_FIXED_HADAMARD_SEVEN_PROFILE_UNION_PASS' if args.mode == 'final'
                      else 'INDEPENDENT_SEVEN_PROFILE_UNION_PREPARATION_PASS', mode=args.mode, timestamp=now,
            source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
            inputs_sha256=pins, outputs_sha256={key(p): sha(p) for p in out.iterdir()},
            profile_population=1608, AC_exclusions=312, all_orbits=268, nonempty_orbits=216,
            nonempty_profile_members=1296, rank_census_retained_subsets=200, exact_formula_scopes_checked=216,
            duplicate_coverage=0, missing_profiles=0, authenticated_complete_proofs=len(proof_records),
            authenticated_complete_proof_bytes=proof_bytes, approved_claim_ids=claim_ids,
            pending_new_proof_gate=args.mode != 'final', exclusion_approved=args.mode == 'final',
            rejected_corruptions=len(controls), new_native_calls=0, new_DRAT_replays=0,
            target_resolution=False, elapsed_seconds=time.perf_counter() - started)
        save(out / 'summary.json', result)
        print(json.dumps(dict(status=result['status'], summary_sha256=sha(out / 'summary.json'),
                              elapsed_seconds=result['elapsed_seconds'])))
    except BaseException as error:
        save(out / 'failure.json', dict(error=repr(error), traceback=traceback.format_exc(),
                                       source_sha256=sha(Path(__file__)), inputs_sha256=pins))
        raise


if __name__ == '__main__':
    main()
