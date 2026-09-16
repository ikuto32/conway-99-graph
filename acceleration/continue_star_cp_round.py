"""Run one bounded, audited CP neighborhood from the current star-merit seed.

The old edge CP only selects candidates. Exact star intervals govern adoption.
Existing outputs are never overwritten, failed stages are never retried, and
pending completion cases prevent starting another round with this driver.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
A = ROOT/'acceleration'
PYTHON = ROOT/'.venv/Scripts/python.exe'
IMPORT_PINS = {
    'continue_cp_round.py': 'f8cd98d97f569beae91958ad1da7d803a45004179e7592e43fc8d543f493cb25',
    'build_cp_completion_checkpoint.py': '3ce94bbdd49f9a6f216bb87d2f75ee3e6e2ad6f24dea198c4d4a5b0ba08a5b4f',
    'evaluate_cp_star_shortlist_v2.py': '83cc10e42923ea5dfd6e39b81bee4ad19585539639045a03f9c812c97eac19ae',
    'build_star_guided_checkpoint.py': 'ff9b952e21e0ee569a93c0894e0a04c09b68d02e0c2e62daab47c3487263c242',
}
for _name, _expected in IMPORT_PINS.items():
    if sha256((A/_name).read_bytes()).hexdigest() != _expected:
        raise ValueError('Changed frozen helper: '+_name)

from continue_cp_round import FROZEN_SHA256, graph_signature
from build_cp_completion_checkpoint import Index, require, resolve, key, fraction
from evaluate_cp_star_shortlist_v2 import PINS, ROOT_PINS, digest, load, save

OBJECTIVE = 'STAR_SIMPLEX_RECIPROCITY_PLUS_LINEAR_CAP_VIOLATIONS'
CHECKPOINTS = {'HASH_VERIFIED_CP_COMPLETION_CHECKPOINT', 'HASH_VERIFIED_STAR_GUIDED_ROUND_CHECKPOINT',
               'HASH_VERIFIED_FIXED_STAR_DUAL_SHORTLIST_CHECKPOINT'}


def check_seed(previous, seed, warm, star_audit, replay, local):
    """Pure semantic controls; Index separately verifies every file binding."""
    require(previous['status'] in CHECKPOINTS, 'Unsupported checkpoint')
    require(previous['goal']['active'] is True and previous['goal']['complete'] is False and
            previous['graph_constructed'] is False and previous['general_nonexistence_proved'] is False and
            previous['submission_txt_exists'] is False, 'Goal state requires reassessment')
    require(previous.get('pending_completion_work') is None, 'Resolve pending completion work first')
    require(not previous.get('unselected_eligible_indices'), 'Previous near-zero shortlist is unfinished')
    current = previous['current_star_marginal_best']
    require(current['objective'] == OBJECTIVE and current['comparison_to_old_edge_merit'] is False,
            'Current merit is not the frozen star objective')
    lo, hi = fraction(current['exact_interval']['lower']), fraction(current['exact_interval']['upper'])
    require(0 < lo <= hi and star_audit['status'] == 'INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS' and
            star_audit['positive_exact_dual_excludes_fixed_K'] is True and
            fraction(star_audit['exact_dual_lower']) == lo and fraction(star_audit['exact_primal_upper']) == hi,
            'Current seed lacks positive exact star interval')
    require(replay['status'] == 'INDEPENDENT_INTEGER_STAR_MARGINAL_CERTIFICATE_REPLAY_PASS' and
            replay['fixed_K_excluded'] is True and int(replay['integer_scale']) > 0 and
            Fraction(int(replay['exact_integer_gap']), int(replay['integer_scale'])) == lo,
            'Current integer proof differs')
    require(key(warm['candidate_path']) == key(current['best_candidate_path']) and
            warm['candidate_sha256'] == current['best_candidate_sha256'], 'Edge warm start belongs to another K')
    graph_signature(seed)
    require(local['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and
            local['complete_used_domains_verified'] is True and local['propagation_status'] == 'ARC_CONSISTENT_NONEMPTY' and
            [r['outer_vertex'] for r in local['independently_reenumerated_domains']] == list(range(84)) and
            all(r['domain_size'] > 0 for r in local['independently_reenumerated_domains']),
            'Current seed lacks complete independent local domains')


def preflight(args):
    require(sys.version_info[:2] == (3, 12), 'Use workspace Python3.12')
    out = resolve(args.out)
    require(out.is_relative_to(ROOT) and out != ROOT and not out.exists(), 'Use a fresh workspace output directory')
    require(type(args.max_star_candidates) is int and 1 <= args.max_star_candidates <= 32, 'Invalid shortlist cap')
    require(args.kind in ('same', 'cross'), 'Invalid neighborhood kind')
    require(re.fullmatch('[0-9a-f]{64}', args.previous_sha256) is not None, 'Expected lowercase SHA256')
    require(not (ROOT/'submission.txt').exists(), 'Unexpected submission artifact')
    book = Index()
    book.bind(args.previous, args.previous_sha256)
    previous = book.read(args.previous)
    refs = previous['referenced_files_sha256']
    require(type(refs) is dict and len(refs) == previous['verified_referenced_file_count'] and refs,
            'Invalid checkpoint reference inventory')
    for name, expected in refs.items():
        require(type(expected) is str and re.fullmatch('[0-9a-f]{64}', expected) is not None,
                'Malformed checkpoint reference hash: '+str(name))
        book.bind(name, expected)
    normalized_refs = {key(p): h for p,h in refs.items()}
    require(len(normalized_refs) == len(refs), 'Ambiguous normalized reference names')
    current = previous['current_star_marginal_best']
    seed_path, warm_path = current['best_candidate_path'], current['edge_phase1_path']
    audit_path = current['star_audit_path']
    for field in ('best_candidate', 'edge_phase1', 'star_phase1', 'star_audit', 'star_certificate_replay', 'independent_pair_audit'):
        path, expected = current[field+'_path'], current[field+'_sha256']
        require(normalized_refs.get(key(path)) == expected, 'Current seed evidence is outside checkpoint: '+field)
        book.bind(path, expected)
    seed, warm = book.read(seed_path), book.read(warm_path)
    star_audit = book.read(audit_path)
    replay = book.read(current['star_certificate_replay_path'])
    local = book.read(current['independent_pair_audit_path'])
    check_seed(previous,seed,warm,star_audit,replay,local)
    for obj in (star_audit,replay,local):
        book.assert_bound(obj,seed_path)
    book.assert_bound(star_audit,current['star_phase1_path'])
    book.assert_bound(replay,star_audit['certificate_path'])
    pins = dict(FROZEN_SHA256)
    pins.update({'acceleration/'+n: h for n,h in PINS.items()})
    pins.update(ROOT_PINS)
    pins.update({'acceleration/'+n: h for n,h in IMPORT_PINS.items()})
    for name, expected in pins.items():
        book.bind(name,expected)
    pins[key(__file__)] = book.bind(__file__)
    pins[key(PYTHON)] = book.bind(PYTHON)
    priors = []
    for name in sorted(normalized_refs):
        if name.endswith('/summary.json'):
            summary = load(name)
            if summary.get('status') == 'BOUNDED_CP_MATCHING_SEARCH_FINISHED':
                book.read(name)
                require(len(summary['records']) == summary['probes'], 'Incomplete prior CP inventory')
                priors.append(name)
    require(priors, 'No bound previous CP records')
    inputs = dict(pins)
    for name in (args.previous,seed_path,warm_path,audit_path,*priors):
        inputs[key(name)] = book.bind(name)
    family, search = out/'family', out/'search'
    inp, native, proof = family/'input.txt', family/'all.json', family/'independent_audit.json'
    steps = []
    def add(stage, program, argv, result, status):
        program = A/program
        command = ([str(PYTHON),'-B',key(program)] if program.suffix == '.py' else [str(program)])+list(map(str,argv))
        steps.append(dict(stage=stage,command=command,result_path=key(result),expected_status=status))
    candidate = key(seed_path)
    if args.kind == 'same':
        add('native','build/overlap_matching_neighbors.exe',[key(inp),key(native),'all'],native,
            'COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION')
        add('family_audit','audit_whole_matching_family.py',['--candidate',candidate,'--input',key(inp),
            '--native',key(native),'--out',key(proof)],proof,'INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS')
        producer,auditor,audit_status = 'search_cp_matching_v2.py','audit_cp_matching_search_v2.py','INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS'
    else:
        atomic_proof = family/'atomic_audit.json'
        add('native','build/overlap_cycle_neighbors.exe',[key(inp),key(native),'both'],native,'COMPLETE_ATOMIC_CYCLE_SUBFAMILY_ENUMERATION')
        add('atomic_audit','audit_atomic_cycle_family.py',['--candidate',candidate,'--input',key(inp),'--native',key(native),
            '--out',key(atomic_proof)],atomic_proof,'INDEPENDENT_COMPLETE_ATOMIC_CYCLE_FAMILY_PASS')
        common = ['--candidate',candidate,'--native',key(native),'--family-audit',key(atomic_proof)]
        native = family/'cross.json'
        add('extract','extract_cross_atomic_family.py',[*common,'--out',key(native)],native,'COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION')
        add('cross_audit','audit_cross_atomic_extraction.py',[*common,'--adapted',key(native),'--out',key(proof)],proof,
            'INDEPENDENT_COMPLETE_CROSS_ATOMIC_CYCLE_EXTRACTION_PASS')
        producer,auditor,audit_status = 'search_cp_cross.py','audit_cp_cross_search.py','INDEPENDENT_CP_CROSS_SEARCH_AUDIT_PASS'
    argv = ['--native',key(native),'--family-audit',key(proof),'--initial',candidate,'--initial-phase1',key(warm_path),
        '--gpu','acceleration/build/overlap_cp_gpu_layout_v2.exe','--gpu-source','acceleration/overlap_cp_gpu_layout_v2.cu',
        '--gpu-audit','acceleration/results/20260916_cp_gpu_layout_v2_controls/audit.json','--out',key(search)]
    for prior in priors:
        argv += ['--previous-summary',prior]
    add('search',producer,argv,search/'summary.json','BOUNDED_CP_MATCHING_SEARCH_FINISHED')
    add('search_audit',auditor,['--run',key(search),'--out',key(search/'audit.json')],search/'audit.json',audit_status)
    manifest = dict(status='STAR_GUIDED_CP_NEIGHBORHOOD_MANIFEST',created_utc=datetime.now(timezone.utc).isoformat(),
        inputs_sha256=inputs,parent_checkpoint_path=key(args.previous),parent_checkpoint_sha256=args.previous_sha256,
        parent_reference_count=len(refs),initial_candidate_path=candidate,initial_candidate_sha256=book.bind(seed_path),
        initial_edge_phase1_path=key(warm_path),initial_edge_phase1_sha256=book.bind(warm_path),
        baseline_star_audit_path=key(audit_path),baseline_star_audit_sha256=book.bind(audit_path),
        kind='whole_same_sign_matching' if args.kind == 'same' else 'cross_single_3_4',previous_summaries=priors,steps=steps,
        seed_exactly_excluded=True,old_edge_CP_ranks_only=True,requires_new_star_objective_evaluation=True,
        max_star_candidates=args.max_star_candidates,goal_complete=False)
    followups = [
        dict(stage='star_evaluation',command=[str(PYTHON),'-B','acceleration/evaluate_cp_star_shortlist_v2.py','--run',key(search),
            '--baseline-star-audit',key(audit_path),'--out',key(out/'star_shortlist'),'--max-candidates',str(args.max_star_candidates)],
            result_path=key(out/'star_shortlist/summary.json'),expected_status='BOUNDED_CP_STAR_SHORTLIST_EVALUATION_FINISHED'),
        dict(stage='checkpoint',command=[str(PYTHON),'-B','acceleration/build_star_guided_checkpoint.py','--previous',key(args.previous),
            '--previous-sha256',args.previous_sha256,'--round',key(out),'--out',key(out/'checkpoint.json')],
            result_path=key(out/'checkpoint.json'),expected_status='HASH_VERIFIED_STAR_GUIDED_ROUND_CHECKPOINT')]
    return manifest,followups,seed,out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous',required=True)
    p.add_argument('--previous-sha256',required=True)
    p.add_argument('--kind',choices=('same','cross'),required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--max-star-candidates',type=int,default=32)
    p.add_argument('--validate-only',action='store_true')
    args = p.parse_args()
    manifest,followups,seed,out = preflight(args)
    if args.validate_only:
        print(json.dumps(dict(status='ONE_STAR_CP_ROUND_READ_ONLY_PREFLIGHT_PASS',manifest=manifest,followups=followups,
                              processes_launched=0,output_created=False)),flush=True)
        return
    out.mkdir(parents=True)
    (out/'family').mkdir(); (out/'logs').mkdir()
    save(out/'manifest.json',manifest)
    save(out/'followup_manifest.json',dict(status='ONE_STAR_CP_ROUND_FOLLOWUPS',steps=followups,
        inputs_sha256={key(out/'manifest.json'):digest(out/'manifest.json')}))
    with (out/'family/input.txt').open('x',encoding='ascii',newline='\n') as stream:
        stream.write('C99OVERLAPS1 1\n'+' '.join(str(v) for edge in sorted(seed['overlap_edges_outer_zero_based']) for v in edge)+'\n')
    records,active = [],None
    started = time.perf_counter()
    try:
        for order,step in enumerate(manifest['steps']+followups):
            active = step['stage']
            require(all(digest(n) == h for n,h in manifest['inputs_sha256'].items()), 'Input changed during run')
            require(not resolve(step['result_path']).exists(), 'Never overwrite a stage result')
            log = out/'logs'/f'{order:02d}_{active}.log'
            print(json.dumps(dict(stage=active,event='START')),flush=True)
            before = time.perf_counter()
            # Each invoked producer has its own finite caps; this is a hard outer ceiling.
            timeout = 3600 if active == 'star_evaluation' else 1800
            with log.open('x',encoding='utf-8') as stream:
                process = subprocess.run(step['command'],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,timeout=timeout)
            require(process.returncode == 0, active+' failed; preserve '+key(log))
            result = load(step['result_path'])
            require(result['status'] == step['expected_status'], 'Unexpected result status: '+active)
            row = dict(stage=active,result_path=step['result_path'],result_sha256=digest(step['result_path']),
                status=result['status'],log_path=key(log),log_sha256=digest(log),elapsed_seconds=time.perf_counter()-before)
            records.append(row)
            save(out/'logs'/f'{order:02d}_{active}_completed.json',row)
            print(json.dumps(dict(stage=active,event='FINISHED',elapsed_seconds=row['elapsed_seconds'])),flush=True)
            if order+1 == len(manifest['steps']):
                save(out/'run_result.json',dict(status='STAR_GUIDED_CP_NEIGHBORHOOD_FINISHED',
                    manifest_path=key(out/'manifest.json'),manifest_sha256=digest(out/'manifest.json'),records=list(records),goal_complete=False))
        checkpoint = load(out/'checkpoint.json')
        save(out/'completion.json',dict(status='ONE_STAR_CP_ROUND_FINISHED_GOAL_REMAINS_OPEN',records=records,
            inputs_sha256={key(out/'manifest.json'):digest(out/'manifest.json'),key(out/'followup_manifest.json'):digest(out/'followup_manifest.json')},
            checkpoint_path=key(out/'checkpoint.json'),checkpoint_sha256=digest(out/'checkpoint.json'),
            pending_completion_work=checkpoint['pending_completion_work'],unselected_eligible_indices=checkpoint['unselected_eligible_indices'],
            elapsed_seconds=time.perf_counter()-started,goal_marked_complete=False))
    except BaseException as exc:
        save(out/'failure.json',dict(status='ONE_STAR_CP_ROUND_STOPPED_PRESERVING_ARTIFACTS',stage=active,
            exception_type=type(exc).__name__,message=str(exc),completed_steps=records,retries=0,goal_marked_complete=False))
        raise


if __name__ == '__main__':
    main()
