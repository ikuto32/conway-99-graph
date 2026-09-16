"""Bind prior fixed-K exact LP and complete pair evidence to an identical MIP K."""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

from audit_certificate import full_graph, require

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--prior-evidence', type=Path, required=True)
    parser.add_argument('--prior-evidence-sha256', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve prior evidence binding')
    hashes = {}
    parsed = {}

    def bind(path, expected=None):
        path = Path(path).resolve()
        raw = path.read_bytes()
        actual = sha256(raw).hexdigest()
        require(expected is None or actual == expected, 'Changed proof dependency: '+str(path))
        key = path.relative_to(ROOT).as_posix()
        if key in hashes:
            require(hashes[key] == actual, 'Dependency changed during audit')
            return parsed.get(key)
        hashes[key] = actual
        if path.suffix != '.json':
            return None
        data = json.loads(raw)
        parsed[key] = data
        if isinstance(data, dict):
            for field in ('inputs_sha256', 'files_sha256', 'sources_sha256', 'source_sha256'):
                for name, digest in data.get(field, {}).items():
                    candidate = Path(name)
                    # Old phase-I artifacts use basename source names.
                    if not candidate.exists() and candidate.name == str(candidate):
                        candidate = ROOT/'acceleration'/candidate
                    bind(candidate, digest)
        return data

    prior = bind(args.prior_evidence, args.prior_evidence_sha256.lower())
    require(prior['status'] == 'INDEPENDENT_TWO_TRADE_BEST_LOCAL_PASS_GLOBAL_OBSTRUCTION_BOUND', 'Wrong prior evidence status')
    old = bind(prior['candidate_path'], prior['candidate_sha256'])
    candidate_path = args.run/'candidate.json'
    current = bind(candidate_path)
    candidate_audit = bind(args.run/'candidate_independent_audit.json')
    require(candidate_audit['status'] == 'INDEPENDENT_WHOLE_MATCHING_CANDIDATE_AND_RETURNED_MERIT_AUDIT_PASS',
            'Current candidate audit is not PASS')
    pair = bind(args.run/'pair_identity_audit.json')
    require(pair['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and
            pair['evidence_method'] == 'PRIOR_INDEPENDENT_PROOF_PLUS_EXACT_LABELED_GRAPH_IDENTITY' and
            pair['complete_used_domains_verified'] is True and pair['propagation_status'] == 'ARC_CONSISTENT_NONEMPTY',
            'Current pair identity evidence is not a complete nonempty closure')
    require(Path(pair['current_candidate_path']).resolve() == candidate_path.resolve(), 'Pair identity bound to wrong current candidate')
    old_rows, old_unknown = full_graph(old)
    new_rows, new_unknown = full_graph(current)
    require(sorted(map(tuple, old['overlap_edges_outer_zero_based'])) == sorted(map(tuple, current['overlap_edges_outer_zero_based']))
            and old_rows == new_rows and old_unknown == new_unknown, 'Prior evidence transfer requires identical labeled graph')
    lower = prior['best_exact_lower_bound']
    require(Fraction(int(lower['numerator']), int(lower['denominator'])) > 0, 'Prior exact LP lower bound is not positive')
    certificate_audits = [data for data in parsed.values() if isinstance(data, dict) and
                          data.get('status') == 'INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS']
    require(any(data['combined_rhs'] == prior['best_integer_certificate_rhs'] < 0 for data in certificate_audits),
            'Bound prior integer Farkas proof missing')
    bind(Path(__file__))
    bind(ROOT/'acceleration/audit_certificate.py')
    result = {'status': 'INDEPENDENT_IDENTICAL_MATCHING_CANDIDATE_PRIOR_PHASE1_AND_PAIR_EVIDENCE_BOUND',
              'candidate_path': candidate_path.as_posix(), 'candidate_sha256': sha256(candidate_path.read_bytes()).hexdigest(),
              'prior_evidence_path': args.prior_evidence.as_posix(), 'prior_evidence_sha256': args.prior_evidence_sha256.lower(),
              'identical168_overlap_edges': True, 'identical99_partial_adjacency': True,
              'identical1680_unknown_edges': True, 'same_exact_fixed_K_phase1_optimum': True,
              'prior_exact_lower_bound': prior['best_exact_lower_bound'], 'prior_exact_upper_bound': prior['best_exact_upper_bound'],
              'prior_integer_certificate_rhs': prior['best_integer_certificate_rhs'],
              'all84_complete_domains_and_nonempty_exact_pair_closure_reused_by_identity': True,
              'new_fixed_K_LP_solves': 0, 'new_native_domain_runs': 0, 'new_certificate_replays': 0,
              'files_sha256': hashes, 'proof_dependencies_checked': len(hashes), 'producer_or_solver_imported': False,
              'scope': 'Reuse of immutable independently audited fixed-K LP obstruction and complete pair closure, justified by exact labeled graph and variable-universe equality. The MIP changed no overlap graph; its time limit/bound/gap gives no new optimality proof. No new enumeration or global Conway nonexistence is claimed.'}
    args.out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'files_sha256'}))


if __name__ == '__main__':
    main()
