"""Independent exhaustive Cartesian census via exact integer vector batches."""
from pathlib import Path
from itertools import product, permutations
from collections import defaultdict, Counter
from datetime import datetime, timezone
import argparse, copy, gzip, hashlib, json, math, platform, subprocess, sys, time
import numpy as np
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/';D=B+'exact_eight_profile_join/';GATE=I+'exact_eight_profile_preflight/summary.json';DOMAINS=I+'exact_eight_profile_preflight/approved_surviving_subsets.json';COORD=B+'hadamard_coordinate_marginal_domains/'
PINS={D+'summary.json':'77ae94974105ffe11d77e88d88e4d7e35670e13118d868def35a69f2079abb70',GATE:'1a120763c8d97677e0339828abf14cba2394e71f5d6459f153e29f42c534541f'}
FIBRES=list(permutations(range(3)))
def need(x,m):
    if not x:raise ValueError(m)
def sha(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def save_gzip(p,x):
    with p.open('xb')as f:
        with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0)as z:z.write((json.dumps(x,separators=(',',':'))+'\n').encode())
def same(a,b):need(a==b,'complete exact comparison')
def packed(values):
    need(all(type(x)is int and 0<=x<4 for x in values),'base-four digits')
    code=sum(x<<(2*i)for i,x in enumerate(values));need(code<2**(2*len(values)),'packing range');return code
def batch(doms,lo,hi):
    q=np.arange(lo,hi,dtype=np.uint64);rows=[]
    for d in reversed(doms):
        rows.append(np.asarray(d,dtype=np.int64)[q%len(d)]);q=q//len(d)
    need(not np.any(q),'mixed-radix range');return np.asarray(rows[::-1],dtype=np.int64)
def membership(sorted_codes,values):
    if not len(sorted_codes):return np.zeros(values.shape,dtype=bool)
    idx=np.searchsorted(sorted_codes,values);valid=idx<len(sorted_codes)
    result=np.zeros(values.shape,dtype=bool);result[valid]=sorted_codes[idx[valid]]==values[valid];return result
def image(flat,p):return tuple(flat[k+p[f]]for k in range(0,len(flat),3)for f in range(3))
def canonical(flat):
    images=[(image(flat,p),p)for p in FIBRES];v,p=min(images);return v,p,len({x for x,p in images})
def controls():
    cases=rows=0
    for sizes in product([1,2,3],repeat=4):
        ds=[list(range(3*i,3*i+n))for i,n in enumerate(sizes)];truth=list(product(*ds));found=[]
        for start in range(0,len(truth),7):found.extend(map(tuple,batch(ds,start,min(start+7,len(truth))).T.tolist()))
        same(found,truth);cases+=1;rows+=len(truth)
    for mask in range(256):
        allowed=[i for i in range(8)if mask>>i&1];same(membership(np.asarray(allowed,dtype=np.uint64),np.arange(10,dtype=np.uint64)).tolist(),[i in allowed for i in range(10)])
    for digits in product(range(4),repeat=3):
        code=packed(digits);same(tuple((code>>(2*j))&3 for j in range(3)),digits)
    for flat,size in [((1,1,1),1),((0,0,3),3),((0,1,2),6)]:same(canonical(flat)[2],size)
    extremes=np.array([0,2**36-1],dtype=np.uint64);same(membership(extremes,np.array([0,1,2**36-2,2**36-1],dtype=np.uint64)).tolist(),[True,False,False,True])
    return dict(mixed_radix_domain_shapes=cases,mixed_radix_rows=rows,membership_sets=256,triplet_pack_controls=64,nonfree_orbit_sizes=[1,3,6],extreme_36bit_membership=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    def pin(p,h=None):
        digest=sha(p);need(h is None or digest==h,'identity '+str(p));need(p not in pins or pins[p]==digest,'consistent binding');pins[str(p)]=digest
    try:
        for p,h in PINS.items():pin(p,h)
        summary=read(D+'summary.json');gate=read(GATE);need(gate['status']=='INDEPENDENT_EXACT_EIGHT_PROFILE_PREFLIGHT_PASS','coverage gate')
        for obj in [summary,gate]:
            for field in ['inputs_sha256','outputs_sha256']:
                for p,h in obj[field].items():pin(p,h)
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_EXACT_EIGHT_PROFILE_JOIN.md','uv.lock','pyproject.toml']:pin(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),versions=dict(python=platform.python_version(),numpy=np.__version__),inputs_sha256=pins,limit_seconds=120,Cartesian_batch_size=65536,arithmetic='uint64, largest signature <2^36; no floating point',solver_calls=0))
        calibration=controls();raw=read(B+'hadamard20_support/six_prism.json');groups=[]
        for x in raw['support_columns']:
            if tuple(x)not in groups:groups.append(tuple(x))
        local=read(B+'hadamard_triplicate_counts/local_triples.json');words=local['words'];sigs=sorted({tuple(sum(int(words[w][p]==f)for w in t)for p in range(6)for f in range(3))for t in local['survivors']});need(len(sigs)==6061,'signature universe')
        codes=[packed(s)for s in sigs];need(len(set(codes))==6061 and all(tuple((code>>(2*j))&3 for j in range(18))==s for code,s in zip(codes,sigs)),'injective full local encoding');code_to_id={x:i for i,x in enumerate(codes)};balanced_code=packed((1,)*18);active_codes=np.asarray(sorted(x for x in codes if x!=balanced_code),dtype=np.uint64)
        coord=[read(COORD+f'coordinate_{a:02d}.json')['ordered_three_fibre_choices']for a in range(12)]
        count_arrays=[np.asarray([[packed(v)for v in row['full20_count_signature']]for row in choices],dtype=np.uint64)for choices in coord]
        approved=sorted(read(DOMAINS)['records'],key=lambda r:r['groups']);need(len(approved)==67,'complete approved universe');same(summary['selected_subsets'],[r['groups']for r in approved]);need(summary['complete']and summary['incomplete_subset']is None and summary['unattempted_subsets']==[],'producer completion')
        witnesses={}
        for label in ['count_master_sat_outcome','count_master_eight_orbit_cut_sat_outcome','count_master_partial_cut_sat_outcome']:
            table=read(I+label+'/independent_count_profile.json')['coordinate_group_fibre_counts'];flat=tuple(x for row in table for counts in row for x in counts);witnesses[flat]=dict(label=label,matches=[])
        results=[];total_checked=total_profiles=total_orbits=0;canonical_records=[];seen_global=set();saved_control=None
        for si,rec in enumerate(tqdm(approved,desc='Independent exhaustive count subsets')):
            E=rec['groups'];ds=rec['coordinate_choice_indices'];size=math.prod(map(len,ds));found=[]
            for low in range(0,size,65536):
                ids=batch(ds,low,min(size,low+65536));valid=np.ones(ids.shape[1],dtype=bool)
                for g,support in enumerate(groups):
                    key=np.zeros(ids.shape[1],dtype=np.uint64)
                    for pos,a in enumerate(support):key|=count_arrays[a][ids[a],g]<<np.uint64(6*pos)
                    valid&=membership(active_codes,key)if g in E else key==balanced_code
                found.extend(map(tuple,ids[:,valid].T.tolist()));total_checked+=ids.shape[1]
                need(time.monotonic()-start<115,'exhaustive audit budget')
            folder=D+f'subset_{si:03d}/';records=[json.loads(line)for line in gzip.decompress((ROOT/folder/'profiles.jsonl.gz').read_bytes()).splitlines()]
            claimed=[tuple(r['coordinate_choice_indices'])for r in records];need(len(claimed)==len(set(claimed)),'distinct raw records');same(set(found),set(claimed));need(len(found)==len(set(found)),'no duplicate Cartesian visits')
            orbit_members=defaultdict(list);orbit_values={};profile_flats={};complete_record={}
            for j,r in enumerate(records):
                same(r['index'],j);ids=r['coordinate_choice_indices'];table=[coord[a][ids[a]]['full20_count_signature']for a in range(12)];same(r['coordinate_group_fibre_counts'],table)
                actual_groups=[g for g,s in enumerate(groups)if any(table[a][g]!=[1,1,1]for a in s)];same(actual_groups,E);same(r['exceptional_groups'],E)
                signature_ids=[code_to_id[packed(tuple(x for a in s for x in table[a][g]))]for g,s in enumerate(groups)];same(r['group_signature_indices'],signature_ids)
                flat=tuple(x for row in table for counts in row for x in counts);canonical_flat,p,orbit_size=canonical(flat);digest=hashlib.sha256(bytes(flat)).hexdigest();cdigest=hashlib.sha256(bytes(canonical_flat)).hexdigest()
                same(r['profile_sha256'],digest);same(r['canonical_fibre_profile_sha256'],cdigest);same(r['canonicalizing_fibre_permutation'],list(p));same(r['fibre_orbit_size'],orbit_size)
                need(flat not in profile_flats and flat not in seen_global,'global literal uniqueness');profile_flats[flat]=j;seen_global.add(flat)
                if flat in witnesses:witnesses[flat]['matches'].append(dict(subset=si,index=j,byte_profile_sha256=digest))
                orbit_members[cdigest].append(dict(index=j,profile_sha256=digest,canonicalizing_fibre_permutation=list(p)));orbit_values[cdigest]=(canonical_flat,orbit_size);complete_record[flat]=r
            expected_orbits=[]
            for digest in sorted(orbit_members):
                canonical_flat,os=orbit_values[digest];members=orbit_members[digest];images={image(canonical_flat,p)for p in FIBRES}
                need(len(images)==os==len(members)and all(x in profile_flats for x in images),'all actual disjoint orbit images')
                expected_orbits.append(dict(canonical_fibre_profile_sha256=digest,canonical_counts=list(canonical_flat),orbit_size=os,members=members))
                cr=complete_record[canonical_flat];canonical_records.append(dict(subset_index=si,groups=E,representative_profile_index=cr['index'],canonical_fibre_profile_sha256=digest,coordinate_choice_indices=cr['coordinate_choice_indices'],group_signature_indices=cr['group_signature_indices'],coordinate_group_fibre_counts=cr['coordinate_group_fibre_counts'],orbit_size=os))
            saved_orbits=read(folder+'orbits.json');same(saved_orbits,dict(complete=True,orbits=expected_orbits));stats=read(folder+'summary.json');need(stats['complete']and stats['subset_index']==si,'subset completeness');same(stats['groups'],E);same(stats['labelled_profiles'],len(records));same(stats['fibre_orbits'],len(expected_orbits))
            result=dict(subset_index=si,groups=E,Cartesian_assignments_checked=size,labelled_profiles=len(records),fibre_orbits=len(expected_orbits),orbit_size_histogram=dict(Counter(os for _,os in orbit_values.values())))
            save(out/f'subset_{si:03d}.json',result);results.append(result);total_profiles+=len(records);total_orbits+=len(expected_orbits)
            if records and saved_control is None:saved_control=(copy.deepcopy(records[0]),copy.deepcopy(expected_orbits[0]))
            need(time.monotonic()-start<119,'whole raw/orbit audit budget')
        need(total_checked==7122626 and total_profiles==9288 and total_orbits==1548,'complete actual census');same(summary['labelled_profiles'],total_profiles);same(summary['fibre_orbits'],total_orbits);need(all(len(x['matches'])==1 for x in witnesses.values()),'all three exact prior witnesses included')
        rejected=[]
        def reject(label,fn):
            try:fn()
            except(ValueError,KeyError,TypeError,IndexError):rejected.append(label)
            else:raise ValueError('corrupt control accepted '+label)
        original,orbit=saved_control
        for label,mutation in [('raw_count',lambda r:r['coordinate_group_fibre_counts'][0][0].__setitem__(0,r['coordinate_group_fibre_counts'][0][0][0]+1)),('local_signature',lambda r:r['group_signature_indices'].__setitem__(0,-1)),('digest',lambda r:r.__setitem__('profile_sha256','0'*64)),('orbit_size',lambda r:r.__setitem__('fibre_orbit_size',1))]:
            wrong=copy.deepcopy(original);mutation(wrong);reject(label,lambda wrong=wrong:same(wrong,original))
        wrong=copy.deepcopy(orbit);wrong['members']=wrong['members'][:-1];reject('missing_orbit_member',lambda:same(wrong,orbit))
        reject('missing_subset',lambda:same(len(results[:-1]),67));reject('invented_complete_total',lambda:same(total_profiles+1,9288))
        reject('duplicate_profile',lambda:need(len({(1,2),(1,2)})==2,'duplicate tuples'))
        calibration.update(rejected=rejected,known_raw_count_witnesses=list(witnesses.values()),full_Cartesian_population=total_checked,complete_labelled_profiles=total_profiles,complete_fibre_orbits=total_orbits)
        save(out/'controls.json',calibration);save_gzip(out/'canonical_representatives.json.gz',dict(records=canonical_records,complete=True,labelled_profiles=total_profiles,scope='Complete necessary exactly-eight count CSP; no earlier exclusion removed.'))
        stamp=datetime.now(timezone.utc).isoformat();binding=dict(id='C-FIXED-HADAMARD-COMPLETE-EIGHT-COUNT-PROFILE-CENSUS',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='The complete exactly-eight count-table CSP remaining after the verified4184-subset reduction has9288 distinct labelled count profiles across67 subsets. Their simultaneous global fibre relabellings form1548 disjoint complete orbits, each of size6 as individually checked. All7122626 Cartesian assignments were independently evaluated, and every saved raw count table, local signature and orbit member was checked. No earlier literal exclusion is subtracted.',scope='Complete finite necessary count relaxation on the frozen six-prism Hadamard support with exactly eight unbalanced groups and inherited within-triplicate-cap catalogue. No Gram factor, cross-group cap, residualD or target graph is asserted.',assumptions=['Verified exhaustive reduction to the exact67 saved coordinate-domain products.','Pinned complete raw catalogue and coordinate choices.'],dependencies=[dict(id='C-FIXED-HADAMARD-EIGHT-COUNT-TABLE-SUBSET-REDUCTION',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-COMPLETE-COORDINATE-MARGINAL-DOMAINS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='premise')],verifier='/root',producer='/root/eight_domain_audit',method='Exhaustive mixed-radix Cartesian batches, exact36-bit signature membership, every literal saved count and all fibre images; independent of producer DFS.',shared_components=['Prior independent preflight/domain/census coverage is trusted. No producer imports.','Pinned NumPy uint64 integer operations, Python standard library and raw artifacts are shared trusted components.'],inputs_sha256=pins,limitations=['These counts measure this necessary count CSP only, not factors, graphs, search difficulty or target-wide coverage.','Relabelling orbits do not assume a target automorphism.','All prior count witnesses are retained; no exclusion union is inferred.'],created_at=stamp,updated_at=stamp);save(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_COMPLETE_EXACT_EIGHT_PROFILE_JOIN_PASS',timestamp=stamp,inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT))for p in out.iterdir()if p.is_file()},checked_subsets=67,Cartesian_assignments_checked=total_checked,labelled_profiles=total_profiles,complete_fibre_orbits=total_orbits,controls_rejected=len(rejected),solver_calls=0,native_calls=0,shared_components=binding['shared_components'],elapsed_seconds=time.monotonic()-start);save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha((out/'summary.json').relative_to(ROOT)),binding_sha256=sha((out/'claim_binding.json').relative_to(ROOT)))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__).relative_to(ROOT))));raise
if __name__=='__main__':main()
