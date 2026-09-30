"""One-shot, source-only next-lift native wrapper preparation; no imports of runtime code."""
import ast,difflib,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'acceleration/native_20260930_eight_count_profile_lift_third.py'
NEW=ROOT/'acceleration/native_20260930_exact_eight_next_lift.py'
SPEC=NEW.with_name(NEW.stem+'_spec.md')
OUT=ROOT/'acceleration/results/20260930_exact_eight_next_lift_native_preparation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
    assert sha(OLD)=='e73f44028b13dbeac8710f98826439b22a30504956f3a6a4d127d35469928a59'
    assert not NEW.exists() and not OUT.exists() and SPEC.exists()
    text=OLD.read_text();changes=[]
    def replace(old,new,n=None):
        nonlocal text
        count=text.count(old);assert count>0 and(n is None or count==n),(old,count,n)
        text=text.replace(old,new);changes.append(dict(old=old,new=new,occurrences=count))
    replace('third literal eight-exception count profile','next selected literal exact-eight count profile',1)
    replace('eight_count_profile_lift_third','exact_eight_next_lift')
    replace('INDEPENDENT_THIRD_LITERAL_EIGHT_COUNT_PROFILE_ENCODING_PASS','INDEPENDENT_EXACT_EIGHT_NEXT_LITERAL_GRAM_ENCODING_PASS',1)
    replace('INDEPENDENT_THIRD_LITERAL_EIGHT_COUNT_PROFILE_OBJECT_CALIBRATION_PASS','INDEPENDENT_EXACT_EIGHT_NEXT_LITERAL_GRAM_OBJECT_CALIBRATION_PASS',1)
    for old,new in [
      ('0f82ec4239be19f6ba3311b26a5d0f10b093c4aee0aff682dc68debe55d160a9','6fecea814c533a081ee0292087b1bf4cccb9cb132ea232b907acd227ba610962'),
      ('0a821d08532ece7d99bc5917a61af8dd0338379ab73a83c3687cbdf5ea480634','91084af7baa7041e6f66ce9cdcfb00b72eebce07389a5d0e160209457438109d'),
      ('4f5eedcd74eb2c5d44a6955f80b9d8cfb8899949bcfeb31a5aafd56adc8260e2','d8a05714c5297495c2a2d28835bd0c41de90a956162f998158dea39f78cf04b1'),
      ('03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e','7997ff6bb2ae409cade1094e0a3d16ef82f17051a2fbfa2a96412342e4bdc446'),
      ('69eb50b0cb780b58df71283195a84fcf50a5b9ea627d3e879aa5131abc4404b6','6cad750feb66e73dbeec98d818ca1a15b049105167c4cacce70e3a1071bd17dc'),
      ('59cf7df0013dc62b79812b784a15a7e9b42ee101510f5a94db0dcfa998812767','473b4774650f43fbd51dc9387f006bf1b9626e70acfd80e4a3ab45c25ac04dff'),
      ('b6386f66bb570df301a766ce4e59f389850e3adcbf11cb959c614fcd0a5b221f','ef0f6cbc9688db47eea55ddcb97de0fca063b6eb3361827c28426926ccfe53fd'),
      ('3bc6ebf9444e7a2f15af1ac85c6164119333244ced5d6dbe83a6c6b367e533d5','40c141a31c059e2d413e99e8f20ccb8d149b25599139a64258c5259d9b649cb9'),
      ('3755c635bcfc602d85a981f179c9b3bb4760362d843c15251213e2458146141c','eecca94d25028ffe61d728165fcad57180fb1e7537a6ff0e841cb0da023681cc')]:replace(old,new,1)
    replace("PINS.update({ROOT/'acceleration/native_20260930_eight_count_profile_lift_second.py':'35ab36f43c526ea3a787ee11c2cf07113c931ac79244a9d14766c178360c24ef',ROOT/'acceleration/native_20260930_eight_count_profile_lift_second_spec.md':'7274f084995451fb495fccc96e4dda2e905eb2f7646ff4dbfcd572c042e48c88'})", "PINS.update({ROOT/'acceleration/native_20260930_eight_count_profile_lift_third.py':'e73f44028b13dbeac8710f98826439b22a30504956f3a6a4d127d35469928a59',ROOT/'acceleration/native_20260930_eight_count_profile_lift_third_spec.md':'b566790256cacc66758dd51c5eee1f1846c9499d0d5c1a1eb9a92df467fcf94d'})\nSELECTION=DATA/'selection.json';BLOCK_GATE=B/'20260930_independent_review/exact_eight_block_screen/summary.json';BLOCK_SUMMARY=B/'20260930_exact_eight_block_screen/summary.json'\nENCODING_GATE=B/'20260930_independent_review/exact_eight_next_lift/summary.json';ENCODING_SHA='395a7396168bd0ec5faf1413f12b14d6e630d3c961723d1b68f0d6c07c96402e'\nPINS.update({SELECTION:'dbc6460fabee748ba25a6a1f801d2fe45300f9a440ebeba2b410b00b1c920590',BLOCK_GATE:'6c21ef6951f72fbeabab8be0a649f178ca8b17eb91edcc35c3291d6790f6256a',BLOCK_SUMMARY:'9fbfde4c8d1f1b4fc0aee7b89783a76dcd71c48adf75dbe6c32f116438634edb',ENCODING_GATE:ENCODING_SHA})",1)
    replace("scope['selected_profile_id']=='count_master_third_native_sat_after_six_scalar_cuts'", "scope['selected_profile_id']=='exact_eight_first_block_survivor_outside_three_historical_orbits'",1)
    replace("    scope=h.read(SCOPE);profile=h.read(PROFILE);model=h.read(MODEL)","    h.require(args.encoding_gate.resolve()==ENCODING_GATE.resolve() and args.encoding_gate_sha256==ENCODING_SHA,'exact approved encoding gate')\n    scope=h.read(SCOPE);profile=h.read(PROFILE);model=h.read(MODEL)\n    h.require(profile['selected_subset_index']==0 and scope['selected_full_count_sha256']==profile['full_count_profile_sha256']=='a2a3d60e21811916cde9269f08221000990e8235629bcc67d880ae472b6a18f9','selected complete count profile')",1)
    replace("scope['exceptional_groups']==[1,3,5,11,13,15,18,19]", "scope['exceptional_groups']==[0,1,2,5,9,10,12,14]",1)
    replace('direct+=[initial,producer.PROFILE,producer.GATE]','direct+=[initial,SELECTION,BLOCK_GATE,BLOCK_SUMMARY]',1)
    replace('THIRD_EIGHT_COUNT_PROFILE_NATIVE','EXACT_EIGHT_NEXT_LITERAL_GRAM_NATIVE')
    replace('conway99-third-eight-count-profile-','conway99-exact-eight-next-lift-')
    replace("'Candidate eight-count-profile decoder", "'Candidate selected exact-eight-profile decoder",1)
    replace('EIGHT_COUNT_PROFILE_SAT_RAW_UNCHECKED','EXACT_EIGHT_NEXT_LITERAL_GRAM_SAT_RAW_UNCHECKED',1)
    replace('EIGHT_COUNT_PROFILE_UNSAT_TRACE_UNCHECKED','EXACT_EIGHT_NEXT_LITERAL_GRAM_UNSAT_TRACE_UNCHECKED',1)
    ast.parse(text,filename=str(NEW));compile(text,str(NEW),'exec')
    assert 'producer.PROFILE'not in text and 'producer.GATE'not in text and 'preserved=True'not in text
    assert "future_availability='UNKNOWN'"in text and "h.run_record(command,folder/'solver',70)"in text
    assert "e.command(60,[h.linux(h.NATIVE),'--no-binary','-c','1000000',h.linux(CNF),proof])"in text
    closure={NEW,SPEC,ROOT/'acceleration/theory_20260930_exact_eight_next_lift_spec.md'};todo=[NEW]
    while todo:
        p=todo.pop();tree=ast.parse(text if p==NEW else p.read_text())
        for n in ast.walk(tree):
            mods=[a.name for a in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.module else[]
            for mod in mods:
                q=ROOT/'acceleration'/f'{mod}.py'
                if q.exists()and q not in closure:closure.add(q);todo.append(q)
    closure.add(ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_cnf.py')
    assert len([p for p in closure if p.suffix=='.py'])==6
    NEW.write_text(text,encoding='utf8',newline='\n');OUT.mkdir()
    (OUT/'source_delta.patch').write_text(''.join(difflib.unified_diff(OLD.read_text().splitlines(True),text.splitlines(True),fromfile=key(OLD),tofile=key(NEW))),encoding='utf8',newline='\n')
    save(OUT/'replacements.json',changes)
    pins={key(p):sha(p)for p in closure|{OLD,OLD.with_name(OLD.stem+'_spec.md'),Path(__file__)}}
    for name in ['summary.json','instance.cnf','model.json','scope.json','initial_domains.json','selected_profile.json','selection.json']:
        p=ROOT/'acceleration/results/20260930_exact_eight_next_lift'/name;pins[key(p)]=sha(p)
    for folder in ['exact_eight_next_lift','exact_eight_block_screen']:
        p=ROOT/f'acceleration/results/20260930_independent_review/{folder}/summary.json';pins[key(p)]=sha(p)
    save(OUT/'summary.json',dict(status='EXACT_EIGHT_NEXT_LIFT_NATIVE_SOURCE_PREPARATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,native_source_closure=sorted(map(key,closure)),source_delta_sha256=sha(OUT/'source_delta.patch'),replacements_sha256=sha(OUT/'replacements.json'),controls=['Frozen predecessor authenticated','Every exact replacement multiplicity checked','AST and compile-only syntax validation','Six runtime Python sources and two specs statically enumerated','No dynamic producer.PROFILE/GATE None reference','Exact60s/1M/70s guards retained','Workspace future availability UNKNOWN retained'],native_imports=0,native_calls=0,preflight_calls=0,independent_approval=False,scope='Source-only engineering preparation; no object calibration or native outcome asserted.'))
    print(json.dumps(dict(source_sha256=sha(NEW),spec_sha256=sha(SPEC),summary_sha256=sha(OUT/'summary.json'),closure=sorted(map(key,closure)))))
if __name__=='__main__':main()
