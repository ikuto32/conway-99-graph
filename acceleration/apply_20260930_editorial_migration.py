"""Apply the exact independently reviewed clarification; preserve all evidence.

Requires the separate root engineering approval and two actual dependent-impact
reviews. This registrar is bookkeeping, not mathematical verification.
"""
from datetime import datetime, timezone
from hashlib import sha256
import copy
import json
from pathlib import Path
import sys
import yaml
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_independent_review/'
OUT=ROOT/'acceleration/results/20260930_editorial_migration_applied'
REVIEW=B+'automorphism_assumption_editorial/summary.json'
SNAP=B+'automorphism_assumption_editorial/CLAIMS.reviewed.yaml'
ENGINEERING=B+'editorial_migration_corrected/summary.json'
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def load(name):return json.loads((ROOT/name).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes()
    if digest(path)!='20b3ee7d9c13c5142205492832a85ba877f35492ab26c0db1fdd5e3b9ba7e168':raise ValueError('current ledger differs from exact reviewed snapshot')
    engineering=load(ENGINEERING)
    if engineering['status']!='INDEPENDENT_CORRECTED_EDITORIAL_MIGRATION_CHECKER_PASS':raise ValueError('root independent engineering gate absent')
    for name,value in engineering['inputs_sha256'].items():
        if digest(ROOT/name)!=value:raise ValueError('changed engineering input '+name)
    review=load(REVIEW)
    if digest(ROOT/REVIEW)!='1584c3c0ef52fdee47c056fec317260d6952fdbd46a9e47e0742ce1f6d711388':raise ValueError('changed semantic review')
    reports=[('editorial-dependent-dual',B+'editorial_dependent_impact/dual_gram.json','b833aa2b8b444130b85119d1e753203882f962e3939e9bc3e9b197ea7ea94ef7'),
             ('editorial-dependent-w81',B+'editorial_dependent_impact/w81_nogood.json','44e397965694458dfa45e6884f7ea0961de9c84c775c3806e20c15a39cc90564')]
    old=registry.read_ledger(path);data=copy.deepcopy(old);claims={c['id']:c for c in data['claims']}
    now=datetime.now(timezone.utc).isoformat()
    def artifact(aid,name):
        if aid in {a['id'] for a in data['artifacts']}:raise ValueError('already registered '+aid)
        data['artifacts'].append(dict(id=aid,path=name,sha256=digest(ROOT/name),availability='LOCAL_ONLY',retrieval='Exact workspace-relative immutable audit; public commit not yet confirmed.',unavailable_reason='Publication pending.'))
    rid,sid='editorial-assumption-review','editorial-assumption-snapshot'
    artifact(rid,REVIEW);artifact(sid,SNAP)
    migration=dict(id='M-AUTOMORPHISM-ASSUMPTION-CLARIFICATION-20260930',version=1,kind='REVIEWED_ASSUMPTION_CLARIFICATION',review_artifact=dict(artifact=rid,sha256=digest(ROOT/REVIEW)),snapshot_artifact=dict(artifact=sid,sha256=digest(ROOT/SNAP)),claims=[])
    affected={r['claim_id'] for r in review['records']}
    for row in review['records']:
        c=claims[row['claim_id']]
        if registry.canonical_claim_digest(c)!=row['reviewed_claim_sha256']:raise ValueError('changed original claim')
        migration['claims'].append(dict(claim_id=c['id'],from_revision=c['revision'],to_revision=c['revision']+1,old_claim_sha256=row['reviewed_claim_sha256'],old_assumptions=c['assumptions'],new_assumptions=row['recommended_assumptions']))
        c['revision']+=1;c['assumptions']=row['recommended_assumptions'];c['updated_at']=now;c['evidence'] += [rid,sid]
        c['verification'].append(dict(claim_revision=c['revision'],verifier=review['verifier'],method='editorial_impact_review',command_or_audit=REVIEW,timestamp=review['timestamp'],outcome='PASS',scope=c['scope']['description'],artifact_hashes={rid:digest(ROOT/REVIEW),sid:digest(ROOT/SNAP)},shared_components=['Original independently checked mathematical evidence is retained; it is not relabelled as a fresh replay.'],controls=['Exact seventeen old claims and approved replacement lists authenticated against immutable review and snapshot.'],limitations=['Editorial clarification only. No mathematical statement, scope, assumption of symmetry or asymmetry, or artifact bytes changed.']))
    for aid,name,expected in reports:
        if digest(ROOT/name)!=expected:raise ValueError('dependent review changed')
        r=load(name)
        if r['status']!='INDEPENDENT_EDITORIAL_DEPENDENCY_IMPACT_PASS':raise ValueError('dependent review did not pass')
        for inp,value in r['inputs_sha256'].items():
            if digest(ROOT/inp)!=value:raise ValueError('dependent impact input changed '+inp)
        c=claims[r['claim_id']]
        if registry.canonical_claim_digest(c)!=r['old_claim_sha256']:raise ValueError('dependent claim changed')
        artifact(aid,name);c['evidence'].append(aid);c['revision']=r['claim_revision'];c['dependencies']=r['recommended_dependencies'];c['updated_at']=now
        c['verification'].append(dict(claim_revision=c['revision'],verifier=r['verifier'],method='independent_artifact_check',command_or_audit=name,timestamp=r['timestamp'],outcome='PASS',scope=c['scope']['description'],artifact_hashes={aid:expected},shared_components=r['shared_components'],controls=['Actual independent dependency-use review and exact literal arithmetic controls enumerated in the bound report.'],limitations=r['limitations']))
        affected.add(c['id'])
    for c in data['claims']:
        for dependency in c['dependencies']:
            if dependency['id'] in affected:dependency['revision']=claims[dependency['id']]['revision']
    data['schema_version']=2;data['editorial_migrations']=[migration];data['updated_at']=now
    check=registry.validate(data,ROOT,load('docs/claims.schema.json'),'available',old)
    if not check['valid']:raise ValueError(check['errors'])
    OUT.mkdir(parents=True,exist_ok=False)
    (OUT/'CLAIMS.before.yaml').write_bytes(before)
    result=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    if path.read_bytes()!=before:raise ValueError('concurrent ledger change')
    path.write_bytes(result);(OUT/'CLAIMS.after.yaml').write_bytes(result)
    report=dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(ROOT),previous_sha256=sha256(before).hexdigest(),ledger_sha256=sha256(result).hexdigest(),editorial_claims=17,separately_reviewed_dependents=2,affected_claim_ids=sorted(affected),new_mathematical_claims=0,engineering_review=ENGINEERING,engineering_review_sha256=digest(ROOT/ENGINEERING),validation=check)
    (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(affected_claims=len(affected),new_mathematical_claims=0,valid=check['valid'])))
if __name__=='__main__':main()
