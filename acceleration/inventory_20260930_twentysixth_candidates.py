"""Read-only wave26 candidate selection/recovery inventory, not a catalog/stager."""
from pathlib import Path
from collections import defaultdict
import argparse, ast, hashlib, json, re, subprocess
import yaml

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_';I=B+'independent_review/'
HEAD='297202394cd8cb1e37f5a8832006644bd59763d6'
REGISTRATIONS=['acceleration/results/20260930_twentysixth_profile_registration', 'acceleration/results/20260930_twentysixth_upper_registration', 'acceleration/results/20260930_twentysixth_block_registration', 'acceleration/results/20260930_twentysixth_eight_reduction_registration', 'acceleration/results/20260930_twentysixth_census_algebra_registration', 'acceleration/results/20260930_twentysixth_psd_registration', 'acceleration/results/20260930_twentysixth_scalar_registration', 'acceleration/results/20260930_twentysixth_block_screen_registration']
REGISTRARS=['register_20260930_twentysixth_profile_claims.py', 'register_20260930_twentysixth_upper_claim.py', 'register_20260930_twentysixth_block_claim.py', 'register_20260930_twentysixth_eight_reduction_claim.py', 'register_20260930_twentysixth_census_algebra_claims_v2.py', 'register_20260930_twentysixth_psd_claim.py', 'register_20260930_twentysixth_scalar_claim.py', 'register_20260930_twentysixth_block_screen_claim.py']
EXTRA_DIRS=['acceleration/results/20260930_third_count_profile_setup', 'acceleration/results/20260930_first_third_proof_obstructions', 'acceleration/results/20260930_first_third_gram_lp', 'acceleration/results/20260930_first_third_block_singletons', 'acceleration/results/20260930_count_min_upper_inventory', 'acceleration/results/20260930_count_min_upper_inventory_controls_addendum', 'acceleration/results/20260930_eight_count_profile_lift_third_native_preparation', 'acceleration/results/20260930_twentysixth_census_algebra_registration_preparation']
EXTRA_FILES=['acceleration/results/20260930_resume/twentyfifth_publication_ci_completion.json', 'acceleration/register_20260930_twentysixth_census_algebra_claims.py', 'docs/RESULT_20260930_FIRST_THIRD_PROOF_OBSTRUCTIONS.md', 'docs/DESIGN_20260930_COUNT_MIN_UPPER_CNF.md', 'docs/DERIVATION_20260930_GF3_HOLLOW_RESIDUAL.md', 'docs/DERIVATION_20260930_COUNT_MIN_UPPER_ENVELOPE.md', 'docs/AUDIT_20260930_TRIPLICATE_COUNT_PSD.md', 'docs/AUDIT_20260930_THIRD_EIGHT_COUNT_PROFILE_UNSAT.md', 'docs/AUDIT_20260930_THIRD_COUNT_DIAGNOSTIC_PLAN.md', 'docs/AUDIT_20260930_SHARED_BLOCK_IDENTITY.md', 'docs/AUDIT_20260930_GF3_HOLLOW_RESIDUAL.md', 'docs/AUDIT_20260930_EXACT_EIGHT_SCALAR_SCREEN.md', 'docs/AUDIT_20260930_EXACT_EIGHT_PROFILE_PREFLIGHT.md', 'docs/AUDIT_20260930_EXACT_EIGHT_PROFILE_JOIN.md', 'docs/AUDIT_20260930_EXACT_EIGHT_BLOCK_SCREEN.md', 'docs/AUDIT_20260930_EIGHT_COUNT_PROFILE_LIFT_THIRD.md', 'docs/AUDIT_20260930_COUNT_MIN_UPPER_CNF.md']
FORBIDDEN_FILES={'PROMPT.md',I+'hadamard_oriented_unknown/process.stdout.log'}
FUTURE_PREFIXES=['acceleration/results/20260930_exact_eight_next_lift', 'acceleration/results/20260930_independent_review/exact_eight_next_lift', 'acceleration/results/20260930_triplicate_psd_kernel_options', 'acceleration/results/20260930_independent_review/triplicate_psd_kernel_options', 'acceleration/theory_20260930_exact_eight_next_lift', 'acceleration/native_20260930_exact_eight_next_lift', 'acceleration/audit_20260930_exact_eight_next_lift', 'acceleration/prepare_20260930_exact_eight_next_lift', 'acceleration/theory_20260930_triplicate_psd_kernel_options', 'acceleration/audit_20260930_triplicate_psd_kernel_options', 'docs/AUDIT_20260930_EXACT_EIGHT_NEXT_LIFT', 'docs/AUDIT_20260930_TRIPLICATE_PSD_KERNEL_OPTIONS']
PRIOR='acceleration/results/20260930_twentyfifth_artifact_packaging_v2/catalog.json'
LIMIT=10*1024**2

def forbidden(p):return p in FORBIDDEN_FILES or p.startswith('tools/') or any(p.startswith(x) for x in FUTURE_PREFIXES)
def safe(p):
    assert not forbidden(p),('forbidden before read/hash',p)
    q=(ROOT/p).resolve();assert q.is_relative_to(ROOT)
    assert q.name.lower() not in ['.env','.env.local','credentials','credentials.json','id_rsa','id_ed25519']
    assert q.suffix.lower() not in ['.pem','.key']
    return q
def sha(p):
    q=safe(p)
    with q.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(p):return json.loads(safe(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8') as stream:json.dump(x,stream,sort_keys=True,indent=2);stream.write('\n')
def root_directory(p):
    z=p.split('/')
    if p.startswith(I):return '/'.join(z[:4]) if len(z)>4 else None
    if p.startswith('acceleration/results/') and len(z)>3:return '/'.join(z[:3])
    return None
def references(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if isinstance(k,str) and isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) and k.startswith(('acceleration/','docs/','.github/','build/','external_conway99_research/')):yield k,v
            if isinstance(k,str) and k in ['path','raw_path','raw_original_path','cnf_path','model_path','scope_path','source_path'] and isinstance(v,str):
                hk={'raw_path':'raw_sha256','raw_original_path':'raw_sha256','cnf_path':'cnf_sha256','model_path':'model_sha256','scope_path':'scope_sha256','source_path':'source_sha256'}.get(k,'sha256')
                if re.fullmatch('[0-9a-f]{64}',str(obj.get(hk,''))) and v.startswith(('acceleration/','docs/')):yield v,obj[hk]
            yield from references(v)
    elif isinstance(obj,list):
        for v in obj:yield from references(v)
def package_records(obj,origin):
    if isinstance(obj,dict):
        p=obj.get('raw_path',obj.get('raw_original_path'));parts=obj.get('parts')
        if p and obj.get('gzip_path') and obj.get('gzip_sha256'):
            yield p,dict(manifest_path=origin,raw_sha256=obj.get('raw_sha256'),raw_bytes=obj.get('raw_bytes'),part_count=1,parts=[dict(path=obj['gzip_path'],sha256=obj['gzip_sha256'],bytes=obj.get('gzip_bytes'))],recovery_checked_by_inventory=False)
        if p and isinstance(parts,list) and parts:
            yield p,dict(manifest_path=origin,raw_sha256=obj.get('raw_sha256'),raw_bytes=obj.get('raw_bytes'),part_count=len(parts),parts=parts,recovery_checked_by_inventory=False)
        for v in obj.values():yield from package_records(v,origin)
    elif isinstance(obj,list):
        for v in obj:yield from package_records(v,origin)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(exist_ok=False,parents=True)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();assert head==HEAD
    public=set(subprocess.check_output(['git','ls-tree','-r','--name-only','-z',HEAD],cwd=ROOT).decode().split('\0'))
    prior=read(PRIOR);prior_known={x['path'] for x in prior['entries']}|set(prior.get('prior_recoverable_dependencies',[]));known=public|prior_known
    selected=set();directories=set();parsed={};expect=defaultdict(set);origins=defaultdict(set);pending=[];rejected=[];syntax_history=[];sources=[];chain=[]
    def add_file(p,origin):
        if forbidden(p):rejected.append(dict(path=p,origin=origin,read_or_hashed=False));return
        if p.startswith(('build/','external_conway99_research/')):return
        if not safe(p).is_file():pending.append(dict(path=p,reason='referenced file absent',origin=origin));return
        selected.add(p);origins[p].add(origin)
    def add_dir(d,origin):
        assert d not in ['acceleration/results',I.rstrip('/')]
        if forbidden(d):rejected.append(dict(path=d,origin=origin,read_or_hashed=False));return
        if not safe(d).is_dir():pending.append(dict(path=d,reason='declared directory absent',origin=origin));return
        if d in directories:return
        directories.add(d)
        for q in safe(d).rglob('*'):
            if q.is_file():add_file(q.relative_to(ROOT).as_posix(),origin)
    ledger_hash=sha('CLAIMS.yaml');assert ledger_hash=='8bcdad8f4b2e871b6c0bdf6ef72736033a8d84624af029e1b01c2951bc4b8146'
    ledger=yaml.safe_load(safe('CLAIMS.yaml').read_bytes());assert len(ledger['claims'])==278
    assert {state:sum(c['status']==state for c in ledger['claims']) for state in ['VERIFIED','CANDIDATE','REFUTED']}=={'VERIFIED':273,'CANDIDATE':3,'REFUTED':2}
    assert all(c['review_state']=='CLEAR' for c in ledger['claims'])
    previous=None
    for d,src in zip(REGISTRATIONS,REGISTRARS):
        s=read(d+'/summary.json');before=safe(d+'/CLAIMS.before.yaml').read_bytes();after=safe(d+'/CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest()==s['previous_ledger_sha256'];assert hashlib.sha256(after).hexdigest()==s['ledger_sha256']
        assert previous is None or before==previous;previous=after
        chain.append(dict(directory=d,summary_sha256=sha(d+'/summary.json'),before_sha256=s['previous_ledger_sha256'],after_sha256=s['ledger_sha256'],new_claim_ids=s['new_claim_ids']))
        add_dir(d,'exact eight-registration chain');add_file('acceleration/'+src,'registrar')
        for p,h in s['checked_input_bindings'].items():
            expect[p].add(h)
            if p not in known and not p.startswith(('build/','external_conway99_research/')):
                rd=root_directory(p)
                if rd:add_dir(rd,'registrar input '+d)
                else:add_file(p,'registrar input '+d)
    assert hashlib.sha256(previous).hexdigest()==ledger_hash
    assert sum(len(x['new_claim_ids']) for x in chain)==11
    for d in EXTRA_DIRS:add_dir(d,'parent-authorized completed extension/engineering lane')
    for p in EXTRA_FILES:add_file(p,'explicit supplemental source/doc')
    add_file(Path(__file__).resolve().relative_to(ROOT).as_posix(),'inventory source')
    done=set()
    while selected-done:
        p=min(selected-done);done.add(p);q=safe(p)
        if q.suffix=='.json':
            try:obj=read(p)
            except (UnicodeError,json.JSONDecodeError):continue
            parsed[p]=obj
            for name,h in references(obj):
                expect[name].add(h)
                if name in known or name.startswith(('build/','external_conway99_research/')):continue
                rd=root_directory(name)
                if rd:add_dir(rd,'bound reference from '+p)
                else:add_file(name,'bound reference from '+p)
        elif q.suffix=='.py':
            try:tree=ast.parse(q.read_bytes())
            except SyntaxError as exc:syntax_history.append(dict(path=p,line=exc.lineno,message=exc.msg));continue
            for node in ast.walk(tree):
                names=[x.name for x in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and node.module else []
                for name in names:
                    rel='acceleration/'+name.split('.')[0]+'.py'
                    if rel not in known and safe(rel).is_file():add_file(rel,'static repository import from '+p)
            sp=q.with_name(q.stem+'_spec.md').relative_to(ROOT).as_posix()
            if sp not in known and safe(sp).is_file():add_file(sp,'sibling source spec')
    packages=defaultdict(list)
    for p,obj in parsed.items():
        for raw,r in package_records(obj,p):packages[raw].append(r)
    entries=[];large=[];mismatches=[]
    for p in sorted(selected):
        q=safe(p);h=sha(p);size=q.stat().st_size
        if expect[p] and h not in expect[p]:mismatches.append(dict(path=p,actual=h,expected=sorted(expect[p])))
        entry=dict(path=p,sha256=h,bytes=size,already_public_at_baseline=p in public,origins=sorted(origins[p]))
        entries.append(entry)
        if size>LIMIT:
            rec=[r for r in packages[p] if r['raw_sha256']==h and r['raw_bytes']==size]
            gz=p+'.gz';gzip_sibling=safe(gz).is_file()
            large.append(dict(**entry,recovery_status='EXISTING_MANIFEST_METADATA' if rec else 'EXISTING_GZIP_SIBLING' if gzip_sibling else 'PACKAGE_OR_RECOVERY_NEEDED',package_records=rec,gzip_sibling=gz if gzip_sibling else None,inventory_has_recovered_bytes=False,publication_availability='LOCAL_ONLY_RAW'))
    result=dict(schema='WAVE26_CANDIDATE_SELECTION_RECOVERY_INVENTORY_V1',status='CANDIDATE_INVENTORY_ONLY_NOT_PUBLICATION_APPROVAL',baseline_HEAD=head,ledger_cutoff=dict(path='CLAIMS.yaml',sha256=ledger_hash,claims=278,VERIFIED=273,CANDIDATE=3,REFUTED=2,review_state='ALL_CLEAR'),source_sha256=sha(Path(__file__).resolve().relative_to(ROOT).as_posix()),prior_catalog=dict(path=PRIOR,sha256=sha(PRIOR)),registration_chain=chain,new_claim_ids=[x for r in chain for x in r['new_claim_ids']],explicit_directories=sorted(directories),explicit_files=sorted(p for p in selected if not any(p.startswith(d+'/') for d in directories)),entries=entries,selected_files=len(entries),selected_bytes=sum(x['bytes'] for x in entries),oversized_raw_or_payload_files=large,hash_mismatches=mismatches,pending=pending,rejected_future_or_protected_references=rejected,preserved_syntax_failure_sources=syntax_history,prior_public_or_recoverable_dependencies=sorted(set(expect)&known),research_payload_limit_bytes=LIMIT,metadata_allowance='Final catalog/stage/reference wrappers require separate explicit <=32MiB protocol and independent consistency gate.',limitations=['Inventory only: no independent mathematical promotion, source execution, raw restoration, checkpoint, stage/index or Git mutation.','All new raw files over10MiB must remain LOCAL_ONLY and have exact public recovery before publication.','Existing package metadata is authenticated against raw hash/size here but gzip contents are not replayed by this inventory.','Final publication still requires the parent checkpoint, replay guide, exact catalog and independent consistency gate.','Private protected file, PROMPT and tools submodule are never read or hashed.'],excluded_wave27_prefixes=FUTURE_PREFIXES)
    save(out/'inventory.json',result)
    print(json.dumps(dict(inventory_sha256=sha((out/'inventory.json').relative_to(ROOT).as_posix()),selected=len(entries),directories=len(directories),large=len(large),needs_package=sum(x['recovery_status']=='PACKAGE_OR_RECOVERY_NEEDED' for x in large),mismatches=len(mismatches),pending=len(pending),rejected=len(rejected))))
if __name__=='__main__':main()
