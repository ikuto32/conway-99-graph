"""Bounded native local-condition scan of accepted global-defect states.

This preserves complete native domains and pair-AC traces, but does not replace
independent domain enumeration or event replay. Numerical merit remains only
the saved phase-I merit of each candidate.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time

from audit_certificate import full_graph, require

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def read(path):
    return json.loads(path.read_bytes())


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def invoke(args):
    subprocess.run([str(a) for a in args], check=True, timeout=45,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--initial-directory', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve previous scan')
    summary_path = args.directory/'summary.json'
    summary = read(summary_path)
    require(summary['status'] == 'BOUNDED_GLOBAL_DEFECT_SEARCH_FINISHED', 'Search incomplete')
    args.out.mkdir(parents=True)
    stars = ROOT/'acceleration/build/star_domains.exe'
    pairs = ROOT/'acceleration/build/pair_domains.exe'
    source_paths = [Path(__file__), summary_path, args.directory/'manifest.json', stars, pairs,
                    ROOT/'acceleration/star_domains.rs', ROOT/'acceleration/pair_domains.rs',
                    ROOT/'acceleration/audit_certificate.py']
    bindings = {key(p): digest(p) for p in source_paths}
    started = time.perf_counter()
    records = []

    def metrics(candidate_path, domain_path, pair_path, objective, iteration, probe_path=None):
        candidate, domains, closure = map(read, (candidate_path, domain_path, pair_path))
        full_graph(candidate)
        require(domains['complete_domain_enumeration'] is True, 'Incomplete domain enumeration')
        sizes = [len(d['domain_masks_hex']) for d in domains['domains']]
        require(len(sizes) == 84, 'Domain count mismatch')
        record = dict(iteration=iteration, numeric_phase1_objective=objective,
                      candidate_path=key(candidate_path), candidate_sha256=digest(candidate_path),
                      domains_path=key(domain_path), domains_sha256=digest(domain_path),
                      pair_path=key(pair_path), pair_sha256=digest(pair_path),
                      local_empty_count=sum(n == 0 for n in sizes),
                      min_domain_size=min(sizes), total_domains=sum(sizes),
                      reciprocity_status=domains['propagation']['status'],
                      reciprocity_surviving_domains=sum(map(len, domains['propagation']['surviving_domain_ids'])),
                      pair_status=closure['propagation_status'],
                      pair_empty_vertex=closure['empty_vertex'],
                      pair_surviving_domains=sum(map(len, closure['surviving_domain_ids'])),
                      pair_checks=closure['domain_pairs_evaluated'],
                      pair_relations=closure['vertex_pair_relations_built'],
                      pair_events=len(closure['events']),
                      domain_seconds=domains['elapsed_seconds'], pair_seconds=closure['elapsed_seconds'])
        if probe_path:
            record.update(phase1_path=key(probe_path), phase1_sha256=digest(probe_path))
        for p in (candidate_path, domain_path, pair_path):
            bindings[key(p)] = digest(p)
        if probe_path:
            bindings[key(probe_path)] = digest(probe_path)
        records.append(record)
        print(json.dumps({k: record[k] for k in ('iteration', 'numeric_phase1_objective',
                          'total_domains', 'pair_status', 'pair_empty_vertex')}), flush=True)

    initial_probe = summary['records'][0]['previous_probe']
    initial_path = ROOT/initial_probe['candidate_path']
    initial_known = args.initial_directory/'best_candidate.json'
    require(read(initial_path)['overlap_edges_outer_zero_based'] == read(initial_known)['overlap_edges_outer_zero_based'],
            'Initial controls do not match the search initial state')
    require(digest(initial_path) == initial_probe['candidate_sha256'], 'Initial candidate hash mismatch')
    metrics(initial_path, args.initial_directory/'best_domains_native.json',
            args.initial_directory/'best_pair_native_500m.json', initial_probe['objective'], -1,
            ROOT/initial_probe['result_path'])

    accepted = [r for r in summary['records'] if r['accepted']]
    require(len(accepted) == summary['accepted_moves'] == len(summary['overlap_candidates'])-1,
            'Accepted state count mismatch')
    for index, record in enumerate(accepted, 1):
        probe = record['chosen_probe']
        candidate_path, probe_path = ROOT/probe['candidate_path'], ROOT/probe['result_path']
        require(digest(candidate_path) == probe['candidate_sha256'], 'Candidate hash mismatch')
        require(digest(probe_path) == probe['result_sha256'], 'Phase-I hash mismatch')
        candidate = read(candidate_path)
        edges = candidate['overlap_edges_outer_zero_based']
        require(edges == summary['overlap_candidates'][index], 'Saved snapshot mismatch')
        full_graph(candidate)
        prefix = args.out/f"iteration_{record['iteration']:04d}"
        input_path = prefix.with_suffix('.txt')
        domain_path = Path(str(prefix)+'_domains.json')
        pair_input = Path(str(prefix)+'_pair_domains.txt')
        pair_path = Path(str(prefix)+'_pair.json')
        input_path.write_text('C99OVERLAPS1 1\n'+' '.join(str(x) for edge in edges for x in edge)+'\n', encoding='ascii')
        if edges == read(args.directory/'best_candidate.json')['overlap_edges_outer_zero_based']:
            domain_path = args.directory/'best_star_domains_native.json'
            pair_path = args.directory/'best_pair_ac_native.json'
        else:
            invoke([stars, input_path, domain_path, 30, 2000000, 20000])
            domains = read(domain_path)
            require(domains['complete_domain_enumeration'] is True, 'Domain cap reached; no exclusion')
            require(all(d['domain_masks_hex'] for d in domains['domains']), 'Local empty requires separate handling')
            pair_input.write_text('C99DOMAINS1 84\n'+'\n'.join(str(len(d['domain_masks_hex']))+' '+
                                  ' '.join(d['domain_masks_hex']) for d in domains['domains'])+'\n', encoding='ascii')
            invoke([pairs, input_path, pair_input, pair_path, 30, 500000000])
        bindings[key(input_path)] = digest(input_path)
        if pair_input.exists():
            bindings[key(pair_input)] = digest(pair_input)
        metrics(candidate_path, domain_path, pair_path, probe['objective'], record['iteration'], probe_path)

    passing = [r for r in records if r['pair_status'] == 'ARC_CONSISTENT_NONEMPTY']
    result = dict(status='NATIVE_LOCAL_CONDITION_SCAN_FINISHED', inputs_sha256=bindings,
                  records=records, accepted_states=len(accepted), total_states=len(records),
                  pair_nonempty_states=len(passing), pair_empty_states=sum(r['pair_status'] == 'EMPTY_DOMAIN' for r in records),
                  pair_incomplete_states=sum(r['pair_status'] == 'INCOMPLETE' for r in records),
                  best_pair_nonempty=min(passing, key=lambda r:r['numeric_phase1_objective']) if passing else None,
                  elapsed_seconds=time.perf_counter()-started,
                  scope='Native complete-domain and full pair-AC controls, not independently replayed here. Nonempty AC is only a necessary condition. Saved phase-I objectives are numerical.')
    save(args.out/'summary.json', result)
    print(json.dumps({k:result[k] for k in ('status','total_states','pair_nonempty_states','pair_empty_states','pair_incomplete_states','best_pair_nonempty','elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
