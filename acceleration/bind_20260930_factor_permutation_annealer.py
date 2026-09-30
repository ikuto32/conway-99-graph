"""Bind the checked finite engine traces to the three immutable intended raw cores."""
from datetime import datetime,timezone
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'acceleration/results/20260930_independent_review/factor_permutation_annealer/summary.json'
PRIOR_SHA='861071f985ee6643863e214f2df2e2220960e37809b19a62bdb972c52ba85ea2'
D=ROOT/'acceleration/results/20260930_factor_permutation_annealer_calibration_v2'
def digest(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    assert digest(PRIOR)==PRIOR_SHA;prior=json.loads(PRIOR.read_bytes());assert prior['status']=='INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS'
    bindings={**prior['inputs_sha256'],key(PRIOR):PRIOR_SHA}
    for p,sha in bindings.items():assert digest(ROOT/p)==sha
    def read(p):
        value=digest(p);assert bindings[key(p)]==value;return json.loads(p.read_bytes())
    shift=read(ROOT/'acceleration/results/20260930_triangle_joint_factor_cnf/scope.json')['core']
    n=12;shift_core=[[0]*36 for _ in range(36)]
    for g in range(3):
        for r,mate in enumerate(shift['internal_matchings'][g]):shift_core[g*n+r][g*n+mate]=1
    for left,right,permutation in[(0,1,shift['F01']),(0,2,shift['F02']),(1,2,shift['P12'])]:
        for r,s in enumerate(permutation):shift_core[left*n+r][right*n+s]=shift_core[right*n+s][left*n+r]=1
    sources={
      'shift6':shift_core,
      'six_prism':read(ROOT/'acceleration/results/20260930_independent_review/prism_all_columns_cnf/derived_geometry.json')['core_adjacency'],
      'fixture243':read(ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json')['cubic_core60'],
    }
    records=[]
    for label,core in sources.items():
        problem=read(D/f'{label}_problem.json');assert problem['core_adjacency']==core
        for path in D.glob(label+'*_raw*.json'):
            assert read(path)['core_adjacency']==core
        altered=[row[:]for row in core];altered[0][1]^=1;assert problem['core_adjacency']!=altered
        records.append(dict(label=label,vertices=len(core),entries_checked=len(core)**2,exact_frozen_source_match=True,changed_core_control_rejected=True))
    for path in[D/'boundary_63_64_raw_final.json',D/'boundary_127_128_raw_final.json']:assert read(path)['core_adjacency']==sources['fixture243']
    bindings[key(Path(__file__).resolve())]=digest(Path(__file__).resolve())
    report={**prior,'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'command':[sys.executable,*sys.argv],
      'inputs_sha256':bindings,'claim_id':'C-FACTOR-PERMUTATION-ANNEALER-CALIBRATION','claim_revision':1,
      'prior_complete_trace_audit':dict(path=key(PRIOR),sha256=PRIOR_SHA),'intended_core_bindings':records,
      'binding_scope':'This addendum checks the three intended immutable core identities in addition to the prior exact trace/score/domain/build checks. It does not alter frozen prior records or extend finite floating-parity coverage.'}
    out=args.out/'summary.json'
    with out.open('x',encoding='utf-8')as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(dict(status=report['status'],sha256=digest(out))))
if __name__=='__main__':main()
