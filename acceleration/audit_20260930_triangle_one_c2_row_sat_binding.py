"""Bind independently checked actual25row construction and fresh controls."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import platform
import subprocess
import sys
import json
import audit_20260930_triangle_one_c2_row_object as checker

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_triangle_one_c2_row_native_pilot'
AUDIT=ROOT/'acceleration/results/20260930_independent_review/triangle_one_c2_row_sat_object/summary.json'
AUDIT_SHA='e4693a9bb52831e26ecdeb350565123df4cac58917a66db4762ea31e161809b1'
CAL=ROOT/'acceleration/results/20260930_independent_review/triangle_one_c2_row_object_calibration/summary.json'
CAL_SHA='3e33674feff8b5914547c8a459b83e12c0b11dd86c43bc6706882509d0d91b6a'
need,digest,key,read,save=checker.need,checker.digest,checker.key,checker.read,checker.save

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    need(digest(AUDIT)==AUDIT_SHA and digest(CAL)==CAL_SHA,'actualSAT and pre-solve calibration identities')
    audit,cal=read(AUDIT),read(CAL)
    need(audit['status']=='INDEPENDENT_TRIANGLE_ONE_C2_ROW_SAT_OBJECT_PASS' and cal['status']=='INDEPENDENT_TRIANGLE_ONE_C2_ROW_OBJECT_CHECKER_CALIBRATION_PASS','actual and calibration PASS states')
    model,scope,derived,current=checker.inputs();g,columns,known,entries,refs,components=derived
    bindings={**audit['inputs_sha256'],**cal['inputs_sha256'],**current,key(AUDIT):AUDIT_SHA,key(CAL):CAL_SHA,key(__file__):digest(__file__)}
    path=AUDIT.with_name('independent_factor.json');need(digest(path)==audit['independent_factor_sha256'],'exact independent rawfactor');bindings[key(path)]=digest(path)
    factor=read(path);c=factor['incidence_matrix'];positive=checker.raw.validate(c,g,known,components,columns)
    need(positive['Q1']==factor['Q1'] and c[24]==factor['selected_C2_row'],'rawmatrix/Q1/selectedrow equality')
    manifest=read(D/'manifest.json');summary=read(D/'summary.json');receipt=read(D/'main/solver.receipt.json')
    need(receipt['actual_exit_code']==10 and not receipt['outer_windows_guard_expired'] and summary['actual_exit_code']==10,'completed native SAT')
    for p in [D/'manifest.json',D/'summary.json',D/'main/solver.receipt.json',D/'main/launch.json']:bindings[key(p)]=digest(p)
    for p,v in manifest['inputs_sha256'].items():need(digest(ROOT/p)==v,'native run input '+p);bindings[p]=v
    values=checker.common.assignment_values(read(D/'main/parsed_model.json')['assignment'],74814)
    controls=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):controls.append(label)
        else:raise ValueError('actual-object corruption accepted '+label)
    def clauses(v):
        with (checker.D/'instance.cnf').open('rb') as stream:return checker.common.check_cnf_stream(stream,v,74814,256151)
    for label,index in [('C1_primary_flip',1),('C2_primary_flip',601),('first_auxiliary_flip',651)]:
        bad=values[:];bad[index]^=1;reject(label,lambda:clauses(bad))
    bad=deepcopy(c);e=next(e for e in entries if e['row']==24);bad[24][e['column']]^=1
    reject('raw_selected_C2_bit_flip',lambda:checker.raw.validate(bad,g,known,components,columns))
    bad=deepcopy(c);bad[24][0]=bool(bad[24][0]);reject('raw_boolean_instead_of_integer',lambda:checker.raw.validate(bad,g,known,components,columns))
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'unchanged inputs and artifacts')
    report=dict(status='INDEPENDENT_TRIANGLE_ONE_C2_ROW_CONSTRUCTION_BINDING_PASS',claim_id='C-FIXED-TRIANGLE-ONE-C2-ROW-PROJECTION-CONSTRUCTION',claim_revision=1,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),verifier='/root/eight_domain_audit independent actual25row checking path',inputs_sha256=bindings,kind='construction',basis=['COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
      statement='The exact saved25x60binary incidence matrix comprising canonicalC0, allC1rows and C2coordinate0 satisfies the frozen principalGram, all25row margins10,120complete-fibre-column margins2,180component capacities<=2 and1770outside-column overlap caps<=2; its savedQ1 and selectedC2row equal independent raw decoding.',
      dependencies=[dict(id='C-FIXED-TRIANGLE-ONE-C2-ROW-TARGET-PROJECTION-CNF',revision=1,relation='uses_result')],scope='One explicit25row target-necessary projection in the fixed39core labels; no omittedC2 rows, residualD or targetgraph supplied.',
      original_run_source_commit=manifest['source_commit'],original_run_command=manifest['command'],native_command=receipt['command'],native_exit_code=10,
      full_clause_check=dict(variables=74814,clauses=256151,complete=True,audit=key(AUDIT),sha256=AUDIT_SHA),raw_matrix_check=dict(rows=25,columns=60,integer_Gram_entries=625,row_margins=25,complete_fibre_column_margins=120,component_capacities=180,outside_column_pair_caps=1770,Q1_entries=60,selected_C2_weight=sum(c[24])),
      raw_factor=key(path),raw_factor_sha256=digest(path),fresh_actual_corruptions_rejected=controls,pre_solve_calibration=dict(path=key(CAL),sha256=CAL_SHA,fresh_codec_and_isolated_column_controls=10,earlier_raw25_controls=9),
      shared_components=['Frozen pre-solve independent checker reused exactly; no producer imports.','Fresh controls calibrate that path and are not represented as a separate independent implementation.'],limitations=['This is not a36rowfactor or99vertexgraph.','No general existence/nonexistence or external review claimed.'],artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False)
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'),factor_sha256=digest(path))))

if __name__=='__main__':main()
