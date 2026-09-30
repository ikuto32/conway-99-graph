"""Complete strengthened parity CNF and raw projection audit; no solver."""
from copy import deepcopy
from datetime import datetime,timezone
from itertools import product
from pathlib import Path
import argparse,json,platform,subprocess,sys
import audit_20260930_hadamard_balanced_parity_v2 as base
import audit_20260930_hadamard_balanced_parity_cuts as lemma

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';D=B/'20260930_hadamard_parity_support_cuts'
RAW=lemma.local.RAW;OLD_MODEL=ROOT/base.MODEL;OLD_CNF=ROOT/base.CNF
GENERAL=B/'20260930_independent_review/hadamard_balanced_parity_cuts/summary.json'
OLD_GATE=B/'20260930_independent_review/hadamard_balanced_parity/summary.json'
DELTA=B/'20260930_independent_review/hadamard_parity_object_v2_delta/summary.json'
OLD_SAT=B/'20260930_independent_review/hadamard_balanced_parity_sat_v2/summary.json'
PINS={
 D/'summary.json':'73b213a34c58ce0fbaa5c200394941a43f0840a6e29307e8ed1d8aa64e3c2e31',
 D/'instance.cnf':'db9816ddf037250efc04b1e093e407eac0ec2c4fadf2f24b5774fb3249eba07f',
 D/'model.json':'c477693bbf634609c234bf5b791c499f8f9ded091795b01bec297746288b4f4f',
 OLD_MODEL:'a75b60c4ef0f8decd7537d70cced7bffa14cb7a4881de726bf98c96635888147',
 OLD_CNF:'92801921a62236effa19b0f6e7463c6f5c1ca2cb0b6957cf7d315a73e0e43fca',
 GENERAL:'31c47c1faccc8ae043433f814932e2d419e1c2a188ffc1bd54a53b21ceeca6c1',
 OLD_GATE:'8134ed25d5dc06704e6f7f668fa03deec56874eca6d5fad9e6a4138787c7dd76',
 DELTA:'599b7b2f713124e658ce0a7c3b06be0d0a79f170a5fb9fed45531eb5aec914b5',
 OLD_SAT:'d2536119ac3fa0d45c190a6562de2ccc67c3f9c9765fbfc03257e37b15097f9c',
 RAW:lemma.local.RAW_SHA,
 Path(base.__file__):'74557011dc83dd38a302766392273278e10b6ecc58fcc0639bbf4b0a78a8f7ae',
}
need=base.need
def read(p):return json.loads(Path(p).read_bytes())
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):return base.h(p)
def save(p,x):return base.save(p,x)
def same(a,b):return json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True)

def reconstruct(model,oldmodel,raw):
    prefix,groups,pairs=base.reconstruct(raw,oldmodel)
    necessary=lemma.reconstruct_cuts(raw,oldmodel)
    records=[dict(coordinates=c['coordinates'],groups=c['groups'],difference_variables=c['difference_literals'],constant_selectors=c['constant_pattern_literals'],clause=c['clause'])for c in necessary]
    expected=deepcopy(oldmodel);expected.update(schema='BALANCED_TRIPLET_PARITY_SUPPORT_CUT_CNF_V1',clauses=4541,zero_disagreement_support_cuts=records,original_model_sha256=PINS[OLD_MODEL],original_formula_sha256=PINS[OLD_CNF],scope='Strengthened necessary balanced parity projection for one fixed support with column caps; no full-factor equivalence.')
    need(same(model,expected),'all strengthened model fields and sixty independently reconstructed cuts')
    return prefix+[x['clause']for x in records],groups,pairs,records

def raw_cut_checks(patterns,groups,pairs,require_all=True):
    need(len(patterns)==20 and all(type(p)is list and len(p)==6 and all(type(v)is int and v in(0,1)for v in p) and p in g['parity_patterns']for p,g in zip(patterns,groups,strict=True)),'twenty literal allowed parity patterns')
    records=[]
    for pair in pairs:
        a,b=pair['coordinates'];different=0;constant=[]
        for term in pair['terms']:
            g=term['group'];coords=groups[g]['support'];p=patterns[g]
            different+=int(p[coords.index(a)]!=p[coords.index(b)])
            if not any(p):constant.append(g)
        ok=different>0 or len(constant)>0
        records.append(dict(coordinates=[a,b],disagreement_count=different,selected_constant_groups=constant,satisfied=ok))
    need(not require_all or all(r['satisfied']for r in records),'all sixty raw-pattern support cuts')
    return records

def check_object(values,clauses,groups,pairs,decoded=None):
    need(not base.satisfied(clauses,values),'all 4541 actual clauses')
    result=base.projection(values,groups,pairs)
    result['model_sha256']=PINS[D/'model.json']
    result['support_cut_checks']=raw_cut_checks(result['selected_group_parity_patterns'],groups,pairs)
    if decoded is not None:
        base.compare_decoded(result,decoded)
        need(same(decoded['support_cut_checks'],result['support_cut_checks']),'all sixty exact raw-pattern decoded records')
    return result

def primitive_and_corrupt_controls(model,oldmodel,raw,clauses,groups,pairs):
    rejected=[]
    def reject(name,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,TypeError):rejected.append(name)
        else:raise ValueError('bad strengthened parity control accepted '+name)
    for name in ['missing_cut','negated_cut','wrong_auxiliary','wrong_constant','scope_balance','general_support','changed_original_pin']:
        bad=deepcopy(model)
        if name=='missing_cut':bad['zero_disagreement_support_cuts'].pop()
        elif name=='negated_cut':bad['zero_disagreement_support_cuts'][0]['clause'][0]*=-1
        elif name=='wrong_auxiliary':bad['zero_disagreement_support_cuts'][0]['difference_variables'][0]+=1
        elif name=='wrong_constant':bad['zero_disagreement_support_cuts'][0]['constant_selectors'][0]+=1
        elif name=='scope_balance':bad['additional_balance_assumption']=False
        elif name=='general_support':bad['scope']='Unrestricted target equivalence'
        else:bad['original_formula_sha256']='0'*64
        reject(name,lambda bad=bad:reconstruct(bad,oldmodel,raw))
    full=base.cnf_bytes(clauses)
    reject('changed_prefix_literal',lambda:need(base.cnf_bytes([[-clauses[0][0],*clauses[0][1:]],*clauses[1:]])==full,'complete prefix bytes'))
    reject('dropped_last_clause',lambda:need(base.cnf_bytes(clauses[:-1])==full,'complete extension bytes'))
    for mask in range(2048):
        vals={i+1:bool(mask&(1<<i))for i in range(11)}
        need((not base.satisfied(clauses[:56],vals))==(mask.bit_count()==1),'full one-hot truth')
    orclauses=[[-i,7]for i in range(1,7)]+[[-7,*range(1,7)]]
    for mask in range(128):
        vals={i+1:bool(mask&(1<<i))for i in range(7)}
        need((not base.satisfied(orclauses,vals))==(vals[7]==any(vals[i]for i in range(1,7))),'full difference OR truth')
    for bits in product(range(2),repeat=10):need(bool(any(bits))==(sum(bits[:5])>0 or sum(bits[5:])>0),'full support-cut truth')
    oldpath=B/'20260930_hadamard_balanced_parity_native_pilot/main/parsed_model.json'
    oldvalues=base.assignment(read(oldpath)['assignment'],520)
    need(not base.satisfied(clauses[:4481],oldvalues),'actual old positive still satisfies old formula')
    oldprojection=base.projection(oldvalues,groups,pairs)
    oldchecks=raw_cut_checks(oldprojection['selected_group_parity_patterns'],groups,pairs,False)
    failed=[r['coordinates']for r in oldchecks if not r['satisfied']]
    need(failed==[[4,9],[7,11]] and len(base.satisfied(clauses,oldvalues))==2,'actual old SAT object violates precisely two new cuts')
    reject('old_projection_not_strengthened_SAT',lambda:check_object(oldvalues,clauses,groups,pairs))
    # Metadata comparisons are calibrated on an explicitly invalid-for-the-new-
    # formula old projection; this does not invent a positive new SAT object.
    expected=deepcopy(oldprojection);expected['support_cut_checks']=oldchecks;expected['model_sha256']=PINS[D/'model.json']
    comparison=deepcopy(expected)
    for record in comparison['group_records']:record['parity_mask_hex']=format(int(record['parity_mask_hex'],16),'02x')
    base.compare_decoded(expected,comparison)
    for name in ['changed_raw_cut_count','changed_raw_cut_satisfaction','changed_hexmask','changed_model_hash','target_graph_flag']:
        bad=deepcopy(comparison)
        if name=='changed_raw_cut_count':bad['support_cut_checks'][0]['disagreement_count']+=1
        elif name=='changed_raw_cut_satisfaction':bad['support_cut_checks'][0]['satisfied']=not bad['support_cut_checks'][0]['satisfied']
        elif name=='changed_hexmask':bad['group_records'][0]['parity_mask_hex']='ff'
        elif name=='changed_model_hash':bad['model_sha256']='0'*64
        else:bad['target_graph']=True
        reject(name,lambda bad=bad:base.compare_decoded(expected,bad))
    constant=[[0]*6 for _ in range(20)];checks=raw_cut_checks(constant,groups,pairs)
    need(len(checks)==60 and all(len(x['selected_constant_groups'])==5 and x['disagreement_count']==0 for x in checks),'raw positive for added cuts only')
    constantvalues={i:False for i in range(1,521)}
    for g in groups:constantvalues[g['selectors'][0]]=True
    need(base.satisfied(clauses,constantvalues)==[4481],'all-constant object fails only original nonconstant clause')
    reject('all_constant_not_strengthened_SAT',lambda:check_object(constantvalues,clauses,groups,pairs))
    synthetic=[i if i%2 else -i for i in range(1,521)];vals=base.assignment(synthetic,520)
    text='c SYNTHETIC CODEC ONLY; NOT RESEARCH SAT\ns SATISFIABLE\nv '+' '.join(map(str,synthetic))+' 0\n'
    need(base.native(text,520)==vals,'all520 synthetic native/JSON identity')
    syntheticclauses=[[synthetic[i%520]]for i in range(4541)]
    need(not base.satisfied(syntheticclauses,vals),'full4541 synthetic clause positive')
    for name,bad in [('missing_status',text.replace('s SATISFIABLE\n','')),('wrong_status',text.replace('SATISFIABLE','UNSATISFIABLE')),('missing_zero',text.replace(' 0\n','\n')),('post_zero_literal',text+'v 1\n'),('duplicate_ID',text.replace('v 1 -2','v 1 1'))]:reject(name,lambda bad=bad:base.native(bad,520))
    reject('short_JSON',lambda:base.assignment(synthetic[:-1],520));reject('Boolean_JSON',lambda:base.assignment([True,*synthetic[1:]],520))
    badcs=deepcopy(syntheticclauses);badcs[0][0]*=-1
    reject('false_synthetic_clause',lambda:need(not base.satisfied(badcs,vals),'false clause refused'))
    badpatterns=deepcopy(oldprojection['selected_group_parity_patterns']);badpatterns[0][0]=1
    reject('invalid_gauge_pattern',lambda:raw_cut_checks(badpatterns,groups,pairs,False))
    return dict(onehot_truth_cases=2048,OR_truth_cases=128,support_cut_truth_cases=1024,old_positive_scope='Actual520-ID SAT witness for old4481 clauses only; rejected by two added clauses.',old_violated_coordinate_pairs=failed,all_constant_scope='Positive for all60 added cuts only; fails the original nonconstant-group clause.',raw_all_constant_cut_records=checks,synthetic_scope='520-ID/4541-clause codec positive with synthetic unit formula, not research SAT.',corruptions_rejected=rejected),text,syntheticclauses

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['audit','calibrate','sat']);ap.add_argument('--encoding-gate',type=Path);ap.add_argument('--encoding-gate-sha256');ap.add_argument('--assignment',type=Path);ap.add_argument('--native-output',type=Path);ap.add_argument('--decoded',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(p,h=None):
        p=p.resolve();v=sha(p);need(h is None or v==h,'input identity '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        producer=read(D/'summary.json')
        for p,h in{**producer['inputs_sha256'],**producer['outputs_sha256']}.items():pin(ROOT/p,h)
        for gp in[GENERAL,OLD_GATE,DELTA,OLD_SAT]:
            g=read(gp)
            for p,h in{**g['inputs_sha256'],**g.get('outputs_sha256',{})}.items():pin(ROOT/p,h)
        need(read(GENERAL)['status']=='INDEPENDENT_HADAMARD_BALANCED_PARITY_CONSTANT_GROUP_CUTS_PASS','exact general necessity gate')
        need(read(OLD_GATE)['status']=='INDEPENDENT_HADAMARD_BALANCED_PARITY_ENCODING_PASS','old full encoding gate')
        need(read(DELTA)['status']=='INDEPENDENT_HADAMARD_PARITY_OBJECT_V2_DELTA_AND_CALIBRATION_PASS','unchanged corrected raw helper review')
        model=read(D/'model.json');oldmodel=read(OLD_MODEL);raw=read(RAW);clauses,groups,pairs,records=reconstruct(model,oldmodel,raw)
        need(OLD_CNF.read_bytes()==base.cnf_bytes(clauses[:4481]),'all original4481 raw clauses independently rebuilt')
        need((D/'instance.cnf').read_bytes()==base.cnf_bytes(clauses),'all4541 literal clauses and header')
        need(same(read(D/'added_clauses.json'),records),'every saved extension record')
        calibration,text,synthetic=primitive_and_corrupt_controls(model,oldmodel,raw,clauses,groups,pairs)
        save(out/'controls.json',calibration);(out/'synthetic_native.log').write_text(text,encoding='ascii');(out/'synthetic.cnf').write_bytes(base.cnf_bytes(synthetic))
        if args.mode!='audit':
            need(args.encoding_gate is not None and args.encoding_gate_sha256,'explicit independent encoding gate')
            pin(args.encoding_gate,args.encoding_gate_sha256);g=read(args.encoding_gate)
            need(g['status']=='INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_ENCODING_PASS','new encoding gate')
            for p in[D/'instance.cnf',D/'model.json',GENERAL,OLD_GATE]:need(g['inputs_sha256'][key(p)]==PINS[p],'same full encoding premise '+key(p))
        result=None
        if args.mode=='sat':
            need(args.assignment is not None and args.native_output is not None,'complete raw SAT inputs')
            pin(args.assignment);pin(args.native_output);values=base.assignment(read(args.assignment)['assignment'],520)
            need(base.native(args.native_output.read_text(),520)==values,'all raw native/JSON assignments agree')
            decoded=None
            if args.decoded:pin(args.decoded);decoded=read(args.decoded)
            result=check_object(values,clauses,groups,pairs,decoded);save(out/'independent_projection.json',result)
        for p in[Path(__file__),Path(lemma.__file__),Path(lemma.local.__file__),Path(lemma.local.support.__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_PARITY_SUPPORT_CUTS.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        status=dict(audit='INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_ENCODING_PASS',calibrate='INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_OBJECT_CHECKER_CALIBRATION_PASS',sat='INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_SAT_OBJECT_PASS')[args.mode]
        now=datetime.now(timezone.utc).isoformat();limitations=['Necessary projection only for the balanced-triplet fixed-support family with outside-column caps; no full factor equivalence.','No proof that arbitrary factors are balanced; no other support covered.','A SAT projection is neither a Gram factor nor a target graph; residual D is absent.','UNSAT needs separate complete proof replay; the complete semantic premise includes the earlier cyclic-factor exclusion through the original nonconstant-group clause.','No solver called by this checker; no full research-positive projection for the new formula is invented.']
        report=dict(status=status,timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},encoding_gate_sha256=args.encoding_gate_sha256 if args.mode!='audit'else None,encoding_gate_null_reason='This report is the encoding gate.'if args.mode=='audit'else None,verifier='/root/state_literature_audit',method='Full independent original-clause reconstruction plus independent proved-extension mapping; complete raw projection checking',counts=dict(variables=520,clauses=4541,old_clauses=4481,new_clauses=60,old_witness_new_violations=2,corruptions_rejected=len(calibration['corruptions_rejected'])),shared_components=['Frozen independently authored Eight v2 reconstruction/native/assignment/projection helpers, exact source hash bound.','Own separate universal constant-group necessity audit and literal-map checker.','Standard library only; no producer encoder/decoder/native-wrapper import.'],recommendation='VERIFIED'if args.mode=='audit'else None,limitations=limitations,artifact_availability='LOCAL_ONLY',target_resolution=False,solver_calls=0)
        save(out/'summary.json',report)
        if args.mode=='audit':
            save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-PROJECTION',revision=1,statement='Every coordinatewise balanced full-prescribed-Gram factor on the fixed six-prism Hadamard support that satisfies all outside-column caps induces a satisfying assignment of the authenticated 520-variable, 4541-clause formula consisting of the original parity projection and all sixty constant-group support cuts.',kind='encoding',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope=limitations[0],assumptions=['The explicit fixed support, full Gram, coordinatewise balance and outside-column caps.','No nontrivial target automorphism is assumed.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-BALANCED-PARITY-PROJECTION',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-BALANCED-PARITY-CONSTANT-GROUP-NECESSITY',revision=1,relation='uses_result')],verifier=report['verifier'],method=report['method'],evidence=[dict(path=key(out/'summary.json'),sha256=sha(out/'summary.json'),availability='LOCAL_ONLY')],limitations=limitations,created_at=now,updated_at=now))
        print(json.dumps(dict(status=status,sha256=sha(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise

if __name__=='__main__':main()
