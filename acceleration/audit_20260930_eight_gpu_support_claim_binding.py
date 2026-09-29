"""Bind all six independently completed raw-support evaluations to one revision."""
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse,json,platform,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--audit-sha256',required=True);args=parser.parse_args()
    path=ROOT/'acceleration/results/20260930_independent_review/eight_gpu_support_run02.json'
    assert digest(path)==args.audit_sha256
    audit=json.loads(path.read_bytes());assert audit['status']=='INDEPENDENT_EIGHT_COORDINATE_GPU_EXACT_SUPPORT_ATTEMPTS_PASS'
    expected=[(c,k)for c in(1000,5000,10000)for k in('last','average')]
    assert len(audit['attempts'])==audit['independently_evaluated_attempts']==6 and audit['skipped_attempts']==audit['failed_attempts']==0
    assert [(r['iterations'],r['iterate'])for r in audit['attempts']]==expected
    assert all(r['status']=='INDEPENDENT_EXACT_RAW_SUPPORT_PASS'and r['checked_columns']==1875214 and r['checked_centers']==84 and r['denominator']==2**20 for r in audit['attempts'])
    assert audit['raw_original_choices']==2290122 and audit['independently_rejected_choices']==414908 and audit['retained_choices']==1875214
    numerators=[r['numerator']for r in audit['attempts']]
    assert numerators==[-77488,-88510,-211,-26216,-1,-13149] and not any(n>0 for n in numerators)
    bindings={path.relative_to(ROOT).as_posix():digest(path)}
    for p in[Path(__file__).resolve(),ROOT/'uv.lock',ROOT/'acceleration/results/20260930_independent_review/eight_gpu_support_derivation.md',ROOT/'acceleration/results/20260930_eight_moment_pdhg/run02/certificates/summary.json',ROOT/'acceleration/results/20260930_eight_moment_pdhg/run02/summary.json']:
        bindings[p.relative_to(ROOT).as_posix()]=digest(p)
    values=[dict(iterations=r['iterations'],iterate=r['iterate'],numerator=r['numerator'],denominator=r['denominator'],reduced=str(Fraction(r['numerator'],r['denominator'])),certificate_path=r['certificate_path'],certificate_sha256=r['certificate_sha256'])for r in audit['attempts']]
    statement='For each of the six frozen run02 support attempts, in checkpoint order 1000, 5000, 10000 and last then average, independently evaluating every one of the 1875214 retained eight-coordinate stars gives exact support-bound numerators [-77488,-88510,-211,-26216,-1,-13149] over denominator 1048576. All six bounds are nonpositive and establish no exclusion.'
    report=dict(status='INDEPENDENT_EIGHT_GPU_SUPPORT_CLAIM_BINDING_PASS',claim_id='C-PARTIAL-K-EIGHT-COORDINATE-GPU-FROZEN-SUPPORT-ATTEMPTS',claim_revision=1,recommendation='VERIFIED',review_state='CLEAR',statement=statement,kind='empirical/engineering result',basis=['COMPUTED'],verifier='/root/state_literature_audit independent checking agent',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),scope='Exactly the frozen 120-fixed-K-edge eight-coordinate family with all prescribed absences, and its audited matching-filtered moment relaxation. Exactly six saved weight choices, not optimization over all possible weights.',dependencies=[dict(id='C-PARTIAL-K-EIGHT-COORDINATE-DOMAINS',revision=1,relation='coverage'),dict(id='C-PARTIAL-K-EIGHT-COORDINATE-NEIGHBORHOOD-MATCHING-FILTER',revision=1,relation='uses_result'),dict(id='C-PARTIAL-K-EIGHT-COORDINATE-MATCHING-FILTERED-MOMENT-ENCODING',revision=1,relation='verification_dependency')],inputs_sha256=bindings,exact_values=values,counts=dict(frozen_attempts=6,independently_evaluated_attempts=6,skipped_attempts=0,failed_attempts=0,positive_attempts=0,distinct_retained_stars=1875214,star_evaluations_across_six_attempts=6*1875214,centers_per_attempt=84,center_maxima_across_six_attempts=6*84),best_bound=dict(numerator=max(numerators),denominator=1048576,iterations=10000,iterate='last',metric='Matching-filtered full-neighborhood moment L1 support lower bound for this fixed family; larger is stronger. This bound is weaker than the trivial nonnegative objective lower bound zero.'),checking_method='Checkpoint byte recovery from authenticated gzip parts, exact binary64 ratio rounding and clipping, independent Python unbounded-integer direct raw-neighborhood scoring of every retained star, all maxima and first argmax IDs, and complete sound-filter premise binding. No serialized matrix arithmetic or producer scorer imports.',shared_components=audit['shared_components'],controls=audit['controls'],limitations=audit['limitations']+['These six nonpositive lower bounds prove neither exact LP feasibility nor graph existence, and are not evidence that no stronger support bound exists.','GPU numerical calibration is engineering context, not a mathematical premise for validity of arbitrary integer weights.','The first native run produced no checkpoints; its six independently audited skips are a separate execution record and are not six additional evaluated bounds.'],unrestricted_target_resolution=False,external_review=False)
    out=ROOT/'acceleration/results/20260930_independent_review/eight_gpu_support_run02_claim_binding.json'
    with out.open('x')as f:json.dump(report,f,indent=2)
    print(report['status'],digest(out))
if __name__=='__main__':main()
