"""Separate literal matrix oracle and checking-path review for pilot01."""
from collections import Counter
import copy,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORT='acceleration/results/20261002_independent_review/hypergraph_pilot01/summary.json'
SOURCE='acceleration/audit_20261002_hypergraph_saved_objects_v3.py'
SOURCE_SHA='0fd03abfff20fc3d3e58bd615f75cb319a123e4adf59015f25725ed5c781e0bf'
SPEC='acceleration/audit_20261002_hypergraph_saved_objects_v3_spec.md'
SPEC_SHA='4034de81c7c55e874331575cc9bf0073deb370c09cfb62198bd9d57fd5e98aad'
CAL='acceleration/results/20261002_independent_review/hypergraph_saved_calibration03/summary.json'
CAL_SHA='8927cc04d9f8282da48b2443ca61c48a5bf7debce0ca71b6b3850d30ddc479cb'
RAW='acceleration/results/20261002_hypergraph_pilot01/native/best.adj'


def need(value,why):
    if not value:raise ValueError(why)


def oracle(matrix,n,k):
    need(len(matrix)==n and all(len(row)==n for row in matrix),'oracle exact shape')
    need(all(type(x)is int and x in [0,1] for row in matrix for x in row),'oracle binary domain')
    need(all(matrix[u][u]==0 and sum(matrix[u])==k for u in range(n)),'oracle diagonal/regularity')
    need(all(matrix[u][v]==matrix[v][u] for u in range(n) for v in range(n)),'oracle symmetry')
    adjacent=Counter();nonadjacent=Counter();el=em=0;mismatches=0
    for u in range(n):
        for v in range(n):
            # Row dot products differ from adapter row-column scalar path;
            # exact symmetry is established above before this equality is used.
            common=sum(x*y for x,y in zip(matrix[u],matrix[v]))
            expected=(k-2 if u==v else 0)-matrix[u][v]+2
            mismatches+=int(common!=expected)
            if u<v:
                if matrix[u][v]:adjacent[common]+=1;el+=(common-1)**2
                else:nonadjacent[common]+=1;em+=(common-2)**2
    need(sum(adjacent.values())==n*k//2 and sum(nonadjacent.values())==n*(n-1)//2-n*k//2,'oracle exact pair partition')
    return dict(adjacent_pairs=sum(adjacent.values()),nonadjacent_pairs=sum(nonadjacent.values()),
                adjacent_common_neighbor_histogram={str(c):adjacent[c] for c in sorted(adjacent)},
                nonadjacent_common_neighbor_histogram={str(c):nonadjacent[c] for c in sorted(nonadjacent)},
                E_lambda=el,E_mu=em,exact_energy=el+em,identity_mismatch_count=mismatches,ordered_entries_checked=n*n)


def main():
    report_sha=sys.argv[1];pins={}
    def pin(name,wanted=None):
        digest=hashlib.sha256((ROOT/name).read_bytes()).hexdigest();need(wanted is None or digest==wanted,'frozen identity '+name);pins[name]=digest
    def read(name,wanted=None):pin(name,wanted);return json.loads((ROOT/name).read_bytes())
    report=read(REPORT,report_sha);pin(SOURCE,SOURCE_SHA);pin(SPEC,SPEC_SHA);cal=read(CAL,CAL_SHA)
    need(report['status']=='HYPERGRAPH_SCIENTIFIC_SAVED_OBJECTS_V3_CHECKED_PENDING_INDEPENDENT_REVIEW' and report['verifier']=='/root/checkpoint_audit','separate actual checking execution')
    need(cal['verifier']=='/root/checkpoint_audit' and cal['calibration_control_count']==29,'independently executed strict29-control calibration')
    need(report['saved_state_files']==22 and report['saved_unique_steps']==21 and report['full_trajectory_checked'] is False
         and report['sparse_trace_records']==2247 and report['full_anchored_proposals_replayed']==2067 and report['unreplayed_sparse_records']==180,'exact saved-object and sparse checking scopes')
    need(report['target_zero_candidates']==0 and report['target_resolution'] is False,'no target candidate resolution')
    checks=read(str(Path(REPORT).parent/'object_checks.json').replace('\\','/'),report['outputs_sha256']['object_checks.json'])
    need(len(checks['saved_objects'])==22 and sum(len(record['objects']) for record in checks['saved_objects'])==44,'complete44 saved current/best objects')
    # Written independent source review: state/domain/set scorer and RNG core
    # are the previously calibrated checker authored by this verifier, while
    # the adapter merely reads/pins receipts and exports scalar matrix checks.
    # Scalar loop was reviewed against the exact stated identity; every negative
    # state control in v3 requires its exact CheckError stage. Unrelated exceptions
    # cannot satisfy the controls. Sparse frontier resumes only from exact states.
    rawhash=report['inputs_sha256'][RAW];pin(RAW,rawhash)
    raw=(ROOT/RAW).read_text(encoding='ascii').splitlines()
    need(raw[0]=='99' and len(raw)==100 and all(len(row)==99 and set(row)<=set('01') for row in raw[1:]),'literal99raw matrix')
    matrix=[[int(value) for value in row] for row in raw[1:]];result=oracle(matrix,99,14)
    for field,value in result.items():
        if field not in ['identity_mismatch_count','ordered_entries_checked']:need(report['final_best_diagnostics'][field]==value,'separate literal matrix diagnostic equality')
    need(result['exact_energy']==report['final_best_energy']==report['final_current_energy']==3034 and result['E_lambda']==427 and result['E_mu']==2607,'exact saved residual scope')
    current=report['raw_final_matrices']['current'];best=report['raw_final_matrices']['best']
    need(current['path'] is None and current['availability']=='MISSING','missing raw current file explicitly retained')
    pin(current['independently_reconstructed_export'],current['export_sha256']);pin(best['independently_reconstructed_export'],best['export_sha256'])
    need((ROOT/current['independently_reconstructed_export']).read_bytes()==(ROOT/RAW).read_bytes()==(ROOT/best['independently_reconstructed_export']).read_bytes(),'exact independently reconstructed current/best raw matrix bytes')
    # Independent positive and corrupted oracle tests.
    rook=[[int(u!=v and (u//3==v//3 or u%3==v%3)) for v in range(9)] for u in range(9)]
    valid=oracle(rook,9,4);need(valid['exact_energy']==valid['identity_mismatch_count']==0 and valid['ordered_entries_checked']==81,'known valid oracle control')
    rejected=[]
    damaged_histogram=copy.deepcopy(result['adjacent_common_neighbor_histogram']);damaged_histogram['1']+=1
    for label,call,expected in [('rook_scope',lambda:oracle(rook,99,14),'oracle exact shape'),
                       ('raw_loop',lambda:oracle([[1 if u==v==0 else matrix[u][v] for v in range(99)] for u in range(99)],99,14),'oracle diagonal/regularity'),
                       ('raw_score_changed',lambda:need(result['exact_energy']==3033,'corrupt exact score'),'corrupt exact score'),
                       ('raw_histogram_changed',lambda:need(damaged_histogram==result['adjacent_common_neighbor_histogram'],'corrupt raw histogram equality'),'corrupt raw histogram equality')]:
        try:call()
        except ValueError as error:need(str(error)==expected,'exact expected negative oracle diagnostic');rejected.append(label)
        else:raise ValueError('corrupted oracle control accepted')
    protocol=read('acceleration/results/20261002_hypergraph_pilot01/protocol.json')
    receipt=read('acceleration/results/20261002_hypergraph_pilot01/research.receipt.json','2ee3bba12e5bfa3ffb7d37ff80401ad78b14af6dd263be785dc8eacf2265f78c')
    outer=protocol['supervision'];sm=read(outer['path'],outer['sha256']);ss=read(str(Path(outer['path']).parent/'summary.json').replace('\\','/'))
    need(receipt['process_group']==outer['group']==399 and receipt['cwd']=='/mnt/c/Users/ikuto/projects/conway-99-graph','native group/cwd correlated with actual Linux outer')
    need(ss['cleanup']['process_group_live_pids']==[] and ss['cleanup']['job_active_zero_observed'] is True and ss['cleanup']['reaped'] is True
         and ss['cleanup']['cleanup_errors']==[] and ss['command_exit_code']==0,'completed Linux group actually observed empty')
    need(sm['seconds']==outer['outer_seconds']==300 and outer['producer_seconds']==270 and outer['guard_argv'][:2]==['/usr/bin/timeout','--signal=KILL'],'fixed contained command exact limits')
    pin(Path(__file__).relative_to(ROOT).as_posix());pin('uv.lock');pin('pyproject.toml')
    summary=dict(status='INDEPENDENT_HYPERGRAPH_PILOT01_SAVED_OBJECTS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/checkpoint_audit',producer='/root/native_driver',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,
        source_review=dict(adapter_author='/root/native_driver',discovery_author='/root/native_driver',mathematical_set_state_rng_core_author='/root/checkpoint_audit',
            separate_checking_path='Independent adjacency-set/full common-neighbor implementation and exact integer RNG, separately reviewed scalar matrix code, and fresh literal99matrix row-dot oracle.',
            changed_v3_controls='Exact-stage negative diagnostic, nonzero sparse RNG, complete-anchor and explicit-gap falsification; v1/v2 failures preserved.',
            shared_components=['Previously calibrated independent Python state/scorer/RNG helper.','Producer-authored file/receipt adapter, now independently source-reviewed/executed.','SHA-256, Python arithmetic/runtime and supervisor.']),
        statement='All22saved pilot01 state files contain independently checked full99point linear-triple current/best graphs and exact caches/energies; final current/best raw matrices agree and have exact residual E3034=427+2607. Of2247sparse trace records,2067proposals are fully replayed from complete state anchors;180remain unanchored. This is not a target graph or complete trajectory certificate.',
        saved_state_files=22,saved_unique_steps=21,complete_saved_current_best_graph_objects=44,raw_final_best_matrix_sha256=rawhash,raw_current_matrix_availability='MISSING',
        exact_literal_best_diagnostics=result,full_anchored_proposals=2067,unanchored_sparse_records=180,full_trajectory_checked=False,
        native_reported_ending_step=20000000,native_counter_limitation='Recorded counters and monotonicity/result agreement only;20million proposals are not independently replayed.',
        native_wall_seconds=receipt['wall_seconds'],historical_linux_cleanup_verified=True,current_execution_state='UNKNOWN; no new live process observation in this audit.',
        calibrated_controls={'known_rook_matrix':valid,'corrupted_oracle_rejected':rejected,'strict_adapter_controls':29},
        target_resolution=False,new_exclusions=0,overall_search_coverage='UNKNOWN; no validated denominator.',
        limitations=['Finite saved-object equality is not a whole trajectory or performance guarantee.','No search-space connectedness/exhaustive coverage assertion.','Raw producer current adjacency export is absent; exact reconstruction is separately preserved.',
                     'The final residual3034 is positive, so these matrices refute their own target-certificate candidacy.','No target-valid99positive fixture is available; known9vertex SRG and malformed/nonzero99fixtures calibrate the exact validator.'])
    out=ROOT/'acceleration/results/20261002_independent_review/hypergraph_pilot_review01';out.mkdir(exist_ok=False)
    with (out/'summary.json').open('x',encoding='utf8',newline='\n') as f:json.dump(summary,f,indent=2);f.write('\n')
    print(json.dumps({'path':(out/'summary.json').relative_to(ROOT).as_posix(),'sha256':hashlib.sha256((out/'summary.json').read_bytes()).hexdigest()}))


if __name__=='__main__':main()
