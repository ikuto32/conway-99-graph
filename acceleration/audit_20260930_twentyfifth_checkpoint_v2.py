"""Independent wave25 checkpoint, replay-CLI and recovery consistency audit.

Reads frozen data only. Does not import producers, the checkpoint writer,
cataloguer, restorer or scientific checkers; does not launch native programs.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import argparse
import ast
import copy
import hashlib
import json
import re
import shlex
import sys
import time
import zlib
import yaml

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'
CP = B + 'resume/twentyfifth_milestone_checkpoint.json'
SNAP = B + 'resume/claims_at_twentyfifth_milestone.yaml'
GUIDE = 'docs/REPRODUCING_20260930_TWENTYFIFTH_WAVE.md'
REPORT = 'docs/RESEARCH_20260930_TWENTYFIFTH_WAVE.md'
MANIFEST = B + 'twentyfifth_raw_recovery/manifest.json'
BLOCKED = B + 'independent_review/hadamard_oriented_unknown/process.stdout.log'
PINS = {
    CP: '450671e692b6074b73f99c9138208b206c5b6ab3918c9385dfdff57f80ece873',
    SNAP: '82e03975b3e6eb109a0fb9c82746475a253763d1620d543e8938fec561d3cd77',
    MANIFEST: '695d61b39c466660cb854377800dd036362739a4bd03ffc200bf6e35873ea45b',
    'acceleration/recover_20260930_twentyfifth_raw_artifacts.py': 'bfdb92ae56e008907fea9f0bee9d24e7ac2b6b0af9dcf235ec227b4c959b6a56',
}
REGS = ['profile', 'scalar', 'direct_encoding', 'unknown', 'lex_cuts', 'final']
RUNS = [
    ('count_master_eight_orbit_cut_native_pilot', 'count_master_eight_orbit_cut_sat_outcome', 10, 'SATISFIABLE'),
    ('count_master_partial_cuts_native_pilot', 'count_master_partial_cut_sat_outcome', 10, 'SATISFIABLE'),
    ('eight_count_profile_lift_second_native_pilot', 'second_eight_count_profile_unsat', 20, 'UNSATISFIABLE'),
    ('direct_cell_standalone_native_pilot', 'direct_cell_standalone_unknown_v2', 0, None),
    ('direct_cell_count_coupled_native_pilot', 'direct_cell_count_coupled_unknown_v2', 124, 'UNKNOWN'),
    ('direct_cell_lex_standalone_native_pilot', 'direct_cell_lex_standalone_unknown', 124, 'UNKNOWN'),
    ('direct_cell_lex_coupled_native_pilot', 'direct_cell_lex_coupled_unknown', 124, 'UNKNOWN'),
]
INPUTS = {}


def require(test, message):
    if not test:
        raise ValueError(message)


def path(p):
    p = str(p).replace('\\', '/')
    require(p != BLOCKED and 'PROMPT.md' not in p and not p.startswith('tools/'), 'protected path')
    q = (ROOT / p).resolve()
    require(q.is_relative_to(ROOT), 'path escapes repository')
    return q


def digest(p):
    q = path(p)
    with q.open('rb') as f:
        h = hashlib.file_digest(f, 'sha256').hexdigest()
    INPUTS[q.relative_to(ROOT).as_posix()] = h
    return h


def load(p):
    digest(p)
    return json.loads(path(p).read_bytes())


def bind(mapping):
    for p, expected in mapping.items():
        require(digest(p) == expected, 'hash mismatch: ' + p)


def write(p, obj):
    with p.open('x', encoding='utf8', newline='\n') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def validate_checkpoint(c, new_claims):
    require(c['claim_population'] == 267 and c['claim_status_counts'] == {'VERIFIED': 262, 'CANDIDATE': 3, 'REFUTED': 2}, 'claim totals')
    require(c['claim_review_counts'] == {'CLEAR': 267}, 'review totals')
    require(set(c['new_verified_ids']) == {x['id'] for x in new_claims if x['status'] == 'VERIFIED'}, 'new verified IDs')
    require(set(c['new_candidate_ids']) == {x['id'] for x in new_claims if x['status'] == 'CANDIDATE'}, 'new candidate IDs')
    require(c['new_refuted_ids'] == [] and len(c['new_verified_ids']) == 18 and len(c['new_candidate_ids']) == 1, 'new status counts')
    require(c['count_search']['SAT'] == 2 and c['count_search']['attempted'] == 2 and len(set(c['count_search']['unique_profile_digests'])) == 2, 'count witnesses')
    require(c['literal_gram_lift']['UNSAT'] == 1 and c['literal_gram_lift']['proof_bytes'] == 1269209, 'literal proof count')
    require(c['direct_cell_search']['UNKNOWN'] == 4 and c['direct_cell_search']['SAT'] == c['direct_cell_search']['UNSAT'] == 0, 'UNKNOWN counts')
    require(c['partial_trace_transport'] == dict(host_streams=4, raw_bytes=1848656911, gzip_parts=222, complete_unsat_proofs=0), 'partial trace scope')
    require(c['target_resolution'] == 'UNKNOWN' and c['external_review'] is None, 'target/external conclusion')
    require(all(c[k] == 0 for k in ['new_full_factors', 'new_complete99_graphs', 'new_whole_support_exclusions', 'new_unrestricted_exclusions']), 'unsupported conclusion')
    require(c['third_count']['full_factor'] is False and c['third_count']['upper_envelope_failures'] == 0, 'count vs factor')


def decode_member(raw):
    dec = zlib.decompressobj(16 + zlib.MAX_WBITS)
    result = dec.decompress(raw) + dec.flush()
    require(dec.eof and not dec.unused_data and not dec.unconsumed_tail, 'gzip member completeness')
    return result


def recover_check(record):
    original = path(record['path'])
    total = hashlib.sha256()
    offset = 0
    with original.open('rb') as f:
        for part in record['parts']:
            require(part['raw_offset'] == offset, 'part offset/order')
            require(path(part['path']).stat().st_size == part['gzip_bytes'] <= 10 * 1024**2, 'gzip size')
            require(digest(part['path']) == part['gzip_sha256'], 'gzip hash')
            data = decode_member(path(part['path']).read_bytes())
            require(len(data) == part['raw_bytes'] and hashlib.sha256(data).hexdigest() == part['raw_sha256'], 'raw part identity')
            require(f.read(len(data)) == data, 'literal original byte comparison')
            total.update(data)
            offset += len(data)
        require(not f.read(1), 'original tail')
    require(offset == record['bytes'] and total.hexdigest() == record['sha256'], 'whole original identity')
    INPUTS[record['path']] = total.hexdigest()
    return dict(path=record['path'], bytes=offset, sha256=total.hexdigest(), gzip_parts=len(record['parts']), literal_original_equal=True)


def cli_check(text):
    records = []
    lines = [s for s in text.splitlines() if s.startswith('uv run ') and ' python -B acceleration/' in s]
    for line in lines:
        args = shlex.split(line)
        pos = args.index('-B')
        script, argv = args[pos + 1], args[pos + 2:]
        digest(script)
        tree = ast.parse(path(script).read_text(encoding='utf8'))
        names, required, modes = set(), set(), set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                if isinstance(value, ast.Dict):
                    modes.update(k.value for k in value.keys if isinstance(k, ast.Constant) and isinstance(k.value, str))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'add_argument' and node.args:
                name = node.args[0]
                if isinstance(name, ast.Constant) and isinstance(name.value, str):
                    names.add(name.value)
                    if any(k.arg == 'required' and isinstance(k.value, ast.Constant) and k.value.value is True for k in node.keywords):
                        required.add(name.value)
        options = {x for x in argv if x.startswith('--')}
        require(options <= names and required <= options, 'CLI option/required mismatch: ' + script)
        if 'mode' in names:
            require(argv and argv[0] in modes, 'CLI submode mismatch')
        for i, token in enumerate(argv):
            if token in ('--out', '--receipt'):
                require(argv[i+1].startswith('build/replay-wave25-') or argv[i+1] == 'build/wave25-recovery.json', 'nonfresh replay output')
        records.append(dict(script=script, argv=argv, static_cli_match=True, executed=False))
    require(len(records) == 13, 'expected guide command population')
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    try:
        bind(PINS)
        bind({
            'acceleration/audit_20260930_twentyfifth_checkpoint.py': '7ec3b65f67611919cf82ea377c862cc89a8676363fba9eddd29e2b45762cfa2a',
            'acceleration/results/20260930_independent_review/twentyfifth_checkpoint/failure.json': 'a5cd11d38bd4ed3869c0c960056a22a9270885fd8118a5a58faa3e7bffcb4820'
        })
        for p in [__file__, str(Path(__file__).with_name(Path(__file__).stem + '_spec.md'))]:
            digest(Path(p).relative_to(ROOT).as_posix())
        c = load(CP)
        bind(c['evidence_sha256'])
        digest(REPORT)
        digest(GUIDE)
        digest('acceleration/record_20260930_twentyfifth_checkpoint.py')
        require(INPUTS['acceleration/record_20260930_twentyfifth_checkpoint.py'] == c['writer_sha256'], 'writer identity')
        oldp = B + 'resume/claims_at_twentyfourth_milestone.yaml'
        digest(oldp)
        old = yaml.safe_load(path(oldp).read_bytes())
        final = yaml.safe_load(path(SNAP).read_bytes())
        oldclaims = {x['id']: x for x in old['claims']}
        claims = {x['id']: x for x in final['claims']}
        require(len(oldclaims) == 248 and len(claims) == 267, 'distinct claim population')
        require(all(claims.get(k) == v for k, v in oldclaims.items()), 'old claim changed')
        first_before = B + 'twentyfifth_profile_registration/CLAIMS.before.yaml'
        digest(first_before)
        initial = yaml.safe_load(path(first_before).read_bytes())
        require(set(initial) == set(old), 'pre-wave root key set')
        require(all(initial[k] == old[k] for k in old if k not in ('updated_at', 'artifacts')), 'pre-wave nonpublication mutation')
        oa, ia = [{v['id']:v for v in doc['artifacts']} for doc in (old, initial)]
        require(set(oa) == set(ia), 'pre-wave artifact population')
        publication_changes = []
        for key in oa:
            if oa[key] != ia[key]:
                require(set(oa[key]) == set(ia[key]) and all(oa[key][f] == ia[key][f] for f in oa[key] if f not in ('availability','retrieval','unavailable_reason')), 'pre-wave artifact content mutation')
                require(oa[key]['availability'] == 'LOCAL_ONLY' and ia[key]['availability'] == 'PUBLIC' and ia[key]['unavailable_reason'] is None, 'pre-wave availability direction')
                require(ia[key]['retrieval'] == 'https://github.com/ikuto32/conway-99-graph/blob/bc8a3462003f3095efe6c96e5023b9d17cfcd5d3/' + ia[key]['path'], 'pre-wave publication retrieval')
                publication_changes.append(key)
        require(len(publication_changes) == 38, 'pre-wave publication population')
        prior_bytes = path(first_before).read_bytes()
        chain, newids = [], []
        for name in REGS:
            d = B + 'twentyfifth_' + name + '_registration/'
            receipt = load(d + 'summary.json')
            before, after = d + 'CLAIMS.before.yaml', d + 'CLAIMS.after.yaml'
            bind({before: receipt['previous_ledger_sha256'], after: receipt['ledger_sha256']})
            require(path(before).read_bytes() == prior_bytes, 'registration byte chain')
            bb, aa = [yaml.safe_load(path(p).read_bytes()) for p in (before, after)]
            bc, ac = [{v['id']: v for v in x['claims']} for x in (bb, aa)]
            require(all(ac.get(k) == v for k, v in bc.items()), 'prior claim mutation inside chain')
            added = set(ac) - set(bc)
            require(added == set(receipt['new_claim_ids']), 'registrar actual additions')
            newids += sorted(added)
            chain.append(dict(path=d, before=len(bc), after=len(ac), new_ids=sorted(added)))
            prior_bytes = path(after).read_bytes()
        require(prior_bytes == path(SNAP).read_bytes() and len(set(newids)) == len(newids) == 19, 'chain final snapshot')
        newclaims = [claims[x] for x in newids]
        require(Counter(x['status'] for x in newclaims) == {'VERIFIED': 18, 'CANDIDATE': 1}, 'added status totals')
        require(Counter(x['status'] for x in final['claims']) == c['claim_status_counts'], 'actual ledger statuses')
        require(all(x['review_state'] == 'CLEAR' for x in final['claims']), 'actual ledger review state')
        require(all(x['revision'] == 1 for x in newclaims), 'new revisions')
        arts = {x['id']: x for x in final['artifacts']}
        for claim in newclaims:
            for aid in claim['evidence']:
                art = arts[aid]
                require(art['availability'] == 'LOCAL_ONLY', 'premature public availability')
                require(digest(art['path']) == art['sha256'], 'ledger evidence identity')
        validate_checkpoint(c, newclaims)
        run_records, outcome_reports = [], {}
        for run, review, exitcode, status in RUNS:
            d = B + run + '/'
            s = load(d + 'summary.json')
            gate = load(I + review + '/summary.json')
            outcome_reports[review] = gate
            require(s['research_calls'] == 1 and not s['automatic_retry'], 'one attempt')
            receipt = s['receipt']
            require(receipt['actual_exit_code'] == exitcode, 'native exit')
            command = receipt['command']
            require('60s' in command and '1000000' in command and '--as=4294967296:4294967296' in command and '--fsize=10737418240:10737418240' in command, 'native actual limits')
            logpath = d + 'main/solver.stdout.log'
            digest(logpath)
            text = path(logpath).read_text(encoding='utf8')
            statuses = re.findall(r'^s (\S+)\s*$', text, re.M)
            require(statuses == ([] if status is None else [status]), 'native status lines')
            for p in [d+'main/solver.receipt.json', d+'main/launch.json']:
                digest(p)
            trace = d + 'main/proof.drat'
            require(digest(trace) == s['proof_copy']['sha256'] and path(trace).stat().st_size == s['proof_copy']['bytes'], 'saved native trace')
            if exitcode in (0, 124):
                require(gate['interpreted_result'] == 'UNKNOWN' and gate['actual_research_calls'] == 1, 'UNKNOWN gate')
                require(gate['partial_trace']['sha256'] == INPUTS[trace], 'UNKNOWN trace pin')
            run_records.append(dict(path=d, native_exit=exitcode, status_lines=statuses, trace_sha256=INPUTS[trace], trace_bytes=path(trace).stat().st_size, independent_gate=I+review+'/summary.json'))
        second, third = [outcome_reports[k] for k in ['count_master_eight_orbit_cut_sat_outcome', 'count_master_partial_cut_sat_outcome']]
        require(c['count_search']['unique_profile_digests'] == [second['profile_sha256'], third['profile_sha256']], 'distinct count identities')
        require(third['variables_checked'] == 155939 and third['actual_clauses_checked'] == 705845 and third['exception_count'] == 8 and third['universal_upper_bounds_checked'] == 540 and third['upper_bound_failures'] == 0, 'third count metrics')
        proof = outcome_reports['second_eight_count_profile_unsat']
        require(proof['proof']['bytes'] == 1269209 and proof['proof']['complete_independent_replay'] is True, 'complete literal proof')
        for replay in proof['replays']:
            require(replay['accepted'] == replay['expected_acceptance'], 'proof controls/outcome')
            for kind in ['stdout', 'stderr']:
                p = I+'second_eight_count_profile_unsat/'+replay['name']+'.'+kind+'.log'
                require(digest(p) == replay[kind+'_sha256'], 'proof replay log identity')
        full = proof['replays'][-1]
        require(full['accepted'] and full['actual_exit_code'] == 0 and full['proof_sha256'] == run_records[2]['trace_sha256'], 'actual complete replay record')
        require('s VERIFIED' in path(I+'second_eight_count_profile_unsat/'+full['name']+'.stdout.log').read_text(), 'actual checker verdict')
        require(full['command'][1].endswith('eight_count_profile_lift_second\\instance.cnf'), 'proof literal input scope')
        gf = load(I+'gf2_alternating_completion_v2/summary.json')
        require(c['gf2']['exact_completion_pairs'] == gf['exact_completion_pairs'] == 4096 and c['gf2']['direct_D_systems'] == gf['direct_D_systems'] == 8192 and c['gf2']['saved_core_diagnostics'] == gf['saved_core_diagnostics'] == 70, 'GF2 finite totals')
        transports = [load(I+p+'/summary.json') for p in ['direct_cell_unknown_trace_transport', 'lex_unknown_trace_transport']]
        require(sum(x['raw_bytes'] for x in transports) == 1848656911 and sum(x['gzip_parts'] for x in transports) == 222 and all(not x['complete_unsat_proof'] for x in transports), 'transport aggregates')
        ex = c['execution']
        require(ex['command'][ex['command'].index('-C')+1] == 'cadical' and ex['exit_code'] == 1 and ex['state'] == 'NO_CADICAL_PROCESS_OBSERVED', 'targeted historical observation')
        for kind in ['stdout', 'stderr']:
            require(digest(B+'resume/twentyfifth_process_snapshot.'+kind+'.log') == ex[kind+'_sha256'], 'process snapshot identity')
        require(len(path(B+'resume/twentyfifth_process_snapshot.stdout.log').read_bytes().splitlines()) <= 1, 'no process rows')
        report = path(REPORT).read_text(encoding='utf8')
        table_ids = re.findall(r'^\| (C-[A-Z0-9-]+) r1 \| (VERIFIED|CANDIDATE|REFUTED) \|', report, re.M)
        require(dict(table_ids) == {x['id']: x['status'] for x in newclaims}, 'report claim table')
        for marker in ['267 ledger claims:262 VERIFIED', 'three CANDIDATE/CLEAR, two REFUTED/CLEAR', 'one literal Gram UNSAT', 'four direct-cell UNKNOWNs', 'No whole-support or unrestricted exclusion was added', '31,254,053-clause estimate is CANDIDATE']:
            require(marker in report, 'report scope/count statement: '+marker)
        guide = path(GUIDE).read_text(encoding='utf8')
        cli = cli_check(guide)
        require(PINS[MANIFEST] in guide and full['proof_sha256'] in guide and full['cnf_sha256'] in guide, 'guide exact pins')
        manifest = load(MANIFEST)
        bind(manifest['inputs_sha256'])
        records = manifest['records']
        require(len(records) == 8 and len({r['path'] for r in records}) == 8, 'raw recovery population')
        require(Counter(Path(r['path']).suffix for r in records) == {'.drat': 4, '.cnf': 3, '.json': 1}, 'recovery artifact types')
        require(sum(r['bytes'] for r in records) == 1907346389 and sum(len(r['parts']) for r in records) == 231, 'recovery totals')
        require({r['path'] for r in records if r['path'].endswith('.drat')} == {r['path']+'main/proof.drat' for r in run_records[3:]}, 'only four UNKNOWN traces in recovery')
        recovered = [recover_check(r) for r in records]
        saved_recovery = load(B+'resume/twentyfifth_raw_recovery.json')
        require(saved_recovery['originals'] == 8 and saved_recovery['raw_bytes'] == 1907346389 and saved_recovery['mathematical_verification'] is False, 'saved recovery receipt')
        controls = []
        mutations = [('count_population', ['claim_population'], 268), ('UNKNOWN_as_UNSAT', ['direct_cell_search','UNSAT'], 1), ('trace_as_proof', ['partial_trace_transport','complete_unsat_proofs'], 4), ('false_target', ['target_resolution'], 'SOLVED'), ('count_as_factor', ['third_count','full_factor'], True), ('duplicate_count', ['count_search','unique_profile_digests'], [second['profile_sha256']]*2)]
        for name, keys, value in mutations:
            bad = copy.deepcopy(c); target = bad
            for key in keys[:-1]: target = target[key]
            target[keys[-1]] = value
            try: validate_checkpoint(bad, newclaims)
            except ValueError: controls.append(name)
            else: raise ValueError('control accepted: '+name)
        sample = path(records[0]['parts'][0]['path']).read_bytes()
        for name, bad in [('truncated_gzip', sample[:-1]), ('extra_member', sample+sample)]:
            try: decode_member(bad)
            except (ValueError, zlib.error): controls.append(name)
            else: raise ValueError('gzip control accepted')
        bad = copy.deepcopy(records[0]); bad['parts'][0]['raw_offset'] = 1
        try: recover_check(bad)
        except ValueError: controls.append('wrong_raw_offset')
        else: raise ValueError('offset control accepted')
        write(out/'prior_publication_transition.json', dict(artifact_ids=publication_changes, claim_changes=0, content_hash_changes=0, scope='Saved historical ledger transition only; no fresh remote availability check.'))
        write(out/'registration_chain.json', chain)
        write(out/'actual_native_records.json', run_records)
        write(out/'replay_cli_review.json', cli)
        write(out/'recovery_identity.json', recovered)
        write(out/'controls.json', dict(rejected=controls, count=len(controls)))
        result = dict(status='INDEPENDENT_TWENTYFIFTH_CHECKPOINT_REPLAY_RECOVERY_CONSISTENCY_PASS', timestamp=datetime.now(timezone.utc).isoformat(), command=[sys.executable,*sys.argv], cwd=str(ROOT), claim_population=267, new_verified=18, new_candidate=1, previous_claims_unchanged=248, native_calls=7, count_SAT=2, literal_Gram_UNSAT=1, direct_cell_UNKNOWN=4, complete_proof_bytes=1269209, partial_trace_bytes=1848656911, recovered_raw_artifacts=8, recovered_raw_bytes=1907346389, recovered_gzip_parts=231, guide_commands_checked=len(cli), controls_rejected=len(controls), inputs_sha256=INPUTS, outputs_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}, shared_components=['Python standard library and PyYAML; saved raw records and previously independent scientific gates are data premises.', 'No repository producer, cataloguer, restorer, scientific checker or checkpoint-writer imports.'], limitations=['Checkpoint/report/CLI and byte-transport consistency only; existing mathematical gates are authenticated, not reproved here.', 'No publication catalog or staged/index/remote-availability approval; own candidate inventory is not used as an approval premise.', 'CLI syntax inspected without executing research commands. No solver, DRAT rerun, Git mutation or ledger edit.', 'Exact historical process observation only; no current process-state claim.', 'Original four UNKNOWN streams are complete saved host byte streams, not complete UNSAT certificates.'], elapsed_seconds=time.monotonic()-started)
        write(out/'summary.json', result)
        print(json.dumps({k:v for k,v in result.items() if k not in ['inputs_sha256','outputs_sha256','shared_components','limitations']}))
    except Exception as e:
        write(out/'failure.json', dict(error=repr(e), inputs_sha256=INPUTS, elapsed_seconds=time.monotonic()-started))
        raise


if __name__ == '__main__':
    main()
