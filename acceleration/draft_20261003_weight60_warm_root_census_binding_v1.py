"""Draft exact schema2 census binding from ROOT's already completed dense audit.

Metadata/identity checks only, no mathematical approval or ledger mutation.
"""
import argparse,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
REPORT='acceleration/results/20261003_independent_review/weight60_warm_roots_dense01/summary.json'
REPORT_SHA='becf048cbb32ec577a78c7084fc949103af91f66c92c5936137a9740c5cdd35a'
CHECKER='acceleration/audit_20261003_weight60_warm_root_census_v2.py'
CHECKER_SHA='bd1021c4461400d0821292210f3a8da1a5f56b943ed2abbb2753c899f5db0771'
PRODUCER='acceleration/results/20261003_weight60_warm_root_census02/summary.json'
PRODUCER_SHA='57fad3b7fa053af077ef4e5175e550843e47dfc5cd61477a206eda66064f70e5'
CAL='acceleration/results/20261003_independent_review/weight60_warm_roots_dense01/calibration.json'
CAL_SHA='fb4e8b514c07a85f892fcd2ba0056d7bddb14a6596d6641bb4539624730fd06b'
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(data,stream,indent=2);stream.write('\n')
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,required=True);a=ap.parse_args()
    d=CommandDeadline(a.seconds,allocation_reason='Metadata-only exact alreadyROOT-reviewed census/schema2 claim binding and direct immutable source/artifact closure, no mathematical replay')
    out=a.out.resolve();need(out.is_relative_to(ROOT),'workspace output');out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(name,wanted=None):
        need(not d.status()['stop_required'] and d.status()['remaining_seconds']>20,'not completed within allocated metadata budget')
        path=(ROOT/name).resolve();need(path.is_relative_to(ROOT) and path.is_file(),'exact local artifact exists')
        digest=sha(path);need(wanted is None or digest==wanted,'exact pinned identity '+name);need(name not in pins or pins[name]==digest,'consistent repeated pin');pins[name]=digest
        return json.loads(path.read_bytes()) if path.suffix=='.json' else None
    report=pin(REPORT,REPORT_SHA);producer=pin(PRODUCER,PRODUCER_SHA);pin(CHECKER,CHECKER_SHA);cal=pin(CAL,CAL_SHA)
    need(report['status']=='INDEPENDENT_WEIGHT60_WARM_TWO_GRAPH_DENSE_ROOT_CENSUS_V2_PASS' and report['verifier']=='/root' and report['producer']=='/root/structural','ROOT independent exact recorded outcome')
    need((report['raw_graphs'],report['complete_roots'],report['literal_triangle_population'],report['complete_scalar_matrix_entries'])==(2,198,313698,19602),'exact finite coverage')
    need(report['graph_records']==[
        dict(label='final_best',matching_roots=99,fully_cn2_roots=0,minimum_mu_row_residual=52,minimum_root_ties=[11,41,77],selected_root=11,triangle_count=231,global_mu_energy=3480),
        dict(label='first_lambda0',matching_roots=99,fully_cn2_roots=0,minimum_mu_row_residual=50,minimum_root_ties=[81],selected_root=81,triangle_count=231,global_mu_energy=3608)],'exact all-root/minimum/tie statement')
    need(cal['positive_roots']==9 and cal['strict_negative_controls']==5 and report['controls']==cal,'recorded calibrated finite checker')
    need(report['target_resolution']=='NONE','no target promotion')
    for name,digest in report['inputs_sha256'].items():pin(name,digest)
    for name,digest in producer['inputs_sha256'].items():pin(name,digest)
    for name,descriptor in producer['artifacts'].items():pin(name,descriptor['sha256'])
    for prefix in ['acceleration/results/20261003_independent_review/weight60_warm_roots_supervision01','acceleration/results/20261003_weight60_warm_root_census_supervision02']:
        for leaf in ['manifest.json','summary.json','stdout.log','stderr.log','progress.jsonl']:pin(prefix+'/'+leaf)
    pin(Path(__file__).resolve().relative_to(ROOT).as_posix());pin('acceleration/draft_20261003_weight60_warm_root_census_binding_v1_spec.md')
    pin('acceleration/audit_20261003_weight60_warm_root_census_v2_spec.md','0446dd0f7cc80d8c5d0f3ffbb97549e27744d069f7068b3e79816e06bcca138c')
    now=datetime.now(timezone.utc).isoformat()
    statement='For exactly the two frozen labelled99-vertex raw warm graphs final_best (adjacency SHA2569d5b88ba2a2eb13d39d2a5edea1c25af9a9105c143c4297fe37e84f666a37a2d) and stepzero first_lambda0 (adjacency SHA256818314b75fccfa0f3fe702602afb02b6415f3138a770ef15ed0621d189d88836), every one of their198 labelled roots has a14-neighbor perfect matching, and no root has common-neighbor count2 for all84 outsiders. The minimum exact row residual sum_over_outsiders(CN(root,v)-2)^2 is52 at all and only roots11,41,77 in final_best and50 uniquely at root81 in stepzero first_lambda0; their exact global mu residual energies are3480 and3608 respectively.'
    binding=dict(binding_schema_version=2,id='C-HYPERGRAPH-WEIGHT60-WARM01-TWO-GRAPH-WARM-ROOT-CENSUS',revision=1,claim_revision=1,kind='empirical/engineering result',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,
        scope=dict(description='Complete198 labelled-root census of exactly two pinned saved partial graphs; no other graphs or hypothetical target objects. No SAT instance, target exclusion, scaffold-equivalence certificate or target resolution.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Use exactly the two hashed labelled raw adjacency files and original labels0..98.','An outsider is a distinct nonneighbor of the selected root; row residual uses all84 outsiders.','VERIFIED is reported solely from ROOT\'s independent dense audit, not approved by the producer metadata author.'],
        dependencies=[],dependency_reason='The direct dense checker rechecks complete literal raw graph domains and all198 records. No annealer success, history or necessary-model theorem is a premise of this finite statement.',
        created_at=now,updated_at=now,producer='/root/structural',verifier='/root',method='independent_artifact_check',verification_timestamp=report['timestamp'],report=REPORT,report_sha256=REPORT_SHA,
        command=report['command'],cwd=report['cwd'],python=report['python'],source_commit=producer['source_commit'],producer_source_commit=producer['source_commit'],
        source_commit_scope='Published producer base43175e0a96ed4abbf6b03e16b67adff6f6f40b20; new census/checker/metadata source byte identities are separately pinned, no claim that uncommitted sources belonged to that commit.',
        verifier_source_commit=None,verifier_source_commit_reason='ROOT report does not record a checking source commit; exact checker source SHA256 and command are preserved instead of inventing one.',
        inputs_sha256=pins,independent_statement_binding=dict(report_hash_bound=True,complete_population_fields_bound=True,graph_records_bound=True,source_and_calibration_bound=True,self_approval=False,requires_ROOT_review_of_this_editorial_binding=True),
        pre_output_calibration=dict(path=CAL,sha256=CAL_SHA,positive_fixture='Knownvalid generic rook9 SRG(9,4,1,2), all9 literal root neighborhoods and exact dense identity.',positive_root_count=9,negative_control_count=5,
                                    corrupted_controls=['diagonal1','asymmetric edge deletion','boolean entry rejected as nonliteral integer','binary-domain entry2','corrupted dense common-neighbor entry inconsistent with literal witnesses'],
                                    timing=cal['control_timing'],control_scope='Finite ROOT-authored checker controls, not a generic target99 certificate.'),
        shared_components=['Both paths use the pinned command_deadline.py deadline helper and run_compute_command.py containment; neither is the mathematical scorer.','Both use Python standard-library JSON and integers and identical rawinput bytes; parser defects are not eliminated by separate authorship alone.','The new producer V2 explicitly reuses old V1 producer census helpers; its new source/spec and actual controls/receipts are separately pinned. ROOT imports no producer census or annealer scorer; its new V2 literal dense matrix product and independent neighbor/triple enumeration replace producer bitset intersections.'],
        artifact_availability='LOCAL_ONLY',retrieval='Exact repository-relative evidence and hashes listed in closure.json; immutable public availability requires separate publication review.',
        limitations=report['limitations']+['No complete annealer trajectory or earliest lambda0 selection claim.','No general graph normalization or target nonexistence implication.','Schema validation/claim registration is metadata, not a new mathematical verification.'],
        ledger_edited=False,target_resolution=False,external_review='Not externally peer-reviewed; separate internal ROOT checking only.')
    save(out/'claim_binding_schema2_draft.json',binding)
    closure=dict(schema='WEIGHT60_WARM_ROOT_CENSUS_DIRECT_BINDING_CLOSURE_V1',source_commit=producer['source_commit'],records=[dict(path=name,sha256=digest,bytes=(ROOT/name).stat().st_size,availability='LOCAL_ONLY') for name,digest in sorted(pins.items())],
                 claim_binding=dict(path=(out/'claim_binding_schema2_draft.json').relative_to(ROOT).as_posix(),sha256=sha(out/'claim_binding_schema2_draft.json')),mathematical_replay=False,ledger_edited=False)
    save(out/'closure.json',closure);print(json.dumps(dict(binding_sha256=sha(out/'claim_binding_schema2_draft.json'),closure_sha256=sha(out/'closure.json'),records=len(pins),ledger_edited=False)))
if __name__=='__main__':main()
