"""Independent read-only frozen317->318 catalogue claim transition."""
from collections import Counter
import copy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import yaml
from audit_20261002_wave31_transition_v1 import UniqueLoader,need
from audit_20261002_wave32_transition_v1 import transition

ROOT=Path(__file__).resolve().parents[1]
REG='acceleration/results/20261002_wave32_registration03'
CID='C-UNRESTRICTED-ROOTED7-NONEDGE-LOCAL-CATALOGUE-COVERAGE'
BIND='acceleration/results/20261002_independent_review/rooted7_catalogue01/claim_binding.json'
BIND_SHA='bd579023a9dcf1cf6758b5be691d3aedf39a5727350d1d3ac2ca406752de95f5'


def main():
    pins={}
    def pin(name,wanted=None):
        with (ROOT/name).open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
        need(wanted is None or digest==wanted,'frozen artifact identity '+name);pins[name]=digest
    def load(name,wanted=None):pin(name,wanted);return json.loads((ROOT/name).read_bytes())
    registration=load(REG+'/summary.json');binding=load(BIND,BIND_SHA)
    need(registration['before_ledger_sha256']=='44e119ac7e1952e1d0abde8d68f3556c8aec9f73ba6e470d3d24e8fddc781d56'
         and registration['ledger_sha256']=='b0210a82c6df9a3991246dc708ef8240f5fe47b4a470e8c467da910b3da6ed5b'
         and registration['new_claim_ids']==[CID],'exact frozen317to318 registration')
    before_name=REG+'/CLAIMS.before.yaml';after_name=REG+'/CLAIMS.after.yaml'
    pin(before_name,registration['before_ledger_sha256']);pin(after_name,registration['ledger_sha256'])
    before=yaml.load((ROOT/before_name).read_text(encoding='utf8'),Loader=UniqueLoader)
    after=yaml.load((ROOT/after_name).read_text(encoding='utf8'),Loader=UniqueLoader)
    old,new,artifacts=transition(before,after,[CID],{CID:binding});claim=new[CID]
    need(len(old)==317 and len(new)==318,'complete record population')
    need(claim['scope']['unrestricted_target'] is True and claim['scope']['target_resolution']=='NONE'
         and claim['dependencies']==[] and binding['premise_state']['no_induced_triangular_prism']=='UNKNOWN'
         and 'UNKNOWN' in claim['unknowns']['premises'],'exact finite coverage and explicit conditional subcatalogue premise')
    report=load(binding['report'],binding['report_sha256'])
    need(report['status']=='INDEPENDENT_COMPLETE_ROOTED7_CATALOGUE_COVERAGE_PASS' and report['target_resolution'] is False
         and report['new_exclusions']==0,'coverage report only')
    need(report['all_labelled_masks_of_fixed_nonedge']==1048576 and report['admissible_labelled_masks']==251010
         and report['complete_rooted_classes']==2770 and report['conditional_prismfree_classes']==2750,'exact independently checked catalogue counts')
    for name,digest in binding['inputs_sha256'].items():pin(name,digest)
    for aid in claim['evidence']:
        record=artifacts[aid];pin(record['path'],record['sha256'])
        need(claim['verification'][0]['artifact_hashes'][aid]==record['sha256'],'exact evidence binding')
    rejected=[]
    mutations=[('prior_claim_changed',lambda x:x['claims'][0].update(statement='changed')),
               ('finite_claim_broadened',lambda x:x['claims'][-1]['scope'].update(target_resolution='NONEXISTENCE')),
               ('premise_promoted',lambda x:x['claims'][-1]['unknowns'].update(premises='ESTABLISHED'))]
    for label,mutate in mutations:
        damaged=copy.deepcopy(after);mutate(damaged)
        try:
            transition(before,damaged,[CID],{CID:binding})
            need('UNKNOWN' in damaged['claims'][-1]['unknowns']['premises'],'premise remains UNKNOWN')
        except ValueError:rejected.append(label)
        else:raise ValueError('corrupted transition accepted')
    for name in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261002_wave31_transition_v1.py',
                 'acceleration/audit_20261002_wave32_transition_v1.py','uv.lock','pyproject.toml']:pin(name)
    summary=dict(status='INDEPENDENT_WAVE32_EXACT317_TO318_TRANSITION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/checkpoint_audit',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),exact_command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,
        previous_claims=317,current_claims=318,unchanged_prior_claims=317,new_claim_ids=[CID],current_clear_status_counts=dict(Counter(c['status'] for c in new.values() if c['review_state']=='CLEAR')),
        new_exclusions=0,target_resolution='UNKNOWN',overall_search_coverage='UNKNOWN; no validated denominator.',corrupted_controls_rejected=rejected,mathematical_replays=0,
        scope='Frozen exact claim transition only; all317 prior records, artifacts and target semantics retained. Complete small catalogue is not marked-model/LP verification.',
        limitations=['The previously independent catalogue exhaustion is bound by its exact report; it is not rerun.','No present live ledger or remote publication state is inferred.','Prism absence remains UNKNOWN.'],artifact_availability='LOCAL_ONLY')
    out=ROOT/'acceleration/results/20261002_independent_review/rooted7_transition01';out.mkdir(exist_ok=False)
    with (out/'summary.json').open('x',encoding='utf8',newline='\n') as f:json.dump(summary,f,indent=2);f.write('\n')
    print(json.dumps({'path':(out/'summary.json').relative_to(ROOT).as_posix(),'sha256':hashlib.sha256((out/'summary.json').read_bytes()).hexdigest()}))


if __name__=='__main__':main()
