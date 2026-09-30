"""Independent completed-interval census review using exact packed integer coefficients."""
import argparse, gzip, hashlib, importlib.util, io, json, platform, subprocess, sys, time
from collections import Counter
from datetime import datetime,timezone
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
D=B/'20260930_hadamard_four_group_joint_v2'
SCREEN=B/'20260930_hadamard_four_group_local_screen'
GATE=B/'20260930_independent_review/hadamard_four_group_local_screen/summary.json'
OBJECT=ROOT/'acceleration/audit_20260930_four_group_partial_object.py'
OBJECT_GATE=B/'20260930_independent_review/four_group_partial12_object/summary.json'
PINS={D/'summary.json':'6c50233086be7bc982fb032e36b809fc77e1325d1c734638f4daf982185f17f7',GATE:'ff30d47b012d1661182f1cba066425dd9d5aaccad3754cad4d526b7477725c67',OBJECT_GATE:'8a48a303d687f48c3a84b2427b303a16a32f16e336677e194c4b7b19eafb5fe1'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def write(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def idx(bits):
    return [i for i in range(bits.bit_length()) if bits>>i&1]
def pack(values):return sum(v<<(6*i) for i,v in enumerate(values))
def ceiling(target):
    need(all(0<=v<=31 for v in target),'target range')
    return pack([31-v for v in target]),pack([32]*len(target))
def bounded(value,offset,tag):return (value+offset)&tag==0
def sparse(columns):
    a=Counter()
    for col in columns:
        for pair in combinations_with_replacement(sorted(col),2):a[pair]+=1
    return a
def controls(obj):
    count=0
    for target in range(19):
        off,tag=ceiling([target,target])
        for values in product(range(4),repeat=4):
            x=sum(values);v=pack([x,12-x]);need(bounded(v,off,tag)==(x<=target and 12-x<=target),'all exact two-lane coefficient cases');count+=1
    fixture=read(B/'20260930_srg243_residual_fixture/triangle_blocks.json')['factor60x180']
    target=[sum(fixture[i][d]*fixture[j][d] for d in range(180)) for i,j in combinations_with_replacement(range(60),2)]
    off,tag=ceiling(target);cols=[{i for i in range(60) if fixture[i][d]} for d in range(24)];pairs=list(combinations_with_replacement(range(60),2));parts=[]
    for n in range(8):
        c=sparse(cols[3*n:3*n+3]);parts.append(pack([c[p] for p in pairs]))
    for ids in combinations(range(8),4):need(bounded(sum(parts[i] for i in ids),off,tag),'genuine243 joint positive')
    off,tag=ceiling([2]);need(bounded(2,off,tag) and not bounded(3,off,tag),'third use of target2 rejected')
    off,tag=ceiling([1]);need(not bounded(2,off,tag),'second use of target1 rejected')
    return dict(exhaustive_two_lane_cases=count,genuine243_four_group_positives=70,target_overflow_controls=2)
def verify_records(path,expected,domains,outer,width2,width3):
    remaining=set(expected);last=None;count=0
    with gzip.open(path,'rt',encoding='utf-8') as f:
        for line in f:
            r=json.loads(line);need(set(r)=={'option_indices','local_survivor_indices'},'raw tuple schema')
            v=r['option_indices'];need(len(v)==4 and all(type(x) is int for x in v) and v[0]==outer,'tuple outer interval')
            need(all(0<=x<len(domain) for x,domain in zip(v,domains,strict=True)),'tuple ranges')
            need(r['local_survivor_indices']==[domain[x] for x,domain in zip(v,domains,strict=True)],'literal catalogue IDs')
            code=(v[1]*width2+v[2])*width3+v[3]
            need(code in remaining,'unexpected or duplicate saved tuple');remaining.remove(code)
            need(last is None or tuple(v)>last,'strict saved lexicographic order');last=tuple(v);count+=1
    need(not remaining,'all independent survivors saved')
    return count
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        p=p.resolve()
        if key(p) in pins:
            need(h is None or pins[key(p)]==h,'consistent repeated pin');return
        v=sha(p);need(h is None or h==v,'pin '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        og=read(OBJECT_GATE);pin(OBJECT,og['inputs_sha256'][key(OBJECT)])
        spec=importlib.util.spec_from_file_location('independent_partial_object',OBJECT);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
        s=read(D/'summary.json');sg=read(GATE);need(sg['status']=='INDEPENDENT_HADAMARD_FOUR_GROUP_LOCAL_PROFILE_SCREEN_PASS','independent table gate')
        for p,h in s['inputs_sha256'].items():pin(ROOT/p,h)
        for p in [D/'manifest.json',D/'controls.json']:pin(p)
        K,groups,local=obj.context();words=local['words'];triples=local['survivors'];pairs=list(combinations_with_replacement(range(36),2));off,tag=ceiling([K[i][j] for i,j in pairs])
        calibration=controls(obj);write(out/'controls.json',calibration)
        checkpoints={}
        for entry in s['checkpoints']:
            p=ROOT/entry['path'];pin(p,entry['sha256']);cp=read(p);ck=(cp['case'],cp['outer_index']);need(ck not in checkpoints,'unique completed interval');checkpoints[ck]=cp
            for raw in cp['outputs']:pin(ROOT/raw['path'],raw['sha256'])
        screen=read(SCREEN/'summary.json');todo=[r for r in screen['case_summaries'] if not r['gram_caps_ac_empty']];need(len(todo)==96 and s['selected_profiles']==96,'selected profile population')
        total_population=sum(__import__('math').prod(r['final_sizes']) for r in todo);need(total_population==s['cartesian_population']==145590048,'frozen Cartesian population')
        totals=Counter();results=[];witnesses=[];seen=set();cache={}
        for index,reported in enumerate(tqdm(s['case_results'],desc='Independent joint interval census',mininterval=1)):
            ci=reported['case'];need(ci==todo[index]['case'],'fixed declared case order')
            casepath=SCREEN/f'case_{ci:03d}.json';pin(casepath,sg['inputs_sha256'][key(casepath)]);case=read(casepath)
            caseout=D/f'case_{ci:03d}';pin(caseout/'summary.json');need(read(caseout/'summary.json')==reported,'case summary identity')
            domains=case['local_survivor_indices'];masks=list(map(lambda x:int(x,16),case['gram_caps_ac']['final_masks']));tables={}
            for p in case['pairs']:
                left,right=p['sides'];forward=list(map(lambda x:int(x,16),p['both_forward_masks']));back=[sum(1<<i for i,row in enumerate(forward) if row>>j&1) for j in range(len(domains[right]))]
                tables[left,right]=forward;tables[right,left]=back
            features=[]
            for side,g in enumerate(case['groups']):
                values=[]
                for li in domains[side]:
                    ck=(g,li)
                    if ck not in cache:
                        columns=[{12*words[w][pos]+a for pos,a in enumerate(groups[g])} for w in triples[li]];counts=sparse(columns);cache[ck]=pack([counts[p] for p in pairs])
                    values.append(cache[ck])
                features.append(values)
            # Independent meet-in-the-middle join: form the (2,3) relation first,
            # then join the (0,1) pair through all four cross relations.
            right_pairs=[(k,l,features[2][k]+features[3][l]) for k in idx(masks[2]) for l in idx(masks[3]&tables[2,3][k])]
            casecounts=Counter();outer=reported['outer_done'];complete=outer==idx(masks[0])
            need(outer==idx(masks[0])[:len(outer)] and bool(reported['complete'])==complete,'exact prefix/completeness')
            need(complete or index==len(s['case_results'])-1,'only last attempted case may be partial')
            need(reported['status']==('COMPLETE' if complete else 'UNKNOWN_RESOURCE_LIMIT'),'status scope')
            need(reported['cartesian_population']==__import__('math').prod(m.bit_count() for m in masks),'case Cartesian universe')
            first=None
            for i in outer:
                cp=checkpoints[ci,i];seen.add((ci,i));need(cp['source_case_sha256']==pins[key(casepath)],'checkpoint scope hash')
                valid_triples=set()
                for j in idx(masks[1]&tables[0,1][i]):
                    for k in idx(masks[2]&tables[0,2][i]&tables[1,2][j]):
                        if bounded(features[0][i]+features[1][j]+features[2][k],off,tag):valid_triples.add((j,k))
                expected=set();cliques=0
                for k,l,packed_right in right_pairs:
                    if not(tables[0,2][i]>>k&1 and tables[0,3][i]>>l&1):continue
                    js=masks[1]&tables[0,1][i]&tables[2,1][k]&tables[3,1][l]
                    for j in idx(js):
                        if (j,k) not in valid_triples:continue
                        cliques+=1
                        if bounded(features[0][i]+features[1][j]+packed_right,off,tag):expected.add((j*len(domains[2])+k)*len(domains[3])+l)
                chunk=caseout/f'outer_{i:03d}.jsonl.gz';need(key(chunk) in pins,'checkpoint binds compressed tuple artifact')
                actual=verify_records(chunk,expected,domains,i,len(domains[2]),len(domains[3]))
                need(cp['compatible_triples']==len(valid_triples) and cp['four_clique_candidates']==cliques and cp['survivors']==actual,'all independently derived checkpoint counters')
                casecounts.update(compatible_triples=len(valid_triples),four_clique_candidates=cliques,surviving_partial_objects=actual,completed_outer_choices=1)
                if first is None and expected:
                    code=min(expected);l=code%len(domains[3]);code//=len(domains[3]);k=code%len(domains[2]);j=code//len(domains[2]);first=[i,j,k,l]
            for field in ['compatible_triples','four_clique_candidates','surviving_partial_objects']:need(casecounts[field]==reported[field],'complete saved-interval count '+field)
            witnesspath=caseout/'first_witness.json';need(first is not None and key(witnesspath) in pins,'nonempty witness checkpoint binding')
            w=read(witnesspath);need(w['chosen']==first,'first saved lexicographic witness');wcheck=obj.check(w,case,K,groups,local);witnesses.append(wcheck)
            results.append(dict(case=ci,complete=complete,outer_done=outer,counts=dict(casecounts),witness_sha256=pins[key(witnesspath)],remaining_case_scope='Complete AC Cartesian domain' if complete else 'Only saved outer-choice prefix; unvisited choices UNKNOWN'))
            totals.update(casecounts)
        need(seen==set(checkpoints),'every and only saved checkpoint audited')
        need(len(results)==36 and sum(r['complete'] for r in results)==35 and s['unattempted_profiles']==60 and s['completed_profiles']==35,'stage boundaries')
        need(totals['surviving_partial_objects']==7335060==s['surviving_partial_objects'] and s['profiles_with_partial_object']==36 and s['complete_empty_profiles']==0,'aggregate counts')
        need(s['status']=='CANDIDATE_JOINT_FOUR_GROUP_PARTIAL' and s['native_solver_calls']==0,'producer outcome/solver count')
        # Preserve the stopped-v1 control failure as such; it precedes research loop.
        failure=B/'20260930_hadamard_four_group_joint/failure.json';need('243' in read(failure)['error'],'preserved genuine243 control failure')
        rejected=[]
        control_dir=out/'corrupted_controls';control_dir.mkdir()
        small=control_dir/'small.jsonl.gz'
        with gzip.open(small,'wt',encoding='utf-8') as f:f.write(json.dumps(dict(option_indices=[0,0,0,0],local_survivor_indices=[7,8,9,10]))+'\n')
        need(verify_records(small,{0},[[7],[8],[9],[10]],0,1,1)==1,'small positive raw codec')
        def reject(name,fn):
            try:fn()
            except(ValueError,KeyError,IndexError,TypeError,gzip.BadGzipFile,EOFError):rejected.append(name)
            else:raise ValueError('accepted corruption '+name)
        reject('unexpected_tuple',lambda:verify_records(small,set(),[[7],[8],[9],[10]],0,1,1))
        reject('missing_tuple',lambda:verify_records(small,{0,1},[[7],[8],[9],[10]],0,1,1))
        reject('wrong_catalogue_id',lambda:verify_records(small,{0},[[6],[8],[9],[10]],0,1,1))
        reject('wrong_outer_interval',lambda:verify_records(small,{0},[[7],[8],[9],[10]],1,1,1))
        duplicate=control_dir/'duplicate.jsonl.gz'
        with gzip.open(duplicate,'wt',encoding='utf-8') as f:
            for _ in range(2):f.write(json.dumps(dict(option_indices=[0,0,0,0],local_survivor_indices=[7,8,9,10]))+'\n')
        reject('duplicate_tuple',lambda:verify_records(duplicate,{0},[[7],[8],[9],[10]],0,1,1))
        broken=control_dir/'broken.jsonl.gz';broken.write_bytes(small.read_bytes()[:-8]);reject('truncated_gzip',lambda:verify_records(broken,{0},[[7],[8],[9],[10]],0,1,1))
        write(out/'corruption_controls.json',dict(rejected=rejected,intentionally_corrupt_artifacts={key(p):sha(p) for p in control_dir.iterdir()}))
        write(out/'independent_counts.json',dict(records=results,totals=dict(totals)))
        write(out/'independent_first_objects.json',dict(records=witnesses,scope='36 separate partial twelve-column constructions, no remaining48-column factor.'))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_FOUR_GROUP_JOINT.md']:pin(p)
        ts=datetime.now(timezone.utc).isoformat();write(out/'manifest.json',dict(timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start,native_solver_calls=0))
        binding=dict(id='C-FIXED-HADAMARD-FOUR-EXCEPTION-PARTIAL12-CENSUS',revision=1,kind='construction',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='In the saved fixed-support exactly-four-exception Gram-plus-column-cap screen, every tuple in the completed intervals of cases0 through35 is independently reconstructed and checked: cases0 through34 exhaust their AC domains, case35 exhausts only its saved first3 outer choices, and the 1263 intervals contain exactly7335060 twelve-column partial objects. Each of the36 attempted cases has an independently checked raw partial witness. The remaining60 selected profiles were not attempted.',scope='A complete finite census only for the recorded intervals and partial twelve-column objects; case35 beyond its prefix and60 other profiles remain UNKNOWN.',assumptions=['Exact fixed Hadamard six-prism support and profile-domain convention.','Partial objects obey Gram upper bounds and all66 internal outside-column caps.'],dependencies=[dict(id='C-FIXED-HADAMARD-FOUR-EXCEPTION-LOCAL-PROFILE-SCREEN',revision=1,relation='premise')],verifier='/root/structural_attack',producer='/root/state_literature_audit',method='A separate pair-pair join using complete integer Gram coefficients packed into independently calibrated base64 lanes; exact set comparison against every saved compressed tuple, raw36x12 object checks and explicit residual pair decompositions.',shared_components=['Previously independently checked pair tables and local catalogue; no producer imports.','Frozen independently authored raw partial-object checker; Python exact integers, gzip and JSON runtime.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},artifact_availability='LOCAL_ONLY',availability_reason='Pending parent publication; original compressed chunks retained.',external_review=None,external_review_reason='No external review asserted.',limitations=['No completion to a full36x60 factor or99-vertex graph.','Partial objects do not by themselves certify residual PSD or a shared remaining-column realization.','Do not extrapolate case35 to its full Cartesian domain or count unattempted profiles as exclusions.','The observed producer elapsed120.047s is a saved execution measurement, not a replayed performance guarantee.'],created_at=ts,updated_at=ts)
        write(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_HADAMARD_FOUR_GROUP_JOINT_PARTIAL_CENSUS_PASS',timestamp=ts,inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},completed_profiles=35,partially_completed_profiles=1,unattempted_profiles=60,completed_intervals=len(checkpoints),raw_partial_objects=totals['surviving_partial_objects'],raw_first_witnesses=len(witnesses),independent_counts=dict(totals),corruptions_rejected=len(rejected),native_solver_calls=0,target_resolution=False)
        write(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'),elapsed_seconds=time.perf_counter()-start)))
    except BaseException as e:write(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
