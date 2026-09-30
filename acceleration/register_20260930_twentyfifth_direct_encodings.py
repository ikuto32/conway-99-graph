"""Register two exact encodings from separate clause and semantic reviews."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];I='acceleration/results/20260930_independent_review/'
REPORTS=[(I+'direct_cell_count_cnf/summary.json','a7fd5968681257c60a0e82a36b53f40798487d727f2f467dae47918becf84042','INDEPENDENT_DIRECT_CELL_ALL_CAPS_ENCODING_PASS','/root'),(I+'direct_cell_semantics/summary.json','88d6e8134c34b61d44a29e0bc525aebfb260f3f71c78efa72b98a7049275fdc8','INDEPENDENT_DIRECT_CELL_SEMANTICS_PASS','/root/eight_domain_audit')]
def sha(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==252
    inputs={};audits=[];evidence=[];hashes={}
    for i,(name,pin,status,verifier)in enumerate(REPORTS):
        assert sha(name)==pin;report=read(name);assert report['status']==status;inputs[name]=pin;audits.append(report)
        for field in ['inputs_sha256','outputs_sha256']:
            for p,h in report[field].items():assert sha(p)==h,p;assert p not in inputs or inputs[p]==h;inputs[p]=h
        aid=f'twentyfifth-direct-encoding-review-{i}';assert aid not in {a['id']for a in data['artifacts']};evidence.append(aid);hashes[aid]=pin
        data['artifacts'].append(dict(id=aid,path=name,sha256=pin,availability='LOCAL_ONLY',retrieval='Exact workspace path; full clause and separate semantic audit reports bind commands, raw artifacts and controls.',unavailable_reason='Twenty-fifth immutable evidence publication not yet confirmed.'))
    assert [(r['variant'],r['variables'],r['clauses'])for r in audits[0]['formulas']]==[('standalone',23112,320484),('at_least_seven',169151,968960)]
    assert audits[0]['solver_calls']==audits[1]['native_calls']==0
    raw='ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'
    definitions=[('C-FIXED-HADAMARD-DIRECT-CELL-ALL-CAPS-ENCODING','standalone',23112,320484,'45bac5dddcc805010dd4da150cc1c4613855b5d0e1e436f7b584067875c85250',False),('C-FIXED-HADAMARD-DIRECT-CELL-COUNT-COUPLED-ALL-CAPS-ENCODING','at_least_seven',169151,968960,'07323c9fbbd75e328dfa0d1a99c760823799ecf7bba74722e2720d7dbb97c959',True)]
    now=datetime.now(timezone.utc).isoformat();ids=[]
    for cid,variant,n,m,cnf,coupled in definitions:
        scope='One literal six-prism support/core, complete integer Gram and all outside-column caps; original column labels retained. '+('An explicit at-least-seven-unbalanced-group restriction and the verified count-master coverage are included.'if coupled else 'No exception-count restriction or column normalization.')
        statement=f'The pinned {n}-variable {m}-clause {variant} CNF (SHA256 {cnf}) projects under its 1,080 cell variables exactly onto the binary 36x60 matrices F with literal support L from raw artifact SHA256 {raw}, two entries per fibre of each column, prescribed integer FF^T, and all 1,770 outside-column overlaps at most two'+(', with at least seven unbalanced triplicate-support groups; each such labelled matrix admits a compatible count-master and auxiliary extension.'if coupled else '; each such labelled matrix admits the encoded auxiliary extension.')
        deps=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise')]
        if coupled:deps.append(dict(id='C-FIXED-HADAMARD-ARBITRARY-EXCEPTION-COUNT-MASTER-ENCODING',revision=1,relation='encoding_equivalence'))
        assumptions=['The exact literal support, core and Gram target identified in the statement.','The formula concerns factors only; no residual graph D is encoded.']
        if coupled:assumptions+=['At least seven unbalanced groups is an explicit additional predicate.','Previously independently checked complete count-master coverage, coordinate domains and local catalogue are premises of the converse.']
        limits=['No arbitrary support/core or unrestricted target coverage.','No satisfying raw factor or UNSAT proof is asserted by this encoding claim.','No target automorphism, cyclic condition or sorting normalization is assumed.','Known-positive SRG243 controls have different parameters; no full-Gram positive factor for this research support is known.']
        verification=[]
        for i,((name,pin,status,verifier),a)in enumerate(zip(REPORTS,audits)):
            verification.append(dict(claim_revision=1,verifier=verifier,method='independent_artifact_check'if i==0 else'independent_derivation',command_or_audit=name,timestamp=a['timestamp'],outcome='PASS',scope='Exact '+variant+' raw-cell recipe and full CNF bytes, all actual clauses and saved artifact/section bindings.'if i==0 else 'Written necessity/converse with independently enumerated complete local/count domains, all omitted zero-Gram entries and gadget premises; complete CNF bytes are the separate first review.',artifact_hashes=hashes,shared_components=a.get('shared_components',a.get('trusted_components')),controls=['Exact positive and corrupt controls in this immutable report; no new checking performed by the registrar.'],limitations=limits+(['The independently authenticated count-master prefix is reused.' ]if i==0 else['No full formula reconstruction in the semantic review.'])))
        assert cid not in {c['id']for c in data['claims']}
        data['claims'].append(dict(id=cid,revision=1,statement=statement,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),assumptions=assumptions,dependencies=deps,evidence=evidence.copy(),verification=verification,limitations=limits,created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Independent internal reviews only; no external peer review.'},reproducibility=dict(manifest=evidence[0])));ids.append(cid)
    assert data['claims'][:-2]==old['claims']and data['artifacts'][:len(old['artifacts'])]==old['artifacts'];data['updated_at']=now
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_twentyfifth_direct_encoding_registration';out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    receipt=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),registrar_sha256=sha(Path(__file__).relative_to(ROOT)),checked_input_bindings=inputs,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),new_claim_ids=ids,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,registrar_performs_mathematical_verification=False,validation=validation,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=2)))
if __name__=='__main__':main()
