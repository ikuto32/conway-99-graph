"""Independent semantic/census controls. No research encoders/checkers imported."""
from pathlib import Path
from itertools import combinations,product
from collections import Counter,defaultdict
from datetime import datetime,timezone
from copy import deepcopy
import argparse,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
RAW=B+'hadamard20_support/six_prism.json';MASTER=B+'hadamard_count_master_cnf/model.json';LOCAL=B+'hadamard_triplicate_counts/local_triples.json';D=B+'direct_cell_count_cnf/'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',MASTER:'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',I+'hadamard_count_master_cnf_v2/summary.json':'80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888',I+'coordinate_marginal_domains/summary.json':'9d08476ace166438321273b13161d759dbc858c782b16d8a2f0e9801d424cf39',I+'hadamard_six_profile_union/summary.json':'6a7b34f7feaf7d9330ce07f4c615f4198e8cdc0c8ac22dd7fb5e673ba59311df',B+'srg243_residual_fixture/triangle_blocks.json':'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439'}
def need(b,s):
    if not b:raise ValueError(s)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,x):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def factor_gram(F,C,n):
    need(len(F)==3*n and all(len(row)==len(F[0]) and all(type(v)is int and v in(0,1) for v in row) for row in F),'strict raw factor')
    expected=[[n*(i==j)-C[i][j]-sum(C[i][k]*C[k][j] for k in range(3*n))+2-int(i//n==j//n) for j in range(3*n)] for i in range(3*n)]
    actual=[[sum(a*b for a,b in zip(F[i],F[j])) for j in range(3*n)] for i in range(3*n)]
    need(actual==expected,'literal integer Gram');return actual
def sat(cs,b):return all(any(b[abs(v)]==(v>0) for v in c) for c in cs)
def flag():return [[-1,-4,7],[-2,-5,7],[-3,-6,7],[-1,4,-7],[-2,5,-7],[-3,6,-7]]
def countlink(k):return [[-1,*[-2-i if bit else 2+i for i,bit in enumerate(bits)]] for bits in product((False,True),repeat=3) if sum(bits)!=k]
def control_suite(fixture):
    rejected=[];eq=conditional=0;counterexample=None
    def reject(name,fn):
        try:fn()
        except (ValueError,IndexError,TypeError):rejected.append(name)
        else:raise ValueError('accepted corruption '+name)
    for bits in product((False,True),repeat=7):
        result=sat(flag(),dict(enumerate(bits,1)));intended=bits[6]==(bits[:3]==bits[3:6])
        if sum(bits[:3])==sum(bits[3:6])==1:need(result==intended,'all equality flags under onehot');eq+=1
        elif result!=intended and counterexample is None:counterexample=dict(bits=list(bits),clauses_satisfied=result,unconditional_equality=intended)
    need(counterexample is not None,'onehot premise cannot be dropped')
    for k in range(4):
        for bits in product((False,True),repeat=4):
            need(sat(countlink(k),dict(enumerate(bits,1)))==((not bits[0]) or sum(bits[1:])==k),'conditional count exact truth');conditional+=1
    # Literal threshold recurrence evaluated as a truth relation, including folded constants.
    threshold=0
    for q,r in product((False,True),repeat=2):
        for x,z in product((False,True),repeat=2):need((z==(q or(x and r)))==((not z or q or x)and(not z or q or r)and(z or not q)and(z or not x or not r)),'both-direction recurrence');threshold+=1
    F,C=fixture['factor60x180'],fixture['cubic_core60'];factor_gram(F,C,20)
    for name in ['bit','shape','bool','nonbinary']:
        f=deepcopy(F)
        if name=='bit':f[0][0]^=1
        elif name=='shape':f.pop()
        elif name=='bool':f[0][0]=bool(f[0][0])
        else:f[0][0]=2
        reject('genuine243_'+name,lambda f=f:factor_gram(f,C,20))
    return dict(equality_truth_cases=eq,conditional_count_truth_cases=conditional,threshold_truth_cases=threshold,missing_onehot_counterexample=counterexample,genuine243_positive=True,corruptions_rejected=rejected)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def load(p,h=None):
        got=sha(ROOT/p);need(h is None or got==h,'input pin '+p);pins[p]=got;return json.loads((ROOT/p).read_bytes())
    try:
        for p,h in PINS.items():load(p,h)
        raw=load(RAW);master=load(MASTER);local=load(LOCAL);prod=load(D+'summary.json')
        for p,h in prod['inputs_sha256'].items():need(sha(ROOT/p)==h,'frozen producer input '+p);pins[p]=h
        for p,h in prod['outputs_sha256'].items():need(sha(ROOT/p)==h,'frozen producer artifact '+p);pins[p]=h
        ctrl=control_suite(load(B+'srg243_residual_fixture/triangle_blocks.json'));write(out/'controls.json',ctrl)
        C=[[int((i%12==j%12 and i//12!=j//12)or(i//12==j//12 and (i%12)^1==j%12)) for j in range(36)] for i in range(36)]
        G=[[12*(i==j)-C[i][j]-sum(C[i][k]*C[k][j] for k in range(36))+2-int(i//12==j//12) for j in range(36)] for i in range(36)]
        need(C==raw['core_adjacency'] and G==raw['prescribed_Gram36'],'literal derived core Gram')
        L=raw['L'];cols=[[a for a in range(12) if L[a][d]] for d in range(60)];groups=[list(x) for x in dict.fromkeys(map(tuple,cols))];gc=[[d for d in range(60) if cols[d]==s] for s in groups]
        need(cols==raw['support_columns'] and groups==master['groups'] and len(groups)==20 and all(len(x)==3 for x in gc),'exact labelled groups')
        need(all(len(s)==6 and all(len(set(s)&{a,a+1})==1 for a in range(0,12,2)) for s in cols),'one coordinate per prism')
        zero=[];positive=[]
        for i,j in combinations(range(36),2):
            a,b=i%12,j%12
            if a==b or (a^1)==b:need(G[i][j]==0,'structural zero');zero.append([i,j])
            else:need(G[i][j]==(1 if i//12==j//12 else 2),'Gram nonzero');positive.append([i,j])
        need(len(zero)==90 and len(positive)==540 and all(G[i][i]==10 for i in range(36)),'complete Gram decomposition')
        words=[w for w in product(range(3),repeat=6) if all(w.count(f)==2 for f in range(3))];need([list(w) for w in words]==local['words'],'complete90 balanced words')
        pair_ok={(i,j):sum(a==b for a,b in zip(words[i],words[j]))<=2 for i,j in combinations(range(90),2)}
        survivors=[];signatures=defaultdict(list);tested=0
        for ids in combinations(range(90),3):
            tested+=1
            if not all(pair_ok[i,j] for i,j in combinations(ids,2)):continue
            ws=[words[i] for i in ids]
            if any(any(n>(1 if f==h else 2) for (f,h),n in Counter((w[a],w[b]) for w in ws).items()) for a,b in combinations(range(6),2)):continue
            counts=tuple(sum(w[a]==f for w in ws) for a in range(6) for f in range(3));signatures[counts].append(len(survivors));survivors.append(list(ids))
        need(tested==117480 and survivors==local['survivors'] and len(survivors)==31110,'complete independent local-triple census')
        expected=[dict(index=i,counts=list(s),local_survivor_indices=signatures[s],count=len(signatures[s])) for i,s in enumerate(sorted(signatures))]
        need(expected==master['local_signatures'] and len(expected)==6061,'every signature and witness class')
        channels={};tables=0
        for cd in master['coordinate_domains']:
            a=cd['coordinate'];incident=[g for g,s in enumerate(groups) if a in s];need(cd['incident_groups']==incident,'coordinate incidence')
            for t in cd['count_tables']:
                need(len(t)==20 and all(len(row)==3 and all(type(v)is int and 0<=v<=3 for v in row) for row in t),'bounded integer table')
                need(all(sum(t[g])==(3 if g in incident else 0) for g in range(20)) and all(sum(t[g][f] for g in incident)==10 for f in range(3)),'marginal row and local sums')
                need(all(sum(t[g][f] for g in incident if b in groups[g])==5 for b in range(12) if b not in (a,a^1) for f in range(3)),'all full-Gram marginal equations');tables+=1
            for g in incident:channels[a,g]=sorted({tuple(t[g]) for t in cd['count_tables']})
        need(tables==2226,'all saved coordinate tables')
        for ch in master['count_channels']:need([list(v) for v in channels[ch['coordinate'],ch['group']]]==ch['values'],'every exact channel projection')
        retained=0
        for gd in master['group_domains']:
            g=gd['group'];s=groups[g]
            allowed=[i for i,sig in enumerate(expected) if all(tuple(sig['counts'][3*k:3*k+3]) in channels[a,g] for k,a in enumerate(s))]
            need(allowed==gd['signature_indices'],'complete unfiltered-then-unary-projected group signatures');retained+=len(allowed)
        need(retained==74798 and sum(len(x) for x in channels.values())==927,'all retained master choices')
        models=[]
        for variant in ['standalone','at_least_seven']:
            m=load(D+variant+'/model.json');s=load(D+variant+'/scope.json');r=m['recipe']
            need(s['L12x60']==L and s['core_adjacency36']==C and s['prescribed_Gram36']==G and s['column_normalization'] is None and s['target_automorphism_assumed'] is False and s['residual_D_encoded'] is False,'exact scope and no normalization')
            need(r['groups']==groups and r['group_columns']==gc and len(r['cell_variables'])==1080 and len(r['Gram_products'])==8100 and len(r['Gram_rows'])==540,'full finite recipe populations')
            seen=set()
            for cap in r['column_caps']:
                d,e=cap['columns'];need((d,e) not in seen and d<e,'unique cap pair');seen.add((d,e));common=sorted(set(cols[d])&set(cols[e]));need(cap['common_coordinates']==common and cap['automatic']==(len(common)<=2) and len(cap['equality_flags'])==(len(common) if len(common)>2 else 0),'literal cap recipe')
            need(seen==set(combinations(range(60),2)),'complete1770 caps')
            if variant=='at_least_seven':
                expectedlinks=[dict(group=c['group'],coordinate=c['coordinate'],fibre=f,selector=v,value=k,inputs=[next(x for g,d2,a,h,x in r['cell_variables'] if d2==d and a==c['coordinate'] and h==f) for d in gc[c['group']]]) for c in master['count_channels'] for values,v in zip(c['values'],c['variables']) for f,k in enumerate(values)]
                need(expectedlinks==r['count_links'] and s['minimum_exception_count']==7,'every literal master-cell coupling')
            else:need(len(r['standalone_row_counters'])==36 and s['minimum_exception_count'] is None,'explicit standalone row counts')
            models.append(dict(variant=variant,variables=m['variables'],clauses=m['clauses'],all_caps=True,count_links=len(r['count_links']),complete_clause_reconstruction=False))
        # All possible local balanced columns obey every mixed cap, independently of the global Gram.
        mixedchecks=0
        for support in cols:
            for w in words:
                selected={12*f+a for a,f in zip(support,w)}
                for i in range(36):need(int(i in selected)+sum(C[i][j] for j in selected)<=1,'automatic mixed cap');mixedchecks+=1
        write(out/'finite_checks.json',dict(local_triples_tested=tested,local_survivors=len(survivors),count_classes=len(expected),coordinate_tables=tables,retained_group_choices=retained,count_channel_values=sum(len(x) for x in channels.values()),Gram_diagonals=36,Gram_positive_upper=positive,Gram_zero_upper=zero,column_pair_intersection_histogram=dict(Counter(len(set(cols[d])&set(cols[e])) for d,e in combinations(range(60),2))),mixed_cap_local_checks=mixedchecks,formulas=models))
        for p in ['acceleration/audit_20260930_direct_cell_count_cnf.py','docs/DESIGN_20260930_DIRECT_CELL_COUNT_GRAM.md','docs/AUDIT_20260930_DIRECT_CELL_SEMANTICS.md',Path(__file__).relative_to(ROOT).as_posix(),'uv.lock','pyproject.toml']:pins[p]=sha(ROOT/p)
        need(time.perf_counter()-start<120,'bounded120second review')
        write(out/'summary.json',dict(status='INDEPENDENT_DIRECT_CELL_SEMANTICS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()},verifier='/root/eight_domain_audit',statement='The specified standalone semantic constraints project exactly onto binary36x60 factors with the literal L, prescribed Gram and all outside-column caps. Count-master coupling projects onto the same raw factors with its explicitly additional >=7 exception bound, relying on authenticated complete coordinate/master coverage. Labelled columns remain unrestricted. Mixed caps are automatic in this fixed six-prism geometry.',scope='One literal core/support. Mathematical reduction and finite recipe/control review only; complete CNF byte/gate/object checking remains separate.',trusted_components=['Previously independently verified complete coordinate census and count-master encoding/coverage; fixed-support at-most-six exclusion as explicit >=7 necessity premise.','Raw producer artifacts used as data only; no producer or root-checker imports. Root checker source reviewed but not executed or modified.'],controls=ctrl,limitations=['No full factor known in this research scope.','Genuine243 positive is a distinct graph/parameter fixture.','No residual D or99vertex target encoded.','No assumption that arbitrary target admits this L or has an automorphism.','Standalone and>=7 are separately scoped; extra bound is not silently derived from within caps alone.','No full formula reconstruction or native calls in this gate.'],target_resolution='UNKNOWN',native_calls=0,elapsed_seconds=time.perf_counter()-start))
        print(json.dumps(dict(status='INDEPENDENT_DIRECT_CELL_SEMANTICS_PASS',summary_sha256=sha(out/'summary.json'))))
    except BaseException as e:write(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
