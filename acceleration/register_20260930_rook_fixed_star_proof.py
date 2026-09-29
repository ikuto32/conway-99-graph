"""Bind independently checked CNF equivalence and full DRAT proof to narrow claims."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import yaml
import validate_claims as validator

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'


def digest(p):return sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())


def main():
    ledger=ROOT/'CLAIMS.yaml';before=ledger.read_bytes();old=validator.read_ledger(ledger);data=validator.read_ledger(ledger)
    encoding_path=B+'rook_window_sat/independent_cnf_encoding.json';proof_path=B+'rook_sat_independent_proof/summary.json'
    encoding=read(encoding_path);proof=read(proof_path)
    assert encoding['recommendation']==proof['recommendation']=='VERIFIED'
    assert proof['status']=='INDEPENDENT_FIXED_ROOK_STAR_WINDOW_UNSAT_PASS' and proof['proof_lines']==781892
    assert proof['dependencies'][0]['id']==encoding['claim_id']
    assert any(r['name']=='main_complete_proof' and r['accepted'] and r['exit_code']==0 for r in proof['controls_and_replay'])
    for report in (encoding,proof):
        for p,h in report['inputs_sha256'].items():assert digest(Path(p))==h,p
    now=datetime.now(timezone.utc).isoformat();added=[]
    for label,r,audit,kind,manifest,deps in [
        ('rook-fixed-star-cnf',encoding,encoding_path,'encoding',B+'rook_window_sat/manifest.json',[dict(id='C-ROOK-NINE-REGULAR-SET-ENCODING',revision=1,relation='uses_result')]),
        ('rook-fixed-star-proof',proof,proof_path,'exclusion',B+'rook_sat_pilot/manifest.json',proof['dependencies'])]:
        evidence={label+'-audit':audit,label+'-manifest':manifest,label+'-model':B+'rook_window_sat/model.json',label+'-cnf':B+'rook_window_sat/instance.cnf',label+'-cnf-gzip':B+'rook_window_sat/instance.cnf.gz',label+'-cnf-summary':B+'rook_window_sat/summary.json'}
        if kind=='exclusion':evidence.update({label+'-raw':proof['proof_artifact'],label+'-gzip':B+'rook_sat_pilot/main/proof.drat.gz',label+'-recovery':B+'rook_sat_pilot/main/compressed_proof.json',label+'-checker-build':B+'rook_sat_independent_proof/checker_build/build_manifest.json',label+'-checker-source':B+'rook_sat_independent_proof/checker_build/drat-trim.c'})
        artifacts=[dict(id=i,path=p,sha256=digest(p),availability='LOCAL_ONLY',retrieval='Workspace-relative artifact; exact gzip recovery and checker sources are preserved alongside raw artifacts.',unavailable_reason='Not yet assigned confirmed immutable public retrieval; compiled checker and large raw files may remain local with reproducible source/recovery companions.') for i,p in evidence.items()]
        claim=dict(id=r['claim_id'],revision=r['claim_revision'],statement=r['statement'],kind=kind,basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
            scope=dict(description=r['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=['Only the exact labelled central star, its five internal matchings, rook9 scaffold and indicated free edges.','No graph automorphism or universal rook-containment assumption.'],
            dependencies=deps,evidence=list(evidence),verification=[dict(claim_revision=1,verifier=r['verifier'],method='independent_artifact_check',command_or_audit=audit,timestamp=r['timestamp'],outcome='PASS',scope=r['scope'],
                artifact_hashes={a['id']:a['sha256'] for a in artifacts},shared_components=r.get('shared_components',['Python standard library, pinned upstream DRAT checker with disclosed portability patch, MSVC compiler and Windows runtime']),
                controls=['Complete clause reconstruction and calibrated rook/cardinality/AND controls.' if kind=='encoding' else 'Fresh checker positive proof plus three corrupted empty-proof controls, then complete main trace replay.'],limitations=r['limitations'])],
            limitations=r['limitations'],created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Current-project internal independent review, not external peer review.'},reproducibility=dict(manifest=label+'-manifest'))
        assert claim['id'] not in {c['id'] for c in data['claims']}
        data['claims'].append(claim);data['artifacts'].extend(artifacts);added.append(claim['id'])
    data['updated_at']=now
    result=validator.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert result['valid'],result['errors']
    out=ROOT/(B+'resume')
    with(out/'claims_before_rook_fixed_star.yaml').open('xb')as f:f.write(before)
    assert ledger.read_bytes()==before
    ledger.write_text(yaml.safe_dump(data,sort_keys=False,width=110),encoding='utf-8')
    with(out/'rook_fixed_star_registration.json').open('x',encoding='utf-8')as f:json.dump(dict(timestamp=now,new_claim_ids=added,previous_ledger_sha256=sha256(before).hexdigest(),ledger_sha256=digest('CLAIMS.yaml'),validation=result,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN'),f,indent=2)
    print(json.dumps(dict(claims_added=added,target_resolution='UNKNOWN')))


if __name__=='__main__':main()
