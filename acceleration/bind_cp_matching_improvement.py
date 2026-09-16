"""Verify one strictly improving, independently pair-consistent shortlist seed.

The positive fixed-K bound still excludes this seed as a completion. Adopting
it means changing K in subsequent searches, not seeking a completion of this K.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

from audit_certificate import audit as audit_integer, require
from audit_phase1_kkt import inspect_artifact, exact_integer_certificate, rational
from audit_matching_accepted import check_matching_geometry


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def fraction(record):
    return Fraction(int(record['numerator']), int(record['denominator']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--search-audit', type=Path, required=True)
    parser.add_argument('--index', type=int, required=True)
    parser.add_argument('--previous-candidate', type=Path, required=True)
    parser.add_argument('--previous-phase1', type=Path, required=True)
    parser.add_argument('--pair-audit', type=Path, required=True)
    parser.add_argument('--pair-certificate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve prior adoption evidence')
    summary = json.loads(args.summary.read_bytes())
    require(summary['status'] == 'BOUNDED_CP_MATCHING_SEARCH_FINISHED', 'Incomplete shortlist')
    search_audit = json.loads(args.search_audit.read_bytes())
    require(search_audit['status'] == 'INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS', 'Search audit incomplete')
    require(search_audit['inputs_sha256'].get(args.summary.as_posix()) == digest(args.summary),
            'Search audit is not bound to this summary')
    for name, expected in search_audit['inputs_sha256'].items():
        require(digest(Path(name)) == expected, 'Changed search audit dependency')
    records = [row for row in summary['records'] if row['proposal_index'] == args.index]
    require(len(records) == 1, 'Missing or duplicate selected candidate')
    record = records[0]
    candidate_path, phase_path = Path(record['candidate_path']), Path(record['result_path'])
    require(digest(candidate_path) == record['candidate_sha256'] and digest(phase_path) == record['result_sha256'],
            'Changed shortlist candidate or LP')
    candidate, phase = (json.loads(path.read_bytes()) for path in (candidate_path, phase_path))
    previous = json.loads(args.previous_candidate.read_bytes())
    check_matching_geometry(set(map(tuple, previous['overlap_edges_outer_zero_based'])),
                            set(map(tuple, candidate['overlap_edges_outer_zero_based'])), record['move'])
    pair = json.loads(args.pair_audit.read_bytes())
    require(pair['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS'
            and pair['propagation_status'] == 'ARC_CONSISTENT_NONEMPTY'
            and pair['complete_used_domains_verified']
            and sorted(row['outer_vertex'] for row in pair['independently_reenumerated_domains']) == list(range(84)),
            'Not an independently complete nonempty pair closure')
    inputs = dict(pair['inputs_sha256'])
    require(inputs.get(str(candidate_path)) == digest(candidate_path)
            and inputs.get(str(args.pair_certificate)) == digest(args.pair_certificate), 'Different pair proof candidate')
    for name, expected in inputs.items():
        require(digest(Path(name)) == expected, 'Changed pair proof dependency')
    pairs = json.loads(args.pair_certificate.read_bytes())
    remaining = sum(len(row) for row in pairs['surviving_domain_ids'])
    old_audit = inspect_artifact(args.previous_candidate, args.previous_phase1)
    new_audit = inspect_artifact(candidate_path, phase_path)
    improvement = fraction(old_audit['exact_dual_lower_bound']) - fraction(new_audit['exact_primal_upper_bound'])
    require(improvement > 0, 'No strict exact improvement')
    require(fraction(new_audit['exact_dual_lower_bound']) > 0, 'This adoption bundle expects a positive fixed-K bound')
    cert = exact_integer_certificate(candidate, phase, digest(candidate_path))
    args.out.mkdir(parents=True)

    def save(name, data):
        path = args.out / name
        with path.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(data, indent=2, allow_nan=False) + '\n')
        inputs[str(path)] = digest(path)
        return path

    save('previous_phase1_audit.json', old_audit)
    save('new_phase1_audit.json', new_audit)
    cert_path = save('integer_certificate.json', cert)
    cert_audit = audit_integer(candidate_path, cert_path)
    require(cert_audit['status'] == 'INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS', 'Fixed-K integer proof failed')
    save('integer_certificate_audit.json', cert_audit)
    phase_copy = args.out / 'best_phase1.json'
    phase_copy.write_bytes(phase_path.read_bytes())
    inputs[str(phase_copy)] = digest(phase_copy)
    best_path = save('best_candidate.json', dict(overlap_edges_outer_zero_based=candidate['overlap_edges_outer_zero_based'],
                    numeric_phase1_objective=phase['numeric_objective'], original_candidate_path=str(candidate_path),
                    original_candidate_sha256=digest(candidate_path), original_phase1_path=str(phase_path),
                    original_phase1_sha256=digest(phase_path), pair_compatible_search_seed_only=True))
    sources = [args.summary, args.search_audit, args.previous_candidate, args.previous_phase1, candidate_path, phase_path,
               args.pair_audit, args.pair_certificate, Path(__file__)] + [Path(__file__).with_name(name) for name in
               ('audit_certificate.py', 'audit_phase1.py', 'audit_phase1_kkt.py', 'audit_matching_accepted.py')]
    inputs.update({str(path): digest(path) for path in sources})
    report = dict(status='INDEPENDENT_STRICT_MATCHING_MERIT_IMPROVEMENT_AND_COMPLETE_PAIR_CLOSURE_PASS',
                  original_candidate_path=str(candidate_path), original_candidate_sha256=digest(candidate_path),
                  best_candidate_path=str(best_path), best_candidate_sha256=digest(best_path),
                  numeric_objective=phase['numeric_objective'],
                  previous_exact_lower_bound=old_audit['exact_dual_lower_bound'],
                  best_exact_lower_bound=new_audit['exact_dual_lower_bound'],
                  best_exact_upper_bound=new_audit['exact_primal_upper_bound'],
                  guaranteed_merit_decrease=rational(improvement), move=record['move'],
                  complete_local_domains=84,
                  original_local_choices=sum(row['domain_size'] for row in pair['independently_reenumerated_domains']),
                  independently_verified_surviving_pair_choices=remaining, pair_deletions_checked=pair['events_verified'],
                  best_fixed_K_integer_certificate_rhs=cert['combined_rhs'], inputs_sha256=inputs,
                  full_graph_constructed=False, general_nonexistence_proved=False,
                  scope='A strictly better positive phase-I search seed with independently complete nonempty pair arc consistency. The same fixed K is still impossible by an independent integer certificate. Change overlap assignments further; no completion or general nonexistence theorem is claimed.')
    # Save last: do not insert this report's own hash into its input map.
    with (args.out / 'combined_evidence.json').open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('inputs_sha256', 'move')}))


if __name__ == '__main__':
    main()
