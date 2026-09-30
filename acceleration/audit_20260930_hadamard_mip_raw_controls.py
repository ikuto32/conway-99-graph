"""Calibrate exact MIP-value and cap-aware raw-factor helpers, no MIP run."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse,json,math,platform,subprocess,sys
import audit_20260930_hadamard_mip_raw as raw
import audit_20260930_fixed_support_raw_preparation as full
ROOT=full.ROOT;need,digest,key,read,save=full.need,full.digest,full.key,full.read,full.save

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);bindings={};rejected=[]
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'exact input '+key(p));bindings[key(p)]=value
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError,IndexError,TypeError):rejected.append(name)
        else:raise ValueError('accepted malformed control '+name)
    try:
        prep=ROOT/'acceleration/results/20260930_independent_review/fixed_support_raw_preparation/summary.json';pin(prep,'61c45a7f3efde426bc6e6f6010af1f718885c26f79c487ee877467f2b2d1136e')
        for p,h in read(prep)['inputs_sha256'].items():pin(ROOT/p,h)
        fixture=ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json';pin(fixture,'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439');f=read(fixture);c=f['cubic_core60'];factor=f['factor60x180'];l=[[sum(factor[20*g+a][d]for g in range(3))for d in range(180)]for a in range(20)]
        checked=raw.gram_factor(c,factor,l,research=False);old,_,_=full.verify_fixed_support(c,factor,l,research=False);need(checked['all_caps_valid']and checked['canonical_factor']==old['canonical_factor']['incidence_matrix'],'genuine positive and distinct raw checking paths agree')
        save(out/'known243_positive.json',dict(parameters=[243,22,1,2],classification=checked['classification'],exact_checks=checked['exact_checks'],maximum_column_overlap=max(v[2]for v in checked['all_column_overlaps']),not_research99=True))
        for name in ['bit','Boolean_bit','core','fixed_support','degree_preserving_Gram','duplicate_C0']:
            cc=deepcopy(c);ff=deepcopy(factor);ll=deepcopy(l)
            if name=='bit':ff[20][0]^=1
            elif name=='Boolean_bit':ff[20][0]=bool(ff[20][0])
            elif name=='core':cc[0][1]^=1
            elif name=='fixed_support':ll[0][0]^=1
            elif name=='degree_preserving_Gram':
                for row in ff[20:40]:row[0],row[1]=row[1],row[0]
            else:
                for row in ff[:20]:row[1]=row[0]
            reject(name,lambda cc=cc,ff=ff,ll=ll:raw.gram_factor(cc,ff,ll,research=False))
        reject('243_not_research99',lambda:raw.gram_factor(c,factor,l))
        values=[0.0,1.0,-5e-8,1+5e-8,math.nextafter(1e-7,0.0),1-math.nextafter(1e-7,0.0)];bits,rounding=raw.rounded_binary(values,len(values));need(bits==[0,1,0,1,0,1],'finite rounding positives')
        for name,v in [('fractional',0.5),('outside',1.01),('nan',float('nan')),('infinity',float('inf')),('Boolean',True),('just_above_threshold',math.nextafter(1e-7,math.inf))]:reject(name,lambda v=v:raw.rounded_binary([v],1))
        reject('missing_value',lambda:raw.rounded_binary([0.0],2))
        columns=[[0,2],[0],[0],[1],[1,2],[1]];rhs=[1,1,2];orders=[dict(terms=[[0,0],[1,1],[2,2],[3,0],[4,-1],[5,-2]])];cuts=[[1,4]];positive,order_values=raw.exact_linear([1,0,0,0,1,0],columns,rhs,orders,cuts)
        truth=0;accepted=0
        for tup in product((0,1),repeat=6):
            expected=sum(tup[:3])==1 and sum(tup[3:])==1 and tup[0]+tup[4]==2 and tup[1]+2*tup[2]-tup[4]-2*tup[5]<=-1 and tup[1]+tup[4]<=1
            try:raw.exact_linear(list(tup),columns,rhs,orders,cuts);actual=True
            except ValueError:actual=False
            need(actual==expected,'complete six-bit exact linear oracle');truth+=1;accepted+=actual
        reject('false_cut',lambda:raw.exact_linear([1,0,0,0,1,0],columns,rhs,orders,[[0,4]]));reject('negative_cut_index',lambda:raw.exact_linear([1,0,0,0,1,0],columns,rhs,orders,[[-1,1]]));reject('wrong_RHS',lambda:raw.exact_linear([1,0,0,0,1,0],columns,[1,1,1],orders,cuts))
        cols=[{0,1,2,3},{1,2,3,4},{0,4},{0,1,2,3}];toy=[[int(i in s)for s in cols]for i in range(5)];overlaps,violations=raw.column_caps(toy);need(overlaps==[[0,1,3],[0,2,1],[0,3,4],[1,2,1],[1,3,3],[2,3,1]],'exact cap classifier toy oracle');need([x['columns']for x in violations]==[[0,1],[0,3],[1,3]],'retain every invalid pair')
        save(out/'exact_controls.json',dict(rounding=rounding,rounded_values=bits,linear_truth_assignments=truth,linear_accepted=accepted,cap_toy_overlaps=overlaps,cap_toy_violations=violations,cap_toy_scope='Intersection classifier only; this toy is not an SRG Gram factor.',corruptions_rejected=rejected))
        for p in [Path(__file__),Path(raw.__file__),ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        report=dict(status='INDEPENDENT_HADAMARD_MIP_RAW_HELPER_CALIBRATION_PASS_NOT_MODEL_GATE',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,outputs_sha256={key(p):digest(p)for p in out.iterdir()if p.is_file()},verifier='/root/state_literature_audit',producer_imports=False,artifact_availability='LOCAL_ONLY',target_resolution=False,research_calls=0,corruptions_rejected=rejected,shared_components=['Previously independently authored complete raw factor checker used only to cross-check the genuine243 positive.','New direct set-intersection Gram and cap path plus exact rational tolerance comparisons.'],limitations=['Raw helper calibration only; no MIP matrix, solver result or research factor is approved.','A Gram-valid/cap-invalid branch will be labelled as weaker evidence; no such research witness is invented here.'])
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
