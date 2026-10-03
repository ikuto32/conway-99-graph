"""Independent fixed-core positive-unit mapping and exact augmented-byte audit."""
from copy import deepcopy
from datetime import datetime, timezone
from itertools import combinations, permutations
from pathlib import Path
import argparse
import hashlib
import io
import json
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_connected_fixed_core_cnf'
BASE=ROOT/'acceleration/results/20260930_variable_core_factor_cnf'
GATES={
 'acceleration/results/20260930_independent_review/variable_core_factor_cnf_v2/summary.json':
 ('ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0','INDEPENDENT_VARIABLE_CORE_FACTOR_CNF_ENCODING_PASS'),
 'acceleration/results/20260930_independent_review/connected_identity_cores/summary.json':
 ('efdcacb9130bf29a28ece4c07022bdab11ab953a862f117fc55f44bd5244d2b4','INDEPENDENT_CONNECTED_IDENTITY_CORE_PORTFOLIO_PASS')}
BATCH_SHA='39425b88f3fa5e46d95c3f4231b044c05484fc9d209250d7c045de6589cd82d6'
def need(x,s):
    if not x: raise ValueError(s)
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def expected_rows(core):
    need(all(core[k]==list(range(12)) for k in ['P','cross01','cross02']),'declared identity crosses')
    need(core['M0']==[i^1 for i in range(12)],'standard M0')
    out=[];pairs=list(combinations(range(12),2))
    for g in (1,2):
        q=core[f'M{g}'];need(len(q)==12 and all(type(x) is int and 0<=x<12 for x in q),'matching type')
        need(all(q[a]!=a and q[q[a]]==a for a in range(12)),'matching involution')
        for j,(a,b) in enumerate(pairs):
            if q[a]==b:out.append(dict(kind='matching',fibre=g,endpoints=[a,b],literal=1441+66*(g-1)+j))
    out += [dict(kind='permutation',row=i,column=i,literal=1573+13*i) for i in range(12)]
    need(len(out)==24 and len({r['literal'] for r in out})==24,'24 distinct unit variables')
    return out

def core_check(core):
    expected_rows(core);c=[[0]*36 for _ in range(36)]
    for g in range(3):
        for a,b in enumerate(core[f'M{g}']):c[12*g+a][12*g+b]=1
    for g,h in [(0,1),(0,2),(1,2)]:
        for a in range(12):c[12*g+a][12*h+a]=c[12*h+a][12*g+a]=1
    need(c==core['core_adjacency'],'literal cubic core reconstruction')
    h=[[0]*39 for _ in range(39)]
    for a,b in combinations(range(3),2):h[a][b]=h[b][a]=1
    for g in range(3):
        for a in range(12):h[g][3+12*g+a]=h[3+12*g+a][g]=1
    for a in range(36):h[3+a][3:]=c[a][:]
    need(h==core['full39_adjacency'],'literal 39-vertex reconstruction')
    nb=[{j for j,x in enumerate(row) if x} for row in h]
    need(all(len(nb[a]&nb[b])<=2-h[a][b] for a,b in combinations(range(39),2)),'all 39 pair caps')
    gram=[[2-int(a//12==b//12)-c[a][b]-sum(c[a][k]*c[k][b] for k in range(36))+
           12*int(a==b) for b in range(36)] for a in range(36)]
    need(gram==core['target_gram'],'literal exact target Gram')
    return dict(vertices=39,pair_caps=741,Gram_entries=1296)

def metadata(model):
    pairs=list(combinations(range(12),2))
    matches=[dict(id=1441+66*(g-1)+j,fibre=g,endpoints=[a,b]) for g in (1,2) for j,(a,b) in enumerate(pairs)]
    perms=[dict(id=1573+12*a+b,row=a,column=b) for a in range(12) for b in range(12)]
    need(model['matching_variables']==matches and model['permutation_variables']==perms,'independent lexicographic ID map')
    need((model['variables'],model['clauses'])==(110904,518160),'base dimensions')

def compare_cnf(base,aug,literals,variables=110904,clauses=518160):
    need(base.readline()==f'p cnf {variables} {clauses}\n'.encode(),'base exact header')
    need(aug.readline()==f'p cnf {variables} {clauses+len(literals)}\n'.encode(),'augmented exact header')
    for i in range(clauses):
        line=base.readline();need(line.endswith(b' 0\n'),'base complete clause boundary')
        need(aug.readline()==line,'exact unchanged base clause '+str(i))
    need(base.read()==b'','base complete population')
    need(aug.read()==b''.join(f'{v} 0\n'.encode() for v in literals),'exact positive-unit suffix')

def bind_inputs():
    inputs={};batch=read(D/'summary.json')
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'hash '+key(p));inputs[key(p)]=value
    pin(D/'summary.json',BATCH_SHA)
    need(batch['schema']=='CONNECTED_FIXED_CORE_CNF_BATCH_V1','batch schema')
    for p,(h,status) in GATES.items():
        pin(ROOT/p,h);gate=read(ROOT/p);need(gate['status']==status,'independent prerequisite gate')
        for path,value in gate['inputs_sha256'].items():pin(ROOT/path,value)
    for path,value in {**batch['inputs_sha256'],**batch['outputs_sha256']}.items():pin(ROOT/path,value)
    need([r['core_index'] for r in batch['records']]==list(range(4)),'exact four-core index population')
    model=read(BASE/'model.json');metadata(model)
    return batch,model,inputs

def controls():
    rejected=[]
    def reject(name,fn):
        try:fn()
        except ValueError:rejected.append(name)
        else:raise AssertionError(name)
    def matchings(points):
        if not points:yield set();return
        a,*rest=points
        for b in rest:
            for tail in matchings([x for x in rest if x!=b]):yield {(min(a,b),max(a,b))}|tail
    ms=list(matchings(list(range(6))))
    need(len(ms)==15 and all(sum(want<=other for other in ms)==1 for want in ms),'all 15 matching domains and fixing sets')
    ps=list(permutations(range(4)))
    need(all(sum(all(other[i]==want[i] for i in range(4)) for other in ps)==1 for want in ps),'all 24 permutation domains')
    b=b'p cnf 3 2\n1 -2 0\n2 3 0\n';a=b'p cnf 3 4\n1 -2 0\n2 3 0\n1 0\n3 0\n'
    compare_cnf(io.BytesIO(b),io.BytesIO(a),[1,3],3,2)
    for name,bad in [('wrong_header',a.replace(b'3 4',b'3 3',1)),('changed_base_clause',a.replace(b'1 -2',b'-1 -2',1)),
                     ('omitted_unit',a[:-4]),('negative_unit',a.replace(b'3 0\n',b'-3 0\n')),
                     ('duplicate_suffix',a+b'3 0\n'),('wrong_unit_order',a[:-8]+b'3 0\n1 0\n')]:
        reject(name,lambda bad=bad:compare_cnf(io.BytesIO(b),io.BytesIO(bad),[1,3],3,2))
    core=read(D/'core_00/core.json');rows=expected_rows(core)
    for name,change in [('omitted_semantic_unit',lambda r:r.pop()),('duplicate_semantic_unit',lambda r:r.append(r[0])),
                        ('wrong_edge_literal',lambda r:r[0].update(literal=r[0]['literal']+1))]:
        bad=deepcopy(rows);change(bad);reject(name,lambda:need(bad==expected_rows(core),'exact unit population/map'))
    for name,field in [('changed_matching','M1'),('changed_core','core_adjacency'),('changed_Gram','target_gram')]:
        bad=deepcopy(core)
        if field=='M1':bad[field][0]=0
        else:bad[field][0][0]^=1
        reject(name,lambda:core_check(bad))
    return dict(complete_small_matching_domains=15,complete_small_permutation_domains=24,
                synthetic_byte_positive=True,corruptions_rejected=rejected)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    try:
        batch,model,inputs=bind_inputs();checks=[]
        for r in batch['records']:
            core=read(ROOT/r['core_path']);units=read(ROOT/r['units_path']);rows=expected_rows(core)
            need(core==read(ROOT/f"acceleration/results/20260930_connected_identity_cores/core_{r['core_index']:02d}.json"),'exact audited selected core')
            need(units==dict(core_index=r['core_index'],core_path=r['core_path'],core_sha256=r['core_sha256'],rows=rows),'all unit semantics')
            for typ in ['core','units','cnf']:
                need(digest(ROOT/r[typ+'_path'])==r[typ+'_sha256'],'record input hash')
            need(r['base_model_path']==key(BASE/'model.json') and r['base_model_sha256']==digest(BASE/'model.json'),'common exact model')
            need((r['variables'],r['clauses'],r['added_positive_units'])==(110904,518184,24),'case dimensions')
            with (BASE/'instance.cnf').open('rb') as b,(ROOT/r['cnf_path']).open('rb') as a:
                compare_cnf(b,a,[x['literal'] for x in rows])
            checks.append(dict(core_index=r['core_index'],units=[x['literal'] for x in rows],
                               all_base_clauses_checked=518160,positive_units_checked=24,**core_check(core)))
        control=controls();save(args.out/'controls.json',control);save(args.out/'case_checks.json',checks)
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_CONNECTED_FIXED_CORE_CNF.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:
            inputs[key(p)]=digest(p)
        now=datetime.now(timezone.utc).isoformat()
        report=dict(status='INDEPENDENT_CONNECTED_FIXED_CORE_CNF_BATCH_PASS',timestamp=now,inputs_sha256=inputs,
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),cases=checks,
            claim_id='C-FOUR-CONNECTED-FIXED-CORE-FACTOR-CNF',claim_revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],
            recommendation='VERIFIED',review_state='CLEAR',
            statement='Each of the four frozen augmented CNFs is exactly the independently checked necessary variable-core factor encoding restricted to its stated connected core, via 24 positive units fixing both matchings and the identity cross permutation.',
            scope='Four particular raw connected identity-P cores; necessary incidence factors with all base caps, no residual D.',
            assumptions=['No nontrivial target automorphism is assumed.'],
            dependencies=[dict(id='C-FOUR-CONNECTED-IDENTITY-CORE-PORTFOLIO',revision=1,relation='uses_result'),
                          dict(id='C-UNRESTRICTED-VARIABLE-CORE-FACTOR-CNF',revision=1,relation='encoding_equivalence')],
            verifier='/root/state_literature_audit',method='independent_artifact_check_and_derivation',
            shared_components=['Python standard library; authenticated prior independent base encoding and domain gates.','No producer imports.'],
            mathematical_audit='docs/AUDIT_20260930_CONNECTED_FIXED_CORE_CNF.md',
            outputs_sha256={key(p):digest(p) for p in args.out.iterdir() if p.is_file()},
            controls=control,artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False,
            limitations=['These four cores are not a complete target normalization or coverage.',
                         'No solver was run; no factor, graph or UNSAT result is asserted.',
                         'Base encoding correctness is inherited from its exact independently checked gate; this audit checks all appended bytes and their semantics.'],
            created_at=now,updated_at=now)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
