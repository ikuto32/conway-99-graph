"""Independent complete count-CSP encoding audit. No producer imports or solver."""
from pathlib import Path
from itertools import product
from collections import defaultdict,Counter
from datetime import datetime,timezone
import argparse,copy,gzip,hashlib,json,platform,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1]; B='acceleration/results/20260930_'
D=B+'hadamard_count_master_cnf/'; PRE=B+'hadamard_count_master_preflight/'
PG=B+'independent_review/hadamard_count_master_preflight/summary.json'
UG=B+'independent_review/hadamard_six_profile_union/summary.json'
RAW=B+'hadamard20_support/six_prism.json'; LOCAL=B+'hadamard_triplicate_counts/local_triples.json'
PINS={D+'summary.json':'2137fe0c32043a82166a484085d366309e4037d24aa558dabca20a44e73bff04',D+'model.json':'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',D+'baseline.cnf':'609a606c2b228e3956e43ab7d2589dcbcdca797f5978ffa51c8029aa042b7ba7',D+'at_least_seven.cnf':'f303edec9a91dc9bcecb95804ee151d0e38e8100b17c9c45a7b4d58b8edbf55e',D+'scope.json':'719fb6e1d7b98656f23b31a83343fb9dfa952ea9a0c14fef3d564faf896f0959',PG:'5b23e5a188522c669128ec9f79ec8fb975d75e251c15be4ebc0857b96d4876b3',UG:'6a7b34f7feaf7d9330ce07f4c615f4198e8cdc0c8ac22dd7fb5e673ba59311df'}
def need(x,m):
    if not x:raise ValueError(m)
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def signed_values(xs,n):
    need(type(xs)is list and len(xs)==n,'complete assignment length');v=[None]*(n+1)
    for x in xs:
        need(type(x)is int and 1<=abs(x)<=n and v[abs(x)]is None,'strict unique signed assignment');v[abs(x)]=x>0
    return v
def clause_pass(c,v):return any(v[abs(x)]==(x>0)for x in c)
def check_assignment(clauses,v):
    for i,c in enumerate(clauses,1):need(clause_pass(c,v),f'false actual clause {i}')
def onehot(xs,ps):
    yield xs
    if ps:
        yield [-xs[0],ps[0]]
        for i in range(1,len(xs)-1):
            yield [-xs[i],ps[i]];yield [-ps[i-1],ps[i]];yield [-xs[i],-ps[i-1]]
        yield [-xs[-1],-ps[-1]]
def gate_clauses(z,q,x,r):
    # Enumerate all falsifying valuations of the exact Boolean relation.
    names=sorted({a for a in(q,x,r,z)if type(a)is int});answer=[]
    for bits in product(range(2),repeat=len(names)):
        assignment=dict(zip(names,bits));ev=lambda t:int(t)if type(t)is bool else assignment[t]
        if assignment[z]!=int(ev(q)+ev(x)*ev(r)>0):answer.append([(-a if assignment[a]else a)for a in names])
    return answer
def exact_stream(path,n,clauses):
    with Path(path).open('rb')as f:
        need(f.readline()==f'p cnf {n} {len(clauses)}\n'.encode(),'exact DIMACS header')
        for i,c in enumerate(clauses,1):need(f.readline()==(' '.join(map(str,c))+' 0\n').encode(),f'exact clause bytes {i}')
        need(f.read()==b'','no trailing/unaccounted clauses')
def build_expected(inventory,coordinates,signatures):
    last=0;cd=[];gd=[];ch=[]
    def alloc(n):
        nonlocal last
        xs=list(range(last+1,last+n+1));last+=n;return xs
    for a,c in enumerate(coordinates):cd.append(dict(coordinate=a,selectors=alloc(len(c['ordered_three_fibre_choices'])),incident_groups=c['incident_groups'],count_tables=[x['full20_count_signature']for x in c['ordered_three_fibre_choices']]))
    for g in inventory['group_domains']:gd.append(dict(group=g['group'],support=g['support'],signature_indices=g['signature_indices'],selectors=alloc(len(g['signature_indices']))))
    for c in inventory['channel_domains']:ch.append(dict(coordinate=c['coordinate'],group=c['group'],values=c['values'],variables=alloc(len(c['values']))))
    primary=last;clauses=[];domains=[]
    for kind,ds,field in [('coordinate',cd,'selectors'),('group',gd,'selectors'),('channel',ch,'variables')]:
        for d in ds:
            xs=d[field];ps=alloc(len(xs)-1);start=len(clauses)+1;clauses.extend(onehot(xs,ps));identity=[d['coordinate'],d['group']]if kind=='channel'else d[kind]
            domains.append(dict(kind=kind,identity=identity,selectors=xs,prefix_variables=ps,first_clause=start,clause_count=len(clauses)-start+1))
    oh=len(clauses);lookup={(c['coordinate'],c['group'],tuple(v)):x for c in ch for v,x in zip(c['values'],c['variables'])}
    for c in cd:
        for x,t in zip(c['selectors'],c['count_tables']):
            for g in c['incident_groups']:clauses.append([-x,lookup[c['coordinate'],g,tuple(t[g])]])
    ci=len(clauses)
    for d in gd:
        for x,si in zip(d['selectors'],d['signature_indices']):
            for j,a in enumerate(d['support']):clauses.append([-x,lookup[a,d['group'],tuple(signatures[si]['counts'][3*j:3*j+3])]])
    n=last;basecount=len(clauses);balanced=[]
    for d in gd:
        ids=[x for x,si in zip(d['selectors'],d['signature_indices'])if signatures[si]['counts']==[1]*18];need(len(ids)==1,'unique balanced selector');balanced+=ids
    states={};records=[];suffix=[]
    for i in range(1,21):
        for j in range(1,min(i,14)+1):
            z=alloc(1)[0];q=states.get((i-1,j),False);r=True if j==1 else states.get((i-1,j-1),False);x=balanced[i-1];cs=gate_clauses(z,q,x,r)
            records.append(dict(i=i,j=j,id=z,q=q,x=x,r=r,first_clause=basecount+len(suffix)+1,clause_count=len(cs)));suffix.extend(cs);states[i,j]=z
    suffix.append([-states[20,14]])
    extension=dict(input_variables=balanced,at_most=13,states=records,final_threshold=states[20,14],first_clause=basecount+1,clause_count=len(suffix),new_variables=last-n)
    return dict(coordinate_domains=cd,group_domains=gd,count_channels=ch,one_hot_domains=domains,primary_variables=primary,clause_sections=dict(onehots=[1,oh],coordinate_implications=[oh+1,ci],group_implications=[ci+1,basecount]),extension=extension),clauses,suffix,n,last
def literal_decode(model,values,variant):
    coordinates=[];cs=[];gs=[];signatures=[];witnesses=[]
    for d in model['coordinate_domains']:
        selected=[i for i,x in enumerate(d['selectors'])if values[x]];need(len(selected)==1,'one coordinate selector');i=selected[0];coordinates.append(d['count_tables'][i]);cs.append(d['selectors'][i])
    need(len(coordinates)==12,'12 coordinates')
    for a,t in enumerate(coordinates):
        need(len(t)==20,'20 groups per coordinate')
        for g,v in enumerate(t):need(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v)and sum(v)==3*int(a in model['groups'][g]),'strict local/absent coordinate counts')
        for f in range(3):
            ds=[t[g][f]-int(a in model['groups'][g])for g in range(20)]
            need(sum(ds)==0 and all(sum(ds[g]for g,s in enumerate(model['groups'])if b in s)==0 for b in range(12)),'literal complete marginal equations')
    for d in model['group_domains']:
        picked=[i for i,x in enumerate(d['selectors'])if values[x]];need(len(picked)==1,'one group selector');i=picked[0];sid=d['signature_indices'][i];s=model['local_signatures'][sid];raw=[x for a in d['support']for x in coordinates[a][d['group']]]
        need(raw==s['counts']and all(sum(raw[3*j+f]for j in range(6))==6 for f in range(3)),'raw group incidence agreement and fibre quota');gs.append(d['selectors'][i]);signatures.append(sid);witnesses.append(s['local_survivor_indices'])
    for d in model['count_channels']:
        chosen=[i for i,x in enumerate(d['variables'])if values[x]];need(len(chosen)==1 and d['values'][chosen[0]]==coordinates[d['coordinate']][d['group']],'literal channel count agreement')
    exc=[g for g,s in enumerate(model['groups'])if any(coordinates[a][g]!=[1,1,1]for a in s)];need(variant=='baseline'or len(exc)>=7,'at least seven exceptional groups')
    dev=[[[coordinates[a][g][f]-int(a in model['groups'][g])for g in exc]for f in range(3)]for a in range(12)];profile=dict(groups=exc,deviations=dev)
    return dict(variant=variant,selected_coordinate_selector_ids=cs,selected_group_selector_ids=gs,selected_global_signature_indices=signatures,coordinate_group_fibre_counts=coordinates,exceptional_groups=exc,exception_count=len(exc),coordinate_fibre_deviations=dev,profile_sha256=hashlib.sha256(json.dumps(profile,sort_keys=True,separators=(',',':')).encode()).hexdigest(),local_survivor_indices_by_group=witnesses,full_factor=False,target_graph=False,residual_D=None,all_cross_group_column_caps_checked=False)
def controls(out,model,base,suffix,n,nn):
    rejected=[]
    def reject(name,fn):
        try:fn()
        except(ValueError,KeyError,IndexError):rejected.append(name);return
        raise ValueError('corruption accepted '+name)
    tiny=0
    for k in range(1,7):
        xs=list(range(1,k+1));ps=list(range(k+1,2*k));c=list(onehot(xs,ps));counts=Counter()
        for bits in product((False,True),repeat=2*k-1):
            v=[None,*bits]
            if all(clause_pass(r,v)for r in c):counts[bits[:k]]+=1
            tiny+=1
        need(counts==Counter({bits:1 for bits in product((False,True),repeat=k)if sum(bits)==1}),'unique existential sequential prefix control')
    gates=0
    for state in model['extension']['states']:
        names=sorted({v for v in(state['id'],state['q'],state['x'],state['r'])if type(v)is int});c=gate_clauses(state['id'],state['q'],state['x'],state['r'])
        for bits in product((False,True),repeat=len(names)):
            v=dict(zip(names,bits));ev=lambda t:t if type(t)is bool else v[t];expected=v[state['id']]==(ev(state['q'])or(ev(state['x'])and ev(state['r'])))
            need(all(any(v[abs(x)]==(x>0)for x in row)for row in c)==expected,'actual threshold local truth');gates+=1
    records=[]
    for p in sorted((ROOT/D).glob('*_assignment.json')):
        v=signed_values(json.loads(p.read_bytes())['assignment'],n);check_assignment(base,v);decoded=literal_decode(model,v,'baseline');records.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),exception_count=decoded['exception_count'],actual_baseline_clauses=len(base)))
        aug=v+[False]*(nn-n)
        for s in model['extension']['states']:aug[s['id']]=sum(aug[x]for x in model['extension']['input_variables'][:s['i']])>=s['j']
        check_assignment(suffix[:-1],aug);reject('baseline_'+p.stem+'_at_least_seven',lambda:check_assignment(suffix,aug))
        for kind,x in [('selector',model['coordinate_domains'][0]['selectors'][0]),('prefix',model['one_hot_domains'][0]['prefix_variables'][0]),('channel',model['count_channels'][0]['variables'][0])]:
            bad=v.copy();bad[x]=not bad[x];reject(p.stem+'_'+kind,lambda:check_assignment(base,bad))
        changed=[*base];changed[0]=[-next(x for x in base[0]if v[x])];reject(p.stem+'_actual_clause_corruption',lambda:check_assignment(changed,v))
    need(len(records)==2 and sorted(r['exception_count']for r in records)==[0,6],'two authentic count-only controls')
    # Exercise exact byte-stream checker with deliberate header, clause, order and suffix changes.
    sample=out/'stream_positive.cnf';sample.write_bytes(b'p cnf 2 2\n1 0\n-1 2 0\n');exact_stream(sample,2,[[1],[-1,2]])
    for name,bytes_ in [('header',b'p cnf 3 2\n1 0\n-1 2 0\n'),('literal',b'p cnf 2 2\n-1 0\n-1 2 0\n'),('order',b'p cnf 2 2\n-1 2 0\n1 0\n'),('extra',sample.read_bytes()+b'2 0\n')]:
        q=out/('stream_corrupt_'+name+'.cnf');q.write_bytes(bytes_);reject('stream_'+name,lambda:exact_stream(q,2,[[1],[-1,2]]))
    return dict(tiny_onehot_complete_assignments=tiny,actual_threshold_truth_rows=gates,positive_baseline_count_assignments=records,rejected_corruptions=rejected,full_factor_positive=False)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        actual=sha(ROOT/p);need(h is None or h==actual,'hash '+p);pins[p]=actual
    try:
        for p,h in PINS.items():pin(p,h)
        producer=read(D+'summary.json')
        for p,h in {**producer['inputs_sha256'],**producer['outputs_sha256']}.items():pin(p,h)
        pre=read(PG);need(pre['status']=='INDEPENDENT_COUNT_MASTER_PREFLIGHT_REVIEW_PASS','preflight gate');inventory=read(PRE+'inventory.json');need(pre['inputs_sha256'][PRE+'inventory.json']==pins[PRE+'inventory.json'],'preflight table binding')
        for p,h in pre['inputs_sha256'].items():pin(p,h)
        raw=read(RAW);groups=list(dict.fromkeys(tuple(a for a in range(12)if raw['L'][a][d])for d in range(60)));need(inventory['groups']==list(map(list,groups)),'raw support groups')
        local=read(LOCAL);catalog=defaultdict(list)
        for i,t in enumerate(local['survivors']):
            sig=tuple(sum(local['words'][w][a]==f for w in t)for a in range(6)for f in range(3));catalog[sig].append(i)
        sigs=[dict(index=i,counts=list(s),local_survivor_indices=catalog[s],count=len(catalog[s]))for i,s in enumerate(sorted(catalog))];need(sigs==read(PRE+'local_signatures.json')['signatures'],'all6061 literal signatures and witnesses')
        coords=[]
        for rec in inventory['coordinate_records']:pin(rec['path'],rec['sha256']);coords.append(read(rec['path']))
        expected,base,suffix,n,nn=build_expected(inventory,coords,sigs);model=read(D+'model.json')
        need(model['schema']=='ARBITRARY_EXCEPTION_COUNT_MASTER_CNF_V1'and model['groups']==inventory['groups']and model['local_signatures']==sigs,'model exact raw scope')
        for k,v in expected.items():need(model[k]==v,'all reconstructed metadata '+k)
        need((n,len(base),nn,len(base)+len(suffix))==(155750,704454,155939,705833),'exact dimensions')
        exact_stream(ROOT/(D+'baseline.cnf'),n,base);exact_stream(ROOT/(D+'at_least_seven.cnf'),nn,base+suffix)
        need((ROOT/(D+'extension.cnfpart')).read_bytes()==b''.join((' '.join(map(str,c))+' 0\n').encode()for c in suffix),'exact appended suffix')
        ext=read(D+'extension.json');need(ext['threshold']==expected['extension']and ext['balanced_selector_ids']==expected['extension']['input_variables']and ext['new_activity_variables']==0,'extension maps/no hidden primary restriction')
        need(ext['necessity_gate_path']==UG and ext['necessity_gate_sha256']==pins[UG],'union premise pin')
        scope=read(D+'scope.json');need(scope['groups']==inventory['groups']and scope['within_group_caps_inherited']and not any(scope[k]for k in ['cross_group_caps_encoded','full_Gram_encoded','residual_D_encoded','target_automorphism_assumed']),'scope and omitted equations')
        need(scope['preflight_gate_sha256']==pins[PG]and scope['extension_necessity_gate_sha256']==pins[UG],'scope exact premises')
        for name,vars_,cs in [('baseline',n,len(base)),('at_least_seven',nn,len(base)+len(suffix))]:need(model['variants'][name]==dict(variables=vars_,clauses=cs,cnf_path=D+name+'.cnf',cnf_sha256=pins[D+name+'.cnf']),'variant path/count/hash')
        recovered=[]
        for r in read(D+'packages.json')['records']:
            pin(r['raw_path'],r['raw_sha256']);pin(r['gzip_path'],r['gzip_sha256']);h=hashlib.sha256();length=0
            with gzip.open(ROOT/r['gzip_path'],'rb')as f:
                for block in iter(lambda:f.read(1048576),b''):h.update(block);length+=len(block)
            need(h.hexdigest()==r['raw_sha256']and length==r['raw_bytes'],'whole gzip identity');recovered.append(r)
        save(out/'controls.json',controls(out,model,base,suffix,n,nn));save(out/'recovery_checks.json',dict(records=recovered))
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_HADAMARD_COUNT_MASTER_CNF.md','uv.lock','pyproject.toml']:pin(p)
        result=dict(status='INDEPENDENT_HADAMARD_COUNT_MASTER_ENCODING_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()},baseline_variables=n,baseline_clauses_checked=len(base),augmented_variables=nn,augmented_clauses_checked=len(base)+len(suffix),complete_clause_reconstruction=True,coordinate_choices=2226,group_choices=74798,count_channels=927,scope='Exact baseline joint-count CSP and exact separately scoped >=7-exception extension; neither is full Gram or a full factor.',independence='Fresh checker, no producer imports; independently approved preflight tables and coordinate-domain/root audit are trusted premises. Raw local signatures and all clauses reconstructed here.',solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start)
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),seconds=result['elapsed_seconds'])))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=pins,source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
