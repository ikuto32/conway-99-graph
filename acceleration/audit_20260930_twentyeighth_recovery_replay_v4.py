"""Read-only independent gzip/original comparison and replay ABI audit."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,copy,hashlib,json,re,shlex,sys,time,traceback,zlib
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
MAN=B+'twentyeighth_raw_recovery/manifest.json';GUIDE='docs/REPRODUCING_20260930_TWENTYEIGHTH_WAVE.md';PLAN=B+'resume/twentyeighth_replay_plan.json';HELPER='acceleration/recover_20260930_twentyeighth_raw_artifacts.py';CONTROLS=B+'twentyeighth_recovery_controls/summary.json'
PINS={MAN:'33b00a791e57a732a27d18061c52f1ac6b3e71d964d9bf03c1e986ae12c82c89',GUIDE:'95b76d5f21e15d90ebc036a36e7f47eabaec91c548015a42ebf0f56d87ecd779',PLAN:'135c47ef31dd275f84dbc6c5d115a93d752780900f5e3f116f7a2822854f4920',HELPER:'f503fa64f21771619c6756c64710e0a06185f5a8b433b0a9653954e33b014256',CONTROLS:'770fb50844c65d5e6400ad406b00b3dfe7ac5d82e2aae7caf2c49aec2259da49'}
PINS.update({'acceleration/audit_20260930_twentyeighth_recovery_replay.py':'5510827b8f00c01c2603eb7b39ae04b1c67d51cb8a6c8e0fb26e12080258b50e','acceleration/audit_20260930_twentyeighth_recovery_replay_spec.md':'15d5852dd4625d769b7dc3b92270933c359380b0493f42c9fc1733260c10305d',I+'twentyeighth_recovery_replay/failure.json':'aee563abe41a8783ed7feed20ddd10b553f8ac5bf139a08e8b6b95d408ec2654'})
PINS.update({'acceleration/audit_20260930_twentyeighth_recovery_replay_v2.py':'4f0dbb300633c5bc42a3125a4fb223cefb2a5a8ad908c33d142c596981897cf2','acceleration/audit_20260930_twentyeighth_recovery_replay_v2_spec.md':'b36951e90e8776e5655f0c9cbafda98f2957ef26c51c0e76a7153670e45f904d',I+'twentyeighth_recovery_replay_v2/failure.json':'b732be0efd21d9e623bfd44c2d018f509a354649c65a04673ddce50972edae6f'})
PINS.update({'acceleration/audit_20260930_twentyeighth_recovery_replay_v3.py':'94d1b929cdd3648d093e92a9ef8ea3e6642f4d505e3f2130033a9c8a6c09c8e6','acceleration/audit_20260930_twentyeighth_recovery_replay_v3_spec.md':'db55a86758ee0f712b6fa021053055f97b319fc4030408fabcac71d1afc76909',I+'twentyeighth_recovery_replay_v3/failure.json':'7593e1f2414b69866abb01877121dda0597e70bc247051dd5b90c91d1d43b5bb'})
NAMES=['exact_eight_next32_cnfs','exact_eight_next32_object_calibration','exact_eight_next32_proofs','exact_eight_first12_union_v2','exact_eight_sizeclass16_cnfs_v2','exact_eight_sizeclass16_object_calibration','exact_eight_sizeclass16_proofs','exact_eight_kernel_redundancy'];INPUTS={}
def need(x,m):
    if not x:raise ValueError(m)
def safe(p):
    q=Path(p);q=q.resolve()if q.is_absolute()else(ROOT/q).resolve();need(q.is_relative_to(ROOT),'path containment');r=q.relative_to(ROOT).as_posix();need(not r.startswith('tools/')and q.name!='PROMPT.md'and r!=I+'hadamard_oriented_unknown/process.stdout.log','protected path');return q
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
def replay():
    p=load(PLAN);need(p['status']=='TWENTYEIGHTH_REPLAY_COMMANDS_AUTHENTICATED_NOT_EXECUTED'and [r['name']for r in p['commands']]==NAMES,'eight exact nonexecuted commands');need(p['native_search_calls']==0 and len(p['skipped_checks'])==1,'explicit skip record');bind({p['command'][1]:p['source_sha256']});rows=[]
    for r in p['commands']:
        old=load(r['original_report']);need(INPUTS[r['original_report']]==r['original_report_sha256']and old['command']==r['original_command']and old['status']==r['expected_status'],'original command/report identity');cmd=r['original_command'];indices=[i for i,t in enumerate(cmd)if t.startswith('acceleration/audit_')and t.endswith('.py')];need(len(indices)==1,'one independent checker');ix=indices[0];script=cmd[ix];need(sha(script)==r['source_sha256'],'checker bytes');expected=[str(ROOT/'build/research-venv/Scripts/python.exe'),'-B',*cmd[ix:]];expected[expected.index('--out')+1]='build/research-local/wave28-replay/'+r['name'];need(r['replay_command']==expected,'only interpreter/out changed');rows.append(cli(script,cmd[ix+1:]))
    text=safe(GUIDE).read_text(encoding='utf8');commands=[]
    for line in text.splitlines():
        if not line.startswith('uv run '):continue
        ts=shlex.split(line);ix=ts.index('-B');commands.append(cli(ts[ix+1],ts[ix+2:]))
    need(len(commands)==1 and commands[0]['script']==HELPER,'exact one guide recovery CLI');need(commands[0]['argv']==['--manifest',MAN,'--manifest-sha256',PINS[MAN],'--receipt','build/research-local/wave28-recovery-receipt.json'],'guide exact recovery args')
    normalized=' '.join(text.split())
    for x in ['Forty-seven oversized raw models','524,689,195','LOCAL_ONLY','eight exact original commands','No fresh repeat of the eight already successful mathematical audits was run','It does not expand the later48 literal exclusions to their fibre images','All1,687,356 initial options','replacement launcher belongs to the following wave','All48 new complete proof files fit the10MiB individual publication']:
        need(x in normalized,'guide scope '+x)
    return rows+commands
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bad=[]
    def reject(n,f):
        try:f()
        except(ValueError,zlib.error):bad.append(n);return
        raise ValueError('accepted corruption '+n)
    try:
        bind(PINS)
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:sha(p)
        m=load(MAN);need(len(m['records'])==len({r['path']for r in m['records']})==47,'47 unique records');need(sum(r['bytes']for r in m['records'])==524689195,'raw total')
        root=load(CONTROLS);bind(root['inputs_sha256']);bind(root['outputs_sha256']);rr=root['fresh_recovery_receipt'];bind({rr['path']:rr['sha256']});fresh=load(rr['path']);need(fresh['status']=='TWENTYEIGHTH_RAW_ARTIFACT_RECOVERY_PASS'and fresh['originals']==47 and fresh['raw_bytes']==524689195 and fresh['action_counts']=={'RESTORED_MISSING':47}and not fresh['mathematical_verification'],'complete fresh restoration receipt');need(len(root['controls'])==7 and all(c['rejected']and c['exit_code']==1 and c['no_success_receipt']for c in root['controls']),'root seven malformed controls');need(fresh['source_sha256']==PINS[HELPER],'actual restorer identity')
        outputs=[recovery(r,safe(fresh['destination'])/r['path'])for r in m['records']];need(sum(r['gzip_parts']for r in outputs)==47,'47 complete gzip streams');clis=replay()
        sample=m['records'][0];raw=safe(sample['parts'][0]['path']).read_bytes();reject('truncated gzip',lambda:decode(raw[:-1]));reject('extra gzip member',lambda:decode(raw+raw))
        for label,field,value in [('wrong offset','raw_offset',1),('wrong raw hash','raw_sha256','0'*64)]:
            r=copy.deepcopy(sample);r['parts'][0][field]=value;reject(label,lambda r=r:recovery(r))
        r=copy.deepcopy(sample);r['parts']=[];reject('missing part',lambda:recovery(r));reject('unknown flag',lambda:cli(HELPER,clis[-1]['argv']+['--invented']))
        save(out/'checked_records.json',dict(recovery=outputs,replay_commands=clis,original_root_controls=7,corruptions_rejected=bad,actual_math_replays=0,publication_reruns_explicitly_skipped=True,fresh_restored_tree_availability='LOCAL_ONLY'))
        need(time.monotonic()-start<120,'bounded allocation');s=dict(status='INDEPENDENT_TWENTYEIGHTH_RECOVERY_REPLAY_METADATA_PASS',created_at=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),raw_originals=47,raw_bytes=524689195,gzip_streams=47,actual_mathematical_replays=0,planned_mathematical_commands=8,guide_recovery_commands=1,controls_rejected=bad,inputs_sha256=INPUTS,outputs_sha256={key(out/'checked_records.json'):sha(out/'checked_records.json')},catalog_approval=False,scope='Literal gzip/original/fresh-copy identity and static replay ABI only. Original scientific audit records remain authoritative; no fresh mathematical replay.',elapsed_seconds=time.monotonic()-start);save(out/'summary.json',s);print(json.dumps(dict(status=s['status'],sha256=sha(out/'summary.json'),seconds=s['elapsed_seconds'])))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=INPUTS));raise
if __name__=='__main__':main()
