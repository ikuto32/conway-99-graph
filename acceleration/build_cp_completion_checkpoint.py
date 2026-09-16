"""Hash-verified completion evidence index; no solve and no goal-state change."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def resolve(name):
    p = Path(str(name).replace('\\', '/'))
    if not p.is_absolute():
        p = ROOT/p
        if not p.exists() and len(Path(name).parts) == 1:
            p = ROOT/'acceleration'/name
    return p.resolve()


def key(name):
    p = resolve(name)
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()


def read_json(path):
    return json.loads(resolve(path).read_bytes())


def fraction(value):
    return Fraction(int(value['numerator']), int(value['denominator']))


class Index:
    def __init__(self):
        self.verified, self.direct, self.statuses, self.documents = {}, {}, {}, {}

    def bind(self, name, expected=None):
        label = key(name)
        if label not in self.verified:
            h = sha256()
            with resolve(name).open('rb') as stream:
                for block in iter(lambda: stream.read(1 << 20), b''):
                    h.update(block)
            self.verified[label] = h.hexdigest()
        require(expected is None or self.verified[label] == expected, 'Changed artifact: '+label)
        return self.verified[label]

    def bindings(self, data):
        if isinstance(data, dict):
            for field, value in data.items():
                if field.endswith('_sha256') and isinstance(value, dict) and value and all(
                        isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) for v in value.values()):
                    for p,h in value.items():
                        self.bind(p,h)
                elif field.endswith('_path') and isinstance(value,str) and isinstance(data.get(field[:-5]+'_sha256'),str):
                    self.bind(value,data[field[:-5]+'_sha256'])
                self.bindings(value)
        elif isinstance(data,list):
            for value in data:
                self.bindings(value)

    def read(self, path, status=None):
        name = key(path)
        if name not in self.documents:
            self.documents[name] = read_json(path)
            self.bindings(self.documents[name])
            self.direct[name] = self.bind(path)
            if isinstance(self.documents[name],dict) and 'status' in self.documents[name]:
                self.statuses[name] = self.documents[name]['status']
        obj = self.documents[name]
        require(status is None or obj.get('status') == status, 'Unexpected status: '+name)
        return obj

    def assert_bound(self, report, path):
        declared = {key(p):h for p,h in report['inputs_sha256'].items()}
        require(declared.get(key(path)) == self.bind(path), 'Report does not bind '+key(path))


def check_case_semantics(index, candidate_path, candidate_sha, row, report, made, mapped, sat, produced, drat, local):
    """Pure association checks; cryptographic file checks belong to Index."""
    require(row['proposal_index'] == report['proposal_index'] == index, 'CP index association differs')
    require(key(row['candidate_path']) == key(report['candidate_path']) == key(candidate_path) and
            row['candidate_sha256'] == candidate_sha, 'CP candidate association differs')
    require(key(report['result_path']) == key(row['result_path']), 'CP result association differs')
    exact = report['phase1_audit']
    require(fraction(exact['exact_dual_lower_bound']) <= 0 and 0 <= fraction(exact['exact_primal_upper_bound']) <= Fraction(1,100000000),
            'Candidate is outside the audited near-zero selection')
    require(made['candidate_sha256'] == mapped['candidate_sha256'] == produced['candidate_sha256'] == drat['candidate_sha256'] == candidate_sha and
            all(key(obj['candidate_path']) == key(candidate_path) for obj in (made,mapped,produced,drat)), 'Fixed-K candidate association differs')
    require(made['cnf_sha256'] == mapped['cnf_sha256'] == produced['cnf_sha256'] == drat['cnf_sha256'] and
            all(key(obj['cnf_path']) == key(made['cnf_path']) for obj in (mapped,produced,drat)), 'Fixed CNF association differs')
    require(sat['status'] == 'UNSAT_UNVERIFIED' and sat['validated_witness'] is None and
            sat['fixed_K_excluded_by_this_run'] is False, 'Original SAT outcome is not unverified UNSAT')
    require(produced['status'] == 'UNSAT_PROOF_UNCHECKED' and produced['verified'] is False and
            produced['solver_record']['proof_created'] is True and
            produced['solver_record']['native_proof_finalized_before_read'] is True and
            produced['solver_record']['terminal_empty_clause_synthesized'] is False, 'Untrusted or incomplete proof production')
    require(drat['status'] == 'DRAT_VERIFIED' and drat['verified'] is True and drat['return_code'] == 0 and
            's VERIFIED' in drat['transcript'].splitlines() and drat['mapping_rechecked'] is True and
            drat['fixed_K_excluded_by_verified_CNF'] is True and drat['general_nonexistence_proved'] is False,
            'DRAT contradiction was not independently verified')
    require(produced['proof_sha256'] == drat['proof_sha256'] and key(produced['proof_path']) == key(drat['proof_path']), 'Verified proof differs from generated proof')
    require(local['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and local['propagation_status'] == 'ARC_CONSISTENT_NONEMPTY' and
            local['complete_used_domains_verified'] is True and local['producer_or_solver_imported'] is False and
            len(local['independently_reenumerated_domains']) == 84 and
            {r['outer_vertex'] for r in local['independently_reenumerated_domains']} == set(range(84)), 'Complete independent local closure absent')


def inspect_case(book, index, cnf_dir, sat_dir, drat_dir, local_dir):
    cnf_dir,sat_dir,drat_dir,local_dir = map(resolve,(cnf_dir,sat_dir,drat_dir,local_dir))
    made = book.read(cnf_dir/'manifest.json','FIXED_OVERLAP_CNF_ADAPTER_COMPLETE')
    candidate_path = resolve(made['candidate_path']); candidate_sha = book.bind(candidate_path,made['candidate_sha256'])
    search_dir = candidate_path.parent.parent
    search = book.read(search_dir/'summary.json','BOUNDED_CP_MATCHING_SEARCH_FINISHED')
    audit = book.read(search_dir/'audit.json')
    require(audit['status'] in ('INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS','INDEPENDENT_CP_CROSS_SEARCH_AUDIT_PASS'), 'CP independent audit absent')
    book.assert_bound(audit,search_dir/'summary.json')
    rows = [r for r in search['records'] if r['proposal_index'] == index]
    reports = [r for r in audit['probe_reports'] if r['proposal_index'] == index]
    require(len(rows) == len(reports) == 1, 'CP index missing/duplicated')
    row,report = rows[0],reports[0]
    book.assert_bound(audit,candidate_path);book.assert_bound(audit,row['result_path'])
    book.bind(row['result_path'],row['result_sha256'])
    mapped = book.read(cnf_dir/'independent_audit.json','INDEPENDENT_FIXED_OVERLAP_CNF_MAPPING_AUDIT_PASS')
    sat = book.read(sat_dir/'result.json','UNSAT_UNVERIFIED')
    produced = book.read(drat_dir/'proof_generation.json','UNSAT_PROOF_UNCHECKED')
    drat = book.read(drat_dir/'independent_drat_audit.json','DRAT_VERIFIED')
    local = book.read(local_dir/'independent_pair_audit.json','INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS')
    for evidence in (mapped,sat,produced,drat):
        book.assert_bound(evidence,cnf_dir/'manifest.json')
        book.assert_bound(evidence,candidate_path)
        book.assert_bound(evidence,made['cnf_path'])
    for evidence in (sat,produced,drat):
        book.assert_bound(evidence,cnf_dir/'independent_audit.json')
    book.assert_bound(drat,produced['proof_path'])
    require(resolve(sat['manifest_path']) == cnf_dir/'manifest.json' and resolve(sat['audit_path']) == cnf_dir/'independent_audit.json', 'SAT references another fixed CNF')
    for name in (candidate_path,local_dir/'stars.json',local_dir/'pairs.json'):
        book.assert_bound(local,name)
    pairs = book.read(local_dir/'pairs.json','EXACT_PAIR_DOMAIN_ARC_CONSISTENT_NONEMPTY')
    require(pairs['propagation_status'] == 'ARC_CONSISTENT_NONEMPTY' and len(pairs['surviving_domain_ids']) == 84 and
            all(pairs['surviving_domain_ids']), 'Native local witness inventory differs')
    check_case_semantics(index,candidate_path,candidate_sha,row,report,made,mapped,sat,produced,drat,local)
    candidate = book.read(candidate_path)
    signature = tuple(sorted(map(tuple,candidate['overlap_edges_outer_zero_based'])))
    require(len(signature) == len(set(signature)) == 168, 'Invalid candidate edge signature')
    record = dict(proposal_index=index, candidate_path=key(candidate_path),candidate_sha256=candidate_sha,
        search_audit_path=key(search_dir/'audit.json'),search_audit_sha256=book.bind(search_dir/'audit.json'),
        exact_LP_interval={k:report['phase1_audit'][k] for k in ('exact_dual_lower_bound','exact_primal_upper_bound')},
        exact_LP_feasibility_proved=False, cnf_manifest_path=key(cnf_dir/'manifest.json'),cnf_manifest_sha256=book.bind(cnf_dir/'manifest.json'),
        cnf_path=made['cnf_path'],cnf_sha256=made['cnf_sha256'],sat_result_path=key(sat_dir/'result.json'),sat_result_sha256=book.bind(sat_dir/'result.json'),
        proof_generation_path=key(drat_dir/'proof_generation.json'),proof_generation_sha256=book.bind(drat_dir/'proof_generation.json'),
        proof_path=produced['proof_path'],proof_sha256=produced['proof_sha256'],drat_audit_path=key(drat_dir/'independent_drat_audit.json'),
        drat_audit_sha256=book.bind(drat_dir/'independent_drat_audit.json'),independent_pair_audit_path=key(local_dir/'independent_pair_audit.json'),
        independent_pair_audit_sha256=book.bind(local_dir/'independent_pair_audit.json'),
        original_star_choices=sum(r['domain_size'] for r in local['independently_reenumerated_domains']),
        surviving_pair_choices=sum(map(len,pairs['surviving_domain_ids'])),independent_pair_events=local['events_verified'],
        full_pair_AC_nonempty=True, fixed_K_DRAT_verified=True)
    return record,signature


def inspect_star_frontier(book, summary_path, replay_path, completion_manifest, cases):
    summary = book.read(summary_path,'BOUNDED_STAR_MARGINAL_SHORTLIST_FINISHED')
    manifest = book.read(summary['manifest_path'],'STAR_MARGINAL_SHORTLIST_MANIFEST')
    replay_summary = book.read(replay_path,'NINE_STAR_MARGINAL_INTEGER_CERTIFICATES_AND_EXACT_INTERVAL_COMPARISON_PASS')
    baseline = book.read(manifest['baseline_audit_path'],'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS')
    book.assert_bound(baseline,cases[0]['candidate_path'])
    book.assert_bound(baseline,cases[0]['independent_pair_audit_path'])
    require(manifest['baseline_exact_lower'] == baseline['exact_dual_lower'] == replay_summary['baseline_exact_lower'] and
            baseline['positive_exact_dual_excludes_fixed_K'] is True and fraction(baseline['exact_dual_lower']) > 0,
            'Star baseline exact bound differs')
    selected = {r['proposal_index']:r for r in completion_manifest['selected_candidates']}
    rows = {r['proposal_index']:r for r in summary['records']}
    replays = {r['proposal_index']:r for r in replay_summary['records']}
    require(len(rows) == len(summary['records']) == len(replays) == len(replay_summary['records']) == 9 and
            set(rows) == set(replays) == set(selected) and manifest['candidates'] == completion_manifest['selected_candidates'],
            'Star study candidate inventory differs')
    by_index = {r['proposal_index']:r for r in cases}
    improved = []
    for index,row in rows.items():
        replay_row = replays[index]; original = selected[index]; case = by_index[index]
        require(row['candidate_sha256'] == replay_row['candidate_sha256'] == original['candidate_sha256'] == case['candidate_sha256'] and
                key(row['candidate_path']) == key(replay_row['candidate_path']) == key(original['candidate_path']),
                'Star study changes candidate association')
        result = book.read(row['result_path'])
        audit = book.read(row['audit_path'],'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS')
        replay = book.read(replay_row['replay_path'],'INDEPENDENT_INTEGER_STAR_MARGINAL_CERTIFICATE_REPLAY_PASS')
        certificate = book.read(replay_row['certificate_path'])
        book.assert_bound(audit,row['result_path']);book.assert_bound(audit,row['candidate_path'])
        book.assert_bound(audit,case['independent_pair_audit_path'])
        book.assert_bound(replay,replay_row['certificate_path']);book.assert_bound(replay,row['candidate_path'])
        require(key(audit['certificate_path']) == key(replay_row['certificate_path']) and
                audit['certificate_sha256'] == replay_row['certificate_sha256'] and
                row['audit_sha256'] == replay_row['audit_sha256'] and key(row['audit_path']) == key(replay_row['audit_path']),
                'Star certificate/audit/replay association differs')
        require(row['exact_lower'] == replay_row['exact_lower'] == audit['exact_dual_lower'] and
                row['exact_upper'] == replay_row['exact_upper'] == audit['exact_primal_upper'] and
                fraction(audit['exact_dual_lower']) == Fraction(int(replay['exact_integer_gap']),int(replay['integer_scale'])) > 0 and
                audit['positive_exact_dual_excludes_fixed_K'] is True and replay['fixed_K_excluded'] is True,
                'Star exact arithmetic claims differ')
        margin = fraction(baseline['exact_dual_lower']) - fraction(audit['exact_primal_upper'])
        require(row['exact_strict_improvement'] is (margin > 0) and replay_row['exact_strict_improvement'] is (margin > 0) and
                fraction(replay_row['guaranteed_improvement']) == margin, 'Star strict-improvement claim differs')
        if margin > 0:
            improved.append(index)
    best_index = min(rows,key=lambda i:(fraction(rows[i]['exact_upper']),i))
    best,verified_best = rows[best_index],replays[best_index]
    require(summary['best'] == best and replay_summary['best'] == verified_best and
            summary['exact_strict_improvement_count'] == replay_summary['exact_strict_improvement_count'] == len(improved) and
            all(fraction(best['exact_upper']) < fraction(row['exact_lower']) for i,row in rows.items() if i != best_index),
            'Star best interval is not strictly best among nine')
    require(best_index in improved and replay_summary['all_nine_fixed_K_certificates_positive'] is True,
            'No verified star-objective progress')
    return dict(objective=manifest['merit'],comparison_to_old_edge_merit=False,proposal_index=best_index,
        best_candidate_path=best['candidate_path'],best_candidate_sha256=best['candidate_sha256'],
        star_phase1_path=best['result_path'],star_phase1_sha256=best['result_sha256'],
        star_audit_path=best['audit_path'],star_audit_sha256=best['audit_sha256'],
        star_certificate_replay_path=verified_best['replay_path'],star_certificate_replay_sha256=verified_best['replay_sha256'],
        edge_phase1_path=selected[best_index]['phase1_path'],edge_phase1_sha256=selected[best_index]['phase1_sha256'],
        exact_interval=dict(lower=best['exact_lower'],upper=best['exact_upper']),
        baseline_candidate_path=cases[0]['candidate_path'],baseline_candidate_sha256=cases[0]['candidate_sha256'],
        baseline_audit_path=manifest['baseline_audit_path'],baseline_audit_sha256=manifest['baseline_audit_sha256'],
        baseline_exact_lower=baseline['exact_dual_lower'],guaranteed_improvement=verified_best['guaranteed_improvement'],
        all_other_shortlist_lower_bounds_exceed_best_upper=True,exact_strict_improvement_count=len(improved),
        all_nine_fixed_K_also_excluded_by_star_certificate=True,positive_merit_seed_still_excluded=True,
        independent_pair_audit_path=by_index[best_index]['independent_pair_audit_path'],
        independent_pair_audit_sha256=by_index[best_index]['independent_pair_audit_sha256'],graph_completion=False)


def build(args):
    book = Index();book.bind(args.previous,args.previous_sha256)
    previous = book.read(args.previous)
    require(previous['goal']['active'] is True and previous['goal']['complete'] is False and
            previous['graph_constructed'] is False and previous['general_nonexistence_proved'] is False, 'Goal state requires reassessment')
    zero,neighborhood = resolve(args.zero_root),resolve(args.neighborhood)
    completion = neighborhood/'completion'
    records,signatures = [],[]
    for index in (226,2700):
        record,sig = inspect_case(book,index,zero/f'cnf_{index}',zero/f'sat_{index}',zero/f'drat_{index}',zero/f'local_{index}')
        records.append(record);signatures.append(sig)
    manifest = book.read(completion/'manifest.json','CP_COMPLETION_INVESTIGATION_MANIFEST')
    summary = book.read(completion/'summary.json','BOUNDED_CP_COMPLETION_INVESTIGATIONS_FINISHED')
    batch_manifest = book.read(completion/'drat_batch_manifest.json','EXACT_CP_COMPLETION_DRAT_BATCH_MANIFEST')
    batch = book.read(completion/'drat_batch_summary.json','BOUNDED_CP_COMPLETION_DRAT_BATCH_FINISHED')
    local_summary = book.read(completion/'local_audits_summary.json','NINE_LOCAL_AUDITS_RECORDED')
    expected = [r['proposal_index'] for r in manifest['selected_candidates']]
    require(len(expected) == len(set(expected)) == manifest['eligible_candidates'] == 9, 'Wrong expected neighborhood inventory')
    require([r['proposal_index'] for r in summary['completed']] == [r['proposal_index'] for r in batch_manifest['records']] ==
            [r['proposal_index'] for r in batch['records']] == expected and
            set(r['index'] for r in local_summary['records']) == set(expected), 'Batch inventories differ')
    require(batch['fixed_K_DRAT_verified'] == 9 and batch['unresolved_candidates'] == 0 and
            all(r['status'] == 'DRAT_VERIFIED' and r['verified'] is True for r in batch['records']), 'Not all expected contradictions are verified')
    require(key(summary['manifest_path']) == key(completion/'manifest.json') and
            key(batch['manifest_path']) == key(completion/'drat_batch_manifest.json') and
            key(local_summary['manifest_path']) == key(completion/'manifest.json'), 'Batch manifest linkage differs')
    require(batch_manifest['selection_reconstructed_from_exact_audit'] is True and
            [dict((k,r[k]) for k in manifest['selected_candidates'][0]) for r in batch_manifest['records']] == manifest['selected_candidates'],
            'Selection reconstruction or candidate/interval association differs')
    for index in expected:
        base = completion/f'index_{index}'
        record,sig = inspect_case(book,index,base/'cnf',base/'sat',base/'drat',base/'local')
        selected = next(r for r in manifest['selected_candidates'] if r['proposal_index'] == index)
        bound = next(r for r in batch['records'] if r['proposal_index'] == index)
        local_record = next(r for r in local_summary['records'] if r['index'] == index)
        require(record['candidate_sha256'] == selected['candidate_sha256'] == bound['candidate_sha256'] and
                key(record['candidate_path']) == key(selected['candidate_path']) == key(bound['candidate_path']) and
                record['drat_audit_sha256'] == bound['audit_sha256'] and
                record['independent_pair_audit_sha256'] == local_record['audit_sha256'], 'Neighborhood result association differs')
        records.append(record);signatures.append(sig)
    require(len(set(signatures)) == 11, 'Fixed-K exclusions are not11 distinct labeled graphs')
    pending = previous['pending_completion_work']
    require(pending is not None and pending['proposal_index'] == 226 and key(pending['candidate_path']) == records[0]['candidate_path'], 'Previous pending work is not the verified226 case')
    pivot = book.read(neighborhood/'pivot_manifest.json','BOUNDED_NUMERICAL_ZERO_SEED_NEIGHBORHOOD_PLAN')
    book.assert_bound(pivot,args.previous);book.assert_bound(pivot,records[0]['candidate_path'])
    family = book.read(neighborhood/'family/independent_audit.json','INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS')
    search = book.read(neighborhood/'search/summary.json','BOUNDED_CP_MATCHING_SEARCH_FINISHED')
    search_audit = book.read(neighborhood/'search/audit.json','INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS')
    book.assert_bound(search_audit,neighborhood/'family/independent_audit.json')
    require(search['coarse_candidate_count'] == family['legal_count'] == search_audit['coarse_candidates'], 'Neighborhood family count differs')
    star_best = inspect_star_frontier(book,args.star_summary,args.star_replays,manifest,records)
    for path in args.extra_report:
        book.read(path)
    book.direct[key(Path(__file__))] = book.bind(Path(__file__))
    require(not (ROOT/'submission.txt').exists(), 'Unexpected submission file')
    return dict(status='HASH_VERIFIED_CP_COMPLETION_CHECKPOINT',created_utc=datetime.now(timezone.utc).isoformat(),
        goal=previous['goal'],current_best=previous['current_best'],current_star_marginal_best=star_best,
        graph_constructed=False,general_nonexistence_proved=False,
        submission_txt_exists=False,previous_checkpoint_preserved=dict(path=key(args.previous),sha256=book.bind(args.previous)),
        pending_completion_work=None,previous_pending_completion_resolved=dict(**pending,resolution='FIXED_K_DRAT_VERIFIED',
            drat_audit_path=records[0]['drat_audit_path'],drat_audit_sha256=records[0]['drat_audit_sha256']),
        fixed_K_DRAT_verified_count=11,distinct_labeled_fixed_K_count=11,all11_complete_pair_AC_nonempty=True,
        fixed_K_records=records,neighborhood_complete_same_sign_finals=family['legal_count'],
        neighborhood_LP_artifacts=search['probes'],neighborhood_near_zero_completed=9,
        exact_LP_feasibility_of_near_zero_candidates_proved=False,positive_merit_seed_preserved=True,
        exclusion_scope='11 individual labeled E0 fixed-K instances, relative to the frozen unrestricted CNF encoding and independently checked DRAT proofs.',
        next_focus='Stronger star-marginal necessary constraints or objective; current LP and pair AC can both pass impossible fixed K.',
        limits=dict(full_E0_or_Conway_coverage=False,general_nonexistence=False,all_family_LP_optimized=False,graph_witness=False),
        direct_artifacts_sha256=book.direct,report_statuses=book.statuses,referenced_files_sha256=book.verified,
        verified_referenced_file_count=len(book.verified),indexing_only_no_solver_or_domain_reruns=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous',type=Path,required=True)
    parser.add_argument('--previous-sha256',required=True)
    parser.add_argument('--zero-root',type=Path,required=True)
    parser.add_argument('--neighborhood',type=Path,required=True)
    parser.add_argument('--star-summary',type=Path,required=True)
    parser.add_argument('--star-replays',type=Path,required=True)
    parser.add_argument('--extra-report',type=Path,action='append',default=[])
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--validate-only',action='store_true')
    args = parser.parse_args();require(not args.out.exists(),'Preserve previous index')
    result = build(args)
    if not args.validate_only:
        with args.out.open('x',encoding='utf-8') as stream:
            stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status=result['status'],verified_files=result['verified_referenced_file_count'],
                         fixed_K_DRAT_verified=result['fixed_K_DRAT_verified_count'],output_created=not args.validate_only)),flush=True)


if __name__ == '__main__':
    main()
