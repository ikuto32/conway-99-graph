"""Source/protocol gate supplement; no producer import or GPU execution."""
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import platform
import sys
import audit_20260917_rerank_v3_inputs as prior

def main():
    bindings={}
    def bind(p,h=None):
        k=prior.key(p)
        if k not in bindings:bindings[k]=prior.digest(p)
        prior.require(h is None or h==bindings[k],'changed artifact '+k);return bindings[k]
    def read(p):
        bind(p);d=json.loads(prior.path(p).read_bytes())
        for f,h in d.get('inputs_sha256',{}).items():bind(f,h)
        return d
    out=prior.path('acceleration/results/20260917_independent_review/rerank_v3_calibration_gate.json');prior.require(not out.exists(),'preserve report')
    bind(__file__);bind(prior.__file__)
    gate_path='acceleration/results/20260917_independent_review/rerank_v3_inputs.json'
    bind(gate_path,'012cbae529722638288cf529ab60f045fcd036a7eef5828d7ee8d44926745311');gate=read(gate_path)
    prior.require(gate['status']=='INDEPENDENT_WHOLE_STAR_RERANK_V3_INPUT_PASS','full payload proof gate')
    wrapper='acceleration/refine_whole_star_rank_v3_calibrated.py';doc='docs/NEXT_20260917_WHOLE_STAR_RERANK_V3_CALIBRATION.md'
    bind(wrapper,'14794ed43c4f97b4936f0269c5ba94b0ccf8f31bd748486ebb748e45e9b79380')
    bind(doc,'b67a89d3d92d3cd2b3f7e9cb0a89718aff6bd9f08af97f22ad1f94a0d12083fc')
    controls=read('acceleration/results/20260917_whole_star_rerank_v3/calibration_controls.json')
    prior.require(controls['status']=='WHOLE_STAR_RERANK_V3_CALIBRATION_CONTROLS_PASS' and controls['positive_controls']==4 and controls['negative_controls']==5 and
                  [r['outcome']for r in controls['controls']]==['ACCEPT']*4+['REJECT']*5 and controls['independent_verification']is False,'producer synthetic controls')
    # Independent arithmetic review of the disclosed reversal and tie
    # fixtures. This does not execute the producer metrics implementation.
    exact=[(Fraction(10*i),Fraction(10*i+1))for i in range(16)]
    old=[(Fraction((15-i)*10-200),Fraction((15-i)*10+200))for i in range(16)]
    new=[(Fraction(10*i-1),Fraction(10*i+2))for i in range(16)]
    def stats(values):
        gaps=sorted(hi-lo for lo,hi in values)
        inversions=[sum((values[i][which],i)>(values[j][which],j)for i,j in combinations(range(16),2))for which in (0,1)]
        return sum(gaps)/16,(gaps[7]+gaps[8])/2,inversions
    prior.require(stats(old)==(400,400,[120,120])and stats(new)==(3,3,[0,0]),'independent reversal fixture arithmetic')
    prior.require(stats([(Fraction(-1),Fraction(200))]*16)==(201,201,[0,0]),'independent tie fixture')
    touching=exact.copy();touching[1]=(exact[0][1],exact[1][1])
    prior.require(sum(not(a[1]<b[0]or b[1]<a[0])for a,b in combinations(touching,2))==1,'touching interval ambiguity')
    arithmetic_controls=[dict(name='independent_reversal_mean_median_and120inversions',outcome='PASS'),dict(name='independent_tie_ID_order',outcome='PASS'),dict(name='touching_exact_endpoints_ambiguous',outcome='PASS')]
    prior.require(all(prior.digest(f)==h for f,h in bindings.items()),'inputs changed')
    result=dict(status='INDEPENDENT_WHOLE_STAR_RERANK_V3_CALIBRATION_GATE_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=gate['source_commit'],inputs_sha256=bindings,command=[sys.executable]+sys.argv,working_directory=str(Path.cwd()),python=platform.python_version(),
        producer_imported=False,GPU_processes=0,LP_runs=0,base_payload_gate_path=gate_path,
        source_review=['main invokes frozen producer preflight and original input gate, then supplementary gate before execute',
            'wrapper adds only bound reporting sources and post-execution descriptive statistics; no binary or selection mutation',
            'means and even-population medians use exact rationals of binary-float endpoint differences',
            'all16 calibration cases and120 pairs included; overlapping/touching exact intervals remain ambiguous',
            'separated-pair comparisons use numerical score then original ID; ties separately counted',
            'endpoint diagnostics compare to saved exact interval, not to an asserted true optimum',
            'strict empirical improvement flags compare each statistic separately; no target-progress score or retrospective filtering'],
        independently_calculated_fixture_controls=arithmetic_controls,producer_controls_reviewed=9,producer_controls_reexecuted=False,
        scope='Source/protocol readiness gate for frozen calibration wrapper plus prior exact-byte input gate; actual5000 outputs/statistics remain pending independent raw review',
        shared_trusted_components=['Python standard library','earlier independent payload gate helpers'],target_resolution='UNKNOWN')
    out.open('x',encoding='utf8').write(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],sha256=prior.digest(out))))

if __name__=='__main__':main()
