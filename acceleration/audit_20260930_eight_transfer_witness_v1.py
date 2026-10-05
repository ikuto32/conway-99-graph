"""Independent set-graph checking of 84 frozen-weight support witnesses.

Standard library only; no producer or prior audit module is imported. Checks
each selected star and each matching edge by actual full-99 graph mutation.
No full maxima, matching counts, screening order, or optimizer is checked.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'acceleration/results/20260916_star_guided_round2/search/probes/selection_03_index_18481_candidate.json'
NEW = ROOT/'acceleration/results/20260930_eight_domains/run01'
OLD = ROOT/'acceleration/results/20260917_partial_six_matchings'
CERT = ROOT/'acceleration/results/20260917_six_moment_pdhg/run01/certificates/10000_last.json'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def all_caps(graph):
    return all(len(row) <= 14 and v not in row for v,row in enumerate(graph)) and all(
        (v in graph[u]) == (u in graph[v]) and len(graph[u] & graph[v]) <= 2-int(v in graph[u])
        for u,v in combinations(range(len(graph)),2))


def add(graph,u,v):
    need(u != v and v not in graph[u] and u not in graph[v], 'new simple edge required')
    graph[u].add(v)
    graph[v].add(u)


def valid_matching(nodes, witness, allowed):
    return (len(witness)*2 == len(nodes) and sorted(v for edge in witness for v in edge) == sorted(nodes)
            and all(len(edge) == 2 and tuple(sorted(edge)) in allowed for edge in witness))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists(), 'preserve prior audit')
    started = time.monotonic()
    bindings = {}

    def read(path):
        bindings[key(path)] = digest(path)
        return json.loads(Path(path).read_bytes())

    result = read(args.run/'summary.json')
    run_manifest = read(args.run/'manifest.json')
    certificate = read(CERT)
    old_manifest = read(OLD/'manifest.json')
    new_manifest = read(NEW/'manifest.json')
    raw = read(BASE)
    for path,expected in run_manifest['inputs_sha256'].items():
        need(digest(ROOT/path) == expected, 'producer input changed: ' + path)
        bindings[path] = expected
    for name,expected in result['output_sha256'].items():
        need(digest(args.run/name) == expected, 'producer output changed: ' + name)
        bindings[key(args.run/name)] = expected
    # Independent label list construction: sort admissible root-symbol pairs.
    labels = sorted([(a,b) for a in range(14) for b in range(a+1,14) if a//2 != b//2],
                    key=lambda pair:(pair[0]//2,pair[1]//2,pair[0]%2,pair[1]%2))
    support = [{a//2,b//2} for a,b in labels]
    pairs = list(combinations(range(84),2))
    released = {pair for pair in pairs if len(support[pair[0]]&support[pair[1]]) == 1
                and any(symbol < 8 and symbol in labels[pair[1]] for symbol in labels[pair[0]])}
    baseline = set(map(tuple,raw['overlap_edges_outer_zero_based']))
    fixed = baseline-released
    unknown = {pair for pair in pairs if support[pair[0]].isdisjoint(support[pair[1]])} | released
    need((len(baseline),len(fixed),len(released),len(unknown)) == (168,120,480,2160), 'scope counts')
    need(new_manifest['remaining_fixed_K_edges_outer'] == sorted(map(list,fixed))
         and new_manifest['unknown_edges_outer'] == sorted(map(list,unknown)), 'scope identities')
    graph = [set() for _ in range(99)]
    for root in range(1,15):
        add(graph,0,root)
    for root in range(1,15,2):
        add(graph,root,root+1)
    for u,pair in enumerate(labels):
        for symbol in pair:
            add(graph,u+15,symbol+1)
    for u,v in fixed:
        add(graph,u+15,v+15)
    need(all_caps(graph), 'fixed graph caps')
    denominator = certificate['denominator']
    y_values = certificate['moment_weight_numerators']
    q_values = certificate['reciprocity_weight_numerators']
    old_unknown = list(map(tuple,old_manifest['unknown_edges_outer']))
    need(type(denominator) is int and denominator == 1048576, 'denominator')
    need(len(y_values) == len(pairs) and len(q_values) == len(old_unknown) == 2040
         and all(type(value) is int for value in y_values+q_values)
         and all(abs(value) <= denominator for value in y_values), 'exact coefficient dimensions and box')
    need(set(old_unknown) <= unknown and len(set(old_unknown)) == 2040, 'zero-extension scope')
    y = dict(zip(pairs,y_values))
    q = dict(zip(old_unknown,q_values))
    roots = set(range(15))
    rhs_dot = sum(y[(a,b)] * (2-int(b+15 in graph[a+15])-len(graph[a+15]&graph[b+15]&roots))
                  for a,b in pairs)
    unknown99 = {(a+15,b+15) for a,b in unknown}

    def check(record, table):
        u = record['outer_vertex']
        need(type(u) is int and 0 <= u < 84, 'center')
        index = record['original_id']
        need(type(index) is int and 0 <= index < table['domain_size'], 'original ID')
        need(record['mask_hex'] == table['domain_masks_hex'][index], 'raw domain mask identity')
        mask = int(record['mask_hex'],16)
        need(0 <= mask < 1 << 84, 'mask range')
        chosen = {v for v in range(84) if mask >> v & 1}
        trial = [row.copy() for row in graph]
        for v in chosen:
            need(tuple(sorted((u,v))) in unknown, 'star edge outside unknown universe')
            add(trial,u+15,v+15)
        center = u+15
        need(len(trial[center]) == 14 and all_caps(trial), 'star degree or full99 caps')
        need(all(len(trial[center]&trial[root]) == 2-int(root in trial[center]) for root in range(1,15)), 'exact root quotas')
        neighbors = sorted(trial[center])
        forced = [[a,b] for a,b in combinations(neighbors,2) if b in trial[a]]
        used = [v for edge in forced for v in edge]
        need(len(used) == len(set(used)), 'forced graph is not a matching')
        free = sorted(set(neighbors)-set(used))
        saved = record['matching']
        need(forced == saved['forced_edges_full99'] and free == saved['unmatched_vertices_full99'], 'matching vertex scope')
        witness = saved['matching_witness_full99']
        need(valid_matching(free,witness,unknown99), 'matching endpoint coverage or unknown-edge scope')
        for a,b in witness:
            single = [row.copy() for row in trial]
            add(single,a,b)
            need(all_caps(single), 'matching edge not individually admissible')
        outer = {v-15 for v in trial[center] if v >= 15}
        need(len(outer) == 12, 'full outer neighborhood size')
        # Dot the mathematical row definitions with the one-column incidence
        # directly. This is not the producer's sparse neighborhood scorer.
        moment_score = sum(weight * (int(a in outer and b in outer) + int(a == u and b in chosen))
                           for (a,b),weight in y.items())
        reciprocity_score = sum(weight * (int(a == u and b in chosen)-int(b == u and a in chosen))
                                for (a,b),weight in q.items())
        score = moment_score+reciprocity_score
        need(score == record['score_numerator'], 'exact column score')
        return dict(outer_vertex=u,original_id=index,score_numerator=score,moment_score_numerator=moment_score,
                    reciprocity_score_numerator=reciprocity_score,matching_edges_individually_checked=len(witness),
                    forced_matching_edges=len(forced),domain_sha256=digest(NEW/f'domain_{u:02d}.json'))

    need(len(result['records']) == 84 and [r['outer_vertex'] for r in result['records']] == list(range(84)), '84 distinct ordered witnesses')
    tables = [read(NEW/f'domain_{u:02d}.json') for u in range(84)]
    # A known matching fixture and deliberate missing/duplicate edge fixtures.
    need(valid_matching([1,2,3,4],[[1,2],[3,4]],{(1,2),(3,4)}), 'positive matching fixture')
    need(not valid_matching([1,2,3,4],[[1,2]],{(1,2),(3,4)}), 'missing matching edge fixture')
    need(not valid_matching([1,2,3,4],[[1,2],[1,2]],{(1,2),(3,4)}), 'duplicate matching edge fixture')
    good = result['records'][0]
    check(good,tables[0])
    rejected = []
    for corruption in ('score','missing_star_edge','missing_matching_edge','duplicate_matching_edge'):
        bad = deepcopy(good)
        if corruption == 'score':
            bad['score_numerator'] += 1
        elif corruption == 'missing_star_edge':
            mask = int(bad['mask_hex'],16)
            bad['mask_hex'] = hex(mask ^ (mask & -mask))
        elif corruption == 'missing_matching_edge':
            bad['matching']['matching_witness_full99'].pop()
        else:
            bad['matching']['matching_witness_full99'][-1] = bad['matching']['matching_witness_full99'][0]
        try:
            check(bad,tables[0])
        except ValueError:
            rejected.append(corruption)
        else:
            raise ValueError('corruption accepted: ' + corruption)
    records = [check(record,tables[u]) for u,record in enumerate(result['records'])]
    total = sum(record['score_numerator'] for record in records)
    upper = rhs_dot-total
    need((rhs_dot,total,upper,denominator) == (result['rhs_dot_numerator'],result['witness_sum_numerator'],
                                             result['support_bound_upper_numerator'],result['denominator']), 'saved exact totals')
    need(upper < 0 and result['transferred_positive_bound_refuted'], 'nonpositive transferred bound')
    for path in (__file__,ROOT/'uv.lock'):
        bindings[key(path)] = digest(path)
    need(all(digest(ROOT/path) == expected for path,expected in bindings.items()), 'input stability')
    audit = dict(status='INDEPENDENT_EIGHT_COORDINATE_FROZEN_WEIGHT_NONPOSITIVITY_PASS',
                 claim_id='C-EIGHT-COORDINATE-FROZEN-WEIGHT-NONPOSITIVITY',claim_revision=1,recommendation='VERIFIED',
                 statement='For the exact 10000-last six-coordinate weights, zero-extended by reciprocity weight zero on newly freed edges, the eight-coordinate local domain with the individually admissible-neighborhood-matching necessary test has support-bound value at most -3762780/1048576. Therefore this one fixed transferred vector cannot give a positive support-bound exclusion.',
                 timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                 command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                 verifier='/root/eight_domain_audit independent checking agent',verification_type='Independent set-graph artifact checking and row-incidence integer dot products',
                 scope='Exactly the 120-fixed-K-edge eight-coordinate family and one fixed certificate vector. No automorphism assumption.',
                 inputs_sha256=bindings,records=records,checked_witness_stars=84,
                 individual_matching_edges_checked=sum(record['matching_edges_individually_checked'] for record in records),
                 rhs_dot_numerator=rhs_dot,witness_sum_numerator=total,support_bound_upper_numerator=upper,
                 denominator=denominator,reduced_upper_bound=str(Fraction(upper,denominator)),
                 derivation='For each center u the verified witness is in its local matching-survivor domain H_u, so max_{s in H_u} score_u(s) is at least its witness score. Summing, (y*b - sum_u max score_u)/D <= (2543434-6306214)/1048576 < 0. No full maximization is needed for this upper bound.',
                 controls=dict(known_matching_accepted=True,missing_and_duplicate_matching_fixtures_rejected=True,
                               raw_positive_star_accepted=True,corrupted_records_rejected=rejected),
                 producer_imported=False,shared_code='Python standard library only; no producer or prior checker imports',
                 elapsed_seconds=time.monotonic()-started,artifact_availability='LOCAL_ONLY',
                 artifact_availability_reason='Local raw artifacts hash-bound before publication',
                 limitations=['No full maxima, exact support-bound value, full matching counts, or screening-order correctness checked.',
                              '84 independently admissible stars need not agree globally.',
                              'Each matching edge is checked alone; the full matching is not claimed jointly valid.',
                              'Only this fixed coefficient vector is excluded from giving a positive bound; no statement about other weights or global feasibility.',
                              'Producer sampled-choice and matching-attempt counts were not independently reproduced.'],
                 target_resolution=False,external_review=False)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:
        json.dump(audit,stream,indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=audit['status'],upper_bound=audit['reduced_upper_bound'],sha256=digest(args.out))))


if __name__ == '__main__':
    main()
