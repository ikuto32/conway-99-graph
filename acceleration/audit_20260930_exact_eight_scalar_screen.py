"""Independent raw catalogue/extrema/orbit audit; standard library only."""
import argparse,collections,copy,gzip,hashlib,itertools,json,platform,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';D=B/'20260930_exact_eight_scalar_screen';J=B/'20260930_exact_eight_profile_join';I=B/'20260930_independent_review'
PERMS=list(itertools.permutations(range(3)))
def need(x,m):
    if not x:raise ValueError(m)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):
    if str(p).endswith('.gz'):
        with gzip.open(p,'rt',encoding='utf8') as f:return json.load(f)
    return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,separators=(',',':'));f.write('\n')
def gzsave(p,x):
    with p.open('xb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0) as g:g.write((json.dumps(x,separators=(',',':'))+'\n').encode())
def digest(v):return hashlib.sha256(bytes(v)).hexdigest()
def flatten(counts):
    need(len(counts)==12 and all(len(row)==20 and all(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v) for v in row) for row in counts),'strict count table');return bytes(x for row in counts for v in row for x in v)
def transform(v,p):return bytes(v[k+p[f]] for k in range(0,720,3) for f in range(3))
def catalogue():
    words=[w for w in itertools.product(range(3),repeat=6) if all(w.count(f)==2 for f in range(3))];bits=[sum(1<<(3*a+f) for a,f in enumerate(w)) for w in words];pairs=list(itertools.combinations(range(6),2));triples=[];vectors=[];signatures=[]
    for ids in itertools.combinations(range(90),3):
        if any((bits[i]&bits[j]).bit_count()>2 for i,j in itertools.combinations(ids,2)):continue
        values=[0]*135
        for pi,(a,b) in enumerate(pairs):
            for wi in ids:values[9*pi+3*words[wi][a]+words[wi][b]]+=1
        if any(v>(1 if k%9//3==k%3 else 2) for k,v in enumerate(values)):continue
        triples.append(ids);vectors.append(bytes(values));signatures.append(tuple(sum(words[wi][a]==f for wi in ids) for a in range(6) for f in range(3)))
    need(len(words)==90 and len(triples)==31110,'raw complete local universe');return words,triples,vectors,signatures
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        s=sha(p);need(h is None or s==h,'identity '+key(p));pins[key(p)]=s
    try:
        pin(D/'summary.json','58a483301606ae9fcc418b10d091ef6bd524683fda513a79e7d536d07b3d953f');summary=read(D/'summary.json')
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/p,h)
        gate=I/'exact_eight_profile_join/summary.json';pin(gate,'2538bf724a3938b14ffd1856fc4e9a8a6a294a6905ddc7000d19cf72f93b217c');join_gate=read(gate);need(join_gate['status']=='INDEPENDENT_COMPLETE_EXACT_EIGHT_PROFILE_JOIN_PASS','coverage premise');join=read(J/'summary.json')
        for p,h in join['outputs_sha256'].items():need(join_gate['inputs_sha256'].get(p)==h and sha(ROOT/p)==h,'all complete join artifacts authenticated')
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_EXACT_EIGHT_SCALAR_SCREEN.md']:pin(p)
        raw=read(B/'20260930_hadamard20_support/six_prism.json');local=read(B/'20260930_hadamard_triplicate_counts/local_triples.json');words,triples,values,signatures=catalogue();need([list(w) for w in words]==local['words'] and [list(t) for t in triples]==local['survivors'],'every local catalogue entry')
        partition=collections.defaultdict(list)
        for ti,s in enumerate(signatures):partition[s].append(ti)
        sigs=sorted(partition);need(len(sigs)==6061,'all count signatures');index={s:i for i,s in enumerate(sigs)};saved=read(B/'20260930_hadamard_count_master_preflight/local_signatures.json')['signatures']
        need(all(r['index']==i and tuple(r['counts'])==sigs[i] and r['local_survivor_indices']==partition[sigs[i]] for i,r in enumerate(saved)) and len(saved)==6061,'full signature rank/class lists')
        mins=[];maxs=[];bounds=[]
        for si,s in enumerate(sigs):
            rows=[values[ti] for ti in partition[s]];lo=[min(col) for col in zip(*rows)];hi=[max(col) for col in zip(*rows)];mins.append(lo);maxs.append(hi);bounds.append(dict(signature_index=si,class_size=len(rows),minimum=lo,maximum=hi))
        tab=read(B/'20260930_hadamard_count_gram_intervals/signature_intervals.json.gz');cells=[(a,b,f,h) for a,b in itertools.combinations(range(6),2) for f in range(3) for h in range(3)];need(tab['local_cells']==[list(x) for x in cells] and len(tab['records'])==6061,'complete table shape')
        for si,r in enumerate(tab['records']):
            need(r['signature_index']==si and r['minimum']==mins[si] and r['maximum']==maxs[si],'all818235 regenerated extrema pairs')
            for typ,ext in [('minimum',mins),('maximum',maxs)]:
                need(len(r[typ+'_witnesses'])==135,'complete attainer array')
                for ci,ti in enumerate(r[typ+'_witnesses']):need(ti in partition[sigs[si]] and values[ti][ci]==ext[si][ci],'all saved literal extremum attainers')
        gzsave(out/'independent_extrema.json.gz',bounds)
        groups=[]
        for col in range(60):
            s=tuple(a for a in range(12) if raw['L'][a][col])
            if s not in groups:groups.append(s)
        need(len(groups)==20 and all(len(s)==6 for s in groups),'fixed support groups');c=raw['core_adjacency'];g=[[12*int(i==j)-c[i][j]-sum(c[i][k]*c[k][j] for k in range(36))+2-int(i//12==j//12) for j in range(36)] for i in range(36)];need(g==raw['prescribed_Gram36'],'raw core Gram')
        gcells=[(a,b,f,h) for a,b in itertools.combinations(range(12),2) if a//2!=b//2 for f in range(3) for h in range(3)];localindex={cell:i for i,cell in enumerate(cells)};globalindex={cell:i for i,cell in enumerate(gcells)};terms=[[(gi,localindex[(s.index(a),s.index(b),f,h)]) for gi,s in enumerate(groups) if a in s and b in s] for a,b,f,h in gcells];targets=[g[12*f+a][12*h+b] for a,b,f,h in gcells];need(len(gcells)==540 and all(len(t)==5 for t in terms),'all540 five-term cells')
        def signature_ids(v):
            need(len(v)==720 and all(vv<=3 for vv in v),'720 counts');ids=[]
            for gi,s in enumerate(groups):
                need(all(sum(v[60*a+3*gi:60*a+3*gi+3])==(3 if a in s else 0) for a in range(12)),'literal support margins');ids.append(index[tuple(v[60*a+3*gi+f] for a in s for f in range(3))])
            return ids
        def screen(v):
            ids=signature_ids(v);lo=[sum(mins[ids[gi]][li] for gi,li in ts) for ts in terms];hi=[sum(maxs[ids[gi]][li] for gi,li in ts) for ts in terms];bad=[k for k,t in enumerate(targets) if not lo[k]<=t<=hi[k]];return ids,lo,hi,bad
        def failure(cert,ids,lo,hi,bad):
            need(bad and cert is not None and cert['cell_index']==bad[0],'lexicographic first failed cell');k=bad[0];a,b,f,h=gcells[k];need(cert['coordinates']==[a,b] and cert['fibres']==[f,h] and cert['target']==targets[k] and cert['lower']==lo[k] and cert['upper']==hi[k] and cert['violation']==('TARGET_BELOW_LOWER' if targets[k]<lo[k] else 'TARGET_ABOVE_UPPER'),'literal failed total')
            need(len(cert['terms'])==5,'five certificate terms')
            for rec,(gi,li) in zip(cert['terms'],terms[k]):
                si=ids[gi];need(rec['group']==gi and rec['support']==list(groups[gi]) and rec['signature_index']==si and rec['signature_counts']==list(sigs[si]) and rec['local_cell_index']==li and rec['local_cell']==list(cells[li]) and rec['class_size']==len(partition[sigs[si]]) and rec['minimum']==mins[si][li] and rec['maximum']==maxs[si][li],'complete class term')
                for typ,ext in [('minimum',mins),('maximum',maxs)]:
                    w=rec[typ+'_attainer'];ti=w['local_survivor_index'];need(ti in partition[sigs[si]] and w['word_indices']==list(triples[ti]) and w['colour_words']==[list(words[wi]) for wi in triples[ti]] and w['value']==values[ti][li]==ext[si][li],'literal full attainer')
        # Independently transport every local triple, count class and Gram cell.
        wi={w:i for i,w in enumerate(words)};ti={t:i for i,t in enumerate(triples)};local_transports=0
        for p in PERMS:
            inv=[p.index(i) for i in range(3)];wordmap=[wi[tuple(inv[x] for x in w)] for w in words]
            for t,s in zip(triples,signatures):
                image=tuple(sorted(wordmap[w] for w in t));need(image in ti and signatures[ti[image]]==tuple(s[3*a+p[f]] for a in range(6) for f in range(3)),'all local triple/signature fibre images');local_transports+=1
            need(all(g[12*f+a][12*h+b]==g[12*p[f]+a][12*p[h]+b] for a in range(12) for b in range(12) for f in range(3) for h in range(3)),'entire Gram fibre covariance')
        representatives=[];all_members={};rep_index={}
        for sub in join['completed_subset_records']:
            op=next(ROOT/p for p in sub['artifacts_sha256'] if p.endswith('/orbits.json'));pp=next(ROOT/p for p in sub['artifacts_sha256'] if p.endswith('/profiles.jsonl.gz'));profiles={}
            with gzip.open(pp,'rt') as f:
                for line in f:
                    r=json.loads(line);v=flatten(r['coordinate_group_fibre_counts']);need(digest(v)==r['profile_sha256'] and signature_ids(v)==r['group_signature_indices'],'literal labelled profile');need(r['index'] not in profiles and digest(v) not in all_members,'labelled uniqueness');profiles[r['index']]=(v,r);all_members[digest(v)]=(v,sub['subset_index'],r['index'])
            orbits=read(op);need(orbits['complete'],'complete orbit file')
            for r in orbits['orbits']:
                v=bytes(r['canonical_counts']);images={transform(v,p) for p in PERMS};dg=digest(v);need(v==min(images) and dg==r['canonical_fibre_profile_sha256'] and dg not in rep_index and r['orbit_size']==len(images)==len(r['members'])==6,'canonical complete orbit')
                seen=set()
                for member in r['members']:
                    vv,rawr=profiles[member['index']];need(vv in images and digest(vv)==member['profile_sha256'] and transform(vv,member['canonicalizing_fibre_permutation'])==v and rawr['canonical_fibre_profile_sha256']==dg,'each labelled transport');seen.add(vv)
                need(seen==images,'whole six-image population');rep=dict(digest=dg,subset_index=sub['subset_index'],exceptional_groups=sub['groups'],v=v,members=r['members'],source_orbits_path=key(op));representatives.append(rep);rep_index[dg]=rep
        need(len(representatives)==1548 and len(all_members)==9288,'whole population')
        included={};exc=read(D/'excluded_representatives.json.gz');sur=read(D/'surviving_representatives.json.gz');need(exc['complete'] and sur['complete'],'both lists complete')
        for excluded,obj in [(True,exc),(False,sur)]:
            for rec in obj['records']:
                dg=rec['canonical_fibre_profile_sha256'];need(dg not in included and dg in rep_index,'disjoint complete partition');rep=rep_index[dg];need(flatten(rec['counts'])==rep['v'] and rec['members']==rep['members'] and rec['subset_index']==rep['subset_index'] and rec['exceptional_groups']==rep['exceptional_groups'] and rec['orbit_size']==6 and rec['source_orbits_path']==rep['source_orbits_path'],'whole representative payload');included[dg]=(excluded,rec)
        need(set(included)==set(rep_index),'exact union')
        verified=[];hist=collections.Counter();fail_examples=[];orbit_checks=0;screen_seen=set()
        with gzip.open(D/'screens.jsonl.gz','rt') as f:
            for lineno,line in enumerate(f):
                rec=json.loads(line);dg=rec['canonical_fibre_profile_sha256'];need(dg not in screen_seen and dg==representatives[lineno]['digest'],'ordered unique full screens');screen_seen.add(dg);rep=rep_index[dg];ids,lo,hi,bad=screen(rep['v']);need(rec['subset_index']==rep['subset_index'] and rec['group_signature_indices']==ids and rec['lower_bounds']==lo and rec['upper_bounds']==hi and rec['failed_cell_indices']==bad,'all540 array entries and failed IDs')
                excluded,savedrec=included[dg];need(excluded==bool(bad) and savedrec['failed_cell_indices']==bad and savedrec['first_failure']==rec['first_failure'],'list/screen complete agreement')
                if bad:failure(rec['first_failure'],ids,lo,hi,bad);fail_examples.append((copy.deepcopy(rec),ids,lo,hi,bad)) if not fail_examples else None
                else:need(rec['first_failure'] is None,'no invented failure')
                for p in PERMS:
                    vv=transform(rep['v'],p);ii,ll,hh,bb=screen(vv);mapping=[globalindex[a,b,p[f],p[h]] for a,b,f,h in gcells];need(ll==[lo[k] for k in mapping] and hh==[hi[k] for k in mapping] and bool(bb)==bool(bad) and digest(vv) in all_members,'full labelled scalar transport');orbit_checks+=1
                hist.update(bad);verified.append(dict(canonical_fibre_profile_sha256=dg,failed_cell_indices=bad,labelled_images=6));
                if (lineno+1)%300==0:print(json.dumps(dict(checked=lineno+1,elapsed_seconds=time.perf_counter()-start)),flush=True)
        need(screen_seen==set(rep_index),'all1548 screens');negative=sum(bool(r['failed_cell_indices']) for r in verified);need(negative==756 and len(verified)-negative==792,'actual split');need({int(k):v for k,v in summary['failed_cell_histogram'].items()}==dict(hist),'complete failure histogram');gzsave(out/'independent_outcomes.json.gz',verified)
        historical=[]
        for rec in read(D/'historical_memberships.json')['records']:
            p=ROOT/rec['raw_path'];pin(p,rec['raw_sha256']);rawp=read(p);v=flatten(rawp['coordinate_group_fibre_counts']);ii,ll,hh,bb=screen(v);can=min(transform(v,p) for p in PERMS);dg=digest(can);cc=screen(can)[3];need(rec['historical_deviation_digest']==rawp['profile_sha256'] and rec['literal_full_count_sha256']==digest(v) and rec['canonical_full_count_sha256']==dg and rec['original_orientation_failed_cell_indices']==bb and rec['canonical_failed_cell_indices']==cc and rec['representative_screened'] and not rec['prior_exclusion_subtracted'],'historical digest/scope distinction');need(rec['exact_member_reference'] in rep_index[dg]['members'] and rec['exact_member_reference']['profile_sha256']==digest(v),'exact historical raw membership');need((not bb) if rec['name'] in ['first','third'] else bool(bb),'historical controls')
            if rec['name']=='second':k=globalindex[9,11,2,1];need(k in bb and hh[k]==1 and targets[k]==2,'known exact negative')
            historical.append(dict(name=rec['name'],raw_digest=digest(v),canonical_digest=dg,failed_cells=bb,previous_exclusion_subtracted=False))
        balanced=bytes(v for a in range(12) for s in groups for v in ([1,1,1] if a in s else [0,0,0]));need(not screen(balanced)[3],'balanced necessary relaxation positive')
        rejected=[]
        def reject(name,fn):
            try:fn()
            except (ValueError,KeyError,IndexError,TypeError):rejected.append(name)
            else:raise ValueError('accepted corruption '+name)
        rec,ids,lo,hi,bad=fail_examples[0];certificate=rec['first_failure']
        for name,edit in [('target',lambda c:c.__setitem__('target',c['target']+1)),('total',lambda c:c.__setitem__('upper',c['upper']+1)),('missing_term',lambda c:c['terms'].pop()),('group',lambda c:c['terms'][0].__setitem__('group',99)),('class_size',lambda c:c['terms'][0].__setitem__('class_size',0)),('signature',lambda c:c['terms'][0].__setitem__('signature_index',-1)),('extremum',lambda c:c['terms'][0].__setitem__('maximum',4)),('attainer',lambda c:c['terms'][0]['maximum_attainer'].__setitem__('local_survivor_index',31110))]:
            damaged=copy.deepcopy(certificate);edit(damaged);reject(name,lambda damaged=damaged:failure(damaged,ids,lo,hi,bad))
        reject('missing_failure',lambda:failure(certificate,ids,lo,hi,[]));reject('wrong_array',lambda:need(lo==[lo[0]+1]+lo[1:],'array equality'));reject('missing_union_member',lambda:need(set(list(included)[1:])==set(rep_index),'union'));reject('wrong_orbit_image',lambda:need(transform(representatives[0]['v'],[0,0,1]) in {transform(representatives[0]['v'],p) for p in PERMS},'bijective fibre action'))
        tiny=0
        for x in [(0,),(1,),(0,1),(0,2),(1,2)]:
            for y in [(0,),(1,),(0,1),(0,2),(1,2)]:
                vals=[a+b for a in x for b in y];need(min(vals)==min(x)+min(y) and max(vals)==max(x)+max(y),'finite extrema control');tiny+=1
        save(out/'controls.json',dict(historical=historical,balanced_positive=True,small_extrema_cases=tiny,corruptions_rejected=rejected));need(summary['complete'] and [summary[k] for k in ['representatives_total','representatives_checked','representatives_excluded','representatives_surviving','labelled_total','labelled_excluded','labelled_surviving']]==[1548,1548,756,792,9288,4536,4752],'all producer summary counts')
        ts=datetime.now(timezone.utc).isoformat();scope='The complete fixed-support exactly-eight count population with full local within-triplicate caps/Gram domains; scalar bounds only. No simultaneous factor conclusion for survivors.';limitations=['No prior historical profile exclusions are added or subtracted; they overlap this same population.','The792 representative/4752 labelled survivors only satisfy necessary scalar tests, not joint Gram choices, cross-group caps or a residual graph.','No target automorphism, unrestricted graph exclusion or whole-support exclusion.']
        binding=dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-SCALAR-EXCLUSIONS',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='All1548 global-fibre representatives of the independently complete9288 labelled exactly-eight count profiles were checked against all540 exact five-group scalar Gram intervals. Exactly756 representatives and their4536 labelled images violate at least one interval and cannot realize the prescribed Gram in the complete within-triplicate-cap domains. The remaining792 representatives/4752 labelled images survive only these necessary scalar tests. Historical literal profiles are included without additive exclusion counting.',scope=scope,assumptions=['Pinned fixed six-prism Hadamard support, exactly-eight count census and complete local domain convention.'],dependencies=[dict(id='C-FIXED-HADAMARD-COMPLETE-EIGHT-COUNT-PROFILE-CENSUS',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='coverage')],verifier='/root/structural_attack',producer='/root/eight_domain_audit',method='Independent bitmask/raw-pair catalogue enumeration, complete signature extrema, all labelled scalar arrays, direct fibre transports and full failure certificates, plus historical/corruption controls.',shared_components=['Raw independently gated census and catalogue data; standard-library integer operations.','No producer or repository checker imports; saved interval table was checked against regenerated extrema, not trusted for arithmetic.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},limitations=limitations,artifact_availability='LOCAL_ONLY',availability_reason='Awaiting parent publication.',external_review=None,external_review_reason='No external review asserted.',created_at=ts,updated_at=ts);save(out/'claim_binding.json',binding)
        report=dict(status='INDEPENDENT_EXACT_EIGHT_SCALAR_INTERVAL_SCREEN_PASS',created_at=ts,inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},local_triples_enumerated=117480,local_survivors=31110,signature_classes=6061,local_extrema_cells=6061*135,local_fibre_transports=local_transports,canonical_scalar_cells=1548*540,labelled_scalar_cells=orbit_checks*540,representatives_checked=1548,labelled_profiles=9288,representatives_excluded=756,labelled_excluded=4536,representatives_surviving=792,labelled_surviving=4752,first_failure_certificates=756,corruptions_rejected=rejected,claim_id=binding['id'],claim_revision=1,scope=scope,limitations=limitations,native_calls=0,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),python=platform.python_version(),command=[sys.executable,*sys.argv],elapsed_seconds=time.perf_counter()-start);save(out/'summary.json',report);print(json.dumps(dict(summary_sha256=sha(out/'summary.json'),binding_sha256=sha(out/'claim_binding.json'),elapsed_seconds=report['elapsed_seconds'])))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),inputs_sha256=pins));raise
if __name__=='__main__':main()
