"""Stream a frozen interval inventory to candidate CNF; no solver calls."""
from datetime import datetime,timezone
from itertools import product
from pathlib import Path
import argparse,ctypes,gzip,hashlib,json,os,platform,shutil,subprocess,sys,time,traceback

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
INV=B+'count_interval_inventory/';BASE=B+'hadamard_count_master_cnf/';GATE=B+'independent_review/hadamard_count_master_cnf_v2/summary.json'
PINS={INV+'summary.json':'0c11732c0a9c039d7b5235b4c5303b7e4226c7cca7b08e8af8da7f74af150c32',INV+'configuration.json.gz':'97794c8be67bf32276763a0439edc3e83ba81a1fa8ee88604f2d75c5721c1099',INV+'controls.json':'81524bc911f63c21f57d5f216663c58f98d79a60d34937da6ae4e58105ca2523',GATE:'80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888',B+'independent_review/count_gram_intervals/summary.json':'ebace5fc527bded41f3c31fb66455e78b0eb133c8575508d4426eff912e6ae33',BASE+'model.json':'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',BASE+'at_least_seven.cnf':'f303edec9a91dc9bcecb95804ee151d0e38e8100b17c9c45a7b4d58b8edbf55e'}
EXPECTED=(185963,7659287,163409055);PART=9*1024**2

def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def memory():
    if os.name!='nt':return None
    class PMC(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
    p=PMC();p.cb=ctypes.sizeof(p);handle=ctypes.c_void_p(-1);ok=ctypes.windll.psapi.GetProcessMemoryInfo(handle,ctypes.byref(p),p.cb)
    return dict(working_set_bytes=p.WorkingSetSize,peak_working_set_bytes=p.PeakWorkingSetSize)if ok else None
def token(x,v):return x if type(x)is bool else v[abs(x)]==(x>0)
def relation(out,q,x,r):
    ids=sorted({abs(z)for z in [out,q,x,r]if type(z)is not bool})
    for bits in product((False,True),repeat=len(ids)):
        v=dict(zip(ids,bits))
        if v[out]!=(token(q,v)or(token(x,v)and token(r,v))):yield[-z if v[z]else z for z in ids]
def encoded(cs):return ''.join(' '.join(map(str,c))+' 0\n'for c in cs).encode('ascii')

def package(source,name,out,check):
    pieces=[];rawhash=hashlib.sha256();offset=0
    with source.open('rb')as f:
        for i,block in enumerate(iter(lambda:f.read(PART),b'')):
            check();part=out/f'{name}.part{i:03d}.gz'
            with part.open('xb')as fp:
                with gzip.GzipFile(filename='',mode='wb',fileobj=fp,mtime=0,compresslevel=6)as g:g.write(block)
            need(part.stat().st_size<10*1024**2,'public member limit')
            restored=gzip.decompress(part.read_bytes());need(restored==block,'literal member recovery');rawhash.update(restored)
            pieces.append(dict(path=key(part),sha256=sha(part),bytes=part.stat().st_size,raw_offset=offset,raw_bytes=len(block),raw_sha256=hashlib.sha256(block).hexdigest()));offset+=len(block)
    need(rawhash.hexdigest()==sha(source)and offset==source.stat().st_size,'full package recovery')
    return dict(raw_path=key(out/name),raw_sha256=rawhash.hexdigest(),raw_bytes=offset,raw_availability='LOCAL_ONLY',parts=pieces,recovery_identity=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume',type=Path);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={};streams=[];state=None;peak=0
    def check():
        nonlocal peak
        m=memory()
        if m:peak=max(peak,m['peak_working_set_bytes']);need(m['working_set_bytes']<=768*1024**2,'768MiB working-set limit')
        if time.monotonic()-start>=180:raise TimeoutError('180-second cooperative allocation')
    try:
        for p,h in PINS.items():need(sha(ROOT/p)==h,'pin '+p);pins[p]=h
        config=json.loads(gzip.decompress((ROOT/(INV+'configuration.json.gz')).read_bytes()))
        for p,h in config['inputs_sha256'].items():need(sha(ROOT/p)==h,'inventory closure '+p);pins[p]=h
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=sha(p)
        need(read(ROOT/GATE)['status']=='INDEPENDENT_HADAMARD_COUNT_MASTER_ENCODING_PASS','base encoding gate')
        need(tuple(config['selected_totals'][k]for k in ['variables','clauses','ascii_cnf_bytes'])==EXPECTED,'fixed totals')
        model=read(ROOT/(BASE+'model.json'));selectors={d['group']:d['selectors']for d in model['group_domains']};base=config['base'];full=out/'instance.cnf.partial';suffix=out/'interval.cnfpart.partial';header=f'p cnf {EXPECTED[0]} {EXPECTED[1]}\n'.encode()
        state=dict(next_channel=0,next_cell=0,suffix_clauses=0,suffix_bytes=0,full_bytes=0,checkpoint_index=0)
        resume_record=None
        if args.resume:
            old=args.resume.resolve();previous=read(old/'summary.json');need(previous['status']=='PARTIAL_UNKNOWN','explicit partial-only resume');checkpoint=read(old/'checkpoint.json');need(previous['checkpoint_sha256']==sha(old/'checkpoint.json'),'resume summary checkpoint pin');need(checkpoint['inputs_sha256']==pins,'resume immutable inputs/source/spec');state=checkpoint['state']
            for name,target in [('instance.cnf.partial',full),('interval.cnfpart.partial',suffix)]:
                src=old/name;rec=checkpoint['partial_files'][name];need(src.stat().st_size==rec['bytes']and sha(src)==rec['sha256'],'resume complete saved bytes');shutil.copyfile(src,target)
            resume_record=dict(previous_summary_path=key(old/'summary.json'),previous_summary_sha256=sha(old/'summary.json'),previous_checkpoint_path=key(old/'checkpoint.json'),previous_checkpoint_sha256=sha(old/'checkpoint.json'))
        else:
            with full.open('xb')as target,(ROOT/base['cnf_path']).open('rb')as source:
                oldheader=source.readline();target.write(header);shutil.copyfileobj(source,target,1024**2)
            suffix.touch(exist_ok=False);state['full_bytes']=full.stat().st_size
        fullhash=hashlib.sha256();sufhash=hashlib.sha256()
        for p,h in [(full,fullhash),(suffix,sufhash)]:
            with p.open('rb')as f:
                for block in iter(lambda:f.read(1024**2),b''):h.update(block)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),limits=dict(cooperative_seconds=180,working_set_bytes=768*1024**2,raw_chunk_bytes=PART,native_calls=0),resume=resume_record,expected_variables=EXPECTED[0],expected_clauses=EXPECTED[1],expected_bytes=EXPECTED[2]))
        ff=full.open('ab');sf=suffix.open('ab');streams=[ff,sf]
        def checkpoint():
            ff.flush();sf.flush();os.fsync(ff.fileno());os.fsync(sf.fileno());state['checkpoint_index']+=1
            rec=dict(inputs_sha256=pins,state=state.copy(),partial_files={'instance.cnf.partial':dict(bytes=state['full_bytes'],sha256=fullhash.hexdigest()),'interval.cnfpart.partial':dict(bytes=state['suffix_bytes'],sha256=sufhash.hexdigest())},elapsed_seconds=time.monotonic()-start)
            save(out/f'checkpoint_{state["checkpoint_index"]:04d}.json',rec);tmp=out/'checkpoint.next.json';save(tmp,rec);os.replace(tmp,out/'checkpoint.json')
        def emit(data,count):
            ff.write(data);sf.write(data);fullhash.update(data);sufhash.update(data);state['full_bytes']+=len(data);state['suffix_bytes']+=len(data);state['suffix_clauses']+=count
        checkpoint();check()
        for i in range(state['next_channel'],len(config['channels'])):
            c=config['channels'][i];need(state['suffix_clauses']+1==c['first_clause']and state['suffix_bytes']==c['first_byte'],'channel sequence');mask=int(c['selector_index_mask_hex'],16);members=[]
            while mask:
                b=mask&-mask;members.append(selectors[c['group']][b.bit_length()-1]);mask-=b
            need(len(members)==c['member_count'],'channel mask population');z=c['variable'];data=(''.join(f'-{x} {z} 0\n'for x in members)+' '.join(map(str,[-z,*members]))+' 0\n').encode('ascii');need(len(data)==c['byte_count'],'literal OR byte prediction');emit(data,len(members)+1);state['next_channel']=i+1
            if (i+1)%128==0:checkpoint();check()
        checkpoint();check()
        for i in range(state['next_cell'],len(config['cells'])):
            cell=config['cells'][i]
            for rec in [cell['lower_counter'],cell['upper_counter']]:
                need(state['suffix_clauses']+1==rec['first_clause']and state['suffix_bytes']==rec['first_byte'],'counter sequence');startc=state['suffix_clauses'];startb=state['suffix_bytes']
                for r in rec['states']:
                    clauses=list(relation(r['id'],r['q'],r['x'],r['r']));data=encoded(clauses);need(len(clauses)==r['clause_count']and len(data)==r['byte_count'],'literal maxterm gate prediction');emit(data,len(clauses))
                emit(encoded([[-rec['final']]if rec['mode']=='at_most'else[rec['final']]]),1)
                need(state['suffix_clauses']-startc==rec['clause_count']and state['suffix_bytes']-startb==rec['byte_count'],'counter totals')
            state['next_cell']=i+1
            if (i+1)%45==0:checkpoint();check()
        checkpoint();check();ff.close();sf.close();streams=[]
        need(state['suffix_clauses']==config['selected_totals']['new_clauses']and state['suffix_bytes']==config['selected_totals']['new_body_bytes'],'whole suffix counts');need(state['full_bytes']==EXPECTED[2]and base['clauses']+state['suffix_clauses']==EXPECTED[1],'complete declared formula')
        actual_count=0;prefix_ok=True
        with full.open('rb')as f,(ROOT/base['cnf_path']).open('rb')as old,suffix.open('rb')as s:
            need(f.readline()==header,'actual header');old.readline()
            for block in iter(lambda:old.read(1024**2),b''):need(f.read(len(block))==block,'exact frozen base body');actual_count+=block.count(b'\n')
            for block in iter(lambda:s.read(1024**2),b''):need(f.read(len(block))==block,'exact preserved suffix body');actual_count+=block.count(b'\n')
            need(not f.read(1)and actual_count==EXPECTED[1],'all line count and exhaustion')
        need(sha(full)==fullhash.hexdigest()and sha(suffix)==sufhash.hexdigest(),'fresh complete streaming hashes');check()
        packages=[package(full,'instance.cnf',out,check),package(suffix,'interval.cnfpart',out,check)];save(out/'packages.json',dict(schema='CONTIGUOUS_RAW_GZIP_MEMBERS_V1',records=packages))
        scope=dict(schema='AT_LEAST_SEVEN_COUNT_MASTER_INTERVAL_SCOPE_V1',inputs_sha256=pins,necessary_only=True,complete_coordinate_count_domains=True,complete_group_count_signatures=True,at_least_seven_exceptional_groups=True,all_540_exact_signature_interval_bounds=True,within_group_caps_inherited=True,cross_group_caps_encoded=False,full_Gram_encoded=False,residual_D_encoded=False,target_automorphism_assumed=False,full_factor=False,target_graph=False)
        save(out/'scope.json',scope);save(out/'model.json',dict(schema='EXACT_COUNT_MASTER_INTERVAL_CNF_V1',variables=EXPECTED[0],clauses=EXPECTED[1],cnf_path=key(out/'instance.cnf'),cnf_sha256=fullhash.hexdigest(),base_model_path=BASE+'model.json',base_model_sha256=PINS[BASE+'model.json'],base_variant='at_least_seven',base_cnf_path=base['cnf_path'],base_cnf_sha256=base['cnf_sha256'],base_variables=base['variables'],base_clauses=base['clauses'],inventory_configuration_path=INV+'configuration.json.gz',inventory_configuration_sha256=PINS[INV+'configuration.json.gz'],suffix_path=key(out/'interval.cnfpart'),suffix_sha256=sufhash.hexdigest(),scope_path=key(out/'scope.json'),scope_sha256=sha(out/'scope.json'),inputs_sha256=pins,complete_factor=False,target_graph=False))
        check();os.replace(full,out/'instance.cnf');os.replace(suffix,out/'interval.cnfpart')
        summary=dict(status='CANDIDATE_EXACT_COUNT_INTERVAL_CNF_BUILT',inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},variables=EXPECTED[0],clauses=EXPECTED[1],cnf_bytes=EXPECTED[2],suffix_clauses=state['suffix_clauses'],suffix_bytes=state['suffix_bytes'],channels_completed=state['next_channel'],cells_completed=state['next_cell'],native_calls=0,solver_calls=0,independent_approval=False,elapsed_seconds=time.monotonic()-start,peak_working_set_bytes=peak or None,artifact_availability='LOCAL_ONLY',scope='Necessary count-signature interval extension of the at-least-seven relaxation, no simultaneous full factor, cross-group caps or residual completion.')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in ['inputs_sha256','outputs_sha256']}));print('summary_sha256',sha(out/'summary.json'))
    except TimeoutError as e:
        for f in streams:f.close()
        checkpoint_path=out/'checkpoint.json'
        # A checkpoint is a resumable boundary only when every saved byte is covered.
        cp=read(checkpoint_path)if checkpoint_path.exists()else None
        complete=bool(cp)and all((out/n).stat().st_size==r['bytes']and sha(out/n)==r['sha256']for n,r in cp['partial_files'].items())
        save(out/'summary.json',dict(status='PARTIAL_UNKNOWN'if complete else'FAILED_UNCHECKPOINTED_PARTIAL',reason=str(e),checkpoint_sha256=sha(checkpoint_path)if cp else None,inputs_sha256=pins,state=state,elapsed_seconds=time.monotonic()-start,native_calls=0));print('PARTIAL_UNKNOWN'if complete else'FAILED_UNCHECKPOINTED_PARTIAL')
    except BaseException as e:
        for f in streams:f.close()
        save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=pins,state=state,elapsed_seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
