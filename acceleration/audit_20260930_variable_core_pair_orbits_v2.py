"""Independent exact ordered-pair transports and CNF suffix checking; no producer imports."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import file_digest, sha256
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import io
import json
import platform
import subprocess
import sys
import time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20260930_variable_core_factor_cnf'
RAW=ROOT/'acceleration/results/20260930_variable_core_pair_orbits'
FIRST=ROOT/'acceleration/results/20260930_variable_core_m1_orbits'
CENSUS=ROOT/'acceleration/results/20260930_triangle_matching_pair_census_v2'
PROOF=ROOT/'docs/AUDIT_20260930_VARIABLE_CORE_PAIR_ORBITS.md'
GATES={
 ROOT/'acceleration/results/20260930_independent_review/triangle_matching_pair_census/summary.json':('085748fd2ebb03bdb7ea6048d782be0c17ce8cadef4ea32028cb58ca6b0efb79','INDEPENDENT_TRIANGLE_ORDERED_MATCHING_PAIR_CENSUS_PASS'),
 ROOT/'acceleration/results/20260930_independent_review/variable_core_m1_orbits/summary.json':('ef13877c79a1115cf34a105a9704bb58c0ad981189dfe6acda9b4de4a27d6584','INDEPENDENT_VARIABLE_CORE_M1_ORBIT_NORMALIZATION_PASS'),
 ROOT/'acceleration/results/20260930_independent_review/variable_core_factor_cnf_v2/summary.json':('ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0','INDEPENDENT_VARIABLE_CORE_FACTOR_CNF_ENCODING_PASS'),
 ROOT/'acceleration/results/20260930_independent_review/unrestricted_triangle_factor/summary.json':('a7d470ccf10df7dff77884c8bd1fe4784234ac80bc4e1b684e0050c3e33a4acd','INDEPENDENT_UNRESTRICTED_TRIANGLE_FACTOR_NORMALIZATION_PASS')}

def need(ok,s):
    if not ok:raise ValueError(s)
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def digest(p):
    with p.open('rb') as f:return file_digest(f,'sha256').hexdigest()
def pairs_object(items):
    d={}
    for k,v in items:need(k not in d,'duplicate JSON key');d[k]=v
    return d
def read(p):return json.loads(p.read_bytes(),object_pairs_hook=pairs_object)
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def matching_universe(n):
    result=[];mate=[-1]*n
    def visit():
        if -1 not in mate:result.append(tuple(mate));return
        a=mate.index(-1)
        for b in range(a+1,n):
            if mate[b]!=-1:continue
            mate[a]=b;mate[b]=a;visit();mate[a]=mate[b]=-1
    visit();return result

def bijection(h,n):
    need(type(h)is list and len(h)==n and all(type(x)is int for x in h) and sorted(h)==list(range(n)),'coordinate bijection')

def check_map(h,source,target,m0,m1=None):
    n=len(m0);bijection(h,n)
    need(all(h[m0[i]]==m0[h[i]] for i in range(n)),'M0 edge preservation')
    if m1 is not None:need(all(h[m1[i]]==m1[h[i]] for i in range(n)),'first representative edge preservation')
    need(all(h[source[i]]==target[h[i]] for i in range(n)),'second/source matching edge transport')
    labels=[q for q in combinations(range(n),2) if m0[q[0]]!=q[1]];index={q:i for i,q in enumerate(labels)}
    images=[]
    for a,b in labels:
        pair=tuple(sorted((h[a],h[b])));need(pair in index,'C0 image remains nonmatching');images.append(index[pair])
    need(sorted(images)==list(range(len(labels))),'all C0 column images bijective')
    return images

def conjugated(q,h):
    # Independent direct labelled edge assignment, not producer group traversal.
    result=[None]*len(q)
    for i,j in enumerate(q):result[h[i]]=h[j]
    need(all(x is not None for x in result),'complete conjugated matching')
    return tuple(result)

def ordered_records(rows,total):
    need(len(rows)==total,'complete record count')
    need(all(type(r['matching_index'])is int for r in rows),'integer record indices')
    need([r['matching_index'] for r in rows]==list(range(total)),'ordered complete unique matching indices')

def suffix(reps):
    ids={(g,a,b):1441+66*(g-1)+i for g in (1,2) for i,(a,b) in enumerate(combinations(range(12),2))}
    selectors=list(range(110905,114485));need(len(reps)==len(selectors),'selector count')
    clauses=[selectors]
    for v,r in zip(selectors,reps,strict=True):
        for g in (1,2):
            edge_set=[(a,b) for a,b in combinations(range(12),2) if r[f'M{g}'][a]==b]
            need(len(edge_set)==6,'representative matching edges')
            clauses.extend([[-v,ids[g,a,b]] for a,b in edge_set])
    return clauses,ids

def exact_bytes(base,augmented,clauses,variables=110904,base_count=518160,selectors=3580):
    need(base.readline()==f'p cnf {variables} {base_count}\n'.encode(),'base header')
    need(augmented.readline()==f'p cnf {variables+selectors} {base_count+len(clauses)}\n'.encode(),'augmented header')
    body_hash=sha256();body_bytes=0
    for b in iter(lambda:base.read(1<<20),b''):
        need(augmented.read(len(b))==b,'exact complete original body');body_hash.update(b);body_bytes+=len(b)
    tail=b''.join((' '.join(map(str,c))+' 0\n').encode() for c in clauses)
    need(augmented.read()==tail,'exact only independently derived suffix')
    return dict(original_body_bytes=body_bytes,original_body_sha256=body_hash.hexdigest(),suffix_bytes=len(tail),suffix_sha256=sha256(tail).hexdigest(),suffix_clauses=len(clauses))

def selector_controls():
    mm=matching_universe(4);choices=list(product(mm,repeat=2));edges=list(combinations(range(4),2));cases=0
    selectors=list(range(13,22));clauses=[selectors]
    for v,(a,b) in zip(selectors,choices):
        for g,m in enumerate([a,b]):clauses.extend([[-v,1+6*g+i] for i,(u,w) in enumerate(edges) if m[u]==w])
    for index,choice in enumerate(choices):
        edge_values=[int(m[u]==w) for m in choice for u,w in edges]
        for bits in product((0,1),repeat=9):
            values=[0,*edge_values,*bits]
            actual=all(any(values[abs(l)]==int(l>0) for l in c) for c in clauses)
            need(actual==(bits==tuple(int(j==index) for j in range(9))),'literal selector truth table');cases+=1
    # Full small-universe composition: independently choose two-stage maps on n4.
    m0=mm[0];group=[list(h) for h in permutations(range(4)) if all(h[m0[i]]==m0[h[i]] for i in range(4))]
    for a,b in choices:
        first=min(conjugated(a,h) for h in group);h=next(h for h in group if conjugated(a,h)==first)
        moved=conjugated(b,h);stabilizer=[k for k in group if conjugated(first,k)==first]
        second=min(conjugated(moved,k) for k in stabilizer);k=next(k for k in stabilizer if conjugated(moved,k)==second)
        joined=[k[h[i]] for i in range(4)];check_map(joined,a,first,m0);check_map(joined,b,second,m0)
    return dict(selector_boolean_cases=cases,exhaustive_n4_ordered_pair_compositions=len(choices))

def covariance(h,m1,m2,stage):
    # Controls use intentionally arbitrary binary arrays, not feasible factors.
    n=12;labels=[q for q in combinations(range(n),2) if q[1]!=(q[0]^1)];column_index={q:i for i,q in enumerate(labels)}
    cm=[column_index[tuple(sorted((h[a],h[b])))] for a,b in labels];rm=[g*n+h[a] for g in range(3) for a in range(n)]
    p=[(5*i+stage+1)%12 for i in range(12)]
    def core(q1,q2,perm):
        c=[[0]*36 for _ in range(36)]
        for g,q in enumerate([[i^1 for i in range(12)],q1,q2]):
            for i,j in enumerate(q):c[g*n+i][g*n+j]=1
        for i in range(n):
            for a,b in [(i,n+i),(i,2*n+i),(n+i,2*n+perm[i])]:c[a][b]=c[b][a]=1
        return c
    c=core(m1,m2,p);d=core(conjugated(m1,h),conjugated(m2,h),conjugated(p,h))
    need(all(d[rm[i]][rm[j]]==c[i][j] for i in range(36) for j in range(36)),'raw core covariance including arbitrary P')
    f=[[int(i in q) for q in labels] for i in range(12)]+[[int((17*i+11*j+stage)%7<3) for j in range(60)] for i in range(24)]
    ff=[[0]*60 for _ in range(36)]
    for i in range(36):
        for j in range(60):ff[rm[i]][cm[j]]=f[i][j]
    need(ff[:12]==f[:12],'canonical C0 covariance')
    def expressions(c,f):
        rows=[set(j for j,v in enumerate(row) if v) for row in c]
        gram=[[12*int(i==j)+2-c[i][j]-len(rows[i]&rows[j])-int(i//12==j//12) for j in range(36)] for i in range(36)]
        rowsets=[set(j for j,v in enumerate(row) if v) for row in f]
        actual=[[len(rowsets[i]&rowsets[j]) for j in range(36)] for i in range(36)]
        mixed=[[f[i][j]+sum(f[k][j] for k in rows[i]) for j in range(60)] for i in range(36)]
        cols=[set(i for i in range(36) if f[i][j]) for j in range(60)]
        overlap=[[len(cols[i]&cols[j]) for j in range(60)] for i in range(60)]
        return gram,actual,mixed,overlap
    a=expressions(c,f);b=expressions(d,ff)
    for z in (0,1):need(all(a[z][i][j]==b[z][rm[i]][rm[j]] for i in range(36) for j in range(36)),'Gram expression covariance')
    need(all(a[2][i][j]==b[2][rm[i]][cm[j]] for i in range(36) for j in range(60)),'mixed cap covariance')
    need(all(a[3][i][j]==b[3][cm[i]][cm[j]] for i in range(60) for j in range(60)),'column cap covariance')
    need(all(sum(f[i])==sum(ff[rm[i]]) for i in range(36)),'row margins covariance')
    need(all(sum(f[g*12+i][j] for i in range(12))==sum(ff[g*12+i][cm[j]] for i in range(12)) for g in range(3) for j in range(60)),'fibre margins covariance')
    return dict(stage=stage,P=p,not_a_research_factor=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(p,expected=None):
        got=digest(p)
        if expected is not None:need(got==expected,'exact input identity '+key(p))
        if key(p) in bindings:need(bindings[key(p)]==got,'unchanged repeated input')
        bindings[key(p)]=got;return got
    try:
        for gate,(sha,status) in GATES.items():
            bind(gate,sha);raw=read(gate);need(raw['status']==status,'premise status')
            for name,identity in raw['inputs_sha256'].items():bind(ROOT/name,identity)
        bind(RAW/'summary.json','f9207830da583bc3f4d88862875768f4758a5d5ea7a4daf1e313af5a5d094429')
        for name,record in read(RAW/'summary.json')['outputs'].items():
            p=ROOT/name;bind(p,record['sha256']);need(p.stat().st_size==record['bytes'],'producer output byte length')
        for p in [Path(__file__),PROOF,ROOT/'docs/AUDIT_20260930_VARIABLE_CORE_PAIR_ORBITS_V2_ADDENDUM.md',ROOT/'acceleration/audit_20260930_variable_core_pair_orbits.py',ROOT/'acceleration/results/20260930_independent_review/variable_core_pair_orbits/failure.json',ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'acceleration/theory_20260930_variable_core_pair_orbits.py',ROOT/'acceleration/theory_20260930_variable_core_pair_orbits_spec.md']:bind(p)
        generated=matching_universe(12);matchings=read(CENSUS/'matchings.json');lookup={tuple(q):i for i,q in enumerate(matchings)}
        need(len(lookup)==len(generated)==len(matchings)==10395 and set(lookup)==set(generated),'complete independently generated matching universe')
        first=read(FIRST/'transports.json');coverage=read(RAW/'coverage.json');extension=read(RAW/'extension.json');model=read(BASE/'model.json');m0=list(i^1 for i in range(12))
        need(first['M0']==m0,'standard M0');ordered_records(first['records'],10395)
        need(len(first['representatives'])==11,'eleven first representatives');first_counts=Counter()
        for rec in first['records']:
            s=rec['representative'];need(type(s)is int and 0<=s<11,'first-stage index')
            check_map(rec['coordinate_permutation'],matchings[rec['matching_index']],first['representatives'][s],m0);first_counts[s]+=1
        need(coverage['first_transports_path']==key(FIRST/'transports.json') and coverage['first_transports_sha256']==digest(FIRST/'transports.json'),'first transport recipe identity')
        need(coverage['first_transport_audit_sha256']==GATES[ROOT/coverage['first_transport_audit']][0],'first gate reference')
        expected_reps=[];stage_records=[];stage_reports=[];covariance_records=[]
        need(len(coverage['stages'])==11,'complete stage metadata')
        for s in tqdm(range(11),desc='Independent complete pair transports'):
            census=read(CENSUS/f'stage_{s:02d}.json');path=RAW/f'stage_{s:02d}_transports.json';data=read(path);m1=census['M1']
            need(m1==first['representatives'][s]==data['M1'],'first representative exact membership')
            need(census['first_members']==[r['matching_index'] for r in first['records'] if r['representative']==s],'complete frozen first orbit membership')
            need(census['first_orbit_size']==first_counts[s],'first orbit size')
            need(data['first_stage']==s and data['source_stage']==key(CENSUS/f'stage_{s:02d}.json') and data['source_stage_sha256']==digest(CENSUS/f'stage_{s:02d}.json'),'source stage binding')
            need(data['matching_universe_path']==key(CENSUS/'matchings.json') and data['matching_universe_sha256']==digest(CENSUS/'matchings.json'),'stage universe binding')
            membership={};global_ids=[]
            for local,orb in enumerate(census['second_orbits']):
                index=len(expected_reps);global_ids.append(index);expected_reps.append(dict(pair_representative_index=index,first_stage=s,second_orbit=local,M1=m1,M2=orb['representative']))
                need(orb['representative_index']==lookup[tuple(orb['representative'])] and orb['representative_index'] in orb['members'] and orb['orbit_size']==len(orb['members']),'frozen second orbit indexing')
                for member in orb['members']:
                    need(member not in membership,'disjoint saved second orbit membership');membership[member]=(local,index)
            need(set(membership)==set(range(10395)),'complete census second-stage universe')
            need(data['pair_representative_indices']==global_ids and data['records_count']==10395 and data['P_restriction'] is False,'stage scope metadata')
            ordered_records(data['records'],10395);column_hash=sha256()
            for rec in data['records']:
                index=rec['matching_index'];local,gid=membership[index]
                need(type(rec['second_orbit'])is int and type(rec['pair_representative_index'])is int and (rec['second_orbit'],rec['pair_representative_index'])==(local,gid),'exact frozen orbit membership')
                cols=check_map(rec['coordinate_permutation'],matchings[index],expected_reps[gid]['M2'],m0,m1)
                column_hash.update(bytes(cols))
            reported=coverage['stages'][s]
            need(reported==dict(first_stage=s,transports_path=key(path),transports_sha256=digest(path),pair_representatives=len(global_ids),covered_second_matchings=10395,first_orbit_size=first_counts[s]),'exact stage coverage metadata')
            stage_records.append(data['records']);stage_reports.append(dict(stage=s,records=10395,pair_representatives=len(global_ids),first_orbit_size=first_counts[s],canonical_C0_images_checked=10395*60,derived_column_map_stream_sha256=column_hash.hexdigest(),stream_format='60 byte-valued column indices per record, ordered by matching_index; derivable from bound raw coordinate maps.'))
            h=next((r['coordinate_permutation'] for r in reversed(data['records']) if r['coordinate_permutation']!=list(range(12))),list(range(12)))
            covariance_records.append(covariance(h,m1,matchings[(997+37*s)%10395],s))
        need(len(expected_reps)==3580 and len({(tuple(r['M1']),tuple(r['M2'])) for r in expected_reps})==3580,'3580 distinct ordered representative pairs')
        need(coverage['pair_representatives']==extension['representative_pairs']==expected_reps,'every representative exact frozen order')
        need((coverage['matching_universe'],coverage['first_stages'],coverage['second_transport_records'],coverage['complete_labelled_pair_population'])==(10395,11,114345,108056025),'complete population metadata')
        need(sum(first_counts.values())*10395==108056025 and coverage['population_materialized'] is False,'two-stage coverage population')
        controls=read(RAW/'composition_controls.json');need(controls['count']==len(controls['records'])==10395 and controls['exhaustive_labelled_pair_check'] is False,'composition controls scope')
        for i,record in enumerate(controls['records']):
            j=(37*i+997)%10395;fr=first['records'][i];s=fr['representative'];h=fr['coordinate_permutation'];moved=lookup[conjugated(matchings[j],h)];sr=stage_records[s][moved];k=sr['coordinate_permutation'];joined=[k[h[a]] for a in range(12)];gid=sr['pair_representative_index'];rep=expected_reps[gid]
            expected=dict(first_matching_index=i,second_matching_index=j,first_stage=s,normalized_second_matching_index=moved,pair_representative_index=gid,composed_coordinate_permutation=joined)
            need(record==expected,'exact deterministic sampled composition recipe');check_map(joined,matchings[i],rep['M1'],m0);check_map(joined,matchings[j],rep['M2'],m0)
        clauses,ids=suffix(expected_reps)
        expected_matching=[dict(id=v,fibre=g,endpoints=[a,b]) for (g,a,b),v in ids.items()]
        need(model['matching_variables']==expected_matching,'all132 matching primary IDs independently reconstructed')
        need(extension['selectors']==list(range(110905,114485)) and extension['appended_clauses']==clauses and (extension['variables'],extension['clauses'])==(114484,561121),'exact selector clause metadata')
        for field,path in [('base_cnf',BASE/'instance.cnf'),('base_model',BASE/'model.json'),('coverage',RAW/'coverage.json')]:need(extension[field+'_path']==key(path) and extension[field+'_sha256']==digest(path),'extension input binding')
        need(all(extension[x] is False for x in ['P_restricted','component_restrictions','target_automorphism_assumed','residual_D_included']),'precise scope flags')
        with (BASE/'instance.cnf').open('rb') as a,(RAW/'instance.cnf').open('rb') as b:byte_record=exact_bytes(a,b,clauses)
        small=selector_controls();negative=[]
        def reject(label,fun):
            try:fun()
            except (ValueError,KeyError,IndexError,TypeError):negative.append(label)
            else:raise AssertionError('corruption accepted '+label)
        rec=stage_records[0][0];source=matchings[0];target=expected_reps[rec['pair_representative_index']]['M2'];h=rec['coordinate_permutation']
        bad=list(h);bad[0]=bad[1];reject('nonbijective_map',lambda:check_map(bad,source,target,m0,m0))
        bad2=list(h);bad2[0]=True;reject('Boolean_map_entry',lambda:check_map(bad2,source,target,m0,m0))
        reject('noncentralizing_map',lambda:check_map([0,2,1]+list(range(3,12)),source,target,m0,m0))
        reject('wrong_second_matching',lambda:check_map(h,source,matchings[1],m0,m0))
        reject('missing_second_record',lambda:ordered_records(stage_records[0][:-1],10395))
        duplicate=deepcopy(stage_records[0][:2]);duplicate[1]['matching_index']=0;reject('duplicate_second_index',lambda:ordered_records(duplicate,2))
        reject('missing_first_record',lambda:ordered_records(first['records'][:-1],10395))
        # Actual byte-checking routine on independent tiny positive/corrupt fixtures.
        tiny=b'p cnf 2 1\n1 -2 0\n';tail=[[3],[-3,1]];correct=b'p cnf 3 3\n1 -2 0\n3 0\n-3 1 0\n'
        exact_bytes(io.BytesIO(tiny),io.BytesIO(correct),tail,2,1,1)
        for name,badbytes in [('wrong_header',correct.replace(b'3 3',b'3 4',1)),('changed_base',correct.replace(b'1 -2',b'1 2',1)),('wrong_selector_sign',correct.replace(b'-3 1',b'3 1')),('extra_P_restriction',correct+b'2 0\n'),('missing_clause',correct[:correct.rfind(b'-3 1 0\n')])]:
            reject(name,lambda badbytes=badbytes:exact_bytes(io.BytesIO(tiny),io.BytesIO(badbytes),tail,2,1,1))
        save(args.out/'controls.json',dict(positive=small,covariance=covariance_records,corruptions_rejected=negative,sampled_compositions=10395,sampled_compositions_are_not_universal_proof=True))
        save(args.out/'stage_checks.json',stage_reports)
        claim=dict(id='C-VARIABLE-CORE-ORDERED-MATCHING-PAIR-ORBIT-NORMALIZATION',revision=1,statement='The exact augmented CNF is equisatisfiable with the audited arbitrary-core necessary-factor CNF under coordinate relabelling preserving M0, by complete coverage of all ordered M1/M2 matchings by the3580 frozen representatives; P remains arbitrary. Every target graph supplies an augmented-model solution by the pinned universal normalization, but an augmented SAT object need not complete to a graph.',dependencies=[dict(id=i,revision=1,relation=r) for i,r in [('C-TRIANGLE-ORDERED-MATCHING-PAIR-CENSUS','uses_result'),('C-VARIABLE-CORE-M1-ELEVEN-ORBIT-NORMALIZATION','normalization'),('C-UNRESTRICTED-TRIANGLE-NECESSARY-FACTOR-CNF-ENCODING','encoding_equivalence'),('C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION','coverage')]])
        result=dict(status='INDEPENDENT_VARIABLE_CORE_PAIR_ORBIT_NORMALIZATION_PASS',claim_id=claim['id'],claim_revision=1,claim=claim,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,checking_method='Independent exhaustive raw-map checks, fresh matching enumeration, literal covariance controls, written universal composition derivation and complete byte comparison. No producer imports.',trusted_components='Pinned previous census, first-stage normalization, base encoding and universal triangle normalization; Python standard library/tqdm and hardware. No new solver.',matching_universe=10395,first_transport_records_checked=10395,second_transport_records_checked=114345,second_stage_C0_images_checked=6860700,ordered_matching_pair_population=108056025,representative_pairs=3580,universal_coverage_basis='Complete two-stage tables and conjugation bijection, not sampled compositions.',variables=114484,clauses=561121,byte_check=byte_record,controls=dict(small=small,corruptions=len(negative),raw_covariance_cases=11,sampled_compositions=10395),solver_calls=0,P_arbitrary=True,nontrivial_target_automorphism_assumed=False,target_resolution=False,limitations=['SAT means necessary factor only; residual D absent.','No UNSAT or search result established.','Orbit distinctness uses independently audited frozen census.','Transported primary assignments may require fresh auxiliary assignments; no literal CNF automorphism claimed.'],elapsed_seconds=time.monotonic()-start,outputs_sha256={key(p):digest(p) for p in args.out.iterdir() if p.is_file()})
        save(args.out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=digest(args.out/'summary.json'),elapsed_seconds=result['elapsed_seconds'])))
    except Exception as e:
        save(args.out/'failure.json',dict(error_type=type(e).__name__,error=str(e),inputs_sha256=bindings));raise

if __name__=='__main__':main()
