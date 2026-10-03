"""Independent raw exact rational and modular witness checking; no elimination."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys
import time
import audit_20260930_prism_all_columns as independent

ROOT=independent.ROOT
D=ROOT/'acceleration/results/20260930_prism_column_modular'
GATE=ROOT/'acceleration/results/20260930_independent_review/prism_all_columns_cnf/summary.json'
GATE_SHA='07c589160e930205bc7e42f9524846280b4a8f0573ca9e5dfa06b627a6d115c3'
need,digest,key,save=independent.need,independent.digest,independent.key,independent.save

def rational_check(witness,equations):
    need(type(witness['variables'])is int and witness['variables']==5760,'all5760variables')
    num,den=witness['numerator'],witness['denominator']
    need(type(num)is int and type(den)is int and den>0,'literal rational value')
    value=Fraction(num,den);need(0<value<1,'strict box interior')
    for inputs,bound,_ in equations:need(len(inputs)*value==bound,'exact rational equality')
    return dict(variables=5760,equations=len(equations),numerator=value.numerator,denominator=value.denominator,strict_box_interior=True)

def modular_check(witness,prime,equations):
    need(type(witness['prime'])is int and witness['prime']==prime,'declared finite field')
    x=witness['assignment'];need(len(x)==5760 and all(type(v)is int and 0<=v<prime for v in x),'complete canonical field assignment')
    actual=[]
    for inputs,bound,_ in equations:
        total=sum(x[i-1]for i in inputs);need((total-bound)%prime==0,'exact congruence');actual.append(total)
    return dict(prime=prime,variables=len(x),equations=len(equations),all_residues_zero=True,
      integer_equalities_satisfied=sum(total==bound for total,(_,bound,_)in zip(actual,equations)),
      integer_equalities_not_satisfied=sum(total!=bound for total,(_,bound,_)in zip(actual,equations)),rank_checked=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(p,expected=None):
        value=digest(p);need(expected is None or value==expected,'exact hash '+str(p));bindings[key(p)]=value;return p
    def read(p,expected=None):return json.loads(bind(p,expected).read_bytes())
    try:
        gate=read(GATE,GATE_SHA);need(gate['status']=='INDEPENDENT_SIX_PRISM_ALL_COLUMNS_CNF_ENCODING_PASS','full domain/equation gate')
        for p,sha in gate['inputs_sha256'].items():bind(ROOT/p,sha)
        summary=read(D/'summary.json');manifest=read(D/'manifest.json')
        for p,sha in manifest['inputs_sha256'].items():bind(ROOT/p,sha)
        for p,sha in summary['outputs_sha256'].items():bind(ROOT/p,sha)
        model=read(independent.D/'model.json')
        equations=independent.scope_check(model,independent.derive())
        need(len(equations)==540,'full independent equation population')
        uniform=read(D/'uniform_rational_witness.json');rational=rational_check(uniform,equations)
        witnesses={p:read(D/f'mod_{p}.json')for p in(2,3)}
        modular=[modular_check(witnesses[p],p,equations)for p in(2,3)]
        corrupt=[]
        def reject(name,fn):
            try:fn()
            except (ValueError,KeyError,IndexError):corrupt.append(name)
            else:raise ValueError('corrupted witness accepted '+name)
        for label,field,value in [('wrong_denominator','denominator',97),('zero_weight','numerator',0),('wrong_dimension','variables',5759),('Boolean_numerator','numerator',True)]:
            bad=deepcopy(uniform);bad[field]=value;reject(label,lambda:rational_check(bad,equations))
        for p in(2,3):
            for label in ['changed_entry','missing_entry','out_of_field','Boolean_entry','wrong_prime']:
                bad=deepcopy(witnesses[p])
                if label=='changed_entry':bad['assignment'][0]=(bad['assignment'][0]+1)%p
                elif label=='missing_entry':bad['assignment'].pop()
                elif label=='out_of_field':bad['assignment'][0]=p
                elif label=='Boolean_entry':bad['assignment'][0]=False
                else:bad['prime']=5
                reject(f'mod{p}_{label}',lambda:modular_check(bad,p,equations))
        # Exact checking controls are against the actual large equations and raw witnesses;
        # no claim is made about the producer's elimination algorithm or rank telemetry.
        save(args.out/'controls.json',dict(positive_controls=[rational,*modular],corrupted_witnesses_rejected=corrupt))
        bind(Path(__file__));bind(Path(independent.__file__))
        need(all(digest(ROOT/p)==sha for p,sha in bindings.items()),'stable input bytes')
        report=dict(status='INDEPENDENT_SIX_PRISM_LINEAR_RELAXATION_WITNESSES_PASS',claim_id='C-SIX-PRISM-COLUMN-LINEAR-RELAXATION-WITNESSES',claim_revision=1,
          timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
          verifier='/root/state_literature_audit independent exact witness checker',recommendation='VERIFIED',review_state='CLEAR',kind='construction',basis=['COMPUTED'],
          statement='The540 linear one-choice/Gram equations for the5760 primary choices in the frozen complete six-prism model have the saved uniform rational solution x_j=1/96 inside[0,1], and the two separately saved assignments solve their reductions modulo2 and modulo3, respectively.',
          scope='Three specifically defined linear relaxations of one fixed six-prism abstract factor model; no binary integer factor or target feasibility follows.',
          assumptions=['Equations are the complete independently audited one-choice and row-Gram primary-choice system.','No nontrivial target automorphism is assumed.'],
          dependencies=[dict(id='C-SIX-PRISM-COMPLETE-COLUMN-FACTOR-CNF',revision=1,relation='encoding_equivalence')],
          rational=rational,modular=modular,controls_rejected=corrupt,checking_method='Reconstruct raw39/complete domain/equations with independent audited source, then direct Fraction and Python integer sums for every saved witness. No producer imports or elimination.',
          shared_components=['Own frozen independent raw39/domain/equation reconstruction.','Python exact integers, fractions and standard library.'],
          limitations=['Rank345 is unreviewed producer telemetry and is not a claim of this audit.','The three witnesses are separate relaxation witnesses; they are not combined into an integer binary solution.','No auxiliary threshold-CNF satisfying assignment is asserted.','No factor, residual D, target graph or exclusion is established.'],
          floating_point_used=False,solver_calls=0,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as error:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(error),inputs_sha256=bindings));raise

if __name__=='__main__':main()
