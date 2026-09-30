"""Auditor metadata addenda only; frozen mathematical statements and original reports unchanged."""
from datetime import datetime,timezone
from hashlib import file_digest
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
PAIR=ROOT/'acceleration/results/20260930_independent_review/variable_core_pair_orbits_v2/summary.json'
MOD=ROOT/'acceleration/results/20260930_independent_review/triangle_modular_kernel_finite/summary.json'
PINS={PAIR:'6a9840be472b5bcd546a270c881c9f86d09a4bf6cc8eccade6b30f045a2bb33a',MOD:'abdea549a37df6089d197884f0d83d206a6ccb77be502d5f252f2d12ef6b9f90'}
def digest(p):
    with p.open('rb') as f:return file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def need(b,s):
    if not b:raise ValueError(s)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    inputs={};reports={}
    for p,h in PINS.items():
        need(digest(p)==h,'frozen report');inputs[key(p)]=h;reports[p]=json.loads(p.read_bytes())
        for name,value in reports[p]['inputs_sha256'].items():need(digest(ROOT/name)==value,'unchanged original audit input');inputs[name]=value
        for name,value in reports[p].get('outputs_sha256',{}).items():need(digest(ROOT/name)==value,'unchanged audit evidence');inputs[name]=value
    inputs[key(Path(__file__))]=digest(Path(__file__))
    pair=reports[PAIR];mod=reports[MOD];now=datetime.now(timezone.utc).isoformat()
    records=[dict(id=pair['claim']['id'],revision=1,statement=pair['claim']['statement'],kind='encoding',basis=['DERIVED','COMPUTED'],recommended_status='VERIFIED',recommended_review_state='CLEAR',scope='Universal normalization of the audited necessary arbitrary-core factor model by complete ordered matching-pair relabelling. Every target supplies a normalized-model solution under the pinned triangle-normalization premise. This is not a sufficient graph construction and excludes no target or factor.',assumptions=['Pinned complete census and first-stage normalization remain valid at the cited revisions.','Pinned base encoding and universal triangle normalization remain valid at the cited revisions.'],dependencies=pair['claim']['dependencies'],verifier='/root/eight_domain_audit',verification_method=pair['checking_method'],trusted_components=pair['trusted_components'],evidence_report=key(PAIR),evidence_sha256=PINS[PAIR],verification_timestamp=pair['timestamp'],editorial_addendum_timestamp=now,limitations=pair['limitations'],statement_or_scope_changed=False,mathematical_rerun=False),
      dict(id=mod['claim_id'],revision=1,statement=mod['exact_statement'],kind='empirical/engineering result',basis=['COMPUTED'],recommended_status='VERIFIED',recommended_review_state='CLEAR',scope='Exactly the256 deterministically reconstructed finite-field perturbations of one pinned SRG243 fixture,128 in each field, and agreement with the saved finite summaries. No unrestricted-target coverage or universal redundancy implication.',assumptions=['Exact pinned SRG243 block fixture and deterministic seed/source protocol.','Python random.Random draw order is shared for protocol reconstruction.'],dependencies=[dict(id='C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL',revision=1,relation='verification_dependency')],verifier='/root/eight_domain_audit',verification_method=mod['checking_path'],trusted_components='Python integer arithmetic, standard library PRNG for identical seeded protocol, and hardware. Elimination and modular product code are independently authored; no producer imports.',evidence_report=key(MOD),evidence_sha256=PINS[MOD],verification_timestamp=mod['timestamp'],editorial_addendum_timestamp=now,limitations=[mod['missing_original_artifact_limitation'],*mod['limitations']],statement_or_scope_changed=False,mathematical_rerun=False)]
    result=dict(status='INDEPENDENT_PAIR_AND_MODULAR_CLAIM_METADATA_BINDING_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,claims=records,ledger_edited=False,previous_reports_unchanged=True,target_resolution=False)
    p=args.out/'summary.json'
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(status=result['status'],summary_sha256=digest(p))))
if __name__=='__main__':main()
