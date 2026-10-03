"""Independent full interval-CNF reconstruction, no producer imports/native calls."""
from pathlib import Path
from itertools import combinations,product
from datetime import datetime,timezone
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
import audit_20260930_hadamard_count_master_cnf_v2 as basecheck
ROOT=basecheck.ROOT;B=basecheck.B;BASE=basecheck.D;D=B+'count_interval_cnf/';INV=B+'count_interval_inventory/'
TABLE=B+'hadamard_count_gram_intervals/signature_intervals.json.gz';IG=B+'independent_review/count_gram_intervals/summary.json';BG=B+'independent_review/hadamard_count_master_cnf_v2/summary.json';RAW=basecheck.RAW
need=basecheck.need;read=basecheck.read;sha=basecheck.sha;save=basecheck.save
PINS={D+'summary.json':'224eb5e1d016bda6ac903de5c59ab489c1c3d4c0abdc5ecf342c97d4f2ea0a84',D+'instance.cnf':'5ee253b41de8cfcc5529175c4685c0fc9a8886b8d6c3600e435ae9db5146cbab',D+'model.json':'ae40c085c48dc44b7a7438b4c707f2c16408258d4501e855b151200ef1b6c995',D+'scope.json':'5e7e1ee1dd23e327609dde81a6a137f8efb46171b1d7eca9907b4f20058ca6e3',IG:'ebace5fc527bded41f3c31fb66455e78b0eb133c8575508d4426eff912e6ae33',BG:'80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888',TABLE:'41c4269eb86477069e63900e14296e88734d668a160907f5ce1f0277d2cd230a'}
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def line(c):return (' '.join(map(str,c))+' 0\n').encode()
def controls():
    ors=0;prefixes=0;corrupt=0
    for n in range(1,6):
        for mask in range(1<<n):
            members=[i+1 for i in range(n)if mask>>i&1];z=n+1;cs=[[-x,z]for x in members]+[[-z,*members]]
            for bits in product((False,True),repeat=n):
                want=any(bits[x-1]for x in members)
                for zz in [False,True]:
                    v=[None,*bits,zz];need(all(basecheck.clause_pass(c,v)for c in cs)==(zz==want),'full OR iff truth');ors+=1
                v=[None,*bits,not want];need(not all(basecheck.clause_pass(c,v)for c in cs),'flipped OR');corrupt+=1
    for ins in [[1,2,3],[1,1,2],[False,1,True,2],[True,True,1],[False,False,1]]:
        for bound,mode in product((1,2),('at_most','at_least')):
            last=3;states={};cs=[];rows=[];limit=bound+1 if mode=='at_most'else bound
            for i,x in enumerate(ins,1):
                for j in range(1,min(i,limit)+1):
                    last+=1;q=states.get((i-1,j),False);r=True if j==1 else states.get((i-1,j-1),False);cs+=basecheck.gate_clauses(last,q,x,r);states[i,j]=last;rows.append((last,i,j))
            final=states[len(ins),limit];cs.append([-final]if mode=='at_most'else[final]);ids=sorted({x for x in ins if type(x)is int})
            for bits in product((False,True),repeat=len(ids)):
                v=[False]*(last+1)
                for x,b in zip(ids,bits):v[x]=b
                ev=lambda t:t if type(t)is bool else v[t]
                for z,i,j in rows:v[z]=sum(ev(t)for t in ins[:i])>=j
                total=sum(ev(t)for t in ins);want=total<=bound if mode=='at_most'else total>=bound;need(all(basecheck.clause_pass(c,v)for c in cs)==want,'complete repeated/constant threshold positive/negative');prefixes+=1
                v[rows[0][0]]=not v[rows[0][0]];need(not all(basecheck.clause_pass(c,v)for c in cs[:-1]),'wrong threshold state');corrupt+=1
    return dict(full_OR_truth_rows=ors,threshold_inputs=prefixes,flipped_gate_controls=corrupt,full_factor_positive=False)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):pins[p]=sha(ROOT/p);need(h is None or pins[p]==h,'hash '+p)
    try:
        for p,h in PINS.items():pin(p,h)
        producer=read(D+'summary.json')
        for p,h in {**producer['inputs_sha256'],**producer['outputs_sha256']}.items():pin(p,h)
        for gate,status in [(BG,'INDEPENDENT_HADAMARD_COUNT_MASTER_ENCODING_PASS'),(IG,'INDEPENDENT_COUNT_SIGNATURE_GRAM_INTERVALS_PASS')]:
            g=read(gate);need(g['status']==status,'independent premise status')
            for p,h in g['inputs_sha256'].items():pin(p,h)
        save(out/'controls.json',controls());base=read(BASE+'model.json');model=read(D+'model.json');scope=read(D+'scope.json');raw=read(RAW)
        with gzip.open(ROOT/TABLE,'rt',encoding='utf-8')as f:table=json.load(f)
        with gzip.open(ROOT/(INV+'configuration.json.gz'),'rt',encoding='utf-8')as f:cfg=json.load(f)
        need(cfg['base']==base['variants']['at_least_seven'],'immutable augmented base metadata');gd=base['group_domains'];bounds=table['records'];localindex={tuple(c):i for i,c in enumerate(table['local_cells'])}
        need(len(bounds)==6061 and all(r['signature_index']==i and all(0<=a<=b<=2 for a,b in zip(r['minimum'],r['maximum']))for i,r in enumerate(bounds)),'exact whole table coefficient range')
        C=raw['core_adjacency'];G=[[12*int(i==j)-C[i][j]+2-sum(C[i][k]*C[k][j]for k in range(36))-int(i//12==j//12)for j in range(36)]for i in range(36)];need(G==raw['prescribed_Gram36'],'raw-core-derived Gram')
        channels=[];cells=[];identities={};last=155939;requests=0;false_count=0;shared_requests=0;nc=0;nb=0
        def channel(g,j,kind,t,origin):
            nonlocal last,requests,false_count,shared_requests,nc,nb
            d=gd[g];members=[i for i,sid in enumerate(d['signature_indices'])if bounds[sid]['minimum'if kind=='lower'else'maximum'][j]>=t];requests+=1
            if not members:false_count+=1;return False
            if len(members)==len(d['selectors']):return True
            if len(members)==1:return d['selectors'][members[0]]
            ident=(g,tuple(members))
            if ident in identities:shared_requests+=1;return identities[ident]
            last+=1;z=last;identities[ident]=z;selected=[d['selectors'][i]for i in members];mask=sum(1<<i for i in members);cs=[[-x,z]for x in selected]+[[-z,*selected]];length=sum(len(line(c))for c in cs)
            channels.append(dict(variable=z,group=g,selector_index_mask_hex=format(mask,'x'),member_count=len(selected),selector_decimal_digits_sum=sum(len(str(x))for x in selected),first_request=origin,first_clause=nc+1,clause_count=len(cs),first_byte=nb,byte_count=length));nc+=len(cs);nb+=length;return z
        balanced=[next(s for s in d['signature_indices']if base['local_signatures'][s]['counts']==[1]*18)for d in gd]
        for a,b in combinations(range(12),2):
            if a//2==b//2:continue
            for f,h in product(range(3),repeat=2):
                ci=len(cells);terms=[];lower=[];upper=[];bl=bh=0
                for d in gd:
                    g=d['group'];s=d['support']
                    if a not in s or b not in s:continue
                    j=localindex[s.index(a),s.index(b),f,h];tokens=[]
                    for kind,t in [('lower',1),('lower',2),('upper',1),('upper',2)]:tokens.append(channel(g,j,kind,t,dict(cell=ci,group=g,local_cell=j,bound=kind,threshold=t)))
                    terms.append(dict(group=g,local_cell=j,lower=tokens[:2],upper=tokens[2:]));lower+=tokens[:2];upper+=tokens[2:];bl+=bounds[balanced[g]]['minimum'][j];bh+=bounds[balanced[g]]['maximum'][j]
                target=G[12*f+a][12*h+b];need(len(terms)==5 and bl<=target<=bh,'five terms and positive balanced control');cells.append(dict(index=ci,coordinates=[a,b],fibres=[f,h],target=target,terms=terms,lower_inputs=lower,upper_inputs=upper,balanced_lower=bl,balanced_upper=bh))
        need(channels==cfg['channels'],'complete independently reconstructed group/subset OR masks, sharing and ranges');need((len(channels),requests,false_count,shared_requests)==(8244,10800,2388,168),'complete request census')
        # Compare all actual bytes using independent reconstructed clauses, retaining constant memory.
        with (ROOT/(D+'instance.cnf')).open('rb')as actual,(ROOT/(D+'interval.cnfpart')).open('rb')as suffix,(ROOT/(BASE+'at_least_seven.cnf')).open('rb')as old:
            need(actual.readline()==b'p cnf 185963 7659287\n','new exact header');need(old.readline()==b'p cnf 155939 705833\n','base exact header')
            for block in iter(lambda:old.read(1048576),b''):need(actual.read(len(block))==block,'entire unchanged base body')
            emitted=0;bytes_=0
            def emit(c):
                nonlocal emitted,bytes_
                expected=line(c);need(actual.readline()==expected and suffix.readline()==expected,f'actual full/suffix clause {emitted+1}');emitted+=1;bytes_+=len(expected)
            for c in channels:
                mask=int(c['selector_index_mask_hex'],16);xs=[x for i,x in enumerate(gd[c['group']]['selectors'])if mask>>i&1];need(emitted+1==c['first_clause']and bytes_==c['first_byte'],'actual channel boundary')
                for x in xs:emit([-x,c['variable']])
                emit([-c['variable'],*xs])
            need((emitted,bytes_)==(nc,nb),'all OR bytes and clauses')
            for cell in cells:
                for kind,mode in [('lower','at_most'),('upper','at_least')]:
                    inputs=cell[kind+'_inputs'];bound=cell['target'];limit=bound+1 if mode=='at_most'else bound;states={};records=[];first=emitted+1;firstbyte=bytes_;initial=last
                    for i,x in enumerate(inputs,1):
                        for j in range(1,min(i,limit)+1):
                            last+=1;z=last;q=states.get((i-1,j),False);r=True if j==1 else states.get((i-1,j-1),False);cfirst=emitted+1;bfirst=bytes_
                            for clause in basecheck.gate_clauses(z,q,x,r):emit(clause)
                            records.append(dict(i=i,j=j,id=z,q=q,x=x,r=r,first_clause=cfirst,clause_count=emitted-cfirst+1,first_byte=bfirst,byte_count=bytes_-bfirst));states[i,j]=z
                    final=states[len(inputs),limit];emit([-final]if mode=='at_most'else[final]);cell[kind+'_counter']=dict(mode=mode,bound=bound,inputs=inputs,states=records,final=final,new_variables=last-initial,first_clause=first,clause_count=emitted-first+1,first_byte=firstbyte,byte_count=bytes_-firstbyte)
                need(cell==cfg['cells'][cell['index']],f'complete interval cell metadata {cell["index"]}')
            need(not actual.read(1)and not suffix.read(1),'complete formula exhaustion');need((last,emitted,bytes_)==(185963,6953454,152147616),'final exact totals')
        need(len(cells)==540 and model['variables']==last and model['clauses']==705833+emitted and model['base_model_path']==BASE+'model.json'and model['base_model_sha256']==pins[BASE+'model.json']and model['base_variant']=='at_least_seven','model exact scope')
        need(model['inventory_configuration_path']==INV+'configuration.json.gz'and model['inventory_configuration_sha256']==pins[INV+'configuration.json.gz']and model['cnf_sha256']==pins[D+'instance.cnf'],'model raw identities')
        need(all(scope[k]for k in ['necessary_only','complete_coordinate_count_domains','complete_group_count_signatures','at_least_seven_exceptional_groups','all_540_exact_signature_interval_bounds','within_group_caps_inherited'])and not any(scope[k]for k in ['cross_group_caps_encoded','full_Gram_encoded','residual_D_encoded','target_automorphism_assumed','full_factor','target_graph']),'precise necessary relaxation scope')
        recovered=[]
        for package in read(D+'packages.json')['records']:
            digest=hashlib.sha256();offset=0
            for p in package['parts']:
                need(p['raw_offset']==offset and sha(ROOT/p['path'])==p['sha256'],'ordered compressed part identity');block=gzip.decompress((ROOT/p['path']).read_bytes());need(len(block)==p['raw_bytes']and hashlib.sha256(block).hexdigest()==p['raw_sha256'],'raw member bytes');digest.update(block);offset+=len(block)
            need(offset==package['raw_bytes']and digest.hexdigest()==package['raw_sha256']==sha(ROOT/package['raw_path']),'whole ordered recovery identity');recovered.append(dict(raw_path=package['raw_path'],raw_bytes=offset,parts=len(package['parts']),sha256=digest.hexdigest()))
        save(out/'recovery_checks.json',dict(records=recovered));save(out/'exact_inventory.json',dict(global_cells=540,threshold_requests=requests,constant_false_requests=false_count,reused_proper_OR_requests=shared_requests,new_OR_channels=len(channels),new_threshold_variables=last-155939-len(channels),suffix_clauses=emitted,suffix_bytes=bytes_,all_complete=True))
        for p in [key(Path(__file__)),key(Path(basecheck.__file__)),'docs/AUDIT_20260930_COUNT_INTERVAL_CNF.md','uv.lock','pyproject.toml']:pin(p)
        result=dict(status='INDEPENDENT_COUNT_INTERVAL_ENCODING_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},variables=last,clauses_checked=705833+emitted,raw_bytes_checked=(ROOT/(D+'instance.cnf')).stat().st_size,global_interval_cells=540,complete_reconstruction=True,scope='Exact conjunction of the authenticated >=7 count-CSP and all540 scalar local-signature Gram interval inequalities; necessary relaxation only.',trusted_components=['Independent base encoding and root interval-extrema gates reused as explicit premises.','Only independently authored threshold truth helper imported. No producer imports.'],solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start)
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),seconds=result['elapsed_seconds'])))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
