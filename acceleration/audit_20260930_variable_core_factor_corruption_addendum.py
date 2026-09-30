"""Fresh whole-model metadata corruptions for the frozen encoding checker."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_variable_core_factor_cnf_v2 as check

ROOT=check.ROOT
GATE=ROOT/'acceleration/results/20260930_independent_review/variable_core_factor_cnf_v2/summary.json'
GATE_SHA='ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    check.need(check.digest(GATE)==GATE_SHA,'frozen encoding report')
    gate=json.loads(GATE.read_bytes());bindings={**gate['inputs_sha256'],check.key(GATE):GATE_SHA}
    for p,h in bindings.items():check.need(check.digest(ROOT/p)==h,'frozen input '+p)
    model=json.loads((check.D/'model.json').read_bytes());scope=json.loads((check.D/'scope.json').read_bytes());records=[]
    for name in ['first_counter_annotation','first_counter_bound','first_product_reference','last_channel_wrong_transpose','first_channel_output_alias','missing_column_cap_record','wrong_column_clause_number']:
        bad=deepcopy(model)
        if name=='first_counter_annotation':bad['counter_rows'][0]['kind']='permutation_degree'
        elif name=='first_counter_bound':bad['counter_rows'][0]['bound']=0
        elif name=='first_product_reference':bad['product_variables'][0]['left']+=1
        elif name=='last_channel_wrong_transpose':bad['selector_channel_groups'][3]['selector_matrix']=deepcopy(scope['symbolic_P'])
        elif name=='first_channel_output_alias':bad['selector_channel_groups'][0]['output_matrix'][0][0]=1
        elif name=='missing_column_cap_record':bad['column_cap_records'].pop()
        else:bad['column_cap_records'][0][4]+=1
        try:check.audit_clauses(bad,scope,check.D/'instance.cnf')
        except ValueError as error:records.append(dict(control=name,outcome='REJECTED',error=str(error)))
        else:raise ValueError('corrupted whole-model input accepted '+name)
    bindings[check.key(__file__)]=check.digest(__file__)
    check.need(all(check.digest(ROOT/p)==h for p,h in bindings.items()),'stable preserved inputs')
    report=dict(status='INDEPENDENT_VARIABLE_CORE_FACTOR_FRESH_METADATA_CORRUPTION_CONTROLS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
      statement='The frozen independent complete-clause checker rejects all seven explicitly defined in-memory mutations of the authenticated actual model.',controls=records,raw_model_sha256=check.digest(check.D/'model.json'),encoding_gate_sha256=GATE_SHA,claim_revision_binding=dict(id='C-UNRESTRICTED-TRIANGLE-NECESSARY-FACTOR-CNF-ENCODING',revision=1),
      shared_components=['The exact already audited encoding checker is deliberately reused; these are fresh negative calibration cases, not another independent mathematical checking implementation.'],limitations=['No raw artifact or old report was changed.','No solver run or additional mathematical conclusion.'],target_resolution=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
    check.save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=check.digest(args.out/'summary.json'))))

if __name__=='__main__':main()
