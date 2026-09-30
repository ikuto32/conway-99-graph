"""Candidate sixty-clause extension of the independently checked parity model."""
from datetime import datetime,timezone
from itertools import product
from pathlib import Path
import argparse,copy,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
PINS={B+'hadamard_balanced_parity/instance.cnf':'92801921a62236effa19b0f6e7463c6f5c1ca2cb0b6957cf7d315a73e0e43fca',
 B+'hadamard_balanced_parity/model.json':'a75b60c4ef0f8decd7537d70cced7bffa14cb7a4881de726bf98c96635888147',
 B+'hadamard_balanced_parity_native_pilot/main/parsed_model.json':'0451ffb8b9b6712cd993d7259aa75f3e534845cec34cf7384c534825a0a3ff59',
 B+'independent_review/hadamard_balanced_parity_sat_v2/summary.json':'d2536119ac3fa0d45c190a6562de2ccc67c3f9c9765fbfc03257e37b15097f9c'}
def h(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        for p,sha in PINS.items():assert h(ROOT/p)==sha,p
        original=json.loads((ROOT/(B+'hadamard_balanced_parity/model.json')).read_bytes());model=copy.deepcopy(original)
        raw=(ROOT/(B+'hadamard_balanced_parity/instance.cnf')).read_bytes();header,body=raw.split(b'\n',1);assert header==b'p cnf 520 4481'
        baseclauses=[[int(x)for x in line.split()[:-1]]for line in body.splitlines()];assert len(baseclauses)==4481
        assignment=json.loads((ROOT/(B+'hadamard_balanced_parity_native_pilot/main/parsed_model.json')).read_bytes())['assignment']
        values={abs(x):x>0 for x in assignment};assert set(values)==set(range(1,521))and len(assignment)==520
        assert all(any(values[abs(x)]==(x>0)for x in row)for row in baseclauses)
        cuts=[];false=[]
        for row in original['pair_rows']:
            groups=[term['group']for term in row['terms']];assert len(set(groups))==5
            differences=[term['difference_variable']for term in row['terms']]
            constants=[original['groups'][j]['selectors'][0]for j in groups]
            assert all(original['groups'][j]['parity_patterns'][0]==[0]*6 for j in groups)
            clause=differences+constants;assert len(set(clause))==10
            entry=dict(coordinates=row['coordinates'],groups=groups,difference_variables=differences,constant_selectors=constants,clause=clause)
            cuts.append(entry)
            if not any(values[v]for v in clause):false.append(entry)
        assert len(cuts)==60 and [r['coordinates']for r in false]==[[4,9],[7,11]]
        model.update(schema='BALANCED_TRIPLET_PARITY_SUPPORT_CUT_CNF_V1',clauses=4541,zero_disagreement_support_cuts=cuts,
            original_model_sha256=PINS[B+'hadamard_balanced_parity/model.json'],original_formula_sha256=PINS[B+'hadamard_balanced_parity/instance.cnf'],
            scope='Strengthened necessary balanced parity projection for one fixed support with column caps; no full-factor equivalence.')
        save(out/'model.json',model)
        appended=''.join(' '.join(map(str,row['clause']))+' 0\n'for row in cuts).encode()
        with(out/'instance.cnf').open('xb')as stream:stream.write(b'p cnf 520 4541\n'+body+appended)
        save(out/'added_clauses.json',cuts)
        truth=0
        for bits in product(range(2),repeat=10):
            assert any(bits)==(any(bits[:5])or any(bits[5:]));truth+=1
        assert truth==1024 and not any([0]*10)and any([1]+[0]*9)and any([0]*5+[1]+[0]*4)
        save(out/'old_witness_rejection.json',dict(old_formula_satisfied=True,violated_new_clauses=false,
            old_claim_invalidated=False,reason='Old claim was projection feasibility only; the stricter formula is a new experiment.'))
        save(out/'controls.json',dict(truth_assignments=truth,all_zero_negative=True,single_disagreement_positive=True,single_constant_positive=True))
        assert time.monotonic()-start<60
        pins=dict(PINS)
        for p in ['acceleration/theory_20260930_hadamard_parity_support_cuts.py','acceleration/theory_20260930_hadamard_parity_support_cuts_spec.md','uv.lock','pyproject.toml']:pins[p]=h(ROOT/p)
        save(out/'summary.json',dict(status='CANDIDATE_BALANCED_PARITY_SUPPORT_CUT_MODEL',timestamp=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():h(p)for p in out.iterdir()if p.is_file()},
            variables=520,clauses=4541,original_clauses=4481,added_clauses=60,old_witness_violations=2,solver_calls=0,independent_approval=False,target_resolution='UNKNOWN'))
        print(json.dumps(dict(status='CANDIDATE_BALANCED_PARITY_SUPPORT_CUT_MODEL',variables=520,clauses=4541,old_witness_violations=2,solver_calls=0)))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=h(__file__)));raise
if __name__=='__main__':main()
