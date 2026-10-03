"""Candidate producer: exact shared-threshold scalar upper-envelope extension.

No repository imports and no native solver. The prior inventory and malformed
controls remain immutable data. This implementation is not independent review.
"""
from pathlib import Path
from itertools import combinations, product
from datetime import datetime, timezone
import argparse
import copy
import gzip
import hashlib
import json
import platform
import subprocess
import sys
import time
import zlib

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
BASE=B+'count_master_scalar_cuts/'
MASTER=B+'hadamard_count_master_cnf/model.json'
RAW=B+'hadamard20_support/six_prism.json'
INV=B+'count_min_upper_inventory/'
ASSIGN=B+'count_master_partial_cuts_native_pilot/main/parsed_model.json'
OLDN,OLDM,N,M=155939,705845,161159,726485
PINS={
 BASE+'instance.cnf':'baca89a7014e10e1fea9fd1873ef5dde4a090ab02dfe1791b4734a196677880b',
 BASE+'model.json':'5e69de324c1a1d406764e95e3962dacf08924dab0c0b687a758614cc7fd49add',
 BASE+'scope.json':'acaaa3b8bb3df262f71ee8f14b063c47c29e5305dc82b7875ce0e1a2459abda0',
 BASE+'summary.json':'d2c4e4eb6c50e5b14aef98039b4a485e7971786ecf420e7dc339a2f167bf8502',
 MASTER:'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',
 RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 B+'independent_review/count_master_partial_cut_cnf/summary.json':'dc1ada9d87d41b5cc6597cd0ff7ce2ed0a06981d8b487dbb797505240f435460',
 B+'independent_review/count_master_partial_cut_sat_outcome/summary.json':'736ccbcda81ee34c21ede2a80253d5b224fabb96a2e83d0a2c1c76dba435d071',
 ASSIGN:'29a86b25a32b466bb7ff8b501421f1c38306728506306be343d006cc1f9a4324',
 B+'independent_review/count_master_partial_cut_sat_outcome/independent_count_profile.json':'03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e',
 INV+'summary.json':'187f1c826dc2e9a71942a59b62abf18ee9c06867ead5f815495e24d9514850ad',
 B+'count_min_upper_inventory_controls_addendum/summary.json':'830ef414a3086119ea2b6c04fb2919db6879c9cc1d96e5a6b6e73c8d434ca1f7',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}


def need(ok,msg):
    if not ok:raise ValueError(msg)


def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()


def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def read(p):return json.loads(Path(p).read_bytes())


def save(p,x):
    with Path(p).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,sort_keys=True,separators=(',',':'));f.write('\n')


def line(c):return (' '.join(map(str,c))+' 0\n').encode('ascii')
def or_gate(q,xs):return [[-x,q] for x in xs]+[[-q,*xs]]
def and_gate(q,a,b):return [[-q,a],[-q,b],[q,-a,-b]]
def bound(xs,k):
    need((len(xs),k) in ((5,1),(10,2)),'bound shape')
    return [xs] if k==1 else [xs[:i]+xs[i+1:] for i in range(10)]
def satisfied(cs,v):return all(any(v[abs(x)]==(x>0) for x in c) for c in cs)


def values(assignment,n):
    need(type(assignment) is list and len(assignment)==n,'complete assignment length')
    v=[None]*(n+1)
    for x in assignment:
        need(type(x) is int and 1<=abs(x)<=n and v[abs(x)] is None,'unique integer assignment ID')
        v[abs(x)]=x>0
    need(all(x is not None for x in v[1:]),'all IDs present');return v


def check_cnf(path,v,n,m):
    count=0
    with Path(path).open('rb') as f:
        need(f.readline()==f'p cnf {n} {m}\n'.encode(),'exact DIMACS header')
        for raw in f:
            xs=list(map(int,raw.split()));need(xs and xs[-1]==0 and all(x and abs(x)<=n for x in xs[:-1]),'DIMACS clause syntax')
            need(any(v[abs(x)]==(x>0) for x in xs[:-1]),'false actual clause '+str(count+1));count+=1
    need(count==m,'actual complete clause count');return count


def recipe(master,raw):
    groups=list(dict.fromkeys(map(tuple,raw['support_columns'])))
    need(len(groups)==20 and all(raw['support_columns'].count(list(g))==3 for g in groups),'raw triplicate groups')
    need([list(g) for g in groups]==master['groups'],'same group order')
    channels=sorted(master['count_channels'],key=lambda d:(d['coordinate'],d['group']))
    need(len(channels)==120 and {(d['coordinate'],d['group']) for d in channels}=={(a,g) for g,s in enumerate(groups) for a in s},'complete120 incidence channels')
    nextvar=OLDN;thresholds=[];products=[];cells=[];ids={}
    for ch in channels:
        a,g=ch['coordinate'],ch['group'];vs=ch['variables'];counts=ch['values']
        need(len(vs)==len(counts) and len(set(vs))==len(vs) and all(0<v<=OLDN for v in vs),'channel variable layout')
        need(all(len(c)==3 and sum(c)==3 and all(type(x)is int and 0<=x<=3 for x in c) for c in counts),'count compositions')
        for f,t in product(range(3),(1,2)):
            nextvar+=1;ids[a,g,f,t]=nextvar
            thresholds.append(dict(coordinate=a,group=g,fibre=f,threshold=t,variable=nextvar,selected_alternatives=[v for v,c in zip(vs,counts) if c[f]>=t],count_channel_variables=vs,count_channel_values=counts))
    C=raw['core_adjacency'];G=raw['prescribed_Gram36']
    for a,b in combinations(range(12),2):
        gs=[g for g,s in enumerate(groups) if a in s and b in s]
        if not gs:need(b==a^1,'only nonmatching coordinate pairs');continue
        need(len(gs)==5,'five complete contributors')
        for f,h in product(range(3),repeat=2):
            i,j=12*f+a,12*h+b;k=2-int(f==h)-C[i][j]-sum(C[i][z]*C[z][j] for z in range(36))
            need(k==G[i][j]==(1 if f==h else 2),'literal target')
            xs=[]
            for g in gs:
                for t in range(1,k+1):
                    nextvar+=1;xs.append(nextvar)
                    products.append(dict(coordinates=[a,b],fibres=[f,h],group=g,threshold=t,variable=nextvar,left=ids[a,g,f,t],right=ids[b,g,h,t]))
            cells.append(dict(coordinates=[a,b],fibres=[f,h],rows=[i,j],target=k,incident_groups=gs,product_variables=xs,bound_clause_count=1 if k==1 else 10))
    need((len(thresholds),len(products),len(cells),nextvar)==(720,4500,540,N),'complete recipe population')
    return thresholds,products,cells


def suffix_clauses(thresholds,products,cells):
    for r in thresholds:
        for c in or_gate(r['variable'],r['selected_alternatives']):yield 'count_threshold_OR',c
    byid={r['variable']:r for r in products}
    for cell in cells:
        for q in cell['product_variables']:
            r=byid[q]
            for c in and_gate(q,r['left'],r['right']):yield 'overlap_AND',c
        for c in bound(cell['product_variables'],cell['target']):yield 'lower_bound_on_upper_envelope',c


def controls(thresholds,products,cells,master,raw):
    checked={}
    checked['binary_strip_pairs']=0
    for u,v in product(list(product((0,1),repeat=3)),repeat=2):
        need(sum(a*b for a,b in zip(u,v))<=min(sum(u),sum(v)),'intersection upper bound');checked['binary_strip_pairs']+=1
    for a,b,k in product(range(4),range(4),(1,2)):need(sum(a>=t and b>=t for t in range(1,k+1))==min(a,b,k),'clipped minimum')
    for xs,k in product(product(range(4),repeat=5),(1,2)):need((sum(xs)>=k)==(sum(min(x,k) for x in xs)>=k),'clipped sum')
    checked['OR_assignments']=0
    for n in range(5):
        for bits in product((False,True),repeat=n+1):
            v=dict(enumerate(bits,1));need(satisfied(or_gate(n+1,list(range(1,n+1))),v)==(bits[-1]==any(bits[:-1])),'OR truth');checked['OR_assignments']+=1
    for a,b,q in product((False,True),repeat=3):need(satisfied(and_gate(3,1,2),{1:a,2:b,3:q})==(q==(a and b)),'AND truth')
    checked['bound_assignments']=0
    for n,k in [(5,1),(10,2)]:
        for bits in product((False,True),repeat=n):need(satisfied(bound(list(range(1,n+1)),k),dict(enumerate(bits,1)))==(sum(bits)>=k),'complete bound truth');checked['bound_assignments']+=1
    count=0
    for r in thresholds:
        for j,c in enumerate(r['count_channel_values']):
            v={x:i==j for i,x in enumerate(r['count_channel_variables'])};v[r['variable']]=c[r['fibre']]>=r['threshold']
            clauses=or_gate(r['variable'],r['selected_alternatives']);need(satisfied(clauses,v),'actual alternative');v[r['variable']]=not v[r['variable']];need(not satisfied(clauses,v),'threshold flip');count+=1
    checked['actual_onehot_threshold_alternatives']=count
    # Compare raw metadata mutations to a fresh raw-input reconstruction.
    pristine=recipe(master,raw);rejected=[]
    tests=[('omitted_threshold_alternative',0,0,'selected_alternatives',thresholds[0]['selected_alternatives'][:-1]),('wrong_threshold',0,0,'threshold',3),('negated_AND_input',1,0,'left',-products[0]['left']),('changed_target',2,0,'target',cells[0]['target']+1),('missing_group',2,0,'incident_groups',cells[0]['incident_groups'][:-1]),('missing_product',2,0,'product_variables',cells[0]['product_variables'][:-1])]
    for name,part,index,field,new in tests:
        bad=copy.deepcopy(pristine);bad[part][index][field]=new;need(bad!=recipe(master,raw),'malformed recipe missed');rejected.append(name)
    # Deliberate dropped CNF constraints admit the exact corrupt valuation.
    v={1:True,2:False,3:False};need(satisfied(or_gate(3,[1,2])[1:],v) and not satisfied(or_gate(3,[1,2]),v),'omitted OR clause')
    v={1:False,2:True,3:True};need(satisfied(and_gate(3,1,2)[1:],v) and not satisfied(and_gate(3,1,2),v),'omitted AND clause')
    v={i:i==1 for i in range(1,11)};need(satisfied(bound(list(range(1,11)),2)[1:],v) and not satisfied(bound(list(range(1,11)),2),v),'omitted bound clause')
    rejected+=['omitted_OR_forward_clause','omitted_AND_forward_clause','omitted_bound_clause']
    return dict(checked=checked,malformed_rejected=rejected,scope='Producer finite gadget/metadata calibration, not independent encoding approval and not a full-factor positive.')


def decode(assignment,model_path):
    """Complete candidate assignment -> raw count table and all540 upper bounds.

    No producer imports. Checks the entire augmented DIMACS and raw master maps.
    It neither constructs nor approves a 36x60 factor or a residual graph.
    """
    model=read(model_path);need(model['schema']=='COUNT_MIN_UPPER_ENVELOPE_REFERENCE_MODEL_V1','model schema')
    for p,h in model['decoder_inputs_sha256'].items():need(sha(ROOT/p)==h,'decoder input identity')
    v=values(assignment,model['variables']);cnf=ROOT/model['cnf_path'];need(sha(cnf)==model['cnf_sha256'],'decoded actualCNF identity')
    checked=check_cnf(cnf,v,model['variables'],model['clauses']);master=read(ROOT/model['base_count_model_path'])
    coordinates=[None]*12;coordinate_ids=[]
    for d in master['coordinate_domains']:
        selected=[i for i,x in enumerate(d['selectors']) if v[x]];need(len(selected)==1,'one coordinate selector');i=selected[0]
        coordinates[d['coordinate']]=d['count_tables'][i];coordinate_ids.append(d['selectors'][i])
    group_ids=[];local=[];signatures=[]
    for d in master['group_domains']:
        selected=[i for i,x in enumerate(d['selectors']) if v[x]];need(len(selected)==1,'one group selector');i=selected[0];sid=d['signature_indices'][i];s=master['local_signatures'][sid]
        actual=[x for a in d['support'] for x in coordinates[a][d['group']]];need(actual==s['counts'],'group/coordinate incidence match')
        need(all(sum(actual[3*j+f] for j in range(6))==6 for f in range(3)),'group/fibre quota');group_ids.append(d['selectors'][i]);local.append(s['local_survivor_indices']);signatures.append(sid)
    for ch in master['count_channels']:
        selected=[i for i,x in enumerate(ch['variables']) if v[x]];need(len(selected)==1 and ch['values'][selected[0]]==coordinates[ch['coordinate']][ch['group']],'literal count channel')
    for a,counts in enumerate(coordinates):
        for f in range(3):
            delta=[counts[g][f]-int(a in master['groups'][g]) for g in range(20)]
            need(sum(delta)==0 and all(sum(delta[g] for g in range(20) if b in master['groups'][g])==0 for b in range(12)),'summed Gram marginals')
    checks=[]
    for r in model['scalar_cells']:
        a,b=r['coordinates'];f,h=r['fibres'];terms=[min(coordinates[a][g][f],coordinates[b][g][h]) for g in r['incident_groups']]
        need(sum(terms)>=r['target'],'literal upper-envelope inequality');checks.append(dict(coordinates=[a,b],fibres=[f,h],target=r['target'],terms=terms,sum_upper=sum(terms),satisfied=True))
    for r in model['threshold_channels']:need(v[r['variable']]==(coordinates[r['coordinate']][r['group']][r['fibre']]>=r['threshold']),'literal threshold auxiliary')
    for r in model['overlap_products']:need(v[r['variable']]==(v[r['left']] and v[r['right']]),'literal product auxiliary')
    exceptional=[g for g,s in enumerate(master['groups']) if any(coordinates[a][g]!=[1,1,1] for a in s)];need(len(exceptional)>=7,'inherited exception premise')
    deviations=[[[coordinates[a][g][f]-int(a in master['groups'][g]) for g in exceptional] for f in range(3)] for a in range(12)]
    digest=hashlib.sha256(json.dumps(dict(groups=exceptional,deviations=deviations),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return dict(schema='COUNT_MIN_UPPER_DECODED_CANDIDATE_V1',selected_coordinate_selector_ids=coordinate_ids,selected_group_selector_ids=group_ids,selected_global_signature_indices=signatures,coordinate_group_fibre_counts=coordinates,local_survivor_indices_by_group=local,exceptional_groups=exceptional,exception_count=len(exceptional),coordinate_fibre_deviations=deviations,profile_sha256=digest,upper_envelope_checks=checks,actual_clauses_checked=checked,variables_checked=len(assignment),model_sha256=sha(model_path),full_factor=False,target_graph=False,residual_D=None,cross_group_column_caps_checked=False,independent_approval=False)


def package(path,out):
    parts=[];offset=0;whole=hashlib.sha256()
    with path.open('rb') as f:
        while True:
            raw=f.read(8*1024**2)
            if not raw:break
            p=out/f'{path.name}.part{len(parts):04d}.gz'
            with p.open('xb') as fd:
                with gzip.GzipFile(filename='',mode='wb',fileobj=fd,mtime=0,compresslevel=9) as g:g.write(raw)
            compressed=p.read_bytes();d=zlib.decompressobj(31);restored=d.decompress(compressed)+d.flush()
            need(d.eof and not d.unused_data and restored==raw and len(compressed)<10*1024**2,'exact public gzip identity')
            parts.append(dict(path=key(p),gzip_sha256=sha(p),gzip_bytes=p.stat().st_size,raw_offset=offset,raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest()));offset+=len(raw);whole.update(raw)
    need(whole.hexdigest()==sha(path),'whole recovery hash');return dict(path=key(path),sha256=whole.hexdigest(),bytes=offset,parts=parts,availability='LOCAL_ONLY',public_lossless_recovery=True)


def build(out):
    start=time.monotonic();pins=dict(PINS)
    for p,h in pins.items():need(sha(ROOT/p)==h,'pinned input '+p)
    for p in [Path(__file__),Path(__file__).with_name('theory_20260930_count_min_upper_cnf_spec.md'),ROOT/'docs/DESIGN_20260930_COUNT_MIN_UPPER_CNF.md']:
        pins[key(p)]=sha(p)
    inv=read(ROOT/(INV+'summary.json'))
    for p,h in inv['outputs_sha256'].items():need(sha(ROOT/p)==h,'immutable inventory output');pins[p]=h
    save(out/'manifest.json',dict(status='CANDIDATE_PREDECLARED_BUILD',timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),inputs_sha256=pins,cooperative_seconds=120,planning_memory_bytes=512*1024**2,source_frozen_before_execution=True,native_calls=0,solver_calls=0,selection='Exact existing six-full-profile/six-partial-cut prefix, plus all540 scalar min-count upper bounds; no sampling or deduplication.'))
    master=read(ROOT/MASTER);raw=read(ROOT/RAW);thresholds,products,cells=recipe(master,raw)
    for actual,filename in [(thresholds,'threshold_channels.json'),(products,'overlap_products.json'),(cells,'scalar_cells.json')]:
        old=read(ROOT/(INV+filename))['records'];need(len(actual)==len(old) and all(all(x[k]==y[k] for k in x) for x,y in zip(actual,old)),'same preregistered recipe '+filename)
    ctrl=controls(thresholds,products,cells,master,raw);save(out/'controls.json',ctrl)
    suffix=out/'suffix.cnf.body';nclauses=0;nbytes=0;sections={}
    with suffix.open('xb') as f:
        for section,clause in suffix_clauses(thresholds,products,cells):
            need(all(type(x)is int and 0<abs(x)<=N for x in clause),'literal range');data=line(clause);f.write(data);nclauses+=1;nbytes+=len(data)
            q=sections.setdefault(section,dict(clauses=0,bytes=0));q['clauses']+=1;q['bytes']+=len(data)
    need(nclauses==20640 and nbytes==571440 and sha(suffix)=='a99c2118364159e9035e0353e21cd8e1e12fead8c0b82df7b16f826e52937845','exact frozen suffix recipe')
    partial=out/'instance.cnf.partial';cnf=out/'instance.cnf'
    with partial.open('xb') as target,(ROOT/(BASE+'instance.cnf')).open('rb') as base:
        need(base.readline()==f'p cnf {OLDN} {OLDM}\n'.encode(),'exact prefix header');target.write(f'p cnf {N} {M}\n'.encode())
        for block in iter(lambda:base.read(1024**2),b''):target.write(block)
        with suffix.open('rb') as f:
            for block in iter(lambda:f.read(1024**2),b''):target.write(block)
    need(partial.stat().st_size==11834633,'full ASCII estimate');partial.rename(cnf)
    # Independently compare every body byte to prefix then separately retained suffix.
    with cnf.open('rb') as f,(ROOT/(BASE+'instance.cnf')).open('rb') as base:
        f.readline();base.readline()
        for block in iter(lambda:base.read(1024**2),b''):need(f.read(len(block))==block,'unchanged full prefix body')
        need(f.read()==suffix.read_bytes(),'exact appended suffix')
    scope=dict(schema='FIXED_SUPPORT_COUNT_MIN_UPPER_SCOPE_V1',scope='Exact inherited >=7 count relaxation, its six full-profile and six scalar necessary cuts, and all540 universal scalar upper-envelope inequalities. Necessary for factors in the literal fixed-support family under the inherited premises. Not sufficient for Gram realization, cross-column caps, residual D or target existence.',groups=master['groups'],raw_support_path=RAW,raw_support_sha256=PINS[RAW],old_scope_path=BASE+'scope.json',old_scope_sha256=PINS[BASE+'scope.json'],count_only=True,full_factor=False,target_graph=False,independent_approval=False,no_target_automorphism_assumed=True)
    save(out/'scope.json',scope)
    model=dict(schema='COUNT_MIN_UPPER_ENVELOPE_REFERENCE_MODEL_V1',variables=N,clauses=M,old_variables=OLDN,old_clause_count=OLDM,base_count_model_path=MASTER,base_count_model_sha256=PINS[MASTER],prefix_cnf_path=BASE+'instance.cnf',prefix_cnf_sha256=PINS[BASE+'instance.cnf'],prefix_model_path=BASE+'model.json',prefix_model_sha256=PINS[BASE+'model.json'],cnf_path=key(cnf),cnf_sha256=sha(cnf),scope_path=key(out/'scope.json'),scope_sha256=sha(out/'scope.json'),suffix_path=key(suffix),suffix_sha256=sha(suffix),threshold_channels=thresholds,overlap_products=products,scalar_cells=cells,clause_sections=sections,decoder_inputs_sha256={MASTER:PINS[MASTER],BASE+'instance.cnf':PINS[BASE+'instance.cnf'],BASE+'model.json':PINS[BASE+'model.json'],RAW:PINS[RAW]},decode_ABI='decode(assignment: list[int], model_path: Path) -> raw count table and540 scalar checks; all161159IDs/all726485actualclauses checked',inputs_sha256=pins,independent_approval=False,full_factor=False,target_graph=False)
    save(out/'model.json',model)
    original=read(ROOT/ASSIGN)['assignment'];v=values(original,OLDN);check_cnf(ROOT/(BASE+'instance.cnf'),v,OLDN,OLDM)
    v.extend([None]*(N-OLDN))
    for r in thresholds:v[r['variable']]=any(v[x] for x in r['selected_alternatives'])
    for r in products:v[r['variable']]=v[r['left']] and v[r['right']]
    assignment=[i if v[i] else -i for i in range(1,N+1)]
    save(out/'candidate_auxiliary_assignment.json',dict(assignment=assignment,origin='Deterministic new auxiliaries of the unchanged saved third-count native assignment; no new solver call.'))
    decoded=decode(assignment,out/'model.json');need(decoded['profile_sha256']=='3bc6ebf9444e7a2f15af1ac85c6164119333244ced5d6dbe83a6c6b367e533d5','same old count profile, not fresh discovery');save(out/'candidate_decoded_count_profile.json',decoded)
    rejects=[]
    for name,bad in [('missing_ID',assignment[:-1]),('duplicate_ID',[assignment[0]]+assignment[:-1]),('noninteger_ID',[True]+assignment[1:]),('out_of_range',[N+1]+assignment[1:])]:
        try:values(bad,N)
        except ValueError:rejects.append(name)
        else:raise ValueError('assignment corruption accepted')
    for name,var in [('wrong_threshold',thresholds[0]['variable']),('wrong_product',products[0]['variable'])]:
        wrong=v.copy();wrong[var]=not wrong[var]
        try:check_cnf(cnf,wrong,N,M)
        except ValueError:rejects.append(name)
        else:raise ValueError('auxiliary corruption accepted')
    # Small complete-file codecs reject header, count and terminator corruption.
    fixture=out/'synthetic_codec.cnf';fixture.write_bytes(b'p cnf 2 2\n1 0\n-1 2 0\n');check_cnf(fixture,[None,True,True],2,2)
    for name,data in [('wrong_header',b'p cnf 3 2\n1 0\n-1 2 0\n'),('missing_clause',b'p cnf 2 2\n1 0\n'),('unterminated',b'p cnf 2 2\n1\n-1 2 0\n')]:
        p=out/(name+'.cnf');p.write_bytes(data)
        try:check_cnf(p,[None,True,True],2,2)
        except ValueError:rejects.append(name)
        else:raise ValueError('CNF codec corruption accepted')
    save(out/'object_controls.json',dict(rejected=rejects,full_actual_assignment_checked=True,unchanged_source_count_profile=decoded['profile_sha256'],scope='Candidate producer object calibration; positive is an existing count-relaxation witness, not a full factor.'))
    pkg=package(cnf,out);save(out/'artifact_packages.json',dict(schema='COUNT_MIN_UPPER_CNF_GZIP_PACKAGE_V1',records=[pkg],identity_only=True,mathematical_verification=False))
    need(time.monotonic()-start<120,'cooperative build budget')
    summary=dict(status='CANDIDATE_COUNT_MIN_UPPER_ENVELOPE_CNF_BUILT',inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},variables=N,clauses=M,new_variables=N-OLDN,new_clauses=nclauses,ASCII_bytes=cnf.stat().st_size,suffix_ASCII_bytes=nbytes,thresholds=720,products=4500,scalar_cells=540,sections=sections,candidate_same_count_auxiliary_extension_satisfies_actual_formula=True,source_count_profile_sha256=decoded['profile_sha256'],candidate_exception_count=decoded['exception_count'],native_calls=0,solver_calls=0,independent_approval=False,artifact_availability='LOCAL_ONLY',full_factor=False,target_graph=False,repository_imports=[],shared_production_components=['Recipe matches own frozen inventory and prior small-gadget construction; reconstruction/count decoding is fresh stdlib code using immutable master metadata.', 'Inherited mathematical validity and necessity of prefix remain separate independent-gate premises.'],elapsed_seconds=time.monotonic()-start)
    save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],summary_sha256=sha(out/'summary.json'),CNF_sha256=sha(cnf),model_sha256=sha(out/'model.json'),scope_sha256=sha(out/'scope.json'),variables=N,clauses=M,elapsed_seconds=summary['elapsed_seconds'])))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:build(out)
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(__file__),independent_approval=False));raise


if __name__=='__main__':main()
