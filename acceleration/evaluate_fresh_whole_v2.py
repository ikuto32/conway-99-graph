"""Original-star shortlist evaluation for audited whole-family fresh v2 ranking.

No cross-family relabeling or original-domain flag conversion is used.
The ranking auditor path/hash is supplied explicitly and bound before execution.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import re
import subprocess
import sys
import time

import evaluate_fresh_star_shortlist as shared
from audit_certificate import full_graph
ROOT=shared.ROOT
PINS=dict(shared.PINS)
PINS['evaluate_fresh_star_shortlist.py']='affa5acf237e46b4c82c0ce867c56bb4ec6336d367dde2cd79ab3b23872d9ae5'
ROOT_PINS=shared.ROOT_PINS
require,resolve,key,digest,load,save=shared.require,shared.resolve,shared.key,shared.digest,shared.load,shared.save
number,rational,normalized=shared.number,shared.rational,shared.normalized
complete_pair_evidence,checked_star_interval=shared.complete_pair_evidence,shared.checked_star_interval
compare_original_domains,restart_choice,check_edge_warm=shared.compare_original_domains,shared.restart_choice,shared.check_edge_warm
evaluation_selection,graph_key=shared.evaluation_selection,shared.graph_key
OBJECTIVE='ORIGINAL_STAR_SIMPLEX_PDHG_V1'
RANKING_AUDIT_STATUS='INDEPENDENT_WHOLE_FRESH_STAR_PDHG_RANKING_AUDIT_PASS'

def select_records(audit,family,count,mode):
    require(audit['status']==RANKING_AUDIT_STATUS and
        audit['producer_or_native_imported'] is False and audit['all_serialized_models_reconstructed'] is True and
        audit['independent_domain_enumeration_performed'] is False,'Fresh independent ranking audit required')
    require(count==16 and type(count) is int and mode=='union','Frozen whole-v2 union16 selection required')
    require(family['status']=='COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION' and family['selector']=='all','Honest whole family required')
    n=family['legal_count']
    require(n==len(family['overlap_candidates'])==len(family['moves']),'Incomplete family inventory')
    rows=audit['records'];indices=[r['proposal_index'] for r in rows]
    require(len(indices)==len(set(indices)) and all(type(i) is int and 0<=i<n for i in indices),'Invalid attempted ranking indices')
    require(all(type(r.get('original_native_index')) is int and r['original_native_index']==r['proposal_index'] for r in rows),'Whole family native ID must equal original row')
    available=[]
    for row in rows:
        require(type(row['available']) is bool,'Invalid availability flag')
        if row['available']:
            require(all(type(row[k]) in (int,float) and isfinite(row[k]) for k in ('best_upper_numeric','best_lower_numeric')),
                'Nonfinite ranked score')
            require(row['best_upper_numeric']>=-1e-10 and row['best_lower_numeric']<=row['best_upper_numeric']+1e-7,
                'Inconsistent heuristic interval')
            available.append(row)
        else:
            require(row['best_upper_numeric'] is None and row['best_lower_numeric'] is None,'Unavailable candidate received a score')
    upper=[r['proposal_index'] for r in sorted(available,key=lambda r:(r['best_upper_numeric'],r['proposal_index']))]
    lower=[r['proposal_index'] for r in sorted(available,key=lambda r:(r['best_lower_numeric'],r['proposal_index']))]
    controls=audit['numeric_cpu_controls']
    require(len(controls)==min(3,len(available)) and len({r['proposal_index'] for r in controls})==len(controls) and
        all(r['proposal_index'] in upper for r in controls),'Independent numerical CPU replay coverage required')
    require(upper==audit['ranked_by_upper_indices'] and lower==audit['ranked_by_lower_indices'],'Fresh numerical ranking order differs')
    selected=evaluation_selection(upper,lower,count,mode)
    require(audit['evaluation_selections'][f'{mode}_{count}']==selected,'Independent downstream selection differs')
    return selected,upper,lower,[r['proposal_index'] for r in rows if not r['available']]

def verify_whole_records(ranking,audit,family):
    require(ranking['status']=='NUMERICAL_WHOLE_FRESH_STAR_PDHG_RANKING_FINISHED' and
        ranking['producer_version']=='whole_fresh_v2_balanced' and ranking['objective_id']==OBJECTIVE,
        'Whole balanced ranking header differs')
    require(ranking['original_complete_domains_used'] is True and ranking['pair_pruned_domains_used'] is False and
        ranking['independently_audited_original_domains'] is False,'Wrong ranked original-domain scope')
    require(family['status']=='COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION' and
        family['selector']=='all','Wrong whole-family scope')
    indices=ranking['input_selected_indices']
    require(indices==audit['input_selected_indices']==[r['proposal_index'] for r in ranking['records']]
        ==[r['proposal_index'] for r in audit['records']] and len(indices)==len(set(indices)),
        'Ranking/audit attempted inventory mismatch')
    for numerical,checked in zip(ranking['records'],audit['records']):
        i=numerical['proposal_index']
        require(type(i) is int and 0<=i<family['legal_count'] and type(numerical['original_native_index']) is int and
                type(checked['original_native_index']) is int and numerical['original_native_index']==checked['original_native_index']==i,
                'Whole native row identity differs')
        move=family['moves'][i]
        require(move['matching_class'] in ('same_0','same_1') and type(move['root_group']) is int and 0<=move['root_group']<7,
                'Wrong whole matching coordinate')
        expected=dict(root_group=move['root_group'],matching_class=move['matching_class'],
            changed_edges=move['changed_edges'],alternating_cycle_sizes=sorted(len(c)//2 for c in move['alternating_cycles']))
        require(sum(expected['alternating_cycle_sizes'])==expected['changed_edges'] and
            2<=expected['changed_edges']<=6 and all(n>=2 for n in expected['alternating_cycle_sizes']),
            'Invalid full alternating-cycle geometry')
        require(all(numerical.get(name)==value for name,value in expected.items()),'Whole multiple-cycle metadata differs')
        for name in ('candidate_path','candidate_sha256','domains_path','domains_sha256','best_upper_numeric','best_lower_numeric'):
            require(numerical[name]==checked[name],'Independent whole ranking record differs: '+name)
        require((numerical['status']=='NUMERICALLY_SCORED')==checked['available'],'Availability differs')


def preflight(args):
    require(sys.version_info[:2]==(3,12),'Use workspace Python3.12')
    out=resolve(args.out)
    require(out.is_relative_to(ROOT) and out!=ROOT and not out.exists(),'Use a fresh workspace output')
    require(type(args.max_candidates) is int and args.max_candidates==16 and args.selection=='union' and
        isfinite(args.seconds) and 0<args.seconds<=3600 and isfinite(args.audit_seconds) and 0<args.audit_seconds<=3600,
        'Invalid finite evaluation limits')
    require(type(args.ranking_auditor_sha256) is str and re.fullmatch('[0-9a-f]{64}',args.ranking_auditor_sha256),
        'Independent ranking auditor is not yet frozen')
    inputs={}
    def bind(name,expected=None):
        label=key(name)
        if label not in inputs:inputs[label]=digest(name)
        require(expected is None or inputs[label]==expected,'Changed dependency: '+label)
        return inputs[label]
    def read(name):
        bind(name);data=load(name)
        for p,h in data.get('inputs_sha256',{}).items():
            require(type(h) is str and re.fullmatch('[0-9a-f]{64}',h),'Malformed declared input hash')
            bind(p,h)
        return data
    for name,h in PINS.items():bind(ROOT/'acceleration'/name,h)
    for name,h in ROOT_PINS.items():bind(ROOT/name,h)
    auditor_path=resolve(args.ranking_auditor)
    bind(auditor_path,args.ranking_auditor_sha256);bind(Path(__file__))
    ranking=read(args.ranking);audit=read(args.ranking_audit)
    require(ranking['status']=='NUMERICAL_WHOLE_FRESH_STAR_PDHG_RANKING_FINISHED' and ranking['producer_version']=='whole_fresh_v2_balanced' and ranking['objective_id']==OBJECTIVE,'Whole balanced ranking/objective required')
    require(ranking['original_complete_domains_used'] is True and ranking['pair_pruned_domains_used'] is False and ranking['independently_audited_original_domains'] is False,'Original native domains required; completeness still needs later independent enumeration')
    audit_inputs=normalized(audit['inputs_sha256'])
    require(key(audit['ranking_summary_path'])==key(args.ranking) and audit['ranking_summary_sha256']==bind(args.ranking) and
        audit_inputs.get(key(args.ranking))==bind(args.ranking) and audit_inputs.get(key(auditor_path))==args.ranking_auditor_sha256,
        'Independent ranking report association differs')
    family_path,family_audit_path=audit['family_path'],audit['family_audit_path']
    bind(family_path,audit['family_sha256']);bind(family_audit_path,audit['family_audit_sha256'])
    require(audit_inputs.get(key(family_path))==bind(family_path) and audit_inputs.get(key(family_audit_path))==bind(family_audit_path),
        'Independent ranking family binding differs')
    family,family_audit=read(family_path),read(family_audit_path)
    require(family_audit['status']=='INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS' and family_audit['legal_count']==family['legal_count'] and
        normalized(family_audit['inputs_sha256']).get(key(family_path))==bind(family_path),'Complete family proof differs')
    selection,upper,lower,unavailable=select_records(audit,family,args.max_candidates,args.selection)
    verify_whole_records(ranking,audit,family)
    rows={r['proposal_index']:r for r in audit['records']}
    baseline=read(args.baseline_star_audit)
    require(baseline['status']=='INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS' and baseline['positive_exact_dual_excludes_fixed_K'] is True,
        'Positive exact star baseline required')
    lo,hi=number(baseline['exact_dual_lower']),number(baseline['exact_primal_upper'])
    require(0<lo<=hi,'Invalid exact star baseline interval')
    cert=read(baseline['certificate_path']);bind(baseline['certificate_path'],baseline['certificate_sha256'])
    require(cert['fixed_K_excluded'] is True and number(cert['exact_phase1_lower_bound'])==lo,'Baseline certificate differs')
    baseline_inputs=normalized(baseline['inputs_sha256'])
    for name in ('star_marginal_phase1.py','audit_star_marginal_phase1.py'):
        require(baseline_inputs.get(key(ROOT/'acceleration'/name))==PINS[name],'Baseline star objective differs')
    chosen=[]
    for selection_row in selection:
        i=selection_row['proposal_index'];row=rows[i]
        for field in ('candidate','domains'):
            p,h=row[field+'_path'],row[field+'_sha256']
            require(audit_inputs.get(key(p))==h,'Selected ranking evidence is outside independent audit')
            bind(p,h)
        candidate=load(row['candidate_path']);domains=load(row['domains_path'])
        require(graph_key(candidate['overlap_edges_outer_zero_based'])==graph_key(family['overlap_candidates'][i]),
            'Ranking candidate is not the selected family graph')
        full_graph(candidate)
        require(domains['complete_domain_enumeration'] is True and len(domains['domains'])==84 and
            all(r['domain_masks_hex'] for r in domains['domains']),'Available ranking lacks all original domains')
        chosen.append(dict(**selection_row,candidate_path=key(row['candidate_path']),candidate_sha256=row['candidate_sha256'],
            ranking_domains_path=key(row['domains_path']),ranking_domains_sha256=row['domains_sha256'],
            original_native_index=i,root_group=family['moves'][i]['root_group'],matching_class=family['moves'][i]['matching_class'],changed_edges=family['moves'][i]['changed_edges'],alternating_cycle_sizes=sorted(len(c)//2 for c in family['moves'][i]['alternating_cycles']),
            best_upper_numeric=row['best_upper_numeric'],best_lower_numeric=row['best_lower_numeric'],
            upper_rank=upper.index(i)+1,lower_rank=lower.index(i)+1))
    require(all(digest(p)==h for p,h in inputs.items()),'Input changed during preflight')
    return dict(status='WHOLE_FRESH_STAR_SHORTLIST_EVALUATION_MANIFEST_V2',objective_id=OBJECTIVE,original_complete_domains_used=True,pair_pruned_domains_used=False,ranking_auditor_path=key(auditor_path),ranking_auditor_sha256=bind(auditor_path),inputs_sha256=inputs,
        ranking_path=key(args.ranking),ranking_sha256=bind(args.ranking),ranking_audit_path=key(args.ranking_audit),
        ranking_audit_sha256=bind(args.ranking_audit),family_path=key(family_path),family_sha256=bind(family_path),
        family_audit_path=key(family_audit_path),family_audit_sha256=bind(family_audit_path),family_legal_candidates=family['legal_count'],
        ranking_attempted_candidates=len(audit['records']),eligible_candidates=len(upper),selected_candidates=chosen,
        max_candidates=args.max_candidates,selection_mode=args.selection,
        unselected_ranked_indices=[i for i in upper if i not in {r['proposal_index'] for r in chosen}],
        unavailable_ranking_indices=unavailable,baseline_star_audit_path=key(args.baseline_star_audit),
        baseline_star_audit_sha256=bind(args.baseline_star_audit),baseline_exact_lower=rational(lo),baseline_exact_upper=rational(hi),
        ranking_baseline_need_not_equal_comparison_baseline=True,numerical_scores_are_certificates=False,
        original_domain_set_identity_required=True,CP_nearzero_eligibility_assumed=False,
        native_star_seconds=30,native_star_node_cap=2000000,native_star_domain_cap=20000,
        native_pair_seconds=30,native_pair_check_cap=500000000,independent_pair_seconds=args.audit_seconds,
        per_star_LP_seconds=args.seconds,per_restart_edge_LP_seconds=args.seconds,
        subprocess_wall_seconds=180+max(args.seconds,args.audit_seconds),
        merit='STAR_SIMPLEX_RECIPROCITY_PLUS_LINEAR_CAP_VIOLATIONS',old_edge_merit_comparison=False,
        edge_warm_policy='Only best independently positive strict star improver; precise producer and unchanged1e-7 audit. Failure/cap remains pending restart.',
        exact_edge_LP_feasibility_claimed=False,SAT_or_DRAT_invocations=0,graph_constructed=False,general_nonexistence_proved=False)

def execute(args,manifest):
    out = resolve(args.out); out.mkdir(parents=True, exist_ok=False)
    save(out/'manifest.json', manifest)
    records, steps, output_hashes = [], [], {}
    started, active = time.perf_counter(), None
    source_bindings = {key(ROOT/'acceleration'/p): h for p, h in PINS.items()}
    source_bindings.update({key(ROOT/p): h for p, h in ROOT_PINS.items()})
    source_bindings[key(Path(__file__))] = manifest['inputs_sha256'][key(Path(__file__))]
    def collect(name, status=None):
        data = load(name)
        require(status is None or data['status'] == status, 'Unexpected output status: '+key(name))
        output_hashes[key(name)] = digest(name)
        for field in ('inputs_sha256', 'files_sha256'):
            for p, expected in data.get(field, {}).items():
                require(digest(p) == expected, 'Output dependency changed: '+key(p))
                output_hashes[key(p)] = expected
        return data
    def execute(script, arguments, result_path, logfile, allow_failure=False):
        require(all(digest(p) == h for p, h in source_bindings.items()), 'Pinned source changed')
        with logfile.open('x', encoding='utf-8') as stream:
            try:
                result = subprocess.run([sys.executable, '-B', str(ROOT/'acceleration'/script)]+arguments,
                    cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=manifest['subprocess_wall_seconds'], check=False)
                code=result.returncode
            except subprocess.TimeoutExpired:
                if not allow_failure:
                    raise
                stream.write('\nPENDING_RESTART_SUBPROCESS_TIMEOUT\n');code=None
        output_hashes[key(logfile)] = digest(logfile)
        if code != 0:
            require(allow_failure,script+' failed; inspect '+key(logfile))
            steps.append(dict(stage=script,status='PENDING_RESTART_PROCESS_FAILURE_OR_CAP',return_code=code,
                log_path=key(logfile),log_sha256=digest(logfile)))
            if result_path.exists():
                output_hashes[key(result_path)]=digest(result_path)
            return None
        data = collect(result_path)
        steps.append(dict(stage=script, result_path=key(result_path), result_sha256=digest(result_path),
            log_path=key(logfile), log_sha256=digest(logfile)))
        return data
    try:
        for chosen in manifest['selected_candidates']:
            active = chosen['proposal_index']; directory = out/f'index_{active}'; directory.mkdir()
            row = dict(**{k:v for k,v in chosen.items() if k != 'candidate_document'}, audited=False, fixed_K_excluded=False, exact_strict_improvement=False,
                       status='PENDING_LOCAL_EVIDENCE',edge_LP_status='NOT_EVALUATED_UNLESS_STRICT_BEST')
            records.append(row)
            print(json.dumps(dict(index=active, event='START')), flush=True)
            require(digest(chosen['candidate_path']) == chosen['candidate_sha256'], 'Selected input changed')
            local = directory/'local'
            gate = execute('check_shortlist_native_pair.py', ['--candidate', chosen['candidate_path'], '--out', key(local)],
                           local/'gate.json', directory/'01_native.log')
            require(gate['status'] == 'NATIVE_SHORTLIST_PAIR_GATE_FINISHED' and
                    key(gate['candidate_path']) == chosen['candidate_path'] and gate['candidate_sha256'] == chosen['candidate_sha256'],
                    'Native gate input differs')
            row.update(gate_path=key(local/'gate.json'), gate_sha256=digest(local/'gate.json'), native_passed=gate['passed'])
            if not gate['passed']:
                row.update(status='PENDING_NATIVE_GATE_FAILED_OR_CAPPED', reason='Native outcomes alone give no independent exclusion')
                continue
            pair_path = local/'independent_pair_audit.json'
            pair = execute('audit_goal_theory_pairs.py', ['--candidate', chosen['candidate_path'], '--domains', key(local/'stars.json'),
                '--pair-certificate', key(local/'pairs.json'), '--out', key(pair_path), '--seconds', str(args.audit_seconds)],
                pair_path, directory/'02_pair_audit.log')
            row.update(independent_pair_audit_path=key(pair_path), independent_pair_audit_sha256=digest(pair_path))
            if pair['status'] != 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS':
                require(pair['status'] in ('INCOMPLETE_PAIR_SEARCH_NO_EXCLUSION', 'INCOMPLETE_PAIR_AUDIT_NO_EXCLUSION'),
                        'Unexpected independent pair result')
                row.update(status='PENDING_INCOMPLETE_INDEPENDENT_PAIR_AUDIT'); continue
            complete_pair_evidence(pair, chosen, local/'stars.json')
            ranking_stars = load(chosen['ranking_domains_path'])
            fresh_stars = load(local/'stars.json')
            compare_original_domains(ranking_stars, fresh_stars, pair)
            row.update(original84_domain_sets_equal_ranking=True, ranking_domain_audit_independent=True)
            result_path = directory/'phase1.json'
            result = execute('star_marginal_phase1.py', ['--candidate', chosen['candidate_path'], '--domains', key(local/'stars.json'),
                '--domain-audit', key(pair_path), '--out', key(result_path), '--seconds', str(args.seconds)],
                result_path, directory/'03_star_lp.log')
            require(key(result['candidate_path']) == chosen['candidate_path'] and result['candidate_sha256'] == chosen['candidate_sha256']
                    and key(result['domains_path']) == key(local/'stars.json') and key(result['domain_audit_path']) == key(pair_path),
                    'Star LP input differs')
            row.update(result_path=key(result_path), result_sha256=digest(result_path), numerical_status=result['status'])
            if not all(k in result for k in ('numeric_probabilities', 'numeric_cap_duals', 'numeric_reciprocity_duals')):
                row.update(status='PENDING_NO_STAR_PRIMAL_DUAL'); continue
            audit_path, cert_path, replay_path = directory/'audit.json', directory/'integer_certificate.json', directory/'replay.json'
            audit = execute('audit_star_marginal_phase1.py', ['--result', key(result_path), '--out', key(audit_path),
                '--certificate-out', key(cert_path)], audit_path, directory/'04_star_audit.log')
            require(key(audit['certificate_path']) == key(cert_path) and audit['certificate_sha256'] == digest(cert_path),
                    'Certificate association differs')
            collect(cert_path)
            audit_map = normalized(audit['inputs_sha256'])
            require(audit_map.get(key(result_path)) == digest(result_path) and
                    audit_map.get(chosen['candidate_path']) == chosen['candidate_sha256'], 'Star audit association differs')
            replay = execute('verify_star_marginal_certificate.py', ['--candidate', chosen['candidate_path'], '--domains', key(local/'stars.json'),
                '--domain-audit', key(pair_path), '--certificate', key(cert_path), '--out', key(replay_path)],
                replay_path, directory/'05_integer_replay.log')
            lo, hi = checked_star_interval(audit, replay)
            row.update(status='FIXED_K_EXCLUDED_EXACT_STAR_CERTIFICATE' if lo > 0 else 'PENDING_NONPOSITIVE_EXACT_STAR_BOUND',
                audited=True, fixed_K_excluded=lo > 0, exact_lower=rational(lo), exact_upper=rational(hi),
                audit_path=key(audit_path), audit_sha256=digest(audit_path), certificate_path=key(cert_path), certificate_sha256=digest(cert_path),
                replay_path=key(replay_path), replay_sha256=digest(replay_path),
                exact_strict_improvement=hi < number(manifest['baseline_exact_lower']),
                guaranteed_improvement=rational(number(manifest['baseline_exact_lower'])-hi))
            print(json.dumps(dict(index=active, status=row['status'], star_lower=float(lo), star_upper=float(hi))), flush=True)
        # Edge merit is not a selection or exclusion condition here. One fresh
        # strict audit supplies a usable restart state only after star proof.
        restart = restart_choice(records,number(manifest['baseline_exact_lower']))
        restart_seed,pending_restart,edge_runs=None,None,0
        if restart is not None:
            active=restart['proposal_index'];directory=out/f'index_{active}'
            edge_path,edge_audit_path=directory/'edge_phase1.json',directory/'edge_phase1_audit.json'
            edge_runs=1
            edge=execute('phase1_probe_precise.py',['--input',restart['candidate_path'],'--out',key(edge_path),
                '--seconds',str(args.seconds)],edge_path,directory/'06_edge_warm.log',allow_failure=True)
            pending_restart=dict(proposal_index=active,status='PENDING_EDGE_WARM_RESULT_OR_STRICT_AUDIT',
                candidate_path=restart['candidate_path'],candidate_sha256=restart['candidate_sha256'])
            restart['edge_LP_status']='PENDING_EDGE_WARM_RESULT_OR_STRICT_AUDIT'
            if edge is not None:
                require(key(edge['candidate_path'])==restart['candidate_path'] and edge['candidate_sha256']==restart['candidate_sha256'],
                    'Edge warm input differs from strict star improver')
                restart.update(edge_phase1_path=key(edge_path),edge_phase1_sha256=digest(edge_path))
                if edge.get('optimal') is True and all(k in edge for k in ('numeric_edge_values','phase1_multipliers')):
                    edge_audit=execute('audit_phase1_kkt.py',['--candidate',restart['candidate_path'],'--phase1',key(edge_path),
                        '--out',key(edge_audit_path)],edge_audit_path,directory/'07_edge_warm_audit.log',allow_failure=True)
                    if edge_audit is not None:
                        check_edge_warm(restart,edge,edge_audit,edge_path)
                        restart.update(edge_LP_status='STRICTLY_AUDITED_RESTART_WARM',edge_phase1_audit_path=key(edge_audit_path),
                            edge_phase1_audit_sha256=digest(edge_audit_path))
                        restart_seed=dict(restart);pending_restart=None
        require(all(digest(p) == h for p, h in {**manifest['inputs_sha256'], **output_hashes}.items()), 'Bound evidence changed during evaluation')
        audited = sorted((r for r in records if r['audited']), key=lambda r: (number(r['exact_upper']), r['proposal_index']))
        save(out/'summary.json', dict(status='BOUNDED_WHOLE_FRESH_STAR_SHORTLIST_EVALUATION_FINISHED',objective_id=OBJECTIVE, manifest_path=key(out/'manifest.json'),
            manifest_sha256=digest(out/'manifest.json'), inputs_sha256=manifest['inputs_sha256'], outputs_sha256=output_hashes,
            records=records, completed_steps=steps, best=audited[0] if audited else None,
            best_interval_strictly_below_other_audited_intervals=bool(audited) and all(number(audited[0]['exact_upper']) < number(r['exact_lower']) for r in audited[1:]),
            pending_candidates=[r for r in records if not r['fixed_K_excluded']], unselected_ranked_indices=manifest['unselected_ranked_indices'],
            exact_fixed_K_exclusions=sum(r['fixed_K_excluded'] for r in records),
            exact_strict_improvement_count=sum(r['exact_strict_improvement'] for r in records),
            elapsed_seconds=time.perf_counter()-started, SAT_or_DRAT_invocations=0, graph_constructed=False,
            general_nonexistence_proved=False, goal_marked_complete=False,
            native_scores_are_exclusion_certificates=False, CP_nearzero_eligibility_assumed=False,
            edge_LP_runs=edge_runs,restart_seed=restart_seed,pending_restart=pending_restart,
            scope='Only selected fixed K. Fresh numerical PDHG scores rank only; every star bound uses84 independently complete domains exactly equal to ranking input domains and fresh integer replay. Caps and nonpositive bounds remain pending. Only the best positive strict star improver is eligible for an audited edge warm start.'))
    except BaseException as exc:
        save(out/'failure.json', dict(status='WHOLE_FRESH_STAR_SHORTLIST_EVALUATION_STOPPED', active_index=active,
            error_type=type(exc).__name__, message=str(exc), records=records, completed_steps=steps,
            outputs_sha256=output_hashes, no_exclusion_from_failure=True, graph_constructed=False))
        raise


def argument_parser():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ranking',type=Path,required=True)
    parser.add_argument('--ranking-audit',type=Path,required=True)
    parser.add_argument('--ranking-auditor',type=Path,required=True)
    parser.add_argument('--ranking-auditor-sha256',required=True,
        help='Explicit immutable source pin for the independent whole-ranking checker; report must bind it.')
    parser.add_argument('--baseline-star-audit',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--max-candidates',type=int,default=16,choices=(16,))
    parser.add_argument('--selection',choices=('union',),default='union')
    parser.add_argument('--seconds',type=float,default=30)
    parser.add_argument('--audit-seconds',type=float,default=60)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--validate-only',action='store_true')
    mode.add_argument('--execute',action='store_true')
    return parser


def main():
    args=argument_parser().parse_args()
    manifest=preflight(args)
    if args.validate_only:
        print(json.dumps(dict(status='WHOLE_FRESH_STAR_SHORTLIST_READ_ONLY_PREFLIGHT_PASS',
            eligible=manifest['eligible_candidates'],selected=len(manifest['selected_candidates']),
            selected_indices=[r['proposal_index'] for r in manifest['selected_candidates']],
            original_complete_domains_used=True,pair_pruned_domains_used=False,
            output_created=False,processes_launched=0)))
        return
    execute(args,manifest)


if __name__=='__main__':main()
