"""Run the existing complete-star/pair gate on one saved shortlist candidate.

This records native necessary-condition checks, not independent evidence or
a completion witness. Capped checks stay unavailable and are not exclusions.
"""
import argparse
import json
from pathlib import Path
import subprocess
import time

from audit_certificate import full_graph, require
from guided_overlap import digest, write_input, invoke
from prepare import path_key

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve prior gate record')
    candidate = json.loads(args.candidate.read_bytes())
    full_graph(candidate)
    args.out.mkdir(parents=True)
    stars_exe = ROOT / 'acceleration/build/star_domains.exe'
    pairs_exe = ROOT / 'acceleration/build/pair_domains.exe'
    sources = [args.candidate, Path(__file__), stars_exe, pairs_exe] + [ROOT / 'acceleration' / name for name in
               ('audit_certificate.py', 'guided_overlap.py', 'prepare.py', 'star_domains.rs', 'pair_domains.rs')]
    bindings = {path_key(path): digest(path) for path in sources}
    started = time.perf_counter()
    candidate_input = args.out / 'candidate.txt'
    stars_path = args.out / 'stars.json'
    write_input(candidate_input, [candidate['overlap_edges_outer_zero_based']])
    stars = invoke(stars_exe, candidate_input, stars_path, 30, 2000000, 20000)
    report = dict(status='NATIVE_SHORTLIST_PAIR_GATE_FINISHED', passed=False,
                  candidate_path=path_key(args.candidate), candidate_sha256=digest(args.candidate),
                  star_status=stars['status'], inputs_sha256=bindings,
                  files_sha256={path_key(path): digest(path) for path in (candidate_input, stars_path)})
    if stars['status'] == 'COMPLETE_DOMAINS_RECIPROCITY_ARC_CONSISTENT_NONEMPTY':
        domains_path, pairs_path = args.out / 'domains.txt', args.out / 'pairs.json'
        domains_path.write_text('C99DOMAINS1 84\n' + ''.join(str(len(row['domain_masks_hex'])) + ' ' +
            ' '.join(row['domain_masks_hex']) + '\n' for row in stars['domains']), encoding='ascii')
        process = subprocess.run([str(pairs_exe), str(candidate_input), str(domains_path), str(pairs_path),
                                  '30', '500000000'], text=True, capture_output=True, timeout=40)
        require(process.returncode == 0, 'Native pair process failed: ' + process.stderr)
        pairs = json.loads(pairs_path.read_bytes())
        report.update(pair_status=pairs['status'], passed=pairs['status'] == 'EXACT_PAIR_DOMAIN_ARC_CONSISTENT_NONEMPTY',
                      remaining_choices=sum(len(row) for row in pairs['surviving_domain_ids']))
        report['files_sha256'].update({path_key(path): digest(path) for path in (domains_path, pairs_path)})
    for path in sources:
        require(digest(path) == bindings[path_key(path)], 'Source changed during native gate')
    report.update(elapsed_seconds=time.perf_counter()-started,
                  scope='Native complete-domain/pair necessary-condition gate only. Independent reenumeration is still required. No graph completion, exact exclusion from caps, or general proof is claimed.')
    with (args.out / 'gate.json').open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('inputs_sha256', 'files_sha256')}))


if __name__ == '__main__':
    main()
