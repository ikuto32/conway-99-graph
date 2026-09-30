"""Independent complete first-class falsification; no producer imports."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
CAT=B+'hadamard_triplicate_counts/local_triples.json'
SIG=B+'hadamard_count_master_preflight/local_signatures.json'
CAND=B+'count_interval_frechet_v2/summary.json'
PINS={CAT:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',SIG:'075120017568ecbb0da5369f8e45c0dafd015ae4953681491bab66f04e9fdb45',B+'independent_review/count_gram_intervals/summary.json':'ebace5fc527bded41f3c31fb66455e78b0eb133c8575508d4426eff912e6ae33','acceleration/theory_20260930_count_interval_frechet_v2.py':'f5a3f4cdfaf84bc5f3542b6912935f45f7d509897504dedc4aa6967656b6d679','acceleration/theory_20260930_count_interval_frechet_v2_spec.md':'8fb5fe8717ec8de989cba7850441f3737bcf637ad74cd758de2c3a04e4833b67'}
PINS[CAND]='d18a0926a504090e63eab9f1669fec8ae9c688107673f52691f82d364dccc214'
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def word_check(w):
    need(len(w)==6 and all(type(x)is int and x in (0,1,2) for x in w) and Counter(w)=={0:2,1:2,2:2},'literal balanced word')
def signature(ws):return [sum(w[a]==f for w in ws) for a in range(6) for f in range(3)]
def literal(ws):
    for w in ws:word_check(w)
    need(len(ws)==3 and len({tuple(w) for w in ws})==3,'three distinct words')
    rows=[{d for d,w in enumerate(ws) if w[a]==f} for a in range(6) for f in range(3)]
    gram=[[len(x&y) for y in rows] for x in rows]
    errors=[]
    for a,b in combinations(range(6),2):
        for f,g in product(range(3),repeat=2):
            if gram[3*a+f][3*b+g]>(1 if f==g else 2):errors.append(dict(kind='Gram',coordinates=[a,b],fibres=[f,g]))
    overlaps=[sum(ws[i][a]==ws[j][a] for a in range(6)) for i,j in combinations(range(3),2)]
    for k,v in enumerate(overlaps):
        if v>2:errors.append(dict(kind='column_cap',pair_index=k,value=v))
    return dict(words=[list(w) for w in ws],signature=signature(ws),row_column_sets=[sorted(x) for x in rows],Gram18=gram,column_overlaps=overlaps,violations=errors)
def selected_check(record,words,indices,sig):
    need(record==literal([words[i] for i in indices]),'literal record and every integer Gram entry')
    need(record['signature']==sig and not record['violations'],'class membership and caps')
def verify_family(records,words,allindices,sig):
    need([r['word_indices'] for r in records]==allindices,'complete independently enumerated class')
    for r,ids in zip(records,allindices,strict=True):selected_check(r['literal'],words,ids,sig)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic();pins={}
    def load(p,h=None):
        pins[p]=sha(p);need(h is None or h==pins[p],'identity '+p);return json.loads((ROOT/p).read_bytes())
    try:
        for p,h in PINS.items():pins[p]=sha(p);need(pins[p]==h,'frozen input '+p)
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_LOCAL_FRECHET_EQUALITY_REFUTATION.md','uv.lock','pyproject.toml']:pins[p]=sha(p)
        candidate=load(CAND);cat=load(CAT);signatures=load(SIG)['signatures'];first=candidate['first_counterexample']
        need(first['signature_index']==0 and first['cell_index']==48,'unchanged predeclared selection')
        sig=signatures[0]['counts'];need(sig==[0,0,3,0,2,1,1,1,1,1,1,1,2,1,0,2,1,0],'exact count vector')
        # Build the complete word universe by choosing positions for colours0 and1.
        words=[]
        for zero in combinations(range(6),2):
            for one in combinations([x for x in range(6) if x not in zero],2):
                words.append(tuple(0 if x in zero else 1 if x in one else 2 for x in range(6)))
        words=sorted(words);need(len(words)==len(set(words))==90 and [list(w) for w in words]==cat['words'],'complete literal word universe')
        examined=0;matched=[];accepted=[]
        for ids in combinations(range(90),3):
            examined+=1;ws=[words[i] for i in ids]
            if signature(ws)!=sig:continue
            raw=literal(ws);entry=dict(word_indices=list(ids),literal=raw);matched.append(entry)
            if not raw['violations']:accepted.append(entry)
            need(time.monotonic()-started<60,'declared60s allocation')
        need(examined==117480,'complete unordered word-triple universe')
        ids=[r['word_indices'] for r in accepted];verify_family(accepted,words,ids,sig)
        catalogue_ids=[i for i,t in enumerate(cat['survivors']) if signature([words[j] for j in t])==sig]
        need(catalogue_ids==signatures[0]['local_survivor_indices']==[31107,31109] and [cat['survivors'][i] for i in catalogue_ids]==ids and len(accepted)==signatures[0]['count']==2,'complete matching catalogue class')
        cells=[(x,y,f,g) for x,y in combinations(range(6),2) for f,g in product(range(3),repeat=2)];x,y,f,g=cells[48]
        values=[r['literal']['Gram18'][3*x+f][3*y+g] for r in accepted];n,m=sig[3*x+f],sig[3*y+g];lo=max(0,n+m-3);hi=min(n,m,1 if f==g else 2)
        need((x,y,f,g)==(1,2,1,0) and [n,m]==[2,1] and values==[1,1] and [lo,hi]==[0,1],'independent strict counterexample')
        need(first==dict(signature_index=0,cell_index=48,row_counts=[n,m],fibres=[f,g],proposed_minimum=lo,proposed_maximum=hi,actual_minimum=min(values),actual_maximum=max(values)),'candidate first counterexample exactly reproduced')
        # Unconstrained subset controls distinguish true bounds from the false equality assertion.
        subsets=[{i for i in range(3) if mask>>i&1} for mask in range(8)];checked=0;capchecked=0;rangechecked=0
        for u,v in product(subsets,repeat=2):
            need(max(0,len(u)+len(v)-3)<=len(u&v)<=min(len(u),len(v)),'valid loose Frechet inequalities');checked+=1
            for cap in (1,2):
                if len(u&v)<=cap:need(len(u&v)<=min(len(u),len(v),cap),'valid cap upper inequality');capchecked+=1
        for n,m in product(range(4),repeat=2):
            vals=[len(u&v) for u,v in product(subsets,repeat=2) if len(u)==n and len(v)==m]
            need(min(vals)==max(0,n+m-3) and max(vals)==min(n,m),'known unrestricted fixed-cardinality extrema');rangechecked+=1
        cyclic=literal([[((a//2)+shift)%3 for a in range(6)] for shift in range(3)]);need(not cyclic['violations'],'known positive cyclic local triple')
        rejected=[]
        def reject(name,fn):
            try:fn()
            except (ValueError,IndexError,KeyError):rejected.append(name)
            else:raise ValueError('accepted corruption '+name)
        bad=deepcopy(accepted);bad[0]['literal']['Gram18'][4][6]=0;reject('lowered_counterexample_value',lambda:verify_family(bad,words,ids,sig))
        reject('omitted_class_member',lambda:verify_family(accepted[:-1],words,ids,sig))
        reject('duplicated_class_member',lambda:verify_family(accepted+[accepted[0]],words,ids,sig))
        badsig=sig.copy();badsig[4]-=1;reject('wrong_count_signature',lambda:verify_family(accepted,words,ids,badsig))
        bad=deepcopy(accepted);bad[0]['literal']['words'][0][0]=3;reject('invalid_word_value',lambda:verify_family(bad,words,ids,sig))
        reject('false_extremum_zero',lambda:need(min(values)==0,'actual min1'))
        reject('inequality_falsely_refuted',lambda:need(any(not lo<=v<=hi for v in values),'all loose bounds true'))
        evidence=dict(signature_index=0,signature=sig,cell_index=48,coordinates=[x,y],fibres=[f,g],word_universe=words,unordered_triples_examined=examined,count_matching_candidates=matched,complete_accepted_class=accepted,catalogue_indices=catalogue_ids,values=values,proposed_interval=[lo,hi],actual_interval=[min(values),max(values)],loose_bounds_hold=True)
        save(out/'counterexample.json',evidence);save(out/'controls.json',dict(subset_pair_cases=checked,capped_subset_cases=capchecked,unrestricted_extrema_cases=rangechecked,positive_local_cyclic=cyclic,rejected=rejected))
        ts=datetime.now(timezone.utc).isoformat();claim='C-FIXED-HADAMARD-LOCAL-GRAM-FRECHET-EXTREMA-FORMULA'
        binding=dict(id=claim,revision=1,kind='proposed formula',basis=['DERIVED','COMPUTED'],status='REFUTED',review_state='CLEAR',statement='For every one of the frozen 6,061 complete local count classes and every one of the 135 coordinate/fibre Gram cells, the exact minimum equals max(0,n+m-3) and the exact maximum equals min(n,m,1 if the fibres agree else2).',scope='Proposed equality for exact scalar extrema in the fixed local Gram/within-group-column-cap catalogue only.',refutation='Signature0 and cell48 have row counts2 and1. Every one of the two possible local triples has contribution1, so the exact interval[1,1] differs from the proposed[0,1].',dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='coverage')],verifier='/root/structural_attack',producer='/root',method='Independent enumeration of all90 balanced words/all117480 unordered triples and literal checking of every count-class member; no producer imports.',shared_components=['Pinned raw complete catalogue and proposed signature metadata; independent set-intersection implementation with Python integer arithmetic.'],inputs_sha256=pins,evidence_sha256={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT).as_posix()) for p in out.iterdir() if p.is_file()},limitations=['Does not refute the valid loose Frechet inequalities.','Does not certify the producer219600 total mismatches.','No factor, support, core, or target exclusion is asserted.'],artifact_availability='LOCAL_ONLY',availability_reason='Pending parent publication.',external_review=None,external_review_reason='No external review asserted.',created_at=ts,updated_at=ts)
        save(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_LOCAL_FRECHET_EQUALITY_REFUTATION_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT).as_posix()) for p in out.iterdir() if p.is_file()},claim_id=claim,claim_status='REFUTED',word_universe=90,complete_triple_population=examined,class_candidates=len(matched),class_members=len(accepted),actual_interval=[min(values),max(values)],proposed_interval=[lo,hi],loose_bounds_refuted=False,full_mismatch_count_verified=False,elapsed_seconds=time.monotonic()-started,new_solver_calls=0,target_resolution=False)
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha((out/'summary.json').relative_to(ROOT).as_posix()),binding_sha256=sha((out/'claim_binding.json').relative_to(ROOT).as_posix()))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
