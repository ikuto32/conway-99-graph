"""Freeze four unit-suffix recipes; no search and no claim self-promotion."""
from datetime import datetime,timezone
from hashlib import sha256
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_unrestricted_full99_cnf'
OUT=ROOT/'acceleration/results/20260930_unrestricted_four_branches'
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def main():
    OUT.mkdir(exist_ok=False)
    model=D/'model.json';cnf=D/'instance.cnf'
    assert h(model)=='77089d0a9dd94919bff62aa1e552b758eca061f980524131ad8d1861acce7a8e'
    assert h(cnf)=='7029f5c0965d0121aec6ce24db2b9a3d2e201e85b72c8ef51595c63bb62b2138'
    m=json.loads(model.read_bytes());labels={tuple(v):15+i for i,v in enumerate(m['outer_labels'])}
    ids={tuple(sorted((e['u'],e['v']))):e['id'] for e in m['edge_variables']}
    u=labels[(0,2)];v=labels[(4,6)]
    fixed=ids[tuple(sorted((u,v)))];triple=[ids[tuple(sorted((u,labels[l])))]for l in [(0,3),(1,2),(1,3)]]
    assert len({fixed,*triple})==4
    save(OUT/'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'inputs_sha256':{p.relative_to(ROOT).as_posix():h(p)for p in [Path(__file__),model,cnf,ROOT/'docs/DERIVATION_20260930_UNRESTRICTED_FOUR_BRANCH_COVER.md',ROOT/'acceleration/results/20260930_independent_review/unrestricted_full99_cnf/summary.json',ROOT/'uv.lock']},
        'question':'Can the legacy disjoint-edge normalization be expressed as four exact independently reviewable canonical branch suffixes?',
        'selection':'All four canonical patterns000,001,100,110; no omitted solver outcomes or branch sampling.',
        'scope':'Candidate coverage of every target up to harmless relabeling, not an assumption of target automorphisms.',
        'resource_seconds':30,'solver_calls':0,'status':'CANDIDATE_COVERAGE_AND_LITERAL_MAPPING','success':'Separate mathematical coverage and exact recipe review before proof-based uses.'})
    records=[]
    for name,bits in [('a0',[0,0,0]),('a1_complement',[0,0,1]),('a1_cross',[1,0,0]),('a2_crosses',[1,1,0])]:
        units=[fixed]+[i if b else -i for i,b in zip(triple,bits)]
        suffix=''.join(str(lit)+' 0\n'for lit in units).encode('ascii');p=OUT/(name+'.units.cnfpart');p.write_bytes(suffix)
        digest=sha256();digest.update(b'p cnf 1186500 4136458\n')
        with cnf.open('rb')as f:
            assert f.readline()==b'p cnf 1186500 4136454\n'
            for block in iter(lambda:f.read(1048576),b''):digest.update(block)
        digest.update(suffix)
        records.append({'branch':name,'pattern_xyz':bits,'units':units,'suffix':p.relative_to(ROOT).as_posix(),'suffix_sha256':h(p),'cnf_sha256':digest.hexdigest(),'variables':1186500,'clauses':4136458,
            'recipe':'Replace exactly the base header with p cnf 1186500 4136458 LF; copy its entire body verbatim; append the exact suffix bytes.'})
    pi=list(range(99));symbol=[2,3,0,1,*range(4,14)]
    for s in range(14):pi[1+s]=1+symbol[s]
    for lab,vertex in labels.items():pi[vertex]=labels[tuple(sorted(symbol[s]for s in lab))]
    assert sorted(pi)==list(range(99)) and pi[u]==u and pi[v]==v
    save(OUT/'branches.json',{'fixed_edge':{'labels':[[0,2],[4,6]],'vertices':[u,v],'variable':fixed},'xyz_variables':triple,
        'exchange_pair_groups_0_1':pi,'branches':records,'solver_calls':0,'status':'CANDIDATE_PENDING_INDEPENDENT_COVERAGE_CHECK',
        'limitations':['No SAT/UNSAT result.','Branches are not assigned equal graph populations.','Historical fifth branch and its unproved UNSAT report are not proof premises.']})
    print(json.dumps({'branches':len(records),'fixed_variable':fixed,'xyz_variables':triple,'solver_calls':0}))
if __name__=='__main__':main()
