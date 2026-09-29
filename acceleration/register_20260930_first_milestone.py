"""Register exact independently reviewed statements; no mathematical self-approval."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import yaml
import validate_claims as registry

ROOT = Path(__file__).resolve().parents[1]
BASE = 'acceleration/results/20260930_'


def digest(p):
    return sha256((ROOT/p).read_bytes()).hexdigest()


def read(p):
    return json.loads((ROOT/p).read_bytes())


def main():
    ledger_path = ROOT/'CLAIMS.yaml'
    previous_bytes = ledger_path.read_bytes()
    previous = registry.read_ledger(ledger_path)
    data = registry.read_ledger(ledger_path)
    artifacts, claims = [], []
    now = datetime.now(timezone.utc).isoformat()

    def artifact(aid, p):
        result = dict(id=aid,path=p,sha256=digest(p),availability='LOCAL_ONLY',retrieval='Repository-relative workspace path; immutable publication pointer will be assigned after push.',unavailable_reason='New local evidence has not yet been assigned a confirmed public commit.')
        artifacts.append(result)
        return result

    def check_bindings(report):
        for p,h in report.get('inputs_sha256',report.get('input_hashes',{})).items():
            assert digest(Path(p)) == h, p

    def add(cid, statement, kind, scope, assumptions, dependencies, evidence, manifest, audit_path, report, shared, limitations, controls):
        assert cid not in {c['id'] for c in previous['claims']}
        check_bindings(report)
        records = [artifact(aid,p) for aid,p in evidence.items()]
        hashes = {a['id']:a['sha256'] for a in records}
        shared = [shared] if isinstance(shared, str) else shared
        claims.append(dict(id=cid,revision=1,statement=statement,kind=kind,basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
            scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),assumptions=assumptions,dependencies=dependencies,
            evidence=list(evidence),verification=[dict(claim_revision=1,verifier=report['verifier'],method='independent_artifact_check',
                command_or_audit=audit_path,timestamp=report['timestamp'],outcome='PASS',scope=scope,artifact_hashes=hashes,
                shared_components=shared,controls=controls,limitations=limitations)],limitations=limitations,
            created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Current-project review; no external peer review or novelty claim.'},reproducibility={'manifest':manifest}))

    path=BASE+'independent_review/eight_domains_claim_binding.json'; r=read(path)
    assert r['status']=='INDEPENDENT_EIGHT_COORDINATE_ALL84_BINDING_PASS' and r['recommendation']=='VERIFIED'
    assert (r['centers'],r['domain_choices'],r['old_embedded_choices'])==(84,2290122,879449)
    add(r['claim_id'],r['statement'],'encoding',r['scope'],['Exactly the fixed family in the raw baseline and manifest; no automorphism assumption.'],
        [dict(id='C-PARTIAL-K-SIX-COORDINATE-DOMAINS',revision=1,relation='verification_dependency')],
        {'eight-domains-binding':path,'eight-domains-manifest':BASE+'eight_domains/run01/manifest.json','eight-domains-summary':BASE+'eight_domains/run01/summary.json',
         'eight-old17-audit':BASE+'independent_review/eight_old17_full01/summary.json','eight-new67-audit':BASE+'independent_review/eight_new67_full01/summary.json'},
        'eight-domains-manifest',path,r,r['shared_components'],r['limitations'],['Six restricted-universe exhaustive full-99 controls, graph corruptions, completeness corruptions, and missing/duplicate coverage controls detailed in audits.'])

    path=BASE+'independent_review/eight_transfer_witness_binding.json'; r=read(path)
    assert r['recommendation']=='VERIFIED' and r['checked_witness_stars']==84 and r['support_bound_upper_numerator']==-3762780
    add(r['claim_id'],r['statement'],'empirical/engineering result',r['scope'],['Only the frozen 10000-last coefficient vector extended by zero on newly freed reciprocity edges.'],
        [dict(id='C-PARTIAL-K-EIGHT-COORDINATE-DOMAINS',revision=1,relation='uses_result')],
        {'eight-transfer-audit':path,'eight-transfer-manifest':BASE+'eight_transfer_screen/run01/manifest.json','eight-transfer-witness':BASE+'eight_transfer_screen/run01/summary.json'},
        'eight-transfer-manifest',path,r,r['shared_code'],r['limitations'],['Positive and mutated raw-star, matching, weight and score controls documented in independent audit.'])

    path=BASE+'rook_cell_independent/audit.json'; r=read(path)
    assert r['status']=='PASS' and len(r['claim_bindings'])==2
    for index,binding in enumerate(r['claim_bindings']):
        prefix='rook-cell-compat' if index==0 else 'rook-cell-census'
        evidence={prefix+'-audit':path,prefix+'-manifest':BASE+'rook_cell_factors/manifest.json',prefix+'-derivation':BASE+'rook_cell_independent/AUDIT.md',
                  prefix+'-raw':BASE+('rook_cell_factors/local_witness.json' if index==0 else 'rook_cell_factors/factor_masks.txt')}
        add(binding['id'],binding['statement'],'mathematical result' if index==0 else 'empirical/engineering result',binding['scope'],
            ['The necessity statement is conditional on induced rook9 containment; the witness satisfies only its declared local subsystem.'] if index==0 else ['Fixed labelled K10 minus the explicitly listed perfect matching.'],
            [dict(id='C-ROOK-NINE-REGULAR-SET-ENCODING',revision=1,relation='uses_result')] if index==0 else [],
            evidence,prefix+'-manifest',path,r,['Python standard library; raw artifacts only; independent subset Hamilton-cycle DP and component partition convolution.'],r['limitations'],
            ['Known count controls and nine corrupted witness variants checked; full89,000 masks validated and independently counted.'])

    path=BASE+'independent_review/rook_frozen_window_v2.json'; r=read(path)
    assert r['status']=='INDEPENDENT_FROZEN_ROOK_WINDOW_EXCLUSION_PASS' and r['rejected_edges']==167 and len(r['row_obstructions'])==8
    add(r['claim_id'],r['statement'],'exclusion',r['scope'],['Every adjacency and absence of the raw partial window, its root-cell placement, and the induced rook scaffold remain fixed.'],r['dependencies'],
        {'rook-frozen-window-audit':path,'rook-frozen-window-manifest':BASE+'rook_complete_window/manifest.json','rook-frozen-window-raw':BASE+'rook_joint/joint_witness.json','rook-frozen-window-obstruction':BASE+'rook_complete_window/single_edge_filter.json'},
        'rook-frozen-window-manifest',path,r,r['shared_components'],r['limitations'],r['controls'])

    lit=artifact('literature-20260930-audit',BASE+'literature_audit/AUDIT.md')
    claims.append(dict(id='C-LITERATURE-20260930-PRIMARY-SOURCE-AUDIT',revision=1,
        statement='The explicitly logged primary-source search on2026-09-29UTC/2026-09-30JST identified no target resolution in its inspected sources; it located arXiv2608.11211v2 revised2026-09-18 and recorded a conflict between its order7 discussion and older primary-source automorphism restrictions.',
        kind='literature finding',basis=['CITED'],status='CANDIDATE',review_state='CLEAR',scope=dict(description='Dated bounded search and specified sections only; no claim that the worldwide problem is open.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=[],dependencies=[],evidence=[lit['id']],verification=[],limitations=['Single literature reviewer; no independent full-source recheck or historical computational replay.','Source-byte hashes unavailable; versioned URLs and exact inspection boundaries recorded.'],
        created_at=now,updated_at=now,external_source=None,reproducibility=None,unknowns={'external_source':'Multiple primary sources listed in the dated audit, not an imported archive claim.','reproducibility':'Web search results and dynamic pages are not frozen; precise queries, versions and access failures are recorded in the audit.'}))
    data['artifacts'].extend(artifacts)
    data['claims'].extend(claims)
    data['updated_at']=now
    result=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',previous)
    assert result['valid'], result['errors']
    out=ROOT/(BASE+'resume')
    with (out/'claims_before_first_milestone.yaml').open('xb') as f: f.write(previous_bytes)
    assert ledger_path.read_bytes()==previous_bytes
    ledger_path.write_text(yaml.safe_dump(data,sort_keys=False,width=110),encoding='utf-8')
    receipt=dict(timestamp=now,command=[sys.executable,*sys.argv],working_directory=str(ROOT),registrar_sha256=digest(Path(__file__)),
        previous_ledger_sha256=sha256(previous_bytes).hexdigest(),ledger_sha256=digest('CLAIMS.yaml'),new_claim_ids=[c['id'] for c in claims],
        validation=result,registrar_performs_mathematical_verification=False,target_resolution=data['target']['status'])
    with (out/'first_milestone_registration.json').open('x',encoding='utf-8') as f: json.dump(receipt,f,indent=2)
    print(json.dumps(dict(claim_ids=receipt['new_claim_ids'],target_resolution=data['target']['status'])))


if __name__=='__main__':
    main()
