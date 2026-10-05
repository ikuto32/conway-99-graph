"""Candidate exact interval-extension inventory; no solver or research CNF emission."""
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse, gzip, hashlib, json, platform, subprocess, sys, time, traceback
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
BASE=B+'hadamard_count_master_cnf/'
GATE=B+'independent_review/count_gram_intervals/summary.json'
TABLE=B+'hadamard_count_gram_intervals/signature_intervals.json.gz'
RAW=B+'hadamard20_support/six_prism.json'
PINS={GATE:'ebace5fc527bded41f3c31fb66455e78b0eb133c8575508d4426eff912e6ae33',TABLE:'41c4269eb86477069e63900e14296e88734d668a160907f5ce1f0277d2cd230a',BASE+'summary.json':'2137fe0c32043a82166a484085d366309e4037d24aa558dabca20a44e73bff04',BASE+'model.json':'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',BASE+'scope.json':'719fb6e1d7b98656f23b31a83343fb9dfa952ea9a0c14fef3d564faf896f0959',BASE+'baseline.cnf':'609a606c2b228e3956e43ab7d2589dcbcdca797f5978ffa51c8029aa042b7ba7',BASE+'at_least_seven.cnf':'f303edec9a91dc9bcecb95804ee151d0e38e8100b17c9c45a7b4d58b8edbf55e',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'}

def need(ok,msg):
    if not ok: raise ValueError(msg)
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def gzsave(p,x):
    with p.open('xb')as f:
        with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0,compresslevel=9)as g:
            for chunk in json.JSONEncoder(separators=(',',':')).iterencode(x):g.write(chunk.encode())
            g.write(b'\n')
def token(x,v):return x if type(x)is bool else v[abs(x)]==(x>0)
def gate_clauses(out,q,x,r):
    ids=sorted({abs(z)for z in [out,q,x,r]if type(z)is not bool})
    for bits in product((False,True),repeat=len(ids)):
        values=dict(zip(ids,bits))
        if values[out]!=(token(q,values)or(token(x,values)and token(r,values))):yield[-z if values[z]else z for z in ids]
def line_bytes(c):return sum(len(str(x))+1 for x in c)+2
def sat(cs,v):return all(any(token(x,v)for x in c)for c in cs)

class CounterBuilder:
    def __init__(self,n):self.n=n;self.clauses=0;self.bytes=0
    def add(self,c):self.clauses+=1;self.bytes+=line_bytes(c)
    def prefix(self,inputs,bound,mode,record=True):
        states={};rows=[];start=self.clauses;byte=self.bytes;initial=self.n
        limit=bound+1 if mode=='at_most'else bound
        for i,x in enumerate(inputs,1):
            for j in range(1,min(i,limit)+1):
                q=states.get((i-1,j),False);r=True if j==1 else states.get((i-1,j-1),False)
                self.n+=1;z=self.n;first=self.clauses;firstb=self.bytes
                for c in gate_clauses(z,q,x,r):self.add(c)
                states[i,j]=z
                if record:rows.append(dict(i=i,j=j,id=z,q=q,x=x,r=r,first_clause=first+1,clause_count=self.clauses-first,first_byte=firstb,byte_count=self.bytes-firstb))
        final=states[len(inputs),limit];self.add([-final]if mode=='at_most'else[final])
        return dict(mode=mode,bound=bound,inputs=inputs,states=rows,final=final,new_variables=self.n-initial,first_clause=start+1,clause_count=self.clauses-start,first_byte=byte,byte_count=self.bytes-byte)

def controls():
    or_cases=0;corrupt=0
    for n in range(1,7):
        for mask in range(1<<n):
            members=[i+1 for i in range(n)if mask>>i&1];z=n+1;cs=[[-x,z]for x in members]+[[-z,*members]]
            for chosen in range(1,n+1):
                v={x:x==chosen for x in range(1,n+1)};v[z]=chosen in members
                need(sat(cs,v),'OR exact onehot positive');v[z]^=True;need(not sat(cs,v),'corrupted OR rejected');or_cases+=1;corrupt+=1
            need(sum(line_bytes(c)for c in cs)==len(''.join(' '.join(map(str,c))+' 0\n'for c in cs).encode()),'literal ASCII byte count')
    prefix_cases=0
    for inputs in [[1,2,3],[1,1,2],[False,1,True,2],[True,True,1],[False,False,1]]:
        ids=sorted({x for x in inputs if type(x)is not bool})
        for bound in (1,2):
            for mode in ('at_most','at_least'):
                b=CounterBuilder(3);rec=b.prefix(inputs,bound,mode);cs=[]
                for r in rec['states']:cs+=list(gate_clauses(r['id'],r['q'],r['x'],r['r']))
                cs+=[[-rec['final']]if mode=='at_most'else[rec['final']]]
                for bits in product((False,True),repeat=len(ids)):
                    v=dict(zip(ids,bits))
                    for r in rec['states']:v[r['id']]=sum(token(x,v)for x in inputs[:r['i']])>=r['j']
                    count=sum(token(x,v)for x in inputs);expected=count<=bound if mode=='at_most'else count>=bound
                    need(sat(cs,v)==expected,'repeated/constant exact prefix');prefix_cases+=1
                    if expected:
                        v[rec['states'][0]['id']]^=True;need(not sat(cs,v),'changed prefix rejected');corrupt+=1
                need(b.bytes==len(''.join(' '.join(map(str,c))+' 0\n'for c in cs).encode()),'streamed prefix bytes')
    return dict(or_onehot_cases=or_cases,prefix_input_cases=prefix_cases,corruptions_rejected=corrupt,full_research_factor_positive=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    def budget():need(time.monotonic()-start<60,'60-second cooperative inventory allocation')
    try:
        for p,h in PINS.items():need(sha(ROOT/p)==h,'input pin '+p);pins[p]=h
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=sha(p)
        need(read(GATE)['status']=='INDEPENDENT_COUNT_SIGNATURE_GRAM_INTERVALS_PASS','table gate status')
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),limits=dict(cooperative_seconds=60,planning_memory_bytes=768*1024**2,native_calls=0),algorithm='Exact group/subset channel sharing and streamed maxterm prefix counting; no clause-list materialization.'))
        control=controls();save(out/'controls.json',control);budget()
        model=read(BASE+'model.json');raw=read(RAW)
        with gzip.open(ROOT/TABLE,'rt',encoding='utf-8')as f:table=json.load(f)
        localindex={tuple(c):i for i,c in enumerate(table['local_cells'])};records=table['records']
        need([r['signature_index']for r in records]==list(range(6061)),'ordered complete signature table')
        low=np.array([r['minimum']for r in records],dtype=np.int8);high=np.array([r['maximum']for r in records],dtype=np.int8)
        need(low.shape==high.shape==(6061,135)and np.all((0<=low)&(low<=high)&(high<=2)),'entire coefficient range 0..2')
        del table,records
        base=model['variants']['at_least_seven'];channel_builder=CounterBuilder(base['variables']);shared={};channels=[];requests=[];cells=[];hist=Counter();unshared=CounterBuilder(base['variables']);request_count=0
        gd=model['group_domains'];arrays=[]
        for d in gd:
            sigs=np.array(d['signature_indices'],dtype=np.int32);ids=np.array(d['selectors'],dtype=np.int64);digits=np.array([len(str(x))for x in d['selectors']],dtype=np.int32)
            arrays.append((sigs,ids,digits,low[sigs],high[sigs]))
        def request(g,j,kind,t,origin):
            nonlocal request_count
            sigs,ids,digits,lo,hi=arrays[g];mask=(lo if kind=='lower'else hi)[:,j]>=t;n=int(np.count_nonzero(mask));m=int.from_bytes(np.packbits(mask,bitorder='little').tobytes(),'little');sigdigits=int(np.sum(digits[mask]));request_count+=1
            if n==0:hist['constant_false_requests']+=1;return False
            if n==len(ids):hist['constant_true_requests']+=1;return True
            if n==1:hist['singleton_requests']+=1;return int(ids[np.flatnonzero(mask)[0]])
            hist['proper_or_requests']+=1;unshared.n+=1;unshared.clauses+=n+1;unshared.bytes+=n*(len(str(unshared.n))+6)+2*sigdigits+len(str(unshared.n))+4
            identity=(g,m)
            if identity in shared:return shared[identity]
            channel_builder.n+=1;z=channel_builder.n;shared[identity]=z;first=channel_builder.clauses;firstb=channel_builder.bytes;channel_builder.clauses+=n+1;channel_builder.bytes+=n*(len(str(z))+6)+2*sigdigits+len(str(z))+4
            channels.append(dict(variable=z,group=g,selector_index_mask_hex=format(m,'x'),member_count=n,selector_decimal_digits_sum=sigdigits,first_request=origin,first_clause=first+1,clause_count=n+1,first_byte=firstb,byte_count=channel_builder.bytes-firstb))
            return z
        balanced=[next(s for s in d['signature_indices']if model['local_signatures'][s]['counts']==[1]*18)for d in gd]
        for a,b in combinations(range(12),2):
            if a//2==b//2:continue
            for f,h in product(range(3),repeat=2):
                ci=len(cells);terms=[];lower=[];upper=[];true_lo=0;true_hi=0
                for d in gd:
                    g=d['group'];s=d['support']
                    if a not in s or b not in s:continue
                    j=localindex[s.index(a),s.index(b),f,h];tokens=[]
                    for kind,t in [('lower',1),('lower',2),('upper',1),('upper',2)]:tokens.append(request(g,j,kind,t,dict(cell=ci,group=g,local_cell=j,bound=kind,threshold=t)))
                    terms.append(dict(group=g,local_cell=j,lower=tokens[:2],upper=tokens[2:]));lower+=tokens[:2];upper+=tokens[2:];true_lo+=int(low[balanced[g],j]);true_hi+=int(high[balanced[g],j])
                target=raw['prescribed_Gram36'][12*f+a][12*h+b];need(target==(1 if f==h else 2),'literal target');need(len(terms)==5 and true_lo<=target<=true_hi,'five groups and balanced count positive')
                cells.append(dict(index=ci,coordinates=[a,b],fibres=[f,h],target=target,terms=terms,lower_inputs=lower,upper_inputs=upper,balanced_lower=true_lo,balanced_upper=true_hi))
                if ci%45==0:budget()
        need(len(cells)==540 and request_count==10800,'complete requested population')
        c=CounterBuilder(channel_builder.n);c.clauses=channel_builder.clauses;c.bytes=channel_builder.bytes
        for cell in cells:
            cell['lower_counter']=c.prefix(cell['lower_inputs'],cell['target'],'at_most');cell['upper_counter']=c.prefix(cell['upper_inputs'],cell['target'],'at_least')
            if cell['index']%45==0:budget()
        with (ROOT/base['cnf_path']).open('rb')as f:oldheader=f.readline()
        fullclauses=base['clauses']+c.clauses;newheader=f'p cnf {c.n} {fullclauses}\n'.encode();fullbytes=(ROOT/base['cnf_path']).stat().st_size-len(oldheader)+len(newheader)+c.bytes
        configuration=dict(schema='EXACT_COUNT_GRAM_INTERVAL_EXTENSION_INVENTORY_V1',inputs_sha256=pins,base=base,channel_order='first request in cells/group/lower1,lower2,upper1,upper2',subset_identity='group ID plus little-endian selector-index mask; empty/full/singleton reuse',channels=channels,cells=cells,selected_totals=dict(variables=c.n,clauses=fullclauses,ascii_cnf_bytes=fullbytes,new_variables=c.n-base['variables'],new_clauses=c.clauses,new_body_bytes=c.bytes),scope='Necessary count-signature interval inequalities only; no full factor, cross-group caps or residual D encoded.')
        budget();gzsave(out/'configuration.json.gz',configuration);budget()
        summary=dict(status='CANDIDATE_EXACT_INTERVAL_EXTENSION_INVENTORY_COMPLETE',inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},coefficient_minimum=int(low.min()),coefficient_maximum=int(high.max()),global_cells=540,threshold_requests=request_count,request_histogram=dict(hist),distinct_new_OR_channels=len(channels),OR_clauses=channel_builder.clauses,OR_ascii_bytes=channel_builder.bytes,unshared_proper_OR_channels=unshared.n-base['variables'],unshared_OR_clauses=unshared.clauses,unshared_OR_ascii_bytes=unshared.bytes,channel_variable_savings=unshared.n-channel_builder.n,channel_clause_savings=unshared.clauses-channel_builder.clauses,prefix_variables=c.n-channel_builder.n,prefix_clauses=c.clauses-channel_builder.clauses,prefix_ascii_bytes=c.bytes-channel_builder.bytes,**configuration['selected_totals'],elapsed_seconds=time.monotonic()-start,research_CNF_emitted=False,native_calls=0,solver_calls=0,independent_approval=False,artifact_availability='LOCAL_ONLY',scope=configuration['scope'],recommended_build='Streaming body writer; reuse the frozen base body and exact inventory configuration. Separate resource authorization and independent gates required.')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in ['inputs_sha256','outputs_sha256']}));print('summary_sha256',sha(out/'summary.json'))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=pins,source_sha256=sha(Path(__file__)),elapsed_seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
