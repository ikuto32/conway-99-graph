"""Read-only wave26 checkpoint review; imports no repository implementation."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import argparse
import copy
import hashlib
import json
import re
import sys
import time
import yaml

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'
CP = B + 'resume/twentysixth_milestone_checkpoint.json'
SNAP = B + 'resume/claims_at_twentysixth_milestone.yaml'
OLD = B + 'resume/claims_at_twentyfifth_milestone.yaml'
REPORT = 'docs/RESEARCH_20260930_TWENTYSIXTH_WAVE_CORRECTED.md'
INITIAL_REPORT = 'docs/RESEARCH_20260930_TWENTYSIXTH_WAVE.md'
CORRECTION = B + 'twentysixth_report_scope_correction/summary.json'
REGS = ['profile', 'upper', 'block', 'eight_reduction', 'census_algebra', 'psd', 'scalar', 'block_screen']
GATES = {
 'preflight': 'exact_eight_profile_preflight', 'join': 'exact_eight_profile_join',
 'scalar': 'exact_eight_scalar_screen', 'blocks': 'exact_eight_block_screen',
 'third_proof': 'third_eight_count_profile_unsat', 'psd': 'triplicate_count_psd',
 'gf3': 'gf3_hollow_residual', 'upper': 'count_min_upper_cnf',
}
PINS = {
 CP: '8fc457eb11d2b8f836ff194dffcd5a1618119f66ee5e3a5626310d07a8be59a2',
 SNAP: '8bcdad8f4b2e871b6c0bdf6ef72736033a8d84624af029e1b01c2951bc4b8146',
 OLD: '82e03975b3e6eb109a0fb9c82746475a253763d1620d543e8938fec561d3cd77',
 REPORT: 'fb394a08d95c3cdc41e446393c155a9df8456c2795c9b8f9159fe938038febc6',
 INITIAL_REPORT: '7954cef87b2b7b890f692692e07b9bf3cd9d294726ceb854fe4f9cea2b7a27e1',
}
INPUTS = {}

def need(ok, why):
    if not ok: raise ValueError(why)

def path(p):
    p = str(p).replace('\\', '/')
    need(p != I+'hadamard_oriented_unknown/process.stdout.log' and 'PROMPT.md' not in p and not p.startswith('tools/'), 'protected path')
    q = (ROOT/p).resolve()
    need(q.is_relative_to(ROOT), 'path escape')
    return q

def sha(p):
    q = path(p)
    with q.open('rb') as f: h = hashlib.file_digest(f, 'sha256').hexdigest()
    INPUTS[q.relative_to(ROOT).as_posix()] = h
    return h

def bind(m):
    for p, h in m.items(): need(sha(p) == h, 'identity: '+p)

def load(p):
    sha(p)
    return json.loads(path(p).read_bytes())

def yload(p):
    sha(p)
    return yaml.safe_load(path(p).read_bytes())

def write(p, o):
    with p.open('x', encoding='utf8', newline='\n') as f:
        json.dump(o, f, indent=2); f.write('\n')

def byid(a):
    d = {v['id']:v for v in a}
    need(len(d) == len(a), 'duplicate IDs')
    return d

def checkpoint(c, gates):
    need(c['claim_population'] == 278 and c['claim_status_counts'] == {'VERIFIED':273,'CANDIDATE':3,'REFUTED':2}, 'status counts')
    need(c['claim_review_counts'] == {'CLEAR':278}, 'review counts')
    need(len(c['new_verified_ids']) == len(set(c['new_verified_ids'])) == 11 and c['new_candidate_ids'] == c['new_refuted_ids'] == [], 'new IDs/statuses')
    need(c['target_resolution'] == 'UNKNOWN' and c['external_review'] is None, 'target conclusion')
    need(all(c[k] == 0 for k in ('new_full_factors','new_complete99_graphs','new_whole_support_exclusions','new_unrestricted_exclusions')), 'overstatement')
    need(c['literal_gram_lift'] == {'selected':1,'attempted':1,'completed':1,'UNSAT':1,'complete_independent_proof_replays':1,'proof_bytes':5549451,'scope':'Third literal profile only; no orbit exclusion is inferred.'}, 'literal proof scope')
    expected = dict(kernel_retained_subsets_tested=4184,nonempty_subsets=67,labelled_profiles=9288,global_fibre_classes=1548,scalar_excluded_classes=756,scalar_surviving_classes=792,separate_block_tests=47520,block_excluded_classes=0,block_surviving_classes=792)
    need(all(c['count_pipeline'].get(k) == v for k,v in expected.items()), 'count pipeline')
    need(set(c['excluded_future_cohort']) == {'exact_eight_next_lift','triplicate_psd_kernel_options'}, 'future cohort exclusion')
    for key, values in c['exact_audit_metrics'].items():
        need(key in gates, 'unknown metric source')
        for k,v in values.items(): need(k in gates[key] and gates[key][k] == v, 'raw gate metric '+key+':'+k)
    need(c['exact_audit_metrics']['psd']['literal_research_matrices'] == 3 and c['exact_audit_metrics']['blocks']['representatives_surviving'] == 792, 'PSD population separation')

def claim_check(claim, binding, claims):
    need(claim['id'] == binding['id'] and claim['revision'] == binding['revision'] == 1, 'claim identity')
    need(claim['status'] == binding['status'] == 'VERIFIED' and claim['review_state'] == 'CLEAR', 'claim status')
    need(claim['statement'] == binding['statement'] and claim['dependencies'] == binding['dependencies'], 'statement/dependency mutation')
    need(claim['basis'] == binding['basis'], 'basis mutation')
    need(claim['scope']['target_resolution'] == 'NONE', 'claim target result')
    if 'scope' in binding: need(claim['scope']['description'] == binding['scope'], 'binding scope')
    for dep in claim['dependencies']:
        need(dep['id'] in claims and claims[dep['id']]['revision'] == dep['revision'], 'unresolved dependency')
    need(claim['external_source'] is None, 'unverified external review')

def correction_check(original, corrected, r):
    need(r['old_sentence'] in original and r['new_sentence'] in corrected, 'correction sentences')
    changed = original.replace('# Twenty-sixth research milestone, 2026-09-30', '# Twenty-sixth research milestone, 2026-09-30 (scope correction)', 1)
    changed = changed.replace('\n\n', '\n\nThis corrects one ambiguous scope sentence in the [preserved initial report](RESEARCH_20260930_TWENTYSIXTH_WAVE.md). The numerical checkpoint and ledger are unchanged.\n\n', 1)
    changed = changed.replace(r['old_sentence'], r['new_sentence'], 1)
    need(changed == corrected, 'additional undeclared report edit')
    need(all(r[k] is False for k in ('checkpoint_changed','ledger_changed','mathematical_claim_changed')), 'correction impact')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True); a = ap.parse_args()
    out = a.out.resolve(); out.mkdir(parents=True, exist_ok=False); started = time.monotonic()
    try:
        bind(PINS)
        for p in [Path(__file__), Path(__file__).with_name(Path(__file__).stem+'_spec.md')]: sha(p.relative_to(ROOT).as_posix())
        c = load(CP); bind(c['evidence_sha256'])
        writer = 'acceleration/record_20260930_twentysixth_checkpoint.py'
        need(sha(writer) == c['writer_sha256'], 'checkpoint writer identity')
        need(sha(B+'resume/twentyfifth_milestone_checkpoint.json') == c['previous_checkpoint_sha256'], 'previous checkpoint')
        old, final = yload(OLD), yload(SNAP)
        oldclaims, claims = byid(old['claims']), byid(final['claims'])
        need(len(oldclaims)==267 and len(claims)==278 and all(claims.get(k)==v for k,v in oldclaims.items()), 'prior267 claims changed')
        initial = yload(B+'twentysixth_profile_registration/CLAIMS.before.yaml')
        need(set(initial)==set(old) and all(initial[k]==old[k] for k in old if k not in ('updated_at','artifacts')), 'prior publication nonmetadata change')
        oa, ia = byid(old['artifacts']), byid(initial['artifacts']); need(set(oa)==set(ia), 'prior artifact population')
        changed=[]
        for k in oa:
            if oa[k]==ia[k]: continue
            need(set(oa[k])==set(ia[k]) and all(oa[k][f]==ia[k][f] for f in oa[k] if f not in ('availability','retrieval','unavailable_reason')), 'prior artifact content')
            need(oa[k]['availability']=='LOCAL_ONLY' and ia[k]['availability']=='PUBLIC' and ia[k]['unavailable_reason'] is None, 'publication direction')
            need(ia[k]['retrieval']=='https://github.com/ikuto32/conway-99-graph/blob/9125c523190464b147f67ec1eb58887ad8bb9295/'+ia[k]['path'], 'immutable publication URL')
            changed.append(k)
        need(len(changed)==37, 'prior publication population')
        chain=[]; added_order=[]; prior=path(B+'twentysixth_profile_registration/CLAIMS.before.yaml').read_bytes()
        for name in REGS:
            d=B+'twentysixth_'+name+'_registration/'; s=load(d+'summary.json')
            bind({d+'CLAIMS.before.yaml':s['previous_ledger_sha256'],d+'CLAIMS.after.yaml':s['ledger_sha256']})
            need(path(d+'CLAIMS.before.yaml').read_bytes()==prior, 'exact registration byte chain')
            before,after=yload(d+'CLAIMS.before.yaml'),yload(d+'CLAIMS.after.yaml')
            bc,ac=byid(before['claims']),byid(after['claims']); ba,aa=byid(before['artifacts']),byid(after['artifacts'])
            need(all(ac.get(k)==v for k,v in bc.items()) and all(aa.get(k)==v for k,v in ba.items()), 'old registration records changed')
            need(set(ac)-set(bc)==set(s['new_claim_ids']), 'actual additions')
            source=next(p for p in s['command'] if p.startswith('acceleration/') and p.endswith('.py'))
            need(sha(source)==s['registrar_sha256'], 'registrar source identity')
            need(s['registrar_performs_mathematical_verification'] is False and s['validation']['valid'] is True, 'registrar boundary')
            added_order.extend(s['new_claim_ids']); prior=path(d+'CLAIMS.after.yaml').read_bytes()
            chain.append(dict(name=name,before=len(bc),after=len(ac),new_ids=s['new_claim_ids'],source=source,summary_sha256=INPUTS[d+'summary.json']))
        need(prior==path(SNAP).read_bytes() and added_order==c['new_verified_ids'], 'final chain/new ID order')
        need(Counter(x['status'] for x in final['claims'])==c['claim_status_counts'] and Counter(x['review_state'] for x in final['claims'])==c['claim_review_counts'], 'actual ledger population')
        arts=byid(final['artifacts']); records=[]
        for cid in added_order:
            claim=claims[cid]; ev=[arts[x] for x in claim['evidence']]
            need(len(ev)==2 and all(v['availability']=='LOCAL_ONLY' for v in ev), 'new evidence availability/population')
            bind({v['path']:v['sha256'] for v in ev})
            report=load(ev[0]['path']); binding=load(ev[1]['path']); claim_check(claim,binding,claims)
            v=claim['verification']; need(len(v)==1 and v[0]['outcome']=='PASS' and v[0]['claim_revision']==1, 'verification revision/outcome')
            need(v[0]['command_or_audit']==ev[0]['path'] and v[0]['artifact_hashes']=={e['id']:e['sha256'] for e in ev}, 'exact verification evidence')
            need(report['status'].endswith('_PASS'), 'independent gate status')
            records.append(dict(id=cid,statement=claim['statement'],scope=claim['scope'],dependencies=claim['dependencies'],evidence={e['path']:e['sha256'] for e in ev},scientific_reverification=False))
        gates={k:load(I+n+'/summary.json') for k,n in GATES.items()}; checkpoint(c,gates)
        failure=load(B+'twentysixth_census_algebra_registration_preparation/attempt01/failure.json')
        need(failure['status']=='REGISTRAR_FAILED_BEFORE_LEDGER_WRITE' and failure['error']=="KeyError: 'timestamp'", 'preserved failure')
        failedsource=next(p for p in failure['command'] if p.startswith('acceleration/') and p.endswith('.py'))
        need(sha(failedsource)==failure['source_sha256'], 'failed source identity')
        need(failure['ledger_unchanged_sha256']==INPUTS[B+'twentysixth_census_algebra_registration/CLAIMS.before.yaml'], 'failed ledger unchanged')
        p=gates['third_proof']; need(p['proof']['bytes']==5549451 and p['proof']['complete_independent_replay'] is True, 'proof scope/complete receipt')
        proof=p['proof']['path']; need(sha(proof)==p['proof']['sha256'] and path(proof).stat().st_size==5549451, 'full saved proof bytes')
        for replay in p['replays']:
            need(replay['accepted']==replay['expected_acceptance'], 'replay control')
            for kind in ('stdout','stderr'):
                rp=I+'third_eight_count_profile_unsat/'+replay['name']+'.'+kind+'.log'
                need(sha(rp)==replay[kind+'_sha256'], 'replay log identity')
        full=p['replays'][-1]; cnf=B+'eight_count_profile_lift_third/instance.cnf'
        need(full['accepted'] and full['actual_exit_code']==0 and sha(cnf)==full['cnf_sha256'] and full['proof_sha256']==INPUTS[proof], 'complete literal replay binding')
        need('s VERIFIED' in path(I+'third_eight_count_profile_unsat/'+full['name']+'.stdout.log').read_text(), 'literal checker verdict')
        for val in full['command'][1:]: sha(Path(val).relative_to(ROOT).as_posix())
        run=B+'eight_count_profile_lift_third_native_pilot/'; native=load(run+'summary.json')
        need(native['research_calls']==1 and native['automatic_retry'] is False and native['receipt']['actual_exit_code']==20, 'actual native one UNSAT attempt')
        command=native['receipt']['command']; need(all(v in command for v in ('60s','1000000','--as=4294967296:4294967296','--fsize=10737418240:10737418240')), 'actual native limits')
        need(native['proof_copy']['sha256']==INPUTS[proof] and native['proof_copy']['bytes']==5549451, 'native proof transfer binding')
        sha(run+'main/solver.stdout.log'); native_text=path(run+'main/solver.stdout.log').read_text()
        need(re.findall(r'^s (\S+)\s*$',native_text,re.M)==['UNSATISFIABLE'], 'literal raw native status')
        for name in ('main/solver.receipt.json','main/launch.json'): sha(run+name)
        ex=c['execution']; need(ex['exit_code']==1 and ex['state']=='NO_CADICAL_PROCESS_OBSERVED' and ex['command'][ex['command'].index('-C')+1]=='cadical', 'historical targeted observation')
        for kind in ('stdout','stderr'): need(sha(B+'resume/twentysixth_process_snapshot.'+kind+'.log')==ex[kind+'_sha256'], 'process receipt identity')
        need(len(path(B+'resume/twentysixth_process_snapshot.stdout.log').read_bytes().splitlines())<=1,'no saved process row')
        correction=load(CORRECTION); bind({correction['original_path']:correction['original_sha256'],correction['corrected_path']:correction['corrected_sha256']})
        original=path(INITIAL_REPORT).read_text(encoding='utf8'); corrected=path(REPORT).read_text(encoding='utf8'); correction_check(original,corrected,correction)
        need(re.findall(r'^\| (C-[A-Z0-9-]+) r1 \|',corrected,re.M)==added_order, 'report claim table order')
        markers=['278 ledger claims: 273 VERIFIED/CLEAR, three CANDIDATE/CLEAR, two REFUTED/CLEAR','7,122,626','9,288 labelled count profiles','1,548 six-member fibre orbits','756 classes (4,536 labelled profiles)','792 (4,752 labelled profiles)','47,520 profile/block pairs','2,527 distinct block problems','5,549,451-byte DRAT trace','161,159-variable, 726,485-clause','7,290 direct small systems','No PSD census of the 792 survivors is claimed.','No whole-support or unrestricted exclusion was added.','no orbit or whole-support conclusion is inferred here']
        for marker in markers: need(marker in corrected,'report statement: '+marker)
        controls=[]
        mutations=[('population',['claim_population'],279),('status',['claim_status_counts','VERIFIED'],274),('target',['target_resolution'],'SOLVED'),('factor',['new_full_factors'],1),('scope_union',['new_whole_support_exclusions'],1),('proof_bytes',['literal_gram_lift','proof_bytes'],5549450),('block_excluded',['count_pipeline','block_excluded_classes'],1),('PSD_792',['exact_audit_metrics','psd','literal_research_matrices'],792),('DP_claim',['exact_audit_metrics','blocks','producer_DP_prefix_states_checked'],True)]
        for name,keys,value in mutations:
            bad=copy.deepcopy(c); t=bad
            for k in keys[:-1]:t=t[k]
            t[keys[-1]]=value
            try:checkpoint(bad,gates)
            except ValueError:controls.append(name)
            else:raise ValueError('accepted corruption '+name)
        sample=claims[added_order[0]]; binding=load(arts[sample['evidence'][1]]['path'])
        for name,field,value in [('statement','statement','broader conclusion'),('dependency','dependencies',[]),('claim_revision','revision',2)]:
            bad=copy.deepcopy(sample);bad[field]=value
            try:claim_check(bad,binding,claims)
            except ValueError:controls.append(name)
            else:raise ValueError('accepted claim corruption')
        try:correction_check(original,corrected.replace('No PSD census of the 792 survivors is claimed.','All792 passedPSD.'),correction)
        except ValueError:controls.append('report_PSD_scope')
        else:raise ValueError('accepted report corruption')
        write(out/'checked_records.json',dict(registration_chain=chain,claims=records,previous_publication_only_changes=changed,controls_rejected=controls,report_correction=correction,process_observation_scope='Saved timestamp only; no fresh process assertion.'))
        result=dict(status='INDEPENDENT_TWENTYSIXTH_CHECKPOINT_CONSISTENCY_PASS',created_at=datetime.now(timezone.utc).isoformat(),verifier='/root/state_literature_audit',method='Independent byte-chain, raw named-gate and receipt comparison; no producer imports',command=[sys.executable,*sys.argv],cwd=str(ROOT),registration_chain=8,new_verified=11,total_claims=278,status_counts=c['claim_status_counts'],old_claims_unchanged=267,previous_publication_only_artifacts=37,scientific_reverification=False,independent_saved_proof_receipt_checked=True,proof_bytes=5549451,report_correction_approved=True,checkpoint_changed=False,ledger_changed=False,controls_rejected=controls,inputs_sha256=INPUTS,outputs_sha256={'checked_records.json':hashlib.sha256((out/'checked_records.json').read_bytes()).hexdigest()},limits=dict(native_calls=0,solver_calls=0,catalog_approval=False,scope='Checkpoint/registration/report consistency only; own prior scientific reports are authenticated rather than newly approved.'),elapsed_seconds=time.monotonic()-started)
        write(out/'summary.json',result); print(json.dumps({k:result[k] for k in ('status','registration_chain','new_verified','total_claims','elapsed_seconds')}))
    except Exception as exc:
        write(out/'failure.json',dict(status='FAIL',error=repr(exc),inputs_sha256=INPUTS,elapsed_seconds=time.monotonic()-started));raise

if __name__=='__main__':main()
