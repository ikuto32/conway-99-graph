"""Independent >=7 count-master design proof and exact threshold calibration."""
from datetime import datetime,timezone
from itertools import product
from pathlib import Path
import argparse,hashlib,json,math,platform,subprocess,sys,time,traceback

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
PINS={B+'independent_review/hadamard_count_master_preflight/summary.json':'5b23e5a188522c669128ec9f79ec8fb975d75e251c15be4ebc0857b96d4876b3',B+'independent_review/hadamard_six_profile_union/summary.json':'6a7b34f7feaf7d9330ce07f4c615f4198e8cdc0c8ac22dd7fb5e673ba59311df',B+'hadamard_count_master_preflight/inventory.json':'546a1c8ecc8a796700161ccdd064627561ea3a609955499cf7f3f07009a2ba80',B+'hadamard_count_master_preflight/local_signatures.json':'075120017568ecbb0da5369f8e45c0dafd015ae4953681491bab66f04e9fdb45'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def value(atom,values):return atom if type(atom)is bool else values[abs(atom)]==(atom>0)
def cnf_value(clauses,values):return all(any(value(x,values)for x in row)for row in clauses)
def gate_truth_check(clauses,q,x,r,z):
    variables=sorted({abs(v)for row in clauses for v in row}|{abs(v)for v in [q,x,r,z]if type(v)is not bool})
    checked=0
    for bits in product([False,True],repeat=len(variables)):
        assignment=dict(zip(variables,bits));expected=value(z,assignment)==(value(q,assignment)or(value(x,assignment)and value(r,assignment)))
        need(cnf_value(clauses,assignment)==expected,'complete threshold gate equivalence');checked+=1
    return checked
def illustrative_gate(q,x,r,z):
    # Independent algebraic CNF of z <=> q OR (x AND r), not producer maxterms.
    def neg(v):return not v if type(v)is bool else -v
    clauses=[]
    for row in [[neg(q),z],[neg(x),neg(r),z],[neg(z),q,x],[neg(z),q,r]]:
        if any(type(v)is bool and v for v in row):continue
        literals=list(dict.fromkeys(v for v in row if type(v)is not bool))
        if any(-v in literals for v in literals):continue
        clauses.append(literals)
    return clauses
def full_prefix(n,k):
    states={};clauses=[];gates=[];v=n
    for i in range(1,n+1):
        for j in range(1,min(i,k+1)+1):
            q=states.get((i-1,j),False);r=True if j==1 else states.get((i-1,j-1),False);v+=1;z=v;states[i,j]=z;cs=illustrative_gate(q,i,r,z);gate_truth_check(cs,q,i,r,z);clauses.extend(cs);gates.append(dict(i=i,j=j,q=q,x=i,r=r,z=z,clauses=cs))
    terminal=[]if k>=n else[[-states[n,k+1]]]
    return states,clauses,terminal,gates
def calibration():
    local=[]
    for q,r in [(False,True),(1,True),(False,2),(1,2)]:
        c=illustrative_gate(q,3,r,4);local.append(dict(q=q,x=3,r=r,z=4,clauses=c,truth_assignments=gate_truth_check(c,q,3,r,4)))
    results=[];flips=0;inputcases=0
    for n in range(1,7):
        for k in range(n+1):
            states,clauses,terminal,gates=full_prefix(n,k);accepted=0
            for bits in product([False,True],repeat=n):
                vals={i+1:b for i,b in enumerate(bits)}
                for (i,j),z in states.items():vals[z]=sum(bits[:i])>=j
                need(cnf_value(clauses,vals),'literal prefix-state positive')
                got=cnf_value(clauses+terminal,vals);need(got==(sum(bits)<=k),'complete tiny prefix threshold semantics');accepted+=got;inputcases+=1
                for z in states.values():
                    vals[z]=not vals[z];need(not cnf_value(clauses,vals),'flipped exact auxiliary rejected');vals[z]=not vals[z];flips+=1
            need(accepted==sum(math.comb(n,j)for j in range(k+1)),'accepted primary census');results.append(dict(n=n,bound=k,primary_assignments=2**n,accepted_primary_assignments=accepted,auxiliaries=len(states)))
    rejected=[]
    def reject(name,fn):
        try:fn()
        except ValueError:rejected.append(name);return
        raise ValueError('corrupted threshold accepted '+name)
    correct=illustrative_gate(1,3,2,4);reject('missing_implication',lambda:gate_truth_check(correct[1:],1,3,2,4));wrong=[r[:]for r in correct];wrong[0][-1]=-wrong[0][-1];reject('flipped_output_literal',lambda:gate_truth_check(wrong,1,3,2,4));reject('changed_boundary_constant',lambda:gate_truth_check(illustrative_gate(False,3,True,4),True,3,True,4))
    statuses=CounterLike()
    for mask in range(1<<20):
        unbalanced=mask.bit_count();balanced=20-unbalanced;need((unbalanced>=7)==(balanced<=13),'every20-group Boolean activity configuration');statuses.add(unbalanced>=7)
    need(statuses.yes==988116 and statuses.no==60460,'complete20-bit count census')
    return dict(local_gate_truth_tables=local,tiny_prefix_rows=results,complete_primary_input_cases=inputcases,deliberately_flipped_auxiliary_cases=flips,rejected_corruptions=rejected,all20_group_activity_masks=1<<20,accepted_activity_masks=statuses.yes,rejected_activity_masks=statuses.no,producer_clause_stream_approved=False,shared_code='No producer or previous checker imports; illustrative algebraic CNF differs from the proposed producer truth-table maxterms.')
class CounterLike:
    def __init__(self):self.yes=0;self.no=0
    def add(self,b):
        if b:self.yes+=1
        else:self.no+=1
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        pins[p]=sha(ROOT/p);need(h is None or h==pins[p],'input '+p)
    try:
        for p,h in PINS.items():pin(p,h)
        lower=read(B+'independent_review/hadamard_six_profile_union/summary.json');need(lower['status']=='INDEPENDENT_FIXED_HADAMARD_SIX_PROFILE_UNION_PASS','independent bound premise')
        cb=B+'independent_review/hadamard_six_profile_union/claim_bindings.json';pin(cb,lower['outputs_sha256'][cb]);claims=read(cb);need(any(c['id']=='C-FIXED-HADAMARD-AT-MOST-SIX-UNBALANCED-GROUPS-EXCLUSION'and c['revision']==1 and c['status']=='VERIFIED'for c in claims),'exact>=7 scope premise')
        inv=read(B+'hadamard_count_master_preflight/inventory.json');sigs=read(B+'hadamard_count_master_preflight/local_signatures.json')['signatures'];balanced=[s for s in sigs if s['counts']==[1]*18];need(len(balanced)==1,'unique balanced count signature');si=balanced[0]['index'];domainpositions=[]
        for d in inv['group_domains']:
            need(d['signature_indices'].count(si)==1,'one balanced choice per group');domainpositions.append(dict(group=d['group'],balanced_signature_index=si,position_in_initial_group_domain=d['signature_indices'].index(si)))
        save(out/'balanced_signature_references.json',dict(records=domainpositions,actual_CNF_variable_IDs=None,actual_CNF_variable_IDs_null_reason='This freezes the table interface; actual selector numbering remains to be independently checked after build.'))
        result=calibration();save(out/'controls.json',result)
        states,clauses,terminal,gates=full_prefix(20,13);need(len(states)==189,'189 threshold states')
        maxterm_count=0
        for g in gates:
            ids=sorted({x for x in [g['q'],g['x'],g['r'],g['z']]if type(x)is int});bad=0
            for bits in product([False,True],repeat=len(ids)):
                vals=dict(zip(ids,bits));bad+=value(g['z'],vals)!=(value(g['q'],vals)or(value(g['x'],vals)and value(g['r'],vals)))
            maxterm_count+=bad
        need(maxterm_count+1==1379,'truth-table maxterm suffix prediction')
        save(out/'threshold_design.json',dict(input_semantics='20 balanced-signature selector literals',bound=13,states=[dict(prefix=i,threshold=j,illustrative_variable=z)for(i,j),z in states.items()],prefix_auxiliaries=189,truth_table_maxterm_clauses_including_unit=1379,prospective_augmented_variables=155939,prospective_augmented_clauses=705833,actual_CNF_approved=False,illustrative_clause_count=len(clauses)+len(terminal),note='Illustrative four-clause Boolean identity is for independent semantics controls. Producer uses full falsifying-valuation maxterms, so these streams are intentionally different.'))
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_COUNT_MASTER_AT_LEAST_SEVEN.md','uv.lock','pyproject.toml']:pin(p)
        summary=dict(status='INDEPENDENT_COUNT_MASTER_EXTENSION_DESIGN_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()},scope='Proof of the count-table balanced-selector interface and calibrated threshold semantics, necessary only for the fixed-support full-Gram/all-column-cap family. No actual CNF or native gate.',balanced_signature_index=si,independent_gate_truth_checker='gate_truth_check',actual_CNF_approved=False,solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start);save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],summary_sha256=sha(out/'summary.json'),elapsed_seconds=summary['elapsed_seconds'])))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
