"""Candidate entailed pair-equality units; separate independent review required."""
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,product
import argparse
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
GATE=ROOT/'acceleration/results/20260930_independent_review/unrestricted_full99_cnf/summary.json'
GATE_SHA='2d6702d0f60341378fcf6b5b0808e6c34ea6a1025775cfae60500626f199ef58'
MODEL=ROOT/'acceleration/results/20260930_unrestricted_full99_cnf/model.json'
CNF=MODEL.with_name('instance.cnf')

def require(condition,message):
    if not condition:raise ValueError(message)
def digest(path):
    h=sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):h.update(block)
    return h.hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def save(path,data):
    with path.open('x',encoding='utf-8') as stream:json.dump(data,stream,indent=2);stream.write('\n')

def threshold_reference(row):
    residual=2-row['constant'];m=len(row['inputs'])
    require(row['residual_before_trivial_cap_fold']==residual and row['bound']==min(residual,m),'original residual and folded bound')
    require(residual>=0,'unexpected negative residual in authenticated cap')
    if residual==0:return True
    if residual>m:return False
    states={(i,j):value for i,j,value in row['states']}
    require((m,residual) in states,'needed final threshold present')
    return states[m,residual]

def controls():
    tested=0
    for n in range(6):
        for r in range(n+2):
            for bits in product((0,1),repeat=n):
                # Semantic positive controls for the exact final threshold.
                state=[(n,r,sum(bits)>=r)] if 0<r<=n else []
                row=dict(constant=2-r,inputs=list(range(1,n+1)),states=state,
                         residual_before_trivial_cap_fold=r,bound=min(r,n))
                ref=threshold_reference(row)
                require(ref is (sum(bits)>=r),'threshold semantic fixture')
                if sum(bits)<=r:require((ref is True)==(sum(bits)==r),'upper plus lower equals exact count')
                tested+=1
    rejected=[]
    row=dict(constant=1,inputs=[1,2],states=[[2,1,7]],residual_before_trivial_cap_fold=1,bound=1)
    require(threshold_reference(row)==7,'literal-reference positive control')
    for name,bad in [('wrong_residual',{**row,'residual_before_trivial_cap_fold':2}),
                     ('wrong_folded_bound',{**row,'bound':0}),('missing_needed_threshold',{**row,'states':[]})]:
        try:threshold_reference(bad)
        except ValueError:rejected.append(name)
        else:raise ValueError('corrupted primitive accepted: '+name)
    exact=[triple for triple in product(range(3),repeat=3) if sum(triple)==6]
    require(exact==[(2,2,2)],'positive global tightness control')
    require((1,2,2) in [triple for triple in product(range(3),repeat=3) if sum(triple)==5], 'missing total-tightness counterexample')
    return dict(status='PRODUCER_CONTROLS_PASS_PENDING_INDEPENDENT_REVIEW',threshold_bit_fixtures=tested,
                literal_reference_positive=True,corrupted_rows_rejected=rejected,global_tightness_positive=True,
                weakened_total_does_not_imply_all_equal=True,independent_verification=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);started=time.monotonic();bindings={}
    def cap():require(time.monotonic()-started<120,'producer120second cap')
    def bind(path,expected=None):
        value=digest(path);require(expected is None or value==expected,'input hash '+str(path));bindings[key(path)]=value
        return Path(path)
    try:
        gate=json.loads(bind(GATE,GATE_SHA).read_bytes());require(gate['status']=='INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS','independent base encoding gate')
        model=json.loads(bind(MODEL,gate['inputs_sha256'][key(MODEL)]).read_bytes());bind(CNF,gate['inputs_sha256'][key(CNF)])
        for name in ('acceleration/audit_20260930_unrestricted_full99_cnf_v1.py','acceleration/audit_20260930_eight_full99_cnf_v1.py',
                     'docs/AUDIT_20260930_UNRESTRICTED_FULL99_ENCODING_DERIVATION.md'):
            bind(ROOT/name,gate['inputs_sha256'][name])
        for path in (__file__,Path(__file__).with_suffix('.md'),ROOT/'uv.lock',ROOT/'pyproject.toml'):bind(path)
        save(args.out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
            uv_version=subprocess.check_output(['uv','--version'],text=True).strip(),inputs_sha256=bindings,
            question='Which lower-threshold units explicitly expose the globally entailed equality of every common-neighbor cap?',
            scope='All4851pairs in exact unrestricted full99 encoding; no new target restriction',selection='Every pair row, in raw model order',
            limits=dict(producer_seconds=120,solver_calls=0),numerical_threshold=None,numerical_threshold_null_reason='Exact Boolean/integer arithmetic only',
            random_seed=None,random_seed_null_reason='Deterministic full enumeration',status='CANDIDATE_PROPAGATION_AUGMENTATION'))
        save(args.out/'controls.json',controls());cap()
        known=model['known_adjacency_full99'];expressions=[[bool(x) if x>=0 else None for x in row] for row in known]
        for record in model['edge_variables']:expressions[record['u']][record['v']]=expressions[record['v']][record['u']]=record['id']
        rows=model['counter_rows'];require(len(rows)==4950 and all(row['kind']=='degree' for row in rows[:99]),'all99degree rows first')
        decisions=Counter();unit_to_pairs={};contradictions=[];product_index=0;raw_path=args.out/'rows.jsonl'
        with raw_path.open('x',encoding='utf-8',newline='\n') as stream:
            for pair_index,(u,v) in enumerate(tqdm(list(combinations(range(99),2)),desc='Candidate all-pair equality units')):
                row=rows[99+pair_index];require(row['kind']=='pair_cap' and row['pair']==[u,v] and row['equality'] is False,'raw pair order/sense')
                inputs=[];constant=0;constant_witnesses=[];linear=[];quadratic=[]
                for w in range(99):
                    if w in (u,v):continue
                    left,right=expressions[u][w],expressions[v][w]
                    if left is False or right is False:continue
                    if left is True and right is True:
                        constant+=1;constant_witnesses.append(['common',w])
                    elif type(left) is bool or type(right) is bool:
                        variable=right if left is True else left;inputs.append(variable)
                        linear.append([variable,w,'left_fixed_one' if left is True else 'right_fixed_one'])
                    else:
                        record=model['product_variables'][product_index];product_index+=1
                        require(record['pair']==[u,v] and record['center']==w and record['left']==left and record['right']==right,'raw exact product provenance')
                        inputs.append(record['id']);quadratic.append([record['id'],w,left,right])
                adjacent=expressions[u][v]
                if adjacent is True:constant+=1;constant_witnesses.append(['adjacency',u,v])
                elif type(adjacent) is int:inputs.append(adjacent);linear.append([adjacent,None,'adjacency'])
                require(row['constant']==constant and row['inputs']==inputs,'complete raw polynomial matches row')
                reference=threshold_reference(row);m=len(inputs);residual=2-constant
                if type(reference) is bool:
                    decision='TAUTOLOGY' if reference else 'CONTRADICTION';literal=None
                    if not reference:contradictions.append([u,v])
                else:
                    require(type(reference) is int and 1<=reference<=model['variables'],'exact positive threshold variable')
                    decision='UNIT';literal=reference;unit_to_pairs.setdefault(literal,[]).append([u,v])
                decisions[decision]+=1
                output=dict(pair=[u,v],counter_row_index=99+pair_index,constant=constant,constant_contribution_witnesses=constant_witnesses,
                    polynomial_input_variables=inputs,linear_terms=linear,quadratic_terms=quadratic,
                    term_schemas=dict(linear=['variable','common_neighbor_or_null_for_adjacency','kind'],quadratic=['product_variable','common_neighbor','left_edge_variable','right_edge_variable']),
                    original_exact_residual=residual,encoded_upper_bound=row['bound'],input_count=m,
                    final_threshold_index=[m,residual],final_threshold_reference=reference,decision=decision,unit_literal=literal,
                    unit_literal_null_reason=None if literal is not None else 'The required final threshold is the recorded Boolean constant.',
                    upper_row_first_clause=row['first_clause'],upper_row_clause_count=row['clause_count'])
                stream.write(json.dumps(output,separators=(',',':'))+'\n')
                if pair_index%250==0:cap()
        require(product_index==len(model['product_variables'])==285852 and sum(decisions.values())==4851,'complete polynomial coverage')
        units=sorted(unit_to_pairs);unit_path=args.out/'pair_equalities.units.cnfpart'
        unit_bytes=b''.join(f'{literal} 0\n'.encode() for literal in units)+(b'0\n' if contradictions else b'')
        with unit_path.open('xb') as stream:stream.write(unit_bytes)
        save(args.out/'units.json',dict(units=units,unit_to_pairs=[dict(literal=literal,pairs=unit_to_pairs[literal]) for literal in units],
            contradictions=contradictions,contradiction_clause_added=bool(contradictions),row_decisions=dict(decisions),
            source_cnf_sha256=digest(CNF),source_model_sha256=digest(MODEL),source_gate_sha256=GATE_SHA,
            status='CANDIDATE_REQUIRES_SEPARATE_INDEPENDENT_UNIT_AND_ENTAILMENT_AUDIT'))
        added=len(units)+bool(contradictions);h=sha256();new_header=f"p cnf {model['variables']} {model['clauses']+added}\n".encode()
        h.update(new_header)
        with CNF.open('rb') as stream:
            require(stream.readline()==f"p cnf {model['variables']} {model['clauses']}\n".encode(),'exact base header')
            for block in iter(lambda:stream.read(1<<20),b''):h.update(block)
        h.update(unit_bytes)
        compressed_path=args.out/'rows.jsonl.gz'
        with raw_path.open('rb') as source,compressed_path.open('xb') as target,gzip.GzipFile(fileobj=target,mode='wb',mtime=0) as zipped:
            for block in iter(lambda:source.read(1<<20),b''):zipped.write(block)
        require(compressed_path.stat().st_size<10*1024*1024,'public compressed row metadata below10MiB')
        with gzip.open(compressed_path,'rb') as stream:
            replay=sha256()
            for block in iter(lambda:stream.read(1<<20),b''):replay.update(block)
        require(replay.hexdigest()==digest(raw_path),'row compression roundtrip');cap()
        require(all(digest(ROOT/name)==value for name,value in bindings.items()),'stable inputs')
        outputs={key(path):dict(sha256=digest(path),bytes=path.stat().st_size) for path in args.out.iterdir() if path.is_file()}
        summary=dict(status='CANDIDATE_UNRESTRICTED_PAIR_EQUALITY_UNITS',timestamp=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),inputs_sha256=bindings,outputs=outputs,
            pair_rows=4851,polynomial_product_terms=product_index,row_decisions=dict(decisions),distinct_positive_units=len(units),
            duplicate_unit_occurrences=decisions['UNIT']-len(units),contradiction_rows=len(contradictions),added_clauses=added,
            future_augmented_cnf_sha256=h.hexdigest(),future_variables=model['variables'],future_clauses=model['clauses']+added,
            recipe='Replace base header with future counts and LF, copy complete base body byte-for-byte, append exactpair_equalities.units.cnfpart bytes.',
            exact_entailment_argument='Degree14 fixes total common+adjacency sum to9702;4851 caps eachatmost2 therefore all equal2. Every authenticated bidirectional threshold t(m,2-c) must be true.',
            intended_scope='Redundant propagation augmentation of exact unrestricted base, no additional graph assumption.',
            expected_performance_benefit=None,expected_performance_benefit_null_reason='No solver comparison has been run; stronger propagation is a hypothesis.',
            independent_review=None,independent_review_null_reason='This is a discovery artifact; root will independently check every row/unit before use.',
            elapsed_seconds=time.monotonic()-started,solver_calls=0,base_modified=False,target_resolution=False)
        save(args.out/'summary.json',summary)
        print(json.dumps(dict(status=summary['status'],row_decisions=dict(decisions),units=len(units),summary_sha256=digest(args.out/'summary.json'))))
    except BaseException as error:
        save(args.out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),status='PRODUCER_FAILURE_PRESERVED',type=type(error).__name__,message=str(error),elapsed_seconds=time.monotonic()-started))
        raise

if __name__=='__main__':main()
