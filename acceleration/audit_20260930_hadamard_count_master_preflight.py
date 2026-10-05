"""Independent count-master tables and proposed gadget review; no solver."""
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
import argparse, gzip, hashlib, json, platform, subprocess, sys, time, traceback

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
PRE=B+'hadamard_count_master_preflight/';RAW=B+'hadamard20_support/six_prism.json';LOCAL=B+'hadamard_triplicate_counts/local_triples.json'
CG=B+'independent_review/coordinate_marginal_domains/summary.json';CS=B+'hadamard_coordinate_marginal_domains/summary.json'
LG=B+'independent_review/hadamard_triplicate_counts_v2/summary.json'
PINS={PRE+'summary.json':'f290fc687ac1723354e9b4acf7429de087547f8a422bb4ee7770b2473d62e7bb',PRE+'inventory.json':'546a1c8ecc8a796700161ccdd064627561ea3a609955499cf7f3f07009a2ba80',CG:'9d08476ace166438321273b13161d759dbc858c782b16d8a2f0e9801d424cf39'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def signature(words,triple):
    counts=[Counter(column)for column in zip(*(words[t]for t in triple))]
    return tuple(counts[a][f]for a in range(6)for f in range(3))
def table_check(counts,groups,coordinate_domains,signature_index):
    need(len(counts)==12 and all(len(row)==20 for row in counts),'table dimensions')
    selected=[]
    for a,row in enumerate(counts):
        need(all(len(c)==3 and all(type(x)is int and 0<=x<=3 for x in c)for c in row),'strict bounded integer counts')
        value=tuple(tuple(c)for c in row);need(value in coordinate_domains[a],'whole coordinate-domain membership');selected.append(coordinate_domains[a][value])
    signatures=[]
    for g,support in enumerate(groups):
        sig=tuple(x for a in support for x in counts[a][g]);need(sig in signature_index,'whole local count signature membership');signatures.append(signature_index[sig])
    return dict(coordinate_choice_indices=selected,group_signature_indices=signatures,exceptional_groups=[g for g,support in enumerate(groups)if any(counts[a][g]!=[1,1,1]for a in support)])
def onehot(n):
    need(n>=1,'nonempty onehot domain');xs=list(range(1,n+1))
    if n==1:return 1,[xs]
    s=list(range(n+1,2*n));clauses=[xs,[-xs[0],s[0]]]
    for i in range(1,n-1):clauses.extend([[-xs[i],s[i]],[-s[i-1],s[i]],[-xs[i],-s[i-1]]])
    clauses.append([-xs[-1],-s[-1]]);return 2*n-1,clauses
def sat(clauses,values):return all(any(values[abs(x)-1]==(x>0)for x in clause)for clause in clauses)
def gadget_controls():
    results=[]
    for n in range(1,7):
        nv,clauses=onehot(n);accepted=set();trials=0
        for values in product([False,True],repeat=nv):
            trials+=1
            if sat(clauses,values):accepted.add(values[:n])
        expected={v for v in product([False,True],repeat=n)if sum(v)==1};need(accepted==expected,'onehot existential auxiliary equivalence')
        need(nv==2*n-1 and len(clauses)==(1 if n==1 else 3*n-3),'proposed size formula');results.append(dict(domain=n,variables=nv,clauses=len(clauses),full_assignments=trials,accepted_primary_assignments=len(accepted)))
    nv,c=onehot(3);zero=(False,)*nv;need(sat(c[1:],zero)and not sat(c,zero),'missing at-least-one corruption detected')
    double=(True,False,True,True,True);need(sat(c[:-1],double)and not sat(c,double),'missing final exclusion corruption detected')
    # X, Y and value-channel Q are separately exactly-one; all selector->value implications.
    base=[[1,2],[-1,-2],[3,4],[-3,-4],[5,6],[-5,-6]];links=[[-1,5],[-2,6],[-3,5],[-4,6]]
    accepted=[]
    for vals in product([False,True],repeat=6):
        if sat(base+links,vals):accepted.append([0 if vals[0]else 1,0 if vals[2]else 1,0 if vals[4]else 1])
    need(accepted==[[1,1,1],[0,0,0]],'exact channel agreement and both positives')
    inconsistent=(True,False,False,True,True,False);need(not sat(base+links,inconsistent)and sat(base+links[:-1],inconsistent),'removed group-channel implication detectable')
    return dict(exhaustive_onehot_cases=results,shared_channel_positive_assignments=accepted,deliberately_incomplete_encodings_detected=['missing_at_least_one','missing_final_at_most_one','missing_group_channel_implication'],scope='Independent proposed generic gadgets only; actual future CNF is not reviewed.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        if p not in pins:pins[p]=sha(ROOT/p)
        need(h is None or pins[p]==h,'hash '+p)
    try:
        for p,h in PINS.items():pin(p,h)
        producer=read(PRE+'summary.json');inventory=read(PRE+'inventory.json')
        for p,h in {**producer['inputs_sha256'],**producer['outputs_sha256']}.items():pin(p,h)
        gate=read(CG);need(gate['status']=='INDEPENDENT_COMPLETE_COORDINATE_MARGINAL_DOMAINS_PASS','separately independently approved coordinate domains')
        need(read(LG)['status']=='INDEPENDENT_HADAMARD_TRIPLICATE_PROJECTIONS_PASS'and read(LG)['inputs_sha256'][LOCAL]==pins[LOCAL],'independent complete local catalogue premise')
        save(out/'gadget_controls.json',gadget_controls())
        raw=read(RAW);groups=list(dict.fromkeys(tuple(a for a in range(12)if raw['L'][a][d])for d in range(60)));need(inventory['groups']==[list(g)for g in groups]and len(groups)==20,'raw support groups and order')
        local=read(LOCAL);words=local['words'];triples=local['survivors'];signatures=defaultdict(list)
        for ti,triple in enumerate(triples):
            sig=signature(words,triple);need(all(sum(sig[3*a:3*a+3])==3 for a in range(6))and all(sum(sig[3*a+f]for a in range(6))==6 for f in range(3)),'literal local signature quotas');signatures[sig].append(ti)
        ordered=sorted(signatures);signature_index={s:i for i,s in enumerate(ordered)};saved=read(PRE+'local_signatures.json');need(len(ordered)==6061 and len(triples)==31110 and saved==dict(signatures=[dict(index=i,counts=list(s),local_survivor_indices=signatures[s],count=len(signatures[s]))for i,s in enumerate(ordered)],local_triples=31110),'complete signature deduplication and all witnesses')
        coordinates=[];coordinate_domains=[];channels=[];projections={}
        for a,record in enumerate(read(CS)['records']):
            pin(record['path'],record['sha256']);need(gate['inputs_sha256'][record['path']]==record['sha256'],'coordinate file independently authenticated');c=read(record['path']);coordinates.append(c)
            need(c['coordinate']==a and c['incident_groups']==[g for g,s in enumerate(groups)if a in s],'literal incident support')
            domain={tuple(tuple(v)for v in r['full20_count_signature']):r['index']for r in c['ordered_three_fibre_choices']};need(len(domain)==c['choice_count'],'distinct complete coordinate count profiles');coordinate_domains.append(domain)
            for g in c['incident_groups']:
                values=sorted({v[g]for v in domain});projections[a,g]=set(values);channels.append(dict(coordinate=a,group=g,values=[list(v)for v in values]))
            # Direct scalar necessary equations for every saved count profile (completeness is the root audit premise).
            for v in domain:
                for g,s in enumerate(groups):need(sum(v[g])==(3 if a in s else 0),'coordinate count totals/absent supports')
                for f in range(3):
                    delta=[v[g][f]-int(a in groups[g])for g in range(20)]
                    need(sum(delta)==0 and all(sum(delta[g]for g,s in enumerate(groups)if b in s)==0 for b in range(12)),'literal global marginal equations')
        need(channels==inventory['channel_domains'],'all120 ordered channel alphabets')
        domains=[]
        for g,support in enumerate(groups):
            kept=[];removed=[]
            for si,sig in enumerate(ordered):
                absent=[a for j,a in enumerate(support)if tuple(sig[3*j:3*j+3])not in projections[a,g]]
                if not absent:kept.append(si)
                else:
                    a=absent[0];j=support.index(a);removed.append(dict(signature_index=si,first_bad_coordinate=a,count=list(sig[3*j:3*j+3])))
            domains.append(dict(group=g,support=list(support),signature_indices=kept,unary_removed=removed,count=len(kept)))
        need(domains==inventory['group_domains'],'every retained/removed group signature and first mismatch')
        need(inventory['coordinate_records']==read(CS)['records'],'entire upstream coordinate records')
        sizes=[len(d)for d in coordinate_domains]+[len(d['signature_indices'])for d in domains]+[len(c['values'])for c in channels]
        estimates=dict(unique_local_signatures=len(ordered),coordinate_choice_selectors=sum(map(len,coordinate_domains)),group_signature_selectors=sum(d['count']for d in domains),count_channel_variables=sum(len(c['values'])for c in channels),onehot_domains=len(sizes),prefix_auxiliaries=sum(n-1 for n in sizes),onehot_clauses=sum(1 if n==1 else 3*n-3 for n in sizes),implication_clauses=sum(len(d)*10 for d in coordinate_domains)+sum(d['count']*6 for d in domains))
        estimates['estimated_variables']=sum(sizes)+estimates['prefix_auxiliaries'];estimates['estimated_clauses']=estimates['onehot_clauses']+estimates['implication_clauses']
        need(all(inventory[k]==v for k,v in estimates.items())and inventory['exception_count_bound']is None,'all exact inventory quantities/no hidden exception bound')
        balanced=[[[1,1,1]if a in support else[0,0,0]for support in groups]for a in range(12)];positives=[dict(name='all_balanced_count_table',counts=balanced,selection=table_check(balanced,groups,coordinate_domains,signature_index),is_full_factor=False)]
        sourceprofile=B+'hadamard_six_profile_local_domains/profiles.jsonl.gz'
        with gzip.open(ROOT/sourceprofile,'rt',encoding='utf-8')as f:p=json.loads(next(f))
        need(p['id']=='rank4_00_profile_0000','authenticated six-exception calibration identity');counts=deepcopy(balanced)
        for a in range(12):
            for side,g in enumerate(p['group_ids']):counts[a][g]=[counts[a][g][f]+p['coordinate_fibre_deviations'][a][f][side]for f in range(3)]
        positives.append(dict(name=p['id'],counts=counts,selection=table_check(counts,groups,coordinate_domains,signature_index),is_full_factor=False))
        for p in positives:
            for g,si in enumerate(p['selection']['group_signature_indices']):need(si in domains[g]['signature_indices'],'positive survives exact unary filter')
        rejected=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,KeyError,IndexError):rejected.append(name);return
            raise ValueError('corruption accepted '+name)
        for name in ['noninteger','bound','marginal','absent_support','shape']:
            bad=deepcopy(balanced);a=groups[0][0]
            if name=='noninteger':bad[a][0][0]=True
            elif name=='bound':bad[a][0]=[4,-1,0]
            elif name=='marginal':bad[a][0]=[0,1,2]
            elif name=='absent_support':bad[next(i for i in range(12)if i not in groups[0])][0]=[1,1,1]
            else:bad.pop()
            reject(name,lambda:table_check(bad,groups,coordinate_domains,signature_index))
        broken=deepcopy(signature_index);del broken[(1,)*18];reject('missing_balanced_local_signature',lambda:table_check(balanced,groups,coordinate_domains,broken))
        broken=deepcopy(coordinate_domains);del broken[0][tuple(tuple(x)for x in balanced[0])];reject('missing_coordinate_choice',lambda:table_check(balanced,groups,broken,signature_index))
        save(out/'positive_count_tables.json',dict(records=positives,scope='Two exact joint-count-table witnesses, not full-Gram factors. The first already proves the proposed no-exception-bound master satisfiable at the table level.'))
        save(out/'controls.json',dict(rejected_corruptions=rejected,positive_count_tables=2,full_factor_positive=False,gadget_controls='gadget_controls.json'))
        save(out/'independent_inventory.json',dict(**estimates,group_domain_sizes=[d['count']for d in domains],signature_multiplicity_histogram=dict(Counter(len(x)for x in signatures.values())),unary_retained_signature_uses=sum(d['count']for d in domains),unary_removed_signature_uses=20*len(ordered)-sum(d['count']for d in domains),full_Gram_constraints_encoded=False,cross_group_caps_encoded=False,residual_D_encoded=False,actual_CNF_built_or_audited=False))
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_HADAMARD_COUNT_MASTER_PREFLIGHT.md','uv.lock','pyproject.toml']:pin(p)
        ts=datetime.now(timezone.utc).isoformat();result=dict(status='INDEPENDENT_COUNT_MASTER_PREFLIGHT_REVIEW_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()},checked_scope='Complete prospective domains/counts, unary filter and proposed generic one-hot/channel semantics. No actual CNF or executable gate approved.',independent_of_producer=True,shared_inputs_and_premises=['Previously produced coordinate domains reused only through root independent complete4^10 audit.','Previously independently checked complete31110 local-triple catalogue.','Raw support, standard-library exact arithmetic; no producer imports.'],actual_CNF_approved=False,known_table_witness='all_balanced_count_table',new_obstruction=None,new_obstruction_null_reason='The unbounded relaxation has an explicit balanced count-table witness; it is not a full factor.',**estimates,rejected_corruptions=len(rejected),solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start);save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),elapsed_seconds=result['elapsed_seconds'])))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
