"""Independent all-clause full99 audit via Boolean truth-table prime implicates."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from functools import lru_cache
from hashlib import sha256
from itertools import combinations,product
import gzip
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]


def need(condition,message):
    if not condition:raise ValueError(message)
def digest(path):
    h=sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda:stream.read(1<<20),b''):h.update(data)
    return h.hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def save(path,value):
    with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2);stream.write('\n')


@lru_cache(None)
def truth_relation(signature):
    """F=a OR(b AND c), deriving aliases or all prime CNF implicates."""
    n=1+max((value for kind,value in signature if kind=='v'),default=-1)
    assignments=list(product((False,True),repeat=n))
    truth=[]
    for bits in assignments:
        a,b,c=[bool(value) if kind=='c' else bits[value] for kind,value in signature]
        truth.append(a or(b and c))
    if all(x==truth[0] for x in truth):return ('constant',truth[0])
    for index in range(n):
        if all(answer==bits[index] for bits,answer in zip(assignments,truth)):return ('input',index)
    good=[bits+(answer,) for bits,answer in zip(assignments,truth)]
    implicates=[]
    for signs in product((-1,0,1),repeat=n+1):
        clause=frozenset((i+1)*sign for i,sign in enumerate(signs) if sign)
        if clause and all(any(bits[abs(lit)-1]==(lit>0) for lit in clause) for bits in good):implicates.append(clause)
    primes=tuple(sorted(tuple(sorted(clause)) for clause in implicates if not any(other<clause for other in implicates)))
    # Exhaust the full gate relation, including both possible output values.
    for bits in product((False,True),repeat=n+1):
        observed=all(any(bits[abs(lit)-1]==(lit>0) for lit in clause) for clause in primes)
        need(observed==(bits in good),'prime-clause truth equivalence')
    return ('clauses',primes)


def gate_expectation(a,b,c,output):
    inputs=[];signature=[]
    for reference in (a,b,c):
        if type(reference) is bool:signature.append(('c',int(reference)))
        else:
            need(type(reference) is int and reference>0,'positive gate input reference')
            if reference not in inputs:inputs.append(reference)
            signature.append(('v',inputs.index(reference)))
    kind,payload=truth_relation(tuple(signature))
    if kind!='clauses':
        expected=payload if kind=='constant' else inputs[payload]
        need(type(output) is type(expected) and output==expected,'incorrect folded constant/input alias')
        return [],False
    need(type(output) is int and output>0 and output not in inputs,'fresh nonconstant output')
    variables=inputs+[output]
    return [tuple(sorted(variables[abs(lit)-1]*(1 if lit>0 else -1) for lit in clause)) for clause in payload],True


class ClauseCursor:
    def __init__(self,stream,variables):self.stream=stream;self.variables=variables;self.count=0
    def consume(self,expected):
        observed=[]
        for _ in expected:
            raw=self.stream.readline();need(raw,'missing raw CNF clause')
            numbers=list(map(int,raw.split()))
            need(numbers and numbers[-1]==0 and all(0<abs(x)<=self.variables for x in numbers[:-1]),'raw DIMACS literal/terminator')
            literals=numbers[:-1]
            need(len(literals)==len(set(literals)) and not any(-x in literals for x in literals),'duplicate/tautological raw clause')
            observed.append(tuple(sorted(literals)));self.count+=1
        need(Counter(observed)==Counter(expected),'raw clause segment differs from independent truth-relation CNF')


class GateAudit:
    def __init__(self,cursor,edge_variables):self.cursor=cursor;self.top=edge_variables;self.gates=Counter();self.aliases=0
    def gate(self,a,b,c,reference):
        clauses,fresh=gate_expectation(a,b,c,reference)
        for ref in (a,b,c):need(type(ref) is bool or 1<=ref<=self.top,'non-topological gate input')
        if fresh:
            need(reference==self.top+1,'fresh contiguous auxiliary variable')
            self.top+=1;self.gates[len(clauses)]+=1
        else:self.aliases+=1
        self.cursor.consume(clauses)
    def assert_reference(self,reference,value):
        if type(reference) is bool:self.cursor.consume([] if reference==value else [()])
        else:self.cursor.consume([(reference if value else -reference,)])
    def counter(self,row,inputs,bound,equality,annotation):
        need(all(row.get(name)==value and type(row.get(name)) is type(value) for name,value in annotation.items()),'direct row annotation')
        need(row['inputs']==inputs and len(inputs)==len(set(inputs)) and all(type(x) is int and 1<=x<=self.top for x in inputs),'exact unique cardinality inputs')
        need(type(row['bound']) is int and row['bound']==bound and type(row['equality']) is bool and row['equality']==equality and 0<=bound<=len(inputs),'exact cardinality sense/bound')
        first_clause=self.cursor.count+1;first_aux=self.top+1
        need(row['first_clause']==first_clause,'counter raw clause offset')
        expected_keys=[(i,j) for i in range(1,len(inputs)+1) for j in range(1,min(i,bound+1)+1)]
        need([(state[0],state[1]) for state in row['states']]==expected_keys and all(len(state)==3 for state in row['states']),'complete prefix-state universe/order')
        states={(i,j):ref for i,j,ref in row['states']}
        for i,j in expected_keys:
            a=states.get((i-1,j),False);b=inputs[i-1];c=True if j==1 else states.get((i-1,j-1),False)
            self.gate(a,b,c,states[i,j])
        if equality:self.assert_reference(True if bound==0 else states.get((len(inputs),bound),False),True)
        self.assert_reference(states.get((len(inputs),bound+1),False),False)
        need(row['clause_count']==self.cursor.count-first_clause+1,'counter complete clause range')
        expected_first=first_aux if self.top>=first_aux else None
        expected_last=self.top if expected_first is not None else None
        need(row['first_auxiliary_variable']==expected_first and row['last_auxiliary_variable']==expected_last,'counter auxiliary range')
        need((row['auxiliary_null_reason'] is None)==(expected_first is not None),'explicit auxiliary availability reason')


def toy_counter(n,bound,equality):
    top=n;states={};clauses=[]
    for i in range(1,n+1):
        for j in range(1,min(i,bound+1)+1):
            refs=(states.get((i-1,j),False),i,True if j==1 else states.get((i-1,j-1),False))
            local=[];signature=[]
            for ref in refs:
                if type(ref) is bool:signature.append(('c',int(ref)))
                else:
                    if ref not in local:local.append(ref)
                    signature.append(('v',local.index(ref)))
            kind,payload=truth_relation(tuple(signature))
            if kind=='constant':output=payload
            elif kind=='input':output=local[payload]
            else:top+=1;output=top
            added,_=gate_expectation(*refs,output);clauses.extend(added);states[i,j]=output
    def force(ref,value):
        if type(ref) is bool:
            if ref!=value:clauses.append(())
        else:clauses.append((ref if value else -ref,))
    if equality:force(True if bound==0 else states.get((n,bound),False),True)
    force(states.get((n,bound+1),False),False)
    return top,states,clauses


def controls():
    rows=[];assignments=0;wrong_helpers=0
    for n in range(5):
        for bound in range(n+1):
            for equality in (False,True):
                top,states,clauses=toy_counter(n,bound,equality);accepted=0
                for bits in product((False,True),repeat=n):
                    expected=sum(bits)==bound if equality else sum(bits)<=bound;extensions=0
                    for auxiliary in product((False,True),repeat=top-n):
                        values=bits+auxiliary;ok=all(any(values[abs(lit)-1]==(lit>0) for lit in clause) for clause in clauses)
                        assignments+=1;extensions+=ok;wrong_helpers+=bool(expected and not ok)
                        if ok:
                            for (i,j),reference in states.items():need((reference if type(reference) is bool else values[reference-1])==(sum(bits[:i])>=j),'direct threshold semantic control')
                    need(extensions==int(expected),'unique exact small-counter auxiliary extension');accepted+=extensions
                rows.append(dict(inputs=n,bound=bound,equality=equality,accepted_inputs=accepted))
    prime,_=gate_expectation(1,2,3,4)
    def stream(clauses):return io.BytesIO(b''.join((' '.join(map(str,c))+' 0\n').encode() for c in clauses))
    ClauseCursor(stream(prime),4).consume(prime)
    corrupted=[]
    for name,clauses in [('missing_clause',prime[:-1]),('wrong_sign',[tuple(-x if index==0 else x for index,x in enumerate(prime[0]))]+prime[1:]),('wrong_gate_relation',[(1,4)]+prime[1:])]:
        try:ClauseCursor(stream(clauses),4).consume(prime)
        except ValueError:corrupted.append(name)
        else:raise ValueError('corrupted gate clauses accepted: '+name)
    try:gate_expectation(False,1,True,2)
    except ValueError:corrupted.append('wrong_alias_reference')
    else:raise ValueError('corrupt alias accepted')
    need(wrong_helpers>0,'auxiliary corruption exercise')
    return dict(status='INDEPENDENT_TRUTH_RELATION_AND_PREFIX_CONTROLS_PASS',truth_relation_method='Complete Boolean truth relation and minimal implicate enumeration, not producer gate templates',
                counter_configurations=len(rows),full_assignments_checked=assignments,wrong_helper_assignments_rejected=wrong_helpers,
                known_valid_gate_stream_passed=True,corrupted_artifacts_rejected=corrupted,rows=rows,
                all_accepted_inputs_have_unique_correct_threshold_extension=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--seconds',type=float,default=900)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False);started=time.monotonic();bindings={}
    def read(path,expected=None):
        observed=digest(path);need(expected is None or observed==expected,'artifact hash mismatch: '+str(path));bindings[key(path)]=observed
        return json.loads(Path(path).read_bytes())
    calibration=controls();save(args.out/'controls.json',calibration)
    model_path,cnf_path=args.run/'model.json',args.run/'instance.cnf'
    model=read(model_path,'f2b7a649e74aa476380e14066239a188a2d2122d2ba1cc6e330e9a094d2cc0ee')
    need(digest(cnf_path)=='f247be8432d69f4feec037833a6923ef623e20c0aa0dbdea77fd13ec218d095b','frozen raw CNF identity');bindings[key(cnf_path)]=digest(cnf_path)
    producer_manifest=read(args.run/'manifest.json');producer_summary=read(args.run/'summary.json')
    validator_path=ROOT/'acceleration/audit_20260930_full99_sat_object.py'
    validator_controls_path=ROOT/'acceleration/results/20260930_independent_review/full99_sat_object_calibration/summary.json'
    validator_controls=read(validator_controls_path,'1d8329ebe0b1bad7801d7c3659447abcc944aeb112d1331132dc2bc650fd57c0')
    need(validator_controls['status']=='INDEPENDENT_FULL99_SAT_OBJECT_CHECKER_CALIBRATION_PASS','separately authored decoded-object validator calibration')
    need(digest(validator_path)=='65d90a85be5fe67c510e561839901e9b8b7c3b9fc1ab7439af0e6bd3746a380c','separate full99 validator source pin')
    bindings[key(validator_path)]=digest(validator_path)
    for name,value in producer_manifest['input_hashes'].items():need(digest(ROOT/name)==value,'producer input changed: '+name);bindings[name]=value
    need(bindings['acceleration/theory_20260930_eight_full99_cnf.py']=='21c357543c9397456a911175b277da6e6caa769be31d18c12e034cc76d99074c','producer source pin')
    domain=read(ROOT/'acceleration/results/20260930_independent_review/eight_domains_claim_binding.json','170871c99ed16a160bf1403e4f6443275ca00c3a6ce68775fb56ba5f02783302')
    need(domain['status']=='INDEPENDENT_EIGHT_COORDINATE_ALL84_BINDING_PASS','independent exact family gate')
    scope_path=ROOT/model['scope_path'];scope=read(scope_path,domain['inputs_sha256'][key(scope_path)])
    need(model['scope_sha256']==digest(scope_path),'model scope identity')
    resumed_path=ROOT/'acceleration/results/20260930_eight_domains/run01/manifest.json';resumed=read(resumed_path,domain['inputs_sha256'][key(resumed_path)])
    baseline_path=ROOT/'acceleration/results/20260916_star_guided_round2/search/probes/selection_03_index_18481_candidate.json'
    baseline=read(baseline_path,domain['inputs_sha256'][key(baseline_path)])
    labels=sorted([(a,b) for a in range(14) for b in range(a+1,14) if a//2!=b//2],key=lambda p:(p[0]//2,p[1]//2,p[0]%2,p[1]%2))
    supports=[{a//2,b//2} for a,b in labels]
    pairs=list(combinations(range(84),2))
    freed={pair for pair in pairs if len(supports[pair[0]]&supports[pair[1]])==1 and any(x<8 and x in labels[pair[1]] for x in labels[pair[0]])}
    fixed=set(map(tuple,baseline['overlap_edges_outer_zero_based']))-freed
    unknown=freed|{pair for pair in pairs if supports[pair[0]].isdisjoint(supports[pair[1]])}
    need(len(fixed)==120 and len(unknown)==2160 and len(freed)==480 and not fixed&unknown,'reconstructed family counts')
    for source in (scope,resumed):need(source['remaining_fixed_K_edges_outer']==list(map(list,sorted(fixed))) and source['unknown_edges_outer']==list(map(list,sorted(unknown))),'original/resumed audited family equality')
    known=[[0]*99 for _ in range(99)]
    def edge(u,v,value):known[u][v]=known[v][u]=value
    for u in range(1,15):edge(0,u,1)
    for u,v in combinations(range(1,15),2):
        if (u-1)//2==(v-1)//2:edge(u,v,1)
    for outer,label in enumerate(labels,15):
        for inner in label:edge(outer,inner+1,1)
    for u,v in fixed:edge(u+15,v+15,1)
    for u,v in unknown:edge(u+15,v+15,-1)
    need(model['known_adjacency_full99']==known and model['outer_labels']==list(map(list,labels)),'every raw99fixed/free state')
    need(model['fixed_K_edges']==list(map(list,sorted(fixed))) and model['unknown_edges_outer']==list(map(list,sorted(unknown))) and model['fixed_scaffold_edges']==189,'model family metadata')
    expressions=[[bool(x) if x>=0 else None for x in row] for row in known];edge_records=[]
    for u,v in combinations(range(99),2):
        if known[u][v]==-1:
            variable=len(edge_records)+1;edge_records.append(dict(u=u,v=v,id=variable));expressions[u][v]=expressions[v][u]=variable
    need(model['edge_variables']==edge_records,'exact2160edge bijection and order')
    need(model['degree_rows']==99 and model['pair_cap_rows']==4851 and len(model['counter_rows'])==4950,'complete direct row populations')
    protocol=ROOT/'docs/AUDIT_20260930_EIGHT_FULL99_ENCODING_DERIVATION.md'
    for path in (Path(__file__),protocol,ROOT/'uv.lock'):bindings[key(path)]=digest(path)
    save(args.out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
         command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
         question='Does every raw clause encode exactly the independently reconstructed full99degrees/caps within the frozen eight-coordinate family?',
         scope='Complete raw CNF/model, not a sampled check; no unrestricted target coverage',limits=dict(wall_seconds=args.seconds),numerical_threshold=None,numerical_threshold_null_reason='Exact integers and exhaustive Boolean truth tables only'))
    product_index=0;counter_index=0;checked_rows=[]
    with cnf_path.open('rb') as stream:
        need(stream.readline().split()==[b'p',b'cnf',str(model['variables']).encode(),str(model['clauses']).encode()],'exact DIMACS header')
        cursor=ClauseCursor(stream,model['variables']);audit=GateAudit(cursor,len(edge_records))
        for u in range(99):
            inputs=[x for x in expressions[u] if type(x) is int];constant=sum(x is True for x in expressions[u])
            audit.counter(model['counter_rows'][counter_index],inputs,14-constant,True,dict(kind='degree',vertex=u,original_bound=14,constant=constant));counter_index+=1
        for u,v in tqdm(list(combinations(range(99),2)),desc='Independent full99 pair clauses'):
            inputs=[];constant=0
            for w in range(99):
                if w in (u,v):continue
                left,right=expressions[u][w],expressions[v][w]
                if left is False or right is False:continue
                if left is True and right is True:constant+=1
                elif left is True:inputs.append(right)
                elif right is True:inputs.append(left)
                else:
                    need(product_index<len(model['product_variables']),'missing unknown product')
                    record=model['product_variables'][product_index];product_index+=1
                    need(record['left']==left and record['right']==right and record['pair']==[u,v] and record['center']==w,'direct common-neighbor product identity')
                    need(record['first_clause']==cursor.count+1 and record['clause_count']==3,'product raw clause range')
                    audit.gate(False,left,right,record['id']);inputs.append(record['id'])
            adjacent=expressions[u][v]
            if adjacent is True:constant+=1
            elif type(adjacent) is int:inputs.append(adjacent)
            residual=2-constant;need(residual>=0,'unexpected already-impossible constant cap')
            audit.counter(model['counter_rows'][counter_index],inputs,min(residual,len(inputs)),False,
                          dict(kind='pair_cap',pair=[u,v],original_bound=2,constant=constant,residual_before_trivial_cap_fold=residual));counter_index+=1
            if counter_index%250==0:need(time.monotonic()-started<args.seconds,'audit wall cap')
        need(stream.read()==b'','extra raw CNF bytes/clauses')
    need(counter_index==4950 and product_index==len(model['product_variables'])==110640,'complete direct polynomial/product coverage')
    need(cursor.count==model['clauses']==1684724 and audit.top==model['variables']==485165,'complete raw clause/variable coverage')
    packages=read(args.run/'artifact_packages.json');package_checks=[]
    for package in packages['packages']:
        compressed=b''
        for part in package['ordered_parts']:
            path=ROOT/part['path'];need(path.stat().st_size==part['bytes'] and part['bytes']<10*1024*1024 and digest(path)==part['sha256'],'compressed part identity/size')
            bindings[key(path)]=digest(path);compressed+=path.read_bytes()
        need(sha256(compressed).hexdigest()==package['compressed_stream_sha256'],'ordered compressed stream identity')
        h=sha256();size=0
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as zipped:
            for block in iter(lambda:zipped.read(1<<20),b''):h.update(block);size+=len(block)
        need(h.hexdigest()==package['raw_sha256']==digest(ROOT/package['raw_path']) and size==package['raw_bytes'],'independent public-package decompression identity')
        package_checks.append(dict(raw_path=package['raw_path'],raw_sha256=h.hexdigest(),raw_bytes=size,independent_decompression='PASS'))
    need(all(digest(ROOT/name)==value for name,value in bindings.items()),'input/source stability')
    report=dict(status='INDEPENDENT_EIGHT_FULL99_CNF_ENCODING_PASS',claim_id='C-PARTIAL-K-EIGHT-COORDINATE-FULL99-SAT-ENCODING',claim_revision=1,recommendation='VERIFIED',
                timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                verifier='/root/eight_domain_audit independent checking agent',verification_type='Independent raw-scope and polynomial reconstruction, complete prime-implicate clause comparison, threshold induction, and exact package replay',
                inputs_sha256=bindings,controls=calibration,known_fixed_scaffold_edges=189,fixed_outer_edges=120,unknown_outer_edges=2160,prescribed_absent_unordered_pairs=2382,
                variables=audit.top,edge_variables=2160,product_variables=product_index,prefix_variables=audit.top-2160-product_index,clauses=cursor.count,
                degree_rows=99,pair_cap_rows=4851,gate_clause_populations=dict(audit.gates),folded_alias_states=audit.aliases,independent_package_checks=package_checks,
                statement='The exact saved CNF is satisfiable if and only if there is a99vertex symmetric binary zero-diagonal adjacency satisfying A²=12I-A+2J and every fixed present/absent entry of this exact eight-coordinate family. Every auxiliary product and threshold has full Boolean equivalence.',
                scope='Only the pinned189scaffold/120fixedK/2160unknown family; not unrestricted target coverage.',basis=['DERIVED','COMPUTED'],kind='encoding',
                dependencies=[dict(id='C-PARTIAL-K-EIGHT-COORDINATE-DOMAINS',revision=1,relation='encoding_equivalence')],
                written_derivation=key(protocol),degree_cap_sum=dict(degree=14,edges=693,common_neighbor_sum=9009,cap_lhs_sum=9702,cap_upper_sum=9702),
                producer_imported=False,solver_launched=False,shared_components=['Raw authenticated domain/model/CNF artifacts','Python exact integers; no producer or third-party cardinality code imported'],
                separate_decoded_object_validator=dict(source=key(validator_path),source_sha256=digest(validator_path),calibration=key(validator_controls_path),calibration_sha256=digest(validator_controls_path),
                                                       relationship='Separately authored by /root/state_literature_audit; its calibration is hash-bound here, not represented as independently re-executed by this encoding auditor'),
                limitations=['This is encoding verification, not a SAT result, graph witness, or UNSAT proof.',
                             'Any positive solver assignment still needs complete raw-clause checking and a separate independent99graph validator.',
                             'UNSAT requires a complete independently replayed proof and excludes only this family.',
                             'No hypothetical graph automorphism, target-wide coverage denominator, or external review.'],
                target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-started)
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],clauses=cursor.count,variables=audit.top,sha256=digest(args.out/'summary.json'))))


if __name__=='__main__':main()
