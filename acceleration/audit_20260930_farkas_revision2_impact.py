"""Read-only review of an evidence-only revision; no ledger mutation."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,copy,hashlib,json,subprocess,sys,yaml
import audit_20260930_hadamard_support_farkas as independent
ROOT=independent.ROOT;B=independent.B
need,read,save,digest,key=independent.need,independent.read,independent.save,independent.digest,independent.key
CID='C-FIXED-HADAMARD-CONNECTED01-SUPPORT-EXCLUSION'
def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    ledgerbytes=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(ledgerbytes);claims={c['id']:c for c in ledger['claims']};old=copy.deepcopy(claims[CID]);need(old['revision']==1 and old['status']=='VERIFIED' and old['review_state']=='CLEAR','exact current revision1')
    bindings={}
    def pin(p,h=None):
        value=digest(p);need(h is None or h==value,'input identity '+key(p));bindings[key(p)]=value
    original=B/'20260930_independent_review/hadamard_support_farkas/summary.json';pin(original,'d5a5d63c81a099f49c635ad84861c72ca6aa0c96bea9415dfce188557a5196c1')
    compressed=B/'20260930_independent_review/hadamard_farkas_compressed/summary.json';pin(compressed,'81c9989d4721c4298e6a87525dcdd5fe2592e708c2683bfb55b5015315f6ef8c')
    for report in [read(original),read(compressed)]:
        need(report['status'].endswith('_PASS'),'successful exact audit')
        for p,h in {**report['inputs_sha256'],**report['outputs_sha256']}.items():pin(ROOT/p,h)
    alias=B/'20260930_independent_review/hadamard_farkas_compressed/claim_evidence_addendum.json';pin(alias,'bf6d0599fb43206db68827a056d693c89ad5015c4924fde1e761ca68eda3a506')
    oldbindings=read(B/'20260930_independent_review/hadamard_support_farkas/claim_bindings.json')['claims'];bound=next(x for x in oldbindings if x['id']==CID)
    for field in ['statement','kind','basis','assumptions','dependencies']:need(old[field]==bound[field],'exact original field '+field)
    need(old['scope']['description']==bound['scope'],'unchanged exact scope')
    raw=read(B/'20260930_hadamard20_support/connected_01.json');exact,_=independent.reconstruct(raw)
    originalcert=read(B/'20260930_hadamard_support_lp_dual_repair/certificate.json');smallcert=read(B/'20260930_farkas_compress/certificate.json')
    checks=[]
    for name,cert,expected in [('original',originalcert,-37617760),('compressed',smallcert,-1)]:
        dots,rhs=independent.dual(exact['columns_nonzero_row_indices'],exact['rhs'],cert['values']);need(rhs==expected and len(dots)==4067,'fresh exact certificate '+name)
        checks.append(dict(certificate=name,weights=len(cert['values']),columns=len(dots),minimum_column_product=min(dots),rhs_product=rhs))
    dependents=[dict(id=c['id'],revision=c['revision']) for c in ledger['claims'] if any(d.get('id')==CID for d in c.get('dependencies',[]))];need(not dependents,'no current dependent uses require repinning')
    save(out/'revision1_claim_snapshot.json',old)
    unaffected={cid:copy.deepcopy(claims[cid]) for cid in ['C-FIXED-HADAMARD-CONNECTED02-SUPPORT-EXCLUSION','C-FIXED-HADAMARD-CONNECTED03-SUPPORT-EXCLUSION']};save(out/'unaffected_claim_snapshots.json',unaffected)
    pin(Path(__file__));pin(ROOT/'uv.lock');pin(ROOT/'pyproject.toml')
    now=datetime.now(timezone.utc).isoformat();report=dict(status='INDEPENDENT_FIXED_SUPPORT_FARKAS_REVISION2_IMPACT_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=bindings,observed_ledger_sha256=hashlib.sha256(ledgerbytes).hexdigest(),old_claim_canonical_json_sha256=canonical(old),old_snapshot_sha256=digest(out/'revision1_claim_snapshot.json'),unaffected_claim_canonical_sha256={cid:canonical(c) for cid,c in unaffected.items()},unaffected_snapshot_sha256=digest(out/'unaffected_claim_snapshots.json'),claim_id=CID,from_revision=1,claim_revision=2,statement=old['statement'],kind=old['kind'],basis=old['basis'],scope=old['scope'],assumptions=old['assumptions'],dependencies=old['dependencies'],recommendation='VERIFIED',review_state='CLEAR',verifier='/root/state_literature_audit',method='independent_artifact_check_and_limited_dependency_impact_review',fresh_exact_checks=checks,approved_changes=['Revision1 to2; preserve the entire statement, scope, assumptions, dependencies and all original evidence/verification records.','Append compressed-certificate evidence plus this revision2 PASS record; update timestamp.'],not_approved=['No change to connected02/03 or any unrelated claim, including shared evidence/verification objects.','No deletion or alteration of old evidence, restrictions, verification records or dependency relations.'],mathematical_statement_changed=False,dependent_uses=dependents,availability='LOCAL_ONLY',limitations=['Only one fixed support is excluded.','The original vector with RHS -37617760 continues to establish the exact unchanged statement; the smaller vector is additional evidence only.','Earlier registration failed before any ledger write; no mathematical veto or invalidation of connected02/03 follows.','Canonical JSON digests identify claim content independently of YAML aliases/formatting.'],shared_components=['Frozen independent exact-domain and integer-product checker; no producer repair/compression code imported.'],outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},ledger_changed=False)
    need((ROOT/'CLAIMS.yaml').read_bytes()==ledgerbytes,'ledger remained unchanged during review');save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))
if __name__=='__main__':main()
