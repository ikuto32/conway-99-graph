"""Read-only independent gzip/original comparison and replay ABI audit."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,copy,hashlib,json,re,shlex,sys,time,traceback,zlib
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20261001_';I=B+'independent_review/'
MAN=B+'twentyninth_raw_recovery/manifest.json';GUIDE='docs/REPRODUCING_20261001_TWENTYNINTH_WAVE.md';PLAN=B+'resume/twentyninth_replay_plan.json';HELPER='acceleration/recover_20261001_twentyninth_raw_artifacts.py';CONTROLS=B+'twentyninth_recovery_controls/summary.json'
PINS={'acceleration/audit_20261001_twentyninth_recovery_replay.py':'f029d80bc8f3f6a80725ac6471cc389c1ada45fdb44b8067d93704fc07d3e160','acceleration/audit_20261001_twentyninth_recovery_replay_spec.md':'cfc56f206111a86a332eef96b22a13423ca83f67c743e57241cf63782e345cb0','acceleration/results/20261001_independent_review/twentyninth_recovery_replay/failure.json':'ae7009627d5918cfe2157e0b3611498fb956ebdef29ed399df118c34abdcb267',PLAN:'5e1481131f6fbb1e167c0b80c9285122f1b8609d45e805ff007ed37cb96a7e06',HELPER:'d55e458b2fb980691f416ca346782ba371bf713c80b8ecb055c5240f794a5730'}
NAMES=['exact_eight_next64_cnfs_v3','exact_eight_next64_object_calibration','exact_eight_next64_proofs','exact_eight_prefix64_batch02_cnfs_v3','exact_eight_prefix64_batch02_object_calibration','sizeclass16_gf3_affine_weights','exact_eight_uniform_gram','exact_eight_prefix64_batch02_proofs'];INPUTS={}
def need(x,m):
    if not x:raise ValueError(m)
def safe(p):
    q=Path(p);q=q.resolve()if q.is_absolute()else(ROOT/q).resolve();need(q.is_relative_to(ROOT),'path containment');r=q.relative_to(ROOT).as_posix();need(not r.startswith('tools/')and q.name!='PROMPT.md'and r!='acceleration/results/20260930_independent_review/hadamard_oriented_unknown/process.stdout.log' and 'exact_eight_prefix64_batch03'not in r,'protected path');return q
def key(p):return safe(p).relative_to(ROOT).as_posix()
def sha(p):
    q=safe(p)
    with q.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
    INPUTS[key(q)]=h;return h
def bind(d):
    for p,h in d.items():need(sha(p)==h,'exact hash '+p)
def load(p):sha(p);return json.loads(safe(p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def decode(data):
    d=zlib.decompressobj(31);v=d.decompress(data)+d.flush();need(d.eof and not d.unused_data and not d.unconsumed_tail,'single complete gzip member');return v
def recovery(r,fresh=None):
    offset=0;whole=hashlib.sha256();seen=set();need(r['parts'],'nonempty parts')
    with safe(r['path']).open('rb')as original:
        restored=safe(fresh).open('rb')if fresh else None
        try:
            for p in r['parts']:
                need(p['path']not in seen and p['raw_offset']==offset,'ordered unique contiguous parts');seen.add(p['path']);need(sha(p['path'])==p['gzip_sha256']and safe(p['path']).stat().st_size==p['gzip_bytes']<=10*1024**2,'compressed identity/size');v=decode(safe(p['path']).read_bytes());need(len(v)==p['raw_bytes']and hashlib.sha256(v).hexdigest()==p['raw_sha256'],'decompressed part identity');need(original.read(len(v))==v,'literal retained bytes');need(restored is None or restored.read(len(v))==v,'literal fresh restoration bytes');offset+=len(v);whole.update(v)
            need(not original.read(1)and (restored is None or not restored.read(1)),'no original/restored tail')
        finally:
            if restored:restored.close()
    need(offset==r['bytes']and whole.hexdigest()==r['sha256'],'whole identity');INPUTS[r['path']]=r['sha256'];return dict(path=r['path'],bytes=offset,sha256=whole.hexdigest(),gzip_parts=len(r['parts']),literal_retained_equal=True,literal_fresh_equal=fresh is not None)
def cli(script,argv):
    sha(script);tree=ast.parse(safe(script).read_text(encoding='utf8'));options=set();required=set();modes=set()
    for n in ast.walk(tree):
        if isinstance(n,(ast.Assign,ast.AnnAssign))and isinstance(n.value,ast.Dict):modes.update(k.value for k in n.value.keys if isinstance(k,ast.Constant)and isinstance(k.value,str))
        if isinstance(n,(ast.Assign,ast.AnnAssign))and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='dict':modes.update(k.arg for k in n.value.keywords if k.arg)
        if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='add_argument'and n.args and isinstance(n.args[0],ast.Constant):
            name=n.args[0].value;options.add(name)
            if any(k.arg=='required'and isinstance(k.value,ast.Constant)and k.value.value is True for k in n.keywords):required.add(name)
            for k in n.keywords:
                if name=='mode'and k.arg=='choices'and isinstance(k.value,(ast.List,ast.Tuple)):modes.update(ast.literal_eval(k.value))
    # Expand only literal string-list argument loops; never execute the checker.
    for loop in ast.walk(tree):
        if not isinstance(loop,ast.For)or not isinstance(loop.target,ast.Name)or not isinstance(loop.iter,(ast.List,ast.Tuple)):continue
        if not all(isinstance(v,ast.Constant)and type(v.value)is str for v in loop.iter.elts):continue
        values=[v.value for v in loop.iter.elts]
        for call in ast.walk(loop):
            if not isinstance(call,ast.Call)or not isinstance(call.func,ast.Attribute)or call.func.attr!='add_argument'or not call.args:continue
            def literal_string(e,value):
                if isinstance(e,ast.Constant)and type(e.value)is str:return e.value
                if isinstance(e,ast.Name)and e.id==loop.target.id:return value
                if isinstance(e,ast.BinOp)and isinstance(e.op,ast.Add):
                    left,right=literal_string(e.left,value),literal_string(e.right,value)
                    return left+right if left is not None and right is not None else None
                return None
            names={literal_string(call.args[0],v)for v in values}
            if None in names:continue
            options.update(names)
            if any(k.arg=='required'and isinstance(k.value,ast.Constant)and k.value.value is True for k in call.keywords):required.update(names)
    actual={x for x in argv if x.startswith('--')};need(actual<=options and required<=actual,'argparse flags '+script)
    if 'mode'in options:need(argv[0]in modes,'argparse mode '+script)
    for i,t in enumerate(argv):
        if t.endswith('-sha256')and t[:-7]in argv:need(sha(argv[argv.index(t[:-7])+1])==argv[i+1],'CLI exact hash companion')
    return dict(script=script,argv=argv,executed=False,static_argparse_match=True)
def script_index(cmd):
    need(type(cmd)is list and len(cmd)>=2 and all(type(t)is str for t in cmd),'command string array')
    need(Path(cmd[0]).name.lower()in ('python.exe','python'),'Python command interpreter')
    ix=2 if cmd[1]=='-B'else 1
    need(ix<len(cmd)and cmd[ix].startswith('acceleration/audit_')and cmd[ix].endswith('.py'),'explicit independent checker entry point')
    return ix

def replay():
    p=load(PLAN);need(p['status']=='TWENTYNINTH_REPLAY_COMMANDS_AUTHENTICATED_NOT_EXECUTED'and [r['name']for r in p['commands']]==NAMES,'eight exact nonexecuted commands');need(p['native_search_calls']==0 and len(p['skipped_checks'])==1,'explicit skip record');bind({p['command'][1]:p['source_sha256']});rows=[]
    for r in p['commands']:
        old=load(r['original_report']);need(INPUTS[r['original_report']]==r['original_report_sha256']and old['command']==r['original_command']and old['status']==r['expected_status'],'original command/report identity');cmd=r['original_command'];ix=script_index(cmd);script=cmd[ix];need(sha(script)==r['source_sha256'],'checker bytes');expected=[str(ROOT/'build/research-venv/Scripts/python.exe'),'-B',*cmd[ix:]];expected[expected.index('--out')+1]='build/research-local/wave29-replay/'+r['name'];need(r['replay_command']==expected,'only interpreter/out changed');rows.append(cli(script,cmd[ix+1:]))
    text=safe(GUIDE).read_text(encoding='utf8');commands=[]
    for line in text.splitlines():
        if not line.startswith('uv run '):continue
        ts=shlex.split(line);ix=ts.index('-B');commands.append(cli(ts[ix+1],ts[ix+2:]))
    need(len(commands)==1 and commands[0]['script']==HELPER,'exact one guide recovery CLI');need(commands[0]['argv']==['--manifest',MAN,'--manifest-sha256',PINS[MAN],'--receipt','build/research-local/wave29-recovery-receipt.json'],'guide exact recovery args')
    normalized=' '.join(text.split())
    for marker in ['LOCAL_ONLY','No fresh','eight','792','188','uniform','rank']:
        need(marker in normalized,'guide essential scope '+marker)
    return rows+commands
def main():
    ap=argparse.ArgumentParser()
    for name in ['manifest','guide','controls']:ap.add_argument('--'+name+'-sha256',required=True)
    for name in ['originals','raw-bytes','streams']:ap.add_argument('--expected-'+name,type=int,required=True)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();PINS.update({MAN:args.manifest_sha256,GUIDE:args.guide_sha256,CONTROLS:args.controls_sha256});out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bad=[]
    def reject(n,f):
        try:f()
        except(ValueError,zlib.error):bad.append(n);return
        raise ValueError('accepted corruption '+n)
    try:
        bind(PINS)
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:sha(p)
        need(args.expected_originals>0 and args.expected_raw_bytes>0 and args.expected_streams>0,'explicit positive recovery population')
        m=load(MAN);need(len(m['records'])==len({r['path']for r in m['records']})==args.expected_originals,'exact unique original population');need(sum(r['bytes']for r in m['records'])==args.expected_raw_bytes,'raw total')
        root=load(CONTROLS);bind(root['inputs_sha256']);bind(root['outputs_sha256']);rr=root['fresh_recovery_receipt'];bind({rr['path']:rr['sha256']});fresh=load(rr['path']);need(fresh['status']=='TWENTYNINTH_RAW_ARTIFACT_RECOVERY_PASS'and fresh['originals']==args.expected_originals and fresh['raw_bytes']==args.expected_raw_bytes and fresh['action_counts']=={'RESTORED_MISSING':args.expected_originals}and not fresh['mathematical_verification'],'complete fresh restoration receipt');need(len(root['controls'])==7 and all(c['rejected']and c['exit_code']==1 and c['no_success_receipt']for c in root['controls']),'root seven malformed controls');need(fresh['source_sha256']==PINS[HELPER],'actual restorer identity')
        outputs=[recovery(r,safe(fresh['destination'])/r['path'])for r in m['records']];need(sum(r['gzip_parts']for r in outputs)==args.expected_streams,'all complete gzip streams');clis=replay()
        probe=['python.exe','acceleration/audit_primary.py','--object-checker','acceleration/audit_secondary.py'];need(script_index(probe)==1 and script_index([probe[0],'-B',*probe[1:]])==2,'checker-valued argument positive regression');reject('unsupported Python invocation',lambda:script_index(['python.exe','-c','acceleration/audit_primary.py']));reject('nonchecker entry point',lambda:script_index(['python.exe','acceleration/native_wrong.py','--object-checker','acceleration/audit_secondary.py']));sample=m['records'][0];raw=safe(sample['parts'][0]['path']).read_bytes();reject('truncated gzip',lambda:decode(raw[:-1]));reject('extra gzip member',lambda:decode(raw+raw))
        for label,field,value in [('wrong offset','raw_offset',1),('wrong raw hash','raw_sha256','0'*64)]:
            r=copy.deepcopy(sample);r['parts'][0][field]=value;reject(label,lambda r=r:recovery(r))
        r=copy.deepcopy(sample);r['parts']=[];reject('missing part',lambda:recovery(r));reject('unknown flag',lambda:cli(HELPER,clis[-1]['argv']+['--invented']))
        save(out/'checked_records.json',dict(recovery=outputs,replay_commands=clis,original_root_controls=7,corruptions_rejected=bad,actual_math_replays=0,publication_reruns_explicitly_skipped=True,fresh_restored_tree_availability='LOCAL_ONLY'))
        need(time.monotonic()-start<120,'bounded allocation');s=dict(status='INDEPENDENT_TWENTYNINTH_RECOVERY_REPLAY_METADATA_PASS',created_at=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),raw_originals=args.expected_originals,raw_bytes=args.expected_raw_bytes,gzip_streams=args.expected_streams,actual_mathematical_replays=0,planned_mathematical_commands=8,guide_literal_profiles=188,guide_population=792,derived_unresolved=792-188,correction='V1 counted a checker-valued CLI argument as an entry point; v2 checks the Python script position. Unreached v1 guide marker 604 replaced by authenticated 188 of 792 with arithmetic remainder604.',guide_recovery_commands=1,controls_rejected=bad,inputs_sha256=INPUTS,outputs_sha256={key(out/'checked_records.json'):sha(out/'checked_records.json')},catalog_approval=False,scope='Literal gzip/original/fresh-copy identity and static replay ABI only. Original scientific audit records remain authoritative; no fresh mathematical replay.',elapsed_seconds=time.monotonic()-start);save(out/'summary.json',s);print(json.dumps(dict(status=s['status'],sha256=sha(out/'summary.json'),seconds=s['elapsed_seconds'])))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=INPUTS));raise
if __name__=='__main__':main()
