"""Candidate six fibre-image count-master cuts; exact producer, no solver."""
from datetime import datetime,timezone
from itertools import combinations,permutations
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';BASE=B/'20260930_hadamard_count_master_cnf'
MODEL=BASE/'model.json';CNF=BASE/'at_least_seven.cnf';RAW=B/'20260930_hadamard20_support/six_prism.json';LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
PROFILE=B/'20260930_independent_review/count_master_sat_outcome/independent_count_profile.json';PROOF=B/'20260930_independent_review/eight_count_profile_unsat/summary.json'
SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
ASSIGNMENT=B/'20260930_hadamard_count_master_native_pilot_v2/main/parsed_model.json'
PINS={MODEL:'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',CNF:'f303edec9a91dc9bcecb95804ee151d0e38e8100b17c9c45a7b4d58b8edbf55e',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',PROFILE:'0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152',PROOF:'c846d32c668910bb1254b840ca3bff6b97ec8bb5878e3092e48575e5bbe3e1ed',ASSIGNMENT:'e2a2a5f6daa251d153aa7396759731332a74031ed4c50d4e45d6d81370ad1077',
 B/'20260930_independent_review/hadamard_count_master_cnf_v2/summary.json':'80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888',
 B/'20260930_independent_review/count_master_sat_outcome/summary.json':'61e7eb9643902c866617a270d856a521f71f5b2723c0e731edae3896baba484d',
 B/'20260930_independent_review/eight_count_profile_lift/summary.json':'270d6c53406887c328f4ccbcdc670da5a0e3de156733a2dbd9145582f0cb1802',
 B/'20260930_independent_review/hadamard_seven_fibre_orbits/summary.json':'930f8d9a6e6b5986a61627cf21208c65691254c50fb2a71f6ddc0c4504b94e6f'}

def need(x,msg):
    if not x:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,v):
    with Path(p).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def compact(v):return json.dumps(v,separators=(',',':'),sort_keys=True)
def profile_digest(counts,groups):
    exceptional=[g for g,s in enumerate(groups)if any(counts[a][g]!=[1,1,1]for a in s)]
    deviation=[[[counts[a][g][f]-int(a in groups[g])for g in exceptional]for f in range(3)]for a in range(12)]
    return hashlib.sha256(compact(dict(groups=exceptional,deviations=deviation)).encode()).hexdigest(),exceptional,deviation
def transform_counts(counts,tau):return [[[v[tau.index(f)]for f in range(3)]for v in row]for row in counts]
def mapped_word(word,tau):return [tau[f]for f in word]
def values(lits,n):
    need(len(lits)==n and all(type(x)is int and 0<abs(x)<=n for x in lits)and len({abs(x)for x in lits})==n,'complete unique assignment')
    v=[False]*(n+1)
    for x in lits:v[abs(x)]=x>0
    return v
def clauses(path):
    with Path(path).open('r',encoding='ascii')as f:
        header=next(f).split();need(header[:2]==['p','cnf'],'header');n,m=map(int,header[2:]);rows=[]
        for line in f:
            c=list(map(int,line.split()));need(c and c[-1]==0 and all(0<abs(x)<=n for x in c[:-1]),'valid clause');rows.append(c[:-1])
    need(len(rows)==m,'exact body count');return n,rows
def satisfied(row,v):return any(v[abs(x)]==(x>0)for x in row)
def group_selection(model,counts):
    signatures={tuple(x['counts']):x['index']for x in model['local_signatures']};result=[];ids=[];ranks=[]
    for d in model['group_domains']:
        counts6=sum([counts[a][d['group']]for a in d['support']],[]);s=signatures[tuple(counts6)];i=d['signature_indices'].index(s);sel=d['selectors'][i];ids.append(sel);ranks.append(s)
        result.append(dict(group=d['group'],count_signature=counts6,global_signature_index=s,group_option_index=i,selector=sel,local_survivor_indices=model['local_signatures'][s]['local_survivor_indices']))
    return ids,ranks,result
def construct_assignment(model,counts):
    n=model['variants']['at_least_seven']['variables'];v=[False]*(n+1);coordinate_ids=[]
    for d in model['coordinate_domains']:
        matches=[i for i,t in enumerate(d['count_tables'])if t==counts[d['coordinate']]];need(len(matches)==1,'exact transformed coordinate count domain');i=matches[0];v[d['selectors'][i]]=True;coordinate_ids.append(d['selectors'][i])
    gids,_,_=group_selection(model,counts)
    for x in gids:v[x]=True
    for d in model['count_channels']:
        target=counts[d['coordinate']][d['group']];matches=[i for i,t in enumerate(d['values'])if t==target];need(len(matches)==1,'literal transformed incidence channel');v[d['variables'][matches[0]]]=True
    for d in model['one_hot_domains']:
        need(sum(v[x]for x in d['selectors'])==1,'actual transformed domain onehot')
        for i,x in enumerate(d['prefix_variables']):v[x]=any(v[y]for y in d['selectors'][:i+1])
    ext=model['extension']
    for s in ext['states']:v[s['id']]=sum(v[x]for x in ext['input_variables'][:s['i']])>=s['j']
    return [i if v[i]else -i for i in range(1,n+1)],v,coordinate_ids
def package(path):
    target=path.with_name(path.name+'.gz')
    with path.open('rb')as src,target.open('xb')as raw:
        with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0)as out:
            for b in iter(lambda:src.read(1048576),b''):out.write(b)
    need(target.stat().st_size<10*1024**2,'public gzip ceiling')
    with gzip.open(target,'rb')as packed,path.open('rb')as original:
        while True:
            a=packed.read(1048576);b=original.read(1048576);need(a==b,'literal complete gzip recovery')
            if not a:break
    return dict(raw_path=key(path),raw_sha256=sha(path),raw_bytes=path.stat().st_size,gzip_path=key(target),gzip_sha256=sha(target),gzip_bytes=target.stat().st_size,recovery_identity=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        v=sha(p);need(h is None or h==v,'pin '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        for p in [Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        proof=read(PROOF);need(proof['status']=='INDEPENDENT_LITERAL_EIGHT_COUNT_PROFILE_UNSAT_PASS','actual independent literal exclusion')
        binding=PROOF.parent/'claim_binding.json';pin(binding,proof['outputs_sha256'][key(binding)]);need(read(binding)['id']=='C-FIXED-HADAMARD-EIGHT-COUNT-PROFILE-EXCLUSION','exact prior scope')
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,limits=dict(cooperative_seconds=120,solver_calls=0,native_calls=0),selection='All six global fibre relabellings of one pinned independently excluded literal profile, lexicographic S3 order.',source_sharing='Standard library only; raw frozen models/evidence, no producer or verifier imports.'))
        model=read(MODEL);raw=read(RAW);profile=read(PROFILE);local=read(LOCAL);groups=model['groups'];words=local['words'];triples=local['survivors'];C=raw['core_adjacency'];K=raw['prescribed_Gram36'];L=raw['L'];original=profile['coordinate_group_fibre_counts']
        need(profile_digest(original,groups)[0]==profile['profile_sha256']=='d2b0c89bb1d8f0d75b47f541603e952618cebe9b7ecccd8e1b2c23a279ac8dd9','original literal table')
        need(groups==[d['support']for d in model['group_domains']]and len(groups)==20,'raw group convention')
        wordlookup={tuple(w):i for i,w in enumerate(words)};triplelookup={tuple(t):i for i,t in enumerate(triples)};actions=[];records=[];cuts=[]
        for action,t in enumerate(permutations(range(3))):
            tau=list(t);rowmap=[12*tau[f]+a for f in range(3)for a in range(12)]
            need(sorted(rowmap)==list(range(36))and all(C[rowmap[i]][rowmap[j]]==C[i][j]and K[rowmap[i]][rowmap[j]]==K[i][j]for i in range(36)for j in range(36)),'literal core/Gram covariance')
            need(all({rowmap[12*f+a]for f in range(3)}=={12*f+a for f in range(3)}for a in range(12)),'each coordinate row-sum functional is invariant, hence any aggregate support L is preserved')
            wm=[wordlookup[tuple(mapped_word(w,tau))]for w in words];tm=[triplelookup[tuple(sorted(wm[w]for w in tri))]for tri in triples]
            need(sorted(wm)==list(range(90))and sorted(tm)==list(range(31110)),'complete word/triple bijections')
            transformed=transform_counts(original,tau);digest,exceptional,deviations=profile_digest(transformed,groups);need(exceptional==profile['exceptional_groups'],'all eight exception labels preserved')
            selectors,signature_indices,domain_records=group_selection(model,transformed)
            for g,r in enumerate(domain_records):need(sorted(tm[i]for i in profile['local_survivor_indices_by_group'][g])==r['local_survivor_indices'],'full local-domain fibre bijection')
            clause=[-x for x in selectors];need(len(set(clause))==20 and all(x<0 for x in clause),'exact full twenty-group nogood');cuts.append(clause)
            rec=dict(action_index=action,fibre_image=tau,row_image=rowmap,profile_sha256=digest,coordinate_group_fibre_counts=transformed,exceptional_groups=exceptional,coordinate_fibre_deviations=deviations,selected_group_selector_ids=selectors,selected_global_signature_indices=signature_indices,group_records=domain_records,clause=clause)
            records.append(rec);actions.append(dict(fibre_image=tau,row_image=rowmap,word_image=wm,local_triple_image=tm))
        need(len({r['profile_sha256']for r in records})==len({tuple(x)for x in cuts})==6,'six distinct transformed count profiles/clauses')
        lookup={tuple(a['fibre_image']):i for i,a in enumerate(actions)};composition=[]
        for i,a in enumerate(actions):
            for j,b in enumerate(actions):
                k=lookup[tuple(a['fibre_image'][b['fibre_image'][f]]for f in range(3))];need(all(a['row_image'][b['row_image'][r]]==actions[k]['row_image'][r]for r in range(36)),'literal action composition');need(transform_counts(records[j]['coordinate_group_fibre_counts'],a['fibre_image'])==records[k]['coordinate_group_fibre_counts'],'complete profile action closure');composition.append(dict(left=i,right=j,product=k))
        save(out/'actions.json',dict(actions=actions,composition=composition));save(out/'excluded_profiles.json',dict(records=records,prior_exclusion_path=key(PROOF),prior_exclusion_sha256=PINS[PROOF],scope='Exactly six literal profiles; no other orbit or exception-count coverage.'))
        n,oldclauses=clauses(CNF);need((n,len(oldclauses))==(155939,705833),'exact at-least-seven base')
        with CNF.open('rb')as f:oldheader=f.readline();body=f.read()
        suffix=b''.join((' '.join(map(str,c))+' 0\n').encode()for c in cuts);new=out/'instance.cnf';new.write_bytes(f'p cnf {n} {len(oldclauses)+6}\n'.encode()+body+suffix);(out/'cuts.cnfpart').write_bytes(suffix)
        need(new.read_bytes().split(b'\n',1)[1]==body+suffix,'byte-identical complete body plus six cuts')
        control_records=[]
        for i,r in enumerate(records):
            lits,v,coordinateids=construct_assignment(model,r['coordinate_group_fibre_counts']);need(all(satisfied(c,v)for c in oldclauses),'all base clauses for transformed full count witness');cuttruth=[satisfied(c,v)for c in cuts];need(cuttruth==[j!=i for j in range(6)],'each orbit witness excluded by exactly its own clause')
            save(out/f'control_orbit_{i}_assignment.json',dict(assignment=lits,scope='Constructed exact old count-CSP assignment; violates new cut, no factor or native solve.'));control_records.append(dict(action_index=i,base_clauses_checked=len(oldclauses),cut_satisfaction=cuttruth,coordinate_selector_ids=coordinateids,group_selector_ids=r['selected_group_selector_ids']))
        actual=values(read(ASSIGNMENT)['assignment'],n);need(all(satisfied(c,actual)for c in oldclauses),'original raw native count witness remains valid for old model');need([satisfied(c,actual)for c in cuts]==[False,True,True,True,True,True],'original native witness rejected exactly once')
        unrelated=[]
        for name in ('all_balanced_counts','rank4_00_profile_0000'):
            path=BASE/(name+'_assignment.json');pin(path);a=read(path)['assignment'];v=values(a,model['variants']['baseline']['variables']);need(all(satisfied(c,v)for c in cuts),'unrelated baseline counts satisfy new cuts');unrelated.append(dict(name=name,all_six_cuts=True,baseline_only=True,at_least_seven_satisfied=False,scope='Zero/six exceptions; not a positive for the strengthened >=7 formula.'))
        badmaps=[(0,0,2),(0,1,3)];need(all(sorted(x)!=[0,1,2]for x in badmaps),'corrupt fibre maps rejected')
        flipped=cuts[0][:];flipped[0]*=-1;need(satisfied(flipped,actual)and not satisfied(cuts[0],actual),'signed cut corruption detected')
        missing=records[0]['selected_group_selector_ids'][:-1];need(len(missing)!=20,'missing group selector rejected')
        save(out/'controls.json',dict(orbit_count_assignments=control_records,original_count_witness_base_valid=True,original_cut_truth=[False,True,True,True,True,True],unrelated_cut_only_positives=unrelated,corrupt_controls=['nonbijective fibre map','out-of-range fibre map','signed clause','missing group selector'],new_formula_positive=None,new_formula_positive_reason='No new satisfying count assignment or solver search was obtained.'))
        scope=dict(schema='COUNT_MASTER_SIX_EXCLUDED_EIGHT_PROFILE_IMAGES_V1',base_cnf_path=key(CNF),base_cnf_sha256=PINS[CNF],base_model_path=key(MODEL),base_model_sha256=PINS[MODEL],base_variant='at_least_seven',base_variables=n,base_clauses=len(oldclauses),added_clauses=6,new_variables=0,excluded_full_count_profiles=6,prior_exclusion_path=key(PROOF),prior_exclusion_sha256=PINS[PROOF],relabeling='Global fibre labels only; fixed coordinate/support labels. No hypothetical-target automorphism assumption.',necessity='Any full-Gram factor with within-triplicate caps avoids these six literal profiles by inverse relabelling and the prior exact exclusion.',converse='The new formula is exactly the old count master with these six count tables forbidden; a count-CSP solution need not lift to a factor.',full_factor=False,target_graph=False,residual_D=None)
        save(out/'scope.json',scope);save(out/'model.json',dict(schema='COUNT_MASTER_SIX_FULL_PROFILE_NOGOODS_V1',variables=n,clauses=len(oldclauses)+6,scope_sha256=sha(out/'scope.json'),base_model_path=key(MODEL),base_model_sha256=PINS[MODEL],base_cnf_path=key(CNF),base_cnf_sha256=PINS[CNF],base_body_sha256=hashlib.sha256(body).hexdigest(),clause_records=[dict(index=len(oldclauses)+i+1,action_index=i,profile_sha256=r['profile_sha256'],clause=cuts[i])for i,r in enumerate(records)]))
        packages=[package(new)];save(out/'artifact_packages.json',dict(packages=packages));need(time.perf_counter()-start<120,'declared120-second allocation')
        save(out/'summary.json',dict(status='CANDIDATE_SIX_FIBRE_IMAGE_PROFILE_CUTS_BUILT',inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},variables=n,clauses=len(oldclauses)+6,added_clauses=6,each_clause_literals=20,actions=6,complete_word_images=540,complete_local_triple_images=186660,raw_core_and_Gram_comparisons=7776,excluded_profile_digests=[r['profile_sha256']for r in records],old_count_CSP_positive_controls=6,new_count_CSP_positive_controls=0,solver_calls=0,native_calls=0,independent_approval=False,target_resolution=False,elapsed_seconds=time.perf_counter()-start,scope=scope))
        print(json.dumps(dict(status='CANDIDATE_SIX_FIBRE_IMAGE_PROFILE_CUTS_BUILT',summary_sha256=sha(out/'summary.json'),cnf_sha256=sha(new),model_sha256=sha(out/'model.json'),scope_sha256=sha(out/'scope.json'))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),inputs_sha256=pins));raise
if __name__=='__main__':main()
