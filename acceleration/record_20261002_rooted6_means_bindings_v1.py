"""Bind two exact scoped revisions to the completed independent means review.

No ledger mutation and no new mathematical calculation or theorem promotion.
"""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20261002_independent_review/rooted6_means02'
REPORT=BASE+'/summary.json'
EXPECTED='ffd497c6afacb9173bcb215eceab7603e7530d18d9c4a51dad6ea0e7d8e1d025'

def digest(path):
    with (ROOT/path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
    assert digest(REPORT)==EXPECTED
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report['status']=='INDEPENDENT_ROOTED6_PER_VERTEX_GLOBAL_MEANS_V2_PASS'
    assert report['verifier']=='/root/checkpoint_audit' and report['producer']=='/root/structural'
    hashes=dict(report['inputs_sha256']);hashes.update(report['outputs_sha256']);hashes[REPORT]=EXPECTED
    for path,want in hashes.items():assert digest(path)==want,(path,want)
    now=datetime.now(timezone.utc).isoformat()
    manifest=json.loads((ROOT/BASE/'manifest.json').read_bytes())
    controls={'written_universal_proof':report['written_proof'],
              'written_proof_sha256':hashes[report['written_proof']],
              'finite_controls_are_not_universal_proof':True,
              'fixture_records':report['fixture_records'],
              'nonzero_patterns':[8024,15540,8025],
              'extra_edge_completions':256,'specific_negative_controls':19,
              'controls_artifact':BASE+'/controls.json','controls_sha256':hashes[BASE+'/controls.json'],
              'all_saved_relaxation_corners_checked':4,'all_derived_rows_per_corner':4,
              'profiles_excluded':0}
    common={'revision':1,'claim_revision':1,'basis':['DERIVED','COMPUTED'],
            'status':'VERIFIED','review_state':'CLEAR','verifier':report['verifier'],
            'producer':report['producer'],'method':'independent_derivation',
            'created_at':now,'updated_at':now,'verification_timestamp':report['timestamp'],
            'source_commit':report['source_commit'],'command':manifest['command'],'cwd':manifest['cwd'],
            'python':manifest['python_version'],'inputs_sha256':hashes,'report':REPORT,'report_sha256':EXPECTED,
            'artifacts':[{'path':p,'sha256':h} for p,h in hashes.items()],
            'shared_components':manifest['shared_components'],
            'controls':controls,'limitations':report['limitations'],
            'unknowns':{'external_review':None,'external_review_reason':'Independent internal written/artifact review only.',
                        'target_existence':'UNKNOWN','historical_novelty':None,
                        'historical_novelty_reason':'Archive overlap disclosed; no novelty assessment claimed.'}}
    theorem={**common,'id':'C-UNRESTRICTED-ROOTED6-PER-VERTEX-GLOBAL-PRISM-MEAN-IDENTITIES',
      'kind':'mathematical_result','statement':report['statement'],
      'scope':{'description':'Universal necessary pervertex/global identities for every finite simple srg(n,k,1,2) with nonedges. All counts use actual ordered nonedges and unordered four-subsets, and induced prism sixsets once; no graph automorphism or prism-absence premise. This theorem does not fix individual root profiles or resolve the target.',
               'unrestricted_target':True,'target_resolution':'NONE'},
      'assumptions':['Finite simple srg(n,k,1,2), n-k-1>0; exact lambda1/mu2 and integer adjacency.',
                     'a,b are the free-label orbits of rooted masks8024,15540, roots ordered and other four vertices an unordered subset.',
                     'T_u counts induced triangular-prism sixsets containing u once; T counts these sixsets once.',
                     'No induced-prism absence, nontrivial graph automorphism, vertex transitivity or equal root profiles is assumed.'],
      'dependencies':[{'id':'C-UNRESTRICTED-ROOTED6-NONEDGE-NECESSARY-SYSTEM-NULLSPACE','revision':1,'relation':'normalization',
                       'reason':'Literal current rooted6 variable indices552/566 bind a/b to masks8024/15540. Its target-specific rank result is not a premise of the universal bijection theorem.'}],
      'premise_state':{'no_induced_triangular_prism':'NOT_ASSUMED','reason':'The exact prism terms remain in both identities.'}}
    conditional_statement=('For every actual ordered nonedge(u,v) in any hypothetical prism-free srg(99,14,1,2), '
      'the pinned rooted7 necessary-operator aggregates satisfy exactly four equations: for anchor0 with nonadjacent '
      'partitions0,2 and anchor1 with partitions0,1, the coordinate0 aggregate sum is168-a(u,v) and the coordinate1 '
      'sum is84-b(u,v). All four already saved exact rooted7 corner vectors satisfy those four rows; no graph '
      'realization or profile exclusion follows.')
    rows={**common,'id':'C-PRISMFREE-ROOTED7-PER-VERTEX-MEAN-NECESSARY-ROWS',
      'kind':'encoding','statement':conditional_statement,
      'scope':{'description':'Four conditional necessary equations for the exact existing rooted7 aggregate variables, at every actual ordered target nonedge. Prism absence remains UNKNOWN. Literal saved-corner survival is a finite relaxation result only; no profile exclusion, graph construction or target nonexistence.',
               'unrestricted_target':False,'target_resolution':'NONE'},
      'assumptions':['Hypothetical simple srg(99,14,1,2) and an actual ordered nonadjacent vertex pair.',
                     'No induced triangular prism anywhere in that hypothetical target; this premise remains UNKNOWN.',
                     'Exact existing rooted7 aggregate definitions and rooted6 axes a=mask8024,b=mask15540.',
                     'No automorphism or equal root profiles; excluded other primary root contributes its exact a/b count.'],
      'dependencies':[{'id':theorem['id'],'revision':1,'relation':'uses_result'},
                      {'id':'C-PRISMFREE-ROOTED7-MARKED-REROOT-NECESSARY-ENCODING','revision':1,'relation':'uses_result'},
                      {'id':'C-PRISMFREE-ORDERED-NONEDGE-ROOTED6-INTEGER-DOMAIN','revision':1,'relation':'normalization'}],
      'premise_state':{'no_induced_triangular_prism':'UNKNOWN',
                       'reason':'The general identities retain prism counts; only their conditional specialization yields the four rows.'}}
    for name,record in [('universal_claim_binding.json',theorem),('conditional_rows_claim_binding.json',rows)]:
        path=ROOT/BASE/name
        with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(record,stream,indent=2);stream.write('\n')
        print(json.dumps({'id':record['id'],'revision':1,'path':path.relative_to(ROOT).as_posix(),'sha256':digest(path.relative_to(ROOT))}))

if __name__=='__main__':main()
