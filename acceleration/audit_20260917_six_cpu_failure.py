"""Check failed solver status and symbolic all-zero multiplier support value."""
from datetime import datetime,timezone
import json,subprocess,sys,platform
import audit_20260917_partial_matching as h
ROOT=h.ROOT;D=ROOT/'acceleration/results/20260917_six_filtered_solve5400/run01'
def main():
    bindings={}
    def read(p):bindings[h.key(p)]=h.digest(p);return json.loads(p.read_bytes())
    summary=read(D/'summary.json');numeric=read(D/'numeric_lp.json');certificate=read(D/'exact_support_bound.json');read(D/'manifest.json');gate=read(ROOT/'acceleration/results/20260917_independent_review/six_filtered_moments.json')
    h.require(h.digest(D/'exact_support_bound.json')=='1965c055a6121f09bd097f0f4a7a23d532bce550bdb53931f7fe11acc7405bdc','certificate pin')
    for f,v in summary['output_sha256'].items():h.require(h.digest(D/f)==v,'saved artifact changed');bindings[h.key(D/f)]=v
    h.require(numeric['run_status']=='HighsStatus.kError'and numeric['model_status']==summary['model_status']=='HighsModelStatus.kSolveError','failed status')
    h.require(numeric['value_valid']is False and numeric['dual_valid']is False and numeric['objective_usable']is False and summary['objective']is None,'invalid solution semantics')
    bound=certificate['bound'];y=bound['moment_weight_numerators'];q=bound['reciprocity_weight_numerators'];maxima=bound['center_maxima_numerators']
    h.require(len(y)==3486 and len(q)==2040 and len(maxima)==84 and all(type(v)is int and v==0 for v in y+q+maxima),'zero integer weights/maxima dimensions')
    h.require(bound['denominator']==1048576 and bound['numerator']==0 and bound['strictly_positive']is False,'zero exact bound')
    h.require(len(numeric['row_dual'])==5610 and all(v==0 for v in numeric['row_dual']),'returned zero dual entries')
    h.require(len(numeric['col_value'])==719693 and all(v==0 for v in numeric['col_value']),'returned zero primal entries')
    h.require(gate['retained_original_probability_columns']==712721 and gate['hard_simplex_rows']==84,'nonempty simplex premise')
    corrupted=y[:];corrupted[0]=1;h.require(not all(v==0 for v in corrupted),'corrupt zero-weight control')
    for p in(__file__,h.__file__,ROOT/'uv.lock'):bindings[h.key(p)]=h.digest(p)
    report=dict(status='INDEPENDENT_SIX_CPU_SOLVE_FAILURE_AND_ZERO_WEIGHT_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,recorded_solver_status=numeric['model_status'],value_valid=False,dual_valid=False,objective=None,objective_null_reason='No valid primal and solver reported SolveError; raw info0 is unusable.',recorded_solve_seconds=numeric['solve_seconds'],exact_support_bound=dict(numerator=0,denominator=1048576),method='Read frozen actual solver flags; verify all3486moment and2040reciprocity integerweights are zero. Therefore every column score is symbolically zero on every nonempty simplex, each maximum is zero, and rhs dot zero minus84zero maxima is zero; no column enumeration required.',returned_primal_rejected='Allzero probabilities violate every simplex sum=1.',controls=['nonzero weight rejected by zero-weight checker'],solver_failure_cause=None,solver_failure_cause_null_reason='Log reports IPX failure but does not establish a more specific independently diagnosed cause.',producer_imported=False,shared_components=['Python standard library','prior independent artifact helper','pinned independently checked model dimensions'],limitations=['Saved-record verification, not a repeated solver execution.','Neither existence, infeasibility, nor conditional exclusion follows from this failed run or zero support bound.','Necessary model/domain/filter claims remain separate and unchanged.'])
    p=ROOT/'acceleration/results/20260917_independent_review/six_cpu_failure.json'
    with p.open('x')as f:json.dump(report,f,indent=2)
    print(report['status'],h.digest(p))
if __name__=='__main__':main()
