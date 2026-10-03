"""Independent general phase necessity/dependency audit; no producer imports."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,permutations,product
from pathlib import Path
import argparse,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';D=B+'hadamard_general_f3_phase_preparation/'
PINS={D+'summary.json':'0f4837f96c335188209169b4bdf8976cdd7468919f95db4f9645840fb8359b4b',
 D+'local_controls.json':'1b9cc0e38e1ec13c69c5e50f464e14a1f492603a4981a84db6b476187d3f1233',
 D+'pair_controls.json':'e60d5ba5c17866789c8860c5f52e40402805d78964309cebd45948b0d6bb82e2',
 'acceleration/theory_20260930_hadamard_general_f3_phase_controls.py':'fcc7daf4a3c3cea919557a3368141f99dc83f9ac75c86104f81e5a504194ef56',
 'acceleration/theory_20260930_hadamard_general_f3_phase_spec.md':'454d8870c684223c0db833a0af10e48623f35e9d737017f5cd0840b79b8ed1fe',
 'docs/DERIVATION_20260930_GENERAL_BALANCED_F3_PHASES.md':'234f11ed933ba78ba813d4d1a732d4bdcc697363259e3a3ae8d46cd2afa851b5',
 B+'hadamard_support_cut_lift_cnf/summary.json':'4cb50ce2d2493e58f3cd6be1e68ed1b76bb85a2c55ca3230b05cfba827e3368c',
 B+'hadamard_support_cut_lift_cnf/instance.cnf':'17b3994ba995e283505ca06c3a636558a22815601ccef52c17f11e02fcb84a44',
 B+'hadamard_support_cut_lift_cnf/model.json':'e1ee20cfa16475a17752c9b94ec87219d81a2c6b101ed2ebec98b46cfbdfcbfc',
 B+'independent_review/hadamard_f3_phase_obstruction/summary.json':'0ccca8ba45e0ffa5ff0e1d8d7c051ffcbee3d9d30092fac5df33274d80dea346',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db','pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
def need(ok,why):
    if not ok:raise ValueError(why)
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def literal(p):return tuple((p[0]*x+p[1])%3 for x in range(3))
def affine(p):
    need(sorted(p)==[0,1,2],'literal permutation');s=(p[1]-p[0])%3;t=p[0]
    need(s in(1,2)and literal((s,t))==tuple(p),'affine uniqueness');return(s,t)
def entries(maps):
    ps=[literal(p)for p in maps]
    return [[sum(p[x]==y for p in ps)for y in range(3)]for x in range(3)]
def normalized(maps):
    ps=[literal(p)for p in maps];first=ps[0]
    return tuple(affine(tuple(p[first.index(x)]for x in range(3)))for p in ps)
def local_object(maps):
    need(entries(maps)==[[2]*3 for _ in range(3)],'local2J');norm=normalized(maps);need(norm[0]==(1,0),'gauge identity')
    signs=Counter(s for s,t in norm)
    if signs==Counter({1:6}):
        need(Counter(t for s,t in norm)==Counter({0:2,1:2,2:2}),'constant multiplicities')
        need(sum(t for s,t in norm)%3==0,'constant sum');kind='constant'
    else:
        need(signs==Counter({1:3,2:3}),'mixed sign counts')
        for sign in(1,2):need(sorted(t for s,t in norm if s==sign)==[0,1,2],'mixed bijection')
        kind='mixed'
    return dict(maps=[list(p)for p in maps],kind=kind,normalized_maps=[list(p)for p in norm])
def pair_object(maps):
    need(entries(maps)==[[2-int(x==y)for y in range(3)]for x in range(3)],'pair2J-I')
    odd=[t for s,t in maps if s==2];even=[t for s,t in maps if s==1]
    if len(odd)==0:need(Counter(even)==Counter({0:1,1:2,2:2}),'zero-odd profile')
    else:need(sorted(odd)==[0,1,2]and sorted(even)==[1,2],'three-odd profile')
    need(sum(odd)%3==0 and sum(even)%3==0,'both phase sums necessary')
    return dict(maps=[list(p)for p in maps],odd_count=len(odd))
def map_records(records,constructor):
    answer={}
    for record in records:
        maps=tuple(tuple(p)for p in record['maps']);need(maps not in answer,'no duplicate saved configurations')
        need(record==constructor(maps),'literal record identity');answer[maps]=record
    return answer
def pair_row(bits,odd):
    result=[0]*10
    for g,b in enumerate(bits):
        if bool(b)==odd:result[2*g]=(1 if odd else 2);result[2*g+1]=1
    return result
def required_dependencies(rows,used,inequality_group):
    dependencies={inequality_group}
    for index in used:
        row=rows[index]
        if row['kind']=='gauge':continue
        if row['kind']=='local':dependencies.add(row['group'])
        elif row['kind']=='pair':
            need(len(row['all_incident_groups'])==5 and len(set(row['all_incident_groups']))==5,'all5 pair dependencies')
            dependencies.update(row['all_incident_groups'])
        else:raise ValueError('unknown row kind')
    return sorted(dependencies)
def dependency_controls():
    records=[]
    for bits in product(range(2),repeat=5):
        for odd in(False,True):
            row=pair_row(bits,odd)
            need(row==[v for b in bits for v in(([1,1]if odd else[2,1])if bool(b)==odd else[0,0])],'all32 partitions both row signs')
            records.append(dict(disagreements=list(bits),odd=odd,coefficients=row))
    fixed=[1,1,1,0,0];old=pair_row(fixed,True);changed=fixed[:];changed[4]=1;new=pair_row(changed,True)
    need(old[8:]==[0,0]and new[8:]==[1,1]and old!=new,'invisible group can change pair row')
    rows=[dict(kind='gauge'),dict(kind='local',group=7),dict(kind='pair',all_incident_groups=[0,1,2,3,4])]
    needed=required_dependencies(rows,[0,1,2],6);need(needed==[0,1,2,3,4,6,7],'full row/functional dependency union')
    witnesses=[]
    for outside in product(range(2),repeat=3):
        full=fixed+list(outside);need(pair_row(full[:5],True)==old,'outside choices leave pinned pair row identical');witnesses.append(full)
    return dict(all_pair_rows=records,required_group_union=needed,unchanged_row_assignments=witnesses,
        visible_coefficient_support_counterexample=dict(original_disagreements=fixed,modified_disagreements=changed,omitted_group=4,old_row=old,new_row=new),
        shortened_nogood_rule='Retain all5 groups for every used pair row, each used local row group and the violated mixed-inequality group; gauges need no parity pin. Extra retained groups are safe.',
        general_rule_verified_by_written_dependency_proof=True,actual_research_nogoods_generated=0)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        need(all(h(ROOT/p)==value for p,value in PINS.items()),'immutable inputs')
        pins={**PINS,key(__file__):h(__file__),'docs/AUDIT_20260930_GENERAL_BALANCED_F3_NECESSITY.md':h(ROOT/'docs/AUDIT_20260930_GENERAL_BALANCED_F3_NECESSITY.md')}
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
            verifier='/root/structural_attack',producer='/root/state_literature_audit',producer_code_imported=False,limits=dict(wall_seconds=60,solver_calls=0)))
        ps=list(permutations(range(3)));aff=[affine(p)for p in ps];need(len(set(aff))==6,'S3 coverage')
        even=tuple(sorted(p for p in aff if p[0]==1));odd=tuple(sorted(p for p in aff if p[0]==2))
        # Construct all valid populations by independently derived multiplicity profiles.
        local_universe=set(permutations(even*2))|set(permutations(odd*2))|set(permutations(tuple(aff)))
        pair_universe=set(permutations(((1,0),(1,1),(1,1),(1,2),(1,2))))|set(permutations(((1,1),(1,2),*odd)))
        need(len(local_universe)==900 and len(pair_universe)==150,'profile coverage counts')
        local=read(ROOT/(D+'local_controls.json'));pairs=read(ROOT/(D+'pair_controls.json'))
        actual_local=map_records(local['all_ordered_valid_tuples'],local_object);actual_pair=map_records(pairs['all_valid_ordered_profiles'],pair_object)
        need(set(actual_local)==local_universe and set(actual_pair)==pair_universe,'complete independently derived valid populations')
        quotient={normalized(m):local_object(m)['kind']for m in local_universe}
        saved={tuple(tuple(p)for p in r['maps']):r['kind']for r in local['all_normalized_gauge_orbits']}
        need(saved==quotient and len(local['all_normalized_gauge_orbits'])==150,'complete exact normalized orbit table')
        need(Counter(quotient.values())==Counter(constant=30,mixed=120),'constant/mixed quotient counts')
        need(Counter(x['odd_count']for x in actual_pair.values())==Counter({0:30,3:120}),'both complete pair profiles')
        gauge_cases=[]
        for p in ps:
            for q in ps:
                a,b=affine(p),affine(q);r=affine(tuple(q[p.index(x)]for x in range(3)))
                need(r==(a[0]*b[0]%3,(b[1]-a[0]*b[0]*a[1])%3),'exact relative orientation')
                gauge_cases.append(dict(first=list(p),second=list(q),relative=list(r)))
        constant=tuple(tuple(p)for p in local['constant_blanket_distinctness_countercontrol']);need(local_object(constant)['kind']=='constant'and len(set(constant))<6,'valid repeated-phase constant control')
        need({((y-x)%3,(y+x)%3)for x,y in product(range(3),repeat=2)}==set(product(range(3),repeat=2)),'bijective entry indexing')
        dep=dependency_controls();save(out/'dependency_controls.json',dep);save(out/'independent_profiles.json',dict(local_profiles=[list(even*2),list(odd*2),list(aff)],pair_profiles=[[[1,0],[1,1],[1,1],[1,2],[1,2]],[[1,1],[1,2],*map(list,odd)]],gauge_cases=gauge_cases,constant_repeated_phase_positive=[list(p)for p in constant]))
        rejected=[]
        def rejects(name,fn):
            try:fn()
            except(ValueError,AssertionError,IndexError,KeyError):rejected.append(name)
            else:raise ValueError('bad control accepted: '+name)
        bad=deepcopy(local['all_ordered_valid_tuples'][0]);bad['normalized_maps'][0][1]=1;rejects('bad_gauge_intercept',lambda:map_records([bad],local_object))
        bad=deepcopy(local['all_ordered_valid_tuples'][0]);bad['kind']='mixed'if bad['kind']=='constant'else'constant';rejects('wrong_group_kind',lambda:map_records([bad],local_object))
        reject_local=list(constant);reject_local[1]=(1,1);rejects('constant_wrong_multiplicity',lambda:local_object(reject_local))
        badpair=[(1,1),(1,1),(1,1),(1,2),(1,2)];rejects('zero_odd_wrong_identity_count',lambda:pair_object(badpair))
        wrong=tuple(tuple(p)for p in pairs['linear_only_false_positive']);need(all(sum(t for s,t in wrong if s==sign)%3==0 for sign in(1,2)),'linear sums alone hold in negative control');rejects('sums_not_sufficient',lambda:pair_object(wrong))
        bad=deepcopy(pairs['all_valid_ordered_profiles'][0]);bad['odd_count']=5;rejects('wrong_saved_odd_count',lambda:map_records([bad],pair_object))
        bad=local['all_ordered_valid_tuples'][:-1];rejects('omitted_valid_local_object',lambda:need(set(map_records(bad,local_object))==local_universe,'missing local'))
        bad=pairs['all_valid_ordered_profiles']+[pairs['all_valid_ordered_profiles'][0]];rejects('duplicate_pair_record',lambda:map_records(bad,pair_object))
        rejects('truncated_pair_dependencies',lambda:required_dependencies([dict(kind='pair',all_incident_groups=[0,1,2])],[0],0))
        rejects('dropped_zero_coefficient_dependency',lambda:need(dep['visible_coefficient_support_counterexample']['old_row']==dep['visible_coefficient_support_counterexample']['new_row'],'unfixed invisible group changes row'))
        # The general theorem requires the row-space identity, not a rank heuristic.
        toy_rows=[[1,1,0],[0,1,1]];target=[1,0,2];weights=[1,2]
        need([sum(weights[k]*toy_rows[k][j]for k in range(2))%3 for j in range(3)]==target,'exact positive row identity')
        rejects('wrong_certificate_weights',lambda:need([sum([1,1][k]*toy_rows[k][j]for k in range(2))%3 for j in range(3)]==target,'bad row identity'))
        save(out/'corruptions.json',dict(rejected=rejected,count=len(rejected),linear_certificate_positive=dict(rows=toy_rows,weights=weights,functional=target)))
        previous=read(ROOT/(B+'independent_review/hadamard_f3_phase_obstruction/summary.json'))
        need(previous['status']=='INDEPENDENT_SELECTED_PARITY_GF3_PHASE_EXCLUSION_PASS','checked second branch excluded')
        save(out/'unsearched_cnf_execution_decision.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),
            execution_state='CANCELLED_BEFORE_RESEARCH_SOLVER',authorized_solver_attempts_completed=0,
            decision='Do not launch the previously built240-option CNF: its exact selected branch is already independently excluded by the GF3 certificate.',
            evidence=B+'independent_review/hadamard_f3_phase_obstruction/summary.json',evidence_sha256=PINS[B+'independent_review/hadamard_f3_phase_obstruction/summary.json'],
            cnf_path=B+'hadamard_support_cut_lift_cnf/instance.cnf',cnf_sha256=PINS[B+'hadamard_support_cut_lift_cnf/instance.cnf'],
            model_path=B+'hadamard_support_cut_lift_cnf/model.json',model_sha256=PINS[B+'hadamard_support_cut_lift_cnf/model.json'],
            raw_files_preserved=True,files_deleted_or_changed=[],encoding_independent_gate=None,
            encoding_independent_gate_reason='This formula was built as a candidate and not needed for the independent algebraic exclusion.',
            live_process_observation=None,live_process_observation_reason='No process was launched by this authorized workflow; this is a scheduling decision, not a machine-wide process census.',
            root_request='Preserve and cancel the unsearched240-selector formula after independent branch exclusion.'))
        need(time.monotonic()-start<60,'bounded review');need(all(h(ROOT/p)==value for p,value in pins.items()),'inputs unchanged')
        claim=dict(id='C-FIXED-HADAMARD-GENERAL-BALANCED-GF3-PHASE-NECESSITY',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
            statement='Every balanced-triplet factor on the fixed six-prism Hadamard support admits the stated affineGF3 gauges and constant/mixed local sum rules and the zero/three-odd pair sum rules; a checked mixed nonzero-functional row-space contradiction implies a sound parity nogood when it retains its inequality group and all groups determining every used equation, including all5 incident groups of every used pair row.',
            assumptions=['Additional coordinatewise balance of every identical-support triple.','Prescribed factor Gram and fixed support/core.','Actual row-space identity and full stated dependency union are checked for each applied certificate.'],
            scope='General necessary conditional theorem for this balanced fixed-support family. No assertion of global phase sufficiency or any family exclusion.',
            verifier='/root/structural_attack',producer='/root/state_literature_audit',producer_code_imported=False,
            method='Independent literal permutation and multiplicity-profile derivation, complete raw900/150table checks, gauge reconstruction and dependency-union proof.',
            dependencies=[dict(relation='derived_from',reference='docs/AUDIT_20260930_GENERAL_BALANCED_F3_NECESSITY.md',sha256=pins['docs/AUDIT_20260930_GENERAL_BALANCED_F3_NECESSITY.md'])],
            artifact_availability='LOCAL_ONLY',availability_reason='Workspace verification; publication controlled separately.',external_review=None,external_review_reason='No external review asserted.',
            limitations=['A nonempty linear nullspace is not a full factor.','Constant groups allow repeated equal-sign phases.','The theorem does not approve any ungenerated batch/nogood or its encoding.','No unrestricted target implication without the explicit balanced-support premise.'],
            created_at=datetime.now(timezone.utc).isoformat(),updated_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,evidence_sha256={key(p):h(p)for p in out.iterdir()if p.is_file()})
        save(out/'claim_binding.json',claim)
        save(out/'summary.json',dict(status='INDEPENDENT_GENERAL_BALANCED_GF3_PHASE_NECESSITY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),claim_id=claim['id'],claim_revision=1,
            inputs_sha256=pins,outputs_sha256={key(p):h(p)for p in out.iterdir()if p.is_file()},local_valid_ordered=900,local_gauge_types=150,constant_types=30,mixed_types=120,
            pair_valid_ordered=150,zero_odd_profiles=30,three_odd_profiles=120,raw_general_lemma_verified=True,dependency_rule_verified=True,
            corruption_controls_rejected=len(rejected),solver_calls=0,research_nogoods_checked=0,branch_rank_calculations=0,elapsed_seconds=time.monotonic()-start,
            target_resolution='UNKNOWN',producer_code_imported=False,scope=claim['scope']))
        print(json.dumps(dict(status='INDEPENDENT_GENERAL_BALANCED_GF3_PHASE_NECESSITY_PASS',local_objects=900,pair_objects=150,corruptions=len(rejected),seconds=time.monotonic()-start)))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=h(__file__),elapsed_seconds=time.monotonic()-start,claim_approved=False));raise
if __name__=='__main__':main()
