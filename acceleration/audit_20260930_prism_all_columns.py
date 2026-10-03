"""Independent six-prism universe, raw39 Gram, complete equations and prefix CNF."""
from collections import Counter,defaultdict
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse
import gzip
import hashlib
import io
import json
import platform
import subprocess
import sys
import time
import audit_20260930_eight_full99_cnf_v1 as gates

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_prism_all_columns'
need,digest,key,save=gates.need,gates.digest,gates.key,gates.save
SUMMARY_SHA='8f6da203befb5a10d4e9e17438647207c9a98d0826fcbe91d40820d1b7c1b8d5'
GATES_SHA='c956504752a937ffa6aa1ad84d4aa30d95db8723287970e76cbfd262b74ecf4c'

def derive():
    h=[[0]*39 for _ in range(39)]
    def edge(a,b):h[a][b]=h[b][a]=1
    for a,b in combinations(range(3),2):edge(a,b)
    for r in range(36):edge(r//12,3+r)
    for a,b in combinations(range(36),2):
        ga,gb=a//12,b//12;ca,cb=(a%12)//2,(b%12)//2;ba,bb=a%2,b%2
        if ca==cb and ((ga==gb and ba!=bb)or(ga!=gb and ba==bb)):edge(3+a,3+b)
    need([sum(row)for row in h]==[14]*3+[4]*36,'literal raw39 degrees')
    k=[[12*int(a==b)+2-h[a+3][b+3]-sum(h[a+3][z]*h[b+3][z]for z in range(39))for b in range(36)]for a in range(36)]
    components=[[r for r in range(36)if(r%12)//2==c]for c in range(6)]
    for a,b in product(range(36),repeat=2):
        expected=10 if a==b else(0 if(a%12)//2==(b%12)//2 else(1 if a//12==b//12 else 2))
        need(k[a][b]==expected,'raw target Gram coefficient')
    labels=[list(p)for p in combinations(range(12),2)if k[p[0]][p[1]]==1]
    universe=defaultdict(set);all_states=0
    for states in product(range(6),repeat=6):
        all_states+=1
        if Counter(s//2 for s in states)!={0:2,1:2,2:2}:continue
        rows=tuple(sorted(12*(s//2)+2*c+s%2 for c,s in enumerate(states)))
        pair=tuple(r for r in rows if r<12);universe[pair].add(rows)
    need(all_states==46656 and len(universe)==60 and all(len(v)==96 for v in universe.values()),'complete component-state census')
    for g in range(3):
        total=sum(k[a][b]for a in range(12*g,12*g+12)for b in range(12*g,12*g+12))
        need(total==240,'cell squared-weight identity')
    return h,k,components,labels,universe

def scope_check(model,derived):
    h,k,components,labels,universe=derived
    need(model['schema']=='SIX_PRISM_COMPLETE_COLUMN_DOMAINS_V1','schema')
    need(model['core_adjacency']==[row[3:]for row in h[3:]]and model['target_gram']==k,'all raw core/Gram coefficients')
    need(model['components']==components and model['canonical_C0_columns']==labels,'components and exact C0 labels')
    for field in ['outside_column_caps_encoded','residual_D_encoded','target_graph_encoded','symmetry_or_orbit_pruning','complement_pairing']:
        need(model[field]is False,'scope restriction '+field)
    need(type(model['solver_calls'])is int and model['solver_calls']==0,'no solver call')
    choices=model['choices'];need(len(choices)==5760,'primary population')
    seen=defaultdict(set);refs=defaultdict(list);supports={}
    for expected_id,item in enumerate(choices,1):
        need(set(item)=={'id','column','rows'}and type(item['id'])is int and item['id']==expected_id,'contiguous literal primary IDs')
        d=item['column'];rows=item['rows']
        need(type(d)is int and 0<=d<60 and len(rows)==6 and all(type(r)is int and 0<=r<36 for r in rows),'choice types/ranges')
        need(rows==sorted(set(rows)),'distinct ordered support')
        value=tuple(rows);pair=tuple(labels[d])
        need(value in universe[pair]and value not in seen[d],'unique permitted full choice')
        seen[d].add(value);refs[d].append(expected_id);supports[expected_id]=set(rows)
    need(all(seen[d]==universe[tuple(labels[d])]for d in range(60)),'complete per-column universe, no pruning')
    equations=[]
    for d in range(60):equations.append((refs[d],1,dict(kind='one_choice_per_column',column=d)))
    incidence=0;bounds=Counter()
    for a,b in combinations(range(36),2):
        if k[a][b]==0 or b<12:continue
        inputs=[i for i,s in supports.items()if a in s and b in s]
        incidence+=len(inputs);bounds[k[a][b]]+=1
        equations.append((inputs,k[a][b],dict(kind='row_gram',pair=[a,b])))
    need(len(equations)==540 and bounds=={1:120,2:360}and incidence==80640,'equation and incidence populations')
    return equations

def scope_controls(model,derived):
    small={k:v for k,v in model.items()if k!='counter_rows'};rejected=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):rejected.append(label)
        else:raise ValueError('accepted corruption '+label)
    for label in ['missing_choice','duplicate_support','wrong_id','wrong_column','wrong_cell','Boolean_row','wrong_Gram','wrong_core','complement_restriction','target_claim']:
        bad=deepcopy(small)
        if label=='missing_choice':bad['choices'].pop()
        elif label=='duplicate_support':bad['choices'][1]['rows']=bad['choices'][0]['rows'][:]
        elif label=='wrong_id':bad['choices'][0]['id']=2
        elif label=='wrong_column':bad['choices'][0]['column']=59
        elif label=='wrong_cell':bad['choices'][0]['rows'][-1]=35
        elif label=='Boolean_row':bad['choices'][0]['rows'][0]=False
        elif label=='wrong_Gram':bad['target_gram'][0][1]=1
        elif label=='wrong_core':bad['core_adjacency'][0][1]=0
        elif label=='complement_restriction':bad['complement_pairing']=True
        else:bad['target_graph_encoded']=True
        reject(label,lambda:scope_check(bad,derived))
    return rejected

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(p,expected=None):
        p=Path(p);observed=digest(p);need(expected is None or observed==expected,'hash '+str(p));bindings[key(p)]=observed;return p
    def read(p,expected=None):return json.loads(bind(p,expected).read_bytes())
    try:
        bind(Path(gates.__file__),GATES_SHA)
        summary=read(D/'summary.json',SUMMARY_SHA);manifest=read(D/'manifest.json')
        for p,value in manifest['inputs_sha256'].items():bind(ROOT/p,value)
        for name,record in summary['outputs'].items():need(bind(D/name,record['sha256']).stat().st_size==record['bytes'],'byte length')
        # Transitive producer import absent from its frozen manifest; preserve and disclose this additional binding.
        bind(ROOT/'acceleration/theory_20260930_full_srg_validator.py')
        model=read(D/'model.json');derived=derive();equations=scope_check(model,derived)
        h,k,components,labels,universe=derived
        save(args.out/'derived_geometry.json',dict(raw39_adjacency=h,core_adjacency=[row[3:]for row in h[3:]],target_gram=k,components=components,canonical_C0_columns=labels,
          independent_complete_domain_enumeration='All46656 choices of one vertex from each prism, then exact two-per-cell filter',retained=5760,choices_per_C0_column=96))
        controls=dict(threshold=gates.controls(),scope_corruptions_rejected=scope_controls(model,derived))
        need(len(model['counter_rows'])==len(equations),'complete counter metadata population')
        with (D/'instance.cnf').open('rb')as stream:
            need(stream.readline()==b'p cnf 245880 874800\n','exact header')
            cursor=gates.ClauseCursor(stream,245880);audit=gates.GateAudit(cursor,5760)
            for row,(inputs,bound,annotation)in zip(model['counter_rows'],equations):audit.counter(row,inputs,bound,True,annotation)
            need(stream.read()==b'','no extra clauses')
        need(audit.top==model['variables']==245880 and cursor.count==model['clauses']==874800,'all variables and clauses')
        # First counter controls use the actual first clause range and independently reconstructed input equation.
        first=model['counter_rows'][0];inputs,bound,annotation=equations[0]
        with(D/'instance.cnf').open('rb')as stream:
            stream.readline();segment=b''.join(stream.readline()for _ in range(first['clause_count']))
        controls['actual_counter_corruptions_rejected']=[]
        for label in ['changed_bound','missing_input','missing_state','wrong_offset']:
            bad=deepcopy(first)
            if label=='changed_bound':bad['bound']=2
            elif label=='missing_input':bad['inputs'].pop()
            elif label=='missing_state':bad['states'].pop()
            else:bad['first_clause']=2
            try:gates.GateAudit(gates.ClauseCursor(io.BytesIO(segment),245880),5760).counter(bad,inputs,bound,True,annotation)
            except ValueError:controls['actual_counter_corruptions_rejected'].append(label)
            else:raise ValueError('actual counter corruption accepted '+label)
        save(args.out/'controls.json',controls)
        packages=[]
        for package in read(D/'artifact_packages.json')['packages']:
            compressed=b''.join(bind(ROOT/p['path'],p['sha256']).read_bytes()for p in package['ordered_parts'])
            need(hashlib.sha256(compressed).hexdigest()==package['compressed_stream_sha256'],'gzip stream')
            raw=gzip.decompress(compressed)
            need(len(raw)==package['raw_bytes']and hashlib.sha256(raw).hexdigest()==package['raw_sha256']==digest(ROOT/package['raw_path']),'exact gzip recovery')
            packages.append(dict(path=package['raw_path'],sha256=package['raw_sha256'],bytes=len(raw)))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_PRISM_ALL_COLUMNS.md']:bind(p)
        need(all(digest(ROOT/p)==sha for p,sha in bindings.items()),'stable inputs')
        report=dict(status='INDEPENDENT_SIX_PRISM_ALL_COLUMNS_CNF_ENCODING_PASS',claim_id='C-SIX-PRISM-COMPLETE-COLUMN-FACTOR-CNF',claim_revision=1,
          timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
          verifier='/root/state_literature_audit independent raw39/universe/equations/all-clause checker',recommendation='VERIFIED',review_state='CLEAR',kind='encoding',basis=['DERIVED','COMPUTED'],
          statement='The frozen245880variable874800clause formula is satisfiable exactly when a binary36x60 factor of the fixed six-prism core Gram exists, after bijective canonical C0 column relabelling; every such abstract factor appears, with no complement or five-matching restriction.',
          scope='Only the explicitly fixed identity-cross, standard-internal-matching six-prism39core. All normalized Gram factors, not all target cores.',
          assumptions=['The stated binary factor identity F F^T=K and sixty columns.','No nontrivial target automorphism is assumed.'],
          dependencies=[],dependencies_reason='Direct raw39 target-identity derivation and complete normalization proof are written here; prior five-pattern exclusions are not premises.',
          variables=245880,clauses=874800,primary_variables=5760,canonical_columns=60,choices_per_column=96,complete_component_states=46656,retained_component_states=5760,
          equations=540,row_pair_equations=480,row_pair_incidence_entries=80640,controls=controls,packages=packages,
          mathematical_derivation='docs/AUDIT_20260930_PRISM_ALL_COLUMNS.md',derived_geometry_sha256=digest(args.out/'derived_geometry.json'),
          trusted_components=['Pinned independent GateAudit truth-table and prefix induction checker, reused.','Python exact integers and standard library; tqdm imported by the independent helper.'],producer_imports=False,
          provenance_correction='Producer manifest omitted transitive theory_20260930_full_srg_validator.py import by Encoder; audit binds it explicitly. Frozen producer files/manifests unchanged.',
          limitations=['Outside-column overlap caps and residual D are unencoded.','A SAT factor is not a target graph.','No positive full36 research factor is claimed.','UNSAT requires a separately checked complete proof of this exact CNF.','No unrestricted target/core coverage.'],
          solver_calls=0,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as error:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(error),inputs_sha256=bindings));raise

if __name__=='__main__':main()
