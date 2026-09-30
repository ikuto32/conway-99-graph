"""Bind the hex-format correction, calibrations, and actual parity witness."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse,ast,hashlib,json,platform,subprocess,sys
import audit_20260930_hadamard_balanced_parity_v2 as check
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
def h(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def need(x,s):
    if not x:raise ValueError(s)
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(p,digest=None):
        v=h(ROOT/p);need(digest is None or v==digest,'artifact '+p);pins[p]=v;return ROOT/p
    def load(p,digest=None):return json.loads(pin(p,digest).read_bytes())
    try:
        old='acceleration/audit_20260930_hadamard_balanced_parity.py';new='acceleration/audit_20260930_hadamard_balanced_parity_v2.py'
        encoding=load(I+'hadamard_balanced_parity/summary.json','8134ed25d5dc06704e6f7f668fa03deec56874eca6d5fad9e6a4138787c7dd76')
        pin(old,encoding['inputs_sha256'][old]);pin(new)
        trees=[ast.parse((ROOT/p).read_text()) for p in [old,new]]
        fns=[{n.name:ast.dump(n,include_attributes=False) for n in t.body if isinstance(n,ast.FunctionDef)} for t in trees]
        unchanged=['sign','classification','reconstruct','cnf_bytes','assignment','native','satisfied','projection']
        need(all(fns[0][name]==fns[1][name] for name in unchanged),'all mathematical/encoding/native/assignment/projection functions unchanged')
        failure=load(I+'hadamard_balanced_parity_sat/failure.json');need(failure['error']=="ValueError('decoded raw projection field group_records')",'preserved original metadata failure')
        actual_path=I+'hadamard_balanced_parity_sat_v2/summary.json';actual=load(actual_path,'d2536119ac3fa0d45c190a6562de2ccc67c3f9c9765fbfc03257e37b15097f9c')
        calibration_path=I+'hadamard_balanced_parity_object_calibration_v2/summary.json';cal=load(calibration_path,'101b4af16c1356cad1951f04626d3fcc4a244f3afac220ed94b717b9ee1e8dec')
        need(actual['status']=='INDEPENDENT_HADAMARD_BALANCED_PARITY_SAT_OBJECT_PASS' and cal['status']=='INDEPENDENT_HADAMARD_BALANCED_PARITY_OBJECT_CHECKER_CALIBRATION_PASS','completed corrected gates')
        need(actual['inputs_sha256'][new]==cal['inputs_sha256'][new]==pins[new],'exact corrected source bindings')
        for p,digest in actual['inputs_sha256'].items():pin(p,digest)
        for p,digest in actual['outputs_sha256'].items():pin(p,digest)
        projection_path=I+'hadamard_balanced_parity_sat_v2/independent_projection.json';projection=load(projection_path)
        decoded_path=B+'hadamard_balanced_parity_native_pilot/main/decoded_projection.json';decoded=load(decoded_path)
        check.compare_decoded(projection,decoded)
        alternate=deepcopy(decoded)
        for record in alternate['group_records']:record['parity_mask_hex']=hex(int(record['parity_mask_hex'],16))
        check.compare_decoded(projection,alternate)
        corrupt=[]
        for label in ['mask_value','mask_nonnumeric','other_field']:
            broken=deepcopy(decoded)
            if label=='mask_value':broken['group_records'][0]['parity_mask_hex']=format(int(broken['group_records'][0]['parity_mask_hex'],16)^1,'x')
            elif label=='mask_nonnumeric':broken['group_records'][0]['parity_mask_hex']='not_hex'
            else:broken['group_records'][0]['pattern_index']+=1
            try:check.compare_decoded(projection,broken)
            except ValueError:corrupt.append(label)
            else:raise ValueError('corruption accepted '+label)
        mixed=sum(i!=0 for i in projection['selected_pattern_indices']);pairhist=dict(Counter(p['count'] for p in projection['pair_disagreement_counts']))
        need(mixed==16 and len(projection['selected_pattern_indices'])==20 and pairhist=={0:12,3:48},'raw parity witness counts')
        for label in ['actual_bad_hexmask','actual_bad_selected_pattern','actual_bad_pair_count','actual_flipped_primary','actual_flipped_auxiliary','actual_native_disagreement']:need(label in actual['corruptions'],'fresh actual corruption '+label)
        pin('acceleration/audit_20260930_hadamard_parity_object_v2_delta.py');pin('uv.lock');pin('pyproject.toml')
        now=datetime.now(timezone.utc).isoformat()
        claim=dict(id='C-FIXED-HADAMARD-SIX-PRISM-NONCYCLIC-PARITY-PROJECTION-WITNESS',revision=1,statement='The exact520-variable4481-clause fixed-support parity formula has the saved satisfying assignment: its20one-hot group patterns comprise16mixed and4constant groups, and its60pair disagreement counts comprise48threes and12zeros. Thus this necessary parity projection admits noncyclic choices.',kind='construction',basis=['COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope='Only a witness for the necessary parity projection; no local-colouring lift, full36x60factor, residual graph, fixed-support feasibility or target graph is asserted.',assumptions=['The exact saved support and parity model, with balance explicitly an additional construction restriction.','No hypothetical target automorphism is assumed.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-BALANCED-PARITY-PROJECTION',revision=1,relation='encoding_equivalence')],evidence_references={actual_path:pins[actual_path],projection_path:pins[projection_path],calibration_path:pins[calibration_path]},verification=dict(claim_revision=1,verifier='/root/eight_domain_audit',method='independent_raw_native_assignment_clause_and_projection_check',command_or_audit=actual_path,artifact_hashes={p:digest for p,digest in actual['inputs_sha256'].items() if p.endswith(('/parsed_model.json','/decoded_projection.json','/solver.stdout.log','/instance.cnf','/model.json'))},timestamp=actual['timestamp'],outcome='PASS'),limitations=['This refutes only the assertion that the parity projection forces every group cyclic.','Full-Gram necessity of coordinatewise balance remains UNKNOWN.','The first actual checker failure concerned only optional hexadecimal string representation; original failure/source and both valid representations are preserved.'],created_at=now,updated_at=now,artifact_availability='LOCAL_ONLY')
        save(out/'claim_binding.json',claim)
        report=dict(status='INDEPENDENT_HADAMARD_PARITY_OBJECT_V2_DELTA_AND_CALIBRATION_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={(out/'claim_binding.json').relative_to(ROOT).as_posix():h(out/'claim_binding.json')},unchanged_mathematical_functions=unchanged,hex_format_positive_cases=2,metadata_corruptions=corrupt,actual_fresh_corruptions=6,mixed_groups=mixed,constant_groups=4,pair_count_histogram=pairhist,verifier='/root/eight_domain_audit',shared_components=['Imports the frozen independently authored v2 object checker only. No producer imports.','Mathematical, encoding, native parser and raw projection functions are AST-identical to the original independently calibrated source.'],scope='Source correction provenance and exact metadata calibration; actual mathematical witness is bound to the separate full-object PASS.',encoding_gate_unchanged=True,ledger_changed=False,git_changed=False,target_resolution=False)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=h(out/'summary.json'),claim_sha256=h(out/'claim_binding.json'))))
    except BaseException as exc:save(out/'failure.json',dict(error=repr(exc)));raise
if __name__=='__main__':main()
