"""Independent literal uint16 relation checking and queue-based AC audit."""
from collections import Counter,deque
from datetime import datetime,timezone
from itertools import combinations,permutations,product
from pathlib import Path
import argparse,copy,gzip,hashlib,json,platform,subprocess,sys,time
import numpy as np
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
RUN=B/'20260930_hadamard_six_profile_arc/run01';INV=B/'20260930_hadamard_six_profile_arc/inventory/inventory.json'
DOMAIN=B/'20260930_independent_review/hadamard_six_profile_local_domains/summary.json'
RAW=B/'20260930_hadamard20_support/six_prism.json';CAT=B/'20260930_hadamard_triplicate_counts/local_triples.json';PROFILES=B/'20260930_hadamard_six_profile_local_domains/profiles.jsonl.gz';FIXTURE=B/'20260930_srg243_residual_fixture/triangle_blocks.json'
PINS={RUN/'summary.json':'44805fae16a3f988ac4fa575c1b38bb2a5f5121c5e7521e46f45990b8f83a9b1',INV:'5f41560faa33278529e190babb3e2595f763de85d821998d055338bf6aea7255',DOMAIN:'976e673b02c8742503a33d091e6ddf4650c13289e25fd859cb7854deb0174235'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def gzread(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def pin(p,d,bindings):
    p=Path(p);need(sha(p)==d,'hash '+key(p));k=key(p);need(k not in bindings or bindings[k]==d,'consistent binding');bindings[k]=d
def packed_rows(a):return [hex(sum(1<<int(j) for j in np.flatnonzero(row))) for row in a]
def exact_relations(a,b,g):
    ga=a@a.transpose(0,2,1);gb=b@b.transpose(0,2,1)
    first=np.all(ga[:,None,:,:]+gb[None,:,:,:]<=g[None,None,:,:],axis=(2,3))
    cross=np.matmul(a.transpose(0,2,1)[:,None,:,:],b[None,:,:,:])
    return first,first&np.all(cross<=2,axis=(2,3))
def verify_rows(a,rows):need(rows==packed_rows(a),'all literal relation bits')
def queue_ac(sizes,tables):
    domains=[set(range(n)) for n in sizes];q=deque(permutations(range(len(sizes)),2))
    while q and all(domains):
        i,j=q.popleft();left=sorted(domains[i]);right=sorted(domains[j]);valid=np.any(tables[i,j][np.ix_(left,right)],axis=1)
        gone={x for x,keep in zip(left,valid) if not keep}
        if gone:
            domains[i]-=gone
            q.extend((k,i) for k in range(len(sizes)) if k not in (i,j))
    return domains
def replay(sizes,tables,record):
    domains=[set(range(n)) for n in sizes]
    for d in record['deletions']:
        i,j,x=d['left'],d['right'],d['option'];need(0<=i<len(sizes) and 0<=j<len(sizes) and i!=j and x in domains[i],'deletion active option')
        need(d['right_domain_mask']==hex(sum(1<<v for v in domains[j])),'literal neighbor domain')
        need(not any(tables[i,j][x,y] for y in domains[j]),'deletion lacks every support');domains[i].remove(x)
    need(record['final_masks']==[hex(sum(1<<x for x in d)) for d in domains],'final masks')
    need(record['final_sizes']==list(map(len,domains)) and record['empty']==(not all(domains)),'final empty/sizes')
    if all(domains):
        witnesses=record['support_witnesses'];need([w['sides'] for w in witnesses]==[list(p) for p in permutations(range(len(sizes)),2)],'complete ordered arcs')
        for w in witnesses:
            i,j=w['sides'];need([x for x,y in w['supports']]==sorted(domains[i]),'all surviving source options')
            for x,y in w['supports']:need(y in domains[j] and tables[i,j][x,y],'literal surviving support')
    else:need(record['support_witnesses']==[],'empty-domain report has no fixed-point assertion')
    independent=queue_ac(sizes,tables);need(bool(all(independent))==bool(all(domains)),'independent queue empty outcome')
    if all(domains):need(independent==domains,'same greatest nonempty fixed point')
    return len(record['deletions']),sum(len(w['supports']) for w in record['support_witnesses'])
def control_record(sizes,tables):
    domains=[set(range(n)) for n in sizes];dels=[]
    while all(domains):
        found=False
        for i,j in permutations(range(len(sizes)),2):
            for x in sorted(domains[i]):
                if not any(tables[i,j][x,y] for y in domains[j]):
                    dels.append(dict(left=i,right=j,option=x,right_domain_mask=hex(sum(1<<y for y in domains[j]))));domains[i].remove(x);found=True;break
            if found:break
        if not found:break
    support=[]
    if all(domains):
        for i,j in permutations(range(len(sizes)),2):support.append(dict(sides=[i,j],supports=[[x,next(y for y in sorted(domains[j]) if tables[i,j][x,y])] for x in sorted(domains[i])]))
    return dict(deletions=dels,final_masks=[hex(sum(1<<x for x in d)) for d in domains],final_sizes=list(map(len,domains)),empty=not all(domains),support_witnesses=support)
def controls():
    rejected=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,IndexError):rejected.append(name)
        else:raise ValueError('corruption accepted '+name)
    f=np.array(read(FIXTURE)['factor60x180'],dtype=np.uint16);g=f@f.T;parts=np.stack([f[:,3*i:3*i+3] for i in range(8)])
    r,c=exact_relations(parts,parts,g);need(all(r[i,j] and c[i,j] for i,j in combinations(range(8),2)),'28 genuine243 pair positives');need(not c[0,0],'duplicate columns rejected');rejected.append('duplicate_columns')
    bad=g.copy();contrib=parts[0]@parts[0].T+parts[1]@parts[1].T;i,j=next(zip(*np.nonzero(contrib)));bad[i,j]=0
    need(not exact_relations(parts[:1],parts[1:2],bad)[0][0,0],'damaged Gram rejected');rejected.append('damaged_Gram')
    rows=packed_rows(r);badrows=rows.copy();badrows[0]=hex(int(badrows[0],16)^1);reject('relation_bit',lambda:verify_rows(r,badrows))
    joint=0
    for labels in product(range(16),repeat=3):
        tables={}
        for (i,j),mask in zip(combinations(range(3),2),labels):
            a=np.array([bool(mask>>k&1) for k in range(4)]).reshape(2,2);tables[i,j]=a;tables[j,i]=a.T
        domains=queue_ac([2]*3,tables)
        for values in product(range(2),repeat=3):
            if all(tables[i,j][values[i],values[j]] for i,j in combinations(range(3),2)):
                need(all(values[i] in domains[i] for i in range(3)),'actual assignment preserved');joint+=1
    tables={(i,j):np.ones((2,2),dtype=bool) for i,j in permutations(range(6),2)};positive=control_record([2]*6,tables);replay([2]*6,tables,positive)
    bad=copy.deepcopy(positive);bad['support_witnesses'][0]['supports'][0][1]=2;reject('support_outside_domain',lambda:replay([2]*6,tables,bad))
    bad=copy.deepcopy(positive);bad['support_witnesses'].pop();reject('missing_ordered_arc',lambda:replay([2]*6,tables,bad))
    tables[0,1][:]=False;tables[1,0][:]=False;negative=control_record([2]*6,tables);replay([2]*6,tables,negative);need(negative['empty'],'synthetic contradiction')
    bad=copy.deepcopy(negative);bad['deletions'][0]['right_domain_mask']='0x0';reject('false_neighbor_mask',lambda:replay([2]*6,tables,bad))
    bad=copy.deepcopy(negative);bad['deletions'][0]['option']=2;reject('absent_source_option',lambda:replay([2]*6,tables,bad))
    bad=copy.deepcopy(negative);bad['final_sizes'][0]+=1;reject('wrong_final_size',lambda:replay([2]*6,tables,bad))
    return dict(genuine243_partial_pairs=28,binary_triangle_relation_systems=4096,actual_joint_assignments_preserved=joint,synthetic_six_domain_cases=2,rejected_corruptions=rejected,arithmetic='uint16 exact; no floating point',research_factor_positive=False)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic();bindings={}
    try:
        for p,d in PINS.items():pin(p,d,bindings)
        summary=read(RUN/'summary.json');inv=read(INV);gate=read(DOMAIN)
        need(gate['status'].startswith('INDEPENDENT_') and gate['status'].endswith('_PASS'),'domain coverage gate')
        for obj in (summary,gate):
            for field in ('inputs_sha256','outputs_sha256'):
                for p,d in obj.get(field,{}).items():pin(ROOT/p,d,bindings)
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_SIX_PROFILE_ARC_PLAN.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p,sha(p),bindings)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,time_limit_seconds=600,inputs_sha256=bindings))
        save(out/'controls.json',controls());raw=read(RAW);cat=read(CAT);g=np.array(raw['prescribed_Gram36'],dtype=np.uint16);groups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][d]) for d in range(60)))
        with gzip.open(PROFILES,'rt',encoding='utf-8') as stream:profiles=[json.loads(s) for s in stream]
        need(len(profiles)==984 and len({p['id'] for p in profiles})==984,'frozen labelled population')
        cp=read(ROOT/summary['checkpoint_path']);need(cp['inputs_sha256']==summary['inputs_sha256'] and cp['stop_state']=='COMPLETE','completed checkpoint')
        arrays=[];domain_cache={};endpoint_keys=set()
        for i,ep in enumerate(inv['endpoints']):
            need(ep['index']==i and ep['support']==list(groups[ep['group']]),'literal endpoint indexing')
            identity=(ep['group'],ep['domain_sha256']);need(identity not in endpoint_keys,'unique endpoint');endpoint_keys.add(identity);path=ROOT/ep['domain_path'];pin(path,ep['domain_sha256'],bindings)
            dom=domain_cache.setdefault(ep['domain_sha256'],read(path));ranks=dom['local_survivor_indices'];need(ep['local_survivor_indices']==ranks and ep['count']==dom['count']==len(ranks),'endpoint complete domain')
            a=np.zeros((len(ranks),36,3),dtype=np.uint16)
            for oi,rank in enumerate(ranks):
                for col,w in enumerate(cat['survivors'][rank]):
                    for position,coord in enumerate(ep['support']):a[oi,12*cat['words'][w][position]+coord,col]=1
            need(np.all(a.sum(axis=1)==6),'literal six-coordinate column weights');arrays.append(a)
        need(len(inv['profiles'])==984 and len(inv['relations'])==12648,'frozen inventory counts');expected_uses=[]
        for pi,(p,meta) in enumerate(zip(profiles,inv['profiles'])):
            need(meta['index']==pi and meta['id']==p['id'] and meta['groups']==p['group_ids'] and meta['rank4_case']==p['rank4_case'],'profile identity')
            need(meta['profile_sha256']==p['profile_sha256']==digest(dict(groups=p['group_ids'],deviations=p['coordinate_fibre_deviations'])),'raw profile hash')
            for side,ei in enumerate(meta['endpoints']):
                ep=inv['endpoints'][ei];ref=p['local_domains'][side];need(ep['group']==ref['group']==p['group_ids'][side] and ep['domain_sha256']==ref['sha256'] and ep['domain_path']==ref['path'],'raw profile/domain mapping')
            need([q['sides'] for q in meta['pairs']]==[list(x) for x in combinations(range(6),2)],'all15 unordered arcs')
            for pair in meta['pairs']:
                ei,ej=[meta['endpoints'][j] for j in pair['sides']];need(inv['relations'][pair['relation']]['endpoints']==[ei,ej],'relation endpoints');expected_uses.append(pair['relation'])
        need(set(expected_uses)==set(range(12648)),'no missing/unused relation')
        tables=[];products=0;relation_rows=[]
        for i,(meta,ref) in enumerate(tqdm(zip(inv['relations'],cp['completed_relations']),total=12648,desc='Independent literal pair tables',mininterval=1)):
            need(i==meta['index']==ref['index'],'relation exact order');p=ROOT/ref['path'];pin(p,ref['sha256'],bindings);record=gzread(p);need(record['index']==i and record['endpoints']==meta['endpoints'],'raw relation identity')
            ei,ej=meta['endpoints'];a,b=arrays[ei],arrays[ej];r,c=exact_relations(a,b,g);verify_rows(r,record['gram_forward']);verify_rows(c,record['combined_forward'])
            n=r.size;need(n==meta['option_pairs']==ref['option_pairs']==record['option_pairs'],'relation product count');need(int(r.sum())==record['gram_compatible']==ref['gram_compatible'] and int(c.sum())==record['combined_compatible']==ref['combined_compatible'],'compatible counts')
            products+=n;tables.append((r,c));relation_rows.append(dict(index=i,option_pairs=n,gram_compatible=int(r.sum()),combined_compatible=int(c.sum())))
            if i%200==0:need(time.monotonic()-started<600,'audit600-second allocation')
        need(len(tables)==12648 and len(cp['completed_relations'])==12648 and products==12846624,'complete relation population')
        save(out/'relation_counts.json',dict(records=relation_rows,option_pairs=products,all_Gram_entries_per_pair=1296,cross_column_entries_per_pair=9))
        checked=[];deletions=supports=0;need(len(cp['completed_profiles'])==984,'all profile artifacts')
        for pi,(rawp,meta,ref) in enumerate(tqdm(zip(profiles,inv['profiles'],cp['completed_profiles']),total=984,desc='Independent deletion/support proofs',mininterval=1)):
            p=ROOT/ref['path'];pin(p,ref['sha256'],bindings);rec=gzread(p);need(rec['index']==ref['index']==pi and rec['id']==ref['id']==rawp['id'] and rec['raw_profile']==rawp and rec['profile_sha256']==rawp['profile_sha256'],'saved profile identity')
            need(rec['endpoint_indices']==meta['endpoints'] and rec['relations']==meta['pairs'],'all saved relation references')
            sizes=[inv['endpoints'][e]['count'] for e in meta['endpoints']];need(rec['initial_domain_sizes']==sizes,'initial complete domains');outcomes=[]
            for mode,field in enumerate(('gram_ac','gram_caps_ac')):
                local={}
                for edge in meta['pairs']:
                    i,j=edge['sides'];r=tables[edge['relation']][mode];local[i,j]=r;local[j,i]=r.T
                d,s=replay(sizes,local,rec[field]);deletions+=d;supports+=s;outcomes.append(rec[field]['empty'])
            need(outcomes==[ref['gram_empty'],ref['combined_empty']] and (not outcomes[0] or outcomes[1]),'reported nested outcomes')
            need(rec['gram_ac']['final_sizes']==ref['gram_final_sizes'] and rec['gram_caps_ac']['final_sizes']==ref['combined_final_sizes'],'reference final sizes')
            checked.append(dict(index=pi,id=rawp['id'],rank4_case=rawp['rank4_case'],gram_pair_empty=outcomes[0],combined_empty=outcomes[1]))
            need(time.monotonic()-started<600,'audit600-second allocation')
        first=sum(r['gram_pair_empty'] for r in checked);combined=sum(r['combined_empty'] for r in checked)
        need((first,combined,len(checked)-combined)==(582,654,330),'literal outcome counts');need(summary['Gram_empty_profiles']==first and summary['Gram_caps_empty_profiles']==combined and summary['unresolved_complete_profiles']==330,'summary outcomes')
        save(out/'profile_outcomes.json',dict(records=checked));now=datetime.now(timezone.utc).isoformat();scope='All984 literal exactly-six-exception profiles on one fixed support, using complete locally cap-filtered domains. Both exclusion counts require outside-column caps; first relation omits only cross-group caps. No joint or complete factor feasibility.'
        shared=['Independently audited literal local-domain/catalogue population is an explicit coverage premise, not reconstructed again.','Python/NumPy exact uint16 arithmetic and standard parsers; no producer or prior checker imports.','Literal support, catalogue and genuine243 fixture bytes are shared inputs.']
        limitations=['All330 nonempty fixed points remain unresolved for joint/full factor feasibility.','No fibre-orbit reduction, whole-support exclusion or target resolution.','The582 figure is not a Gram-only-family exclusion because initial domains impose within-group caps.']
        binding=dict(id='C-FIXED-HADAMARD-SIX-EXCEPTION-PAIRWISE-PROFILE-SCREEN',revision=1,statement='For all984 labelled exactly-six-active marginal profiles on the literal fixed Hadamard support, pairwise AC on their complete locally cap-filtered domains empties582 profiles when pair relations require summed prescribed-Gram upper bounds, and654 profiles when cross-group outside-column overlaps are also at most2; the latter includes every former empty profile and leaves330 nonempty fixed points. The complete saved relation tables and deletion/support certificates agree with literal exact arithmetic.',kind='exclusion',basis=['COMPUTED','DERIVED'],status='VERIFIED',review_state='CLEAR',scope=scope,assumptions=['Literal fixed support and full prescribed Gram.','Outside-column pair overlap caps at most2, including inside every local group.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-EXCEPTION-LOCAL-DOMAIN-FILTER',revision=1,relation='coverage')],artifact_hashes=bindings,verifier='/root',checking_method='Complete independent literal matrix relation reconstruction; deletion-proof replay; different queue-based AC; positive and corrupted controls.',shared_components=shared,limitations=limitations,created_at=now,updated_at=now)
        save(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_SIX_EXCEPTION_PROFILE_ARC_SCREEN_PASS',timestamp=now,inputs_sha256=bindings,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},verifier='/root',profiles=984,relations=12648,distinct_option_pairs=products,complete_Gram_entries_per_pair=1296,cross_column_entries_per_pair=9,checked_deletions=deletions,checked_surviving_supports=supports,Gram_pair_empty_profiles=first,combined_empty_profiles=combined,nonempty_profiles=330,scope=scope,shared_components=shared,limitations=limitations,elapsed_seconds=time.monotonic()-started,target_resolution=False)
        save(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs_sha256','outputs_sha256')}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__)),inputs_sha256=bindings));raise
if __name__=='__main__':main()
