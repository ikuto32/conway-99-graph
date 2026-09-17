"""Integrate separate whole16 and finite cyclic-bank reviews."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
REV='acceleration/results/20260917_independent_review/'


def main():
    lp=ROOT/'CLAIMS.yaml'; snapshot=ROOT/'acceleration/results/20260917_resume/claims_before_whole16_and_cyclic.yaml'
    assert not snapshot.exists()
    ledger=yaml.safe_load(lp.read_bytes())
    whole=json.loads((ROOT/REV/'whole16_scope.json').read_bytes())
    cyclic=json.loads((ROOT/REV/'matching_cut_cyclic.json').read_bytes())
    assert whole['status']=='INDEPENDENT_WHOLE_FRESH_STAR_SHORTLIST_AUDIT_PASS'
    assert cyclic['status']=='INDEPENDENT_CYCLIC_SIGN_CUT_APPLICATION_PASS'
    for report in (whole,cyclic):
        for path,h in report['inputs_sha256'].items():assert sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    groups={
        'whole16':{'scope':REV+'whole16_scope.json','raw':REV+'whole16_raw.json',
            'execution-provenance':REV+'whole16_execution_receipt.json',
            'manifest':'acceleration/results/20260917_whole_shortlist_execution/manifest.json',
            'checkpoint':'acceleration/results/20260917_whole_fresh_v2_checkpoint.json'},
        'cyclic-cuts':{'audit':REV+'matching_cut_cyclic.json',
            'manifest':'acceleration/results/20260917_matching_cut_cyclic/manifest.json',
            'summary':'acceleration/results/20260917_matching_cut_cyclic/summary.json'}}
    for prefix,items in groups.items():
        for name,path in items.items():ledger['artifacts'].append(dict(id=prefix+'-'+name,path=path,
            sha256=sha256((ROOT/path).read_bytes()).hexdigest(),availability='LOCAL_ONLY',
            retrieval='Workspace relative path; awaiting publication on draft PR1.',unavailable_reason='New local artifact, not yet published.'))
    hashes={a['id']:a['sha256'] for a in ledger['artifacts']}; now=datetime.now(timezone.utc).isoformat()
    items=[]
    for binding in whole['claim_bindings']:
        indices=', '.join(map(str,binding['indices']))
        statement=('For each of the16 labeled whole-family assignments with indices '+indices+
            ', no srg(99,14,1,2) completes its prescribed present and absent edges, by its independent positive exact original-star lower bound.')
        if binding['id'].endswith('NO-IMPROVEMENT'):
            statement=('For all16 labeled whole-family assignments with indices '+indices+
                ', the exact original-domain STAR_SIMPLEX_RECIPROCITY_PLUS_LINEAR_CAP_VIOLATIONS lower bound exceeds the incumbent18481 upper bound; none improves that objective.')
        items.append((binding['id'],statement,binding['scope'],binding.get('dependencies',[]),whole,'whole16',
            ['Fixed hash-bound overlap assignment and prescribed absent edges for each selected case.'],
            ['Independent third-path controls, full99 coefficients and rational interval checks; all16 selected cases pass.'],
            ['Conditional fixed configurations only; no unrestricted coverage.','Prior independently exhaustive domain audits are reused by exact hashes.']))
    items.append((cyclic['claim_id'],
        'On the frozen29 records with747064 original local choices, the union of14336 distinct positive clauses obtained from16 approved clauses under exactly7 cyclic root-group shifts and128 sign masks removes exactly324 choices, the same identity-clause removal set, hence adds zero removals and leaves every vertex domain nonempty.',
        'Only the exact896 scaffold-preserving coordinate maps and29 named original-domain records; units are(candidate record, outer vertex, original domain ID).',
        cyclic['dependencies'],cyclic,'cyclic-cuts',['The approved16 base clauses and frozen29 corpus; no nontrivial graph automorphism is assumed.'],
        [c['name']+': '+c['outcome'] for c in cyclic['controls']],cyclic['limitations']))
    for id,statement,scope,deps,report,group,assumptions,controls,limits in items:
        assert not any(c['id']==id for c in ledger['claims'])
        evidence=[group+'-'+name for name in groups[group]]
        ledger['claims'].append(dict(id=id,revision=1,statement=statement,
            kind='exclusion' if id.endswith('EXCLUSIONS') else 'mathematical result',basis=['DERIVED','COMPUTED'],
            status='VERIFIED',review_state='CLEAR',scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),
            assumptions=assumptions,dependencies=deps,evidence=evidence,
            verification=[dict(claim_revision=1,verifier='independent_verifier agent',method='independent_artifact_check',
                command_or_audit=groups[group].get('scope',groups[group].get('audit')),timestamp=report['timestamp'],outcome='PASS',
                scope=scope,artifact_hashes={e:hashes[e] for e in evidence},shared_components=report['shared_trusted_components'],
                controls=controls,limitations=limits)],limitations=limits,created_at=now,updated_at=now,
            unknowns={'external_source':'New current-project reviewed result.'},external_source=None,
            reproducibility={'manifest':group+'-manifest'}))
    snapshot.write_bytes(lp.read_bytes());ledger['updated_at']=now
    lp.write_text(yaml.safe_dump(ledger,sort_keys=False,width=110),encoding='utf-8')


if __name__=='__main__':main()
