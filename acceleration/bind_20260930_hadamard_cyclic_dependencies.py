"""Append named dependency identities after their independently reviewed gates."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,subprocess,sys
import audit_20260930_hadamard_cyclic_unsat as audit
ROOT=audit.ROOT;load,save,digest,need,key=audit.load,audit.save,audit.digest,audit.need,audit.key
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    reduction=audit.RED;proof=audit.B+'20260930_independent_review/hadamard_cyclic_unsat/summary.json';oldproof=audit.B+'20260930_independent_review/hadamard_cyclic_unsat/claim_binding.json';oldencoding=audit.B+'20260930_independent_review/hadamard_cyclic_factor_cnf/claim_binding.json'
    pins={reduction:'7b9d988b946284d7a9fbcccccf1c2f32592dbdeb2e30cb6201e1565ea75d4de1',proof:'83029350b25523c015dfe916d8056324c0970021d2b024d68941dd41fb8c2b70',oldproof:'7f7ddc6a23e3b2db4ddff673110cb4ea6230f6477ae2513bb1835615a1f62c2e',audit.ENC:'494add3aecbd2d7d4629c738be73dda3a884c89ecb624fbdb5e867dca2a6ad64',oldencoding:digest(ROOT/oldencoding)}
    for p,h in pins.items():need(digest(ROOT/p)==h,'frozen record '+p)
    red=load(reduction);need(red['claim_id']=='C-FIXED-HADAMARD-SIX-PRISM-CYCLIC-FIBRE-REDUCTION' and red['claim_revision']==1 and red['recommendation']=='VERIFIED' and red['review_state']=='CLEAR','exact reduction claim identity')
    rep=load(proof);need(rep['status']=='INDEPENDENT_FIXED_HADAMARD_CYCLIC_FACTOR_UNSAT_PASS','complete proof replay')
    for p in ['acceleration/results/20260930_hadamard_six_prism_cyclic_cnf/scope.json','acceleration/results/20260930_hadamard_six_prism_cyclic_cnf/model.json','acceleration/results/20260930_hadamard20_support/six_prism.json']:
        need(red['inputs_sha256'][p]==rep['inputs_sha256'][p]==load(audit.ENC)['inputs_sha256'][p],'identical mathematical artifact '+p)
    dependency=dict(id=red['claim_id'],revision=1,relation='normalization')
    updates=[]
    for path in [oldencoding,oldproof]:
        old=load(path);need(old['revision']==1 and old['recommendation']=='VERIFIED','initial approved record')
        deps=old['dependencies']+[dependency]
        updates.append(dict(id=old['id'],revision=old['revision'],statement=old['statement'],scope=old['scope'],assumptions=old['assumptions'],dependencies=deps,source_binding_path=path,source_binding_sha256=digest(ROOT/path),recommendation='VERIFIED',review_state='CLEAR',verification_scope='Named dependency identity completed; original statement, exact scope and all existing evidence remain unchanged.'))
    now=datetime.now(timezone.utc).isoformat();pins[key(__file__)]=digest(__file__)
    record=dict(status='INDEPENDENT_HADAMARD_CYCLIC_NAMED_DEPENDENCY_BINDING_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,claim_updates=updates,verifier='/root/state_literature_audit',method='independent_exact_dependency_scope_review',written_review='The pinned reduction establishes only the phase gauge and full Gram/cap equivalence inside the explicit cyclic-F subclass. The encoding represents exactly those normalized choices; its checked UNSAT trace therefore excludes that subclass including its ungauged phase variants. It supplies no coverage of arbitrary factors on this support. Raw L, core, domains and scope hashes agree across all three gates. The existing encoding and exclusion statements already contain this restriction and require no change.',ledger_changed=False,original_records_preserved=True,artifact_availability='LOCAL_ONLY',target_resolution=False,limitations=['Initial registration metadata only; no new mathematical statement or broader coverage.','No reinterpretation as target or residual automorphism.'])
    save(out/'summary.json',record);print(json.dumps(dict(status=record['status'],sha256=digest(out/'summary.json'))))
if __name__=='__main__':main()
