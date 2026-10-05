"""Append-only exact checking of a smaller same-scope Farkas certificate."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,subprocess,sys
import audit_20260930_hadamard_support_farkas as independent

ROOT=independent.ROOT;B=independent.B;D=B/'20260930_farkas_compress'
need,digest,key,save,read=independent.need,independent.digest,independent.key,independent.save,independent.read

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);bindings={}
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'artifact identity '+key(p));bindings[key(p)]=value
    try:
        original=B/'20260930_independent_review/hadamard_support_farkas/summary.json';pin(original,'d5a5d63c81a099f49c635ad84861c72ca6aa0c96bea9415dfce188557a5196c1')
        old=read(original);need(old['status']=='INDEPENDENT_THREE_FIXED_HADAMARD_SUPPORT_FARKAS_EXCLUSIONS_PASS','prior exact scoped proof')
        pin(Path(independent.__file__),old['inputs_sha256'][key(Path(independent.__file__))])
        pin(D/'summary.json','e32bd98d563960cff732707603a80dbd847aebed6240ba21546b2e20d785d3e3');prod=read(D/'summary.json')
        for p,h in {**prod['inputs_sha256'],**prod['outputs_sha256']}.items():pin(ROOT/p,h)
        rawpath=B/'20260930_hadamard20_support/connected_01.json';pin(rawpath,'2e839fda408da18e3689ffef00de647644375a000d308f4ea306b2cbdfa37e49')
        exact,_=independent.reconstruct(read(rawpath));modelpath=B/'20260930_hadamard_support_lp/exact_model.json';pin(modelpath,'5caeedf8c5e5277f387d1c978a20bb34e07b56d0197ea27c67cc3c535e5986d6');independent.matches_model(read(modelpath),exact)
        certpath=D/'certificate.json';pin(certpath,'8cdedec1978193c28bf52617c21f82873fee7cc4d0f5258c2466f6ed1156c9eb');cert=read(certpath)
        dots,right=independent.dual(exact['columns_nonzero_row_indices'],exact['rhs'],cert['values']);independent.matches_stats(cert,dots,right)
        need(len(cert['values'])==726 and len(dots)==4067 and right==-1,'exact smaller certificate scope and bound')
        weights=cert['values'];stats=dict(maximum_absolute_weight=max(map(abs,weights)),nonzero_onehot_weights=sum(v!=0 for v in weights[:60]),nonzero_Gram_weights=sum(v!=0 for v in weights[60:]))
        need(stats==dict(maximum_absolute_weight=50,nonzero_onehot_weights=59,nonzero_Gram_weights=382),'exact coefficient size counts')
        minima=[];argmins=[]
        for d in range(60):
            choices=[j for j,(column,_) in enumerate(exact['selectors']) if column==d];values=[sum(weights[i] for i in exact['columns_nonzero_row_indices'][j] if i>=60) for j in choices];v=min(values);minima.append(v);argmins.append(choices[values.index(v)])
            need(weights[d]==-v,'exact tight one-hot potential')
        need(cert['divided_gcd']==1 and cert['Gram_option_minima_before_gcd']==minima and cert['argmin_selector_indices']==argmins,'all saved per-column minima and witnesses')
        need(independent.dual([[0,1]],[0,1],[1,-1])==([0],-1),'calibrated tiny positive')
        rejected=[]
        def reject(label,fn):
            try:fn()
            except ValueError:rejected.append(label)
            else:raise ValueError('accepted corrupted compressed certificate '+label)
        reject('zero_dual',lambda:independent.dual(exact['columns_nonzero_row_indices'],exact['rhs'],[0]*726))
        reject('opposite_sign',lambda:independent.dual(exact['columns_nonzero_row_indices'],exact['rhs'],[-v for v in weights]))
        bad=weights[:];bad[0]-=1;reject('underweight_onehot',lambda:independent.dual(exact['columns_nonzero_row_indices'],exact['rhs'],bad))
        badcert={**cert,'rhs_dot':0};reject('altered_rhs_claim',lambda:independent.matches_stats(badcert,dots,right))
        for p in [Path(__file__),ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        save(out/'all_integer_products.json',dict(column_dots=dots,rhs_dot=right,onehot_minima=minima,argmin_selector_indices=argmins))
        report=dict(status='INDEPENDENT_COMPRESSED_CONNECTED01_FARKAS_CERTIFICATE_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=bindings,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},claim_id='C-FIXED-HADAMARD-CONNECTED01-SUPPORT-EXCLUSION',claim_revision=1,existing_statement_and_scope_unchanged=True,mathematical_result='All4067 integer column products are nonnegative and the integer RHS product is -1.',weights=726,columns=4067,minimum_column_dot=min(dots),rhs_dot=right,coefficient_stats=stats,verifier='/root/state_literature_audit',method='independent_integer_artifact_check_using_prior_independent_domain_reconstruction',shared_components=['Frozen independently authored domain/matrix/Farkas checker; no producer repair/compression imports.'],fresh_corruptions_rejected=rejected,artifact_availability='LOCAL_ONLY',recommendation='VERIFIED',review_state='CLEAR',limitations=['Same one saved connected01 coordinate support only; not a core exclusion.','Compression trial search and minimality were not audited or asserted.','Adds alternative exact evidence, no broader claim and no ledger edit.'])
        save(out/'summary.json',report);save(out/'claim_evidence_addendum.json',dict(claim_id=report['claim_id'],claim_revision=1,original_audit=dict(path=key(original),sha256=digest(original)),additional_audit=dict(path=key(out/'summary.json'),sha256=digest(out/'summary.json')),certificate=dict(path=key(certpath),sha256=digest(certpath)),statement_changed=False,scope_changed=False,verifier=report['verifier'],verification_method=report['method'],artifact_availability='LOCAL_ONLY',ledger_changed=False))
        print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'),binding_sha256=digest(out/'claim_evidence_addendum.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
