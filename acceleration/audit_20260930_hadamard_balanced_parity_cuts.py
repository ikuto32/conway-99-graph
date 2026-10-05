"""Independent necessity of sixty constant-group parity cuts.

No producer imports or solver calls. This proves a necessary consequence for
all balanced factors on the one support, not just the first saved parity model.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from itertools import combinations, permutations, product
from pathlib import Path
import argparse,json,platform,subprocess,sys
import audit_20260930_hadamard_parity_lift_domains as local

ROOT=local.ROOT;B=ROOT/'acceleration/results'
MODEL=B/'20260930_hadamard_balanced_parity/model.json'
MODEL_SHA='a75b60c4ef0f8decd7537d70cced7bffa14cb7a4881de726bf98c96635888147'
GATE=B/'20260930_independent_review/hadamard_balanced_parity/summary.json'
GATE_SHA='8134ed25d5dc06704e6f7f668fa03deec56874eca6d5fad9e6a4138787c7dd76'
need,digest,key,save=local.support.need,local.support.digest,local.support.key,local.support.save
def read(p):return json.loads(Path(p).read_bytes())
def same(a,b):return json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True)

def local_theorem():
    ps=list(permutations(range(3)))
    even=[p for p in ps if local.parity(p)==0];odd=[p for p in ps if local.parity(p)==1]
    incidence=[]
    for i in range(3):
        for j in range(3):
            es=[k for k,p in enumerate(even)if p[i]==j];os=[k for k,p in enumerate(odd)if p[i]==j]
            need(len(es)==len(os)==1,'one even/odd permutation per matrix position');incidence.append([es[0],os[0]])
    need(sorted(incidence)==[[a,b]for a in range(3)for b in range(3)],'all nine even/odd multiplicity equations a_i+b_j=2')
    relative=[]
    for p,q in product(ps,repeat=2):
        signs_equal=local.parity(p)==local.parity(q);fixed=sum(a==b for a,b in zip(p,q))
        need(not(signs_equal and p!=q)or fixed==0,'distinct same-parity permutations have no coincidences')
        relative.append(dict(left=list(p),right=list(q),same_parity=signs_equal,coincidences=fixed))
    triples=local.local_triples();cases=[];counts=Counter()
    for index,words in enumerate(triples):
        signature=local.validate_triple([list(w)for w in words]);maps=[tuple(w[i]for w in words)for i in range(6)]
        mixed=any(signature)
        if mixed:need(sorted(maps)==ps,'every mixed balanced triple uses every S3 permutation exactly once')
        for i,j in combinations(range(6),2):
            same_sign=local.parity(maps[i])==local.parity(maps[j])
            by_fibre=[sum(w[i]==w[j]==g for w in words)for g in range(3)]
            if mixed and same_sign:need(by_fibre==[0,0,0],'mixed equal-parity pair gives all three same-fibre Gram coefficients zero');counts['mixed_equal_parity_zero']+=1
            if mixed and not same_sign:need(sum(by_fibre)==1,'opposite-parity relative permutation has one fixed point');counts['mixed_opposite_parity_one']+=1
            if not mixed and maps[i]==maps[j]:need(by_fibre==[1,1,1],'constant profile can supply the required positive same-fibre contributions');counts['constant_positive_pair']+=1
            cases.append(dict(triple=index,positions=[i,j],mixed=bool(mixed),same_parity=same_sign,same_fibre_coefficients=by_fibre))
    need(len(cases)==2250 and counts==Counter(mixed_equal_parity_zero=720,mixed_opposite_parity_one=1080,constant_positive_pair=90),'all finite local theorem controls')
    return dict(permutations=[list(p)for p in ps],even_odd_matrix_incidence=incidence,relative_permutation_cases=relative,balanced_triples=[list(map(list,t))for t in triples],all_coordinate_pair_records=cases,counts=dict(counts))

def reconstruct_cuts(raw,model):
    core,gram,L,supports,_,groups=local.support.reconstruct(raw)
    patterns=[[0]*6]+[list(p)for p in product(range(2),repeat=6)if p[0]==0 and sum(p)==3]
    expectedgroups=[dict(group=g,support=supports[cols[0]],selectors=list(range(11*g+1,11*g+12)),parity_patterns=patterns)for g,cols in enumerate(groups)]
    need(same(model['groups'],expectedgroups),'all group patterns and selector literal definitions')
    expectedrows=[];cuts=[];nextvar=220
    for a,b in combinations(range(12),2):
        if a^1==b:continue
        incident=[g for g,cols in enumerate(groups)if a in supports[cols[0]] and b in supports[cols[0]]]
        need(len(incident)==5,'all five co-occurring support triples')
        need([gram[12*g+a][12*g+b]for g in range(3)]==[1,1,1],'literal same-fibre Gram RHS one')
        terms=[];constant=[]
        for g in incident:
            coords=supports[groups[g][0]];i,j=coords.index(a),coords.index(b)
            disagree=[11*g+k+1 for k,p in enumerate(patterns)if p[i]!=p[j]];need(len(disagree)==6,'six local disagreement patterns')
            nextvar+=1;terms.append(dict(group=g,difference_variable=nextvar,disagree_selectors=disagree));constant.append(11*g+1)
        expectedrows.append(dict(coordinates=[a,b],terms=terms,allowed_disagreement_counts=[0,3]))
        cuts.append(dict(coordinates=[a,b],groups=incident,difference_literals=[t['difference_variable']for t in terms],constant_pattern_literals=constant,clause=[t['difference_variable']for t in terms]+constant,required_same_fibre_Gram=[1,1,1],scope='Necessary for any balanced full-Gram factor on this support; no selected parity branch premise.'))
    need(same(model['pair_rows'],expectedrows)and nextvar==520 and len(cuts)==60,'all sixty raw pair/auxiliary definitions')
    need(model['variables']==520 and model['primary_selectors']==220 and model['additional_balance_assumption']is True and model['target_graph']is False and model['residual_D']is False,'precise model projection scope')
    return cuts

def controls(raw,model,theorem,cuts):
    rejected=[]
    def reject(label,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,TypeError):rejected.append(label)
        else:raise ValueError('accepted bad control '+label)
    for name in ['changed_difference_ID','changed_constant_selector','changed_pattern','changed_group_support','missing_balance']:
        bad=deepcopy(model)
        if name=='changed_difference_ID':bad['pair_rows'][0]['terms'][0]['difference_variable']+=1
        elif name=='changed_constant_selector':bad['groups'][0]['selectors'][0]+=1
        elif name=='changed_pattern':bad['groups'][0]['parity_patterns'][0][1]=1
        elif name=='changed_group_support':bad['groups'][0]['support'][0]^=1
        else:bad['additional_balance_assumption']=False
        reject(name,lambda bad=bad:reconstruct_cuts(raw,bad))
    badraw=deepcopy(raw);badraw['prescribed_Gram36'][0][2]=0
    reject('changed_Gram_RHS',lambda:reconstruct_cuts(badraw,model))
    c=cuts[0]['clause'];need(len(c)==10 and len(set(c))==10 and all(x>0 for x in c),'positive cut mapping')
    truth=[]
    for bits in product(range(2),repeat=10):
        clause=any(bits);forbidden=(sum(bits[:5])==0 and sum(bits[5:])==0)
        need(clause==not_(forbidden),'all cut Boolean truth cases')
        truth.append(int(clause))
    # Actual positive local case: a constant triple has a repeated coordinate
    # permutation and contributes one to each same-fibre Gram entry.
    positive=next(x for x in theorem['all_coordinate_pair_records']if not x['mixed']and x['same_fibre_coefficients']==[1,1,1])
    wrong=deepcopy(positive);wrong['mixed']=True
    reject('false_mixed_positive_pair',lambda:need(not wrong['mixed']or wrong['same_fibre_coefficients']==[0,0,0],'mixed same-sign must be zero'))
    reject('negated_difference_cut',lambda:need(all(x>0 for x in [-c[0],*c[1:]]),'all required disjuncts positive'))
    return dict(cut_truth_cases=len(truth),accepted_truth_cases=sum(truth),local_positive_record=positive,corruptions_rejected=rejected,known243_fixture_used=False,known243_not_applicable_reason='The additional fixed-support balanced-triplet hypothesis is not asserted for the SRG243 control; local exact finite permutation controls establish the relevant domain.')

def not_(x):return not x

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'input identity '+key(p));pins[key(p)]=value
    try:
        for p,h in[(local.RAW,local.RAW_SHA),(MODEL,MODEL_SHA),(GATE,GATE_SHA)]:pin(p,h)
        gate=read(GATE);need(gate['inputs_sha256'][key(MODEL)]==MODEL_SHA,'independent projection encoding gate binds old model')
        theorem=local_theorem();cuts=reconstruct_cuts(read(local.RAW),read(MODEL));calibration=controls(read(local.RAW),read(MODEL),theorem,cuts)
        save(args.out/'local_permutation_controls.json',theorem);save(args.out/'necessary_clauses.json',dict(variables=520,clauses=cuts,additional_balance_assumption=True,one_fixed_support=True,all_balanced_parity_branches=True,actual_factor=None,actual_factor_reason='A necessity theorem; no factor constructed.'))
        save(args.out/'controls.json',calibration)
        for p in[Path(__file__),Path(local.__file__),Path(local.support.__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_BALANCED_PARITY_CUTS.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat();cid='C-FIXED-HADAMARD-BALANCED-PARITY-CONSTANT-GROUP-NECESSITY'
        limitation=['Only factors with the additional coordinatewise balanced three-column-group restriction on the exact six-prism Hadamard support.','No particular saved parity assignment is a mathematical premise.','No residual D, target graph, unrestricted nonexistence, or novelty claim.','This report verifies the necessary clauses and original literal map; it does not authenticate a future appended DIMACS artifact.','The original model final nonconstant-group clause and its cyclic-exclusion premise are not needed for this new local necessity proof.']
        metadata=dict(id=cid,revision=1,statement='For every binary full-prescribed-Gram factor on the frozen six-prism Hadamard support whose three columns in each identical-support group are coordinatewise balanced, each nonmatched coordinate pair satisfies this necessary condition: among its five co-occurring groups, at least one has unequal coordinate-permutation parities or has constant normalized parity on all six coordinates.',kind='mathematical result',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope='All balanced parity branches on one exact fixed support, not arbitrary fixed-support factors.',assumptions=['The full prescribed Gram and explicit coordinatewise balanced group hypothesis.','No nontrivial target automorphism is assumed.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='uses_result'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='verification_dependency'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-BALANCED-PARITY-PROJECTION',revision=1,relation='encoding_equivalence')],verifier='/root/state_literature_audit',method='Independent universal multiplicity argument and full finite S3-array checks; no producer imports',limitations=limitation,created_at=now,updated_at=now,artifact_availability='LOCAL_ONLY')
        report=dict(status='INDEPENDENT_HADAMARD_BALANCED_PARITY_CONSTANT_GROUP_CUTS_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):digest(p)for p in args.out.iterdir()if p.is_file()},claim_id=cid,claim_revision=1,verifier='/root/state_literature_audit',method=metadata['method'],counts=dict(coordinate_permutation_arrays=46656,balanced_local_triples=150,local_pair_records=2250,relative_permutation_cases=36,mixed_equal_parity_zero_cases=720,positive_constant_coincidence_cases=90,necessary_clauses=60,literals_per_clause=10,cut_truth_cases=1024,corruptions_rejected=len(calibration['corruptions_rejected'])),producer_imports=False,shared_components=['Own independent ordered-support core/Gram checker and new S3-array enumeration helper.','Python standard library; no producer classification, factor encoding or solver code imported.'],recommendation='VERIFIED',limitations=limitation,solver_calls=0,target_resolution=False,artifact_availability='LOCAL_ONLY')
        save(args.out/'summary.json',report);metadata['evidence']=[dict(path=key(args.out/'summary.json'),sha256=digest(args.out/'summary.json'),availability='LOCAL_ONLY')];save(args.out/'claim_binding.json',metadata)
        print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'),claim_binding_sha256=digest(args.out/'claim_binding.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(error=repr(e)));raise

if __name__=='__main__':main()
