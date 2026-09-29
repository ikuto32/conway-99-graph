"""Register separately checked sixth-wave results after exact editorial migration."""
from datetime import datetime,timezone
from hashlib import sha256
import copy
import json
from pathlib import Path
import sys
import yaml
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_independent_review/'
OUT=ROOT/'acceleration/results/20260930_sixth_registration'
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())
def dep(cid,relation):return dict(id=cid,revision=1,relation=relation)
def main():
    ledger=ROOT/'CLAIMS.yaml';before=ledger.read_bytes();old=registry.read_ledger(ledger);data=copy.deepcopy(old)
    gate_path='acceleration/results/20260930_independent_review/editorial_migration_applied/summary.json'
    gate=read(gate_path)
    if digest(ROOT/gate_path)!='ff28b33d9e23e425669a82ef6083f833ffd2fd7f8d8b5504eeda78d589d7a383':raise ValueError('migration application audit identity changed')
    if gate['status']!='INDEPENDENT_APPLIED_EDITORIAL_MIGRATION_PASS' or gate['inputs_sha256']['CLAIMS.yaml']!=digest(ledger):raise ValueError('actual migration approval absent or stale')
    specs=[
      ('pair-map-census','eight_pair_relabelings01/summary.json','390e542321011be1f9dd9ef76c6096d473332f45ca7107ad41f9c54d40ac2a38',False),
      ('four-branch-cover','unrestricted_four_branch_cover/summary.json','ae44765cab81327f050b27d3ab75e6b952f44d5387a054a38029516e71516d34',True),
      ('pair-equalities','unrestricted_pair_equalities_v2/summary.json','1ebbff5e7313a97de6ce86aef3a9047ef856aae7ef0e8b1258eec216f1840237',True),
      ('modular-ranks','modular_rank_exact/theorem.json','8ad22ca9d03b86cdffb8d3be8e5de652b115ff06738add262b5ef5abca6cf9ac',True),
      ('modular-minors','modular_rank_exact/summary.json','6841e5c90dc17d519e61c49af8d7d8273f1fb29015e152cad91117143fd2b3d0',False),
      ('strengthened-composition','strengthened_four_branch_composition/summary.json','6610480e8715e7676d0ed9a78aed45b23eddb40bdedc47dde55ec9ed75e7b329',True),
      ('editorial-checker-v2','editorial_migration_corrected/summary.json','6bfb4613a559e8c5e05e8f5d4022ce7a59e5b0b157c316cc00ceb736fe6a545c',False),
    ]
    now=datetime.now(timezone.utc).isoformat();added=[]
    def artifact(aid,path,expected=None):
        value=digest(ROOT/path)
        if expected and value!=expected:raise ValueError('changed audit '+path)
        if aid in {a['id'] for a in data['artifacts']}:raise ValueError('duplicate artifact '+aid)
        data['artifacts'].append(dict(id=aid,path=path,sha256=value,availability='LOCAL_ONLY',retrieval='Workspace-relative independently checked report; its pinned manifests and companion recovery recipes preserve exact inputs.',unavailable_reason='Public evidence commit not yet confirmed.'))
        return value
    for label,suffix,expected,unrestricted in specs:
        audit=B+suffix;r=read(audit)
        if digest(ROOT/audit)!=expected:raise ValueError('unexpected audit bytes '+audit)
        for path,value in r['inputs_sha256'].items():
            if digest(ROOT/path)!=value:raise ValueError('changed checked input '+path)
        aid=label+'-audit';bound={aid:artifact(aid,audit,expected)};extra=[]
        if label=='pair-map-census':
            addendum=B+'eight_pair_relabelings01/editorial_dependency_binding.json';extra_id=label+'-dependency-review'
            bound[extra_id]=artifact(extra_id,addendum,'5ba0860904e2699e1f9764b3aa973da3d39a250112bb662046b460244a3d682a');extra.append(extra_id)
            for d in r['dependencies']:d['revision']=2
        if label=='strengthened-composition':
            r.update(claim_id='C-UNRESTRICTED-STRENGTHENED-FOUR-BRANCH-COMPOSITION',claim_revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],statement='The four exact recorded CNFs, each with1186500variables and4141120clauses, consist of the complete unrestricted basebody followed by4662entailed equalityunits and the four appropriate branchunits. At least one is satisfiable if and only if the unrestricted target exists.',scope='Exactly the four prepared raw instances; complete byte composition and preservation of the prior unrestricted coverage equivalence. No solver answer.',dependencies=[dep('C-UNRESTRICTED-FULL99-PREFIX-CNF-ENCODING','encoding_equivalence'),dep('C-UNRESTRICTED-PAIR-EQUALITY-UNITS','uses_result'),dep('C-UNRESTRICTED-FOUR-BRANCH-COVER','coverage')])
        if label=='editorial-checker-v2':
            r.update(claim_id='C-CURRENT-REGISTRY-EDITORIAL-MIGRATION-CHECKS',claim_revision=1,kind='empirical/engineering result',basis=['COMPUTED'],statement='The exact corrected version2 registry checker passed the recorded independent code review, ten independent standalone-mode adversarial controls, and all56 saved suite tests; the original unapproved-limitations acceptance is rejected by the corrected checker.',scope='Exact frozen checker/schema/test bytes and enumerated finite engineering controls. This is not a formal proof of software correctness or mathematical claim verification.',dependencies=[])
        if not r['status'].startswith('INDEPENDENT_') or not r['status'].endswith('_PASS'):raise ValueError('nonpassing independent report')
        scope=r['scope'];limits=r['limitations']
        method='independent_derivation' if label=='modular-ranks' else 'independent_artifact_check'
        c=dict(id=r['claim_id'],revision=r['claim_revision'],statement=r['statement'],kind=r['kind'],basis=r['basis'],status='VERIFIED',review_state='CLEAR',scope=dict(description=scope,unrestricted_target=unrestricted,target_resolution='NONE'),assumptions=r.get('assumptions',['Exactly the frozen inputs, finite populations, and declared hypotheses in the bound report.','No nontrivial target automorphism is assumed.']),dependencies=r['dependencies'],evidence=[aid,*extra],verification=[dict(claim_revision=r['claim_revision'],verifier=r['verifier'],method=method,command_or_audit=audit,timestamp=r['timestamp'],outcome='PASS',scope=scope,artifact_hashes=bound,shared_components=r.get('shared_components',[]),controls=['Complete stated checks and calibrated positive/corrupted controls are enumerated in the immutable report; no sampled check is promoted to exhaustive coverage.'],limitations=limits)],limitations=limits,created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Internal checking only; external review has not occurred.'},reproducibility=dict(manifest=aid))
        if label=='pair-map-census':
            a=read(B+'eight_pair_relabelings01/editorial_dependency_binding.json')
            c['verification'].append(dict(claim_revision=1,verifier=a['verifier'],method='independent_artifact_check',command_or_audit=B+'eight_pair_relabelings01/editorial_dependency_binding.json',timestamp=a['timestamp'],outcome='PASS',scope=scope,artifact_hashes={extra[0]:bound[extra[0]]},shared_components=['Original mathematical census audit and explicitly reviewed editorial premise corrections.'],controls=['All47 original audit input hashes checked unchanged.'],limitations=['Dependency-impact binding only; no fresh census execution.']))
        if c['id'] in {x['id'] for x in data['claims']}:raise ValueError('existing claim '+c['id'])
        data['claims'].append(c);added.append(c['id'])
    data['updated_at']=now
    check=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old)
    if not check['valid']:raise ValueError(check['errors'])
    OUT.mkdir(parents=True,exist_ok=False);(OUT/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    if ledger.read_bytes()!=before:raise ValueError('concurrent ledger change')
    ledger.write_bytes(after);(OUT/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(ROOT),previous_ledger_sha256=sha256(before).hexdigest(),ledger_sha256=sha256(after).hexdigest(),new_claim_ids=added,validation=check,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(new_claims=len(added),claim_population=len(data['claims']),target_resolution='UNKNOWN')))
if __name__=='__main__':main()
