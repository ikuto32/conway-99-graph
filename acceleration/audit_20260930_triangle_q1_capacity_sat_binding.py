"""Bind actual Q1 projection construction with fresh corruption controls."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import audit_20260930_triangle_q1_capacity_object as checker

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_triangle_q1_capacity_native_pilot'
AUDIT=ROOT/'acceleration/results/20260930_independent_review/triangle_q1_capacity_sat_object/summary.json'
AUDIT_SHA='34eec921b8c149c2bd49860e2f0208c4d2fa472e953c55a89dc867a9d8c2605d'
CAL=ROOT/'acceleration/results/20260930_independent_review/triangle_q1_capacity_object_calibration/summary.json'
CAL_SHA='b4ee539d112b2f4ebe659ece364781a7dd9db99ffd75bbedd14cf8f6e345f434'
need,digest,key,read,save=checker.need,checker.digest,checker.key,checker.read,checker.save

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    need(digest(AUDIT)==AUDIT_SHA and digest(CAL)==CAL_SHA,'frozen actual checker and prior calibration reports')
    audit=read(AUDIT);cal=read(CAL)
    need(audit['status']=='INDEPENDENT_TRIANGLE_Q1_CAPACITY_SAT_OBJECT_PASS' and cal['status']=='INDEPENDENT_TRIANGLE_Q1_CAPACITY_OBJECT_CHECKER_CALIBRATION_PASS','independent complete SAT and preexisting calibration PASS')
    bindings={**audit['inputs_sha256'],**cal['inputs_sha256'],key(AUDIT):AUDIT_SHA,key(CAL):CAL_SHA,key(__file__):digest(__file__)}
    model,scope,derived,current=checker.inputs();bindings.update(current)
    factor_path=AUDIT.with_name('independent_factor.json');need(digest(factor_path)==audit['independent_factor_sha256'],'actual independent rawfactor identity');bindings[key(factor_path)]=digest(factor_path)
    factor=read(factor_path);g,columns,known,entries,refs,components=derived;c=factor['incidence_matrix']
    positive=checker.validate(c,g,known,components,columns);need(positive['Q1']==factor['Q1'],'actual rawmatrix/Q1 agreement')
    run=read(D/'manifest.json');receipt=read(D/'main/solver.receipt.json');summary=read(D/'summary.json')
    need(receipt['actual_exit_code']==10 and not receipt['outer_windows_guard_expired'] and summary['actual_exit_code']==10,'actual completed native SAT receipt')
    for path in [D/'manifest.json',D/'summary.json',D/'main/solver.receipt.json',D/'main/launch.json']:bindings[key(path)]=digest(path)
    for p,v in run['inputs_sha256'].items():need(digest(ROOT/p)==v,'frozen native run input');bindings[p]=v
    values=checker.common.assignment_values(read(D/'main/parsed_model.json')['assignment'],19686);controls=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):controls.append(label)
        else:raise ValueError('actual-object corrupted control accepted '+label)
    def clauses(v):
        with (checker.D/'instance.cnf').open('rb') as f:return checker.common.check_cnf_stream(f,v,19686,68328)
    for label,index in [('first_primary_flip',1),('first_auxiliary_flip',601)]:
        bad=values[:];bad[index]^=1;reject(label,lambda:clauses(bad))
    e=entries[0];bad=deepcopy(c);bad[e['row']][e['column']]^=1
    reject('actual_incidence_bit_flip',lambda:checker.validate(bad,g,known,components,columns))
    bad=deepcopy(c);bad[12][0]=bool(bad[12][0])
    reject('actual_boolean_instead_of_integer',lambda:checker.validate(bad,g,known,components,columns))
    bad=deepcopy(c);forced_rows=[r for r in components[0] if r<24][:3]
    for r in forced_rows:bad[r][0]=1
    reject('actual_column_component_overflow',lambda:checker.independent.capacity_check(bad,components))
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable exact bound artifacts')
    report=dict(status='INDEPENDENT_TRIANGLE_Q1_CAPACITY_CONSTRUCTION_BINDING_PASS',claim_id='C-FIXED-TRIANGLE-CAPACITY-COMPATIBLE-Q1-CONSTRUCTION',claim_revision=1,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),verifier='/root/eight_domain_audit independent complete actual projection artifact reviewer',inputs_sha256=bindings,kind='construction',basis=['COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
      statement='The exact saved binary24x60 matrix(C0;C1), and its independently decoded60entry Q1 permutation, satisfy every entry of the fixed principal Gram, row sums10, each fibre-column sum2, the canonical fixed incidences and all180component partial-column capacities<=2.',
      dependencies=[dict(id='C-FIXED-TRIANGLE-Q1-CAPACITY-PROJECTION-CNF',revision=1,relation='uses_result')],scope='One explicit24row incidence factor for the fixed39core necessary projection; existence of C2, a36rowfactor or a full99graph is not established.',
      original_run_source_commit=run['source_commit'],original_run_command=run['command'],native_command=receipt['command'],native_exit_code=10,
      full_clause_check=dict(variables=19686,clauses=68328,complete=True,report=key(AUDIT),sha256=AUDIT_SHA),raw_matrix_check=dict(rows=24,columns=60,integer_Gram_entries=576,row_margins=24,fibre_column_margins=120,component_capacities=180,Q1_length=60),
      raw_factor=key(factor_path),raw_factor_sha256=digest(factor_path),fresh_corrupted_controls_rejected=controls,preexisting_calibration=dict(path=key(CAL),sha256=CAL_SHA,negative_controls=17),
      shared_components=['Exactly the frozen pre-solve independently authored checker; no producer imported.','Fresh corruption checks reuse its primitive validators and are disclosed as calibration, not another independent implementation.'],limitations=['Not a36rowfactor or99vertex graph.','No target-level existence or nonexistence claim.','No novelty or external review asserted.'],artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False)
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'),factor_sha256=digest(factor_path))))

if __name__=='__main__':main()
