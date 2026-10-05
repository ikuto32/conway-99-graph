"""New bounded exact screen of one independently checked count witness; candidate."""
from pathlib import Path
from itertools import combinations,product
from datetime import datetime,timezone
import argparse,copy,gzip,hashlib,json,platform,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
W=B+'hadamard_count_master_native_pilot_v2/independent_object/independent_count_profile.json'
WG=B+'independent_review/count_master_sat_outcome/summary.json'
IG=B+'independent_review/count_gram_intervals/summary.json'
TABLE=B+'hadamard_count_gram_intervals/signature_intervals.json.gz'
RAW=B+'hadamard20_support/six_prism.json';LOCAL=B+'hadamard_triplicate_counts/local_triples.json';SIG=B+'hadamard_count_master_preflight/local_signatures.json'
PINS={W:'0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152',WG:'61e7eb9643902c866617a270d856a521f71f5b2723c0e731edae3896baba484d',TABLE:'41c4269eb86477069e63900e14296e88734d668a160907f5ce1f0277d2cd230a'}
def need(x,m):
    if not x:raise ValueError(m)
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):pins[p]=sha(ROOT/p);need(h is None or h==pins[p],'hash '+p)
    try:
        for p,h in PINS.items():pin(p,h)
        pin(IG);gate=read(IG);need(gate['status']=='INDEPENDENT_COUNT_SIGNATURE_GRAM_INTERVALS_PASS'and gate['inputs_sha256'][TABLE]==pins[TABLE],'separate root interval audit')
        for p in [RAW,LOCAL,SIG]:pin(p,gate['inputs_sha256'][p])
        for p in [Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix(),'uv.lock','pyproject.toml']:pin(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,limits=dict(seconds=30,profiles=1,global_cells=540,solver_calls=0),scope='One exact native count-CSP witness; independently reviewed interval table is a premise, new exclusion awaits another reviewer.'))
        w=read(W);raw=read(RAW);local=read(LOCAL);signatures=read(SIG)['signatures'];groups=list(dict.fromkeys(tuple(a for a in range(12)if raw['L'][a][d])for d in range(60)))
        with gzip.open(ROOT/TABLE,'rt',encoding='utf-8')as f:table=json.load(f)
        cells=[(a,b,f,h)for a,b in combinations(range(6),2)for f in range(3)for h in range(3)];need(table['local_cells']==list(map(list,cells)),'local coefficient order');index={c:i for i,c in enumerate(cells)};si={tuple(s['counts']):s['index']for s in signatures};bounds=table['records']
        C=raw['core_adjacency'];G=[[12*int(i==j)-C[i][j]+2-sum(C[i][k]*C[k][j]for k in range(36))-int(i//12==j//12)for j in range(36)]for i in range(36)];need(G==raw['prescribed_Gram36'],'raw core-derived exact target')
        counts=w['coordinate_group_fibre_counts'];chosen=[si[tuple(x for a in s for x in counts[a][g])]for g,s in enumerate(groups)];need(chosen==w['selected_global_signature_indices'],'raw selected signature table')
        # Fresh literal local colour comparisons, distinct from producer bit intersections.
        checked=[]
        for sid in sorted(set(chosen+[si[(1,)*18]])):
            s=signatures[sid];vals=[]
            for ti in s['local_survivor_indices']:
                triple=local['survivors'][ti];words=[local['words'][t]for t in triple]
                need([sum(word[a]==f for word in words)for a in range(6)for f in range(3)]==s['counts'],'complete selected local signature')
                vals.append([sum(word[a]==f and word[b]==h for word in words)for a,b,f,h in cells])
            low=[min(v[i]for v in vals)for i in range(135)];high=[max(v[i]for v in vals)for i in range(135)];need(low==bounds[sid]['minimum']and high==bounds[sid]['maximum'],'literal whole selected-domain extrema')
            checked.append(dict(signature_index=sid,local_triples=s['local_survivor_indices'],minimum=low,maximum=high))
        def screen(counts):
            selected=[si[tuple(x for a in s for x in counts[a][g])]for g,s in enumerate(groups)];rows=[]
            for a,b in combinations(range(12),2):
                if a//2==b//2:continue
                for f,h in product(range(3),repeat=2):
                    terms=[]
                    for g,s in enumerate(groups):
                        if a not in s or b not in s:continue
                        j=index[s.index(a),s.index(b),f,h];v=bounds[selected[g]]
                        terms.append(dict(group=g,signature_index=selected[g],local_cell=j,minimum=v['minimum'][j],maximum=v['maximum'][j],minimum_witness=v['minimum_witnesses'][j],maximum_witness=v['maximum_witnesses'][j]))
                    need(len(terms)==5,'five exact contributions');lo=sum(t['minimum']for t in terms);hi=sum(t['maximum']for t in terms);target=G[12*f+a][12*h+b];rows.append(dict(coordinates=[a,b],fibres=[f,h],target=target,lower=lo,upper=hi,passes=lo<=target<=hi,terms=terms))
            need(len(rows)==540,'complete540population');return rows
        balanced=[[[1,1,1]if a in s else[0,0,0]for s in groups]for a in range(12)];positive=screen(balanced);need(all(r['passes']for r in positive),'balanced count relaxation positive')
        rejected=[]
        for name,bad in [('bounds',dict(minimum=[4]*135,maximum=[-1]*135)),('endpoint',dict(minimum=checked[0]['minimum'][:],maximum=checked[0]['maximum'][:]))]:
            if name=='endpoint':bad['minimum'][0]+=1
            try:need(bad['minimum']==checked[0]['minimum']and bad['maximum']==checked[0]['maximum'],'corrupt interval')
            except ValueError:rejected.append(name)
            else:raise ValueError('accepted corrupt interval')
        # Product-domain positive and target violations are exact and independent of research feasibility.
        tiny=[[(0,1),(1,0)],[(1,1),(2,0)]];sums=[tuple(sum(v[j]for v in c)for j in range(2))for c in product(*tiny)]
        lo=[sum(min(v[j]for v in d)for d in tiny)for j in range(2)];hi=[sum(max(v[j]for v in d)for d in tiny)for j in range(2)];need(all(all(lo[j]<=v[j]<=hi[j]for j in range(2))for v in sums),'exact product positive');need(not all(lo[j]<=0<=hi[j]for j in range(2)),'lower-target falsification')
        rows=screen(counts);violations=[r for r in rows if not r['passes']];save(out/'all540_intervals.json',dict(profile_sha256=w['profile_sha256'],selected_signatures=chosen,records=rows));save(out/'selected_local_extrema.json',dict(records=checked));save(out/'controls.json',dict(balanced_count_intervals=540,balanced_passed=True,full_factor_positive=False,exact_product_domain_choices=len(sums),rejected_corruptions=rejected));save(out/'certificate.json',dict(profile_sha256=w['profile_sha256'],count_profile_path=W,count_profile_sha256=pins[W],exceptional_groups=w['exceptional_groups'],failed_cells=violations,statement='Any lift of these exact counts using the complete local catalogue contributes to each Gram entry between the displayed summed minima and maxima. Any failed cell contradicts its exact required integer Gram entry.',status='CANDIDATE_PROFILE_EXCLUSION'if violations else'CANDIDATE_INTERVAL_SURVIVOR',full_factor=False,target_resolution=False))
        result=dict(status='CANDIDATE_EIGHT_EXCEPTION_COUNT_INTERVAL_SCREEN_COMPLETE',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()},profile_sha256=w['profile_sha256'],exception_count=w['exception_count'],global_cells=540,failed_cells=len(violations),selected_local_signature_classes=len(checked),first_failure=violations[0]if violations else None,first_failure_null_reason=None if violations else'Every necessary interval contains its target; this is not a full-Gram lift.',independent_approval=False,shared_trust='Original interval producer authored in this lane, independently approved by root; here no producer imports and all selected local extrema are freshly recomputed by literal color comparisons. New count-profile exclusion requires separate review.',solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start);save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],failed_cells=len(violations),first_failure=result['first_failure'],summary_sha256=sha(out/'summary.json'),certificate_sha256=sha(out/'certificate.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
