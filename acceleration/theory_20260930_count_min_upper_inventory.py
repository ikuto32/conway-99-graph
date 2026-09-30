"""Inventory only: shared Boolean thresholds for universal scalar upper bounds."""
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse, hashlib, json, platform, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
MASTER=B+'hadamard_count_master_cnf/model.json'
RAW=B+'hadamard20_support/six_prism.json'
WITNESS=B+'independent_review/count_master_eight_orbit_cut_sat_outcome/independent_count_profile.json'
PINS={MASTER:'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',
 RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 WITNESS:'7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0',
 B+'hadamard_count_master_cnf/at_least_seven.cnf':'f303edec9a91dc9bcecb95804ee151d0e38e8100b17c9c45a7b4d58b8edbf55e',
 B+'count_master_scalar_cuts/instance.cnf':'baca89a7014e10e1fea9fd1873ef5dde4a090ab02dfe1791b4734a196677880b',
 B+'count_master_scalar_cuts/summary.json':'d2c4e4eb6c50e5b14aef98039b4a485e7971786ecf420e7dc339a2f167bf8502',
 B+'independent_review/hadamard_count_master_cnf_v2/summary.json':'80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888',
 B+'independent_review/count_master_eight_orbit_cut_sat_outcome/summary.json':'7c80d3e4daef0f259bd354e6e6b28188b660edaaf17c7a20f9c54cfb3abc4c3c',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
OVERLAP=['acceleration/theory_20260930_count_interval_inventory.py',
 'acceleration/theory_20260930_count_interval_inventory_spec.md',
 'acceleration/theory_20260930_second_count_partial_cut.py',
 'acceleration/theory_20260930_second_count_partial_cut_spec.md',
 'docs/AUDIT_20260930_LOCAL_FRECHET_EQUALITY_REFUTATION.md']

def need(ok,msg):
    if not ok:raise ValueError(msg)

def sha(p):
    with Path(p).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as stream:json.dump(x,stream,separators=(',',':'),sort_keys=True);stream.write('\n')

def clause_ok(c,values):return any(values[abs(x)]==(x>0) for x in c)
def or_clauses(q,xs):return [[-x,q] for x in xs]+[[-q,*xs]]
def and_clauses(q,a,b):return [[-q,a],[-q,b],[q,-a,-b]]
def bound_clauses(xs,k):
    need((len(xs),k) in [(5,1),(10,2)],'predeclared bound population')
    return [list(xs)] if k==1 else [[x for j,x in enumerate(xs) if j!=i] for i in range(10)]

class Inventory:
    def __init__(self):self.nextvar=155939;self.clauses=0;self.bytes=0;self.hash=hashlib.sha256();self.sections={}
    def variable(self):self.nextvar+=1;return self.nextvar
    def emit(self,c,section):
        need(all(type(x)is int and x and abs(x)<=self.nextvar for x in c),'literal range')
        data=(' '.join(map(str,c))+' 0\n').encode('ascii')
        self.clauses+=1;self.bytes+=len(data);self.hash.update(data)
        item=self.sections.setdefault(section,dict(clauses=0,bytes=0));item['clauses']+=1;item['bytes']+=len(data)

def controls():
    strips=[]
    for a,b in product(product((0,1),repeat=3),repeat=2):
        u,v=sum(a),sum(b);actual=sum(x*y for x,y in zip(a,b));need(actual<=min(u,v),'universal intersection bound')
        strips.append([list(a),list(b),actual,min(u,v)])
    clip=[]
    for u,v,k in product(range(4),range(4),[1,2]):
        flags=[int(u>=t and v>=t) for t in range(1,k+1)]
        need(sum(flags)==min(u,v,k),'exact clipped minimum');clip.append([u,v,k,flags])
    profiles=[]
    for values in product(range(4),repeat=5):
        for k in [1,2]:
            direct=sum(values)>=k;flags=[int(x>=t) for x in values for t in range(1,k+1)]
            need(direct==(sum(flags)>=k),'clipped five-group inequality')
            profiles.append([list(values),k,direct])
    or_cases=0
    for n in range(5):
        q=n+1;xs=list(range(1,n+1));cs=or_clauses(q,xs)
        for values in product((False,True),repeat=n+1):
            truth=dict(enumerate(values,1));need(all(clause_ok(c,truth) for c in cs)==(values[-1]==any(values[:-1])),'complete OR truth');or_cases+=1
    for a,b,q in product((False,True),repeat=3):
        need(all(clause_ok(c,{1:a,2:b,3:q}) for c in and_clauses(3,1,2))==(q==(a and b)),'complete AND truth')
    bounds=0
    for n,k in [(5,1),(10,2)]:
        cs=bound_clauses(list(range(1,n+1)),k)
        for vals in product((False,True),repeat=n):
            need(all(clause_ok(c,dict(enumerate(vals,1))) for c in cs)==(sum(vals)>=k),'complete bound truth');bounds+=1
    need(all(clause_ok(c,{1:True,2:False,3:False}) for c in or_clauses(3,[1,2])[1:]),'missing OR forward admits corruption')
    need(not all(clause_ok(c,{1:True,2:False,3:False}) for c in or_clauses(3,[1,2])),'complete OR rejects corruption')
    need(all(clause_ok(c,{1:False,2:True,3:True}) for c in and_clauses(3,1,2)[1:]),'missing AND implication admits corruption')
    t={i:i==1 for i in range(1,11)}
    need(all(clause_ok(c,t) for c in bound_clauses(list(range(1,11)),2)[1:]) and not all(clause_ok(c,t) for c in bound_clauses(list(range(1,11)),2)),'missing nine-literal clause corruption')
    return {'strip_records':strips,'clipped_pairs':clip,'five_min_vectors':profiles,'OR_assignments':or_cases,'AND_assignments':8,'bound_assignments':bounds,
            'corruptions':['omitted_OR_implication','omitted_AND_implication','omitted_bound_clause'],
            'scope':'Exact local gadgets; no full research factor positive.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        pins=dict(PINS)
        for p,h in pins.items():need(sha(ROOT/p)==h,'frozen input '+p)
        for p in [Path(__file__),Path(__file__).with_name('theory_20260930_count_min_upper_inventory_spec.md'),ROOT/'docs/DERIVATION_20260930_COUNT_MIN_UPPER_ENVELOPE.md',*[ROOT/x for x in OVERLAP]]:pins[key(p)]=sha(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),inputs_sha256=pins,source_frozen_before_controls=True,limits=dict(cooperative_seconds=120,planning_memory_bytes=256*1024**2),CNF_files_to_write=0,native_calls=0,selection='All60 nonmatching coordinate pairs times9 ordered fibre pairs; no sampling or variable-subset deduplication.'))
        ctrl=controls();save(out/'controls.json',ctrl)
        master=read(MASTER);raw=read(RAW);witness=read(WITNESS)
        groups=list(dict.fromkeys(map(tuple,raw['support_columns'])))
        need(len(groups)==20 and all(raw['support_columns'].count(list(s))==3 for s in groups),'twenty triplicate supports')
        C=raw['core_adjacency'];G=raw['prescribed_Gram36'];channels=sorted(master['count_channels'],key=lambda c:(c['coordinate'],c['group']))
        need(len(channels)==120 and len({(x['coordinate'],x['group']) for x in channels})==120,'all120 channels')
        need({(x['coordinate'],x['group']) for x in channels}=={(a,g) for g,s in enumerate(groups) for a in s},'complete channel incidence population')
        inv=Inventory();thresholds=[];ids={};actual_choices=0
        for channel in channels:
            a,g=channel['coordinate'],channel['group'];vals=channel['values'];vs=channel['variables']
            need(len(vals)==len(vs) and len(set(vs))==len(vs) and all(sum(v)==3 and all(type(x)is int and 0<=x<=3 for x in v) for v in vals),'exact count alternatives')
            for f,t in product(range(3),[1,2]):
                q=inv.variable();subset=[v for v,val in zip(vs,vals) if val[f]>=t];ids[a,g,f,t]=q
                cs=or_clauses(q,subset)
                for clause in cs:inv.emit(clause,'count_threshold_OR')
                for j,val in enumerate(vals):
                    truth={v:k==j for k,v in enumerate(vs)};truth[q]=val[f]>=t
                    need(all(clause_ok(c,truth) for c in cs),'actual selected-count threshold positive')
                    truth[q]=not truth[q];need(not all(clause_ok(c,truth) for c in cs),'changed actual threshold rejected');actual_choices+=1
                thresholds.append(dict(coordinate=a,group=g,fibre=f,threshold=t,variable=q,selected_alternatives=subset,count_channel_variables=vs,count_channel_values=vals,clauses=len(cs)))
        need(len(thresholds)==720,'shared threshold total')
        pairs=[]
        for a,b in combinations(range(12),2):
            incident=[g for g,s in enumerate(groups) if a in s and b in s]
            if not incident:
                need(b==(a^1),'only matching coordinate pairs omitted');continue
            need(len(incident)==5,'exact five-group positive pair');pairs.append((a,b,incident))
        need(len(pairs)==60,'all sixty nonmatched pairs')
        products=[];cells=[];known_counts=witness['coordinate_group_fibre_counts'];failures=[]
        for a,b,gs in pairs:
            for f,h in product(range(3),repeat=2):
                i,j=12*f+a,12*h+b;K=12*int(i==j)-C[i][j]-sum(C[i][z]*C[z][j] for z in range(36))+2-int(f==h)
                need(K==G[i][j]==(1 if f==h else 2),'literal positive target')
                xs=[]
                for g in gs:
                    for t in range(1,K+1):
                        left,right=ids[a,g,f,t],ids[b,g,h,t];q=inv.variable();xs.append(q)
                        for clause in and_clauses(q,left,right):inv.emit(clause,'overlap_AND')
                        products.append(dict(coordinates=[a,b],fibres=[f,h],group=g,threshold=t,variable=q,left=left,right=right))
                cs=bound_clauses(xs,K)
                for clause in cs:inv.emit(clause,'lower_bound_on_upper_envelope')
                known=[min(known_counts[a][g][f],known_counts[b][g][h]) for g in gs]
                need(sum(min(1,1) for _ in gs)>=K,'balanced raw-count scalar positive')
                cell=dict(coordinates=[a,b],fibres=[f,h],rows=[i,j],target=K,incident_groups=gs,product_variables=xs,bound_clause_count=len(cs),known_count_witness_terms=known,known_count_witness_satisfies=sum(known)>=K)
                if sum(known)<K:failures.append(cell)
                cells.append(cell)
        need(len(cells)==540 and len(products)==4500,'complete literal populations')
        need(any(x['coordinates']==[9,11] and x['fibres']==[2,1] for x in failures),'authenticated second witness known scalar failure')
        need(time.monotonic()-start<120,'cooperative inventory budget')
        save(out/'threshold_channels.json',dict(records=thresholds,all_onehot_alternatives_checked=actual_choices))
        save(out/'overlap_products.json',dict(records=products))
        save(out/'scalar_cells.json',dict(records=cells,known_second_witness_failures=failures,balanced_count_table_passes_all=True,neither_count_table_is_a_full_factor_claim=True))
        variants=[]
        for label,path,oldclauses in [('at_least_seven',B+'hadamard_count_master_cnf/at_least_seven.cnf',705833),('six_orbit_six_partial',B+'count_master_scalar_cuts/instance.cnf',705845)]:
            with (ROOT/path).open('rb') as stream:header=stream.readline()
            need(header==f'p cnf 155939 {oldclauses}\n'.encode(),'authenticated base header')
            bodybytes=(ROOT/path).stat().st_size-len(header);newheader=f'p cnf {inv.nextvar} {oldclauses+inv.clauses}\n'.encode()
            variants.append(dict(base=label,base_path=path,base_sha256=PINS[path],variables=inv.nextvar,clauses=oldclauses+inv.clauses,full_ASCII_bytes=len(newheader)+bodybytes+inv.bytes,body_reused_bytes=bodybytes,full_formula_built=False))
        inventory=dict(new_variables=inv.nextvar-155939,shared_count_thresholds=720,overlap_AND_variables=4500,new_clauses=inv.clauses,suffix_ASCII_bytes=inv.bytes,hypothetical_suffix_sha256=inv.hash.hexdigest(),sections=inv.sections,variants=variants,threshold_alternative_count_histogram=dict(Counter(len(x['selected_alternatives']) for x in thresholds)),all540_cells=True)
        save(out/'inventory.json',inventory)
        save(out/'overlap_review.json',dict(paths=OVERLAP,search='rg read-only source/doc search for min-overlap, scalar upper/envelope, min(u,v), Frechet and count thresholds; results/build/code trees excluded.',findings=['Existing exact local-class interval extension is broader and much larger.','Existing six partial clauses cover selected scalar failure regions.','Refuted exact Frechet equality does not refute these loose upper inequalities.','No prior complete540-cell shared count-threshold formulation found in this bounded search.'],novelty_claimed=False))
        summary=dict(status='CANDIDATE_COUNT_MIN_UPPER_ENVELOPE_INVENTORY',inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},inventory=inventory,known_second_count_witness_failed_cells=len(failures),actual_channel_alternative_checks=actual_choices,elapsed_seconds=time.monotonic()-start,native_calls=0,CNF_files_written=0,independent_approval=False,artifact_availability='LOCAL_ONLY',scope='All540 universal scalar min-count upper-envelope necessary inequalities on the literal fixed support. This is not exact-class maximum equality or factor realization.')
        save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],summary_sha256=sha(out/'summary.json'),inventory=inventory,known_witness_failed_cells=len(failures),elapsed_seconds=summary['elapsed_seconds'])))
    except BaseException as exc:
        save(out/'failure.json',dict(error=repr(exc),source_sha256=sha(__file__),elapsed_seconds=time.monotonic()-start));raise

if __name__=='__main__':main()
