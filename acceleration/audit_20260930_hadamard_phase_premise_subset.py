"""Independent 14-pattern exclusion review, including six free parity groups."""
from copy import deepcopy
from datetime import datetime,timezone
from itertools import product
from pathlib import Path
import argparse,json,platform,subprocess,sys,time
import audit_20260930_hadamard_f3_phase_obstruction as independent
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';D=B+'hadamard_phase_premise_subset/'
PINS={D+'summary.json':'17e183d83dc983b63e5dd5e874f60e308e5e7e202f14d19e3363c10a2fb14484',D+'certificate.json':'2fd565b2286154190a657e4d6ecff5f53945c8c9eb4651aeb86b1e7374dc4850',D+'attempts.json':'a698fc9cbf1f7aa1ecf6e15c31303775d6281ad576a94edcc539c71ab9b6a8af',
 'acceleration/theory_20260930_hadamard_phase_premise_subset.py':'ee64eb1ef3f8b88a47b8dfc4e9a6f7ae81a923fe3456dce2f54ab76a8bb44c04',
 'acceleration/theory_20260930_hadamard_phase_premise_subset_spec.md':'cfe8d51a8dc8418c6da0913e3e87c1bbbb2d7e019b2c9e1f3b3e2f4773832611',
 B+'hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 B+'independent_review/hadamard_parity_support_cuts_sat/independent_projection.json':'f43ad5f79d6fc8c8f6825f52d0140a07852a873207642b4edb7c035cb5ed4a8c',
 B+'independent_review/hadamard_parity_support_cuts_sat/summary.json':'02ae20d479a0d2589c02f435e2a8fdd781ec0459b60095d130b68b5f2721a04a',
 B+'hadamard_parity_support_cuts/model.json':'c477693bbf634609c234bf5b791c499f8f9ded091795b01bec297746288b4f4f',
 B+'independent_review/hadamard_general_f3_phase_necessity/summary.json':'30dd4e571140a139f7e36baf47f62a4428b752c79bbddd164ec6e54f3b232d67',
 'acceleration/audit_20260930_hadamard_f3_phase_obstruction.py':'7c6c3708b994f55c5e5ec3809639d2a88ec958c4ef66659325a1cef6e4d22e19',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db','pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
need=independent.need;h=independent.h;read=independent.read;save=independent.save;key=independent.key
def row_dependencies(row,groups):
    if row['kind']=='column_gauge':return[]
    if row['kind']=='local_same_sign_sum':return[row['group']]
    need(row['kind']in('pair_odd_phase_sum','pair_even_phase_sum'),'known row semantic kind')
    a,b=row['coordinates'];result=[g for g,s in enumerate(groups)if a in s and b in s]
    need(len(result)==5,'all5 actual incident groups');return result
def semantic_row(row,groups,patterns):
    v=[0]*120
    if row['kind']=='column_gauge':v[6*row['group']]=1;return v
    if row['kind']=='local_same_sign_sum':
        g=row['group'];need(sum(patterns[g])==3,'used local mixed premise')
        for pos,p in enumerate(patterns[g]):
            if (1 if p==0 else 2)==row['sign']:v[6*g+pos]=1
        return v
    a,b=row['coordinates'];wanted=2 if row['kind']=='pair_odd_phase_sum'else 1
    for g in row_dependencies(row,groups):
        ia,ib=groups[g].index(a),groups[g].index(b);ratio=1 if patterns[g][ia]==patterns[g][ib]else 2
        if ratio==wanted:v[6*g+ib]=1;v[6*g+ia]=(-ratio)%3
    return v
def validate_certificate(certificate,system):
    groups=system['groups'];rows=system['rows'];matrix=[r['coefficients']for r in rows];fixed=certificate['fixed_group_indices']
    need(type(fixed)is list and fixed==sorted(set(fixed))and 0 in fixed and all(type(g)is int and 0<=g<20 for g in fixed),'fixed group indices')
    need(certificate['fixed_patterns']==[dict(group=g,pattern=system['patterns'][g])for g in fixed],'literal fixed patterns')
    dependencies=[row_dependencies(r,groups)for r in rows];need(certificate['row_dependencies']==dependencies,'all180 conservative row dependencies')
    target=system['necessary_nonzero_functionals'][0];need(certificate['required_nonzero']==target and target['group']in fixed,'mixed target retained')
    weights=certificate['row_combination'];need(len(weights)==180,'full original-row weights')
    need(independent.linear_combination(weights,matrix)==target['coefficients'],'exact original180row identity')
    union={target['group']};used=[]
    for i,w in enumerate(weights):
        if w:
            need(set(dependencies[i])<=set(fixed),'used row cannot depend on free patterns');union.update(dependencies[i]);used.append(i)
            need(semantic_row(rows[i],groups,system['patterns'])==matrix[i],'literal semantic coefficient row')
    need(certificate['all_gauges_unconditional']is True and certificate['remaining_groups_unrestricted']is True and certificate['minimum_cardinality_claim']is False,'explicit broader scope flags')
    return dependencies,used,sorted(union)
def span_check(matrix,indices,target):
    selected=[matrix[i]for i in indices];rank=len(independent.column_rank(selected));extended=len(independent.column_rank(selected+[target]))
    return rank,rank==extended
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        need(all(h(ROOT/p)==value for p,value in PINS.items()),'frozen inputs and independent helper')
        general=read(ROOT/(B+'independent_review/hadamard_general_f3_phase_necessity/summary.json'));need(general['status']=='INDEPENDENT_GENERAL_BALANCED_GF3_PHASE_NECESSITY_PASS','general necessary theorem gate')
        raw=read(ROOT/(B+'hadamard20_support/six_prism.json'));projection=read(ROOT/(B+'independent_review/hadamard_parity_support_cuts_sat/independent_projection.json'))
        system=independent.derive(raw,projection);matrix=[r['coefficients']for r in system['rows']];target=system['necessary_nonzero_functionals'][0]['coefficients']
        certificate=read(ROOT/(D+'certificate.json'));dependencies,used,union=validate_certificate(certificate,system);fixed=certificate['fixed_group_indices']
        need(len(fixed)==14 and union==fixed,'exact14 required group union');free=sorted(set(range(20))-set(fixed));need(free==[1,2,5,17,18,19],'exact6 free groups')
        pins={**PINS,key(__file__):h(__file__),'docs/AUDIT_20260930_HADAMARD_FOURTEEN_PATTERN_EXCLUSION.md':h(ROOT/'docs/AUDIT_20260930_HADAMARD_FOURTEEN_PATTERN_EXCLUSION.md')}
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
            producer='/root',verifier='/root/structural_attack',producer_code_imported=False,
            shared_checker='Pinned previously independent literal core/phase reconstruction and right-to-left column elimination; no discovery code.',limits=dict(wall_seconds=60,solver_calls=0)))
        tiny=0
        for flat in product(range(3),repeat=4):
            m=[list(flat[:2]),list(flat[2:])];possible={tuple(sum(c[i]*m[i][j]for i in range(2))%3 for j in range(2))for c in product(range(3),repeat=2)}
            for t in product(range(3),repeat=2):need(span_check(m,[0,1],list(t))[1]==(t in possible),'exhaustive729tiny membership cases');tiny+=1
        attempts=read(ROOT/(D+'attempts.json'));need(len(attempts)==20,'all20 saved attempts');current=set(range(20));trace=[]
        for index,record in enumerate(attempts):
            remove=None if index==0 else 20-index;proposal=current if remove is None else current-{remove}
            allowed=[i for i,dep in enumerate(dependencies)if set(dep)<=proposal]
            need(record['attempt']==index and record['tried_removal']==remove and record['fixed_groups']==sorted(proposal)and record['retained_equations']==allowed,'exact saved greedy schedule')
            rank,contains=span_check(matrix,allowed,target);need(record['rank']==rank and record['contains']==contains,'alternate rank/augmented-rank membership')
            if contains:
                need(independent.linear_combination(record['weights'],matrix)==target,'saved positive-attempt row identity')
                need(all(not w or i in allowed for i,w in enumerate(record['weights'])),'positive attempt only retained rows')
                current=set(proposal)
            trace.append(dict(attempt=index,tried_removal=remove,rank=rank,contains=contains,fixed_groups=sorted(proposal),retained_equations=allowed))
        need(sorted(current)==fixed,'final greedy set reproduced')
        all_patterns=[[0]*6]+[list(p)for p in product(range(2),repeat=6)if p[0]==0 and sum(p)==3]
        model=read(ROOT/(B+'hadamard_parity_support_cuts/model.json'));need(len(model['groups'])==20,'20pattern groups')
        mapping=[]
        for g in fixed:
            group=model['groups'][g];need(group['support']==system['groups'][g]and group['parity_patterns']==all_patterns and group['selectors']==list(range(11*g+1,11*g+12)),'independent literal selector map')
            rank=all_patterns.index(system['patterns'][g]);mapping.append(dict(group=g,pattern=system['patterns'][g],pattern_index=rank,selector=11*g+rank+1))
        clause=[-r['selector']for r in mapping];need(len(clause)==len(set(clause))==14,'exact14negative literals')
        # The broad proof is dependency invariance, not sampled branch feasibility.
        changes=0
        for g in free:
            for pattern in all_patterns:
                future=deepcopy(system['patterns']);future[g]=pattern
                need(all(semantic_row(system['rows'][i],system['groups'],future)==matrix[i]for i in used),'used rows invariant under arbitrary free pattern');changes+=1
        for matching in product((False,True),repeat=14):need(any(not b for b in matching)==(not all(matching)),'complete14predicate nogood semantics')
        raw_selected={v for v in projection['selected_group_selector_ids']};need(all(-v in raw_selected for v in clause),'old complete branch violates new necessary clause')
        rejected=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,AssertionError,IndexError,KeyError):rejected.append(name)
            else:raise ValueError('corruption accepted: '+name)
        bad=deepcopy(certificate);bad['fixed_group_indices'].remove(0);bad['fixed_patterns']=[r for r in bad['fixed_patterns']if r['group']!=0];reject('unfixed_target_group',lambda:validate_certificate(bad,system))
        g=next(g for g in fixed if g!=0);bad=deepcopy(certificate);bad['fixed_group_indices'].remove(g);bad['fixed_patterns']=[r for r in bad['fixed_patterns']if r['group']!=g];reject('unfixed_used_row_group',lambda:validate_certificate(bad,system))
        pair_index=next(i for i in used if system['rows'][i]['kind'].startswith('pair_'));bad=deepcopy(certificate);bad['row_dependencies'][pair_index].pop();reject('missing_fifth_pair_dependency',lambda:validate_certificate(bad,system))
        bad=deepcopy(certificate);bad['row_combination'][0]=(bad['row_combination'][0]+1)%3;reject('changed_combination',lambda:validate_certificate(bad,system))
        bad=deepcopy(certificate);bad['fixed_patterns'][0]['pattern'][0]=1;reject('changed_fixed_pattern',lambda:validate_certificate(bad,system))
        bad=deepcopy(certificate);bad['required_nonzero']['required']='zero';reject('reversed_nonzero_requirement',lambda:validate_certificate(bad,system))
        bad=deepcopy(certificate);bad['minimum_cardinality_claim']=True;reject('unjustified_minimum_claim',lambda:validate_certificate(bad,system))
        bad_clause=clause[:];bad_clause[0]=-bad_clause[0];reject('flipped_nogood_literal',lambda:need(bad_clause==[-r['selector']for r in mapping],'literal sign mismatch'))
        bad_clause=clause[:-1];reject('omitted_nogood_literal',lambda:need(bad_clause==[-r['selector']for r in mapping],'missingfixedgroup'))
        bad_clause=clause[:];bad_clause[0]=-(11*free[0]+1);reject('free_group_substituted_in_clause',lambda:need(bad_clause==[-r['selector']for r in mapping],'wronggroup'))
        save(out/'independent_attempt_checks.json',trace)
        save(out/'verified_nogood.json',dict(clause=clause,selector_mapping=mapping,fixed_groups=fixed,free_groups=free,
            model_path=B+'hadamard_parity_support_cuts/model.json',model_sha256=PINS[B+'hadamard_parity_support_cuts/model.json'],
            used_equations=used,row_dependency_union=union,all_gauges_unconditional=True,
            validity='Every balanced full-Gram factor on this fixed support must differ from at least one of these14patterns; the other6patterns are arbitrary.',
            SAT_formula_modified=False,applied_to_solver=False,minimum_cardinality_claim=False))
        save(out/'certificate_replay.json',dict(target=system['necessary_nonzero_functionals'][0],weights=certificate['row_combination'],
            rows=[dict(index=i,coefficients=matrix[i],full_parity_dependencies=dependencies[i],metadata=system['rows'][i])for i in used],
            literal_identity=independent.linear_combination(certificate['row_combination'],matrix),all_used_rows_valid_for_every_assignment_of_free_groups=True,
            dependency_proof_reference='docs/AUDIT_20260930_HADAMARD_FOURTEEN_PATTERN_EXCLUSION.md',single_free_group_calibration_cases=changes,
            joint_free_assignment_enumeration_performed=False))
        save(out/'controls.json',dict(tiny_span_cases=tiny,nogood_predicate_truth_cases=2**14,free_group_single_change_cases=changes,rejected=rejected,positive_literal_certificate=True))
        need(time.monotonic()-start<60,'audit time limit');need(all(h(ROOT/p)==value for p,value in pins.items()),'frozeninputs unchanged')
        claim=dict(id='C-FIXED-HADAMARD-FOURTEEN-PATTERN-PHASE-EXCLUSION',revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
            statement='No binary36x60factor with the prescribed Gram on the fixed six-prism Hadamard support and coordinatewise-balanced identical-support triples can realize all14 specified normalized group patterns; the normalized parity patterns of groups1,2,5,17,18,19 are unrestricted.',
            scope='The exact14group-pattern partial assignment in verified_nogood.json; this is broader than the single20pattern witness but excludes neither allbalancedfactors on the support nor any unrestrictedtarget.',
            assumptions=['Fixed raw support/core and prescribed Gram.','Coordinatewise balance within each identical-support triple.','The14listed group patterns are fixed exactly; sixothers are free.'],
            dependencies=[dict(id='C-FIXED-HADAMARD-GENERAL-BALANCED-GF3-PHASE-NECESSITY',revision=1,relation='uses_result'),
                dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),
                dict(id='C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-SAT-WITNESS',revision=1,relation='derived_from')],
            dependency_note='The witness supplies saved pattern values and selection history only; the earlier full20branch exclusion is not a premise of this broader proof.',
            verifier='/root/structural_attack',producer='/root',method='Independent raw equation/dependency reconstruction, direct row-combination certificate, alternate rank-membership checks and exact14selector mapping.',
            shared_components=['Previously independent literal core/phase and column-rank helper reused with frozen hash; no root discovery code imported.','Raw support and authenticated parity object shared as immutable inputs.','Only Pythonstandardlibrary exact arithmetic and JSON trusted.'],
            limitations=['No global minimum-cardinality claim.','No joint enumeration of sixfreepatterns is needed or asserted; universal validity follows from used-row dependency independence.','Outside-columncaps/residualD absent and unnecessary for this obstruction.','No SAT formula modified or solver called.'],
            artifact_availability='LOCAL_ONLY',availability_reason='Workspace verification only until parent publication.',external_review=None,external_review_reason='No external review asserted.',
            created_at=datetime.now(timezone.utc).isoformat(),updated_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,evidence_sha256={key(p):h(p)for p in out.iterdir()if p.is_file()})
        save(out/'claim_binding.json',claim)
        save(out/'summary.json',dict(status='INDEPENDENT_FOURTEEN_PATTERN_PHASE_EXCLUSION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),claim_id=claim['id'],claim_revision=1,
            inputs_sha256=pins,outputs_sha256={key(p):h(p)for p in out.iterdir()if p.is_file()},fixed_groups=fixed,free_groups=free,clause=clause,
            used_equation_count=len(used),full_pair_dependency_rule_checked=True,original_attempts_independently_reproduced=20,corruptions_rejected=len(rejected),
            elapsed_seconds=time.monotonic()-start,solver_calls=0,SAT_clauses_applied=0,minimum_cardinality_claim=False,target_resolution='UNKNOWN'))
        print(json.dumps(dict(status='INDEPENDENT_FOURTEEN_PATTERN_PHASE_EXCLUSION_PASS',fixed=fixed,free=free,used_equations=len(used),corruptions=len(rejected),seconds=time.monotonic()-start)))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=h(__file__),elapsed_seconds=time.monotonic()-start,claim_approved=False));raise
if __name__=='__main__':main()
