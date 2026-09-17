"""One-time current ledger migration; historical ledger is read-only."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481'
REVIEW='acceleration/results/20260917_independent_review'


def main():
    now=datetime.now(timezone.utc).isoformat()
    artifacts=[]
    def artifact(name,path,public=False):
        artifacts.append(dict(id=name,path=path,sha256=sha256((ROOT/path).read_bytes()).hexdigest(),
            availability='PUBLIC' if public else 'LOCAL_ONLY',
            retrieval=('https://github.com/ikuto32/conway-99-graph/blob/7518ebcec78589fe7f8b068ee7a1dd87e8bf8d42/'+path) if public else 'Workspace relative path; publication pending on codex/fresh-star-audit-20260917.',
            unavailable_reason=None if public else 'New local artifact, not yet published.'))
        return name
    manifest=artifact('fresh-wave-manifest','acceleration/results/20260917_resume/wave_manifest.json')
    baseline=artifact('baseline-original-audit',BASE+'/audit.json',True)
    independent=artifact('baseline-independent-matrix',REVIEW+'/baseline_and_matrix.json')
    domains=artifact('baseline-fresh-domains',REVIEW+'/baseline_fresh_domain_replay.json')
    selection=artifact('fresh-selected-manifest','acceleration/results/20260917_fresh_star_shortlist/manifest.json')
    literature=artifact('literature-refresh','docs/LITERATURE_20260917.md')
    audit=json.loads((ROOT/BASE/'audit.json').read_bytes())
    review=json.loads((ROOT/REVIEW/'baseline_and_matrix.json').read_bytes())
    assumptions=['Root 0 and vertices 1..14 are fixed as seven matched root-neighbor pairs.',
        'Outer vertices are ordered by two distinct root groups and their two binary signs.',
        'The specified 168 overlap edges are present; all other overlapping-support and same-fiber edges are absent.',
        'Only the 1680 disjoint-support pairs may vary; no nontrivial graph automorphism is assumed.']
    limitation=['This fixed-configuration exclusion does not exclude all overlap assignments or prove unrestricted nonexistence.',
        'The star objective is a continuous relaxation, not distance to an SRG or target-wide progress.']
    def claim(id,statement,kind,evidence):
        return dict(id=id,revision=1,statement=statement,kind=kind,basis=['COMPUTED'],status='CANDIDATE',review_state='CLEAR',
            scope=dict(description='Only explicitly fixed complete overlap configurations, with same-fiber edges absent.',unrestricted_target=False,target_resolution='NONE'),
            assumptions=assumptions,dependencies=[],evidence=evidence,verification=[],limitations=limitation,
            created_at=now,updated_at=now,unknowns={'external_source':'Current project claim; no historical claim imported.'},
            external_source=None,reproducibility={'manifest':manifest})
    def fraction(x):
        return x['numerator']+'/'+x['denominator']
    c=claim('C-STAR-BASELINE-18481',
        'For the fixed labeled overlap assignment with SHA256 bd7329b3b6967b9559a7f8873bf25449f438fbfbbd00789c3ededf0ef986b9ea, the minimum of STAR_SIMPLEX_RECIPROCITY_PLUS_LINEAR_CAP_VIOLATIONS over a probability simplex on each of its 84 complete original star domains lies in ['+
        fraction(audit['exact_dual_lower'])+', '+fraction(audit['exact_primal_upper'])+']; the positive lower endpoint excludes every srg(99,14,1,2) completion of this fixed assignment under the stated absent-edge assumptions.',
        'exclusion',[baseline,independent,domains,manifest])
    c['status']='VERIFIED'
    lookup={a['id']:a['sha256'] for a in artifacts}
    c['verification']=[dict(claim_revision=1,verifier='independent_verifier agent',method='independent_artifact_check',
        command_or_audit=REVIEW+'/baseline_and_matrix.json and '+REVIEW+'/baseline_fresh_domain_replay.json; exact commands and source hashes are in those records.',
        timestamp=review['timestamp'],outcome='PASS',scope='Exact fixed-K rational interval and positive integer exclusion, with freshly independently enumerated complete domains.',
        artifact_hashes={k:lookup[k] for k in (baseline,independent,domains)},
        shared_components=['Python standard library','Hash-bound raw artifacts','Reviewed independent domain enumerator; separate from Rust producer'],
        controls=['One historical valid certificate; six corruption controls in separate checker','Four exact matrix-identity fixtures','Fresh complete84-domain replay and635 pair deletion checks'],
        limitations=['No unrestricted coverage or independent normalization theorem claimed.'])]
    selected=json.loads((ROOT/'acceleration/results/20260917_fresh_star_shortlist/manifest.json').read_bytes())
    indices=[r['proposal_index'] for r in selected['selected_candidates']]
    fresh=claim('C-FRESH-STAR-16-EXCLUSIONS',
        'For every one of the 16 distinct labeled overlap assignments selected by the frozen union-16 rule in fresh-selected-manifest (proposal indices '+str(indices)+'), no srg(99,14,1,2) completion exists under the stated fixed present/absent-edge assumptions.',
        'exclusion',[selection,manifest])
    fresh['unknowns']['independent_verification']='The wave is executing; complete results and third-path review are pending.'
    lit=claim('C-LITERATURE-20260917-ABSTRACTS',
        'The focused searches and abstract/version inspections on 2026-09-17 recorded in literature-refresh identified no target resolution within the three inspected arXiv abstracts (2608.11211v1,2604.23037v2,2608.19410v1).',
        'literature finding',[literature])
    lit.update(basis=['CITED'],assumptions=[],reproducibility=None,
        scope=dict(description='Only the named queries and three abstract/version pages accessed on 2026-09-17.',unrestricted_target=False,target_resolution='NONE'),
        limitations=['No full-paper theorem audit or comprehensive worldwide literature search.','First-page date metadata inconsistency remains unresolved.'],
        unknowns={'external_source':'Not imported from historical ledger.','reproducibility':'Web queries, versioned URLs and inspected sections are in the literature note; no computation.','independent_review':'Not independently reviewed.'})
    ledger=dict(schema_version=1,updated_at=now,
        archives=[dict(id='legacy@85e705c',repository='https://github.com/YesterdaysLemon/conway-99-research',commit='85e705cc6c2a14d123120c93a847e30aaab1789e',path='CLAIMS.yaml')],
        artifacts=artifacts,claims=[c,fresh,lit],target=dict(status='UNKNOWN',supporting_claims=[],external_review='No target-resolution artifact submitted for external review.',overall_search_coverage=None,coverage_reason='Overall search coverage: UNKNOWN; no validated denominator.'))
    with (ROOT/'CLAIMS.yaml').open('x',encoding='utf-8') as stream:
        yaml.safe_dump(ledger,stream,sort_keys=False,allow_unicode=True,width=110)


if __name__=='__main__':
    main()
